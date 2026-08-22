import unittest

from engine.intelligence.models import Sentiment
from engine.intelligence.sentiment import SentimentEvidence, SentimentResolver


class SentimentResolverTests(unittest.TestCase):
    def setUp(self):
        self.resolver = SentimentResolver()

    def test_no_evidence_is_neutral(self):
        decision = self.resolver.resolve(())
        self.assertEqual(decision.sentiment, Sentiment.NEUTRAL)
        self.assertEqual(decision.confidence, 0.0)

    def test_low_confidence_fails_to_neutral(self):
        decision = self.resolver.resolve((
            SentimentEvidence(Sentiment.POSITIVE, 0.40, "provider"),
        ))
        self.assertEqual(decision.sentiment, Sentiment.NEUTRAL)

    def test_high_confidence_positive_is_preserved(self):
        decision = self.resolver.resolve((
            SentimentEvidence(Sentiment.POSITIVE, 0.90, "provider"),
        ))
        self.assertEqual(decision.sentiment, Sentiment.POSITIVE)

    def test_strong_conflict_fails_closed_to_neutral(self):
        decision = self.resolver.resolve((
            SentimentEvidence(Sentiment.POSITIVE, 0.90, "provider-a"),
            SentimentEvidence(Sentiment.NEGATIVE, 0.85, "provider-b"),
        ))
        self.assertEqual(decision.sentiment, Sentiment.NEUTRAL)
        self.assertTrue(decision.conflicted)

    def test_sentiment_evidence_requires_source(self):
        with self.assertRaises(ValueError):
            SentimentEvidence(Sentiment.SERIOUS, 0.8, "")


if __name__ == "__main__":
    unittest.main()
