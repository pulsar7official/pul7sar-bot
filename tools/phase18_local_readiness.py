"""Print PUL7SAR Phase 18 local generation/publication readiness as JSON.

Usage from repository root:
    python tools/phase18_local_readiness.py

The command installs nothing, downloads nothing, and calls no paid API. For the
approved FLUX.2 klein candidate it proves that the installed Diffusers build
actually exposes Flux2KleinPipeline, not merely that `diffusers` can import.
When generation readiness is proven it also reports the CUDA-aware dtype that the
real executor will resolve from `--dtype auto`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.flux2_klein_diffusers import Flux2KleinDiffusersProbe
from engine.intelligence.local_backend import LocalBackendKind
from engine.intelligence.local_dtype import LocalDTypeSelector
from engine.intelligence.local_readiness_service import LocalReadinessService
from engine.intelligence.local_runtime import LocalRuntimeProbe
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


def main() -> int:
    backend = Flux2KleinDiffusersProbe().probe()
    runtime = LocalRuntimeProbe().detect()
    bundle = LocalReadinessService().evaluate(
        model=FLUX2_KLEIN_4B_LOCAL,
        backend=backend,
        runtime=runtime,
    )
    report = bundle.as_dict()
    dtype_report: dict[str, object] = {
        "requested": "auto",
        "resolved": None,
        "reason": "generation runtime is not ready",
        "bf16_supported": runtime.metadata.get("bf16_supported"),
        "compute_capability": runtime.metadata.get("compute_capability"),
    }
    if bundle.generation_ready:
        decision = LocalDTypeSelector().select(runtime, "auto")
        dtype_report.update({
            "resolved": decision.resolved,
            "reason": decision.reason,
        })
    report["recommended_dtype"] = dtype_report
    report["command_policy"] = {
        "installs_dependencies": False,
        "downloads_model_weights": False,
        "uses_paid_api": False,
        "backend_probe": LocalBackendKind.DIFFUSERS.value,
        "required_pipeline": "Flux2KleinPipeline",
        "backend_details": list(backend.details),
        "backend_version": backend.version,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if bundle.generation_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
