from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

import tools.phase18_continue_admitted_composition_to_quality_review as checkpoint


class AdmittedCompositionQualityReviewCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path.cwd().resolve()

    def _base_payloads(self, root: Path):
        story_sha = "a" * 64
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
        downstream_false = {
            "composed_visual_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        cs272_path = root / "upstream" / "cs272" / "admission.json"
        cs272_path.parent.mkdir(parents=True)
        cs272_path.write_text("{}\n", encoding="utf-8")
        cs321_path = root / "upstream" / "checkpoint.json"
        cs321_payload = {
            "schema": checkpoint.CS321_SCHEMA,
            "authoritative": False,
            "story_snapshot_sha256": story_sha,
            "candidate_png": candidate,
            "composed_candidate_png": composed,
            "cs272_receipt": cs272_path.relative_to(self.repo_root).as_posix(),
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            **downstream_false,
        }
        cs321_path.write_text(json.dumps(cs321_payload) + "\n", encoding="utf-8")
        cs272_payload = {
            "schema": checkpoint.CS272_SCHEMA,
            "story_snapshot_sha256": story_sha,
            "source_candidate_png": candidate,
            "composed_candidate_png": composed,
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            **downstream_false,
        }
        return story_sha, candidate, composed, cs321_path, cs272_path, cs272_payload

    def test_semantic_pass_flows_to_exact_cs274_request_without_authority_escalation(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            story_sha, candidate, composed, cs321_path, cs272_path, cs272 = self._base_payloads(root)
            output_dir = root / "run"
            cs273_path = output_dir / "cs273" / "semantic.json"
            cs274_path = output_dir / "cs274" / "request.json"
            downstream_false = {
                "composed_visual_approved": False,
                "semantic_approved": False,
                "human_visual_review_approved": False,
                "golden_quality_approved": False,
                "genuine_golden_png_created": False,
                "publication_ready": False,
            }
            cs273 = {
                "schema": checkpoint.CS273_SCHEMA,
                "story_snapshot_sha256": story_sha,
                "composed_candidate_png": composed,
                "semantic_inspection_executed": True,
                "hybrid_surface_semantic_qa_approved": True,
                **downstream_false,
            }
            cs274 = {
                "schema": checkpoint.CS274_SCHEMA,
                "story_snapshot_sha256": story_sha,
                "composed_candidate_png": composed,
                "visual_quality_review_requested": True,
                **downstream_false,
            }

            def fake_run(source_path, semantic_dir, *, repo_root):
                self.assertEqual(source_path, cs272_path.resolve())
                self.assertEqual(semantic_dir, output_dir / "cs273")
                cs273_path.parent.mkdir(parents=True)
                cs273_path.write_text("{}\n", encoding="utf-8")
                return SimpleNamespace(receipt_path=cs273_path)

            def fake_build(source_path, quality_dir, *, repo_root):
                self.assertEqual(source_path, cs273_path)
                self.assertEqual(quality_dir, output_dir / "cs274")
                cs274_path.parent.mkdir(parents=True)
                cs274_path.write_text("{}\n", encoding="utf-8")
                return cs274_path

            with (
                mock.patch.object(checkpoint, "verify_composed_candidate_byte_admission", return_value=cs272),
                mock.patch.object(checkpoint, "run_composed_candidate_hybrid_surface_semantic_qa", side_effect=fake_run),
                mock.patch.object(checkpoint, "verify_composed_candidate_hybrid_surface_semantic_qa", return_value=cs273),
                mock.patch.object(checkpoint, "build_composed_candidate_visual_quality_review_request", side_effect=fake_build),
                mock.patch.object(checkpoint, "verify_composed_candidate_visual_quality_review_request", return_value=cs274),
            ):
                result_path = checkpoint.continue_admitted_composition_to_quality_review(
                    cs321_path,
                    output_dir,
                    repo_root=self.repo_root,
                )

            payload = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "VISUAL_QUALITY_REVIEW_EVIDENCE_REQUIRED")
            self.assertTrue(payload["hybrid_surface_semantic_qa_approved"])
            self.assertTrue(payload["visual_quality_review_requested"])
            self.assertFalse(payload["visual_quality_review_executed"])
            self.assertFalse(payload["visual_quality_review_approved"])
            self.assertFalse(payload["authoritative"])
            for field in checkpoint._DOWNSTREAM_FALSE:
                self.assertIs(payload[field], False)

    def test_semantic_rejection_never_builds_cs274(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            story_sha, _, composed, cs321_path, _, cs272 = self._base_payloads(root)
            output_dir = root / "run"
            cs273_path = output_dir / "cs273" / "semantic.json"
            cs273 = {
                "schema": checkpoint.CS273_SCHEMA,
                "story_snapshot_sha256": story_sha,
                "composed_candidate_png": composed,
                "semantic_inspection_executed": True,
                "hybrid_surface_semantic_qa_approved": False,
                **{field: False for field in checkpoint._DOWNSTREAM_FALSE},
            }

            def fake_run(*args, **kwargs):
                cs273_path.parent.mkdir(parents=True)
                cs273_path.write_text("{}\n", encoding="utf-8")
                return SimpleNamespace(receipt_path=cs273_path)

            with (
                mock.patch.object(checkpoint, "verify_composed_candidate_byte_admission", return_value=cs272),
                mock.patch.object(checkpoint, "run_composed_candidate_hybrid_surface_semantic_qa", side_effect=fake_run),
                mock.patch.object(checkpoint, "verify_composed_candidate_hybrid_surface_semantic_qa", return_value=cs273),
                mock.patch.object(checkpoint, "build_composed_candidate_visual_quality_review_request") as build,
            ):
                result_path = checkpoint.continue_admitted_composition_to_quality_review(
                    cs321_path,
                    output_dir,
                    repo_root=self.repo_root,
                )

            build.assert_not_called()
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["status"],
                "COMPOSED_CANDIDATE_REJECTED_BY_HYBRID_SURFACE_SEMANTIC_QA",
            )
            self.assertFalse(payload["hybrid_surface_semantic_qa_approved"])
            self.assertFalse(payload["visual_quality_review_requested"])
            self.assertIsNone(payload["cs274_receipt"])

    def test_lineage_and_authority_guards_are_fail_closed(self) -> None:
        source = Path("tools/phase18_continue_admitted_composition_to_quality_review.py").read_text(
            encoding="utf-8"
        )
        for marker in (
            "QWEN_POST_COMPOSITION_CROSS_STORY",
            "QWEN_POST_COMPOSITION_SOURCE_CANDIDATE_DRIFT",
            "QWEN_POST_COMPOSITION_COMPOSED_BYTES_DRIFT",
            "QWEN_POST_COMPOSITION_CS273_CROSS_STORY",
            "QWEN_POST_COMPOSITION_CS273_COMPOSED_BYTES_DRIFT",
            "QWEN_POST_COMPOSITION_CS274_CROSS_STORY",
            "QWEN_POST_COMPOSITION_CS274_COMPOSED_BYTES_DRIFT",
        ):
            self.assertIn(marker, source)
        self.assertIn('os.environ["HF_HUB_OFFLINE"] = "1"', source)
        self.assertIn('os.environ["TRANSFORMERS_OFFLINE"] = "1"', source)
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn("golden_quality_approved = True", source)
        self.assertNotIn("publication_ready = True", source)


if __name__ == "__main__":
    unittest.main()
