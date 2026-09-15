import unittest

from engine.intelligence.concept_director import (
    ConceptConstraint,
    ConceptDirectionError,
    ConceptDirector,
    ProposedConcept,
)
from engine.intelligence.models import Sentiment, VisualIntent
from engine.intelligence.neutrality import LoserTreatment, ResultVisualTreatment
from engine.intelligence.perspective import ResultPerspectives


class PerspectiveConceptTests(unittest.TestCase):
    def test_result_perspectives_separate_winner_loser_and_editorial_voice(self):
        perspectives = ResultPerspectives.competitive_result(
            winner_entity="Winner FC",
            loser_entity="Loser FC",
        )
        self.assertEqual(perspectives.winner.sentiment, Sentiment.POSITIVE)
        self.assertEqual(perspectives.loser.sentiment, Sentiment.NEGATIVE)
        self.assertEqual(perspectives.editorial.sentiment, Sentiment.NEUTRAL)

    def test_editorial_result_voice_cannot_be_positive_or_negative(self):
        from engine.intelligence.perspective import EditorialRole, PerspectiveSentiment
        with self.assertRaises(ValueError):
            ResultPerspectives(
                winner=PerspectiveSentiment(EditorialRole.WINNER, Sentiment.POSITIVE, "A"),
                loser=PerspectiveSentiment(EditorialRole.LOSER, Sentiment.NEGATIVE, "B"),
                editorial=PerspectiveSentiment(EditorialRole.EDITORIAL, Sentiment.POSITIVE),
            )

    def test_result_concept_inherits_anti_humiliation_constraints(self):
        director = ConceptDirector()
        intent = VisualIntent(
            family="results",
            concept="celebrate the winner respectfully",
            sentiment=Sentiment.POSITIVE,
            hero_entity="Winner FC",
            color_strategy="adaptive_entity_palette",
            metadata={"requires_identity_gate": False},
        )
        brief = director.build_brief(intent)
        self.assertIn(ConceptConstraint.NO_HUMILIATION, brief.required_constraints)
        self.assertIn(ConceptConstraint.NO_MOCKERY, brief.required_constraints)

    def test_result_concept_must_acknowledge_constraints(self):
        director = ConceptDirector()
        intent = VisualIntent(
            family="results",
            concept="celebrate the winner respectfully",
            sentiment=Sentiment.POSITIVE,
        )
        brief = director.build_brief(intent)
        with self.assertRaises(ConceptDirectionError):
            director.validate(brief, ProposedConcept(description="winner monument"))

    def test_acknowledged_constraints_do_not_override_neutrality_gate(self):
        director = ConceptDirector()
        intent = VisualIntent(
            family="results",
            concept="celebrate the winner respectfully",
            sentiment=Sentiment.POSITIVE,
        )
        brief = director.build_brief(intent)
        concept = ProposedConcept(
            description="winner elevated while loser is mocked below",
            claimed_constraints=brief.required_constraints,
            result_treatment=ResultVisualTreatment(
                loser_treatment=LoserTreatment.HUMILIATING,
                mocking_copy=True,
            ),
        )
        with self.assertRaises(ValueError):
            director.validate(brief, concept)

    def test_respectful_result_concept_passes(self):
        director = ConceptDirector()
        intent = VisualIntent(
            family="results",
            concept="celebrate the winner respectfully",
            sentiment=Sentiment.POSITIVE,
        )
        brief = director.build_brief(intent)
        director.validate(
            brief,
            ProposedConcept(
                description="winner-focused stadium monument; losing side omitted",
                claimed_constraints=brief.required_constraints,
                result_treatment=ResultVisualTreatment(
                    loser_treatment=LoserTreatment.ABSENT,
                ),
            ),
        )


if __name__ == "__main__":
    unittest.main()
