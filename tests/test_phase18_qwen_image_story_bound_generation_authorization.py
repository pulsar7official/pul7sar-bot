from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_live_pipeline_load_recheck import (
    LIVE_PIPELINE_LOAD_RECHECK_SCHEMA,
)
from engine.intelligence.qwen_image_story_bound_generation_authorization import (
    STORY_BOUND_GENERATION_AUTHORIZATION_SCHEMA,
    build_story_bound_generation_authorization,
    verify_story_bound_generation_authorization,
)


class StoryBoundGenerationAuthorizationTests(unittest.TestCase):
    STORY_SHA = "c" * 64
    RUNTIME_SHA = "d" * 64

    def _write_cs260(self, root: Path, **overrides: object) -> Path:
        payload = {
            "schema": LIVE_PIPELINE_LOAD_RECHECK_SCHEMA,
            "status": "QWEN_IMAGE_2512_LIVE_PIPELINE_LOAD_RECHECK_PASSED",
            "story_snapshot_sha256": self.STORY_SHA,
            "model_id": QWEN_IMAGE_2512_MODEL_ID,
            "model_revision": QWEN_IMAGE_2512_REVISION,
            "cost_mode": COST_MODE,
            "expected_runtime_fingerprint_sha256": self.RUNTIME_SHA,
            "production_semantic_replay_executed": True,
            "fresh_story_gates_passed": True,
            "live_observable_host_identity_matched": True,
            "model_weights_loaded": True,
            "sequential_cpu_offload_enabled": True,
            "live_host_recheck_passed": True,
            "controlled_trial_preflight_valid": True,
            "canonical_generation_authorized": False,
            "inference_executed": False,
            "genuine_canonical_inference_executed": False,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        payload.update(overrides)
        payload["receipt_sha256"] = sha256_json(payload)
        path = root / "artifacts" / "cs260" / "live_pipeline_load_recheck.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
        return path

    def test_exact_cs260_authorizes_generation_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._write_cs260(root)
            run = build_story_bound_generation_authorization(
                source, root / "artifacts" / "cs261", repo_root=root
            )
            payload = verify_story_bound_generation_authorization(
                run.receipt_path, repo_root=root
            )
            self.assertEqual(payload["schema"], STORY_BOUND_GENERATION_AUTHORIZATION_SCHEMA)
            self.assertEqual(payload["story_snapshot_sha256"], self.STORY_SHA)
            self.assertTrue(payload["canonical_generation_authorized"])
            self.assertEqual(
                payload["authorization_scope"],
                "single_story_single_model_revision_single_runtime_fingerprint",
            )
            for field in (
                "inference_executed",
                "genuine_canonical_inference_executed",
                "genuine_golden_png_created",
                "semantic_approved",
                "human_visual_review_approved",
                "golden_quality_approved",
                "publication_ready",
            ):
                self.assertFalse(payload[field])

    def test_missing_fresh_story_gate_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._write_cs260(root, fresh_story_gates_passed=False)
            with self.assertRaisesRegex(
                ValueError, "REQUIRED_GATE_MISSING:fresh_story_gates_passed"
            ):
                build_story_bound_generation_authorization(
                    source, root / "artifacts" / "cs261", repo_root=root
                )
            self.assertFalse((root / "artifacts" / "cs261").exists())

    def test_premature_inference_claim_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._write_cs260(root, inference_executed=True)
            with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:inference_executed"):
                build_story_bound_generation_authorization(
                    source, root / "artifacts" / "cs261", repo_root=root
                )

    def test_nonzero_cost_mode_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._write_cs260(root, cost_mode="paid-api")
            with self.assertRaisesRegex(ValueError, "COST_MODE_DRIFT"):
                build_story_bound_generation_authorization(
                    source, root / "artifacts" / "cs261", repo_root=root
                )

    def test_source_tamper_after_authorization_invalidates_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._write_cs260(root)
            run = build_story_bound_generation_authorization(
                source, root / "artifacts" / "cs261", repo_root=root
            )
            source.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SOURCE_BYTE_DRIFT"):
                verify_story_bound_generation_authorization(run.receipt_path, repo_root=root)

    def test_authorization_tamper_fails_digest_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._write_cs260(root)
            run = build_story_bound_generation_authorization(
                source, root / "artifacts" / "cs261", repo_root=root
            )
            payload = json.loads(run.receipt_path.read_text(encoding="utf-8"))
            payload["publication_ready"] = True
            run.receipt_path.write_text(
                json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "DOWNSTREAM_AUTHORITY_DRIFT:publication_ready"):
                verify_story_bound_generation_authorization(run.receipt_path, repo_root=root)

    def test_output_must_not_preexist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._write_cs260(root)
            output = root / "artifacts" / "cs261"
            output.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "OUTPUT_ALREADY_EXISTS"):
                build_story_bound_generation_authorization(source, output, repo_root=root)


if __name__ == "__main__":
    unittest.main()
