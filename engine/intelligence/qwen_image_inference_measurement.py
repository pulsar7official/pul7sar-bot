"""Fail-closed Qwen Image 2512 single-inference measurement evidence.

This module is intentionally narrower than canonical generation.  It can prove
only that the exact pinned Qwen Image 2512 snapshot completed one tiny,
identity-neutral, local inference probe after a successful pipeline-load
measurement.  A successful probe does NOT establish the production runtime
floor, does not create Golden evidence, and never authorizes publication.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_runtime_measurement import (
    LOAD_MEASUREMENT_SCHEMA,
    verify_runtime_load_receipt,
)


INFERENCE_MEASUREMENT_SCHEMA = "pul7sar-phase18-qwen-image-2512-single-inference-measurement-v1"
COST_MODE = "$0-local"
PROBE_WIDTH = 512
PROBE_HEIGHT = 512
PROBE_STEPS = 4
PROBE_GUIDANCE_SCALE = 1.0
PROBE_SEED = 181225
PROBE_OFFLOAD_MODE = "sequential_cpu"
PROBE_PROMPT = (
    "One continuous editorial sports-adjacent environment, empty architectural tunnel opening toward "
    "soft stadium-like ambient light, cinematic depth, realistic materials, no people, no faces, no "
    "identifiable club or venue cues, no readable text, no logos, no crests, no sponsor marks, no "
    "scoreboard, no exact sport geometry, no field lines, no collage, no split-screen."
)
FORBIDDEN_PROMPT_TERMS = (
    "pul7sar",
    "pulsar",
    "tottenham",
    "arsenal",
    "manchester city",
    "real madrid",
    "barcelona",
)


def sha256_json(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_probe_prompt(prompt: str = PROBE_PROMPT) -> str:
    normalized = " ".join(str(prompt).split()).strip()
    lowered = normalized.lower()
    if not normalized:
        raise ValueError("QWEN_IMAGE_INFERENCE_PROBE_PROMPT_EMPTY")
    if any(term in lowered for term in FORBIDDEN_PROMPT_TERMS):
        raise ValueError("QWEN_IMAGE_INFERENCE_PROBE_ENTITY_OR_PLATFORM_LEAK")
    required = (
        "no people",
        "no faces",
        "no readable text",
        "no logos",
        "no crests",
        "no sponsor marks",
        "no exact sport geometry",
        "no field lines",
        "no collage",
        "no split-screen",
    )
    if any(marker not in lowered for marker in required):
        raise ValueError("QWEN_IMAGE_INFERENCE_PROBE_SAFETY_MARKER_MISSING")
    return normalized


def verify_load_measurement_for_inference(receipt: dict[str, Any]) -> str:
    verified = verify_runtime_load_receipt(receipt)
    if receipt.get("schema") != LOAD_MEASUREMENT_SCHEMA:
        raise ValueError("QWEN_IMAGE_INFERENCE_LOAD_SCHEMA_MISMATCH")
    if receipt.get("status") != "QWEN_IMAGE_2512_PIPELINE_LOAD_MEASURED":
        raise ValueError("QWEN_IMAGE_INFERENCE_PIPELINE_LOAD_NOT_PROVEN")
    if receipt.get("pipeline_load_proven") is not True:
        raise ValueError("QWEN_IMAGE_INFERENCE_PIPELINE_LOAD_FALSE")
    if receipt.get("model_id") != QWEN_IMAGE_2512_MODEL_ID:
        raise ValueError("QWEN_IMAGE_INFERENCE_MODEL_MISMATCH")
    if receipt.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_IMAGE_INFERENCE_REVISION_MISMATCH")
    if receipt.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_IMAGE_INFERENCE_COST_MODE_MISMATCH")
    if receipt.get("inference_executed") is not False:
        raise ValueError("QWEN_IMAGE_INFERENCE_LOAD_RECEIPT_AUTHORITY_DRIFT")
    return verified


@dataclass(frozen=True)
class QwenImageInferenceObservation:
    child_exit_code: int
    inference_succeeded: bool
    pipeline_class: str | None
    offload_mode: str | None
    torch_version: str | None
    cuda_version: str | None
    diffusers_version: str | None
    gpu_name: str | None
    native_bf16: bool | None
    gpu_total_vram_gb: float | None
    gpu_free_vram_gb_before: float | None
    gpu_free_vram_gb_after: float | None
    max_cuda_allocated_gb: float | None
    max_cuda_reserved_gb: float | None
    process_max_rss_gb: float | None
    elapsed_seconds: float | None
    output_png_path: str | None
    output_png_sha256: str | None
    output_png_size_bytes: int | None
    failure_type: str | None = None
    failure_message: str | None = None


@dataclass(frozen=True)
class QwenImageInferenceMeasurement:
    load_receipt_sha256: str
    load_receipt_file_sha256: str
    exact_snapshot_path: str
    observation: QwenImageInferenceObservation

    def as_receipt(self) -> dict[str, Any]:
        prompt = validate_probe_prompt(PROBE_PROMPT)
        ok = bool(self.observation.inference_succeeded and self.observation.child_exit_code == 0)
        payload = {
            "schema": INFERENCE_MEASUREMENT_SCHEMA,
            "status": "QWEN_IMAGE_2512_SINGLE_INFERENCE_MEASURED" if ok else "QWEN_IMAGE_2512_SINGLE_INFERENCE_FAILED",
            "model_id": QWEN_IMAGE_2512_MODEL_ID,
            "model_revision": QWEN_IMAGE_2512_REVISION,
            "cost_mode": COST_MODE,
            "load_receipt_sha256": self.load_receipt_sha256,
            "load_receipt_file_sha256": self.load_receipt_file_sha256,
            "exact_snapshot_path": self.exact_snapshot_path,
            "measurement_kind": "isolated_single_inference_probe",
            "probe_prompt": prompt,
            "probe_prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "probe_width": PROBE_WIDTH,
            "probe_height": PROBE_HEIGHT,
            "probe_steps": PROBE_STEPS,
            "probe_guidance_scale": PROBE_GUIDANCE_SCALE,
            "probe_seed": PROBE_SEED,
            "required_offload_mode": PROBE_OFFLOAD_MODE,
            **asdict(self.observation),
            "single_inference_proven": ok,
            "engineering_measurement_only": True,
            "canonical_pixels_reusable": False,
            "runtime_floor_proven": False,
            "local_runtime_qualified": False,
            "canonical_generation_authorized": False,
            "queue_mutated": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        payload["receipt_sha256"] = sha256_json(payload)
        return payload


def verify_inference_measurement_receipt(receipt: dict[str, Any]) -> str:
    if receipt.get("schema") != INFERENCE_MEASUREMENT_SCHEMA:
        raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_SCHEMA_MISMATCH")
    if receipt.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or receipt.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_MODEL_IDENTITY_MISMATCH")
    if receipt.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_COST_MODE_MISMATCH")
    if receipt.get("measurement_kind") != "isolated_single_inference_probe":
        raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_KIND_MISMATCH")
    if receipt.get("probe_width") != PROBE_WIDTH or receipt.get("probe_height") != PROBE_HEIGHT:
        raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_CANVAS_DRIFT")
    if receipt.get("probe_steps") != PROBE_STEPS or receipt.get("probe_seed") != PROBE_SEED:
        raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_PARAMETER_DRIFT")
    if receipt.get("required_offload_mode") != PROBE_OFFLOAD_MODE:
        raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_OFFLOAD_CONTRACT_DRIFT")
    prompt = validate_probe_prompt(str(receipt.get("probe_prompt", "")))
    expected_prompt_sha = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if receipt.get("probe_prompt_sha256") != expected_prompt_sha:
        raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_PROMPT_SHA_MISMATCH")
    for field in (
        "runtime_floor_proven",
        "local_runtime_qualified",
        "canonical_generation_authorized",
        "queue_mutated",
        "semantic_approved",
        "human_visual_review_approved",
        "golden_quality_approved",
        "publication_ready",
    ):
        if receipt.get(field) is not False:
            raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_AUTHORITY_FORBIDDEN")
    if receipt.get("engineering_measurement_only") is not True or receipt.get("canonical_pixels_reusable") is not False:
        raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_BOUNDARY_MISSING")
    claimed = receipt.get("receipt_sha256")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_SHA_INVALID")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    actual = sha256_json(unsigned)
    if actual != claimed:
        raise ValueError("QWEN_IMAGE_INFERENCE_MEASUREMENT_SHA_MISMATCH")
    return actual
