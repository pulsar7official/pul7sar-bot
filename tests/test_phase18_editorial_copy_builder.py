import unittest

from engine.intelligence.editorial_copy_builder import EditorialCopyBuilder, EditorialCopyInput
from engine.intelligence.editorial_headline_grammar import HeadlineInput, HeadlineTone
from engine.intelligence.story_visual_editorial import EditorialEvent


class EditorialCopyBuilderTests(unittest.TestCase):
    def setUp(self):
        self.builder = EditorialCopyBuilder()

    def test_uses_only_supplied_verified_fact_and_context(self):
        decision = self.builder.build(EditorialCopyInput(
            headline_input=HeadlineInput(
                event=EditorialEvent.COMEBACK,
                subject="Player",
                fact_phrase="يعود بعد الغياب",
                tone=HeadlineTone.POSITIVE,
            ),
            verified_context="وسجل هدف الفوز",
        ))
        self.assertEqual(decision.post_text, "Player يعود بعد الغياب. وسجل هدف الفوز.")
        self.assertTrue(decision.context_used)
        self.assertTrue(decision.compact)

    def test_context_is_omitted_if_it_breaks_compact_limit(self):
        decision = self.builder.build(EditorialCopyInput(
            headline_input=HeadlineInput(
                event=EditorialEvent.RESULT,
                subject="Team",
                fact_phrase="يفوز بالمباراة",
            ),
            verified_context="تفصيل " * 50,
            max_body_chars=100,
        ))
        self.assertFalse(decision.context_used)
        self.assertEqual(decision.post_text, "Team يفوز بالمباراة.")

    def test_long_verified_fact_is_not_silently_rewritten(self):
        fact = "تفصيل موثق " * 30
        decision = self.builder.build(EditorialCopyInput(
            headline_input=HeadlineInput(
                event=EditorialEvent.GENERAL,
                subject="Subject",
                fact_phrase=fact,
            ),
            max_body_chars=100,
        ))
        self.assertFalse(decision.compact)
        self.assertIn("تفصيل موثق", decision.post_text)


if __name__ == "__main__":
    unittest.main()
