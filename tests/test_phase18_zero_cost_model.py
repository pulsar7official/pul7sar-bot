import unittest

from engine.intelligence.cost_policy import DevelopmentCostPolicy
from engine.intelligence.provider_prompting import ConstraintPromptMode, PromptConstraintCompiler
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


class ZeroCostModelTests(unittest.TestCase):
    def test_flux2_klein_local_is_allowed_by_zero_cost_policy(self):
        decision = DevelopmentCostPolicy().evaluate(FLUX2_KLEIN_4B_LOCAL.economics)
        self.assertTrue(decision.allowed)

    def test_all_current_platform_canvases_fit_declared_four_megapixel_envelope(self):
        for width, height in (
            (1080, 1350),
            (1080, 1920),
            (1200, 1500),
            (1600, 900),
            (1280, 720),
        ):
            with self.subTest(canvas=(width, height)):
                self.assertTrue(FLUX2_KLEIN_4B_LOCAL.supports_canvas(width, height))

    def test_profile_is_multi_reference_but_not_native_negative_prompt(self):
        self.assertTrue(FLUX2_KLEIN_4B_LOCAL.supports_multi_reference)
        self.assertFalse(FLUX2_KLEIN_4B_LOCAL.supports_native_negative_prompt)

    def test_known_pul7sar_constraints_are_reframed_for_flux(self):
        compiled = PromptConstraintCompiler().compile(
            (
                "no humiliation",
                "no fake signing ceremony",
                "no contract signature",
            ),
            supports_native_negative=False,
        )
        self.assertEqual(compiled.mode, ConstraintPromptMode.POSITIVE_REFRAME)
        self.assertTrue(compiled.complete)
        self.assertFalse(compiled.native_negative_constraints)
        self.assertGreaterEqual(len(compiled.positive_instructions), 2)

    def test_unknown_constraint_fails_closed_instead_of_being_dropped(self):
        compiled = PromptConstraintCompiler().compile(
            ("no previously unseen custom violation",),
            supports_native_negative=False,
        )
        self.assertFalse(compiled.complete)
        with self.assertRaises(ValueError):
            PromptConstraintCompiler().assert_complete(compiled)


if __name__ == "__main__":
    unittest.main()
