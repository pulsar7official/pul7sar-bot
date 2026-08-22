import unittest

from engine.intelligence.local_runtime import (
    LocalModelRuntimeGate, RuntimeHardwareSnapshot, RuntimeKind,
)
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


class LocalRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.gate = LocalModelRuntimeGate()

    def test_cuda_runtime_at_declared_vram_is_compatible(self):
        runtime = RuntimeHardwareSnapshot(
            RuntimeKind.LOCAL_CUDA,
            True,
            gpu_name="Test GPU",
            gpu_vram_gb=13.0,
            torch_available=True,
        )
        self.assertTrue(self.gate.evaluate(FLUX2_KLEIN_4B_LOCAL, runtime).compatible)

    def test_insufficient_vram_fails_closed(self):
        runtime = RuntimeHardwareSnapshot(
            RuntimeKind.LOCAL_CUDA,
            True,
            gpu_name="Small GPU",
            gpu_vram_gb=8.0,
            torch_available=True,
        )
        decision = self.gate.evaluate(FLUX2_KLEIN_4B_LOCAL, runtime)
        self.assertFalse(decision.compatible)
        self.assertTrue(any("below declared minimum" in reason for reason in decision.reasons))

    def test_cpu_only_runtime_is_not_auto_approved_for_flux_candidate(self):
        runtime = RuntimeHardwareSnapshot(
            RuntimeKind.LOCAL_CPU,
            False,
            torch_available=True,
        )
        decision = self.gate.evaluate(FLUX2_KLEIN_4B_LOCAL, runtime)
        self.assertFalse(decision.compatible)
        self.assertIn("CUDA GPU runtime is not available", decision.reasons)

    def test_unknown_vram_is_not_assumed_sufficient(self):
        runtime = RuntimeHardwareSnapshot(
            RuntimeKind.LOCAL_CUDA,
            True,
            gpu_name="Unknown VRAM GPU",
            gpu_vram_gb=None,
            torch_available=True,
        )
        decision = self.gate.evaluate(FLUX2_KLEIN_4B_LOCAL, runtime)
        self.assertFalse(decision.compatible)
        self.assertIn("GPU VRAM could not be proven", decision.reasons)


if __name__ == "__main__":
    unittest.main()
