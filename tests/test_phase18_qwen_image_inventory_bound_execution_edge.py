from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import call, patch

from engine.intelligence.qwen_image_inventory_bound_launch_manifest import (
    verify_inventory_bound_gpu_host_launch_manifest_for_execution,
)


class QwenImageInventoryBoundExecutionEdgeTests(unittest.TestCase):
    def test_execution_edge_requires_byte_replay_before_concrete_invocation_replay(self) -> None:
        root = Path("/repo")
        manifest = {"manifest_sha256": "a" * 64, "snapshot_byte_inventory": {"snapshot_inventory_sha256": "b" * 64}}
        order: list[str] = []

        def byte_verify(*args, **kwargs):
            order.append("bytes")
            return manifest

        def execution_verify(*args, **kwargs):
            order.append("execution")
            return manifest

        with patch(
            "engine.intelligence.qwen_image_inventory_bound_launch_manifest.verify_inventory_bound_gpu_host_launch_manifest",
            side_effect=byte_verify,
        ) as byte_mock, patch(
            "engine.intelligence.qwen_image_inventory_bound_launch_manifest.verify_gpu_host_launch_manifest_for_execution",
            side_effect=execution_verify,
        ) as execution_mock:
            result = verify_inventory_bound_gpu_host_launch_manifest_for_execution(
                root / "launch.json",
                authorization_path=root / "auth.json",
                cs257_run_dir=root / "cs257",
                snapshot_path=root / "snapshot",
                repo_root=root,
                width=1024,
                height=1024,
                seed=7,
                num_inference_steps=8,
                guidance_scale=1.0,
            )

        self.assertEqual(order, ["bytes", "execution"])
        self.assertEqual(result, manifest)
        byte_mock.assert_called_once_with(root / "launch.json", repo_root=root)
        execution_mock.assert_called_once()

    def test_snapshot_byte_drift_stops_before_concrete_invocation_replay(self) -> None:
        root = Path("/repo")
        with patch(
            "engine.intelligence.qwen_image_inventory_bound_launch_manifest.verify_inventory_bound_gpu_host_launch_manifest",
            side_effect=ValueError("QWEN_INVENTORY_BOUND_MANIFEST_SNAPSHOT_BYTE_DRIFT"),
        ), patch(
            "engine.intelligence.qwen_image_inventory_bound_launch_manifest.verify_gpu_host_launch_manifest_for_execution",
        ) as execution_mock:
            with self.assertRaisesRegex(ValueError, "SNAPSHOT_BYTE_DRIFT"):
                verify_inventory_bound_gpu_host_launch_manifest_for_execution(
                    root / "launch.json",
                    authorization_path=root / "auth.json",
                    cs257_run_dir=root / "cs257",
                    snapshot_path=root / "snapshot",
                    repo_root=root,
                    width=1024,
                    height=1024,
                    seed=7,
                    num_inference_steps=8,
                    guidance_scale=1.0,
                )
        execution_mock.assert_not_called()

    def test_replay_mismatch_fails_closed(self) -> None:
        root = Path("/repo")
        byte_bound = {"manifest_sha256": "a" * 64, "snapshot_byte_inventory": {"snapshot_inventory_sha256": "b" * 64}}
        invocation_bound = {"manifest_sha256": "c" * 64, "snapshot_byte_inventory": {"snapshot_inventory_sha256": "b" * 64}}
        with patch(
            "engine.intelligence.qwen_image_inventory_bound_launch_manifest.verify_inventory_bound_gpu_host_launch_manifest",
            return_value=byte_bound,
        ), patch(
            "engine.intelligence.qwen_image_inventory_bound_launch_manifest.verify_gpu_host_launch_manifest_for_execution",
            return_value=invocation_bound,
        ):
            with self.assertRaisesRegex(ValueError, "EXECUTION_REPLAY_DRIFT"):
                verify_inventory_bound_gpu_host_launch_manifest_for_execution(
                    root / "launch.json",
                    authorization_path=root / "auth.json",
                    cs257_run_dir=root / "cs257",
                    snapshot_path=root / "snapshot",
                    repo_root=root,
                    width=1024,
                    height=1024,
                    seed=7,
                    num_inference_steps=8,
                    guidance_scale=1.0,
                )

    def test_canonical_child_imports_inventory_bound_execution_verifier(self) -> None:
        source = Path("tools/phase18_run_one_shot_canonical_inference.py").read_text(encoding="utf-8")
        self.assertIn("qwen_image_inventory_bound_launch_manifest", source)
        self.assertIn("verify_inventory_bound_gpu_host_launch_manifest_for_execution", source)
        self.assertNotIn(
            "from engine.intelligence.qwen_image_gpu_host_launch_manifest import (\n        verify_gpu_host_launch_manifest_for_execution",
            source,
        )
        self.assertIn("local_files_only", source)
        self.assertIn("network_allowed", source)


if __name__ == "__main__":
    unittest.main()
