import unittest

from engine.intelligence.local_runtime import LocalModelRuntimeGate, RuntimeHardwareSnapshot, RuntimeKind
from engine.intelligence.visual_quality_model_selector import QualitySelectionMode, VisualQualityModelSelector
from engine.intelligence.zero_cost_models import (
    FLUX2_KLEIN_4B_LOCAL,
    HIDREAM_O1_IMAGE_DEV_LOCAL,
    QWEN_IMAGE_2512_LOCAL,
    ImageModelRole,
    ImageQualityTier,
)


class VisualQualityModelSelectorTests(unittest.TestCase):
    def test_elite_cinematic_selects_qwen_and_marks_portable_only(self):
        decision = VisualQualityModelSelector().select(
            requested_tier=ImageQualityTier.ELITE,
            preferred_role=ImageModelRole.CINEMATIC_BASE_SCENE,
        )
        self.assertIs(decision.candidate, QWEN_IMAGE_2512_LOCAL)
        self.assertEqual(decision.selected_tier, ImageQualityTier.ELITE)
        self.assertTrue(decision.portable_only)
        self.assertFalse(decision.downgrade_used)

    def test_elite_subject_driven_prefers_hidream(self):
        decision = VisualQualityModelSelector().select(
            requested_tier=ImageQualityTier.ELITE,
            preferred_role=ImageModelRole.SUBJECT_DRIVEN_BASE_SCENE,
        )
        self.assertIs(decision.candidate, HIDREAM_O1_IMAGE_DEV_LOCAL)
        self.assertTrue(decision.portable_only)

    def test_strict_elite_never_falls_back_to_flux(self):
        selector = VisualQualityModelSelector((FLUX2_KLEIN_4B_LOCAL,))
        with self.assertRaisesRegex(ValueError, 'NO_ELITE_MODEL_AVAILABLE'):
            selector.select(requested_tier=ImageQualityTier.ELITE)

    def test_explicit_downgrade_is_visible_and_never_elite(self):
        selector = VisualQualityModelSelector((FLUX2_KLEIN_4B_LOCAL,))
        # Flux is engineering fallback and has no cinematic role, so even an
        # explicit downgrade may not impersonate a cinematic candidate.
        with self.assertRaisesRegex(ValueError, 'NO_EXPLICIT_DOWNGRADE'):
            selector.select(
                requested_tier=ImageQualityTier.ELITE,
                mode=QualitySelectionMode.EXPLICIT_DOWNGRADE,
            )

    def test_unproven_qwen_runtime_floor_blocks_even_large_gpu_snapshot(self):
        runtime = RuntimeHardwareSnapshot(
            kind=RuntimeKind.LOCAL_CUDA,
            cuda_available=True,
            gpu_name='Large GPU',
            gpu_vram_gb=96.0,
            torch_available=True,
        )
        decision = LocalModelRuntimeGate().evaluate(QWEN_IMAGE_2512_LOCAL, runtime)
        self.assertFalse(decision.compatible)
        self.assertTrue(any('VRAM floor has not been proven' in reason for reason in decision.reasons))

    def test_flux_proven_floor_remains_compatible_at_16gb(self):
        runtime = RuntimeHardwareSnapshot(
            kind=RuntimeKind.LOCAL_CUDA,
            cuda_available=True,
            gpu_name='GPU',
            gpu_vram_gb=16.0,
            torch_available=True,
        )
        self.assertTrue(LocalModelRuntimeGate().evaluate(FLUX2_KLEIN_4B_LOCAL, runtime).compatible)


if __name__ == '__main__':
    unittest.main()
