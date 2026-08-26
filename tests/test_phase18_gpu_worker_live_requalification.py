from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from engine.intelligence.generation_jobs import GenerationWorkerCapabilities
from tools import phase18_gpu_worker


class GpuWorkerLiveRequalificationTests(unittest.TestCase):
    def _capabilities(self, gpu_name: str = "Test GPU") -> GenerationWorkerCapabilities:
        return GenerationWorkerCapabilities(
            worker_id="worker-01",
            provider_ids=frozenset({"black-forest-labs"}),
            model_ids=frozenset({"black-forest-labs/FLUX.2-klein-4B"}),
            cuda_available=True,
            bf16_supported=True,
            vram_gb=24.0,
            max_concurrency=1,
            metadata={"gpu_name": gpu_name, "resolved_dtype": "bfloat16", "cost_mode": "$0-local"},
        )

    def test_live_requalification_returns_non_authorizing_receipt(self) -> None:
        qualification = SimpleNamespace(
            eligible=True,
            reasons=(),
            gpu_name="Test GPU",
            cost_mode="$0-local",
            bf16_supported=True,
            as_dict=lambda: {
                "eligible": True,
                "gpu_name": "Test GPU",
                "gpu_free_vram_gb": 18.5,
                "required_vram_gb": 13.0,
                "cost_mode": "$0-local",
            },
        )
        policy = SimpleNamespace(evaluate=lambda **kwargs: qualification)
        runtime_probe = SimpleNamespace(detect=lambda: object())
        with patch.object(phase18_gpu_worker, "GpuHostQualificationPolicy", return_value=policy), patch.object(
            phase18_gpu_worker, "LocalRuntimeProbe", return_value=runtime_probe
        ):
            payload = phase18_gpu_worker._requalify_live_host(self._capabilities())

        self.assertTrue(payload["eligible"])
        self.assertEqual(payload["gpu_free_vram_gb"], 18.5)
        self.assertTrue(payload["requalified_immediately_before_queue_mutation"])
        self.assertFalse(payload["queue_mutated_by_requalification"])
        self.assertFalse(payload["generation_authorized_by_requalification"])
        self.assertFalse(payload["publication_ready"])

    def test_live_requalification_rejects_insufficient_host(self) -> None:
        qualification = SimpleNamespace(
            eligible=False,
            reasons=("live free GPU VRAM 8.000 GB is below required 13.000 GB",),
            gpu_name="Test GPU",
            cost_mode="$0-local",
            bf16_supported=True,
        )
        policy = SimpleNamespace(evaluate=lambda **kwargs: qualification)
        runtime_probe = SimpleNamespace(detect=lambda: object())
        with patch.object(phase18_gpu_worker, "GpuHostQualificationPolicy", return_value=policy), patch.object(
            phase18_gpu_worker, "LocalRuntimeProbe", return_value=runtime_probe
        ):
            with self.assertRaisesRegex(RuntimeError, "live host requalification failed"):
                phase18_gpu_worker._requalify_live_host(self._capabilities())

    def test_live_requalification_rejects_device_identity_change(self) -> None:
        qualification = SimpleNamespace(
            eligible=True,
            reasons=(),
            gpu_name="Different GPU",
            cost_mode="$0-local",
            bf16_supported=True,
            as_dict=lambda: {"eligible": True},
        )
        policy = SimpleNamespace(evaluate=lambda **kwargs: qualification)
        runtime_probe = SimpleNamespace(detect=lambda: object())
        with patch.object(phase18_gpu_worker, "GpuHostQualificationPolicy", return_value=policy), patch.object(
            phase18_gpu_worker, "LocalRuntimeProbe", return_value=runtime_probe
        ):
            with self.assertRaisesRegex(RuntimeError, "device identity changed"):
                phase18_gpu_worker._requalify_live_host(self._capabilities())

    def test_worker_requalifies_before_recovery_and_lease_execution(self) -> None:
        source = Path(phase18_gpu_worker.__file__).read_text(encoding="utf-8")
        loop = source.index("while True:")
        requalify = source.index("_requalify_execution_host(capabilities)", loop)
        recovery = source.index("store.recover_expired", loop)
        run_once = source.index("service.run_once", loop)
        self.assertLess(requalify, recovery)
        self.assertLess(requalify, run_once)

    def test_worker_binds_second_requalification_inside_leased_execution(self) -> None:
        source = Path(phase18_gpu_worker.__file__).read_text(encoding="utf-8")
        service_start = source.index("service = GenerationWorkerService(")
        service = source[service_start : source.index("initial_snapshot =", service_start)]
        self.assertIn("pre_execute_guard=", service)
        self.assertIn("_requalify_execution_host(capabilities)", service)
        self.assertIn("lease_bound_pre_execute_guard", source)

    def test_initial_requalification_occurs_before_store_creation(self) -> None:
        source = Path(phase18_gpu_worker.__file__).read_text(encoding="utf-8")
        main = source[source.index("def main()") :]
        initial = main.index("initial_execution_host = _requalify_execution_host(capabilities)")
        store = main.index("FilesystemGenerationJobStore(")
        self.assertLess(initial, store)


if __name__ == "__main__":
    unittest.main()
