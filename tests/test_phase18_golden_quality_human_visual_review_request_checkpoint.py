from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import tools.phase18_continue_golden_quality_to_human_visual_review_request as checkpoint


class GoldenQualityHumanVisualReviewRequestCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path.cwd().resolve()

    def _fixture(self, root: Path):
        story = "a" * 64
        candidate = {
            "repository_relative_path": "candidate.png",
            "sha256": "b" * 64,
            "byte_size": 24,
            "width": 1280,
            "height": 720,
        }
        composed = {
            "repository_relative_path": "composed.png",
            "sha256": "c" * 64,
            "byte_size": 24,
            "width": 1280,
            "height": 720,
        }
        cs276_path = root / "upstream" / "cs276.json"
        cs276_path.parent.mkdir(parents=True, exist_ok=True)
        cs276_path.write_text("{}\n", encoding="utf-8")
        cs323_path = root / "upstream" / "cs323.json"
        cs323 = {
            "schema": checkpoint.CS323_SCHEMA,
            "status": "GOLDEN_QUALITY_PASSED_AWAITING_DOWNSTREAM_HUMAN_REVIEW",
            "authoritative": False,
            "story_snapshot_sha256": story,
            "candidate_png": candidate,
            "composed_candidate_png": composed,
            "cs276_receipt": cs276_path.relative_to(self.repo_root).as_posix(),
            "visual_quality_review_requested": True,
            "visual_quality_review_executed": True,
            "visual_quality_evidence_admitted": True,
            "visual_quality_review_approved": True,
            "golden_quality_approved": True,
            **{field: False for field in checkpoint._FINAL_FALSE},
        }
        cs323_path.write_text(json.dumps(cs323) + "\n", encoding="utf-8")
        cs276 = {
            "schema": checkpoint.CS276_SCHEMA,
            "story_snapshot_sha256": story,
            "source_candidate_png": candidate,
            "composed_candidate_png": composed,
            "golden_quality_selector_executed": True,
            "golden_quality_approved": True,
            **{field: False for field in checkpoint._FINAL_FALSE},
        }
        return story, candidate, composed, cs323_path, cs276_path, cs276

    def test_exact_golden_pass_creates_only_human_review_request(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            story, candidate, composed, cs323_path, cs276_path, cs276 = self._fixture(root)
            output_dir = root / "run"
            cs277_path = output_dir / "cs277" / "request.json"
            cs277 = {
                "schema": checkpoint.CS277_SCHEMA,
                "story_snapshot_sha256": story,
                "composed_candidate_png": composed,
                "golden_quality_approved": True,
                "human_visual_review_requested": True,
                "human_visual_review_executed": False,
                "human_visual_review_approved": False,
                **{field: False for field in checkpoint._FINAL_FALSE},
            }

            def fake_build(source_path, target_dir, *, repo_root):
                self.assertEqual(source_path, cs276_path.resolve())
                self.assertEqual(target_dir, output_dir / "cs277")
                self.assertEqual(repo_root, self.repo_root)
                cs277_path.parent.mkdir(parents=True)
                cs277_path.write_text("{}\n", encoding="utf-8")
                return cs277_path

            with (
                mock.patch.object(
                    checkpoint,
                    "verify_composed_candidate_golden_quality_adjudication",
                    return_value=cs276,
                ),
                mock.patch.object(
                    checkpoint,
                    "build_composed_candidate_human_visual_review_request",
                    side_effect=fake_build,
                ),
                mock.patch.object(
                    checkpoint,
                    "verify_composed_candidate_human_visual_review_request",
                    return_value=cs277,
                ),
            ):
                result = checkpoint.continue_golden_quality_to_human_visual_review_request(
                    cs323_path,
                    output_dir,
                    repo_root=self.repo_root,
                )

            payload = json.loads(result.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "HUMAN_VISUAL_REVIEW_EVIDENCE_REQUIRED")
            self.assertEqual(payload["story_snapshot_sha256"], story)
            self.assertEqual(payload["candidate_png"], candidate)
            self.assertEqual(payload["composed_candidate_png"], composed)
            self.assertTrue(payload["golden_quality_approved"])
            self.assertTrue(payload["human_visual_review_requested"])
            self.assertFalse(payload["human_visual_review_executed"])
            self.assertFalse(payload["authoritative"])
            for field in checkpoint._FINAL_FALSE:
                self.assertIs(payload[field], False)

    def test_rejected_cs323_cannot_open_human_review_request(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            _, _, _, cs323_path, _, _ = self._fixture(root)
            payload = json.loads(cs323_path.read_text(encoding="utf-8"))
            payload["status"] = "COMPOSED_CANDIDATE_REJECTED_BY_GOLDEN_QUALITY"
            payload["golden_quality_approved"] = False
            cs323_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            with mock.patch.object(
                checkpoint,
                "build_composed_candidate_human_visual_review_request",
            ) as build_request:
                with self.assertRaisesRegex(ValueError, "QWEN_CS324_CS323_NOT_GOLDEN_QUALITY_PASSED"):
                    checkpoint.continue_golden_quality_to_human_visual_review_request(
                        cs323_path,
                        root / "run",
                        repo_root=self.repo_root,
                    )
                build_request.assert_not_called()

    def test_cross_story_and_byte_drift_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            _, _, _, cs323_path, _, cs276 = self._fixture(root)
            cs276 = dict(cs276)
            cs276["story_snapshot_sha256"] = "d" * 64
            with mock.patch.object(
                checkpoint,
                "verify_composed_candidate_golden_quality_adjudication",
                return_value=cs276,
            ):
                with self.assertRaisesRegex(ValueError, "QWEN_CS324_CROSS_STORY"):
                    checkpoint.continue_golden_quality_to_human_visual_review_request(
                        cs323_path,
                        root / "run",
                        repo_root=self.repo_root,
                    )

        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            _, _, _, cs323_path, _, cs276 = self._fixture(root)
            cs276 = dict(cs276)
            cs276["composed_candidate_png"] = {
                "repository_relative_path": "other.png",
                "sha256": "e" * 64,
                "byte_size": 24,
                "width": 1280,
                "height": 720,
            }
            with mock.patch.object(
                checkpoint,
                "verify_composed_candidate_golden_quality_adjudication",
                return_value=cs276,
            ):
                with self.assertRaisesRegex(ValueError, "QWEN_CS324_COMPOSED_BYTES_DRIFT"):
                    checkpoint.continue_golden_quality_to_human_visual_review_request(
                        cs323_path,
                        root / "run",
                        repo_root=self.repo_root,
                    )

    def test_human_verdict_is_never_generated_by_orchestrator(self) -> None:
        source = Path(
            "tools/phase18_continue_golden_quality_to_human_visual_review_request.py"
        ).read_text(encoding="utf-8")
        for marker in (
            "QWEN_CS324_CROSS_STORY",
            "QWEN_CS324_SOURCE_CANDIDATE_DRIFT",
            "QWEN_CS324_COMPOSED_BYTES_DRIFT",
            "QWEN_CS324_CS277_CROSS_STORY",
            "QWEN_CS324_CS277_COMPOSED_BYTES_DRIFT",
        ):
            self.assertIn(marker, source)
        self.assertIn("build_composed_candidate_human_visual_review_request", source)
        self.assertIn("verify_composed_candidate_human_visual_review_request", source)
        self.assertIn('os.environ["HF_HUB_OFFLINE"] = "1"', source)
        self.assertNotIn("build_composed_candidate_human_visual_review_evidence", source)
        self.assertNotIn("independent_manual_human_visual_review", source)
        self.assertNotIn('"decision": "approve"', source)
        self.assertNotIn("human_visual_review_approved = True", source)
        self.assertNotIn("publication_ready = True", source)
        self.assertNotIn("QwenImagePipeline", source)


if __name__ == "__main__":
    unittest.main()
