import unittest

from engine.intelligence.base_scene_quality import (
    BaseSceneEvidence, GenerationDefectEvidence, IdentityVisualEvidence,
    ProtectedRegionEvidence, SubjectFramingEvidence,
)
from engine.intelligence.candidate_selection import CandidateOutcome, RegenerationPolicy, BoundedRegenerationController
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.generation_session import GenerationSessionOrchestrator
from engine.intelligence.provider_adapter import ProviderAdapterRegistry, ProviderRawGeneration


class FakeAdapter:
    provider_id = "free-local"

    def normalize(self, raw, package):
        p = raw.payload
        return BaseSceneEvidence(
            provider_id=raw.provider_id,
            output_ref=raw.output_ref,
            width=p.get("width", 1080),
            height=p.get("height", 1920),
            aspect_ratio=p.get("aspect_ratio", "9:16"),
            framing=SubjectFramingEvidence(True, True, True, p.get("framing", 0.96)),
            identity=IdentityVisualEvidence(True, p.get("identity_match", True), p.get("identity", 0.97), ("ref-1",)),
            protected_regions=(
                ProtectedRegionEvidence("logo", True, p.get("logo_occ", 0.03)),
                ProtectedRegionEvidence("headline", True, p.get("headline_occ", 0.08)),
                ProtectedRegionEvidence("social_footer", True, p.get("footer_occ", 0.02)),
            ),
            defects=GenerationDefectEvidence(p.get("defect_free", True), tuple(p.get("defects", ()))),
            forbidden_visuals_detected=tuple(p.get("forbidden", ())),
            safe_crop_possible=p.get("safe_crop", True),
            provenance={"provider": raw.provider_id, "request_id": raw.output_ref},
        )


class FakeProvider:
    provider_id = "free-local"

    def __init__(self, attempts):
        self.attempts = attempts
        self.calls = 0

    def generate_attempt(self, package, *, attempt_number, candidate_count):
        self.calls += 1
        payloads = self.attempts[attempt_number - 1]
        return tuple(
            ProviderRawGeneration(self.provider_id, f"scene://{attempt_number}-{index}", payload)
            for index, payload in enumerate(payloads[:candidate_count], 1)
        )


class GenerationSessionTests(unittest.TestCase):
    def setUp(self):
        self.package = GenerationPackage(
            platform="instagram_story",
            canvas="1080x1920",
            scene_prompt="approved",
            negative_constraints=("no humiliation",),
            asset_ids=("pul7sar-logo",),
            factual_constraints=("fact",),
            layout_boxes={
                "hero": {"x": 100, "y": 300, "width": 800, "height": 900},
                "logo": {"x": 80, "y": 100, "width": 250, "height": 90},
                "headline": {"x": 100, "y": 1300, "width": 880, "height": 260},
                "social_footer": {"x": 200, "y": 1700, "width": 680, "height": 70},
            },
            accent_hex="#E10600",
        )
        self.registry = ProviderAdapterRegistry((FakeAdapter(),))

    def orchestrator(self, min_quality=0.90, max_attempts=3):
        return GenerationSessionOrchestrator(
            adapters=self.registry,
            regeneration=BoundedRegenerationController(RegenerationPolicy(max_attempts=max_attempts, candidates_per_attempt=2)),
            minimum_quality_score=min_quality,
        )

    def test_first_high_quality_attempt_stops_immediately(self):
        provider = FakeProvider([[{"identity": 0.99, "framing": 0.98, "headline_occ": 0.02}]])
        result = self.orchestrator().run(self.package, provider)
        self.assertEqual(result.outcome, CandidateOutcome.ACCEPTED)
        self.assertEqual(result.attempts_used, 1)
        self.assertEqual(provider.calls, 1)

    def test_rejected_first_attempt_retries(self):
        provider = FakeProvider([
            [{"identity_match": False}],
            [{"identity": 0.99, "framing": 0.99, "headline_occ": 0.01}],
        ])
        result = self.orchestrator().run(self.package, provider)
        self.assertEqual(result.outcome, CandidateOutcome.ACCEPTED)
        self.assertEqual(result.attempts_used, 2)
        self.assertEqual(provider.calls, 2)

    def test_gate_pass_but_quality_below_floor_retries(self):
        provider = FakeProvider([
            [{"identity": 0.90, "framing": 0.85, "logo_occ": 0.17, "headline_occ": 0.17, "footer_occ": 0.17}],
            [{"identity": 0.99, "framing": 0.99, "logo_occ": 0.01, "headline_occ": 0.01, "footer_occ": 0.01}],
        ])
        result = self.orchestrator(min_quality=0.94).run(self.package, provider)
        self.assertEqual(result.outcome, CandidateOutcome.ACCEPTED)
        self.assertEqual(result.attempts_used, 2)
        self.assertEqual(len(result.diagnostics), 2)
        self.assertEqual(result.diagnostics[0].candidate_count, 1)
        self.assertEqual(result.diagnostics[0].accepted_count, 1)
        self.assertEqual(result.diagnostics[1].candidate_count, 1)
        self.assertEqual(result.diagnostics[1].accepted_count, 1)
        self.assertTrue(any("below minimum" in r for r in result.diagnostics[0].rejection_reasons))

    def test_no_best_bad_fallback_after_attempt_limit(self):
        provider = FakeProvider([
            [{"identity_match": False}],
            [{"defect_free": False, "defects": ("warped face",)}],
        ])
        result = self.orchestrator(max_attempts=2).run(self.package, provider)
        self.assertEqual(result.outcome, CandidateOutcome.NO_ACCEPTABLE_SCENE)
        self.assertIsNone(result.selection.selected)
        self.assertEqual(result.attempts_used, 2)

    def test_quality_floor_can_reject_gate_passing_candidates(self):
        provider = FakeProvider([
            [{"identity": 0.90, "framing": 0.85, "logo_occ": 0.17, "headline_occ": 0.17, "footer_occ": 0.17}],
        ])
        result = self.orchestrator(min_quality=0.99, max_attempts=1).run(self.package, provider)
        self.assertEqual(result.outcome, CandidateOutcome.NO_ACCEPTABLE_SCENE)
        self.assertTrue(any("below minimum" in r for r in result.selection.rejection_reasons))

    def test_provider_cannot_return_more_candidates_than_requested(self):
        class BadProvider(FakeProvider):
            def generate_attempt(self, package, *, attempt_number, candidate_count):
                return tuple(ProviderRawGeneration(self.provider_id, f"scene://{i}", {}) for i in range(candidate_count + 1))
        with self.assertRaises(ValueError):
            self.orchestrator().run(self.package, BadProvider([[]]))

    def test_provider_identity_mismatch_is_rejected(self):
        class WrongProvider(FakeProvider):
            def generate_attempt(self, package, *, attempt_number, candidate_count):
                return (ProviderRawGeneration("other-provider", "scene://wrong", {}),)
        with self.assertRaises(ValueError):
            self.orchestrator().run(self.package, WrongProvider([[]]))


if __name__ == "__main__":
    unittest.main()
