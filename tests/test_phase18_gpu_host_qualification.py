import unittest

from engine.intelligence.gpu_host_qualification import GpuHostQualificationPolicy
from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


class GpuHostQualificationTests(unittest.TestCase):
    def setUp(self):
        self.policy = GpuHostQualificationPolicy()

    def test_qualified_host(self):
        runtime = RuntimeHardwareSnapshot(
            kind=RuntimeKind.LOCAL_CUDA,
            cuda_available=True,
            gpu_name="Test GPU",
            gpu_vram_gb=24.0,
            torch_available=True,
            metadata={"bf16_supported": True, "compute_capability": "8.9"},
        )
        result = self.policy.evaluate(runtime=runtime, model=FLUX2_KLEIN_4B_LOCAL)
        self.assertTrue(result.eligible)
        self.assertEqual(result.reasons, ())

    def test_low_vram_is_not_qualified(self):
        runtime = RuntimeHardwareSnapshot(
            kind=RuntimeKind.LOCAL_CUDA,
            cuda_available=True,
            gpu_name="Test GPU",
            gpu_vram_gb=12.0,
            torch_available=True,
            metadata={"bf16_supported": True, "compute_capability": "8.0"},
        )
        result = self.policy.evaluate(runtime=runtime, model=FLUX2_KLEIN_4B_LOCAL)
        self.assertFalse(result.eligible)

    def test_bf16_must_be_proven(self):
        runtime = RuntimeHardwareSnapshot(
            kind=RuntimeKind.LOCAL_CUDA,
            cuda_available=True,
            gpu_name="Test GPU",
            gpu_vram_gb=24.0,
            torch_available=True,
            metadata={"bf16_supported": None, "compute_capability": "8.0"},
        )
        result = self.policy.evaluate(runtime=runtime, model=FLUX2_KLEIN_4B_LOCAL)
        self.assertFalse(result.eligible)
        self.assertIn("native BF16 support is not proven", result.reasons)

    def test_compute_capability_must_be_proven(self):
        runtime = RuntimeHardwareSnapshot(
            kind=RuntimeKind.LOCAL_CUDA,
            cuda_available=True,
            gpu_name="Test GPU",
            gpu_vram_gb=24.0,
            torch_available=True,
            metadata={"bf16_supported": True},
        )
        result = self.policy.evaluate(runtime=runtime, model=FLUX2_KLEIN_4B_LOCAL)
        self.assertFalse(result.eligible)

    def test_cpu_host_is_not_qualified(self):
        runtime = RuntimeHardwareSnapshot(
            kind=RuntimeKind.LOCAL_CPU,
            cuda_available=False,
            torch_available=True,
            metadata={"bf16_supported": True, "compute_capability": "8.0"},
        )
        result = self.policy.evaluate(runtime=runtime, model=FLUX2_KLEIN_4B_LOCAL)
        self.assertFalse(result.eligible)


if __name__ == "__main__":
    unittest.main()
