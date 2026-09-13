from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_sentiment_neutrality_gate_verifier import (
    SENTIMENT_EVIDENCE_SCHEMA,
    VERIFIER_ID,
    VERIFIER_VERSION,
    replay_sentiment_neutrality_gate,
    verify_sentiment_neutrality_evidence,
)
from engine.intelligence.sentiment_neutrality import evaluate_sentiment_neutrality


class SentimentNeutralityGateVerifierTests(unittest.TestCase):
    STORY_SHA = "c" * 64

    def _receipt(self) -> dict:
        return {"verifier_id": VERIFIER_ID, "verifier_version": VERIFIER_VERSION}

    def _evidence(self, **overrides) -> dict:
        payload = {
            "schema": SENTIMENT_EVIDENCE_SCHEMA,
            "gate_id": "sentiment_neutrality",
            "story_snapshot_sha256": self.STORY_SHA,
            "outcome_is_competitive_result": True,
            "opponent_or_loser_present": True,
            "editorial_text_fields": {
                "headline": "Club A wins 2-1 against Club B",
                "caption": "Club A celebrates a narrow victory after a competitive match.",
            },
            "source_backed_emotional_attributions": [],
        }
        payload.update(overrides)
        return payload

    def _write(self, root: Path, payload: dict) -> Path:
        path = root / "sentiment_neutrality.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def test_respectful_result_copy_replays_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence())
            result = replay_sentiment_neutrality_gate(path, self.STORY_SHA, self._receipt())
            self.assertTrue(result["gate_passed"])
            self.assertEqual(result["gate_id"], "sentiment_neutrality")
            self.assertEqual(result["verification_details"]["finding_count"], 0)
            self.assertTrue(result["verification_details"]["respectful_neutrality_allowed"])
            self.assertFalse(result["verification_details"]["invented_emotional_attribution_found"])
            self.assertFalse(result["verification_details"]["degrading_or_humiliating_language_found"])

    def test_degrading_loser_language_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                editorial_text_fields={
                    "headline": "Club A wins 2-1",
                    "caption": "A pathetic display from Club B.",
                }
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "disrespectful_or_degrading_language"):
                verify_sentiment_neutrality_evidence(path, self.STORY_SHA, self._receipt())

    def test_arabic_humiliating_language_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                editorial_text_fields={
                    "headline": "فوز النادي أ بنتيجة 2-1",
                    "caption": "هزيمة مهينة للنادي ب.",
                }
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "disrespectful_or_degrading_language"):
                verify_sentiment_neutrality_evidence(path, self.STORY_SHA, self._receipt())

    def test_unsupported_emotional_attribution_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                editorial_text_fields={
                    "headline": "Club A wins 2-1",
                    "caption": "Club B players were furious after the final whistle.",
                }
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "unsupported_emotional_attribution"):
                verify_sentiment_neutrality_evidence(path, self.STORY_SHA, self._receipt())

    def test_source_backed_non_degrading_emotion_can_be_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                editorial_text_fields={
                    "headline": "Club A wins 2-1",
                    "caption": "The coach said he was furious after the final whistle.",
                },
                source_backed_emotional_attributions=["furious"],
            )
            path = self._write(Path(tmp), evidence)
            result = verify_sentiment_neutrality_evidence(path, self.STORY_SHA, self._receipt())
            self.assertTrue(result["gate_passed"])

    def test_competitive_result_requires_opponent_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence(opponent_or_loser_present=False))
            with self.assertRaisesRegex(ValueError, "RESULT_OPPONENT_CONTEXT_REQUIRED"):
                verify_sentiment_neutrality_evidence(path, self.STORY_SHA, self._receipt())

    def test_cross_story_evidence_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp), self._evidence(story_snapshot_sha256="d" * 64)
            )
            with self.assertRaisesRegex(ValueError, "CROSS_STORY_EVIDENCE"):
                verify_sentiment_neutrality_evidence(path, self.STORY_SHA, self._receipt())

    def test_receipt_verifier_identity_cannot_select_another_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence())
            receipt = self._receipt()
            receipt["verifier_id"] = "wrong"
            with self.assertRaisesRegex(ValueError, "VERIFIER_ID_MISMATCH"):
                verify_sentiment_neutrality_evidence(path, self.STORY_SHA, receipt)

    def test_policy_requires_nonempty_publication_text_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "TEXT_FIELDS_REQUIRED"):
            evaluate_sentiment_neutrality(
                editorial_text_fields={},
                outcome_is_competitive_result=False,
                opponent_or_loser_present=False,
            )

    def test_adapter_exposes_production_provenance_metadata(self) -> None:
        self.assertIs(replay_sentiment_neutrality_gate.PUL7SAR_PRODUCTION_BACKED, True)
        self.assertEqual(
            replay_sentiment_neutrality_gate.PUL7SAR_VERIFIER_GATE_ID,
            "sentiment_neutrality",
        )
        self.assertEqual(replay_sentiment_neutrality_gate.PUL7SAR_VERIFIER_ID, VERIFIER_ID)
        self.assertEqual(
            replay_sentiment_neutrality_gate.PUL7SAR_VERIFIER_VERSION,
            VERIFIER_VERSION,
        )
        self.assertIs(
            replay_sentiment_neutrality_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT,
            verify_sentiment_neutrality_evidence,
        )


if __name__ == "__main__":
    unittest.main()
