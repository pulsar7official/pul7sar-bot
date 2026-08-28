from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION
from engine.intelligence.host_memory_qualification import HostMemoryQualificationReport
from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind
from engine.intelligence.qwen_image_measurement_admission import (
    CANDIDATE_ID,
    DECLARATION_SCHEMA,
    evaluate_measurement_admission,
    verify_declaration,
)


def _sha(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _declaration() -> dict:
    payload = {
        "schema": DECLARATION_SCHEMA,
        "status": "REMOTE_RENDERER_EXPLICIT_LOCAL_MODEL_CANDIDATE_REVISION_PINNED",
        "local_model_candidate_id": CANDIDATE_ID,
        "local_model_id": QWEN_IMAGE_2512_MODEL_ID,
        "local_model_revision": QWEN_IMAGE_2512_REVISION,
        "pinned_model_revision_proven": True,
        "canonical_cost_mode_required": "$0-local",
        "runtime_floor_proven": False,
        "local_runtime_qualified": False,
        "local_generation_authorized": False,
        "canonical_golden_eligible": False,
        "semantic_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    payload["declaration_sha256"] = _sha(payload)
    return payload


def _runtime(*, bf16: bool = True, free_vram: float = 20.0) -> RuntimeHardwareSnapshot:
    return RuntimeHardwareSnapshot(
        kind=RuntimeKind.LOCAL_CUDA,
        cuda_available=True,
        gpu_name="measurement-gpu",
        gpu_vram_gb=24.0,
        torch_available=True,
        metadata={"bf16_supported": bf16, "compute_capability": "8.0", "gpu_free_vram_gb": free_vram},
    )


def _host_memory(*, ready: bool = True, generation_authorized: bool = False) -> HostMemoryQualificationReport:
    return HostMemoryQualificationReport(
        schema="pul7sar-host-memory-qualification-v1",
        ready=ready,
        total_ram_gb=64.0,
        available_ram_gb=40.0 if ready else 4.0,
        used_ram_gb=24.0,
        swap_total_gb=0.0,
        swap_free_gb=0.0,
        minimum_available_ram_gb=10.0,
        measurement_source="fixture",
        reasons=() if ready else ("available_system_ram_below_first_golden_floor",),
        generation_authorized=generation_authorized,
    )


def _complete_snapshot(root: Path, revision: str = QWEN_IMAGE_2512_REVISION) -> Path:
    snapshot = root / "snapshots" / revision
    snapshot.mkdir(parents=True)
    (snapshot / "model_index.json").write_text("{}", encoding="utf-8")
    (snapshot / "weights.safetensors").write_bytes(b"weights")
    return snapshot


class QwenImageMeasurementAdmissionTests(unittest.TestCase):
    def test_declaration_is_sha_bound_and_non_authoritative(self) -> None:
        declaration = _declaration()
        self.assertEqual(verify_declaration(declaration), declaration["declaration_sha256"])
        declaration["local_generation_authorized"] = True
        declaration["declaration_sha256"] = _sha({k: v for k, v in declaration.items() if k != "declaration_sha256"})
        with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
            verify_declaration(declaration)

    def test_measurement_ready_does_not_prove_runtime_floor_or_generation(self) -> None:
        result = evaluate_measurement_admission(
            runtime=_runtime(), host_memory=_host_memory(), diffusers_version="0.test",
            qwen_image_pipeline_available=True, exact_snapshot_path=None, cache_free_gib=80.0,
        )
        self.assertTrue(result.measurement_ready)
        receipt = result.as_receipt(declaration_sha256="a" * 64)
        self.assertFalse(receipt["runtime_floor_proven"])
        self.assertFalse(receipt["local_runtime_qualified"])
        self.assertFalse(receipt["generation_authorized"])
        self.assertFalse(receipt["publication_ready"])

    def test_unknown_runtime_floor_is_not_invented_from_observed_vram(self) -> None:
        result = evaluate_measurement_admission(
            runtime=_runtime(free_vram=23.0), host_memory=_host_memory(), diffusers_version="0.test",
            qwen_image_pipeline_available=True, exact_snapshot_path=None, cache_free_gib=80.0,
        )
        self.assertTrue(result.measurement_ready)
        self.assertNotIn("runtime_floor_proven", result.__dict__)

    def test_bf16_and_live_resource_observability_are_required(self) -> None:
        result = evaluate_measurement_admission(
            runtime=_runtime(bf16=False, free_vram=0.0), host_memory=_host_memory(ready=False), diffusers_version="0.test",
            qwen_image_pipeline_available=True, exact_snapshot_path=None, cache_free_gib=80.0,
        )
        self.assertFalse(result.measurement_ready)
        self.assertIn("native_bf16_not_proven", result.reasons)
        self.assertIn("gpu_live_free_vram_unproven", result.reasons)
        self.assertIn("host_memory_not_ready", result.reasons)

    def test_host_memory_authority_drift_is_rejected(self) -> None:
        result = evaluate_measurement_admission(
            runtime=_runtime(), host_memory=_host_memory(generation_authorized=True), diffusers_version="0.test",
            qwen_image_pipeline_available=True, exact_snapshot_path=None, cache_free_gib=80.0,
        )
        self.assertFalse(result.measurement_ready)
        self.assertIn("host_memory_authority_drift", result.reasons)

    def test_uncached_model_requires_repository_plus_working_headroom(self) -> None:
        result = evaluate_measurement_admission(
            runtime=_runtime(), host_memory=_host_memory(), diffusers_version="0.test",
            qwen_image_pipeline_available=True, exact_snapshot_path=None, cache_free_gib=65.6,
        )
        self.assertFalse(result.measurement_ready)
        self.assertIn("insufficient_cache_disk_for_measurement", result.reasons)
        self.assertAlmostEqual(result.required_free_gib_if_uncached, 65.7)

    def test_exact_pinned_complete_snapshot_reduces_disk_requirement_to_headroom(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            snapshot = _complete_snapshot(Path(temp))
            result = evaluate_measurement_admission(
                runtime=_runtime(), host_memory=_host_memory(), diffusers_version="0.test",
                qwen_image_pipeline_available=True, exact_snapshot_path=str(snapshot), cache_free_gib=8.5,
            )
        self.assertTrue(result.measurement_ready)
        self.assertTrue(result.exact_snapshot_cached)
        self.assertAlmostEqual(result.required_free_gib_if_uncached, 8.0)

    def test_pinned_but_incomplete_snapshot_is_not_treated_as_cached(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            snapshot = Path(temp) / "snapshots" / QWEN_IMAGE_2512_REVISION
            snapshot.mkdir(parents=True)
            result = evaluate_measurement_admission(
                runtime=_runtime(), host_memory=_host_memory(), diffusers_version="0.test",
                qwen_image_pipeline_available=True, exact_snapshot_path=str(snapshot), cache_free_gib=80.0,
            )
        self.assertFalse(result.measurement_ready)
        self.assertFalse(result.exact_snapshot_cached)
        self.assertIn("qwen_image_snapshot_incomplete", result.reasons)

    def test_wrong_snapshot_revision_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            snapshot = _complete_snapshot(Path(temp), "b" * 40)
            result = evaluate_measurement_admission(
                runtime=_runtime(), host_memory=_host_memory(), diffusers_version="0.test",
                qwen_image_pipeline_available=True, exact_snapshot_path=str(snapshot), cache_free_gib=80.0,
            )
        self.assertFalse(result.measurement_ready)
        self.assertIn("qwen_image_snapshot_revision_mismatch", result.reasons)

    def test_qwen_image_pipeline_api_must_exist_before_measurement(self) -> None:
        result = evaluate_measurement_admission(
            runtime=_runtime(), host_memory=_host_memory(), diffusers_version="0.test",
            qwen_image_pipeline_available=False, exact_snapshot_path=None, cache_free_gib=80.0,
        )
        self.assertFalse(result.measurement_ready)
        self.assertIn("qwen_image_pipeline_unavailable", result.reasons)


if __name__ == "__main__":
    unittest.main()
