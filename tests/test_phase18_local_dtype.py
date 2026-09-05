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

    def test_auto_selects_bfloat16_when_proven(self):
        decision = LocalDTypeSelector().select(self.runtime(True), "auto")
        self.assertEqual(decision.resolved, "bfloat16")
        self.assertEqual(decision.quality_tier, "golden_reference")

    def test_auto_fails_closed_when_bfloat16_is_not_supported(self):
        with self.assertRaisesRegex(ValueError, "no native bfloat16 support"):
            LocalDTypeSelector().select(self.runtime(False), "auto")

    def test_auto_fails_closed_when_bfloat16_capability_is_unknown(self):
        with self.assertRaisesRegex(ValueError, "could not be proven"):
            LocalDTypeSelector().select(self.runtime(None), "auto")

    def test_explicit_bfloat16_fails_when_not_proven(self):
        with self.assertRaisesRegex(ValueError, "no native bfloat16 support"):
            LocalDTypeSelector().select(self.runtime(False), "bfloat16")

    def test_explicit_float16_preview_is_allowed_without_bf16(self):
        decision = LocalDTypeSelector().select(self.runtime(False), "float16-preview")
        self.assertEqual(decision.requested, "float16-preview")
        self.assertEqual(decision.resolved, "float16")
        self.assertEqual(decision.quality_tier, "t4_engineering_preview")

    def test_float16_preview_never_claims_golden_reference(self):
        decision = LocalDTypeSelector().select(self.runtime(True), "float16-preview")
        self.assertNotEqual(decision.quality_tier, "golden_reference")

    def test_raw_float16_request_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "explicit float16-preview"):
            LocalDTypeSelector().select(self.runtime(True), "float16")

    def test_float32_request_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "explicit float16-preview"):
            LocalDTypeSelector().select(self.runtime(True), "float32")

    def test_cpu_runtime_is_rejected(self):
        runtime = RuntimeHardwareSnapshot(RuntimeKind.LOCAL_CPU, False, torch_available=True)
        with self.assertRaisesRegex(ValueError, "CUDA runtime"):
            LocalDTypeSelector().select(runtime, "auto")


if __name__ == "__main__":
    unittest.main()
