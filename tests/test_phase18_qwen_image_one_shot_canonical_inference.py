from __future__ import annotations

import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_live_pipeline_load_recheck import (
    LIVE_PIPELINE_LOAD_RECHECK_SCHEMA,
)
from engine.intelligence.qwen_image_one_shot_canonical_inference import (
    CanonicalInferenceImage,
    execute_one_shot_canonical_inference,
    verify_one_shot_canonical_inference,
)
from engine.intelligence.qwen_image_story_bound_generation_authorization import (
    build_story_bound_generation_authorization,
)


def _png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return (
            struct.pack(">I", len(data))
            + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
        )

    rows = b"".join(b"\x00" + b"\x00\x00\x00" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


class OneShotCanonicalInferenceTests(unittest.TestCase):
    STORY_SHA = "c" * 64
    RUNTIME_SHA = "d" * 64

    def _write_cs260(self, root: Path) -> Path:
        payload = {
            "schema": LIVE_PIPELINE_LOAD_RECHECK_SCHEMA,
            "status": "QWEN_IMAGE_2512_LIVE_PIPELINE_LOAD_RECHECK_PASSED",
            "story_snapshot_sha256": self.STORY_SHA,
            "model_id": QWEN_IMAGE_2512_MODEL_ID,
            "model_revision": QWEN_IMAGE_2512_REVISION,
            "cost_mode": COST_MODE,
            "expected_runtime_fingerprint_sha256": self.RUNTIME_SHA,
            "production_semantic_replay_executed": True,
            "fresh_story_gates_passed": True,
            "live_observable_host_identity_matched": True,
            "model_weights_loaded": True,
            "sequential_cpu_offload_enabled": True,
            "live_host_recheck_passed": True,
            "controlled_trial_preflight_valid": True,
            "canonical_generation_authorized": False,
            "inference_executed": False,
            "genuine_canonical_inference_executed": False,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        payload["receipt_sha256"] = sha256_json(payload)
        path = root / "artifacts" / "cs260" / "live_pipeline_load_recheck.json"
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8"
        )
        return path

    def _authorization(self, root: Path) -> Path:
        cs260 = self._write_cs260(root)
        run = build_story_bound_generation_authorization(
            cs260, root / "artifacts" / "cs261", repo_root=root
        )
        return run.receipt_path

    def _run(self, root: Path, authorization: Path, callback, output_name: str = "cs262"):
        return execute_one_shot_canonical_inference(
            authorization,
            root / "artifacts" / output_name,
            repo_root=root,
            prompt="Source-bound neutral sports editorial visual.",
            negative_prompt="mockery, humiliation, invented identity",
            width=16,
            height=16,
            seed=7,
            num_inference_steps=4,
            guidance_scale=1.0,
            observed_runtime_fingerprint_sha256=self.RUNTIME_SHA,
            inference_callable=callback,
        )

    def test_success_executes_exactly_once_and_keeps_downstream_gates_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization = self._authorization(root)
            calls = []

            def inference() -> CanonicalInferenceImage:
                calls.append(1)
                return CanonicalInferenceImage(_png(16, 16), 16, 16)

            run = self._run(root, authorization, inference)
            self.assertEqual(len(calls), 1)
            payload = verify_one_shot_canonical_inference(
                run.receipt_path, repo_root=root
            )
            self.assertEqual(payload["num_inference_steps"], 4)
            self.assertEqual(payload["guidance_scale"], 1.0)
            self.assertTrue(payload["inference_executed"])
            self.assertTrue(payload["genuine_canonical_inference_executed"])
            self.assertFalse(payload["genuine_golden_png_created"])
            for field in (
                "semantic_approved",
                "human_visual_review_approved",
                "golden_quality_approved",
                "publication_ready",
            ):
                self.assertFalse(payload[field])
            self.assertTrue(run.png_path.is_file())
            self.assertTrue(run.consumption_path.is_file())

    def test_runtime_fingerprint_drift_fails_before_consumption_or_inference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization = self._authorization(root)
            calls = []
            with self.assertRaisesRegex(ValueError, "LIVE_RUNTIME_FINGERPRINT_DRIFT"):
                execute_one_shot_canonical_inference(
                    authorization,
                    root / "artifacts" / "cs262",
                    repo_root=root,
                    prompt="neutral visual",
                    negative_prompt="",
                    width=16,
                    height=16,
                    seed=7,
                    num_inference_steps=4,
                    guidance_scale=1.0,
                    observed_runtime_fingerprint_sha256="e" * 64,
                    inference_callable=lambda: calls.append(1),
                )
            self.assertEqual(calls, [])
            self.assertFalse((root / "artifacts" / "cs262").exists())

    def test_measured_envelope_violation_fails_before_claim_and_callback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization = self._authorization(root)
            calls = []
            with self.assertRaisesRegex(ValueError, "WIDTH_OUTSIDE_MEASURED_ENVELOPE"):
                execute_one_shot_canonical_inference(
                    authorization,
                    root / "artifacts" / "too-wide",
                    repo_root=root,
                    prompt="neutral visual",
                    negative_prompt="",
                    width=1025,
                    height=512,
                    seed=7,
                    num_inference_steps=4,
                    guidance_scale=1.0,
                    observed_runtime_fingerprint_sha256=self.RUNTIME_SHA,
                    inference_callable=lambda: calls.append(1),
                )
            with self.assertRaisesRegex(ValueError, "STEPS_OUTSIDE_MEASURED_ENVELOPE"):
                execute_one_shot_canonical_inference(
                    authorization,
                    root / "artifacts" / "too-many-steps",
                    repo_root=root,
                    prompt="neutral visual",
                    negative_prompt="",
                    width=512,
                    height=512,
                    seed=7,
                    num_inference_steps=9,
                    guidance_scale=1.0,
                    observed_runtime_fingerprint_sha256=self.RUNTIME_SHA,
                    inference_callable=lambda: calls.append(1),
                )
            with self.assertRaisesRegex(ValueError, "GUIDANCE_OUTSIDE_MEASURED_CONTRACT"):
                execute_one_shot_canonical_inference(
                    authorization,
                    root / "artifacts" / "guidance-drift",
                    repo_root=root,
                    prompt="neutral visual",
                    negative_prompt="",
                    width=512,
                    height=512,
                    seed=7,
                    num_inference_steps=4,
                    guidance_scale=2.0,
                    observed_runtime_fingerprint_sha256=self.RUNTIME_SHA,
                    inference_callable=lambda: calls.append(1),
                )
            self.assertEqual(calls, [])

    def test_successful_authorization_cannot_be_reused_in_another_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization = self._authorization(root)
            self._run(
                root,
                authorization,
                lambda: CanonicalInferenceImage(_png(16, 16), 16, 16),
            )
            second_calls = []
            with self.assertRaisesRegex(ValueError, "AUTHORIZATION_ALREADY_CONSUMED"):
                self._run(
                    root,
                    authorization,
                    lambda: second_calls.append(1),
                    output_name="cs262-second",
                )
            self.assertEqual(second_calls, [])

    def test_failed_inference_burns_authorization_and_records_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization = self._authorization(root)

            def broken():
                raise RuntimeError("synthetic failure")

            with self.assertRaises(RuntimeError):
                self._run(root, authorization, broken)
            output = root / "artifacts" / "cs262"
            self.assertTrue((output / "canonical_inference_failure.json").is_file())
            self.assertFalse((output / "canonical_candidate.png").exists())

            second_calls = []
            with self.assertRaisesRegex(ValueError, "AUTHORIZATION_ALREADY_CONSUMED"):
                self._run(
                    root,
                    authorization,
                    lambda: second_calls.append(1),
                    output_name="cs262-second",
                )
            self.assertEqual(second_calls, [])

    def test_invalid_png_burns_authorization_and_never_publishes_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization = self._authorization(root)
            with self.assertRaisesRegex(ValueError, "PNG_INVALID"):
                self._run(
                    root,
                    authorization,
                    lambda: CanonicalInferenceImage(b"not-a-png", 16, 16),
                )
            self.assertFalse(
                (root / "artifacts" / "cs262" / "canonical_candidate.png").exists()
            )

    def test_png_byte_tamper_invalidates_success_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization = self._authorization(root)
            run = self._run(
                root,
                authorization,
                lambda: CanonicalInferenceImage(_png(16, 16), 16, 16),
            )
            run.png_path.write_bytes(_png(17, 16))
            with self.assertRaisesRegex(ValueError, "PNG_BYTE_DRIFT"):
                verify_one_shot_canonical_inference(run.receipt_path, repo_root=root)

    def test_consumption_byte_tamper_invalidates_success_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization = self._authorization(root)
            run = self._run(
                root,
                authorization,
                lambda: CanonicalInferenceImage(_png(16, 16), 16, 16),
            )
            claim = json.loads(run.consumption_path.read_text(encoding="utf-8"))
            claim["num_inference_steps"] = 8
            claim["consumption_sha256"] = sha256_json(
                {key: value for key, value in claim.items() if key != "consumption_sha256"}
            )
            run.consumption_path.write_text(
                json.dumps(claim, separators=(",", ":")) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "CONSUMPTION_BYTE_DRIFT"):
                verify_one_shot_canonical_inference(run.receipt_path, repo_root=root)

    def test_authorization_tamper_fails_before_inference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorization = self._authorization(root)
            payload = json.loads(authorization.read_text(encoding="utf-8"))
            payload["publication_ready"] = True
            authorization.write_text(
                json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8"
            )
            calls = []
            with self.assertRaisesRegex(
                ValueError, "DOWNSTREAM_AUTHORITY_DRIFT:publication_ready"
            ):
                self._run(root, authorization, lambda: calls.append(1))
            self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
