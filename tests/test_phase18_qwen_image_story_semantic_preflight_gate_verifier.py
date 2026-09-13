from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_story_semantic_preflight_gate_verifier import (
    VERIFIER_ID,
    VERIFIER_VERSION,
    replay_story_semantic_preflight_gate,
    verify_story_semantic_preflight_evidence,
)
from engine.intelligence.story_semantic_preflight import (
    STORY_SEMANTIC_PREFLIGHT_EVIDENCE_SCHEMA,
    evaluate_story_semantic_preflight,
)


class StorySemanticPreflightGateVerifierTests(unittest.TestCase):
    STORY_SHA = "a" * 64

    def _receipt(self) -> dict:
        return {"verifier_id": VERIFIER_ID, "verifier_version": VERIFIER_VERSION}

    def _request(self, **overrides) -> dict:
        payload = {
            "event": "result",
            "sport": "football",
            "story_core": "Club A defeated Club B 2-1 in a competitive match.",
            "editorial_angle": "A composed victory presented without degrading the opponent.",
            "headline_short": "Club A win 2-1",
            "primary_subject": "Club A",
            "secondary_subjects": ["Club B"],
            "stakes": "normal",
            "sentiment": "neutral",
            "exact_assets": ["club_a_crest", "club_b_crest"],
            "geometry_requirements": [],
            "confidence": 0.95,
        }
        payload.update(overrides)
        return payload

    def _plan(self, **overrides) -> dict:
        payload = {
            "visual_family": "score_monument",
            "production_mode": "hybrid",
            "scene_concept": "A composed victory presented without degrading the opponent.",
            "generated_elements": [
                "atmosphere",
                "lighting",
                "depth",
                "environmental texture",
            ],
            "forbidden_generated_elements": [
                "PUL7SAR logo",
                "brand wordmark",
                "headline text",
                "scores",
                "statistics",
                "club crests",
                "competition logos",
            ],
        }
        payload.update(overrides)
        return payload

    def _evidence(self, **overrides) -> dict:
        payload = {
            "schema": STORY_SEMANTIC_PREFLIGHT_EVIDENCE_SCHEMA,
            "gate_id": "story_semantic_preflight",
            "story_snapshot_sha256": self.STORY_SHA,
            "qwen_generation_requested": True,
            "editorial_request": self._request(),
            "proposed_visual_plan": self._plan(),
        }
        payload.update(overrides)
        return payload

    def _write(self, root: Path, payload: dict) -> Path:
        path = root / "story_semantic_preflight.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path

    def test_project_native_result_plan_replays_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence())
            result = replay_story_semantic_preflight_gate(
                path, self.STORY_SHA, self._receipt()
            )
            self.assertTrue(result["gate_passed"])
            details = result["verification_details"]
            self.assertEqual(details["event"], "result")
            self.assertEqual(details["visual_family"], "score_monument")
            self.assertEqual(details["production_mode"], "hybrid")
            self.assertTrue(details["project_native_editorial_policy_replayed"])
            self.assertTrue(details["story_to_visual_contract_matches"])
            self.assertEqual(len(details["editorial_policy_source_sha256"]), 64)
            self.assertGreater(details["editorial_policy_source_byte_size"], 0)
            raw = path.read_bytes()
            self.assertEqual(result["source_evidence_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(result["source_evidence_byte_size"], len(raw))

    def test_low_confidence_story_is_not_qwen_generation_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                editorial_request=self._request(confidence=0.5),
                proposed_visual_plan=self._plan(production_mode="verified_asset_editorial"),
            )
            path = self._write(Path(tmp), evidence)
            with self.assertRaisesRegex(ValueError, "PRODUCTION_MODE_NOT_QWEN_COMPATIBLE"):
                verify_story_semantic_preflight_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_deterministic_table_story_is_not_qwen_generation_compatible(self) -> None:
        request = self._request(
            event="table",
            story_core="The verified standings changed after the latest round.",
            editorial_angle="Present the verified table movement clearly.",
            headline_short="Standings update",
            primary_subject=None,
            secondary_subjects=[],
            exact_assets=[],
            geometry_requirements=["table_grid"],
        )
        plan = self._plan(
            visual_family="data_editorial",
            production_mode="deterministic_composition",
            scene_concept="Present the verified table movement clearly.",
            generated_elements=[],
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                self._evidence(editorial_request=request, proposed_visual_plan=plan),
            )
            with self.assertRaisesRegex(ValueError, "PRODUCTION_MODE_NOT_QWEN_COMPATIBLE"):
                verify_story_semantic_preflight_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_visual_family_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                self._evidence(proposed_visual_plan=self._plan(visual_family="hero_moment")),
            )
            with self.assertRaisesRegex(ValueError, "VISUAL_FAMILY_DRIFT"):
                verify_story_semantic_preflight_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_scene_concept_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                self._evidence(
                    proposed_visual_plan=self._plan(scene_concept="A different invented concept")
                ),
            )
            with self.assertRaisesRegex(ValueError, "SCENE_CONCEPT_DRIFT"):
                verify_story_semantic_preflight_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_exact_score_cannot_be_added_to_generated_elements(self) -> None:
        generated = list(self._plan()["generated_elements"]) + ["score 2-1"]
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                self._evidence(
                    proposed_visual_plan=self._plan(generated_elements=generated)
                ),
            )
            with self.assertRaisesRegex(ValueError, "GENERATED_ELEMENTS_DRIFT"):
                verify_story_semantic_preflight_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_forbidden_generated_contract_cannot_drop_club_crests(self) -> None:
        forbidden = [
            item
            for item in self._plan()["forbidden_generated_elements"]
            if item != "club crests"
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp),
                self._evidence(
                    proposed_visual_plan=self._plan(forbidden_generated_elements=forbidden)
                ),
            )
            with self.assertRaisesRegex(ValueError, "FORBIDDEN_ELEMENTS_DRIFT"):
                verify_story_semantic_preflight_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_cross_story_evidence_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp), self._evidence(story_snapshot_sha256="b" * 64)
            )
            with self.assertRaisesRegex(ValueError, "CROSS_STORY_EVIDENCE"):
                verify_story_semantic_preflight_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_receipt_cannot_select_another_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), self._evidence())
            receipt = self._receipt()
            receipt["verifier_id"] = "wrong"
            with self.assertRaisesRegex(ValueError, "VERIFIER_ID_MISMATCH"):
                verify_story_semantic_preflight_evidence(path, self.STORY_SHA, receipt)

    def test_qwen_generation_request_flag_is_literal_boolean(self) -> None:
        with self.assertRaisesRegex(ValueError, "QWEN_REQUEST_FLAG_INVALID"):
            evaluate_story_semantic_preflight(
                qwen_generation_requested=1,
                editorial_request=self._request(),
                proposed_visual_plan=self._plan(),
            )

    def test_false_qwen_generation_request_cannot_pass_generation_preflight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(
                Path(tmp), self._evidence(qwen_generation_requested=False)
            )
            with self.assertRaisesRegex(ValueError, "QWEN_GENERATION_NOT_REQUESTED"):
                verify_story_semantic_preflight_evidence(
                    path, self.STORY_SHA, self._receipt()
                )

    def test_adapter_exposes_production_source_object_provenance(self) -> None:
        self.assertIs(
            replay_story_semantic_preflight_gate.PUL7SAR_PRODUCTION_BACKED,
            True,
        )
        self.assertEqual(
            replay_story_semantic_preflight_gate.PUL7SAR_VERIFIER_GATE_ID,
            "story_semantic_preflight",
        )
        self.assertEqual(
            replay_story_semantic_preflight_gate.PUL7SAR_VERIFIER_ID,
            VERIFIER_ID,
        )
        self.assertEqual(
            replay_story_semantic_preflight_gate.PUL7SAR_VERIFIER_VERSION,
            VERIFIER_VERSION,
        )
        self.assertIs(
            replay_story_semantic_preflight_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT,
            verify_story_semantic_preflight_evidence,
        )


if __name__ == "__main__":
    unittest.main()
