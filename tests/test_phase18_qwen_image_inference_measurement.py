from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_MODEL_ID, QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_inference_measurement import (
    COST_MODE,
    INFERENCE_MEASUREMENT_SCHEMA,
    PROBE_HEIGHT,
    PROBE_OFFLOAD_MODE,
    PROBE_PROMPT,
    PROBE_SEED,
    PROBE_STEPS,
    PROBE_WIDTH,
    QwenImageInferenceMeasurement,
    QwenImageInferenceObservation,
    sha256_json,
    validate_probe_prompt,
    verify_inference_measurement_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "phase18_measure_qwen_image_single_inference.py"


def _observation(*, success: bool = True) -> QwenImageInferenceObservation:
    return QwenImageInferenceObservation(
        child_exit_code=0 if success else 2,
        inference_succeeded=success,
        pipeline_class="QwenImagePipeline" if success else None,
        offload_mode=PROBE_OFFLOAD_MODE if success else None,
        torch_version="2.x",
        cuda_version="12.x",
        diffusers_version="0.x",
        gpu_name="Synthetic GPU",
        native_bf16=True,
        gpu_total_vram_gb=24.0,
        gpu_free_vram_gb_before=23.0,
        gpu_free_vram_gb_after=20.0 if success else None,
        max_cuda_allocated_gb=2.0 if success else None,
        max_cuda_reserved_gb=3.0 if success else None,
        process_max_rss_gb=30.0,
        elapsed_seconds=12.0,
        output_png_path="output/phase18_gpu_smoke/probe.png" if success else None,
        output_png_sha256="a" * 64 if success else None,
        output_png_size_bytes=1234 if success else None,
        failure_type=None if success else "RuntimeError",
        failure_message=None if success else "synthetic failure",
    )


def _receipt(*, success: bool = True) -> dict:
    measurement = QwenImageInferenceMeasurement(
        load_receipt_sha256="b" * 64,
        load_receipt_file_sha256="c" * 64,
        exact_snapshot_path=f"/tmp/snapshots/{QWEN_IMAGE_2512_REVISION}",
        observation=_observation(success=success),
    )
    return measurement.as_receipt()


def test_probe_prompt_is_identity_neutral_and_guarded() -> None:
    normalized = validate_probe_prompt(PROBE_PROMPT)
    lowered = normalized.lower()
    assert "pul7sar" not in lowered
    assert "pulsar" not in lowered
    assert "no people" in lowered
    assert "no faces" in lowered
    assert "no readable text" in lowered
    assert "no exact sport geometry" in lowered


def test_successful_probe_still_has_no_canonical_or_publication_authority() -> None:
    receipt = _receipt(success=True)
    assert receipt["schema"] == INFERENCE_MEASUREMENT_SCHEMA
    assert receipt["status"] == "QWEN_IMAGE_2512_SINGLE_INFERENCE_MEASURED"
    assert receipt["model_id"] == QWEN_IMAGE_2512_MODEL_ID
    assert receipt["model_revision"] == QWEN_IMAGE_2512_REVISION
    assert receipt["cost_mode"] == COST_MODE
    assert receipt["single_inference_proven"] is True
    assert receipt["engineering_measurement_only"] is True
    assert receipt["canonical_pixels_reusable"] is False
    assert receipt["runtime_floor_proven"] is False
    assert receipt["local_runtime_qualified"] is False
    assert receipt["canonical_generation_authorized"] is False
    assert receipt["semantic_approved"] is False
    assert receipt["human_visual_review_approved"] is False
    assert receipt["golden_quality_approved"] is False
    assert receipt["publication_ready"] is False
    assert verify_inference_measurement_receipt(receipt) == receipt["receipt_sha256"]


def test_probe_contract_is_fixed_and_small() -> None:
    receipt = _receipt(success=True)
    assert receipt["probe_width"] == PROBE_WIDTH == 512
    assert receipt["probe_height"] == PROBE_HEIGHT == 512
    assert receipt["probe_steps"] == PROBE_STEPS == 4
    assert receipt["probe_seed"] == PROBE_SEED
    assert receipt["required_offload_mode"] == PROBE_OFFLOAD_MODE == "sequential_cpu"


def test_authority_drift_is_rejected_even_with_recomputed_sha() -> None:
    receipt = _receipt(success=True)
    tampered = copy.deepcopy(receipt)
    tampered["publication_ready"] = True
    tampered.pop("receipt_sha256")
    tampered["receipt_sha256"] = sha256_json(tampered)
    with pytest.raises(ValueError, match="AUTHORITY_FORBIDDEN"):
        verify_inference_measurement_receipt(tampered)


def test_probe_prompt_entity_leak_is_rejected() -> None:
    with pytest.raises(ValueError, match="ENTITY_OR_PLATFORM_LEAK"):
        validate_probe_prompt(PROBE_PROMPT + " PUL7SAR")


def test_probe_prompt_missing_geometry_marker_is_rejected() -> None:
    damaged = PROBE_PROMPT.replace("no exact sport geometry, ", "")
    assert damaged != PROBE_PROMPT
    with pytest.raises(ValueError, match="SAFETY_MARKER_MISSING"):
        validate_probe_prompt(damaged)


def test_tool_uses_local_only_bf16_sequential_offload_and_one_image() -> None:
    source = TOOL.read_text(encoding="utf-8")
    assert "local_files_only=True" in source
    assert "torch_dtype=torch.bfloat16" in source
    assert "enable_sequential_cpu_offload" in source
    assert "torch.Generator(device=\"cpu\").manual_seed(PROBE_SEED)" in source
    assert "len(images) != 1" in source
    assert "images[0].save(png_path, format=\"PNG\")" in source
    assert "pipeline_cls.from_pretrained" in source


def test_tool_does_not_call_queue_or_publication_paths() -> None:
    source = TOOL.read_text(encoding="utf-8").lower()
    forbidden = (
        "generationjobstore",
        "queue_mutated = true",
        "publication_ready = true",
        "golden_quality_approved = true",
        "semantic_approved = true",
    )
    for token in forbidden:
        assert token not in source


def test_failed_probe_remains_non_authoritative() -> None:
    receipt = _receipt(success=False)
    assert receipt["status"] == "QWEN_IMAGE_2512_SINGLE_INFERENCE_FAILED"
    assert receipt["single_inference_proven"] is False
    assert receipt["runtime_floor_proven"] is False
    assert receipt["canonical_generation_authorized"] is False
    assert receipt["publication_ready"] is False
    verify_inference_measurement_receipt(receipt)
