from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_model_load_attestation import (
    REQUIRED_COST_MODE,
    attempt_qwen_image_model_load,
)


class _FakeCuda:
    @staticmethod
    def is_available():
        return True

    @staticmethod
    def empty_cache():
        return None


class _FakeTorch:
    bfloat16 = object()
    cuda = _FakeCuda()


class _FakePipeline:
    last_kwargs = None
    offload_enabled = False

    @classmethod
    def from_pretrained(cls, snapshot_path, **kwargs):
        cls.last_kwargs = {"snapshot_path": snapshot_path, **kwargs}
        return cls()

    def enable_sequential_cpu_offload(self):
        type(self).offload_enabled = True


class _FailingPipeline:
    @classmethod
    def from_pretrained(cls, snapshot_path, **kwargs):
        raise RuntimeError("synthetic out-of-memory control fixture")

    def enable_sequential_cpu_offload(self):  # pragma: no cover
        raise AssertionError("must not be reached")


def _readiness(*, passed=True, blockers=()):
    return SimpleNamespace(
        blockers=tuple(blockers),
        static_preflight_passed=passed,
        cuda_available=passed,
        bf16_supported=passed,
    )


class QwenImageModelLoadAttestationTests(unittest.TestCase):
    def setUp(self):
        _FakePipeline.last_kwargs = None
        _FakePipeline.offload_enabled = False

    def test_static_preflight_failure_never_attempts_model_load(self):
        with patch(
            "engine.intelligence.qwen_image_model_load_attestation.inspect_qwen_image_gpu_readiness",
            return_value=_readiness(passed=False, blockers=("cuda_unavailable",)),
        ):
            result = attempt_qwen_image_model_load(
                snapshot_path="/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9",
                cost_mode=REQUIRED_COST_MODE,
            )
        self.assertFalse(result.model_load_attempted)
        self.assertFalse(result.model_loaded)
        self.assertIn("cuda_unavailable", result.blockers)
        self.assertFalse(result.genuine_inference_executed)
        self.assertFalse(result.genuine_golden_png_created)
        self.assertFalse(result.publication_ready)

    def test_non_zero_cost_mode_blocks_load_before_import(self):
        with patch(
            "engine.intelligence.qwen_image_model_load_attestation.inspect_qwen_image_gpu_readiness",
            return_value=_readiness(),
        ):
            result = attempt_qwen_image_model_load(
                snapshot_path="/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9",
                cost_mode="paid-cloud",
            )
        self.assertFalse(result.model_load_attempted)
        self.assertIn("zero_cost_mode_not_locked", result.blockers)
        self.assertFalse(result.network_allowed)
        self.assertTrue(result.local_files_only)

    def test_successful_genuine_load_is_local_bf16_offloaded_but_not_inference(self):
        fake_diffusers = SimpleNamespace(QwenImagePipeline=_FakePipeline)

        def fake_import(name):
            if name == "torch":
                return _FakeTorch
            if name == "diffusers":
                return fake_diffusers
            raise ImportError(name)

        with patch(
            "engine.intelligence.qwen_image_model_load_attestation.inspect_qwen_image_gpu_readiness",
            return_value=_readiness(),
        ), patch(
            "engine.intelligence.qwen_image_model_load_attestation.import_module",
            side_effect=fake_import,
        ):
            result = attempt_qwen_image_model_load(
                snapshot_path="/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9",
                cost_mode=REQUIRED_COST_MODE,
            )

        self.assertTrue(result.model_load_attempted)
        self.assertTrue(result.model_loaded)
        self.assertTrue(result.sequential_cpu_offload_enabled)
        self.assertEqual(result.blockers, ())
        self.assertIs(_FakePipeline.last_kwargs["torch_dtype"], _FakeTorch.bfloat16)
        self.assertTrue(_FakePipeline.last_kwargs["local_files_only"])
        self.assertTrue(_FakePipeline.offload_enabled)
        self.assertFalse(result.network_allowed)
        self.assertFalse(result.genuine_inference_executed)
        self.assertFalse(result.png_created)
        self.assertFalse(result.semantic_approved)
        self.assertFalse(result.genuine_golden_png_created)
        self.assertFalse(result.publication_ready)

    def test_real_load_failure_is_recorded_without_false_success(self):
        fake_diffusers = SimpleNamespace(QwenImagePipeline=_FailingPipeline)

        def fake_import(name):
            if name == "torch":
                return _FakeTorch
            if name == "diffusers":
                return fake_diffusers
            raise ImportError(name)

        with patch(
            "engine.intelligence.qwen_image_model_load_attestation.inspect_qwen_image_gpu_readiness",
            return_value=_readiness(),
        ), patch(
            "engine.intelligence.qwen_image_model_load_attestation.import_module",
            side_effect=fake_import,
        ):
            result = attempt_qwen_image_model_load(
                snapshot_path=Path("/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9"),
                cost_mode=REQUIRED_COST_MODE,
            )

        self.assertTrue(result.model_load_attempted)
        self.assertFalse(result.model_loaded)
        self.assertEqual(result.load_error_type, "RuntimeError")
        self.assertIn("model_load_failed", result.blockers)
        self.assertFalse(result.sequential_cpu_offload_enabled)
        self.assertFalse(result.genuine_inference_executed)
        self.assertFalse(result.publication_ready)


if __name__ == "__main__":
    unittest.main()
