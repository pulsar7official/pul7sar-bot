from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import engine.intelligence.qwen_image_final_semantic_approval_to_semantic_publication_execution_request as subject


def _binding(root: Path, path: Path, receipt_sha: str | None = None) -> dict[str, object]:
    raw = path.read_bytes()
    value: dict[str, object] = {
        "repository_relative_path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }
    if receipt_sha is not None:
        value["receipt_sha256"] = receipt_sha
    return value


class FinalSemanticApprovalToSemanticPublicationRequestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.story = "a" * 64
        (self.root / "artifacts").mkdir()
        (self.root / "artifacts/composed.png").write_bytes(b"PNG")
        self.png = {
            "repository_relative_path": "artifacts/composed.png",
            "sha256": hashlib.sha256(b"PNG").hexdigest(),
            "byte_size": 3,
        }
        self.cs346_path = self.root / "cs346.json"
        self.cs346_path.write_text("{}", encoding="utf-8")
        self.cs282_path = self.root / "cs282.json"
        self.cs282_path.write_text("{}", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _cs346(self) -> dict[str, object]:
        return {
            "schema": subject.CS346_SCHEMA,
            "status": subject.CS346_STATUS,
            "receipt_sha256": "1" * 64,
            "story_snapshot_sha256": self.story,
            "candidate_png": {"sha256": "d" * 64},
            "composed_candidate_png": self.png,
            "snapshot_byte_inventory_verified": True,
            "snapshot_inventory_sha256": "b" * 64,
            "snapshot_file_count": 17,
            "snapshot_total_bytes": 987654321,
            "model_revision": "approved-qwen-image-revision",
            "cs282_receipt": _binding(self.root, self.cs282_path, "2" * 64),
            "golden_quality_approved": True,
            "human_visual_review_approved": True,
            "final_presentation_review_approved": True,
            "exact_brand_integrity_approved": True,
            "typography_integrity_approved": True,
            "composed_visual_approved": True,
            "semantic_approved": True,
            "genuine_golden_png_created": False,
            "publication_ready": False,
            "authoritative": False,
        }

    def _cs282(self) -> dict[str, object]:
        return {
            "schema": subject.CS282_SCHEMA,
            "receipt_sha256": "2" * 64,
            "story_snapshot_sha256": self.story,
            "composed_candidate_png": self.png,
            "composed_visual_approved": True,
            "semantic_approved": True,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _cs283(self) -> dict[str, object]:
        return {
            "schema": subject.CS283_SCHEMA,
            "receipt_sha256": "3" * 64,
            "story_snapshot_sha256": self.story,
            "composed_candidate_png": self.png,
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_execution_requested": True,
            "semantic_publication_gate_executed": False,
            "semantic_publication_allowed": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _run(self) -> tuple[subject.FinalSemanticApprovalToSemanticPublicationExecutionRequestRun, dict[str, object]]:
        cs346, cs282, cs283 = self._cs346(), self._cs282(), self._cs283()

        def build283(given282: Path, output: Path, *, repo_root: Path) -> Path:
            self.assertEqual(given282, self.cs282_path)
            output.mkdir()
            path = output / "cs283.json"
            path.write_text("{}", encoding="utf-8")
            return path

        with (
            mock.patch.object(subject, "verify_final_composed_visual_approval_to_final_semantic_approval", return_value=cs346),
            mock.patch.object(subject, "verify_composed_candidate_final_semantic_approval", return_value=cs282),
            mock.patch.object(subject, "build_semantic_publication_execution_request", side_effect=build283),
            mock.patch.object(subject, "verify_semantic_publication_execution_request", return_value=cs283),
        ):
            run = subject.continue_final_semantic_approval_to_semantic_publication_execution_request(
                self.cs346_path, self.root / "out", repo_root=self.root
            )
            receipt = subject.verify_final_semantic_approval_to_semantic_publication_execution_request(
                run.receipt_path, repo_root=self.root
            )
        return run, receipt

    def test_exact_cs346_continues_once_to_existing_cs283_request_with_snapshot_lineage(self) -> None:
        cs346, cs282, cs283 = self._cs346(), self._cs282(), self._cs283()
        calls = {"cs283": 0}

        def build283(given282: Path, output: Path, *, repo_root: Path) -> Path:
            calls["cs283"] += 1
            self.assertEqual(given282, self.cs282_path)
            output.mkdir()
            path = output / "cs283.json"
            path.write_text("{}", encoding="utf-8")
            return path

        with (
            mock.patch.object(subject, "verify_final_composed_visual_approval_to_final_semantic_approval", return_value=cs346),
            mock.patch.object(subject, "verify_composed_candidate_final_semantic_approval", return_value=cs282),
            mock.patch.object(subject, "build_semantic_publication_execution_request", side_effect=build283),
            mock.patch.object(subject, "verify_semantic_publication_execution_request", return_value=cs283),
        ):
            run = subject.continue_final_semantic_approval_to_semantic_publication_execution_request(
                self.cs346_path, self.root / "out", repo_root=self.root
            )
            receipt = subject.verify_final_semantic_approval_to_semantic_publication_execution_request(
                run.receipt_path, repo_root=self.root
            )
        self.assertEqual(calls["cs283"], 1)
        for field in subject._SNAPSHOT_FIELDS:
            self.assertEqual(receipt[field], cs346[field])
        self.assertTrue(receipt["semantic_publication_execution_requested"])
        self.assertFalse(receipt["semantic_publication_gate_executed"])
        self.assertFalse(receipt["semantic_publication_allowed"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])
        self.assertFalse(receipt["authoritative"])

    def test_unverified_snapshot_is_rejected_before_cs283_build(self) -> None:
        cs346 = self._cs346()
        cs346["snapshot_byte_inventory_verified"] = False
        with (
            mock.patch.object(subject, "verify_final_composed_visual_approval_to_final_semantic_approval", return_value=cs346),
            mock.patch.object(subject, "build_semantic_publication_execution_request") as build283,
        ):
            with self.assertRaisesRegex(ValueError, "snapshot_byte_inventory_verified"):
                subject.continue_final_semantic_approval_to_semantic_publication_execution_request(
                    self.cs346_path, self.root / "out", repo_root=self.root
                )
        build283.assert_not_called()

    def test_final_semantic_approval_is_required(self) -> None:
        cs346 = self._cs346(); cs346["semantic_approved"] = False
        with mock.patch.object(subject, "verify_final_composed_visual_approval_to_final_semantic_approval", return_value=cs346):
            with self.assertRaisesRegex(ValueError, "semantic_approved"):
                subject.continue_final_semantic_approval_to_semantic_publication_execution_request(
                    self.cs346_path, self.root / "out", repo_root=self.root
                )

    def test_premature_publication_authority_is_rejected(self) -> None:
        cs346 = self._cs346(); cs346["publication_ready"] = True
        with mock.patch.object(subject, "verify_final_composed_visual_approval_to_final_semantic_approval", return_value=cs346):
            with self.assertRaisesRegex(ValueError, "publication_ready"):
                subject.continue_final_semantic_approval_to_semantic_publication_execution_request(
                    self.cs346_path, self.root / "out", repo_root=self.root
                )

    def test_cs282_receipt_hash_drift_is_rejected(self) -> None:
        cs346, cs282 = self._cs346(), self._cs282()
        cs346["cs282_receipt"]["receipt_sha256"] = "f" * 64  # type: ignore[index]
        with (
            mock.patch.object(subject, "verify_final_composed_visual_approval_to_final_semantic_approval", return_value=cs346),
            mock.patch.object(subject, "verify_composed_candidate_final_semantic_approval", return_value=cs282),
        ):
            with self.assertRaisesRegex(ValueError, "CS282_RECEIPT_DRIFT"):
                subject.continue_final_semantic_approval_to_semantic_publication_execution_request(
                    self.cs346_path, self.root / "out", repo_root=self.root
                )

    def test_rehashed_snapshot_digest_tamper_is_rejected_by_fresh_cs346_replay(self) -> None:
        run, _ = self._run()
        receipt = json.loads(run.receipt_path.read_text(encoding="utf-8"))
        receipt["snapshot_inventory_sha256"] = "c" * 64
        unsigned = dict(receipt); unsigned.pop("receipt_sha256")
        receipt["receipt_sha256"] = subject.sha256_json(unsigned)
        run.receipt_path.write_text(json.dumps(receipt, separators=(",", ":")) + "\n", encoding="utf-8")
        with (
            mock.patch.object(subject, "verify_final_composed_visual_approval_to_final_semantic_approval", return_value=self._cs346()),
            mock.patch.object(subject, "verify_composed_candidate_final_semantic_approval", return_value=self._cs282()),
            mock.patch.object(subject, "verify_semantic_publication_execution_request", return_value=self._cs283()),
        ):
            with self.assertRaisesRegex(ValueError, "snapshot_inventory_sha256"):
                subject.verify_final_semantic_approval_to_semantic_publication_execution_request(run.receipt_path, repo_root=self.root)

    def test_source_contains_no_gate_execution_generation_or_publish_shortcut(self) -> None:
        source = Path(subject.__file__).read_text(encoding="utf-8")
        self.assertNotIn("execute_semantic_publication_gate(", source)
        self.assertNotIn("SemanticPublicationGate()", source)
        self.assertNotIn("from_pretrained(", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("httpx.", source)
        self.assertNotIn("upload", source.lower())
        self.assertNotIn("publish(", source.lower())
        self.assertNotIn("genuine_golden_png_created\": True", source)
        self.assertNotIn("publication_ready\": True", source)
        self.assertNotIn("authoritative\": True", source)


if __name__ == "__main__":
    unittest.main()
