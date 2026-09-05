from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

import tools.phase18_execute_bound_composition_and_admit as checkpoint


class BoundCompositionExecutionAndAdmissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path.cwd().resolve()

    def _runner(self, root: Path, *, name: str = "compose_visual") -> Path:
        path = root / "renderer.py"
        path.write_text(
            "def " + name + "(preflight, output_path, repo_root):\n"
            "    return None\n",
            encoding="utf-8",
        )
        return path

    def test_exact_repository_runner_loads_named_top_level_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            runner = self._runner(root)
            _, compose_fn = checkpoint._load_exact_runner(
                self.repo_root, runner, "compose_visual"
            )
            self.assertTrue(callable(compose_fn))
            self.assertEqual(compose_fn.__name__, "compose_visual")
            self.assertEqual(Path(compose_fn.__code__.co_filename).resolve(), runner.resolve())

    def test_missing_runner_entrypoint_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            runner = self._runner(Path(td))
            with self.assertRaisesRegex(
                ValueError, "QWEN_BOUND_COMPOSITION_RUNNER_ENTRYPOINT_MISSING"
            ):
                checkpoint._load_exact_runner(
                    self.repo_root, runner, "other_entrypoint"
                )

    def test_runner_outside_repository_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            runner = self._runner(Path(td))
            with self.assertRaisesRegex(
                ValueError, "QWEN_BOUND_COMPOSITION_RUNNER_SOURCE_INVALID"
            ):
                checkpoint._load_exact_runner(
                    self.repo_root, runner, "compose_visual"
                )

    def test_cs271_exact_output_flows_directly_into_cs272_without_authority_escalation(self) -> None:
        with tempfile.TemporaryDirectory(dir=self.repo_root) as td:
            root = Path(td)
            runner = self._runner(root)
            cs270 = root / "cs270.json"
            cs270.write_text("{}\n", encoding="utf-8")
            output_dir = root / "run"

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
            cs271_receipt = output_dir / "cs271" / "one_shot.json"
            cs272_receipt = output_dir / "cs272" / "admission.json"
            cs271_payload = {
                "schema": checkpoint.CS271_SCHEMA,
                "story_snapshot_sha256": story_sha,
                "runner_id": "pul7sar-renderer-v1",
                "runner_entrypoint": "compose_visual",
                "candidate_png": candidate,
                "composed_candidate_png": composed,
                "composition_executed": True,
                **downstream_false,
            }
            cs272_payload = {
                "schema": checkpoint.CS272_SCHEMA,
                "story_snapshot_sha256": story_sha,
                "source_candidate_png": candidate,
                "composed_candidate_png": composed,
                "composition_executed": True,
                "composed_candidate_bytes_admitted_for_post_composition_qa": True,
                **downstream_false,
            }

            def fake_execute(*args, **kwargs):
                cs271_receipt.parent.mkdir(parents=True)
                cs271_receipt.write_text("{}\n", encoding="utf-8")
                self.assertEqual(kwargs["runner_source_path"].resolve(), runner.resolve())
                self.assertEqual(kwargs["compose_fn"].__name__, "compose_visual")
                return SimpleNamespace(receipt_path=cs271_receipt)

            def fake_admit(source_path, admission_dir, *, repo_root):
                self.assertEqual(source_path, cs271_receipt)
                self.assertEqual(admission_dir, output_dir / "cs272")
                cs272_receipt.parent.mkdir(parents=True)
                cs272_receipt.write_text("{}\n", encoding="utf-8")
                return SimpleNamespace(receipt_path=cs272_receipt)

            with (
                mock.patch.object(checkpoint, "execute_one_shot_composition", side_effect=fake_execute),
                mock.patch.object(checkpoint, "verify_one_shot_composition_execution", return_value=cs271_payload),
                mock.patch.object(checkpoint, "admit_composed_candidate_bytes", side_effect=fake_admit),
                mock.patch.object(checkpoint, "verify_composed_candidate_byte_admission", return_value=cs272_payload),
            ):
                checkpoint_path = checkpoint.execute_bound_composition_and_admit(
                    cs270,
                    runner,
                    "compose_visual",
                    "pul7sar-renderer-v1",
                    output_dir,
                    repo_root=self.repo_root,
                )

            payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            self.assertTrue(payload["composition_executed"])
            self.assertTrue(
                payload["composed_candidate_bytes_admitted_for_post_composition_qa"]
            )
            for field in checkpoint._DOWNSTREAM_FALSE:
                self.assertIs(payload[field], False)
            self.assertFalse(payload["authoritative"])
            self.assertEqual(payload["candidate_png"], candidate)
            self.assertEqual(payload["composed_candidate_png"], composed)

    def test_cs272_lineage_drift_fails_closed(self) -> None:
        source = Path("tools/phase18_execute_bound_composition_and_admit.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("QWEN_BOUND_COMPOSITION_CROSS_STORY", source)
        self.assertIn("QWEN_BOUND_COMPOSITION_SOURCE_CANDIDATE_DRIFT", source)
        self.assertIn("QWEN_BOUND_COMPOSITION_COMPOSED_BYTES_DRIFT", source)
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn("publication_ready = True", source)


if __name__ == "__main__":
    unittest.main()
