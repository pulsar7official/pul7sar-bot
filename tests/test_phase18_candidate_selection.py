import unittest

from engine.intelligence.base_scene_quality import (
    BaseSceneEvidence, GenerationDefectEvidence, IdentityVisualEvidence,
    ProtectedRegionEvidence, SubjectFramingEvidence,
)
from engine.intelligence.candidate_selection import (
    BoundedRegenerationController, CandidateOutcome, QualityFirstCandidateSelector,
    RegenerationPolicy,
)
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.provider_adapter import (
    AdapterMismatchError, ProviderAdapterRegistry, ProviderRawGeneration,
)


class _Adapter:
    provider_id = "free-local"

    def normalize(self, raw, package):
        return BaseSceneEvidence(
            provider_id=raw.provider_id,
            output_ref=raw.output_ref,
            width=1080,
            height=1920,
            aspect_ratio="9:16",
            framing=SubjectFramingEvidence(True, True, True, raw.payload.get("framing", 0.95)),
            identity=IdentityVisualEvidence(True, True, raw.payload.get("identity", 0.96), ("verified-ref",)),
            protected_regions=(
                ProtectedRegionEvidence("logo", True, raw.payload.get("logo_occ", 0.02)),
                ProtectedRegionEvidence("headline", True, raw.payload.get("headline_occ", 0.05)),
                ProtectedRegionEvidence("social_footer", True, raw.payload.get("footer_occ", 0.02)),
            ),
            defects=GenerationDefectEvidence(True),
            provenance={"provider": raw.provider_id, "request_id": raw.payload.get("request_id", "req")},
        )


class _BadAdapter(_Adapter):
    provider_id = "bad"
    def normalize(self, raw, package):
        evidence = super().normalize(raw, package)
        return BaseSceneEvidence(
            provider_id="different-provider",
            output_ref=evidence.output_ref,
            width=evidence.width,
            height=evidence.height,
            aspect_ratio=evidence.aspect_ratio,
            framing=evidence.framing,
            identity=evidence.identity,
            protected_regions=evidence.protected_regions,
            defects=evidence.defects,
            provenance=evidence.provenance,
        )


class CandidateSelectionTests(unittest.TestCase):
    def setUp(self):
        self.package = GenerationPackage(
            platform="instagram_story",
            canvas="1080x1920",
            scene_prompt="approved",
            negative_constraints=("no humiliation",),
            asset_ids=("pul7sar-logo",),
            factual_constraints=("verified fact",),
            layout_boxes={
                "hero": {"x": 100, "y": 300, "width": 800, "height": 900},
                "logo": {"x": 80, "y": 100, "width": 250, "height": 90},
                "headline": {"x": 100, "y": 1300, "width": 880, "height": 260},
                "social_footer": {"x": 200, "y": 1700, "width": 680, "height": 70},
            },
            accent_hex="#E10600",
        )
        self.registry = ProviderAdapterRegistry((_Adapter(),))
        self.selector = QualityFirstCandidateSelector()

    def normalized(self, output_ref, **payload):
        return self.registry.normalize(
            ProviderRawGeneration("free-local", output_ref, payload),
            self.package,
        )

    def test_registry_normalizes_provider_payload(self):
        evidence = self.normalized("scene://1", identity=0.98)
        self.assertEqual(evidence.provider_id, "free-local")
        self.assertEqual(evidence.output_ref, "scene://1")
        self.assertEqual(evidence.identity.confidence, 0.98)

    def test_unknown_provider_adapter_is_rejected(self):
        with self.assertRaises(AdapterMismatchError):
            self.registry.normalize(ProviderRawGeneration("unknown", "scene://1", {}), self.package)

    def test_adapter_cannot_relabel_provider(self):
        registry = ProviderAdapterRegistry((_BadAdapter(),))
        with self.assertRaises(AdapterMismatchError):
            registry.normalize(ProviderRawGeneration("bad", "scene://1", {}), self.package)

    def test_best_accepted_candidate_wins_by_quality_not_cost(self):
        a = self.normalized("scene://a", identity=0.92, framing=0.90, headline_occ=0.10)
        b = self.normalized("scene://b", identity=0.99, framing=0.98, headline_occ=0.02)
        result = self.selector.select(self.package, (a, b), attempts_used=1)
        self.assertEqual(result.outcome, CandidateOutcome.ACCEPTED)
        self.assertEqual(result.selected.evidence.output_ref, "scene://b")
        self.assertGreater(result.selected.quality_score, 0.95)

    def test_rejected_candidate_never_gets_quality_score(self):
        bad = self.normalized("scene://bad", identity=0.70)
        evaluation = self.selector.evaluate(self.package, bad)
        self.assertFalse(evaluation.decision.accepted)
        self.assertEqual(evaluation.quality_score, 0.0)

    def test_no_acceptable_scene_returns_explicit_outcome(self):
        bad = self.normalized("scene://bad", identity=0.70)
        result = self.selector.select(self.package, (bad,), attempts_used=2)
        self.assertEqual(result.outcome, CandidateOutcome.NO_ACCEPTABLE_SCENE)
        self.assertIsNone(result.selected)
        self.assertTrue(result.rejection_reasons)

    def test_retry_is_bounded_but_never_degrades_quality(self):
        controller = BoundedRegenerationController(RegenerationPolicy(max_attempts=3, candidates_per_attempt=2))
        bad = self.normalized("scene://bad", identity=0.70)
        result = self.selector.select(self.package, (bad,), attempts_used=1)
        self.assertTrue(controller.may_retry(attempts_used=1, selection=result))
        self.assertFalse(controller.may_retry(attempts_used=3, selection=result))
        with self.assertRaises(ValueError):
            controller.assert_within_bounds(attempts_used=3)

    def test_accepted_scene_stops_retry_immediately(self):
        good = self.normalized("scene://good")
        result = self.selector.select(self.package, (good,), attempts_used=1)
        controller = BoundedRegenerationController()
        self.assertFalse(controller.may_retry(attempts_used=1, selection=result))


if __name__ == "__main__":
    unittest.main()
