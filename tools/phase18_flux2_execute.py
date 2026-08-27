#!/usr/bin/env python3
"""Execute one precompiled PUL7SAR FLUX.2 request on a compatible local CUDA GPU.

This command does not install dependencies and does not use a paid API. It fails
closed unless CUDA/VRAM and explicit Flux2KleinPipeline readiness are proven. On
success it writes a native aligned PNG, normalizes it to the exact platform
canvas, registers the exact-canvas PNG as the visual proof with provenance, and
can persist a machine-readable result file that is immune to noisy library logs.

The Golden reference dtype remains locked to the model's documented bfloat16
Diffusers path. ``auto`` proves native BF16 and never falls back silently.
``float16-preview`` is an explicit zero-cost engineering mode for legacy GPUs
such as Colab T4; it is tagged as non-Golden and can never imply publication
readiness.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from engine.intelligence.approved_model_revisions import FLUX2_KLEIN_4B_REVISION
from engine.intelligence.canvas_normalization import PillowPlatformCanvasNormalizer
from engine.intelligence.cuda_memory import CudaPeakMemoryTracker
from engine.intelligence.flux2_klein_diffusers import (
    Flux2KleinDiffusersProbe,
    build_flux2_klein_pipeline_factory,
)
from engine.intelligence.local_backend import LocalBackendReadinessGate
from engine.intelligence.local_backend_execution import LocalBackendResultGate
from engine.intelligence.local_diffusers_adapter import DiffusersExecutionConfig, DiffusersLocalBackend
from engine.intelligence.local_dtype import LocalDTypeSelector
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from engine.intelligence.local_runtime import LocalRuntimeProbe
from engine.intelligence.visual_proof import VisualProofArtifactWriter
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


_DYNAMIC_VISUAL_BRAIN_RESULT_KEYS = (
    "dynamic_visual_brain_contract",
    "dynamic_visual_brain_story_fingerprint",
    "dynamic_visual_brain_competition_sha256",
    "dynamic_visual_brain_selected_concept_id",
    "dynamic_visual_brain_selected_concept_sha256",
    "dynamic_visual_brain_scene_prompt_sha256",
    "dynamic_visual_brain_original_scene_request_sha256",
    "dynamic_visual_brain_selection_locked_before_rendering",
)


def _request_from_json(path: str):
    """Compatibility wrapper used by tests and callers; enforces versioned handoff."""
    return LocalGenerationHandoff.read(path)


def _handoff_payload_sha256(path: str) -> str:
    """Return the already-verified handoff digest for durable result provenance."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    supplied = data.get("payload_sha256")
    if not isinstance(supplied, str) or len(supplied) != 64:
        raise ValueError("generation handoff is missing a valid payload_sha256")
    LocalGenerationHandoff.read(path)
    return supplied


def _verified_execution_metadata(result) -> tuple[str, str]:
    """Fail closed unless the real pipeline reports the approved revision/offload mode."""
    metadata = getattr(result, "metadata", None)
    if not isinstance(metadata, dict) and not hasattr(metadata, "get"):
        raise RuntimeError("FLUX.2 execution metadata is missing")
    model_revision = metadata.get("model_revision")
    if model_revision != FLUX2_KLEIN_4B_REVISION:
        raise RuntimeError("FLUX.2 execution model revision drifted from the approved immutable revision")
    offload_mode = metadata.get("offload_mode")
    if offload_mode not in {"sequential_cpu", "model_cpu"}:
        raise RuntimeError("FLUX.2 execution did not prove a safe CPU offload mode")
    return str(offload_mode), str(model_revision)


def _dynamic_visual_brain_result_metadata(request) -> dict[str, object]:
    """Carry only locked Dynamic Visual Brain identity into durable executor results.

    The local handoff already SHA-protects request metadata.  This function makes
    the story/concept hashes independently available to downstream PNG/critic
    provenance without granting the generator any additional authority.
    """
    metadata = dict(request.metadata)
    contract = metadata.get("dynamic_visual_brain_contract")
    if not contract:
        return {}

    missing = [key for key in _DYNAMIC_VISUAL_BRAIN_RESULT_KEYS if key not in metadata]
    if missing:
        raise RuntimeError("Dynamic Visual Brain generation metadata is incomplete: " + ", ".join(missing))
    for key in (
        "dynamic_visual_brain_story_fingerprint",
        "dynamic_visual_brain_competition_sha256",
        "dynamic_visual_brain_selected_concept_sha256",
        "dynamic_visual_brain_scene_prompt_sha256",
        "dynamic_visual_brain_original_scene_request_sha256",
    ):
        value = metadata.get(key)
        if not isinstance(value, str) or len(value) != 64:
            raise RuntimeError(f"Dynamic Visual Brain generation metadata has invalid {key}")
    if not isinstance(metadata.get("dynamic_visual_brain_selected_concept_id"), str) or not str(
        metadata.get("dynamic_visual_brain_selected_concept_id")
    ).strip():
        raise RuntimeError("Dynamic Visual Brain generation metadata has invalid selected concept id")
    if metadata.get("dynamic_visual_brain_selection_locked_before_rendering") is not True:
        raise RuntimeError("Dynamic Visual Brain concept was not locked before rendering")

    authority_expectations = {
        "cost_mode": "$0-local",
        "generated_branding_allowed": False,
        "generated_exact_facts_allowed": False,
        "generated_sport_geometry_allowed": False,
        "semantic_inspection_required": True,
        "human_visual_review_required": True,
        "publication_ready": False,
    }
    for key, expected in authority_expectations.items():
        if metadata.get(key) != expected:
            raise RuntimeError(f"Dynamic Visual Brain generation authority drifted at {key}")

    return {key: metadata[key] for key in _DYNAMIC_VISUAL_BRAIN_RESULT_KEYS}


