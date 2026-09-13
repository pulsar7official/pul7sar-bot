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


READY_GPU_QUALIFICATION = {
    "eligible": True,
    "reasons": [],
    "gpu_name": "fixture-gpu",
    "gpu_vram_gb": 24.0,
    "gpu_free_vram_gb": 20.0,
    "bf16_supported": True,
    "compute_capability": "8.9",
    "required_vram_gb": 12.0,
    "cost_mode": "$0-local",
}

READY_HOST_MEMORY = {
    "ready": True,
    "available_ram_gb": 32.0,
    "minimum_available_ram_gb": 10.0,
    "reasons": [],
    "cost_mode": "$0-local",
}

READY_CACHE_HEADROOM = {
    "minimum_working_free_gib": 8.0,
    "free_bytes": 16 * 1024 ** 3,
    "free_gib": 16.0,
    "eligible": True,
    "reason": "post_cache_working_headroom_ready",
}

READY_GENERATION_RUNTIME = {
    "ready": True,
    "schema": "pul7sar-generation-runtime-fingerprint-v1",
    "runtime_fingerprint_sha256": "a" * 64,
    "python_version": "3.13.7",
    "python_implementation": "CPython",
    "machine": "x86_64",
    "packages": {
        "Pillow": "11.3.0",
        "accelerate": "1.10.1",
        "diffusers": "0.40.0",
        "huggingface_hub": "0.35.0",
        "safetensors": "0.6.2",
        "tokenizers": "0.22.0",
        "transformers": "4.56.2",
    },
    "torch": {
        "version": "2.8.0+cu128",
        "cuda_version": "12.8",
        "cuda_available": True,
        "gpu_name": "fixture-gpu",
        "compute_capability": "8.9",
    },
    "cost_mode": "$0-local",
    "generation_authorized": False,
    "publication_ready": False,
}

READY_SEMANTIC_RUNTIME = {
    "ready": True,
    "model_id": QWEN25_VL_3B_MODEL_ID,
    "transformers_version": "4.56.2",
    "torch_version": "2.8.0+cu128",
    "cuda_available": True,
    "failures": [],
    "cost_mode": "$0-local",
    "generation_authorized": False,
    "publication_ready": False,
}


def _snapshot(root: Path, model_id: str, revision: str) -> Path:
    owner, repo = model_id.split("/", 1)
    return root / f"models--{owner}--{repo}" / "snapshots" / revision


def _filesystem_local_resolver(cache_root: Path, model_id: str, revision: str) -> Path | None:
    snapshot = _snapshot(cache_root, model_id, revision)
    return snapshot.resolve() if snapshot.is_dir() else None


