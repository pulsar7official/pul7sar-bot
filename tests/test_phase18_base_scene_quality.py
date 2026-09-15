import unittest

from engine.intelligence.base_scene_quality import (
    BaseSceneEvidence, BaseSceneVisualAcceptanceGate, GenerationDefectEvidence,
    IdentityVisualEvidence, ProtectedRegionEvidence, SubjectFramingEvidence,
)
from engine.intelligence.generation_package import GenerationPackage


class BaseSceneQualityTests(unittest.TestCase):
    def setUp(self):
        self.package = GenerationPackage(
            platform="instagram_story",
            canvas="1080x1920",
            scene_prompt="approved original scene",
            negative_constraints=("no fake signing", "no humiliation"),
            asset_ids=("pul7sar-logo",),
            factual_constraints=("approach story",),
            layout_boxes={
                "hero": {"x": 100, "y": 300, "width": 800, "height": 900},
                "logo": {"x": 80, "y": 100, "width": 250, "height": 90},
                "headline": {"x": 100, "y": 1300, "width": 880, "height": 260},
                "social_footer": {"x": 200, "y": 1700, "width": 680, "height": 70},
            },
            accent_hex="#EF0107",
        )
        self.gate = BaseSceneVisualAcceptanceGate()

    def evidence(self, **changes):
        data = dict(
            provider_id="provider-a",
            output_ref="scene://001",
            width=1080,
            height=1920,
            aspect_ratio="9:16",
            framing=SubjectFramingEvidence(True, True, True, 0.96),
            identity=IdentityVisualEvidence(True, True, 0.97, ("identity-ref-1",)),
            protected_regions=(
                ProtectedRegionEvidence("logo", True, 0.03),
                ProtectedRegionEvidence("headline", True, 0.08),
                ProtectedRegionEvidence("social_footer", True, 0.02),
            ),
            defects=GenerationDefectEvidence(True),
            forbidden_visuals_detected=(),
            safe_crop_possible=True,
            provenance={"provider": "provider-a", "request_id": "req-001", "model": "model-v1"},
        )
        data.update(changes)
        return BaseSceneEvidence(**data)

    def test_clean_scene_is_accepted(self):
        decision = self.gate.evaluate(self.package, self.evidence())
        self.assertTrue(decision.accepted)
        self.assertFalse(decision.failures)

    def test_wrong_resolution_is_rejected(self):
        decision = self.gate.evaluate(self.package, self.evidence(width=1024, height=1792))
        self.assertFalse(decision.accepted)
        self.assertTrue(any("resolution mismatch" in item for item in decision.failures))

    def test_identity_mismatch_is_rejected(self):
        identity = IdentityVisualEvidence(True, False, 0.98, ("identity-ref-1",))
        decision = self.gate.evaluate(self.package, self.evidence(identity=identity))
        self.assertFalse(decision.accepted)
        self.assertTrue(any("identity did not match" in item for item in decision.failures))

    def test_low_identity_confidence_is_rejected(self):
        identity = IdentityVisualEvidence(True, True, 0.72, ("identity-ref-1",))
        decision = self.gate.evaluate(self.package, self.evidence(identity=identity))
        self.assertFalse(decision.accepted)
        self.assertTrue(any("identity-reference confidence" in item for item in decision.failures))

    def test_busy_headline_region_is_rejected(self):
        regions = (
            ProtectedRegionEvidence("logo", True, 0.03),
            ProtectedRegionEvidence("headline", False, 0.55),
            ProtectedRegionEvidence("social_footer", True, 0.02),
        )
        decision = self.gate.evaluate(self.package, self.evidence(protected_regions=regions))
        self.assertFalse(decision.accepted)
        self.assertIn("protected region is not clear enough: headline", decision.failures)

    def test_missing_protected_region_evidence_is_rejected(self):
        regions = (ProtectedRegionEvidence("logo", True, 0.03),)
        decision = self.gate.evaluate(self.package, self.evidence(protected_regions=regions))
        self.assertFalse(decision.accepted)
        self.assertIn("missing protected-region evidence: headline", decision.failures)
        self.assertIn("missing protected-region evidence: social_footer", decision.failures)

    def test_generation_defects_are_rejected(self):
        defects = GenerationDefectEvidence(False, ("extra fingers", "warped equipment"))
        decision = self.gate.evaluate(self.package, self.evidence(defects=defects))
        self.assertFalse(decision.accepted)
        self.assertIn("generation defect: extra fingers", decision.failures)
        self.assertIn("generation defect: warped equipment", decision.failures)

    def test_forbidden_visual_is_rejected(self):
        decision = self.gate.evaluate(self.package, self.evidence(forbidden_visuals_detected=("fake signing ceremony",)))
        self.assertFalse(decision.accepted)
        self.assertIn("forbidden visual detected: fake signing ceremony", decision.failures)

    def test_unsafe_crop_is_rejected(self):
        decision = self.gate.evaluate(self.package, self.evidence(safe_crop_possible=False))
        self.assertFalse(decision.accepted)
        self.assertIn("safe platform crop is not possible", decision.failures)

    def test_missing_provenance_is_rejected(self):
        decision = self.gate.evaluate(self.package, self.evidence(provenance={}))
        self.assertFalse(decision.accepted)
        self.assertIn("provider provenance evidence is missing", decision.failures)

    def test_missing_request_id_is_warning_not_failure(self):
        decision = self.gate.evaluate(self.package, self.evidence(provenance={"provider": "provider-a"}))
        self.assertTrue(decision.accepted)
        self.assertIn("provider provenance does not include request_id", decision.warnings)


if __name__ == "__main__":
    unittest.main()
