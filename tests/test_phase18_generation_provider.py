import unittest

from engine.intelligence.concept_director import ConceptDirector, ProposedConcept
from engine.intelligence.fact_lock import FactLock
from engine.intelligence.generation_authorization import GenerationAuthorizer
from engine.intelligence.generation_provider import (
    AuthorizedSceneGenerator,
    OriginalSceneRequest,
    OriginalSceneResult,
)
from engine.intelligence.models import ClaimKind, LockedClaim, Sentiment, VisualIntent
from engine.intelligence.neutrality import LoserTreatment, ResultVisualTreatment


class _FakeProvider:
    def __init__(self):
        self.calls = 0

    def generate(self, request):
        self.calls += 1
        return OriginalSceneResult(provider="fake", asset_reference="memory://scene-1")


class GenerationProviderBoundaryTests(unittest.TestCase):
    def _fixture(self):
        director = ConceptDirector()
        authorizer = GenerationAuthorizer(director)
        intent = VisualIntent(
            family="results",
            concept="celebrate the winner respectfully",
            sentiment=Sentiment.POSITIVE,
        )
        brief = director.build_brief(intent)
        concept = ProposedConcept(
            description="winner-focused scene with loser omitted",
            claimed_constraints=brief.required_constraints,
            result_treatment=ResultVisualTreatment(loser_treatment=LoserTreatment.ABSENT),
        )
        authorization = authorizer.authorize(
            fact_lock=FactLock((LockedClaim("Winner FC won", ClaimKind.FACT),)),
            intent=intent,
            concept_brief=brief,
            proposed_concept=concept,
        )
        request = OriginalSceneRequest(
            concept_brief=brief,
            proposed_concept=concept,
            output_width=1080,
            output_height=1350,
        )
        return authorizer, authorization, request

    def test_provider_is_called_only_after_authorization(self):
        authorizer, authorization, request = self._fixture()
        provider = _FakeProvider()
        wrapper = AuthorizedSceneGenerator(provider, authorizer=authorizer)
        result = wrapper.generate(request, authorization)
        self.assertEqual(provider.calls, 1)
        self.assertEqual(result.provider, "fake")

    def test_denied_authorization_prevents_provider_invocation(self):
        authorizer, authorization, request = self._fixture()
        denied = type(authorization)(
            allowed=False,
            failures=(),
            reasons=("manual deny for test",),
        )
        provider = _FakeProvider()
        wrapper = AuthorizedSceneGenerator(provider, authorizer=authorizer)
        with self.assertRaises(PermissionError):
            wrapper.generate(request, denied)
        self.assertEqual(provider.calls, 0)

    def test_request_rejects_invalid_dimensions(self):
        _, _, request = self._fixture()
        with self.assertRaises(ValueError):
            OriginalSceneRequest(
                concept_brief=request.concept_brief,
                proposed_concept=request.proposed_concept,
                output_width=0,
                output_height=1350,
            )


if __name__ == "__main__":
    unittest.main()
