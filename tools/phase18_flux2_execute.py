#!/usr/bin/env python3
"""Execute one precompiled PUL7SAR FLUX.2 request on a compatible local CUDA GPU.

This command does not install dependencies and does not use a paid API. It fails
closed unless CUDA/VRAM and Diffusers readiness are proven. On success it writes
a real PNG and registers it into output/phase18_visual_proof with provenance.
"""

from __future__ import annotations

import argparse
import json

from engine.intelligence.flux2_klein_diffusers import build_flux2_klein_pipeline_factory
from engine.intelligence.local_backend import LocalBackendReadinessGate
from engine.intelligence.local_backend_execution import LocalBackendResultGate
from engine.intelligence.local_diffusers_adapter import (
    DiffusersBackendProbe,
    DiffusersExecutionConfig,
    DiffusersLocalBackend,
)
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
    backend_snapshot = DiffusersBackendProbe().probe()
    readiness = LocalBackendReadinessGate().evaluate(
        model=model,
        runtime=runtime,
        backend=backend_snapshot,
    )
    if not readiness.ready:
        raise RuntimeError("local FLUX.2 execution is not ready: " + "; ".join(readiness.failures))

    backend = DiffusersLocalBackend(
        DiffusersExecutionConfig(output_dir=args.generation_dir, dtype=args.dtype),
        build_flux2_klein_pipeline_factory(),
    )
    result = backend.generate(request)
    provenance = LocalBackendResultGate().validate(request, result)
    artifact = VisualProofArtifactWriter(args.proof_dir).register(
        png_path=result.output_ref,
        provenance=provenance,
    )
    print(json.dumps({
        "status": "REAL_VISUAL_PROOF_GENERATED",
        "png": artifact.png_path,
        "metadata": artifact.metadata_path,
        "provider_id": provenance.provider_id,
        "model_id": provenance.model_id,
        "backend": provenance.backend,
        "seed": provenance.seed,
        "request_id": provenance.request_id,
        "width": provenance.width,
        "height": provenance.height,
        "cost_mode": "$0-local",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
