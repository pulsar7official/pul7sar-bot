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


def execute_request(
    *,
    request_path: str,
    generation_dir: str,
    proof_dir: str,
    dtype: str,
) -> dict[str, object]:
    request = _request_from_json(request_path)
    payload_sha256 = _handoff_payload_sha256(request_path)
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

    return {
        "status": "REAL_VISUAL_PROOF_GENERATED",
        "png": artifact.png_path,
        "metadata": artifact.metadata_path,
        "native_png": result.output_ref,
        "provider_id": normalized.provenance.provider_id,
        "model_id": normalized.provenance.model_id,
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
