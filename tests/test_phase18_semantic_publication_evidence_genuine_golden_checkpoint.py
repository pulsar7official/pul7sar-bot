from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution import (
    SCHEMA as CS284_SCHEMA,
)
from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution_request import (
    SCHEMA as CS283_SCHEMA,
)
from engine.intelligence.qwen_image_genuine_golden_materialization import (
    SCHEMA as CS285_SCHEMA,
)
from tools.phase18_continue_semantic_publication_evidence_to_genuine_golden import (
    SCHEMA,
    STATUS,
    continue_semantic_publication_evidence_to_genuine_golden,
)

ROOT = Path(__file__).resolve().parents[1]
MODULE = "tools.phase18_continue_semantic_publication_evidence_to_genuine_golden"
STORY = "a" * 64


class SemanticPublicationEvidenceGenuineGoldenCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.root = Path(self.temp.name)
        self.composed = self.root / "composed.png"
        self.composed.write_bytes(b"exact-composed-png-test-bytes")
        self.composed_binding = self._binding(self.composed)

        self.cs283_path = self.root / "cs283.json"
        self.cs283_path.write_text("{}\n", encoding="utf-8")
        self.cs283_binding = self._binding(self.cs283_path)
        self.cs284_path = self.root / "cs284.json"
        self.cs284_path.write_text("{}\n", encoding="utf-8")
        self.cs327_path = self.root / "cs327.json"
        self.output = self.root / "out"
        self.cs327 = {
            "schema": "pul7sar-phase18-composed-approval-semantic-publication-request-checkpoint-v1",
            "status": "SEMANTIC_PUBLICATION_EXECUTION_EVIDENCE_REQUIRED",
            "authoritative": False,
            "story_snapshot_sha256": STORY,
            "candidate_png": {"sha256": "b" * 64},
            "composed_candidate_png": dict(self.composed_binding),
            "cs283_receipt": self.cs283_path.relative_to(ROOT).as_posix(),
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_execution_requested": True,
            "semantic_publication_gate_executed": False,
            "semantic_publication_allowed": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        self._write_checkpoint()

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _binding(path: Path) -> dict[str, object]:
        raw = path.read_bytes()
        return {
            "repository_relative_path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_size": len(raw),
        }

    def _write_checkpoint(self) -> None:
        self.cs327_path.write_text(json.dumps(self.cs327) + "\n", encoding="utf-8")

    def _cs283(self, **updates):
        value = {
            "schema": CS283_SCHEMA,
            "story_snapshot_sha256": STORY,
            "receipt_sha256": "3" * 64,
            "composed_candidate_png": dict(self.composed_binding),
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_execution_requested": True,
            "semantic_publication_gate_executed": False,
            "semantic_publication_allowed": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        value.update(updates)
        return value

    def _cs284(self, **updates):
        source = dict(self.cs283_binding)
        source["receipt_sha256"] = "3" * 64
        value = {
            "schema": CS284_SCHEMA,
            "story_snapshot_sha256": STORY,
            "source_cs283_semantic_publication_request": source,
            "composed_candidate_png": dict(self.composed_binding),
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_execution_requested": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "semantic_publication_failures": [],
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        value.update(updates)
        return value

    def _fake_materializer(self, source: Path, output_dir: Path, *, repo_root: Path) -> Path:
        del source, repo_root
        output_dir.mkdir()
        golden = output_dir / "genuine_golden_visual.png"
        golden.write_bytes(self.composed.read_bytes())
        receipt = output_dir / "genuine_golden_materialization.json"
        receipt.write_text("{}\n", encoding="utf-8")
        return receipt

    def _cs285(self, **updates):
        golden = self.output / "cs285" / "genuine_golden_visual.png"
        value = {
            "schema": CS285_SCHEMA,
            "story_snapshot_sha256": STORY,
            "source_composed_candidate_png": dict(self.composed_binding),
            "genuine_golden_visual_png": self._binding(golden),
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "byte_identity_preserved": True,
            "genuine_golden_png_created": True,
            "publication_ready": False,
        }
        value.update(updates)
        return value

    def test_happy_path_materializes_exact_bytes_and_stops_before_cs286(self) -> None:
        with (
            patch(f"{MODULE}.verify_semantic_publication_execution_request", return_value=self._cs283()),
            patch(f"{MODULE}.verify_semantic_publication_execution", return_value=self._cs284()),
            patch(f"{MODULE}.materialize_genuine_golden_visual", side_effect=self._fake_materializer) as materialize,
            patch(f"{MODULE}.verify_genuine_golden_materialization", side_effect=lambda *a, **k: self._cs285()),
        ):
            path = continue_semantic_publication_evidence_to_genuine_golden(
                self.cs327_path, self.cs284_path, self.output, repo_root=ROOT
            )

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], SCHEMA)
        self.assertEqual(payload["status"], STATUS)
        self.assertFalse(payload["authoritative"])
        self.assertTrue(payload["semantic_publication_gate_executed"])
        self.assertTrue(payload["semantic_publication_allowed"])
        self.assertTrue(payload["byte_identity_preserved"])
        self.assertTrue(payload["genuine_golden_png_created"])
        self.assertFalse(payload["publication_ready"])
        self.assertEqual(
            payload["source_composed_candidate_png"]["sha256"],
            payload["genuine_golden_visual_png"]["sha256"],
        )
        self.assertTrue(payload["policy"]["cs286_publication_readiness_not_executed"])
        materialize.assert_called_once()

    def test_semantic_publication_rejection_cannot_create_cs285(self) -> None:
        with (
            patch(f"{MODULE}.verify_semantic_publication_execution_request", return_value=self._cs283()),
            patch(
                f"{MODULE}.verify_semantic_publication_execution",
                return_value=self._cs284(
                    semantic_publication_allowed=False,
                    semantic_publication_failures=["semantic_mismatch"],
                ),
            ),
            patch(f"{MODULE}.materialize_genuine_golden_visual") as materialize,
        ):
            with self.assertRaisesRegex(ValueError, "SEMANTIC_PUBLICATION_REJECTED"):
                continue_semantic_publication_evidence_to_genuine_golden(
                    self.cs327_path, self.cs284_path, self.output, repo_root=ROOT
                )
        materialize.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_rejects_cs284_from_different_cs283_even_if_gate_allowed(self) -> None:
        wrong_source = dict(self.cs283_binding)
        wrong_source["sha256"] = "0" * 64
        wrong_source["receipt_sha256"] = "3" * 64
        with (
            patch(f"{MODULE}.verify_semantic_publication_execution_request", return_value=self._cs283()),
            patch(
                f"{MODULE}.verify_semantic_publication_execution",
                return_value=self._cs284(source_cs283_semantic_publication_request=wrong_source),
            ),
            patch(f"{MODULE}.materialize_genuine_golden_visual") as materialize,
        ):
            with self.assertRaisesRegex(ValueError, "CS284_NOT_BOUND_TO_EXACT_CS283:sha256"):
                continue_semantic_publication_evidence_to_genuine_golden(
                    self.cs327_path, self.cs284_path, self.output, repo_root=ROOT
                )
        materialize.assert_not_called()

    def test_rejects_cross_story_cs284(self) -> None:
        with (
            patch(f"{MODULE}.verify_semantic_publication_execution_request", return_value=self._cs283()),
            patch(
                f"{MODULE}.verify_semantic_publication_execution",
                return_value=self._cs284(story_snapshot_sha256="c" * 64),
            ),
            patch(f"{MODULE}.materialize_genuine_golden_visual") as materialize,
        ):
            with self.assertRaisesRegex(ValueError, "CS284_CROSS_STORY"):
                continue_semantic_publication_evidence_to_genuine_golden(
                    self.cs327_path, self.cs284_path, self.output, repo_root=ROOT
                )
        materialize.assert_not_called()

    def test_rejects_composed_png_byte_drift_before_golden(self) -> None:
        drifted = dict(self.composed_binding)
        drifted["sha256"] = "d" * 64
        with (
            patch(f"{MODULE}.verify_semantic_publication_execution_request", return_value=self._cs283()),
            patch(
                f"{MODULE}.verify_semantic_publication_execution",
                return_value=self._cs284(composed_candidate_png=drifted),
            ),
            patch(f"{MODULE}.materialize_genuine_golden_visual") as materialize,
        ):
            with self.assertRaisesRegex(ValueError, "CS284_COMPOSED_BYTES_DRIFT:sha256"):
                continue_semantic_publication_evidence_to_genuine_golden(
                    self.cs327_path, self.cs284_path, self.output, repo_root=ROOT
                )
        materialize.assert_not_called()

    def test_orchestrator_has_no_cs284_execution_generation_or_cs286_shortcut(self) -> None:
        source = (ROOT / "tools/phase18_continue_semantic_publication_evidence_to_genuine_golden.py").read_text(encoding="utf-8")
        self.assertNotIn("execute_semantic_publication_gate(", source)
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn("finalize_genuine_golden_publication_readiness(", source)
        self.assertNotIn("publication_ready\": True", source)


if __name__ == "__main__":
    unittest.main()
