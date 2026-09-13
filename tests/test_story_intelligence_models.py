import unittest

from engine.intelligence import (
    ClaimKind,
    FactLock,
    FactLockViolation,
    IdentityPlan,
    IdentityStatus,
    LockedClaim,
    Sentiment,
    StoryBrief,
    VisualIntent,
)


class StoryIntelligenceModelTests(unittest.TestCase):
    def test_locked_claim_is_immutable_and_validates_confidence(self):
        claim = LockedClaim(
            text="Sam Hickey is a boxer",
            kind=ClaimKind.FACT,
            confidence=0.95,
            metadata={"sport": "boxing"},
        )
        self.assertEqual(claim.confidence, 0.95)
        self.assertEqual(claim.metadata["sport"], "boxing")
        with self.assertRaises(TypeError):
            claim.metadata["sport"] = "golf"
        with self.assertRaises(ValueError):
            LockedClaim(
                text="invalid",
                kind=ClaimKind.FACT,
                confidence=1.2,
            )

    def test_identity_depiction_requires_verified_status(self):
        with self.assertRaises(ValueError):
            IdentityPlan(
                entity_name="Charlie Hull",
                status=IdentityStatus.PARTIAL,
                sport="golf",
                confidence=0.80,
                depiction_allowed=True,
            )

        plan = IdentityPlan(
            entity_name="Charlie Hull",
            status=IdentityStatus.VERIFIED,
            sport="golf",
            gender="female",
            confidence=0.99,
            depiction_allowed=True,
        )
        self.assertTrue(plan.depiction_allowed)

    def test_story_brief_carries_sentiment_separately_from_rendering(self):
        brief = StoryBrief(
            headline="A rising British boxing prospect",
            summary="Sam Hickey belongs to Britain's professional elite.",
            sport="boxing",
            story_type="player_profile",
            primary_entity="Sam Hickey",
            sentiment=Sentiment.POSITIVE,
        )
        self.assertEqual(brief.sentiment, Sentiment.POSITIVE)
        self.assertEqual(brief.sport, "boxing")

    def test_visual_intent_can_reference_identity_plan_without_render_context(self):
        identity = IdentityPlan(
            entity_name="Sam Hickey",
            status=IdentityStatus.VERIFIED,
            sport="boxing",
            role="middleweight boxer",
            nationality="Scottish",
            confidence=0.98,
            depiction_allowed=True,
        )
        intent = VisualIntent(
            family="PLAYER_STORIES",
            concept="Rising through the professional ranks",
            sentiment=Sentiment.POSITIVE,
            hero_entity="Sam Hickey",
            identity_plan=identity,
        )
        self.assertEqual(intent.identity_plan.sport, "boxing")


class FactLockTests(unittest.TestCase):
    def test_forbidden_claims_never_become_usable(self):
        lock = FactLock(
            [
                LockedClaim(
                    text="Arsenal are interested in the player",
                    kind=ClaimKind.FACT,
                ),
                LockedClaim(
                    text="The transfer is officially complete",
                    kind=ClaimKind.FORBIDDEN,
                ),
            ]
        )
        usable_text = {claim.text for claim in lock.usable_claims()}
        self.assertIn("Arsenal are interested in the player", usable_text)
        self.assertNotIn("The transfer is officially complete", usable_text)
        with self.assertRaises(FactLockViolation):
            lock.assert_publishable()

    def test_safe_inference_can_be_excluded(self):
        lock = FactLock(
            [
                LockedClaim(
                    text="The club is preparing for the new season",
                    kind=ClaimKind.FACT,
                ),
                LockedClaim(
                    text="The atmosphere can be portrayed as anticipatory",
                    kind=ClaimKind.SAFE_INFERENCE,
                    confidence=0.85,
                ),
            ]
        )
        claims = lock.usable_claims(include_safe_inference=False)
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0].kind, ClaimKind.FACT)

    def test_require_fact_fails_closed(self):
        lock = FactLock(
            [
                LockedClaim(
                    text="Atletico Madrid are willing to sell",
                    kind=ClaimKind.FACT,
                    confidence=0.90,
                )
            ]
        )
        with self.assertRaises(FactLockViolation):
            lock.require_fact(
                "Atletico Madrid are willing to sell",
                minimum_confidence=0.95,
            )
        claim = lock.require_fact(
            "Atletico Madrid are willing to sell",
            minimum_confidence=0.90,
        )
        self.assertEqual(claim.kind, ClaimKind.FACT)


if __name__ == "__main__":
    unittest.main()
