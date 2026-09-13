import unittest

from engine.intelligence.fact_locked_editorial_adapter import FactLockedEditorialAdapter
from engine.intelligence.models import ClaimKind, LockedClaim
from engine.intelligence.story_visual_editorial import EditorialEvent


class FactLockedEditorialAdapterTests(unittest.TestCase):
    def setUp(self):
        self.adapter = FactLockedEditorialAdapter()

    def claim(self, slot, text, kind=ClaimKind.FACT, confidence=0.95):
        return LockedClaim(text=text, kind=kind, confidence=confidence, metadata={"slot": slot})

    def test_valid_result_slots_require_fact_evidence(self):
        result = self.adapter.build(
            event=EditorialEvent.RESULT,
            values={"subject": "A", "opponent": "B", "result_status": "final", "score": "2-1"},
            locked_claims=(
                self.claim("subject", "A"),
                self.claim("opponent", "B"),
                self.claim("result_status", "final"),
                self.claim("score", "2-1"),
            ),
        )
        self.assertEqual(result.values["score"], "2-1")
        self.assertEqual(result.claim_by_slot["score"].kind, ClaimKind.FACT)

    def test_safe_inference_cannot_back_required_fact_slot(self):
        with self.assertRaisesRegex(ValueError, "not backed by FACT claims"):
            self.adapter.build(
                event=EditorialEvent.RESULT,
                values={"subject": "A", "opponent": "B", "result_status": "final"},
                locked_claims=(
                    self.claim("subject", "A"),
                    self.claim("opponent", "B"),
                    self.claim("result_status", "final", kind=ClaimKind.SAFE_INFERENCE),
                ),
            )

    def test_low_confidence_fact_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "confidence below 0.80"):
            self.adapter.build(
                event=EditorialEvent.INJURY,
                values={"subject": "Player", "injury_status": "confirmed"},
                locked_claims=(
                    self.claim("subject", "Player"),
                    self.claim("injury_status", "confirmed", confidence=0.70),
                ),
            )

    def test_missing_required_schema_slot_fails_before_visual_planning(self):
        with self.assertRaisesRegex(ValueError, "missing required editorial fact slots"):
            self.adapter.build(
                event=EditorialEvent.TRANSFER_CONFIRMED,
                values={"subject": "Player", "destination": "Club"},
                locked_claims=(self.claim("subject", "Player"), self.claim("destination", "Club")),
            )


if __name__ == "__main__":
    unittest.main()
