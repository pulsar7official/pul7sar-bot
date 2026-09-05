from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from engine.intelligence.qwen_image_genuine_golden_materialization import SCHEMA as CS285_SCHEMA
from engine.intelligence.qwen_image_genuine_golden_publication_readiness import SCHEMA as CS286_SCHEMA
from tools.phase18_continue_genuine_golden_to_publication_readiness import (
    SCHEMA,
    STATUS,
    continue_genuine_golden_to_publication_readiness,
)

ROOT = Path(__file__).resolve().parents[1]
MODULE = "tools.phase18_continue_genuine_golden_to_publication_readiness"
STORY = "a" * 64


class GenuineGoldenPublicationReadinessCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.root = Path(self.temp.name)
        self.source = self.root / "composed.png"
        self.golden = self.root / "genuine_golden_visual.png"
        raw = b"exact-genuine-golden-test-bytes"
        self.source.write_bytes(raw)
        self.golden.write_bytes(raw)
        self.source_binding = self._binding(self.source)
        self.golden_binding = self._binding(self.golden)
        self.cs285_path = self.root / "cs285.json"
        self.cs285_path.write_text("{}\n", encoding="utf-8")
        self.cs328_path = self.root / "cs328.json"
        self.output = self.root / "out"
        self.cs328 = {
            "schema": "pul7sar-phase18-semantic-publication-evidence-genuine-golden-checkpoint-v1",
            "status": "GENUINE_GOLDEN_VISUAL_MATERIALIZED_AWAITING_PUBLICATION_READINESS",
            "authoritative": False,
            "story_snapshot_sha256": STORY,
            "source_composed_candidate_png": dict(self.source_binding),
            "genuine_golden_visual_png": dict(self.golden_binding),
            "cs285_receipt": self.cs285_path.relative_to(ROOT).as_posix(),
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "byte_identity_preserved": True,
            "genuine_golden_png_created": True,
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
        self.cs328_path.write_text(json.dumps(self.cs328) + "\n", encoding="utf-8")

    def _cs285(self, **updates):
        value = {
            "schema": CS285_SCHEMA,
            "story_snapshot_sha256": STORY,
            "source_composed_candidate_png": dict(self.source_binding),
            "genuine_golden_visual_png": dict(self.golden_binding),
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

    def _fake_finalize(self, source: Path, output_dir: Path, *, repo_root: Path) -> Path:
        del source, repo_root
        output_dir.mkdir()
        receipt = output_dir / "genuine_golden_publication_readiness.json"
        receipt.write_text("{}\n", encoding="utf-8")
        return receipt

    def _cs286(self, **updates):
        value = {
            "schema": CS286_SCHEMA,
            "story_snapshot_sha256": STORY,
            "source_composed_candidate_png": dict(self.source_binding),
            "genuine_golden_visual_png": dict(self.golden_binding),
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "byte_identity_preserved": True,
            "genuine_golden_png_created": True,
            "publication_ready": True,
        }
        value.update(updates)
        return value

    def test_happy_path_executes_exact_cs286_without_publish_side_effect(self) -> None:
        with (
            patch(f"{MODULE}.verify_genuine_golden_materialization", return_value=self._cs285()),
            patch(f"{MODULE}.finalize_genuine_golden_publication_readiness", side_effect=self._fake_finalize) as finalize,
            patch(f"{MODULE}.verify_genuine_golden_publication_readiness", return_value=self._cs286()),
        ):
            path = continue_genuine_golden_to_publication_readiness(
                self.cs328_path, self.output, repo_root=ROOT
            )

        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], SCHEMA)
        self.assertEqual(payload["status"], STATUS)
        self.assertFalse(payload["authoritative"])
        self.assertTrue(payload["genuine_golden_png_created"])
        self.assertTrue(payload["publication_ready"])
        self.assertFalse(payload["publication_side_effect_executed"])
        self.assertEqual(
            payload["source_composed_candidate_png"]["sha256"],
            payload["genuine_golden_visual_png"]["sha256"],
        )
        finalize.assert_called_once_with(self.cs285_path, self.output / "cs286", repo_root=ROOT)

    def test_rejects_cs328_without_genuine_golden_authority_before_cs286(self) -> None:
        self.cs328["genuine_golden_png_created"] = False
        self._write_checkpoint()
        with patch(f"{MODULE}.finalize_genuine_golden_publication_readiness") as finalize:
            with self.assertRaisesRegex(ValueError, "CS328_STATE_DRIFT:genuine_golden_png_created"):
                continue_genuine_golden_to_publication_readiness(
                    self.cs328_path, self.output, repo_root=ROOT
                )
        finalize.assert_not_called()

    def test_rejects_cross_story_cs285_before_cs286(self) -> None:
        with (
            patch(
                f"{MODULE}.verify_genuine_golden_materialization",
                return_value=self._cs285(story_snapshot_sha256="c" * 64),
            ),
            patch(f"{MODULE}.finalize_genuine_golden_publication_readiness") as finalize,
        ):
            with self.assertRaisesRegex(ValueError, "CS285_CROSS_STORY"):
                continue_genuine_golden_to_publication_readiness(
                    self.cs328_path, self.output, repo_root=ROOT
                )
        finalize.assert_not_called()

    def test_rejects_cs285_golden_binding_drift_before_cs286(self) -> None:
        drifted = dict(self.golden_binding)
        drifted["sha256"] = "d" * 64
        with (
            patch(
                f"{MODULE}.verify_genuine_golden_materialization",
                return_value=self._cs285(genuine_golden_visual_png=drifted),
            ),
            patch(f"{MODULE}.finalize_genuine_golden_publication_readiness") as finalize,
        ):
            with self.assertRaisesRegex(ValueError, "CS285_GOLDEN_BYTES_DRIFT:sha256"):
                continue_genuine_golden_to_publication_readiness(
                    self.cs328_path, self.output, repo_root=ROOT
                )
        finalize.assert_not_called()

    def test_rejects_cs286_that_drops_semantic_publication_authority(self) -> None:
        with (
            patch(f"{MODULE}.verify_genuine_golden_materialization", return_value=self._cs285()),
            patch(f"{MODULE}.finalize_genuine_golden_publication_readiness", side_effect=self._fake_finalize),
            patch(
                f"{MODULE}.verify_genuine_golden_publication_readiness",
                return_value=self._cs286(semantic_publication_allowed=False),
            ),
        ):
            with self.assertRaisesRegex(ValueError, "CS286_STATE_DRIFT:semantic_publication_allowed"):
                continue_genuine_golden_to_publication_readiness(
                    self.cs328_path, self.output, repo_root=ROOT
                )

    def test_orchestrator_has_no_generation_pixel_mutation_or_publish_action(self) -> None:
        source = (ROOT / "tools/phase18_continue_genuine_golden_to_publication_readiness.py").read_text(encoding="utf-8")
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn("execute_semantic_publication_gate(", source)
        self.assertNotIn("publish(", source)
        self.assertNotIn("upload(", source)
        self.assertNotIn("save(", source)


if __name__ == "__main__":
    unittest.main()
