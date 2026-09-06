from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import engine.intelligence.qwen_image_semantic_publication_gate_to_genuine_golden_materialization as subject


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


class SemanticPublicationGateToGenuineGoldenMaterializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.story = "a" * 64
        (self.root / "artifacts").mkdir()
        self.composed_path = self.root / "artifacts/composed.png"
        self.composed_path.write_bytes(b"PNG")
        self.png = _binding(self.root, self.composed_path)
        self.cs348_path = self.root / "cs348.json"
        self.cs348_path.write_text("{}", encoding="utf-8")
        self.cs284_path = self.root / "cs284.json"
        self.cs284_path.write_text("{}", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _cs348(self, *, allowed: bool = True) -> dict[str, object]:
        return {
            "schema": subject.CS348_SCHEMA,
            "status": subject.CS348_STATUS,
            "receipt_sha256": "8" * 64,
            "story_snapshot_sha256": self.story,
            "candidate_png": {"sha256": "d" * 64},
            "composed_candidate_png": self.png,
            "cs284_receipt": _binding(self.root, self.cs284_path, "4" * 64),
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_execution_requested": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": allowed,
            "semantic_publication_failures": [] if allowed else ["rejected"],
            "genuine_golden_png_created": False,
            "publication_ready": False,
            "authoritative": False,
        }

    def _cs284(self, *, allowed: bool = True) -> dict[str, object]:
        return {
            "schema": subject.CS284_SCHEMA,
            "status": subject.CS284_STATUS,
            "receipt_sha256": "4" * 64,
            "story_snapshot_sha256": self.story,
            "composed_candidate_png": self.png,
            "generation_context": {"device": "cuda", "offline": True},
            "weighted_score": 97.0,
            "quality_tier": "golden",
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_execution_requested": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": allowed,
            "semantic_publication_failures": [] if allowed else ["rejected"],
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _cs285(self) -> dict[str, object]:
        golden_path = self.root / "out/cs285/genuine_golden_visual.png"
        return {
            "schema": subject.CS285_SCHEMA,
            "status": subject.CS285_STATUS,
            "receipt_sha256": "5" * 64,
            "story_snapshot_sha256": self.story,
            "source_composed_candidate_png": self.png,
            "genuine_golden_visual_png": _binding(self.root, golden_path),
            "generation_context": {"device": "cuda", "offline": True},
            "weighted_score": 97.0,
            "quality_tier": "golden",
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "byte_identity_preserved": True,
            "genuine_golden_png_created": True,
            "publication_ready": False,
        }

    def test_allowed_exact_cs348_materializes_once_through_existing_cs285(self) -> None:
        cs348, cs284 = self._cs348(), self._cs284()
        calls = {"cs285": 0}

        def materialize(given284: Path, output: Path, *, repo_root: Path) -> Path:
            calls["cs285"] += 1
            self.assertEqual(given284, self.cs284_path)
            output.mkdir()
            golden = output / "genuine_golden_visual.png"
            golden.write_bytes(self.composed_path.read_bytes())
            receipt = output / "genuine_golden_materialization.json"
            receipt.write_text("{}", encoding="utf-8")
            return receipt

        with (
            mock.patch.object(subject, "verify_semantic_publication_request_to_gate_execution", return_value=cs348),
            mock.patch.object(subject, "verify_semantic_publication_execution", return_value=cs284),
            mock.patch.object(subject, "materialize_genuine_golden_visual", side_effect=materialize),
            mock.patch.object(subject, "verify_genuine_golden_materialization", side_effect=lambda *args, **kwargs: self._cs285()),
        ):
            run = subject.continue_semantic_publication_gate_to_genuine_golden_materialization(
                self.cs348_path, self.root / "out", repo_root=self.root
            )
            receipt = subject.verify_semantic_publication_gate_to_genuine_golden_materialization(
                run.receipt_path, repo_root=self.root
            )
        self.assertEqual(calls["cs285"], 1)
        self.assertTrue(receipt["genuine_golden_png_created"])
        self.assertTrue(receipt["byte_identity_preserved"])
        self.assertFalse(receipt["publication_ready"])
        self.assertFalse(receipt["authoritative"])
        self.assertEqual(run.genuine_golden_visual_path.read_bytes(), self.composed_path.read_bytes())

    def test_rejected_cs348_cannot_reach_cs285(self) -> None:
        cs348 = self._cs348(allowed=False)
        with (
            mock.patch.object(subject, "verify_semantic_publication_request_to_gate_execution", return_value=cs348),
            mock.patch.object(subject, "materialize_genuine_golden_visual") as materialize,
        ):
            with self.assertRaisesRegex(ValueError, "semantic_publication_allowed"):
                subject.continue_semantic_publication_gate_to_genuine_golden_materialization(
                    self.cs348_path, self.root / "out", repo_root=self.root
                )
        materialize.assert_not_called()

    def test_cs284_receipt_hash_drift_is_rejected_before_cs285(self) -> None:
        cs348, cs284 = self._cs348(), self._cs284()
        cs348["cs284_receipt"]["receipt_sha256"] = "f" * 64  # type: ignore[index]
        with (
            mock.patch.object(subject, "verify_semantic_publication_request_to_gate_execution", return_value=cs348),
            mock.patch.object(subject, "verify_semantic_publication_execution", return_value=cs284),
            mock.patch.object(subject, "materialize_genuine_golden_visual") as materialize,
        ):
            with self.assertRaisesRegex(ValueError, "CS284_RECEIPT_DRIFT"):
                subject.continue_semantic_publication_gate_to_genuine_golden_materialization(
                    self.cs348_path, self.root / "out", repo_root=self.root
                )
        materialize.assert_not_called()

    def test_cs285_byte_identity_drift_is_rejected(self) -> None:
        cs348, cs284 = self._cs348(), self._cs284()

        def materialize(given284: Path, output: Path, *, repo_root: Path) -> Path:
            output.mkdir()
            (output / "genuine_golden_visual.png").write_bytes(self.composed_path.read_bytes())
            receipt = output / "genuine_golden_materialization.json"
            receipt.write_text("{}", encoding="utf-8")
            return receipt

        def bad_cs285(*args: object, **kwargs: object) -> dict[str, object]:
            value = self._cs285()
            value["genuine_golden_visual_png"] = {
                "repository_relative_path": "out/cs285/genuine_golden_visual.png",
                "sha256": "f" * 64,
                "byte_size": 3,
            }
            return value

        with (
            mock.patch.object(subject, "verify_semantic_publication_request_to_gate_execution", return_value=cs348),
            mock.patch.object(subject, "verify_semantic_publication_execution", return_value=cs284),
            mock.patch.object(subject, "materialize_genuine_golden_visual", side_effect=materialize),
            mock.patch.object(subject, "verify_genuine_golden_materialization", side_effect=bad_cs285),
        ):
            with self.assertRaisesRegex(ValueError, "BYTE_IDENTITY_DRIFT"):
                subject.continue_semantic_publication_gate_to_genuine_golden_materialization(
                    self.cs348_path, self.root / "out", repo_root=self.root
                )

    def test_source_contains_no_generation_network_or_publication_shortcut(self) -> None:
        source = Path(subject.__file__).read_text(encoding="utf-8")
        self.assertNotIn("from_pretrained(", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("httpx.", source)
        self.assertNotIn("execute_semantic_publication_gate", source)
        self.assertNotIn("upload", source.lower())
        self.assertNotIn("publish(", source.lower())
        self.assertNotIn('"publication_ready": True', source)
        self.assertNotIn('"authoritative": True', source)


if __name__ == "__main__":
    unittest.main()
