from types import SimpleNamespace
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_local_inference_runtime import (
    REQUIRED_COST_MODE,
    load_local_inference_runtime,
)
from engine.intelligence.qwen_image_runtime_envelope_plan import DTYPE, OFFLOAD_MODE


class _Props:
    total_memory = 24 * 1024 ** 3


class _Cuda:
    @staticmethod
    def current_device():
        return 0

    @staticmethod
    def get_device_properties(_device):
        return _Props()

    @staticmethod
    def get_device_name(_device):
        return "Synthetic GPU"


class _Version:
    cuda = "12.8"


class _Torch:
    __version__ = "2.synthetic"
    version = _Version()
    cuda = _Cuda()
    bfloat16 = object()


class QwenImagePipeline:
    last_args = None
    offload_enabled = False

    @classmethod
    def from_pretrained(cls, path, **kwargs):
        cls.last_args = {"path": path, **kwargs}
        return cls()

    def enable_sequential_cpu_offload(self):
        type(self).offload_enabled = True


def _readiness(*, passed=True, blockers=()):
    return SimpleNamespace(
        static_preflight_passed=passed,
        snapshot_revision_verified=passed,
        snapshot_structure_verified=passed,
        blockers=tuple(blockers),
    )


def _inventory(digest="a" * 64):
    return SimpleNamespace(
        schema="pul7sar.phase18.qwen_image_snapshot_inventory.v1",
        model_revision="2ce1c28560fbc62c9f5531e076b237d3575330a9",
        snapshot_inventory_sha256=digest,
        snapshot_file_count=4,
        snapshot_total_bytes=100,
    )


def _cs260():
    return {
        "observed_runtime_identity": {
            "gpu_name": "Synthetic GPU",
            "gpu_total_vram_gb": 24.0,
            "torch_version": "2.synthetic",
            "cuda_version": "12.8",
            "diffusers_version": "0.synthetic",
            "pipeline_class": "QwenImagePipeline",
            "dtype": DTYPE,
            "offload_mode": OFFLOAD_MODE,
            "native_bf16": True,
            "model_id": "Qwen/Qwen-Image-2512",
            "model_revision": "2ce1c28560fbc62c9f5531e076b237d3575330a9",
            "weights_loaded": True,
            "sequential_cpu_offload_enabled": True,
        }
    }


