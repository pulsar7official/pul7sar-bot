import unittest

from engine.intelligence.base_scene_layer_evidence import BaseSceneLayerEvidenceAdapter
from engine.intelligence.base_scene_quality import (
    BaseSceneEvidence,
    GenerationDefectEvidence,
    IdentityVisualEvidence,
    SubjectFramingEvidence,
)


class BaseSceneLayerEvidenceAdapterTests(unittest.TestCase):
    def evidence(self, *, forbidden=(), complete=True):
        return BaseSceneEvidence(
            provider_id="local-flux2-klein-4b",
            output_ref="proof.png",
            width=1080,
            height=1080,
            aspect_ratio="1:1",
            framing=SubjectFramingEvidence(True, True, True, 1.0),
            identity=IdentityVisualEvidence(False, False, 1.0),
            protected_regions=(),
            defects=GenerationDefectEvidence(True),
            forbidden_visuals_detected=forbidden,
            safe_crop_possible=True,
            provenance={
                "request_id": "candidate-1",
                "forbidden_visual_inspection_complete": complete,
            },
        )

    def test_complete_clean_inspection_maps_to_clean_layer_evidence(self):
        result = BaseSceneLayerEvidenceAdapter().adapt(self.evidence())
        self.assertTrue(result.complete)
        self.assertFalse(result.evidence.generated_text_detected)
        self.assertFalse(result.evidence.generated_platform_brand_detected)
        self.assertFalse(result.evidence.generated_sport_geometry_detected)

    def test_known_probe_tokens_map_to_exact_layer_flags(self):
        result = BaseSceneLayerEvidenceAdapter().adapt(self.evidence(forbidden=(
            "generated_text",
            "generated_platform_brand",
            "generated_sport_geometry",
        )))
        self.assertTrue(result.complete)
        self.assertTrue(result.evidence.generated_text_detected)
        self.assertTrue(result.evidence.generated_platform_brand_detected)
        self.assertTrue(result.evidence.generated_sport_geometry_detected)

    def test_missing_completeness_proof_fails_closed(self):
        adapter = BaseSceneLayerEvidenceAdapter()
        result = adapter.adapt(self.evidence(complete=False))
        self.assertFalse(result.complete)
        self.assertIn("forbidden_visual_inspection_not_proven_complete", result.blockers)
        with self.assertRaisesRegex(ValueError, "BASE_SCENE_LAYER_EVIDENCE_INCOMPLETE"):
            adapter.assert_complete(result)

    def test_unknown_forbidden_observation_fails_closed(self):
        result = BaseSceneLayerEvidenceAdapter().adapt(self.evidence(forbidden=("mystery_visual",)))
        self.assertFalse(result.complete)
        self.assertIn("unclassified_forbidden_visual_observation", result.blockers)
        self.assertIn("unclassified:mystery_visual", result.evidence.notes)


if __name__ == "__main__":
    unittest.main()
