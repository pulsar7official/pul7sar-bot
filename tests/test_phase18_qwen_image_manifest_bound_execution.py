from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_manifest_bound_execution import (
    build_manifest_bound_execution_argv,
    execute_manifest_bound_inference,
)


class QwenImageManifestBoundExecutionTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, dict]:
        tool = root / "tools/phase18_run_one_shot_canonical_inference.py"
        tool.parent.mkdir(parents=True)
        tool.write_text("print('canonical')\n", encoding="utf-8")
        auth = root / "runs/auth.json"
        auth.parent.mkdir(parents=True)
        auth.write_text("{}\n", encoding="utf-8")
        cs257 = root / "runs/cs257"
        cs257.mkdir()
        snapshot = root / "cache/snapshots/revision"
        snapshot.mkdir(parents=True)
        manifest_path = root / "runs/launch.json"
        manifest_path.write_text("{}\n", encoding="utf-8")
        manifest = {
            "authorization": {"repository_relative_path": "runs/auth.json"},
            "cs257_evidence": {"repository_relative_directory": "runs/cs257"},
            "snapshot": {"resolved_path": str(snapshot)},
            "inference_settings": {
                "width": 1024,
                "height": 1024,
                "seed": 17,
                "num_inference_steps": 8,
                "guidance_scale": 1.0,
            },
        }
        return manifest_path, manifest

    def test_argv_is_derived_from_manifest_without_operator_settings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, manifest = self._fixture(root)
            with patch.dict(os.environ, {"PUL7SAR_PHASE18_COST_MODE": "$0-local"}, clear=False), patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.verify_gpu_host_launch_manifest",
                return_value=manifest,
            ):
                argv = build_manifest_bound_execution_argv(
                    manifest_path,
                    root / "runs/output",
                    repo_root=root,
                    python_executable="python-test",
                )
            self.assertEqual(argv[0], "python-test")
            self.assertIn("--authorization", argv)
            self.assertIn(str((root / "runs/auth.json").resolve()), argv)
            self.assertIn("--cs257-run-dir", argv)
            self.assertIn(str((root / "runs/cs257").resolve()), argv)
            self.assertIn("--seed", argv)
            self.assertEqual(argv[argv.index("--seed") + 1], "17")
            self.assertEqual(argv[argv.index("--steps") + 1], "8")
            self.assertEqual(argv[argv.index("--guidance-scale") + 1], "1.0")

    def test_zero_cost_mode_is_mandatory_before_execution_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, manifest = self._fixture(root)
            with patch.dict(os.environ, {"PUL7SAR_PHASE18_COST_MODE": ""}, clear=False), patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.verify_gpu_host_launch_manifest",
                return_value=manifest,
            ):
                with self.assertRaisesRegex(ValueError, "ZERO_COST_MODE_NOT_LOCKED"):
                    build_manifest_bound_execution_argv(
                        manifest_path, root / "runs/output", repo_root=root
                    )

    def test_output_must_be_new_and_repository_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, manifest = self._fixture(root)
            existing = root / "runs/existing"
            existing.mkdir()
            with patch.dict(os.environ, {"PUL7SAR_PHASE18_COST_MODE": "$0-local"}, clear=False), patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.verify_gpu_host_launch_manifest",
                return_value=manifest,
            ):
                with self.assertRaisesRegex(ValueError, "OUTPUT_ALREADY_EXISTS"):
                    build_manifest_bound_execution_argv(
                        manifest_path, existing, repo_root=root
                    )
                with self.assertRaisesRegex(ValueError, "OUTPUT_OUTSIDE_REPOSITORY"):
                    build_manifest_bound_execution_argv(
                        manifest_path, root.parent / "outside-output", repo_root=root
                    )

    def test_executor_uses_shell_free_subprocess_and_propagates_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, manifest = self._fixture(root)
            completed = type("Completed", (), {"returncode": 23})()
            with patch.dict(os.environ, {"PUL7SAR_PHASE18_COST_MODE": "$0-local"}, clear=False), patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.verify_gpu_host_launch_manifest",
                return_value=manifest,
            ), patch(
                "subprocess.run", return_value=completed
            ) as run:
                code = execute_manifest_bound_inference(
                    manifest_path,
                    root / "runs/output",
                    repo_root=root,
                    python_executable="python-test",
                )
            self.assertEqual(code, 23)
            self.assertFalse(run.call_args.kwargs.get("shell", False))
            self.assertFalse(run.call_args.kwargs["check"])


if __name__ == "__main__":
    unittest.main()
