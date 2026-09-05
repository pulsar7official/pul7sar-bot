from __future__ import annotations

import unittest

from engine.intelligence.models import Sentiment
from engine.intelligence.story_analyzer import StoryAnalysisError, StoryAnalyzer


class StoryAnalyzerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analyzer = StoryAnalyzer()

    def test_normalizes_existing_article_shape_without_inventing_fields(self) -> None:
        brief = self.analyzer.analyze(
            {
                "title": "Sam Hickey is a rising British prospect",
                "summary": "A short source summary.",
                "sport": "boxing",
                "link": "https://example.test/story",
            }
        )

        self.assertEqual(brief.headline, "Sam Hickey is a rising British prospect")
        self.assertEqual(brief.sport, "boxing")
        self.assertIsNone(brief.primary_entity)
        self.assertIsNone(brief.event_status)
        self.assertEqual(brief.sentiment, Sentiment.NEUTRAL)
        self.assertEqual(brief.metadata["link"], "https://example.test/story")

    def test_explicit_identity_and_sentiment_context_are_preserved(self) -> None:
        brief = self.analyzer.analyze(
            {
                "title": "Charlie Hull produces a dramatic finish",
                "summary": "Golf story.",
                "sport": "golf",
                "primary_entity": "Charlie Hull",
                "story_type": "player_story",
                "sentiment": "celebratory",
            }
        )

        self.assertEqual(brief.primary_entity, "Charlie Hull")
        self.assertEqual(brief.story_type, "player_story")
        self.assertEqual(brief.sentiment, Sentiment.POSITIVE)

    def test_transfer_language_is_not_silently_upgraded_to_completed(self) -> None:
        brief = self.analyzer.analyze(
            {
                "title": "Arsenal move closer to a forward",
                "summary": "Talks are progressing, but no signing is confirmed.",
                "sport": "football",
                "story_type": "transfer",
                "event_status": "approach",
                "sentiment": "anticipatory",
            }
        )

        self.assertEqual(brief.event_status, "approach")
        self.assertNotEqual(brief.event_status, "completed")
        self.assertEqual(brief.sentiment, Sentiment.ANTICIPATORY)

    def test_general_multi_league_story_remains_entity_neutral(self) -> None:
        brief = self.analyzer.analyze(
            {
                "title": "Europe's major leagues return",
                "summary": "A new season is approaching.",
                "sport": "football",
                "story_type": "multi_league",
                "sentiment": "anticipatory",
                "secondary_entities": (
                    "Premier League",
                    "LaLiga",
                    "Serie A",
                    "Bundesliga",
                ),
            }
        )

        self.assertIsNone(brief.primary_entity)
        self.assertEqual(brief.story_type, "multi_league")
        self.assertIn("Serie A", brief.secondary_entities)

    def test_positive_and_negative_are_distinct_signals(self) -> None:
        positive = self.analyzer.analyze(
            {"title": "Win", "summary": "", "sentiment": "positive"}
        )
        negative = self.analyzer.analyze(
            {"title": "Loss", "summary": "", "sentiment": "negative"}
        )

        self.assertEqual(positive.sentiment, Sentiment.POSITIVE)
        self.assertEqual(negative.sentiment, Sentiment.NEGATIVE)
        self.assertNotEqual(positive.sentiment, negative.sentiment)

    def test_unknown_sentiment_fails_closed_instead_of_guessing(self) -> None:
        with self.assertRaises(StoryAnalysisError):
            self.analyzer.analyze(
                {"title": "Ambiguous story", "summary": "", "sentiment": "hyped"}
            )

    def test_secondary_entities_string_is_rejected(self) -> None:
        with self.assertRaises(StoryAnalysisError):
            self.analyzer.analyze(
                {
                    "title": "League story",
                    "summary": "",
                    "secondary_entities": "Serie A",
                }
            )

    def test_overrides_are_explicit_and_take_precedence(self) -> None:
        brief = self.analyzer.analyze(
            {
                "title": "Story",
                "summary": "",
                "sport": "football",
                "sentiment": "neutral",
            },
            overrides={"sentiment": "tense", "story_type": "controversy"},
        )

        self.assertEqual(brief.sentiment, Sentiment.TENSE)
        self.assertEqual(brief.story_type, "controversy")


if __name__ == "__main__":
    unittest.main()
