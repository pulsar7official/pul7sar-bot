from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.intelligence.qwen_image_atomic_fresh_story_semantic_replay import (
    ATOMIC_FRESH_STORY_SEMANTIC_REPLAY_SCHEMA,
)
from engine.intelligence.qwen_image_fresh_story_evidence_manifest import (
    FRESH_STORY_EVIDENCE_MANIFEST_SCHEMA,
)
from engine.intelligence.qwen_image_story_bound_canonical_prompt import (
    STORY_BOUND_CANONICAL_PROMPT_SCHEMA,
    build_story_bound_canonical_prompt,
)


class StoryBoundCanonicalPromptTests(unittest.TestCase):
    STORY_SHA = "a" * 64
    AUTH_SHA = "b" * 64

    def _write(self, path: Path, payload: dict) -> bytes:
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
        path.write_bytes(raw)
        return raw

    def _cs257(self, root: Path) -> Path:
        evidence_dir = root / "evidence"
        evidence_payloads = {
            "fact_lock": {
                "required_facts": ["Club A defeated Club B 2-1."],
            },
            "entity_identity_verification": {
                "canonical_entities": [
                    {"display_name": "Club A"},
                    {"display_name": "Club B"},
                ]
            },
            "sentiment_neutrality": {
                "outcome_is_competitive_result": True,
                "opponent_or_loser_present": True,
            },
            "story_semantic_preflight": {
                "qwen_generation_requested": True,
                "editorial_request": {
                    "event": "result",
                    "sport": "football",
                    "story_core": "Club A defeated Club B 2-1.",
                    "editorial_angle": "A composed victory without degrading the opponent.",
                },
                "proposed_visual_plan": {
                    "visual_family": "score_monument",
                    "scene_concept": "Composed premium match-result atmosphere.",
                    "generated_elements": ["atmosphere", "lighting", "depth"],
                    "forbidden_generated_elements": [
                        "headline text",
                        "scores",
                        "club crests",
                    ],
                },
            },
            "zero_cost_policy": {"cost_mode": "$0-local"},
            "semantic_layer_ownership": {
                "layer_plan": [
                    {"name": "atmosphere", "source": "generative", "required": True},
                    {"name": "editorial_typography", "source": "deterministic", "required": True},
                ]
            },
        }
        bindings = []
        for index, (gate, payload) in enumerate(evidence_payloads.items(), start=1):
            full = {"gate_id": gate, "story_snapshot_sha256": self.STORY_SHA, **payload}
            path = evidence_dir / f"{index:02d}_{gate}.json"
            raw = self._write(path, full)
            bindings.append(
                {
                    "gate_id": gate,
                    "repository_relative_path": path.relative_to(root).as_posix(),
                    "byte_size": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            )

        run = root / "artifacts" / "cs257"
        run.mkdir(parents=True)
        manifest = {
            "schema": FRESH_STORY_EVIDENCE_MANIFEST_SCHEMA,
            "evidence_bindings": bindings,
        }
        artifacts = []
        for name, payload in (
            ("fresh_story_evidence_manifest.json", manifest),
            ("fresh_story_gate_verification_contract.json", {"fixture": "contract"}),
            ("fresh_story_gate_receipt_bundle.json", {"fixture": "bundle"}),
            (
                "fresh_story_gate_semantic_replay.json",
                {
                    "story_snapshot_sha256": self.STORY_SHA,
                    "all_gate_specific_verifiers_executed": True,
                    "fresh_story_gates_passed": True,
                },
            ),
        ):
            raw = self._write(run / name, payload)
            artifacts.append(
                {"path": name, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}
            )
        receipt = {
            "schema": ATOMIC_FRESH_STORY_SEMANTIC_REPLAY_SCHEMA,
            "story_snapshot_sha256": self.STORY_SHA,
            "artifacts": artifacts,
            "production_semantic_replay_executed": True,
            "fresh_story_gates_passed": True,
            "controlled_trial_preflight_valid": False,
            "canonical_generation_authorized": False,
            "model_weights_loaded": False,
            "inference_executed": False,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        self._write(run / "atomic_fresh_story_semantic_replay.json", receipt)
        return run

    def _auth(self) -> dict:
        return {
            "story_snapshot_sha256": self.STORY_SHA,
            "authorization_sha256": self.AUTH_SHA,
            "canonical_generation_authorized": True,
        }

    def test_prompt_is_deterministically_derived_from_replayed_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs257 = self._cs257(root)
            auth = root / "auth.json"
            auth.write_text("{}\n", encoding="utf-8")
            with patch(
                "engine.intelligence.qwen_image_story_bound_canonical_prompt.verify_story_bound_generation_authorization",
                return_value=self._auth(),
            ):
                result = build_story_bound_canonical_prompt(cs257, auth, repo_root=root)
            self.assertEqual(result.contract["schema"], STORY_BOUND_CANONICAL_PROMPT_SCHEMA)
            self.assertTrue(result.contract["deterministically_derived_from_replayed_story_evidence"])
            self.assertFalse(result.contract["free_form_prompt_substitution_allowed"])
            self.assertIn("Club A defeated Club B 2-1.", result.prompt)
            self.assertIn("without humiliating", result.prompt)
            self.assertIn("Do not generate any exact text", result.prompt)
            self.assertIn("generated text", result.negative_prompt)

    def test_cross_story_authorization_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs257 = self._cs257(root)
            auth = root / "auth.json"
            auth.write_text("{}\n", encoding="utf-8")
            wrong = self._auth()
            wrong["story_snapshot_sha256"] = "c" * 64
            with patch(
                "engine.intelligence.qwen_image_story_bound_canonical_prompt.verify_story_bound_generation_authorization",
                return_value=wrong,
            ):
                with self.assertRaisesRegex(ValueError, "CROSS_STORY_AUTHORIZATION"):
                    build_story_bound_canonical_prompt(cs257, auth, repo_root=root)

    def test_evidence_byte_tamper_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cs257 = self._cs257(root)
            auth = root / "auth.json"
            auth.write_text("{}\n", encoding="utf-8")
            (root / "evidence" / "01_fact_lock.json").write_text("{}\n", encoding="utf-8")
            with patch(
                "engine.intelligence.qwen_image_story_bound_canonical_prompt.verify_story_bound_generation_authorization",
                return_value=self._auth(),
            ):
                with self.assertRaisesRegex(ValueError, "EVIDENCE_BYTE_DRIFT"):
                    build_story_bound_canonical_prompt(cs257, auth, repo_root=root)


if __name__ == "__main__":
    unittest.main()