class QwenImageLocalInferenceRuntimeTests(unittest.TestCase):
    def setUp(self):
        QwenImagePipeline.last_args = None
        QwenImagePipeline.offload_enabled = False
        inventory_patcher = patch(
            "engine.intelligence.qwen_image_local_inference_runtime._snapshot_inventory",
            return_value=_inventory(),
        )
        inventory_patcher.start()
        self.addCleanup(inventory_patcher.stop)

    def test_zero_cost_lock_blocks_before_preflight(self):
        with patch(
            "engine.intelligence.qwen_image_local_inference_runtime.inspect_qwen_image_gpu_readiness"
        ) as probe:
            with self.assertRaisesRegex(RuntimeError, "ZERO_COST_MODE_NOT_LOCKED"):
                load_local_inference_runtime(
                    cs260=_cs260(),
                    snapshot_path="/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9",
                    cost_mode="paid-cloud",
                )
        probe.assert_not_called()

    def test_static_preflight_failure_blocks_model_load(self):
        with patch(
            "engine.intelligence.qwen_image_local_inference_runtime.inspect_qwen_image_gpu_readiness",
            return_value=_readiness(passed=False, blockers=("cuda_unavailable",)),
        ), patch("engine.intelligence.qwen_image_local_inference_runtime.import_module") as importer:
            with self.assertRaisesRegex(RuntimeError, "STATIC_PREFLIGHT_FAILED"):
                load_local_inference_runtime(
                    cs260=_cs260(),
                    snapshot_path="/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9",
                    cost_mode=REQUIRED_COST_MODE,
                )
        importer.assert_not_called()

    def test_snapshot_structure_must_be_verified_before_inventory_or_load(self):
        bad = _readiness()
        bad.snapshot_structure_verified = False
        with patch(
            "engine.intelligence.qwen_image_local_inference_runtime.inspect_qwen_image_gpu_readiness",
            return_value=bad,
        ), patch("engine.intelligence.qwen_image_local_inference_runtime.import_module") as importer:
            with self.assertRaisesRegex(RuntimeError, "SNAPSHOT_STRUCTURE_UNVERIFIED"):
                load_local_inference_runtime(
                    cs260=_cs260(),
                    snapshot_path="/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9",
                    cost_mode=REQUIRED_COST_MODE,
                )
        importer.assert_not_called()

    def test_successful_runtime_uses_exact_local_snapshot_without_network_fallback(self):
        fake_diffusers = SimpleNamespace(
            __version__="0.synthetic",
            QwenImagePipeline=QwenImagePipeline,
        )

        def fake_import(name):
            if name == "torch":
                return _Torch
            if name == "diffusers":
                return fake_diffusers
            raise ImportError(name)

        snapshot = "/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9"
        with patch(
            "engine.intelligence.qwen_image_local_inference_runtime.inspect_qwen_image_gpu_readiness",
            return_value=_readiness(),
        ), patch(
            "engine.intelligence.qwen_image_local_inference_runtime.import_module",
            side_effect=fake_import,
        ):
            torch, pipeline, live = load_local_inference_runtime(
                cs260=_cs260(),
                snapshot_path=snapshot,
                cost_mode=REQUIRED_COST_MODE,
            )

        self.assertIs(torch, _Torch)
        self.assertIsInstance(pipeline, QwenImagePipeline)
        self.assertEqual(QwenImagePipeline.last_args["path"], snapshot)
        self.assertTrue(QwenImagePipeline.last_args["local_files_only"])
        self.assertIs(QwenImagePipeline.last_args["torch_dtype"], _Torch.bfloat16)
        self.assertTrue(QwenImagePipeline.offload_enabled)
        self.assertEqual(live, _cs260()["observed_runtime_identity"])

    def test_snapshot_byte_drift_fails_before_from_pretrained(self):
        fake_diffusers = SimpleNamespace(
            __version__="0.synthetic",
            QwenImagePipeline=QwenImagePipeline,
        )
        with patch(
            "engine.intelligence.qwen_image_local_inference_runtime.inspect_qwen_image_gpu_readiness",
            return_value=_readiness(),
        ), patch(
            "engine.intelligence.qwen_image_local_inference_runtime.import_module",
            side_effect=lambda name: _Torch if name == "torch" else fake_diffusers,
        ), patch(
            "engine.intelligence.qwen_image_local_inference_runtime._snapshot_inventory",
            side_effect=[_inventory("a" * 64), _inventory("b" * 64)],
        ):
            with self.assertRaisesRegex(RuntimeError, "SNAPSHOT_BYTE_INVENTORY_DRIFT"):
                load_local_inference_runtime(
                    cs260=_cs260(),
                    snapshot_path="/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9",
                    cost_mode=REQUIRED_COST_MODE,
                )
        self.assertIsNone(QwenImagePipeline.last_args)
        self.assertFalse(QwenImagePipeline.offload_enabled)

    def test_host_identity_drift_fails_before_from_pretrained(self):
        fake_diffusers = SimpleNamespace(
            __version__="0.synthetic",
            QwenImagePipeline=QwenImagePipeline,
        )

        def fake_import(name):
            return _Torch if name == "torch" else fake_diffusers

        bad = _cs260()
        bad["observed_runtime_identity"]["gpu_name"] = "Different GPU"
        with patch(
            "engine.intelligence.qwen_image_local_inference_runtime.inspect_qwen_image_gpu_readiness",
            return_value=_readiness(),
        ), patch(
            "engine.intelligence.qwen_image_local_inference_runtime.import_module",
            side_effect=fake_import,
        ):
            with self.assertRaisesRegex(RuntimeError, "PRE_MODEL_LOAD_RUNTIME_IDENTITY_DRIFT:gpu_name"):
                load_local_inference_runtime(
                    cs260=bad,
                    snapshot_path="/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9",
                    cost_mode=REQUIRED_COST_MODE,
                )
        self.assertIsNone(QwenImagePipeline.last_args)
        self.assertFalse(QwenImagePipeline.offload_enabled)

    def test_diffusers_version_drift_fails_before_from_pretrained(self):
        fake_diffusers = SimpleNamespace(
            __version__="0.drifted",
            QwenImagePipeline=QwenImagePipeline,
        )

        def fake_import(name):
            return _Torch if name == "torch" else fake_diffusers

        with patch(
            "engine.intelligence.qwen_image_local_inference_runtime.inspect_qwen_image_gpu_readiness",
            return_value=_readiness(),
        ), patch(
            "engine.intelligence.qwen_image_local_inference_runtime.import_module",
            side_effect=fake_import,
        ):
            with self.assertRaisesRegex(RuntimeError, "PRE_MODEL_LOAD_RUNTIME_IDENTITY_DRIFT:diffusers_version"):
                load_local_inference_runtime(
                    cs260=_cs260(),
                    snapshot_path="/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9",
                    cost_mode=REQUIRED_COST_MODE,
                )
        self.assertIsNone(QwenImagePipeline.last_args)

    def test_expected_post_load_contract_cannot_be_weakened(self):
        fake_diffusers = SimpleNamespace(
            __version__="0.synthetic",
            QwenImagePipeline=QwenImagePipeline,
        )

        def fake_import(name):
            return _Torch if name == "torch" else fake_diffusers

        bad = _cs260()
        bad["observed_runtime_identity"]["sequential_cpu_offload_enabled"] = False
        with patch(
            "engine.intelligence.qwen_image_local_inference_runtime.inspect_qwen_image_gpu_readiness",
            return_value=_readiness(),
        ), patch(
            "engine.intelligence.qwen_image_local_inference_runtime.import_module",
            side_effect=fake_import,
        ):
            with self.assertRaisesRegex(RuntimeError, "EXPECTED_OFFLOAD_AUTHORITY_INVALID"):
                load_local_inference_runtime(
                    cs260=bad,
                    snapshot_path="/tmp/snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9",
                    cost_mode=REQUIRED_COST_MODE,
                )
        self.assertIsNone(QwenImagePipeline.last_args)


if __name__ == "__main__":
    unittest.main()
