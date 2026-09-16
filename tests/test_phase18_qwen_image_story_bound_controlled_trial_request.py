from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_atomic_fresh_story_semantic_replay import (
    ATOMIC_FRESH_STORY_SEMANTIC_REPLAY_SCHEMA,
)
from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA,
    REQUIRED_FRESH_GATE_EVIDENCE,
    REQUIRED_PIXEL_BOUNDARIES,
    REQUIRED_POST_GENERATION_GATES,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_story_bound_controlled_trial_request import (
    STORY_BOUND_CONTROLLED_TRIAL_REQUEST_SCHEMA,
    build_story_bound_controlled_trial_request,
)


class StoryBoundControlledTrialRequestTests(unittest.TestCase):
    STORY_SHA = "a" * 64

    def _write_json(self, path: Path, payload: dict) -> bytes:
        raw = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
        path.write_bytes(raw)
        return raw

    def _preflight(self, root: Path) -> Path:
        payload = {
            "schema": CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA,
            "status": "QWEN_IMAGE_2512_CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_CONTRACT_LOCKED",
            "cost_mode": COST_MODE,
            "preflight_contract_locked": True,
            "live_same_host_recheck_required": True,
            "fresh_story_gate_evidence_required": True,
            "fresh_gate_evidence_required": list(REQUIRED_FRESH_GATE_EVIDENCE),
            "pixel_boundaries_required": list(REQUIRED_PIXEL_BOUNDARIES),
            "post_generation_gates_required": list(REQUIRED_POST_GENERATION_GATES),
            "golden_minimum_score": 8.5,
            "elite_quality_score": 9.0,
            "controlled_trial_preflight_valid": False,
            "live_host_recheck_passed": False,
            "fresh_story_gates_passed": False,
            "genuine_canonical_inference_executed": False,
            "genuine_golden_png_created": False,
            "runtime_floor_proven": False,
            "local_runtime_qualified": False,
            "canonical_generation_authorized": False,
            "canonical_pixels_reusable": False,
            "queue_mutated": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        payload["preflight_contract_sha256"] = sha256_json(payload)
        path = root / "preflight.json"
        self._write_json(path, payload)
        return path

    def _cs257(self, root: Path) -> Path:
        run = root / "artifacts" / "cs257"
        run.mkdir(parents=True)
        artifacts = []
        names = (
            "fresh_story_evidence_manifest.json",
            "fresh_story_gate_verification_contract.json",
            "fresh_story_gate_receipt_bundle.json",
            "fresh_story_gate_semantic_replay.json",
        )
        for name in names:
            if name == "fresh_story_gate_semantic_replay.json":
                payload = {
                    "story_snapshot_sha256": self.STORY_SHA,
                    "all_gate_specific_verifiers_executed": True,
                    "fresh_story_gates_passed": True,
                }
            else:
                payload = {"fixture": name, "story_snapshot_sha256": self.STORY_SHA}
            raw = self._write_json(run / name, payload)
            artifacts.append(
                {
                    "path": name,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "byte_size": len(raw),
                }
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
        self._write_json(run / "atomic_fresh_story_semantic_replay.json", receipt)
        return run

    def test_success_binds_story_and_keeps_runtime_generation_publication_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight(root)
            cs257 = self._cs257(root)
            result = build_story_bound_controlled_trial_request(
                cs257,
                preflight,
                root / "artifacts" / "cs258",
                repo_root=root,
            )
            payload = json.loads(result.request_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], STORY_BOUND_CONTROLLED_TRIAL_REQUEST_SCHEMA)
            self.assertEqual(payload["story_snapshot_sha256"], self.STORY_SHA)
            self.assertTrue(payload["production_semantic_replay_executed"])
            self.assertTrue(payload["fresh_story_gates_passed"])
            self.assertTrue(payload["live_same_host_recheck_required"])
            for field in (
                "live_host_recheck_passed",
                "controlled_trial_preflight_valid",
                "canonical_generation_authorized",
                "model_weights_loaded",
                "inference_executed",
                "genuine_canonical_inference_executed",
                "genuine_golden_png_created",
                "semantic_approved",
                "human_visual_review_approved",
                "golden_quality_approved",
                "publication_ready",
            ):
                self.assertFalse(payload[field])
            claimed = payload["request_sha256"]
            unsigned = dict(payload)
            unsigned.pop("request_sha256")
            self.assertEqual(claimed, sha256_json(unsigned))

    def test_cs257_artifact_tamper_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight(root)
            cs257 = self._cs257(root)
            (cs257 / "fresh_story_gate_semantic_replay.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ARTIFACT_BINDING_DRIFT"):
                build_story_bound_controlled_trial_request(
                    cs257, preflight, root / "artifacts" / "cs258", repo_root=root
                )
            self.assertFalse((root / "artifacts" / "cs258").exists())

    def test_preflight_authority_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight(root)
            payload = json.loads(preflight.read_text(encoding="utf-8"))
            payload["canonical_generation_authorized"] = True
            unsigned = dict(payload)
            unsigned.pop("preflight_contract_sha256", None)
            payload["preflight_contract_sha256"] = sha256_json(unsigned)
            self._write_json(preflight, payload)
            cs257 = self._cs257(root)
            with self.assertRaisesRegex(ValueError, "PREFLIGHT_AUTHORITY_DRIFT"):
                build_story_bound_controlled_trial_request(
                    cs257, preflight, root / "artifacts" / "cs258", repo_root=root
                )

    def test_symlinked_cs257_run_is_rejected_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight(root)
            cs257 = self._cs257(root)
            alias = root / "artifacts" / "cs257-link"
            alias.symlink_to(cs257, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "CS257_RUN_INVALID"):
                build_story_bound_controlled_trial_request(
                    alias, preflight, root / "artifacts" / "cs258", repo_root=root
                )
            self.assertFalse((root / "artifacts" / "cs258").exists())

    def test_symlinked_preflight_is_rejected_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight(root)
            cs257 = self._cs257(root)
            alias = root / "preflight-link.json"
            alias.symlink_to(preflight)
            with self.assertRaisesRegex(ValueError, "PREFLIGHT_OUTSIDE_REPOSITORY"):
                build_story_bound_controlled_trial_request(
                    cs257, alias, root / "artifacts" / "cs258", repo_root=root
                )
            self.assertFalse((root / "artifacts" / "cs258").exists())

    def test_existing_output_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            preflight = self._preflight(root)
            cs257 = self._cs257(root)
            output = root / "artifacts" / "cs258"
            output.mkdir()
            with self.assertRaisesRegex(ValueError, "OUTPUT_ALREADY_EXISTS"):
                build_story_bound_controlled_trial_request(
                    cs257, preflight, output, repo_root=root
                )


if __name__ == "__main__":
    unittest.main()
