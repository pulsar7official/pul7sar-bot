import unittest

from engine.intelligence.local_backend import LocalBackendKind, LocalBackendReadinessGate, LocalBackendSnapshot
from engine.intelligence.local_readiness_report import LocalGenerationReadinessReport
from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


class LocalReadinessReportTests(unittest.TestCase):
    def test_ready_report_is_machine_readable(self):
        runtime = RuntimeHardwareSnapshot(RuntimeKind.LOCAL_CUDA, True, "GPU", 16.0, True)
        backend = LocalBackendSnapshot(LocalBackendKind.DIFFUSERS, True, version="test")
        decision = LocalBackendReadinessGate().evaluate(model=FLUX2_KLEIN_4B_LOCAL, runtime=runtime, backend=backend)
        report = LocalGenerationReadinessReport.build(model=FLUX2_KLEIN_4B_LOCAL, runtime=runtime, backend=backend, readiness=decision)
        data = report.as_dict()
        self.assertTrue(data["ready"])
        self.assertEqual(data["cost_mode"], "$0-local")
        self.assertEqual(data["gpu_vram_gb"], 16.0)

    def test_blockers_are_preserved(self):
        runtime = RuntimeHardwareSnapshot(RuntimeKind.LOCAL_CPU, False, None, None, False)
        backend = LocalBackendSnapshot(LocalBackendKind.DIFFUSERS, False)
        decision = LocalBackendReadinessGate().evaluate(model=FLUX2_KLEIN_4B_LOCAL, runtime=runtime, backend=backend)
        report = LocalGenerationReadinessReport.build(model=FLUX2_KLEIN_4B_LOCAL, runtime=runtime, backend=backend, readiness=decision)
        self.assertFalse(report.ready)
        self.assertGreaterEqual(len(report.blockers), 2)


if __name__ == "__main__":
    unittest.main()
