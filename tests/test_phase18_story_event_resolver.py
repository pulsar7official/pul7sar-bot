import unittest

from engine.intelligence.story_event_resolver import StoryEventResolver
from engine.intelligence.story_visual_editorial import EditorialEvent


class StoryEventResolverTests(unittest.TestCase):
    def setUp(self):
        self.resolver = StoryEventResolver()

    def test_core_aliases_resolve(self):
        cases = {
            "match_result": EditorialEvent.RESULT,
            "signing": EditorialEvent.TRANSFER_CONFIRMED,
            "rumour": EditorialEvent.TRANSFER_RUMOUR,
            "renewal": EditorialEvent.CONTRACT,
            "return": EditorialEvent.COMEBACK,
            "sacking": EditorialEvent.DISMISSAL,
            "milestone": EditorialEvent.RECORD,
            "standings": EditorialEvent.TABLE,
            "formation": EditorialEvent.TACTICS,
            "referee": EditorialEvent.OFFICIATING,
            "fixture": EditorialEvent.SCHEDULE,
            "qualified": EditorialEvent.QUALIFICATION,
            "eliminated": EditorialEvent.ELIMINATION,
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(self.resolver.resolve(raw), expected)

    def test_unknown_fails_closed_by_default(self):
        with self.assertRaisesRegex(ValueError, "unsupported story event"):
            self.resolver.resolve("mystery_event")

    def test_explicit_general_fallback_is_available(self):
        self.assertEqual(self.resolver.resolve("mystery_event", allow_general_fallback=True), EditorialEvent.GENERAL)
        self.assertEqual(self.resolver.resolve(None, allow_general_fallback=True), EditorialEvent.GENERAL)


if __name__ == "__main__":
    unittest.main()
