import tempfile
import unittest
from pathlib import Path

from engine.intelligence.cross_family_visual_system import CrossFamilyVisualDecision, CrossFamilyVisualSystem
from engine.intelligence.original_family_scene_renderer import FamilySceneRequest, OriginalFamilySceneRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_scene_blueprint import VisualSceneBlueprintCompiler

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class OriginalFamilySceneRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.renderer = OriginalFamilySceneRenderer()
        self.compiler = VisualSceneBlueprintCompiler()

    def _request(self, family, archetype_id, seed=18):
        archetype = next(a for a in CrossFamilyVisualSystem.archetypes(family) if a.id == archetype_id)
        decision = CrossFamilyVisualDecision(family, archetype, seed, False)
        blueprint = self.compiler.compile(decision)
        return FamilySceneRequest(
            blueprint=blueprint,
            headline="ORIGINAL VISUAL STUDY",
            primary_label="PRIMARY FACT",
            secondary_label="SECONDARY SIDE",
            primary_value="3–1" if family is EditorialSceneFamily.RESULT_STATEMENT else "27",
            seed=seed,
        )

    def test_all_six_families_render_without_external_pixels(self):
        choices = {
            EditorialSceneFamily.TRANSFER_SIGNATURE: "threshold_arrival",
            EditorialSceneFamily.RESULT_STATEMENT: "arena_outcome",
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: "absence_space",
            EditorialSceneFamily.TACTICAL_BOARD: "phase_corridor",
            EditorialSceneFamily.DATA_MONUMENT: "number_sculpture",
            EditorialSceneFamily.EVENT_EDITORIAL: "object_story",
        }
        with tempfile.TemporaryDirectory() as td:
            digests=set()
            for family, aid in choices.items():
                receipt=self.renderer.render(self._request(family,aid),profile=self.profile,output_path=str(Path(td)/f"{family.value}.png"),font_path=FONT)
                self.assertEqual((receipt.width,receipt.height),(1080,1350))
                self.assertFalse(receipt.source_photo_used)
                self.assertFalse(receipt.generator_used)
                self.assertFalse(receipt.network_used)
                self.assertFalse(receipt.fabricated_crest_used)
                self.assertFalse(receipt.placeholder_used)
                self.assertFalse(receipt.real_person_depicted)
                self.assertFalse(receipt.publication_ready)
                digests.add(receipt.output_sha256)
            self.assertEqual(len(digests),6)

    def test_two_archetypes_in_same_family_are_visually_distinct(self):
        with tempfile.TemporaryDirectory() as td:
            a=self.renderer.render(self._request(EditorialSceneFamily.RESULT_STATEMENT,"club_duel_space",18),profile=self.profile,output_path=str(Path(td)/"a.png"),font_path=FONT)
            b=self.renderer.render(self._request(EditorialSceneFamily.RESULT_STATEMENT,"arena_outcome",18),profile=self.profile,output_path=str(Path(td)/"b.png"),font_path=FONT)
            self.assertNotEqual(a.output_sha256,b.output_sha256)

    def test_same_request_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            req=self._request(EditorialSceneFamily.EVENT_EDITORIAL,"anticipation_tunnel",19)
            a=self.renderer.render(req,profile=self.profile,output_path=str(Path(td)/"a.png"),font_path=FONT)
            b=self.renderer.render(req,profile=self.profile,output_path=str(Path(td)/"b.png"),font_path=FONT)
            self.assertEqual(a.output_sha256,b.output_sha256)
            self.assertEqual(Path(a.output_path).read_bytes(),Path(b.output_path).read_bytes())


if __name__ == "__main__": unittest.main()
