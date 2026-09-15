import tempfile
import unittest
from pathlib import Path

from PIL import Image

from engine.intelligence.base_scene_composition_admission import BaseSceneCompositionAdmissionCompiler
from engine.intelligence.base_scene_execution_gate import BaseSceneExecutionDecision
from engine.intelligence.event_editorial_composition import EventEditorialComposer
from engine.intelligence.event_editorial_hybrid_renderer import EventEditorialHybridRenderer
from engine.intelligence.local_generation_provenance import LocalGenerationProvenance
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.visual_layer_qa import LayerLeakageEvidence
from engine.intelligence.zero_cost_models import ImageQualityTier


class EventEditorialHybridRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.composition = EventEditorialComposer().plan(self.profile)
        self.font = next((p for p in (
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        ) if p.is_file()), None)
        if self.font is None:
            self.skipTest('DejaVu font unavailable')

    def _admission(self, root: Path):
        base = root/'base.png'
        Image.new('RGB', (self.profile.width, self.profile.height), (17, 29, 45)).save(base)
        provenance = LocalGenerationProvenance(
            'local-qwen-image-2512', 'Qwen/Qwen-Image-2512', 'diffusers', 2512, 'event-base',
            self.profile.width, self.profile.height, {'image_quality_tier': 'elite'},
        )
        decision = BaseSceneExecutionDecision(True, True, (), LayerLeakageEvidence())
        return BaseSceneCompositionAdmissionCompiler().compile(
            png_path=str(base), provenance=provenance, execution_decision=decision, quality_tier=ImageQualityTier.ELITE,
        )

    def test_elite_event_base_keeps_symbolic_anchor_generative_but_text_brand_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            admission = self._admission(root)
            receipt = EventEditorialHybridRenderer().render(
                self.composition, admission=admission, profile=self.profile,
                output_path=str(root/'event.png'), headline='NEW ERA', kicker='OFFICIAL ANNOUNCEMENT',
                accent_hex='#C71925', font_path=str(self.font),
            )
            self.assertEqual(receipt.contract, 'pul7sar-event-editorial-hybrid-renderer-v1-cinematic')
            self.assertEqual(receipt.base_quality_tier, 'elite')
            self.assertTrue(receipt.generator_owns_nonfactual_symbolic_anchor)
            self.assertFalse(receipt.generator_owns_readable_text)
            self.assertFalse(receipt.generator_owns_brand)
            self.assertFalse(receipt.person_inserted)
            self.assertFalse(receipt.exact_data_inserted)
            self.assertFalse(receipt.publication_ready)

    def test_tampered_base_after_admission_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            admission = self._admission(root)
            Path(admission.png_path).write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'BYTES_CHANGED'):
                EventEditorialHybridRenderer().render(
                    self.composition, admission=admission, profile=self.profile,
                    output_path=str(root/'event.png'), headline='NEW ERA', kicker='OFFICIAL ANNOUNCEMENT',
                    accent_hex='#C71925', font_path=str(self.font),
                )


if __name__ == '__main__':
    unittest.main()
