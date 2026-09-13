from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import tools.phase18_continue_visual_quality_evidence_to_golden_adjudication as checkpoint


class VisualQualityEvidenceGoldenAdjudicationCheckpointTests(unittest.TestCase):
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
        cs272_path = root / "upstream" / "cs272.json"
        cs274_path = root / "upstream" / "cs274.json"
        admission_path = root / "upstream" / "admission.json"
        external_path = root / "review" / "manual_review.json"
        for path in (cs272_path, cs274_path, admission_path, external_path):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n", encoding="utf-8")
        cs322_path = root / "upstream" / "cs322.json"
        cs322 = {
            "schema": checkpoint.CS322_SCHEMA,
            "status": "VISUAL_QUALITY_REVIEW_EVIDENCE_REQUIRED",
            "authoritative": False,
            "story_snapshot_sha256": story,
            "candidate_png": candidate,
            "composed_candidate_png": composed,
            "cs272_receipt": cs272_path.relative_to(self.repo_root).as_posix(),
            "cs274_receipt": cs274_path.relative_to(self.repo_root).as_posix(),
            "hybrid_surface_semantic_qa_approved": True,
            "visual_quality_review_requested": True,
            "visual_quality_review_executed": False,
            "golden_quality_approved": False,
            **{field: False for field in checkpoint._FINAL_FALSE},
        }
        cs322_path.write_text(json.dumps(cs322) + "\n", encoding="utf-8")
        cs272 = {
            "schema": checkpoint.CS272_SCHEMA,
            "story_snapshot_sha256": story,
            "source_candidate_png": candidate,
            "composed_candidate_png": composed,
            **{field: False for field in checkpoint._FINAL_FALSE},
        }
        cs274 = {
            "schema": checkpoint.CS274_SCHEMA,
            "story_snapshot_sha256": story,
            "composed_candidate_png": composed,
            "visual_quality_review_requested": True,
            **{field: False for field in checkpoint._FINAL_FALSE},
        }
        admission = {
            "schema": checkpoint.CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA,
            "story_snapshot_sha256": story,
            "candidate_png": candidate,
            "cost_mode": "$0-local",
            "network_allowed": False,
            "local_files_only": True,
            **{field: False for field in checkpoint._CANDIDATE_ADMISSION_FALSE},
        }
        return (
            story,
            candidate,
            composed,
            cs322_path,
            cs272_path,
            cs274_path,
            admission_path,
            external_path,
            cs272,
            cs274,
            admission,
        )

    def test_exact_manual_evidence_flows_to_golden_adjudication_without_final_authority(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            (
                story,
                candidate,
                composed,
                cs322_path,
                cs272_path,
                cs274_path,
                admission_path,
                external_path,
                cs272,
                cs274,
                admission,
            ) = self._fixture(root)
            output_dir = root / "run"
            cs275_path = output_dir / "cs275" / "evidence.json"
            cs276_path = output_dir / "cs276" / "adjudication.json"
            cs275 = {
                "schema": checkpoint.CS275_SCHEMA,
                "story_snapshot_sha256": story,
                "composed_candidate_png": composed,
                "visual_quality_review_executed": True,
                "visual_quality_evidence_admitted": True,
                **{field: False for field in checkpoint._FINAL_FALSE},
            }
            cs276 = {
                "schema": checkpoint.CS276_SCHEMA,
                "story_snapshot_sha256": story,
                "source_candidate_png": candidate,
                "composed_candidate_png": composed,
                "visual_quality_review_approved": True,
                "golden_quality_approved": True,
                **{field: False for field in checkpoint._FINAL_FALSE},
            }

            def fake_build_275(request_path, review_path, target_dir, *, repo_root):
                self.assertEqual(request_path, cs274_path.resolve())
                self.assertEqual(review_path, external_path.resolve())
                self.assertEqual(target_dir, output_dir / "cs275")
                cs275_path.parent.mkdir(parents=True)
                cs275_path.write_text("{}\n", encoding="utf-8")
                return cs275_path

            def fake_build_276(candidate_path, composed_path, evidence_path, target_dir, *, repo_root):
                self.assertEqual(candidate_path, admission_path.resolve())
                self.assertEqual(composed_path, cs272_path.resolve())
                self.assertEqual(evidence_path, cs275_path)
                self.assertEqual(target_dir, output_dir / "cs276")
                cs276_path.parent.mkdir(parents=True)
                cs276_path.write_text("{}\n", encoding="utf-8")
                return cs276_path

            with (
                mock.patch.object(checkpoint, "verify_composed_candidate_byte_admission", return_value=cs272),
                mock.patch.object(checkpoint, "verify_composed_candidate_visual_quality_review_request", return_value=cs274),
                mock.patch.object(checkpoint, "verify_canonical_candidate_byte_admission", return_value=admission),
                mock.patch.object(checkpoint, "build_composed_candidate_visual_quality_review_evidence", side_effect=fake_build_275),
                mock.patch.object(checkpoint, "verify_composed_candidate_visual_quality_review_evidence", return_value=cs275),
                mock.patch.object(checkpoint, "build_composed_candidate_golden_quality_adjudication", side_effect=fake_build_276),
                mock.patch.object(checkpoint, "verify_composed_candidate_golden_quality_adjudication", return_value=cs276),
            ):
                result = checkpoint.continue_visual_quality_evidence_to_golden_adjudication(
                    cs322_path,
                    external_path,
                    admission_path,
                    output_dir,
                    repo_root=self.repo_root,
                )

            payload = json.loads(result.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["status"],
                "GOLDEN_QUALITY_PASSED_AWAITING_DOWNSTREAM_HUMAN_REVIEW",
            )
            self.assertTrue(payload["visual_quality_review_executed"])
            self.assertTrue(payload["visual_quality_evidence_admitted"])
            self.assertTrue(payload["golden_quality_approved"])
            self.assertFalse(payload["authoritative"])
            for field in checkpoint._FINAL_FALSE:
                self.assertIs(payload[field], False)

    def test_golden_rejection_is_preserved_and_not_overridden(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            (
                story,
                candidate,
                composed,
                cs322_path,
                _,
                _,
                admission_path,
                external_path,
                cs272,
                cs274,
                admission,
            ) = self._fixture(root)
            output_dir = root / "run"
            cs275_path = output_dir / "cs275" / "evidence.json"
            cs276_path = output_dir / "cs276" / "adjudication.json"
            cs275 = {
                "schema": checkpoint.CS275_SCHEMA,
                "story_snapshot_sha256": story,
                "composed_candidate_png": composed,
                "visual_quality_review_executed": True,
                "visual_quality_evidence_admitted": True,
                **{field: False for field in checkpoint._FINAL_FALSE},
            }
            cs276 = {
                "schema": checkpoint.CS276_SCHEMA,
                "story_snapshot_sha256": story,
                "source_candidate_png": candidate,
                "composed_candidate_png": composed,
                "visual_quality_review_approved": False,
                "golden_quality_approved": False,
                **{field: False for field in checkpoint._FINAL_FALSE},
            }

            def build_275(*args, **kwargs):
                cs275_path.parent.mkdir(parents=True)
                cs275_path.write_text("{}\n", encoding="utf-8")
                return cs275_path

            def build_276(*args, **kwargs):
                cs276_path.parent.mkdir(parents=True)
                cs276_path.write_text("{}\n", encoding="utf-8")
                return cs276_path

            with (
                mock.patch.object(checkpoint, "verify_composed_candidate_byte_admission", return_value=cs272),
                mock.patch.object(checkpoint, "verify_composed_candidate_visual_quality_review_request", return_value=cs274),
                mock.patch.object(checkpoint, "verify_canonical_candidate_byte_admission", return_value=admission),
                mock.patch.object(checkpoint, "build_composed_candidate_visual_quality_review_evidence", side_effect=build_275),
                mock.patch.object(checkpoint, "verify_composed_candidate_visual_quality_review_evidence", return_value=cs275),
                mock.patch.object(checkpoint, "build_composed_candidate_golden_quality_adjudication", side_effect=build_276),
                mock.patch.object(checkpoint, "verify_composed_candidate_golden_quality_adjudication", return_value=cs276),
            ):
                result = checkpoint.continue_visual_quality_evidence_to_golden_adjudication(
                    cs322_path,
                    external_path,
                    admission_path,
                    output_dir,
                    repo_root=self.repo_root,
                )
            payload = json.loads(result.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "COMPOSED_CANDIDATE_REJECTED_BY_GOLDEN_QUALITY")
            self.assertFalse(payload["golden_quality_approved"])

    def test_lineage_zero_cost_and_no_fabrication_guards_are_present(self) -> None:
        source = Path("tools/phase18_continue_visual_quality_evidence_to_golden_adjudication.py").read_text(
            encoding="utf-8"
        )
        for marker in (
            "QWEN_CS323_CROSS_STORY",
            "QWEN_CS323_SOURCE_CANDIDATE_DRIFT",
            "QWEN_CS323_CANDIDATE_ADMISSION_DRIFT",
            "QWEN_CS323_COMPOSED_BYTES_DRIFT",
            "QWEN_CS323_CS274_COMPOSED_BYTES_DRIFT",
            "QWEN_CS323_CS275_COMPOSED_BYTES_DRIFT",
            "QWEN_CS323_CS276_SOURCE_CANDIDATE_DRIFT",
            "QWEN_CS323_CS276_COMPOSED_BYTES_DRIFT",
            "QWEN_CS323_ZERO_COST_LOCAL_ONLY_DRIFT",
        ):
            self.assertIn(marker, source)
        self.assertIn("build_composed_candidate_visual_quality_review_evidence", source)
        self.assertIn("verify_composed_candidate_visual_quality_review_evidence", source)
        self.assertIn("build_composed_candidate_golden_quality_adjudication", source)
        self.assertIn("verify_composed_candidate_golden_quality_adjudication", source)
        self.assertIn('os.environ["HF_HUB_OFFLINE"] = "1"', source)
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn("manual_visual_quality_review\"", source)
        self.assertNotIn("publication_ready = True", source)
        self.assertNotIn("human_visual_review_approved = True", source)


if __name__ == "__main__":
    unittest.main()
