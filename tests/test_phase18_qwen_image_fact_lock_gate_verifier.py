from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_fact_lock_gate_verifier import (
    FACT_LOCK_EVIDENCE_SCHEMA,
    VERIFIER_ID,
    VERIFIER_VERSION,
    replay_fact_lock_gate,
    verify_fact_lock_evidence,
)


class FactLockGateVerifierTests(unittest.TestCase):
    STORY_SHA = "a" * 64

    def _receipt(self) -> dict:
        return {"verifier_id": VERIFIER_ID, "verifier_version": VERIFIER_VERSION}

    def _claim(
        self,
        text: str,
        *,
        kind: str = "fact",
        source: str | None = "https://example.invalid/source",
        confidence: float = 1.0,
    ) -> dict:
        return {
            "text": text,
            "kind": kind,
            "source": source,
            "confidence": confidence,
            "metadata": {},
        }

    def _evidence(self, **overrides) -> dict:
        payload = {
            "schema": FACT_LOCK_EVIDENCE_SCHEMA,
            "gate_id": "fact_lock",
            "story_snapshot_sha256": self.STORY_SHA,
            "minimum_fact_confidence": 1.0,
            "claims": [
                self._claim("Club A defeated Club B 2-1."),
                self._claim(
                    "The win may lift confidence.",
                    kind="safe_inference",
                    source="editorial-inference",
                    confidence=0.8,
                ),
            ],
            "required_facts": ["Club A defeated Club B 2-1."],
        }
        payload.update(overrides)
        return payload

    def _write(self, root: Path, payload: dict) -> Path:
        path = root / "fact_lock.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_required_locked_fact_replays_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence())
            result = replay_fact_lock_gate(path, self.STORY_SHA, self._receipt())
            self.assertTrue(result["gate_passed"])
            self.assertEqual(result["gate_id"], "fact_lock")
            self.assertEqual(result["verification_details"]["forbidden_count"], 0)
            self.assertEqual(result["verification_details"]["required_fact_count"], 1)
            self.assertTrue(result["verification_details"]["fact_sources_present"])
            self.assertTrue(result["verification_details"]["fact_lock_publishable"])

    def test_forbidden_claim_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence()
            evidence["claims"].append(
                self._claim("Unverified allegation.", kind="forbidden", confidence=0.0)
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "SEMANTIC_REJECTED"):
                verify_fact_lock_evidence(path, self.STORY_SHA, self._receipt())

    def test_safe_inference_cannot_satisfy_required_fact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                claims=[
                    self._claim(
                        "Club A defeated Club B 2-1.",
                        kind="safe_inference",
                        source="editorial-inference",
                        confidence=1.0,
                    )
                ]
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "SEMANTIC_REJECTED"):
                verify_fact_lock_evidence(path, self.STORY_SHA, self._receipt())

    def test_fact_without_source_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                claims=[self._claim("Club A defeated Club B 2-1.", source=None)]
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "FACT_SOURCE_MISSING"):
                verify_fact_lock_evidence(path, self.STORY_SHA, self._receipt())

    def test_fact_below_required_confidence_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                minimum_fact_confidence=0.95,
                claims=[self._claim("Club A defeated Club B 2-1.", confidence=0.9)],
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "SEMANTIC_REJECTED"):
                verify_fact_lock_evidence(path, self.STORY_SHA, self._receipt())

    def test_cross_story_evidence_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp), self._evidence(story_snapshot_sha256="b" * 64)
            )
            with self.assertRaisesRegex(ValueError, "CROSS_STORY_EVIDENCE"):
                verify_fact_lock_evidence(path, self.STORY_SHA, self._receipt())

    def test_duplicate_required_fact_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                self._evidence(
                    required_facts=[
                        "Club A defeated Club B 2-1.",
                        "  club a defeated club b 2-1.  ",
                    ]
                ),
            )
            with self.assertRaisesRegex(ValueError, "REQUIRED_FACTS_DUPLICATE"):
                verify_fact_lock_evidence(path, self.STORY_SHA, self._receipt())

    def test_receipt_verifier_identity_cannot_select_another_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence())
            receipt = self._receipt()
            receipt["verifier_id"] = "wrong"
            with self.assertRaisesRegex(ValueError, "VERIFIER_ID_MISMATCH"):
                verify_fact_lock_evidence(path, self.STORY_SHA, receipt)

    def test_adapter_exposes_production_provenance_metadata(self) -> None:
        self.assertIs(replay_fact_lock_gate.PUL7SAR_PRODUCTION_BACKED, True)
        self.assertEqual(replay_fact_lock_gate.PUL7SAR_VERIFIER_GATE_ID, "fact_lock")
        self.assertEqual(replay_fact_lock_gate.PUL7SAR_VERIFIER_ID, VERIFIER_ID)
        self.assertEqual(replay_fact_lock_gate.PUL7SAR_VERIFIER_VERSION, VERIFIER_VERSION)
        self.assertIs(
            replay_fact_lock_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT,
            verify_fact_lock_evidence,
        )


if __name__ == "__main__":
    unittest.main()