class FirstGoldenExecutionBlockerProbeTests(unittest.TestCase):
    def _inspect(
        self,
        *,
        cache: Path,
        torch_module,
        resolver=_filesystem_local_resolver,
        gpu=None,
        memory=None,
        headroom=None,
        runtime=None,
        semantic=None,
    ):
        return inspect(
            env={
                "HF_HUB_CACHE": str(cache),
                "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1",
                "PUL7SAR_PHASE18_COST_MODE": "$0-local",
            },
            torch_module=torch_module,
            snapshot_resolver=resolver,
            gpu_qualification_report=READY_GPU_QUALIFICATION if gpu is None else gpu,
            host_memory_report=READY_HOST_MEMORY if memory is None else memory,
            cache_headroom_report=READY_CACHE_HEADROOM if headroom is None else headroom,
            generation_runtime_report=READY_GENERATION_RUNTIME if runtime is None else runtime,
            semantic_runtime_report=READY_SEMANTIC_RUNTIME if semantic is None else semantic,
        )

    def test_ready_requires_offline_zero_cost_cuda_bf16_runtime_semantic_live_resources_headroom_and_both_exact_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION).mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION).mkdir(parents=True)
            payload = self._inspect(cache=cache, torch_module=_TorchReady())
        self.assertTrue(payload["ready_for_authoritative_golden_preflight"])
        self.assertEqual(payload["blockers"], [])
        self.assertEqual(payload["schema"], "pul7sar-phase18-first-golden-execution-blocker-probe-v6")
        self.assertEqual(payload["cache"]["resolution_mode"], "huggingface-local-files-only")
        self.assertTrue(payload["cache"]["qwen_cached"])
        self.assertTrue(payload["cache"]["flux_cached"])
        self.assertTrue(payload["generation_runtime"]["ready"])
        self.assertEqual(payload["generation_runtime"]["schema"], "pul7sar-generation-runtime-fingerprint-v1")
        self.assertTrue(payload["semantic_runtime"]["ready"])
        self.assertEqual(payload["semantic_runtime"]["model_id"], QWEN25_VL_3B_MODEL_ID)
        self.assertTrue(payload["gpu_qualification"]["eligible"])
        self.assertTrue(payload["host_memory"]["ready"])
        self.assertTrue(payload["cache_headroom"]["eligible"])
        self.assertEqual(payload["cache_headroom"]["minimum_working_free_gib"], 8.0)
        self.assertFalse(payload["authoritative_gate"])
        self.assertFalse(payload["network_download_authorized"])
        self.assertFalse(payload["generation_authorized"])
        self.assertFalse(payload["publication_ready"])
        self.assertFalse(payload["seeds_2_to_4_authorized"])

    def test_blocked_host_reports_runtime_offline_cost_cache_gpu_memory_headroom_software_and_semantic_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = inspect(
                env={"HF_HUB_CACHE": str(Path(tmp) / "hub")},
                torch_module=_TorchBlocked(),
                snapshot_resolver=_filesystem_local_resolver,
                gpu_qualification_report={
                    "eligible": False,
                    "reasons": ["live free GPU VRAM could not be proven"],
                    "cost_mode": "$0-local",
                },
                host_memory_report={
                    "ready": False,
                    "reasons": ["available_system_ram_unproven"],
                    "cost_mode": "$0-local",
                },
                cache_headroom_report={
                    "eligible": False,
                    "reason": "post_cache_working_headroom_below_floor",
                    "free_bytes": 2 * 1024 ** 3,
                    "free_gib": 2.0,
                    "minimum_working_free_gib": 8.0,
                },
                generation_runtime_report={
                    "ready": False,
                    "reason": "generation_runtime_probe_failed:RuntimeError",
                    "cost_mode": "$0-local",
                    "generation_authorized": False,
                    "publication_ready": False,
                },
                semantic_runtime_report={
                    "ready": False,
                    "model_id": QWEN25_VL_3B_MODEL_ID,
                    "failures": ["transformers_qwen2_5_vl_public_api_unavailable"],
                    "cost_mode": "$0-local",
                    "generation_authorized": False,
                    "publication_ready": False,
                },
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
            "GENERATION_RUNTIME_NOT_READY",
            "SEMANTIC_RUNTIME_NOT_READY",
            "GPU_HOST_NOT_GOLDEN_QUALIFIED",
            "HOST_MEMORY_NOT_READY",
            "CACHE_WORKING_HEADROOM_NOT_READY",
            "QWEN_APPROVED_SNAPSHOT_MISSING",
            "FLUX_APPROVED_SNAPSHOT_MISSING",
        }
        self.assertTrue(expected.issubset(blockers))
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_incompatible_generation_software_runtime_blocks_before_authoritative_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION).mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION).mkdir(parents=True)
            payload = self._inspect(
                cache=cache,
                torch_module=_TorchReady(),
                runtime={
                    "ready": False,
                    "reason": "generation_runtime_probe_failed:RuntimeError",
                    "cost_mode": "$0-local",
                    "generation_authorized": False,
                    "publication_ready": False,
                },
            )
        self.assertIn("GENERATION_RUNTIME_NOT_READY", payload["blockers"])
        self.assertFalse(payload["generation_runtime"]["ready"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_semantic_public_api_or_runtime_incoherence_blocks_before_authoritative_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION).mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION).mkdir(parents=True)
            payload = self._inspect(
                cache=cache,
                torch_module=_TorchReady(),
                semantic={
                    **READY_SEMANTIC_RUNTIME,
                    "ready": False,
                    "failures": ["transformers_qwen2_5_vl_public_api_unavailable"],
                },
            )
        self.assertIn("SEMANTIC_RUNTIME_NOT_READY", payload["blockers"])
        self.assertEqual(payload["semantic_runtime"]["failures"], ["transformers_qwen2_5_vl_public_api_unavailable"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_semantic_identity_authority_or_cost_drift_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION).mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION).mkdir(parents=True)
            payload = self._inspect(
                cache=cache,
                torch_module=_TorchReady(),
                semantic={
                    **READY_SEMANTIC_RUNTIME,
                    "model_id": "drifted/model",
                    "cost_mode": "paid",
                    "generation_authorized": True,
                },
            )
        self.assertIn("SEMANTIC_RUNTIME_MODEL_ID_DRIFT", payload["blockers"])
        self.assertIn("SEMANTIC_RUNTIME_ZERO_COST_DRIFT", payload["blockers"])
        self.assertIn("SEMANTIC_RUNTIME_AUTHORITY_DRIFT", payload["blockers"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_runtime_authority_or_cost_drift_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION).mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION).mkdir(parents=True)
            payload = self._inspect(
                cache=cache,
                torch_module=_TorchReady(),
                runtime={
                    **READY_GENERATION_RUNTIME,
                    "cost_mode": "paid",
                    "generation_authorized": True,
                },
            )
        self.assertIn("GENERATION_RUNTIME_ZERO_COST_DRIFT", payload["blockers"])
        self.assertIn("GENERATION_RUNTIME_AUTHORITY_DRIFT", payload["blockers"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_low_live_vram_blocks_even_when_cuda_and_bf16_are_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION).mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION).mkdir(parents=True)
            payload = self._inspect(
                cache=cache,
                torch_module=_TorchReady(),
                gpu={
                    "eligible": False,
                    "reasons": ["live free GPU VRAM 8.000 GB is below required 12.000 GB"],
                    "gpu_free_vram_gb": 8.0,
                    "required_vram_gb": 12.0,
                    "bf16_supported": True,
                    "cost_mode": "$0-local",
                },
            )
        self.assertIn("GPU_HOST_NOT_GOLDEN_QUALIFIED", payload["blockers"])
        self.assertTrue(payload["runtime"]["native_bf16"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_low_available_host_ram_blocks_before_authoritative_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION).mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION).mkdir(parents=True)
            payload = self._inspect(
                cache=cache,
                torch_module=_TorchReady(),
                memory={
                    "ready": False,
                    "available_ram_gb": 6.0,
                    "minimum_available_ram_gb": 10.0,
                    "reasons": ["available_system_ram_below_first_golden_floor"],
                    "cost_mode": "$0-local",
                },
            )
        self.assertIn("HOST_MEMORY_NOT_READY", payload["blockers"])
        self.assertEqual(payload["host_memory"]["available_ram_gb"], 6.0)
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_low_post_cache_working_headroom_blocks_before_authoritative_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION).mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION).mkdir(parents=True)
            payload = self._inspect(
                cache=cache,
                torch_module=_TorchReady(),
                headroom={
                    "minimum_working_free_gib": 8.0,
                    "free_bytes": 7 * 1024 ** 3,
                    "free_gib": 7.0,
                    "eligible": False,
                    "reason": "post_cache_working_headroom_below_floor",
                },
            )
        self.assertIn("CACHE_WORKING_HEADROOM_NOT_READY", payload["blockers"])
        self.assertEqual(payload["cache_headroom"]["minimum_working_free_gib"], 8.0)
        self.assertEqual(payload["cache_headroom"]["free_gib"], 7.0)
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_mutable_or_wrong_revision_directory_does_not_satisfy_cache_requirement(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, "main").mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, "0" * 40).mkdir(parents=True)
            payload = self._inspect(cache=cache, torch_module=_TorchReady())
        self.assertIn("QWEN_APPROVED_SNAPSHOT_MISSING", payload["blockers"])
        self.assertIn("FLUX_APPROVED_SNAPSHOT_MISSING", payload["blockers"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_directory_presence_alone_does_not_mark_snapshot_cached_without_local_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION).mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION).mkdir(parents=True)

            def unresolved(_cache_root: Path, _model_id: str, _revision: str) -> Path | None:
                return None

            payload = self._inspect(cache=cache, torch_module=_TorchReady(), resolver=unresolved)
        self.assertTrue(payload["cache"]["qwen_snapshot_directory_present"])
        self.assertTrue(payload["cache"]["flux_snapshot_directory_present"])
        self.assertFalse(payload["cache"]["qwen_cached"])
        self.assertFalse(payload["cache"]["flux_cached"])
        self.assertIn("QWEN_APPROVED_SNAPSHOT_MISSING", payload["blockers"])
        self.assertIn("FLUX_APPROVED_SNAPSHOT_MISSING", payload["blockers"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_zero_cost_drift_inside_resource_receipts_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "hub"
            _snapshot(cache, QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION).mkdir(parents=True)
            _snapshot(cache, FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION).mkdir(parents=True)
            payload = self._inspect(
                cache=cache,
                torch_module=_TorchReady(),
                gpu={**READY_GPU_QUALIFICATION, "cost_mode": "paid"},
                memory={**READY_HOST_MEMORY, "cost_mode": "paid"},
            )
        self.assertIn("GPU_QUALIFICATION_ZERO_COST_DRIFT", payload["blockers"])
        self.assertIn("HOST_MEMORY_ZERO_COST_DRIFT", payload["blockers"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])


if __name__ == "__main__":
    unittest.main()