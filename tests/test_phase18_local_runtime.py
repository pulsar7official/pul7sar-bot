import unittest
from types import SimpleNamespace
from unittest.mock import patch

import engine.intelligence.local_runtime as local_runtime
from engine.intelligence.local_runtime import (
    LocalModelRuntimeGate, LocalRuntimeProbe, RuntimeHardwareSnapshot, RuntimeKind,
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

    def test_cuda_probe_records_live_free_and_used_vram(self):
        gib = 1024 ** 3

        class FakeCuda:
            @staticmethod
            def is_available():
                return True

            @staticmethod
            def current_device():
                return 0

            @staticmethod
            def get_device_properties(device):
                self.assertEqual(device, 0)
                return SimpleNamespace(name="Mock CUDA GPU", total_memory=24 * gib)

            @staticmethod
            def mem_get_info(device):
                self.assertEqual(device, 0)
                return (20 * gib, 24 * gib)

            @staticmethod
            def is_bf16_supported():
                return True

            @staticmethod
            def get_device_capability(device):
                self.assertEqual(device, 0)
                return (8, 9)

        fake_torch = SimpleNamespace(cuda=FakeCuda(), __version__="2.test")
        with patch.object(local_runtime, "import_module", return_value=fake_torch):
            snapshot = LocalRuntimeProbe().detect()

        self.assertEqual(snapshot.kind, RuntimeKind.LOCAL_CUDA)
        self.assertEqual(snapshot.gpu_vram_gb, 24.0)
        self.assertEqual(snapshot.metadata["gpu_free_vram_gb"], 20.0)
        self.assertEqual(snapshot.metadata["gpu_used_vram_gb"], 4.0)
        self.assertTrue(snapshot.metadata["bf16_supported"])
        self.assertEqual(snapshot.metadata["compute_capability"], "8.9")

    def test_cuda_probe_does_not_invent_free_vram_when_mem_get_info_fails(self):
        gib = 1024 ** 3

        class FakeCuda:
            @staticmethod
            def is_available():
                return True

            @staticmethod
            def current_device():
                return 0

            @staticmethod
            def get_device_properties(device):
                return SimpleNamespace(name="Mock CUDA GPU", total_memory=24 * gib)

            @staticmethod
            def mem_get_info(device):
                raise RuntimeError("driver telemetry unavailable")

            @staticmethod
            def is_bf16_supported():
                return True

            @staticmethod
            def get_device_capability(device):
                return (8, 0)

        fake_torch = SimpleNamespace(cuda=FakeCuda(), __version__="2.test")
        with patch.object(local_runtime, "import_module", return_value=fake_torch):
            snapshot = LocalRuntimeProbe().detect()

        self.assertIsNone(snapshot.metadata["gpu_free_vram_gb"])
        self.assertIsNone(snapshot.metadata["gpu_used_vram_gb"])


if __name__ == "__main__":
    unittest.main()
