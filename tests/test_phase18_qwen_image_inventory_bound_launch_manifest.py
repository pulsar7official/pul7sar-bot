from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_gpu_readiness import SCHEMA as GPU_READINESS_SCHEMA
from engine.intelligence.qwen_image_inventory_bound_launch_manifest import (
    build_inventory_bound_gpu_host_launch_manifest,
    verify_inventory_bound_gpu_host_launch_manifest,
)
from engine.intelligence.qwen_image_snapshot_inventory import build_qwen_image_snapshot_inventory


class QwenImageInventoryBoundLaunchManifestTests(unittest.TestCase):
    def _snapshot(self, root: Path) -> Path:
        snapshot = root / "cache/models--Qwen--Qwen-Image-2512/snapshots" / QWEN_IMAGE_2512_REVISION
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

    def _readiness(self, root: Path, snapshot: Path, *, ready: bool = True) -> Path:
        path = root / "runs/static-readiness.json"
        payload = {
            "schema": GPU_READINESS_SCHEMA,
            "model_id": "Qwen/Qwen-Image-2512",
            "model_revision": QWEN_IMAGE_2512_REVISION,
            "torch_version": "2.x+cu",
            "torch_cuda_version": "12.x",
            "cuda_available": ready,
            "cuda_device_count": 1 if ready else 0,
            "bf16_supported": ready,
            "cuda_bf16_smoke_test_passed": ready,
            "gpu_name": "Synthetic CUDA GPU" if ready else None,
            "gpu_memory_gib_observed": 24.0 if ready else None,
            "nvidia_smi_available": ready,
            "qwen_image_pipeline_importable": ready,
            "sequential_cpu_offload_supported": ready,
            "snapshot_path": str(snapshot.resolve()),
            "snapshot_revision_verified": ready,
            "snapshot_structure_verified": ready,
            "snapshot_component_count": 2,
            "network_required": False,
            "zero_cost_local_only": True,
            "static_preflight_passed": ready,
            "ready_for_model_load_attempt": ready,
            "genuine_inference_executed": False,
            "ready_for_genuine_inference_claim": False,
            "blockers": [] if ready else ["cuda_unavailable"],
        }
        path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        return path

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

    @staticmethod
    def _binding(path: Path, root: Path) -> dict:
        raw = path.read_bytes()
        return {
            "repository_relative_path": path.resolve().relative_to(root.resolve()).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_size": len(raw),
        }

    def test_build_seals_snapshot_inventory_and_exact_readiness_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runs").mkdir()
            snapshot = self._snapshot(root)
            readiness = self._readiness(root, snapshot)
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
                    readiness,
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
            self.assertEqual(result["static_readiness_receipt"], self._binding(readiness, root))
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
            readiness = self._readiness(root, snapshot)
            manifest = root / "runs/launch.json"
            base = self._base_payload(snapshot)
            base["snapshot_byte_inventory"] = build_qwen_image_snapshot_inventory(snapshot).to_dict()
            base["static_readiness_receipt"] = self._binding(readiness, root)
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
            readiness = self._readiness(root, snapshot)
            manifest = root / "runs/launch.json"
            base = self._base_payload(snapshot)
            base["static_readiness_receipt"] = self._binding(readiness, root)
            manifest.write_text(json.dumps(base) + "\n", encoding="utf-8")
            with patch(
                "engine.intelligence.qwen_image_inventory_bound_launch_manifest.verify_gpu_host_launch_manifest",
                return_value=base,
            ):
                with self.assertRaisesRegex(ValueError, "INVENTORY_MISSING"):
                    verify_inventory_bound_gpu_host_launch_manifest(manifest, repo_root=root)

    def test_verify_rejects_readiness_receipt_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runs").mkdir()
            snapshot = self._snapshot(root)
            readiness = self._readiness(root, snapshot)
            manifest = root / "runs/launch.json"
            base = self._base_payload(snapshot)
            base["snapshot_byte_inventory"] = build_qwen_image_snapshot_inventory(snapshot).to_dict()
            base["static_readiness_receipt"] = self._binding(readiness, root)
            base["manifest_sha256"] = "c" * 64
            manifest.write_text(json.dumps(base) + "\n", encoding="utf-8")

            payload = json.loads(readiness.read_text(encoding="utf-8"))
            payload["torch_version"] = "tampered"
            readiness.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
            with patch(
                "engine.intelligence.qwen_image_inventory_bound_launch_manifest.verify_gpu_host_launch_manifest",
                return_value=base,
            ):
                with self.assertRaisesRegex(ValueError, "READINESS_BYTE_DRIFT"):
                    verify_inventory_bound_gpu_host_launch_manifest(manifest, repo_root=root)

    def test_build_rejects_nonready_receipt_before_manifest_materialization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runs").mkdir()
            snapshot = self._snapshot(root)
            readiness = self._readiness(root, snapshot, ready=False)
            output = root / "runs/launch.json"
            base = self._base_payload(snapshot)

            def fake_build(*args, **kwargs):
                temp = Path(args[3])
                payload = dict(base)
                payload["manifest_sha256"] = "d" * 64
                temp.write_text(json.dumps(payload) + "\n", encoding="utf-8")
                return payload

            with patch(
                "engine.intelligence.qwen_image_inventory_bound_launch_manifest.build_gpu_host_launch_manifest",
                side_effect=fake_build,
            ):
                with self.assertRaisesRegex(ValueError, "READINESS_NOT_READY"):
                    build_inventory_bound_gpu_host_launch_manifest(
                        root / "auth.json",
                        root / "cs257",
                        snapshot,
                        readiness,
                        output,
                        repo_root=root,
                        width=1024,
                        height=1024,
                        seed=7,
                        num_inference_steps=8,
                        guidance_scale=1.0,
                    )
            self.assertFalse(output.exists())
            self.assertFalse(output.with_name(output.name + ".cs354-unbound.tmp").exists())


if __name__ == "__main__":
    unittest.main()
