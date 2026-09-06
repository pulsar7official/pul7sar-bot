import unittest

from engine.intelligence.neutrality import (
    EditorialNeutralityGate,
    LoserTreatment,
    NeutralityViolation,
    ResultVisualTreatment,
)


class EditorialNeutralityTests(unittest.TestCase):
    def setUp(self):
        self.gate = EditorialNeutralityGate()

    def test_winner_can_be_celebrated_respectfully(self):
        decision = self.gate.evaluate(
            ResultVisualTreatment(
                celebrates_winner=True,
                loser_treatment=LoserTreatment.RESPECTFUL,
            )
        )
        self.assertTrue(decision.allowed)

    def test_loser_can_be_absent_from_visual(self):
        decision = self.gate.evaluate(
            ResultVisualTreatment(
                celebrates_winner=True,
                loser_treatment=LoserTreatment.ABSENT,
            )
        )
        self.assertTrue(decision.allowed)

    def test_realistic_disappointment_is_allowed(self):
        decision = self.gate.evaluate(
            ResultVisualTreatment(
                celebrates_winner=True,
                loser_treatment=LoserTreatment.REALISTIC_DISAPPOINTMENT,
            )
        )
        self.assertTrue(decision.allowed)

    def test_humiliation_is_rejected(self):
        with self.assertRaises(NeutralityViolation):
            self.gate.assert_allowed(
                ResultVisualTreatment(
                    loser_treatment=LoserTreatment.HUMILIATING,
                )
            )

    def test_mocking_or_degrading_symbols_are_rejected(self):
        for kwargs in (
            {"mocking_copy": True},
            {"degrading_symbolism": True},
            {"domination_symbolism": True},
            {"exaggerated_shame": True},
        ):
            with self.subTest(kwargs=kwargs):
                self.assertFalse(
                    self.gate.evaluate(ResultVisualTreatment(**kwargs)).allowed
                )

    def test_harsh_verified_context_never_authorizes_mockery(self):
        decision = self.gate.evaluate(
            ResultVisualTreatment(
                loser_treatment=LoserTreatment.REALISTIC_DISAPPOINTMENT,
                verified_story_requires_harsh_context=True,
                mocking_copy=True,
            )
        )
        self.assertFalse(decision.allowed)


if __name__ == "__main__":
    unittest.main()
