from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from engine.intelligence.worker_host_memory_guard import WorkerHostMemoryGuard
from tools import phase18_gpu_worker


class WorkerHostMemoryGuardTests(unittest.TestCase):
    def test_guard_returns_non_authorizing_receipt(self) -> None:
        report = SimpleNamespace(
            ready=True,
            cost_mode="$0-local",
            available_ram_gb=18.0,
            minimum_available_ram_gb=10.0,
            total_ram_gb=31.0,
            measurement_source="/proc/meminfo",
            reasons=(),
        )
        probe = SimpleNamespace(inspect=lambda: report)
        with patch(
            "engine.intelligence.worker_host_memory_guard.HostMemoryQualificationProbe",
            return_value=probe,
        ):
            receipt = WorkerHostMemoryGuard().inspect()

        self.assertTrue(receipt.ready)
        self.assertEqual(receipt.available_ram_gb, 18.0)
        self.assertEqual(receipt.minimum_available_ram_gb, 10.0)
        self.assertFalse(receipt.queue_mutated_by_requalification)
        self.assertFalse(receipt.generation_authorized_by_requalification)
        self.assertFalse(receipt.publication_ready)

    def test_guard_rejects_live_ram_drop(self) -> None:
        report = SimpleNamespace(
            ready=False,
            cost_mode="$0-local",
            available_ram_gb=6.5,
            minimum_available_ram_gb=10.0,
            total_ram_gb=31.0,
            measurement_source="/proc/meminfo",
            reasons=("available_system_ram_below_first_golden_floor",),
        )
        probe = SimpleNamespace(inspect=lambda: report)
        with patch(
            "engine.intelligence.worker_host_memory_guard.HostMemoryQualificationProbe",
            return_value=probe,
        ):
            with self.assertRaisesRegex(RuntimeError, "live host-memory requalification failed"):
                WorkerHostMemoryGuard().inspect()

    def test_guard_rejects_unproven_available_ram(self) -> None:
        report = SimpleNamespace(
            ready=True,
            cost_mode="$0-local",
            available_ram_gb=None,
            minimum_available_ram_gb=10.0,
            total_ram_gb=31.0,
            measurement_source="/proc/meminfo",
            reasons=(),
        )
        probe = SimpleNamespace(inspect=lambda: report)
        with patch(
            "engine.intelligence.worker_host_memory_guard.HostMemoryQualificationProbe",
            return_value=probe,
        ):
            with self.assertRaisesRegex(RuntimeError, "did not prove MemAvailable"):
                WorkerHostMemoryGuard().inspect()

    def test_gpu_worker_combines_gpu_and_host_memory_before_store_creation(self) -> None:
        source = Path(phase18_gpu_worker.__file__).read_text(encoding="utf-8")
        main = source[source.index("def main()") :]
        requalify = main.index("initial_execution_host = _requalify_execution_host(capabilities)")
        store = main.index("FilesystemGenerationJobStore(")
        self.assertLess(requalify, store)
        self.assertIn('initial_execution_host["gpu"]', main)
        self.assertIn('initial_execution_host["host_memory"]', main)

    def test_gpu_worker_lease_bound_guard_rechecks_both_resources(self) -> None:
        source = Path(phase18_gpu_worker.__file__).read_text(encoding="utf-8")
        service_start = source.index("service = GenerationWorkerService(")
        service_end = source.index("initial_snapshot =", service_start)
        service = source[service_start:service_end]
        self.assertIn("pre_execute_guard=", service)
        self.assertIn("_requalify_execution_host(capabilities)", service)

    def test_cycle_requalification_precedes_queue_recovery(self) -> None:
        source = Path(phase18_gpu_worker.__file__).read_text(encoding="utf-8")
        loop = source.index("while True:")
        combined = source.index("_requalify_execution_host(capabilities)", loop)
        recovery = source.index("store.recover_expired", loop)
        run_once = source.index("service.run_once", loop)
        self.assertLess(combined, recovery)
        self.assertLess(combined, run_once)


if __name__ == "__main__":
    unittest.main()
