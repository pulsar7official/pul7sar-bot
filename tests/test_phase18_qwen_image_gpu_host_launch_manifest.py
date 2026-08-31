from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_gpu_host_launch_manifest import (
    build_gpu_host_launch_manifest,
    verify_gpu_host_launch_manifest,
)


class QwenImageGpuHostLaunchManifestTests(unittest.TestCase):
    def _fixture(self, root: Path):
        for relative in (
            "engine/intelligence/approved_model_revisions.py",
            "engine/intelligence/qwen_image_gpu_readiness.py",
            "engine/intelligence/qwen_image_local_inference_runtime.py",
            "engine/intelligence/qwen_image_one_shot_canonical_inference.py",
            "engine/intelligence/qwen_image_local_inference_provenance.py",
            "tools/phase18_run_one_shot_canonical_inference.py",
        ):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(relative + "\n", encoding="utf-8")
        auth = root / "runs/auth.json"
        auth.parent.mkdir(parents=True)
        auth.write_text('{"auth":true}\n', encoding="utf-8")
        cs257 = root / "runs/cs257"
        cs257.mkdir()
        (cs257 / "story.json").write_text('{"story":true}\n', encoding="utf-8")
        (cs257 / "semantic.json").write_text('{"semantic":true}\n', encoding="utf-8")
        snapshot = root / "cache/snapshots" / QWEN_IMAGE_2512_REVISION
        snapshot.mkdir(parents=True)
        verified = {
            "story_snapshot_sha256": "a" * 64,
            "inference_executed": False,
            "genuine_canonical_inference_executed": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        prompt = SimpleNamespace(
            story_snapshot_sha256="a" * 64,
            contract={"prompt_sha256": "b" * 64, "negative_prompt_sha256": "c" * 64},
        )
        return auth, cs257, snapshot, verified, prompt

    def test_build_binds_all_launch_inputs_without_granting_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            auth, cs257, snapshot, verified, prompt = self._fixture(root)
            output = root / "runs/launch.json"
            with patch(
                "engine.intelligence.qwen_image_gpu_host_launch_manifest.verify_story_bound_generation_authorization",
                return_value=verified,
            ), patch(
                "engine.intelligence.qwen_image_gpu_host_launch_manifest.build_story_bound_canonical_prompt",
                return_value=prompt,
            ):
                result = build_gpu_host_launch_manifest(
                    auth, cs257, snapshot, output, repo_root=root,
                    width=1024, height=1024, seed=7, num_inference_steps=8, guidance_scale=1.0,
                )
            self.assertTrue(output.is_file())
            self.assertTrue(result["launch_manifest_verified"])
            self.assertFalse(result["network_allowed"])
            self.assertTrue(result["local_files_only"])
            self.assertFalse(result["model_load_attempted"])
            self.assertFalse(result["genuine_canonical_inference_executed"])
            self.assertFalse(result["genuine_golden_png_created"])
            self.assertFalse(result["publication_ready"])
            self.assertEqual(len(result["cs257_evidence"]["files"]), 2)
            self.assertEqual(len(result["execution_contract_sources"]), 6)

    def test_build_rejects_cross_story_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            auth, cs257, snapshot, verified, prompt = self._fixture(root)
            prompt.story_snapshot_sha256 = "d" * 64
            with patch(
                "engine.intelligence.qwen_image_gpu_host_launch_manifest.verify_story_bound_generation_authorization",
                return_value=verified,
            ), patch(
                "engine.intelligence.qwen_image_gpu_host_launch_manifest.build_story_bound_canonical_prompt",
                return_value=prompt,
            ):
                with self.assertRaisesRegex(ValueError, "CROSS_STORY"):
                    build_gpu_host_launch_manifest(
                        auth, cs257, snapshot, root / "runs/launch.json", repo_root=root,
                        width=1024, height=1024, seed=7, num_inference_steps=8, guidance_scale=1.0,
                    )

    def test_build_rejects_inference_settings_outside_measured_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            auth, cs257, snapshot, verified, prompt = self._fixture(root)
            with patch(
                "engine.intelligence.qwen_image_gpu_host_launch_manifest.verify_story_bound_generation_authorization",
                return_value=verified,
            ), patch(
                "engine.intelligence.qwen_image_gpu_host_launch_manifest.build_story_bound_canonical_prompt",
                return_value=prompt,
            ):
                with self.assertRaisesRegex(ValueError, "STEPS_OUTSIDE_MEASURED_ENVELOPE"):
                    build_gpu_host_launch_manifest(
                        auth, cs257, snapshot, root / "runs/launch.json", repo_root=root,
                        width=1024, height=1024, seed=7, num_inference_steps=9, guidance_scale=1.0,
                    )

    def test_verify_detects_cs257_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            auth, cs257, snapshot, verified, prompt = self._fixture(root)
            output = root / "runs/launch.json"
            with patch(
                "engine.intelligence.qwen_image_gpu_host_launch_manifest.verify_story_bound_generation_authorization",
                return_value=verified,
            ), patch(
                "engine.intelligence.qwen_image_gpu_host_launch_manifest.build_story_bound_canonical_prompt",
                return_value=prompt,
            ):
                build_gpu_host_launch_manifest(
                    auth, cs257, snapshot, output, repo_root=root,
                    width=1024, height=1024, seed=7, num_inference_steps=8, guidance_scale=1.0,
                )
                (cs257 / "story.json").write_text('{"story":"changed"}\n', encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "CS257_BYTE_DRIFT"):
                    verify_gpu_host_launch_manifest(output, repo_root=root)

    def test_verify_rejects_manifest_tampering_before_replay(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            auth, cs257, snapshot, verified, prompt = self._fixture(root)
            output = root / "runs/launch.json"
            with patch(
                "engine.intelligence.qwen_image_gpu_host_launch_manifest.verify_story_bound_generation_authorization",
                return_value=verified,
            ), patch(
                "engine.intelligence.qwen_image_gpu_host_launch_manifest.build_story_bound_canonical_prompt",
                return_value=prompt,
            ):
                build_gpu_host_launch_manifest(
                    auth, cs257, snapshot, output, repo_root=root,
                    width=1024, height=1024, seed=7, num_inference_steps=8, guidance_scale=1.0,
                )
            payload = json.loads(output.read_text(encoding="utf-8"))
            payload["network_allowed"] = True
            output.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DIGEST_MISMATCH"):
                verify_gpu_host_launch_manifest(output, repo_root=root)


if __name__ == "__main__":
    unittest.main()
