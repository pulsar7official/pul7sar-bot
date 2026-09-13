import unittest

from engine.intelligence.provider_prompting import PromptConstraintCompiler, ConstraintPromptMode


class GoldenV6ProviderPromptingTests(unittest.TestCase):
    def test_flux_reframes_story_first_pitch_constraints_without_dropping_them(self):
        compiled = PromptConstraintCompiler().compile(
            (
                "no full football pitch as the main visual subject",
                "no centered broadcast-style pitch composition",
                "no tactical diagram or prominent centre-circle/halfway-line geometry",
            ),
            supports_native_negative=False,
        )
        self.assertEqual(compiled.mode, ConstraintPromptMode.POSITIVE_REFRAME)
        self.assertTrue(compiled.complete)
        self.assertEqual(compiled.untranslated_constraints, ())
        joined = " ".join(compiled.positive_instructions).casefold()
        self.assertIn("incidental", joined)
        self.assertIn("oblique", joined)
        self.assertIn("centre circle", joined)
        self.assertNotIn("full playing surface", joined)

    def test_flux_reframes_partial_unverified_geometry_as_exact_or_indeterminate(self):
        compiled = PromptConstraintCompiler().compile(
            (
                "no isolated or partial goal frame or goal net",
                "no penalty-area or goal-area lines",
                "no corner arc or corner flag",
                "no partial regulation football geometry whose physical placement cannot be verified",
            ),
            supports_native_negative=False,
        )
        self.assertEqual(compiled.mode, ConstraintPromptMode.POSITIVE_REFRAME)
        self.assertTrue(compiled.complete)
        self.assertEqual(compiled.untranslated_constraints, ())
        self.assertEqual(len(compiled.positive_instructions), 1)
        joined = " ".join(compiled.positive_instructions).casefold()
        for marker in (
            "outside the frame",
            "fully occluded",
            "visually indeterminate",
            "goal frames or nets",
            "penalty-area or goal-area lines",
            "corner arcs or flags",
            "centre circles",
            "halfway lines",
            "physically coherent",
            "story-authorized",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, joined)

    def test_unknown_constraint_still_fails_closed(self):
        compiled = PromptConstraintCompiler().compile(
            ("no unknown phase18 visual condition",),
            supports_native_negative=False,
        )
        self.assertFalse(compiled.complete)
        with self.assertRaisesRegex(ValueError, "provider constraint translation incomplete"):
            PromptConstraintCompiler().assert_complete(compiled)


if __name__ == "__main__":
    unittest.main()
