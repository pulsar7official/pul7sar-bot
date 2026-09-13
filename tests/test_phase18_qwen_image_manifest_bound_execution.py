from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_manifest_bound_execution import (
    OFFLINE_CHILD_ENVIRONMENT,
    QwenPreloadHostNotReadyError,
    SUCCESS_OUTPUT_FILES,
    build_manifest_bound_execution_argv,
    build_offline_subprocess_environment,
    execute_manifest_bound_inference,
    require_preload_host_ready,
    verify_successful_canonical_output,
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

    @staticmethod
    def _ready_preload_report() -> dict:
        return {
            "blockers": [],
            "ready_for_model_load_attempt": True,
            "model_load_attempted": False,
            "inference_executed": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    @staticmethod
    def _verified_postflight() -> dict:
        return {
            "genuine_canonical_inference_executed": True,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    @staticmethod
    def _materialize_success_bundle(output: Path) -> None:
        output.mkdir()
        for filename in SUCCESS_OUTPUT_FILES:
            (output / filename).write_bytes(b"test-evidence")

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

    def test_offline_child_environment_forces_library_offline_flags(self) -> None:
        environment = build_offline_subprocess_environment(
            {
                "PUL7SAR_PHASE18_COST_MODE": "$0-local",
                "HF_HUB_OFFLINE": "0",
                "TRANSFORMERS_OFFLINE": "0",
                "KEEP_ME": "yes",
            }
        )
        self.assertEqual(environment["PUL7SAR_PHASE18_COST_MODE"], "$0-local")
        self.assertEqual(environment["HF_HUB_OFFLINE"], "1")
        self.assertEqual(environment["TRANSFORMERS_OFFLINE"], "1")
        self.assertEqual(environment["KEEP_ME"], "yes")
        self.assertEqual(
            {key: environment[key] for key in OFFLINE_CHILD_ENVIRONMENT},
            OFFLINE_CHILD_ENVIRONMENT,
        )

    def test_offline_child_environment_rejects_unlocked_cost_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "ZERO_COST_MODE_NOT_LOCKED"):
            build_offline_subprocess_environment(
                {"PUL7SAR_PHASE18_COST_MODE": "paid-or-networked"}
            )

    def test_preload_gate_surfaces_all_blockers_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, _ = self._fixture(root)
            report = self._ready_preload_report()
            report["ready_for_model_load_attempt"] = False
            report["blockers"] = [
                "identity_drift:torch_version",
                "cuda_unavailable",
                "identity_drift:torch_version",
            ]
            with patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.inspect_preload_host",
                return_value=report,
            ):
                with self.assertRaises(QwenPreloadHostNotReadyError) as ctx:
                    require_preload_host_ready(manifest_path, repo_root=root)
            self.assertEqual(
                ctx.exception.blockers,
                ("cuda_unavailable", "identity_drift:torch_version"),
            )

    def test_preload_gate_rejects_any_premature_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, _ = self._fixture(root)
            report = self._ready_preload_report()
            report["semantic_approved"] = True
            with patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.inspect_preload_host",
                return_value=report,
            ):
                with self.assertRaisesRegex(ValueError, "DIAGNOSTIC_AUTHORITY_INVALID"):
                    require_preload_host_ready(manifest_path, repo_root=root)

    def test_success_postflight_requires_all_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "runs/output"
            output.mkdir(parents=True)
            for filename in SUCCESS_OUTPUT_FILES[:-1]:
                (output / filename).write_bytes(b"evidence")
            with self.assertRaisesRegex(ValueError, "POSTFLIGHT_FILE_MISSING:launch_to_output_attestation.json"):
                verify_successful_canonical_output(output, repo_root=root)

    def test_success_postflight_replays_launch_to_output_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "runs/output"
            output.parent.mkdir(parents=True)
            self._materialize_success_bundle(output)
            verified = self._verified_postflight()
            with patch(
                "engine.intelligence.qwen_image_launch_to_output_attestation.verify_launch_to_output_attestation",
                return_value=verified,
            ) as replay:
                result = verify_successful_canonical_output(output, repo_root=root)
            self.assertEqual(result, verified)
            replay.assert_called_once_with(
                output / "launch_to_output_attestation.json",
                repo_root=root.resolve(),
            )

    def test_success_postflight_rejects_premature_downstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "runs/output"
            output.parent.mkdir(parents=True)
            self._materialize_success_bundle(output)
            verified = self._verified_postflight()
            verified["golden_quality_approved"] = True
            with patch(
                "engine.intelligence.qwen_image_launch_to_output_attestation.verify_launch_to_output_attestation",
                return_value=verified,
            ):
                with self.assertRaisesRegex(ValueError, "POSTFLIGHT_AUTHORITY_INVALID"):
                    verify_successful_canonical_output(output, repo_root=root)

    def test_executor_does_not_start_subprocess_when_preload_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, manifest = self._fixture(root)
            blocked = self._ready_preload_report()
            blocked["ready_for_model_load_attempt"] = False
            blocked["blockers"] = ["cuda_unavailable", "native_bf16_unavailable"]
            with patch.dict(os.environ, {"PUL7SAR_PHASE18_COST_MODE": "$0-local"}, clear=False), patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.verify_gpu_host_launch_manifest",
                return_value=manifest,
            ), patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.inspect_preload_host",
                return_value=blocked,
            ), patch("subprocess.run") as run:
                with self.assertRaises(QwenPreloadHostNotReadyError):
                    execute_manifest_bound_inference(
                        manifest_path,
                        root / "runs/output",
                        repo_root=root,
                        python_executable="python-test",
                    )
            run.assert_not_called()

    def test_executor_propagates_nonzero_exit_without_postflight_replay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, manifest = self._fixture(root)
            completed = type("Completed", (), {"returncode": 23})()
            with patch.dict(
                os.environ,
                {"PUL7SAR_PHASE18_COST_MODE": "$0-local"},
                clear=False,
            ), patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.verify_gpu_host_launch_manifest",
                return_value=manifest,
            ), patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.inspect_preload_host",
                return_value=self._ready_preload_report(),
            ), patch(
                "subprocess.run", return_value=completed
            ), patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.verify_successful_canonical_output"
            ) as replay:
                code = execute_manifest_bound_inference(
                    manifest_path,
                    root / "runs/output",
                    repo_root=root,
                    python_executable="python-test",
                )
            self.assertEqual(code, 23)
            replay.assert_not_called()

    def test_executor_uses_shell_free_offline_subprocess_and_requires_postflight_after_zero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path, manifest = self._fixture(root)
            completed = type("Completed", (), {"returncode": 0})()
            output = root / "runs/output"
            with patch.dict(
                os.environ,
                {
                    "PUL7SAR_PHASE18_COST_MODE": "$0-local",
                    "HF_HUB_OFFLINE": "0",
                    "TRANSFORMERS_OFFLINE": "0",
                },
                clear=False,
            ), patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.verify_gpu_host_launch_manifest",
                return_value=manifest,
            ), patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.inspect_preload_host",
                return_value=self._ready_preload_report(),
            ), patch(
                "subprocess.run", return_value=completed
            ) as run, patch(
                "engine.intelligence.qwen_image_manifest_bound_execution.verify_successful_canonical_output",
                return_value=self._verified_postflight(),
            ) as replay:
                code = execute_manifest_bound_inference(
                    manifest_path,
                    output,
                    repo_root=root,
                    python_executable="python-test",
                )
            self.assertEqual(code, 0)
            self.assertFalse(run.call_args.kwargs.get("shell", False))
            self.assertFalse(run.call_args.kwargs["check"])
            child_environment = run.call_args.kwargs["env"]
            self.assertEqual(child_environment["PUL7SAR_PHASE18_COST_MODE"], "$0-local")
            self.assertEqual(child_environment["HF_HUB_OFFLINE"], "1")
            self.assertEqual(child_environment["TRANSFORMERS_OFFLINE"], "1")
            replay.assert_called_once_with(output, repo_root=root)


if __name__ == "__main__":
    unittest.main()
