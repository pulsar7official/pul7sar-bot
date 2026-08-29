from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_live_host_identity_recheck import (
    LIVE_HOST_IDENTITY_RECHECK_SCHEMA,
    build_live_host_identity_recheck,
)
from engine.intelligence.qwen_image_story_bound_controlled_trial_request import (
    STORY_BOUND_CONTROLLED_TRIAL_REQUEST_SCHEMA,
)


class LiveHostIdentityRecheckTests(unittest.TestCase):
    STORY_SHA = "a" * 64
    EXPECTED = {
        "gpu_name": "Fixture GPU",
        "gpu_total_vram_gb": 23.99,
        "torch_version": "2.fixture",
        "cuda_version": "12.fixture",
        "diffusers_version": "0.fixture",
        "pipeline_class": "QwenImagePipeline",
        "dtype": "bfloat16",
        "offload_mode": "sequential_cpu",
        "native_bf16": True,
    }

    def _write(self, path: Path, payload: dict) -> bytes:
        raw = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return raw

    def _inputs(self, root: Path) -> tuple[Path, dict]:
        preflight = {
            "schema": CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_SCHEMA,
            "status": "QWEN_IMAGE_2512_CONTROLLED_GOLDEN_TRIAL_PREFLIGHT_CONTRACT_LOCKED",
            "model_id": QWEN_IMAGE_2512_MODEL_ID,
            "model_revision": QWEN_IMAGE_2512_REVISION,
            "cost_mode": COST_MODE,
            "expected_runtime_identity": dict(self.EXPECTED),
            "expected_runtime_fingerprint_sha256": sha256_json({"runtime_identity": self.EXPECTED}),
            "live_same_host_recheck_required": True,
            "controlled_trial_preflight_valid": False,
            "live_host_recheck_passed": False,
            "canonical_generation_authorized": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        preflight["preflight_contract_sha256"] = sha256_json(preflight)
        preflight_path = root / "contracts" / "preflight.json"
        preflight_raw = self._write(preflight_path, preflight)

        request = {
            "schema": STORY_BOUND_CONTROLLED_TRIAL_REQUEST_SCHEMA,
            "status": "QWEN_IMAGE_2512_STORY_BOUND_CONTROLLED_TRIAL_REQUEST_LOCKED",
            "story_snapshot_sha256": self.STORY_SHA,
            "cost_mode": COST_MODE,
            "source_preflight_contract": {
                "repository_relative_path": preflight_path.relative_to(root).as_posix(),
                "sha256": hashlib.sha256(preflight_raw).hexdigest(),
                "byte_size": len(preflight_raw),
                "preflight_contract_sha256": preflight["preflight_contract_sha256"],
            },
            "production_semantic_replay_executed": True,
            "fresh_story_gates_passed": True,
            "live_same_host_recheck_required": True,
            "live_host_recheck_passed": False,
            "controlled_trial_preflight_valid": False,
            "canonical_generation_authorized": False,
            "model_weights_loaded": False,
            "inference_executed": False,
            "genuine_canonical_inference_executed": False,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        request["request_sha256"] = sha256_json(request)
        request_path = root / "artifacts" / "cs258" / "story_bound_controlled_trial_request.json"
        self._write(request_path, request)
        observation = {
            key: self.EXPECTED[key]
            for key in (
                "gpu_name",
                "gpu_total_vram_gb",
                "torch_version",
                "cuda_version",
                "diffusers_version",
                "native_bf16",
            )
        }
        return request_path, observation

    def test_exact_observable_identity_passes_without_opening_generation_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request, observation = self._inputs(root)
            result = build_live_host_identity_recheck(
                request, observation, root / "artifacts" / "cs259", repo_root=root
            )
            payload = json.loads(result.receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], LIVE_HOST_IDENTITY_RECHECK_SCHEMA)
            self.assertEqual(payload["story_snapshot_sha256"], self.STORY_SHA)
            self.assertTrue(payload["live_observable_host_identity_matched"])
            self.assertTrue(payload["pipeline_load_recheck_required"])
            self.assertTrue(payload["offload_execution_recheck_required"])
            for field in (
                "live_host_recheck_passed",
                "controlled_trial_preflight_valid",
                "canonical_generation_authorized",
                "model_weights_loaded",
                "inference_executed",
                "genuine_canonical_inference_executed",
                "genuine_golden_png_created",
                "semantic_approved",
                "human_visual_review_approved",
                "golden_quality_approved",
                "publication_ready",
            ):
                self.assertFalse(payload[field])
            claimed = payload["receipt_sha256"]
            unsigned = dict(payload)
            unsigned.pop("receipt_sha256")
            self.assertEqual(claimed, sha256_json(unsigned))

    def test_gpu_identity_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request, observation = self._inputs(root)
            observation["gpu_name"] = "Different GPU"
            with self.assertRaisesRegex(ValueError, "RUNTIME_IDENTITY_DRIFT:gpu_name"):
                build_live_host_identity_recheck(
                    request, observation, root / "artifacts" / "cs259", repo_root=root
                )
            self.assertFalse((root / "artifacts" / "cs259").exists())

    def test_native_bf16_false_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request, observation = self._inputs(root)
            observation["native_bf16"] = False
            with self.assertRaisesRegex(ValueError, "NATIVE_BF16_UNPROVEN"):
                build_live_host_identity_recheck(
                    request, observation, root / "artifacts" / "cs259", repo_root=root
                )

    def test_preflight_byte_tamper_after_request_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request, observation = self._inputs(root)
            preflight = root / "contracts" / "preflight.json"
            preflight.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "PREFLIGHT_BYTE_DRIFT"):
                build_live_host_identity_recheck(
                    request, observation, root / "artifacts" / "cs259", repo_root=root
                )

    def test_request_authority_drift_fails_closed_even_with_rehashed_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request, observation = self._inputs(root)
            payload = json.loads(request.read_text(encoding="utf-8"))
            payload["canonical_generation_authorized"] = True
            payload.pop("request_sha256")
            payload["request_sha256"] = sha256_json(payload)
            self._write(request, payload)
            with self.assertRaisesRegex(ValueError, "REQUEST_AUTHORITY_DRIFT"):
                build_live_host_identity_recheck(
                    request, observation, root / "artifacts" / "cs259", repo_root=root
                )

    def test_preflight_parent_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            root = workspace / "repo"
            root.mkdir()
            request, observation = self._inputs(root)
            outside = workspace / "outside-preflight.json"
            original = root / "contracts" / "preflight.json"
            outside.write_bytes(original.read_bytes())

            payload = json.loads(request.read_text(encoding="utf-8"))
            raw = outside.read_bytes()
            payload["source_preflight_contract"] = {
                "repository_relative_path": "../outside-preflight.json",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "byte_size": len(raw),
                "preflight_contract_sha256": json.loads(raw.decode("utf-8"))[
                    "preflight_contract_sha256"
                ],
            }
            payload.pop("request_sha256")
            payload["request_sha256"] = sha256_json(payload)
            self._write(request, payload)
            with self.assertRaisesRegex(ValueError, "PREFLIGHT_OUTSIDE_REPOSITORY"):
                build_live_host_identity_recheck(
                    request, observation, root / "artifacts" / "cs259", repo_root=root
                )

    def test_symlinked_request_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request, observation = self._inputs(root)
            alias = root / "request-link.json"
            alias.symlink_to(request)
            with self.assertRaisesRegex(ValueError, "REQUEST_OUTSIDE_REPOSITORY"):
                build_live_host_identity_recheck(
                    alias, observation, root / "artifacts" / "cs259", repo_root=root
                )


if __name__ == "__main__":
    unittest.main()
