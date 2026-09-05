from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import engine.intelligence.qwen_image_semantic_publication_request_to_gate_execution as subject


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


class SemanticPublicationRequestToGateExecutionTests(unittest.TestCase):
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
        self.cs347_path = self.root / "cs347.json"
        self.cs347_path.write_text("{}", encoding="utf-8")
        self.cs283_path = self.root / "cs283.json"
        self.cs283_path.write_text("{}", encoding="utf-8")
        self.evidence_path = self.root / "semantic-publication-evidence.json"
        self.evidence_path.write_text("{}", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _cs347(self) -> dict[str, object]:
        return {
            "schema": subject.CS347_SCHEMA,
            "status": subject.CS347_STATUS,
            "receipt_sha256": "1" * 64,
            "story_snapshot_sha256": self.story,
            "candidate_png": {"sha256": "d" * 64},
            "composed_candidate_png": self.png,
            "cs283_receipt": _binding(self.root, self.cs283_path, "3" * 64),
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_execution_requested": True,
            "semantic_publication_gate_executed": False,
            "semantic_publication_allowed": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
            "authoritative": False,
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

    def _cs284(self, *, allowed: bool = True) -> dict[str, object]:
        cs283_binding = _binding(self.root, self.cs283_path, "3" * 64)
        evidence_binding = _binding(self.root, self.evidence_path)
        return {
            "schema": subject.CS284_SCHEMA,
            "status": subject.CS284_STATUS,
            "receipt_sha256": "4" * 64,
            "story_snapshot_sha256": self.story,
            "source_cs283_semantic_publication_request": cs283_binding,
            "semantic_publication_execution_evidence": evidence_binding,
            "composed_candidate_png": self.png,
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_execution_requested": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": allowed,
            "base_scene_accepted": allowed,
            "semantic_verifier_eligible": True,
            "semantic_publication_failures": [] if allowed else ["semantic evidence rejected"],
            "semantic_publication_warnings": [],
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _run(self, *, allowed: bool) -> dict[str, object]:
        cs347, cs283, cs284 = self._cs347(), self._cs283(), self._cs284(allowed=allowed)
        calls = {"cs284": 0}

        def execute284(given283: Path, evidence: Path, output: Path, *, repo_root: Path) -> Path:
            calls["cs284"] += 1
            self.assertEqual(given283, self.cs283_path)
            self.assertEqual(evidence, self.evidence_path)
            output.mkdir()
            path = output / "semantic_publication_execution.json"
            path.write_text("{}", encoding="utf-8")
            return path

        with (
            mock.patch.object(subject, "verify_final_semantic_approval_to_semantic_publication_execution_request", return_value=cs347),
            mock.patch.object(subject, "verify_semantic_publication_execution_request", return_value=cs283),
            mock.patch.object(subject, "execute_semantic_publication_gate", side_effect=execute284),
            mock.patch.object(subject, "verify_semantic_publication_execution", return_value=cs284),
        ):
            run = subject.continue_semantic_publication_request_to_gate_execution(
                self.cs347_path,
                self.evidence_path,
                self.root / "out",
                repo_root=self.root,
            )
            receipt = subject.verify_semantic_publication_request_to_gate_execution(run.receipt_path, repo_root=self.root)
        self.assertEqual(calls["cs284"], 1)
        return receipt

    def test_exact_cs347_continues_once_to_existing_cs284_and_preserves_allow(self) -> None:
        receipt = self._run(allowed=True)
        self.assertTrue(receipt["semantic_publication_gate_executed"])
        self.assertTrue(receipt["semantic_publication_allowed"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])
        self.assertFalse(receipt["authoritative"])

    def test_gate_rejection_is_preserved_fail_closed(self) -> None:
        receipt = self._run(allowed=False)
        self.assertTrue(receipt["semantic_publication_gate_executed"])
        self.assertFalse(receipt["semantic_publication_allowed"])
        self.assertEqual(receipt["semantic_publication_failures"], ["semantic evidence rejected"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])

    def test_cs347_must_still_be_request_only(self) -> None:
        cs347 = self._cs347()
        cs347["semantic_publication_gate_executed"] = True
        with mock.patch.object(subject, "verify_final_semantic_approval_to_semantic_publication_execution_request", return_value=cs347):
            with self.assertRaisesRegex(ValueError, "semantic_publication_gate_executed"):
                subject.continue_semantic_publication_request_to_gate_execution(
                    self.cs347_path, self.evidence_path, self.root / "out", repo_root=self.root
                )

    def test_cs283_receipt_hash_drift_is_rejected(self) -> None:
        cs347, cs283 = self._cs347(), self._cs283()
        cs347["cs283_receipt"]["receipt_sha256"] = "f" * 64  # type: ignore[index]
        with (
            mock.patch.object(subject, "verify_final_semantic_approval_to_semantic_publication_execution_request", return_value=cs347),
            mock.patch.object(subject, "verify_semantic_publication_execution_request", return_value=cs283),
        ):
            with self.assertRaisesRegex(ValueError, "CS283_RECEIPT_DRIFT"):
                subject.continue_semantic_publication_request_to_gate_execution(
                    self.cs347_path, self.evidence_path, self.root / "out", repo_root=self.root
                )

    def test_source_contains_no_generation_network_or_publication_shortcut(self) -> None:
        source = Path(subject.__file__).read_text(encoding="utf-8")
        self.assertNotIn("from_pretrained(", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("httpx.", source)
        self.assertNotIn("upload", source.lower())
        self.assertNotIn("publish(", source.lower())
        self.assertNotIn('"semantic_publication_allowed": True', source)
        self.assertNotIn('"genuine_golden_png_created": True', source)
        self.assertNotIn('"publication_ready": True', source)
        self.assertNotIn('"authoritative": True', source)


if __name__ == "__main__":
    unittest.main()
