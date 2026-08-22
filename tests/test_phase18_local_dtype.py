import unittest

from engine.intelligence.local_dtype import LocalDTypeSelector
from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind


class LocalDTypeSelectorTests(unittest.TestCase):
    def runtime(self, bf16):
        return RuntimeHardwareSnapshot(
            RuntimeKind.LOCAL_CUDA,
            True,
            gpu_name="Test GPU",
            gpu_vram_gb=16.0,
            torch_available=True,
            metadata={"bf16_supported": bf16},
        )

    def test_auto_prefers_bfloat16_when_proven(self):
        decision = LocalDTypeSelector().select(self.runtime(True), "auto")
        self.assertEqual(decision.resolved, "bfloat16")

    def test_auto_uses_float16_when_bfloat16_is_not_supported(self):
        decision = LocalDTypeSelector().select(self.runtime(False), "auto")
        self.assertEqual(decision.resolved, "float16")

    def test_auto_uses_conservative_float16_when_capability_unknown(self):
        decision = LocalDTypeSelector().select(self.runtime(None), "auto")
        self.assertEqual(decision.resolved, "float16")

    def test_explicit_bfloat16_fails_when_not_proven(self):
        with self.assertRaisesRegex(ValueError, "support is not proven"):
            LocalDTypeSelector().select(self.runtime(False), "bfloat16")

    def test_explicit_float16_is_allowed(self):
        decision = LocalDTypeSelector().select(self.runtime(False), "float16")
        self.assertEqual(decision.resolved, "float16")

    def test_cpu_runtime_is_rejected(self):
        runtime = RuntimeHardwareSnapshot(RuntimeKind.LOCAL_CPU, False, torch_available=True)
        with self.assertRaisesRegex(ValueError, "CUDA runtime"):
            LocalDTypeSelector().select(runtime, "auto")


if __name__ == "__main__":
    unittest.main()