def execute_request(
    *,
    request_path: str,
    generation_dir: str,
    proof_dir: str,
    dtype: str,
) -> dict[str, object]:
    request = _request_from_json(request_path)
    payload_sha256 = _handoff_payload_sha256(request_path)
    dynamic_visual_brain_metadata = _dynamic_visual_brain_result_metadata(request)
    model = FLUX2_KLEIN_4B_LOCAL
    if request.provider_id != model.provider_id or request.model_id != model.model_id:
        raise ValueError("request does not target the approved zero-cost FLUX.2 klein candidate")
    if request.backend != "diffusers":
        raise ValueError("this execution command only accepts the local diffusers backend")
    if request.reference_asset_ids:
        raise ValueError(
            "reference-image execution remains blocked until the verified asset-path resolver is connected"
        )

    runtime = LocalRuntimeProbe().detect()
    backend_snapshot = Flux2KleinDiffusersProbe().probe()
    readiness = LocalBackendReadinessGate().evaluate(
        model=model,
        runtime=runtime,
        backend=backend_snapshot,
    )
    if not readiness.ready:
        detail = ", ".join(backend_snapshot.details)
        raise RuntimeError(
            "local FLUX.2 execution is not ready: "
            + "; ".join(readiness.failures)
            + (f"; backend_details={detail}" if detail else "")
        )

    dtype_decision = LocalDTypeSelector().select(runtime, dtype)
    memory_tracker = CudaPeakMemoryTracker()
    peak_counters_reset = memory_tracker.reset()
    execution_started_at = datetime.now(timezone.utc)
    execution_started_monotonic = time.monotonic()

    backend = DiffusersLocalBackend(
        DiffusersExecutionConfig(output_dir=generation_dir, dtype=dtype_decision.resolved),
        build_flux2_klein_pipeline_factory(),
    )
    result = backend.generate(request)
    actual_offload_mode, actual_model_revision = _verified_execution_metadata(result)
    native_provenance = LocalBackendResultGate().validate(request, result)

    normalized_path = str(Path(generation_dir) / f"{request.request_id}-platform.png")
    normalized = PillowPlatformCanvasNormalizer().normalize(
        request=request,
        source_png=result.output_ref,
        source_provenance=native_provenance,
        output_path=normalized_path,
    )
    artifact = VisualProofArtifactWriter(proof_dir).register(
        png_path=normalized.output_ref,
        provenance=normalized.provenance,
    )

    execution_seconds = time.monotonic() - execution_started_monotonic
    execution_finished_at = datetime.now(timezone.utc)
    memory = memory_tracker.capture()

    payload: dict[str, object] = {
        "status": "REAL_VISUAL_PROOF_GENERATED",
        "png": artifact.png_path,
        "metadata": artifact.metadata_path,
        "native_png": result.output_ref,
        "provider_id": normalized.provenance.provider_id,
        "model_id": normalized.provenance.model_id,
        "model_revision": actual_model_revision,
        "backend": normalized.provenance.backend,
        "backend_version": backend_snapshot.version,
        "seed": normalized.provenance.seed,
        "request_id": normalized.provenance.request_id,
        "payload_sha256": payload_sha256,
        "native_width": request.width,
        "native_height": request.height,
        "width": normalized.provenance.width,
        "height": normalized.provenance.height,
        "requested_dtype": dtype_decision.requested,
        "resolved_dtype": dtype_decision.resolved,
        "dtype_reason": dtype_decision.reason,
        "precision_quality_tier": dtype_decision.quality_tier,
        "golden_reference_precision": dtype_decision.quality_tier == "golden_reference",
        "actual_offload_mode": actual_offload_mode,
        "offload_mode_proven": True,
        "gpu_name": runtime.gpu_name,
        "gpu_vram_gb": runtime.gpu_vram_gb,
        "bf16_supported": runtime.metadata.get("bf16_supported"),
        "compute_capability": runtime.metadata.get("compute_capability"),
        "execution_started_at": execution_started_at.isoformat(),
        "execution_finished_at": execution_finished_at.isoformat(),
        "execution_seconds": execution_seconds,
        "cuda_memory_available": memory.available,
        "cuda_peak_counters_reset": peak_counters_reset,
        "cuda_device_index": memory.device_index,
        "cuda_peak_allocated_gb": memory.peak_allocated_gb,
        "cuda_peak_reserved_gb": memory.peak_reserved_gb,
        "cuda_current_allocated_gb": memory.current_allocated_gb,
        "cuda_current_reserved_gb": memory.current_reserved_gb,
        "cuda_memory_blocker": memory.blocker,
        "cost_mode": "$0-local",
        "publication_ready": False,
    }
    payload.update(dynamic_visual_brain_metadata)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a real $0-local PUL7SAR FLUX.2 visual proof request")
    parser.add_argument("--request", required=True, help="Versioned PUL7SAR local-generation handoff JSON")
    parser.add_argument("--generation-dir", default="output/phase18_generated")
    parser.add_argument("--proof-dir", default="output/phase18_visual_proof")
    parser.add_argument("--dtype", choices=("auto", "bfloat16", "float16-preview"), default="auto")
    parser.add_argument(
        "--result",
        help="Optional JSON result path. Batch execution should prefer this over parsing stdout.",
    )
    args = parser.parse_args()

    payload = execute_request(
        request_path=args.request,
        generation_dir=args.generation_dir,
        proof_dir=args.proof_dir,
        dtype=args.dtype,
    )
    if args.result:
        result_path = Path(args.result)
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
