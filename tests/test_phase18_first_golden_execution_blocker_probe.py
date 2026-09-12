from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)
from tools.phase18_probe_first_golden_execution_blocker import inspect


class _CudaReady:
    @staticmethod
    def is_available():
        return True

    @staticmethod
    def device_count():
        return 1

    @staticmethod
    def is_bf16_supported():
        return True


class _VersionReady:
    cuda = "12.8"


class _TorchReady:
    cuda = _CudaReady()
    version = _VersionReady()


class _CudaBlocked:
    @staticmethod
    def is_available():
        return False

    @staticmethod
    def device_count():
        return 0

    @staticmethod
    def is_bf16_supported():
        return False


class _VersionBlocked:
    cuda = None


class _TorchBlocked:
    cuda = _CudaBlocked()
    version = _VersionBlocked()


def _snapshot(root: Path, model_id: str, revision: str) -> Path:
    owner, repo = model_id.split("/", 1)
    return root / f"models--{owner}--{repo}" / "snapshots" / revision


class FirstGoldenExecutionBlockerProbeTests(unittest.TestCase):
    def test_ready_requires_offline_zero_cost_cuda_bf16_and_both_exact_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION).mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION).mkdir(parents=True)
            payload = inspect(
                env={
                    "HF_HUB_CACHE": str(cache),
                    "HF_HUB_OFFLINE": "1",
                    "TRANSFORMERS_OFFLINE": "1",
                    "PUL7SAR_PHASE18_COST_MODE": "$0-local",
                },
                torch_module=_TorchReady(),
            )
        self.assertTrue(payload["ready_for_authoritative_golden_preflight"])
        self.assertEqual(payload["blockers"], [])
        self.assertFalse(payload["authoritative_gate"])
        self.assertFalse(payload["network_download_authorized"])
        self.assertFalse(payload["generation_authorized"])
        self.assertFalse(payload["publication_ready"])
        self.assertFalse(payload["seeds_2_to_4_authorized"])

    def test_blocked_host_reports_runtime_offline_cost_and_exact_cache_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = inspect(
                env={"HF_HUB_CACHE": str(Path(tmp) / "hub")},
                torch_module=_TorchBlocked(),
            )
        blockers = set(payload["blockers"])
        expected = {
            "HF_HUB_OFFLINE_NOT_1",
            "TRANSFORMERS_OFFLINE_NOT_1",
            "ZERO_COST_MODE_NOT_ASSERTED",
            "CUDA_UNAVAILABLE",
            "CUDA_RUNTIME_UNAVAILABLE",
            "CUDA_DEVICE_MISSING",
            "NATIVE_BF16_UNAVAILABLE",
            "QWEN_APPROVED_SNAPSHOT_MISSING",
            "FLUX_APPROVED_SNAPSHOT_MISSING",
        }
        self.assertTrue(expected.issubset(blockers))
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_mutable_or_wrong_revision_directory_does_not_satisfy_cache_requirement(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, "main").mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, "0" * 40).mkdir(parents=True)
            payload = inspect(
                env={
                    "HF_HUB_CACHE": str(cache),
                    "HF_HUB_OFFLINE": "1",
                    "TRANSFORMERS_OFFLINE": "1",
                    "PUL7SAR_PHASE18_COST_MODE": "$0-local",
                },
                torch_module=_TorchReady(),
            )
        self.assertIn("QWEN_APPROVED_SNAPSHOT_MISSING", payload["blockers"])
        self.assertIn("FLUX_APPROVED_SNAPSHOT_MISSING", payload["blockers"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])


if __name__ == "__main__":
    unittest.main()
