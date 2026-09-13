from __future__ import annotations

import unittest

from engine.intelligence.identity import (
    IdentityEvidence,
    IdentityRequirements,
    IdentityVerifier,
)
from engine.intelligence.models import IdentityStatus


class IdentityVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.verifier = IdentityVerifier()

    def test_charlie_hull_context_verifies_golf_female_identity(self) -> None:
        requirements = IdentityRequirements(
            entity_name="Charlie Hull",
            sport="golf",
            role="golfer",
            gender="female",
        )
        evidence = [
            IdentityEvidence(
                canonical_name="Charlie Hull",
                source="trusted-sports-provider",
                confidence=0.98,
                sport="golf",
                role="golfer",
                gender="female",
                nationality="English",
            )
        ]

        plan = self.verifier.verify(requirements, evidence)

        self.assertEqual(plan.status, IdentityStatus.VERIFIED)
        self.assertTrue(plan.depiction_allowed)
        self.assertEqual(plan.sport, "golf")
        self.assertEqual(plan.gender, "female")

    def test_charlie_hull_wrong_gender_is_rejected(self) -> None:
        requirements = IdentityRequirements(
            entity_name="Charlie Hull",
            sport="golf",
            gender="female",
        )
        evidence = [
            IdentityEvidence(
                canonical_name="Charlie Hull",
                source="bad-candidate",
                confidence=0.99,
                sport="golf",
                gender="male",
            )
        ]

        plan = self.verifier.verify(requirements, evidence)

        self.assertEqual(plan.status, IdentityStatus.UNVERIFIED)
        self.assertFalse(plan.depiction_allowed)

    def test_sam_hickey_boxing_middleweight_context_verifies(self) -> None:
        requirements = IdentityRequirements(
            entity_name="Sam Hickey",
            sport="boxing",
            role="middleweight boxer",
            nationality="Scottish",
            gender="male",
        )
        evidence = [
            IdentityEvidence(
                canonical_name="Sam Hickey",
                source="trusted-boxing-provider",
                confidence=0.97,
                sport="boxing",
                role="middleweight boxer",
                nationality="Scottish",
                gender="male",
            )
        ]

        plan = self.verifier.verify(requirements, evidence)

        self.assertEqual(plan.status, IdentityStatus.VERIFIED)
        self.assertTrue(plan.depiction_allowed)
        self.assertEqual(plan.sport, "boxing")
        self.assertEqual(plan.role, "middleweight boxer")
        self.assertEqual(plan.nationality, "Scottish")

    def test_sam_hickey_golf_candidate_is_rejected_even_with_name_match(self) -> None:
        requirements = IdentityRequirements(
            entity_name="Sam Hickey",
            sport="boxing",
        )
        evidence = [
            IdentityEvidence(
                canonical_name="Sam Hickey",
                source="wrong-sport-candidate",
                confidence=0.99,
                sport="golf",
            )
        ]

        plan = self.verifier.verify(requirements, evidence)

        self.assertEqual(plan.status, IdentityStatus.UNVERIFIED)
        self.assertFalse(plan.depiction_allowed)
        self.assertIn("context", plan.reason)

    def test_conflicting_high_confidence_sources_fail_closed(self) -> None:
        requirements = IdentityRequirements(
            entity_name="Alex Example",
            sport="boxing",
        )
        evidence = [
            IdentityEvidence(
                canonical_name="Alex Example",
                source="provider-a",
                confidence=0.96,
                sport="boxing",
                gender="male",
            ),
            IdentityEvidence(
                canonical_name="Alex Example",
                source="provider-b",
                confidence=0.92,
                sport="boxing",
                gender="female",
            ),
        ]

        plan = self.verifier.verify(requirements, evidence)

        self.assertEqual(plan.status, IdentityStatus.PARTIAL)
        self.assertFalse(plan.depiction_allowed)
        self.assertIn("conflict", plan.reason)

    def test_low_confidence_match_does_not_allow_depiction(self) -> None:
        requirements = IdentityRequirements(
            entity_name="Prospect Player",
            sport="boxing",
            min_confidence=0.90,
        )
        evidence = [
            IdentityEvidence(
                canonical_name="Prospect Player",
                source="weak-provider",
                confidence=0.72,
                sport="boxing",
            )
        ]

        plan = self.verifier.verify(requirements, evidence)

        self.assertEqual(plan.status, IdentityStatus.PARTIAL)
        self.assertFalse(plan.depiction_allowed)

    def test_name_normalization_handles_case_and_punctuation(self) -> None:
        requirements = IdentityRequirements(
            entity_name="SAM HICKEY",
            sport="boxing",
        )
        evidence = [
            IdentityEvidence(
                canonical_name="Sam-Hickey",
                source="provider",
                confidence=0.95,
                sport="boxing",
            )
        ]

        plan = self.verifier.verify(requirements, evidence)

        self.assertEqual(plan.status, IdentityStatus.VERIFIED)
        self.assertTrue(plan.depiction_allowed)


if __name__ == "__main__":
    unittest.main()
