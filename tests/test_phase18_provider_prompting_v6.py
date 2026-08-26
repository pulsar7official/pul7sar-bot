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
