import unittest

from engine.intelligence.original_scene_request_builder import OriginalSceneRequestBuilder
from engine.intelligence.original_scene_runtime_contract import OriginalSceneRuntimeKind
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily
from engine.intelligence.visual_concept_director import VisualConceptDirector, VisualConceptSignals


class OriginalSceneRequestBuilderTests(unittest.TestCase):
    def setUp(self):
        self.director = VisualConceptDirector()
        self.builder = OriginalSceneRequestBuilder()

    def test_result_atmosphere_becomes_provider_neutral_request(self):
        decision = self.director.direct(
            EditorialSceneFamily.RESULT_STATEMENT,
            VisualConceptSignals(safe_generated_context=True, exact_club_assets=True),
        )
        req = self.builder.build(
            decision,
            emotional_tone="controlled victorious energy",
            safe_negative_space="upper-left",
            context_reference_ids=("verified-reference:001",),
            seed=7,
        )
        self.assertEqual(req.runtime_kind, OriginalSceneRuntimeKind.ATMOSPHERE)
        self.assertIn("readable_text", req.exact_fact_roles_reserved_for_compositor)
        self.assertIn("PUL7SAR logo generated into scene", req.forbidden_visual_claims)
        self.assertEqual(req.seed, 7)

    def test_verified_subject_becomes_identity_conditioned_request(self):
        decision = self.director.direct(
            EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
            VisualConceptSignals(verified_subject_asset=True, story_requires_person=True),
        )
        req = self.builder.build(
            decision,
            emotional_tone="serious editorial restraint",
            safe_negative_space="right third",
            identity_reference_ids=("verified-person:001",),
        )
        self.assertEqual(req.runtime_kind, OriginalSceneRuntimeKind.IDENTITY_CONDITIONED)
        self.assertEqual(req.identity_reference_ids, ("verified-person:001",))

    def test_deterministic_concept_never_enters_generator(self):
        decision = self.director.direct(
            EditorialSceneFamily.RESULT_STATEMENT,
            VisualConceptSignals(exact_club_assets=True),
        )
        with self.assertRaisesRegex(ValueError, "VISUAL_CONCEPT_DOES_NOT_REQUIRE_ORIGINAL_SCENE_RUNTIME"):
            self.builder.build(decision, emotional_tone="neutral", safe_negative_space="top")


if __name__ == "__main__":
    unittest.main()
