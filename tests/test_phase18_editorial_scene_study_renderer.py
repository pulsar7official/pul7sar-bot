import tempfile
import unittest
from pathlib import Path

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.editorial_scene_study_renderer import EditorialSceneStudyRenderer
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_study_handoff import VisualStudyHandoffCompiler


class EditorialSceneStudyRendererTests(unittest.TestCase):
    def setUp(self):
        self.font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
        if not self.font.is_file():
            self.font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

    def handoff(self):
        decision = StoryToVisualOrchestrator().decide(VerifiedEditorialStory(
            event=EditorialEvent.TRANSFER_CONFIRMED,
            sport="football",
            subject="Benchmark Player",
            fact_phrase="joins destination club",
            story_core="fictional transfer composition study",
            tone=HeadlineTone.NEUTRAL,
            confidence=1.0,
        ))
        return VisualStudyHandoffCompiler().compile(
            decision,
            headline="صفقة جديدة",
            supporting_copy="وجه جديد يصل إلى النادي",
        )

    def test_arabic_is_detected_and_raqm_is_required(self):
        self.assertTrue(EditorialSceneStudyRenderer._contains_arabic("صفقة جديدة"))
        self.assertFalse(EditorialSceneStudyRenderer._contains_arabic("TRANSFER"))
        try:
            EditorialSceneStudyRenderer._require_raqm()
        except RuntimeError:
            self.skipTest("Pillow RAQM unavailable on this host")

    def test_renderer_outputs_real_png_without_generator_identity_claim_or_legacy_logo(self):
        if not self.font.is_file():
            self.skipTest("DejaVu font unavailable")
        try:
            EditorialSceneStudyRenderer._require_raqm()
        except RuntimeError:
            self.skipTest("Pillow RAQM unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "editorial-study.png"
            handoff = self.handoff()
            receipt = EditorialSceneStudyRenderer().render(
                handoff,
                output_path=str(out),
                accent_hex="#034694",
                font_path=str(self.font),
                seed=7007,
            )
            self.assertTrue(out.is_file())
            self.assertTrue(out.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual((receipt.width, receipt.height), (1080, 1350))
            self.assertEqual(receipt.handoff_sha256, handoff.payload_sha256)
            self.assertEqual(receipt.contract, "pul7sar-editorial-scene-study-renderer-v3")
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.legacy_logo_used)
            self.assertFalse(receipt.verified_player_asset_used)
            self.assertTrue(receipt.subject_placeholder_used)
            self.assertTrue(receipt.arabic_raqm_used)
            self.assertTrue(receipt.study_only)
            self.assertFalse(receipt.publication_ready)

    def test_render_is_byte_deterministic_for_same_handoff_seed_and_font(self):
        if not self.font.is_file():
            self.skipTest("DejaVu font unavailable")
        try:
            EditorialSceneStudyRenderer._require_raqm()
        except RuntimeError:
            self.skipTest("Pillow RAQM unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            handoff = self.handoff()
            renderer = EditorialSceneStudyRenderer()
            a = renderer.render(handoff, output_path=str(Path(tmp)/"a.png"), accent_hex="#034694", font_path=str(self.font), seed=7007)
            b = renderer.render(handoff, output_path=str(Path(tmp)/"b.png"), accent_hex="#034694", font_path=str(self.font), seed=7007)
            self.assertEqual(a.output_sha256, b.output_sha256)


if __name__ == "__main__":
    unittest.main()
