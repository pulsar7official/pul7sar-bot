import unittest

from engine.intelligence.concept_director import ConceptDirector, ProposedConcept
from engine.intelligence.fact_lock import FactLock
from engine.intelligence.generation_authorization import (
    AuthorizationFailure,
    GenerationAuthorizer,
)
from engine.intelligence.models import (
    ClaimKind,
    IdentityPlan,
    IdentityStatus,
    LockedClaim,
    Sentiment,
    VisualIntent,
)
from engine.intelligence.neutrality import LoserTreatment, ResultVisualTreatment
from engine.intelligence.sentiment import SentimentDecision


class GenerationAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.director = ConceptDirector()
        self.authorizer = GenerationAuthorizer(self.director)

    def _result_intent(self, *, requires_identity=False):
        return VisualIntent(
            family="results",
            concept="celebrate the winner respectfully",
            sentiment=Sentiment.POSITIVE,
            hero_entity="Winner FC" if requires_identity else None,
            metadata={"requires_identity_gate": requires_identity},
        )

    def _safe_concept(self, intent):
        brief = self.director.build_brief(intent)
        concept = ProposedConcept(
            description="winner-focused result visual; loser omitted",
            claimed_constraints=brief.required_constraints,
            result_treatment=ResultVisualTreatment(
                loser_treatment=LoserTreatment.ABSENT,
            ),
        )
        return brief, concept

    def test_safe_result_can_be_authorized(self):
        intent = self._result_intent()
        brief, concept = self._safe_concept(intent)
        decision = self.authorizer.authorize(
            fact_lock=FactLock((LockedClaim("Winner FC won", ClaimKind.FACT),)),
            intent=intent,
            concept_brief=brief,
            proposed_concept=concept,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(self.authorizer.assert_authorized(decision), self.authorizer.TOKEN)

    def test_forbidden_fact_blocks_generation(self):
        intent = self._result_intent()
        brief, concept = self._safe_concept(intent)
        decision = self.authorizer.authorize(
            fact_lock=FactLock((LockedClaim("invented humiliation claim", ClaimKind.FORBIDDEN),)),
            intent=intent,
            concept_brief=brief,
            proposed_concept=concept,
        )
        self.assertFalse(decision.allowed)
        self.assertIn(AuthorizationFailure.FACT_LOCK, decision.failures)

    def test_required_identity_without_plan_blocks_generation(self):
        intent = self._result_intent(requires_identity=True)
        brief, concept = self._safe_concept(intent)
        decision = self.authorizer.authorize(
            fact_lock=FactLock((LockedClaim("Winner FC won", ClaimKind.FACT),)),
            intent=intent,
            concept_brief=brief,
            proposed_concept=concept,
        )
        self.assertFalse(decision.allowed)
        self.assertIn(AuthorizationFailure.IDENTITY, decision.failures)

    def test_partial_identity_blocks_generation(self):
        intent = self._result_intent(requires_identity=True)
        brief, concept = self._safe_concept(intent)
        plan = IdentityPlan(
            entity_name="Winner FC",
            status=IdentityStatus.PARTIAL,
            confidence=0.8,
            depiction_allowed=False,
        )
        decision = self.authorizer.authorize(
            fact_lock=FactLock((LockedClaim("Winner FC won", ClaimKind.FACT),)),
            intent=intent,
            concept_brief=brief,
            proposed_concept=concept,
            identity_plan=plan,
        )
        self.assertFalse(decision.allowed)
        self.assertIn(AuthorizationFailure.IDENTITY, decision.failures)

    def test_verified_identity_allows_identity_gate(self):
        intent = self._result_intent(requires_identity=True)
        brief, concept = self._safe_concept(intent)
        plan = IdentityPlan(
            entity_name="Winner FC",
            status=IdentityStatus.VERIFIED,
            confidence=0.99,
            depiction_allowed=True,
        )
        decision = self.authorizer.authorize(
            fact_lock=FactLock((LockedClaim("Winner FC won", ClaimKind.FACT),)),
            intent=intent,
            concept_brief=brief,
            proposed_concept=concept,
            identity_plan=plan,
        )
        self.assertTrue(decision.allowed)

    def test_conflicted_sentiment_blocks_generation(self):
        intent = self._result_intent()
        brief, concept = self._safe_concept(intent)
        decision = self.authorizer.authorize(
            fact_lock=FactLock((LockedClaim("Winner FC won", ClaimKind.FACT),)),
            intent=intent,
            concept_brief=brief,
            proposed_concept=concept,
            sentiment_decision=SentimentDecision(
                sentiment=Sentiment.NEUTRAL,
                confidence=0.85,
                reason="conflicting high-confidence evidence",
                conflicted=True,
            ),
        )
        self.assertFalse(decision.allowed)
        self.assertIn(AuthorizationFailure.SENTIMENT, decision.failures)

    def test_humiliating_concept_blocks_generation(self):
        intent = self._result_intent()
        brief = self.director.build_brief(intent)
        concept = ProposedConcept(
            description="winner above humiliated loser",
            claimed_constraints=brief.required_constraints,
            result_treatment=ResultVisualTreatment(
                loser_treatment=LoserTreatment.HUMILIATING,
            ),
        )
        decision = self.authorizer.authorize(
            fact_lock=FactLock((LockedClaim("Winner FC won", ClaimKind.FACT),)),
            intent=intent,
            concept_brief=brief,
            proposed_concept=concept,
        )
        self.assertFalse(decision.allowed)
        self.assertIn(AuthorizationFailure.CONCEPT, decision.failures)


if __name__ == "__main__":
    unittest.main()
