#!/usr/bin/env python3
"""Execute one precompiled PUL7SAR FLUX.2 request on a compatible local CUDA GPU.

This command does not install dependencies and does not use a paid API. It fails
closed unless CUDA/VRAM and explicit Flux2KleinPipeline readiness are proven. On
success it writes a native aligned PNG, normalizes it to the exact platform
canvas, and registers the exact-canvas PNG as the visual proof with provenance.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.canvas_normalization import PillowPlatformCanvasNormalizer
from engine.intelligence.flux2_klein_diffusers import (
    Flux2KleinDiffusersProbe,
    build_flux2_klein_pipeline_factory,
)
from engine.intelligence.local_backend import LocalBackendReadinessGate
from engine.intelligence.local_backend_execution import LocalBackendResultGate
from engine.intelligence.local_diffusers_adapter import DiffusersExecutionConfig, DiffusersLocalBackend
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from engine.intelligence.local_runtime import LocalRuntimeProbe
from engine.intelligence.visual_proof import VisualProofArtifactWriter
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


def _request_from_json(path: str):
    """Compatibility wrapper used by tests and callers; enforces versioned handoff."""
    return LocalGenerationHandoff.read(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a real $0-local PUL7SAR FLUX.2 visual proof request")
    parser.add_argument("--request", required=True, help="Versioned PUL7SAR local-generation handoff JSON")
    parser.add_argument("--generation-dir", default="output/phase18_generated")
    parser.add_argument("--proof-dir", default="output/phase18_visual_proof")
    parser.add_argument("--dtype", choices=("float16", "bfloat16", "float32"), default="bfloat16")
    args = parser.parse_args()

    request = _request_from_json(args.request)
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

    backend = DiffusersLocalBackend(
        DiffusersExecutionConfig(output_dir=args.generation_dir, dtype=args.dtype),
        build_flux2_klein_pipeline_factory(),
    )
    result = backend.generate(request)
    native_provenance = LocalBackendResultGate().validate(request, result)

    normalized_path = str(Path(args.generation_dir) / f"{request.request_id}-platform.png")
    normalized = PillowPlatformCanvasNormalizer().normalize(
        request=request,
        source_png=result.output_ref,
        source_provenance=native_provenance,
        output_path=normalized_path,
    )
    artifact = VisualProofArtifactWriter(args.proof_dir).register(
        png_path=normalized.output_ref,
        provenance=normalized.provenance,
    )
    print(json.dumps({
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
        "native_width": request.width,
        "native_height": request.height,
        "width": normalized.provenance.width,
        "height": normalized.provenance.height,
        "cost_mode": "$0-local",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
