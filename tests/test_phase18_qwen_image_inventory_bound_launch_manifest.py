from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_inventory_bound_launch_manifest import (
    build_inventory_bound_gpu_host_launch_manifest,
    verify_inventory_bound_gpu_host_launch_manifest,
)


class QwenImageInventoryBoundLaunchManifestTests(unittest.TestCase):
    def _snapshot(self, root: Path) -> Path:
        snapshot = root / "cache/model/snapshots" / QWEN_IMAGE_2512_REVISION
        (snapshot / "transformer").mkdir(parents=True)
        (snapshot / "text_encoder").mkdir()
        (snapshot / "model_index.json").write_text(
            json.dumps(
                {
                    "_class_name": "QwenImagePipeline",
                    "transformer": ["diffusers", "Transformer"],
                    "text_encoder": ["transformers", "TextEncoder"],
                }
            ) + "\n",
            encoding="utf-8",
        )
        (snapshot / "transformer/model.bin").write_bytes(b"weights-A")
        (snapshot / "text_encoder/config.json").write_text("{}\n", encoding="utf-8")
        return snapshot

    @staticmethod
    def _base_payload(snapshot: Path) -> dict:
        return {
            "schema": "pul7sar-phase18-qwen-image-2512-gpu-host-launch-manifest-v1",
            "status": "QWEN_IMAGE_2512_GPU_HOST_LAUNCH_MANIFEST_VERIFIED",
            "snapshot": {
                "resolved_path": str(snapshot.resolve()),
                "revision": QWEN_IMAGE_2512_REVISION,
                "revision_verified": True,
            },
            "model_load_attempted": False,
            "inference_executed": False,
            "genuine_canonical_inference_executed": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def test_build_seals_snapshot_inventory_and_removes_unbound_temp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runs").mkdir()
            snapshot = self._snapshot(root)
            output = root / "runs/launch.json"
            base = self._base_payload(snapshot)

            def fake_build(*args, **kwargs):
                temp = Path(args[3])
                payload = dict(base)
                payload["manifest_sha256"] = "a" * 64
                temp.write_text(json.dumps(payload) + "\n", encoding="utf-8")
                return payload

            def fake_verify(path: Path, *, repo_root: Path):
                return json.loads(Path(path).read_text(encoding="utf-8"))

            with patch(
                "engine.intelligence.qwen_image_inventory_bound_launch_manifest.build_gpu_host_launch_manifest",
                side_effect=fake_build,
            ), patch(
                "engine.intelligence.qwen_image_inventory_bound_launch_manifest.verify_gpu_host_launch_manifest",
                side_effect=fake_verify,
            ):
                result = build_inventory_bound_gpu_host_launch_manifest(
                    root / "auth.json",
                    root / "cs257",
                    snapshot,
                    output,
                    repo_root=root,
                    width=1024,
                    height=1024,
                    seed=7,
                    num_inference_steps=8,
                    guidance_scale=1.0,
                )

            inventory = result["snapshot_byte_inventory"]
            self.assertEqual(inventory["model_revision"], QWEN_IMAGE_2512_REVISION)
            self.assertEqual(inventory["snapshot_file_count"], 3)
            self.assertGreater(inventory["snapshot_total_bytes"], 0)
            self.assertEqual(len(inventory["snapshot_inventory_sha256"]), 64)
            self.assertTrue(output.is_file())
            self.assertFalse(output.with_name(output.name + ".cs354-unbound.tmp").exists())
            for field in (
                "inference_executed",
                "genuine_canonical_inference_executed",
                "semantic_approved",
                "human_visual_review_approved",
                "golden_quality_approved",
                "genuine_golden_png_created",
                "publication_ready",
            ):
                self.assertFalse(result[field])

    def test_verify_rejects_snapshot_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runs").mkdir()
            snapshot = self._snapshot(root)
            manifest = root / "runs/launch.json"
            base = self._base_payload(snapshot)

            from engine.intelligence.qwen_image_snapshot_inventory import build_qwen_image_snapshot_inventory
            base["snapshot_byte_inventory"] = build_qwen_image_snapshot_inventory(snapshot).to_dict()
            base["manifest_sha256"] = "b" * 64
            manifest.write_text(json.dumps(base) + "\n", encoding="utf-8")

            (snapshot / "transformer/model.bin").write_bytes(b"weights-B")
            with patch(
                "engine.intelligence.qwen_image_inventory_bound_launch_manifest.verify_gpu_host_launch_manifest",
                return_value=base,
            ):
                with self.assertRaisesRegex(ValueError, "SNAPSHOT_BYTE_DRIFT"):
                    verify_inventory_bound_gpu_host_launch_manifest(manifest, repo_root=root)

    def test_verify_rejects_manifest_without_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runs").mkdir()
            snapshot = self._snapshot(root)
            manifest = root / "runs/launch.json"
            base = self._base_payload(snapshot)
            manifest.write_text(json.dumps(base) + "\n", encoding="utf-8")
            with patch(
                "engine.intelligence.qwen_image_inventory_bound_launch_manifest.verify_gpu_host_launch_manifest",
                return_value=base,
            ):
                with self.assertRaisesRegex(ValueError, "INVENTORY_MISSING"):
                    verify_inventory_bound_gpu_host_launch_manifest(manifest, repo_root=root)


if __name__ == "__main__":
    unittest.main()
