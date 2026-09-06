from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import engine.intelligence.qwen_image_genuine_golden_materialization_to_publication_readiness as subject


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


class GenuineGoldenMaterializationToPublicationReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.story = "a" * 64
        (self.root / "artifacts").mkdir()
        self.composed_path = self.root / "artifacts/composed.png"
        self.composed_path.write_bytes(b"PNG")
        self.composed = _binding(self.root, self.composed_path)

        self.golden_path = self.root / "golden/genuine_golden_visual.png"
        self.golden_path.parent.mkdir()
        self.golden_path.write_bytes(self.composed_path.read_bytes())
        self.golden = _binding(self.root, self.golden_path)

        self.cs349_path = self.root / "cs349.json"
        self.cs349_path.write_text("{}", encoding="utf-8")
        self.cs285_path = self.root / "cs285.json"
        self.cs285_path.write_text("{}", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _cs349(self, *, publication_ready: bool = False) -> dict[str, object]:
        return {
            "schema": subject.CS349_SCHEMA,
            "status": subject.CS349_STATUS,
            "receipt_sha256": "9" * 64,
            "story_snapshot_sha256": self.story,
            "candidate_png": {"sha256": "d" * 64},
            "composed_candidate_png": self.composed,
            "cs285_receipt": _binding(self.root, self.cs285_path, "5" * 64),
            "genuine_golden_visual_png": self.golden,
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "byte_identity_preserved": True,
            "genuine_golden_png_created": True,
            "publication_ready": publication_ready,
            "authoritative": False,
        }

    def _cs285(self) -> dict[str, object]:
        return {
            "schema": subject.CS285_SCHEMA,
            "status": subject.CS285_STATUS,
            "receipt_sha256": "5" * 64,
            "story_snapshot_sha256": self.story,
            "source_composed_candidate_png": self.composed,
            "genuine_golden_visual_png": self.golden,
            "png_dimensions": {"width": 1080, "height": 1350},
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

    def _cs286(self, receipt_path: Path) -> dict[str, object]:
        return {
            "schema": subject.CS286_SCHEMA,
            "status": subject.CS286_STATUS,
            "receipt_sha256": "6" * 64,
            "story_snapshot_sha256": self.story,
            "source_cs285_genuine_golden_materialization": _binding(self.root, self.cs285_path, "5" * 64),
            "source_composed_candidate_png": self.composed,
            "genuine_golden_visual_png": self.golden,
            "png_dimensions": {"width": 1080, "height": 1350},
            "generation_context": {"device": "cuda", "offline": True},
            "weighted_score": 97.0,
            "quality_tier": "golden",
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "byte_identity_preserved": True,
            "genuine_golden_png_created": True,
            "publication_ready": True,
        }

    def test_exact_cs349_finalizes_once_through_existing_cs286(self) -> None:
        cs349, cs285 = self._cs349(), self._cs285()
        calls = {"cs286": 0}
        last_receipt: dict[str, Path] = {}

        def finalize(given285: Path, output: Path, *, repo_root: Path) -> Path:
            calls["cs286"] += 1
            self.assertEqual(given285, self.cs285_path)
            output.mkdir()
            receipt = output / "genuine_golden_publication_readiness.json"
            receipt.write_text("{}", encoding="utf-8")
            last_receipt["path"] = receipt
            return receipt

        def verify286(path: Path, *, repo_root: Path) -> dict[str, object]:
            return self._cs286(path)

        with (
            mock.patch.object(subject, "verify_semantic_publication_gate_to_genuine_golden_materialization", return_value=cs349),
            mock.patch.object(subject, "verify_genuine_golden_materialization", return_value=cs285),
            mock.patch.object(subject, "finalize_genuine_golden_publication_readiness", side_effect=finalize),
            mock.patch.object(subject, "verify_genuine_golden_publication_readiness", side_effect=verify286),
        ):
            run = subject.continue_genuine_golden_materialization_to_publication_readiness(
                self.cs349_path, self.root / "out", repo_root=self.root
            )
            receipt = subject.verify_genuine_golden_materialization_to_publication_readiness(
                run.receipt_path, repo_root=self.root
            )

        self.assertEqual(calls["cs286"], 1)
        self.assertTrue(receipt["publication_ready"])
        self.assertTrue(receipt["genuine_golden_png_created"])
        self.assertTrue(receipt["byte_identity_preserved"])
        self.assertFalse(receipt["authoritative"])
        self.assertEqual(run.genuine_golden_visual_path.read_bytes(), self.composed_path.read_bytes())
        self.assertEqual(run.cs286_receipt_path, last_receipt["path"])

    def test_premature_cs349_publication_readiness_cannot_reach_cs286(self) -> None:
        cs349 = self._cs349(publication_ready=True)
        with (
            mock.patch.object(subject, "verify_semantic_publication_gate_to_genuine_golden_materialization", return_value=cs349),
            mock.patch.object(subject, "finalize_genuine_golden_publication_readiness") as finalize,
        ):
            with self.assertRaisesRegex(ValueError, "PREMATURE_PUBLICATION_AUTHORITY"):
                subject.continue_genuine_golden_materialization_to_publication_readiness(
                    self.cs349_path, self.root / "out", repo_root=self.root
                )
        finalize.assert_not_called()

    def test_cs285_receipt_hash_drift_is_rejected_before_cs286(self) -> None:
        cs349, cs285 = self._cs349(), self._cs285()
        cs349["cs285_receipt"]["receipt_sha256"] = "f" * 64  # type: ignore[index]
        with (
            mock.patch.object(subject, "verify_semantic_publication_gate_to_genuine_golden_materialization", return_value=cs349),
            mock.patch.object(subject, "verify_genuine_golden_materialization", return_value=cs285),
            mock.patch.object(subject, "finalize_genuine_golden_publication_readiness") as finalize,
        ):
            with self.assertRaisesRegex(ValueError, "CS285_RECEIPT_DRIFT"):
                subject.continue_genuine_golden_materialization_to_publication_readiness(
                    self.cs349_path, self.root / "out", repo_root=self.root
                )
        finalize.assert_not_called()

    def test_cs286_golden_binding_drift_is_rejected(self) -> None:
        cs349, cs285 = self._cs349(), self._cs285()

        def finalize(given285: Path, output: Path, *, repo_root: Path) -> Path:
            output.mkdir()
            receipt = output / "genuine_golden_publication_readiness.json"
            receipt.write_text("{}", encoding="utf-8")
            return receipt

        def bad286(path: Path, *, repo_root: Path) -> dict[str, object]:
            value = self._cs286(path)
            value["genuine_golden_visual_png"] = {
                "repository_relative_path": self.golden_path.relative_to(self.root).as_posix(),
                "sha256": "f" * 64,
                "byte_size": 3,
            }
            return value

        with (
            mock.patch.object(subject, "verify_semantic_publication_gate_to_genuine_golden_materialization", return_value=cs349),
            mock.patch.object(subject, "verify_genuine_golden_materialization", return_value=cs285),
            mock.patch.object(subject, "finalize_genuine_golden_publication_readiness", side_effect=finalize),
            mock.patch.object(subject, "verify_genuine_golden_publication_readiness", side_effect=bad286),
        ):
            with self.assertRaisesRegex(ValueError, "CS286_STATE_DRIFT:genuine_golden_visual_png"):
                subject.continue_genuine_golden_materialization_to_publication_readiness(
                    self.cs349_path, self.root / "out", repo_root=self.root
                )

    def test_source_contains_no_generation_network_or_publish_side_effect(self) -> None:
        source = Path(subject.__file__).read_text(encoding="utf-8")
        self.assertNotIn("from_pretrained(", source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("httpx.", source)
        self.assertNotIn("materialize_genuine_golden_visual", source)
        self.assertNotIn("execute_semantic_publication_gate", source)
        self.assertNotIn("upload(", source.lower())
        self.assertNotIn("publish(", source.lower())
        self.assertNotIn('"authoritative": True', source)


if __name__ == "__main__":
    unittest.main()
