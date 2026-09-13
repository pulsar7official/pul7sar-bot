"""Print PUL7SAR Phase 18 local generation/publication readiness as JSON.

The command installs nothing, downloads nothing, and calls no paid API. It
proves the installed Diffusers build exposes Flux2KleinPipeline and separates
the quality-locked Golden BF16 path from the explicit FP16 engineering-preview
path used on compatible zero-cost legacy GPUs such as Colab T4.
"""
from __future__ import annotations

import argparse
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
    parser = argparse.ArgumentParser(description="PUL7SAR Phase 18 local GPU readiness")
    parser.add_argument("--dtype", choices=("auto", "bfloat16", "float16-preview"), default="auto")
    args = parser.parse_args()

    backend = Flux2KleinDiffusersProbe().probe()
    runtime = LocalRuntimeProbe().detect()
    bundle = LocalReadinessService().evaluate(
        model=FLUX2_KLEIN_4B_LOCAL,
        backend=backend,
        runtime=runtime,
    )
    report = bundle.as_dict()
    dtype_report: dict[str, object] = {
        "requested": args.dtype,
        "resolved": None,
        "reason": "generation runtime is not ready",
        "bf16_supported": runtime.metadata.get("bf16_supported"),
        "compute_capability": runtime.metadata.get("compute_capability"),
    }
    requested_generation_ready = False
    golden_generation_ready = False
    precision_quality_tier = None
    if bundle.generation_ready:
        try:
            decision = LocalDTypeSelector().select(runtime, args.dtype)
        except ValueError as exc:
            dtype_report["reason"] = str(exc)
        else:
            dtype_report.update({
                "resolved": decision.resolved,
                "reason": decision.reason,
                "quality_tier": decision.quality_tier,
            })
            precision_quality_tier = decision.quality_tier
            requested_generation_ready = True
            golden_generation_ready = decision.quality_tier == "golden_reference"

    report["recommended_dtype"] = dtype_report
    report["requested_generation_ready"] = requested_generation_ready
    report["golden_generation_ready"] = golden_generation_ready
    report["precision_quality_tier"] = precision_quality_tier
    report["publication_ready"] = False
    report["command_policy"] = {
        "installs_dependencies": False,
        "downloads_model_weights": False,
        "uses_paid_api": False,
        "backend_probe": LocalBackendKind.DIFFUSERS.value,
        "required_pipeline": "Flux2KleinPipeline",
        "golden_reference_dtype": "bfloat16",
        "engineering_preview_dtype": "float16",
        "preview_may_claim_golden": False,
        "backend_details": list(backend.details),
        "backend_version": backend.version,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if requested_generation_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
