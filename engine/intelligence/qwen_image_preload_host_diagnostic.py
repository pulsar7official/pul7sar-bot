"""Non-inference host diagnostic for the Phase 18 Qwen Image path."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

SCHEMA = "pul7sar-phase18-qwen-image-2512-preload-host-diagnostic-v1"


def compare_preload_identity(observed: Mapping[str, Any], expected: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field, value in observed.items():
        wanted = expected.get(field)
        if field == "gpu_total_vram_gb":
            if not isinstance(wanted, (int, float)) or isinstance(wanted, bool):
                blockers.append("expected_vram_invalid")
            elif abs(float(value) - float(wanted)) > 0.05:
                blockers.append("identity_drift:gpu_total_vram_gb")
        elif value != wanted:
            blockers.append(f"identity_drift:{field}")
    return sorted(set(blockers))


def non_authority_fields() -> dict[str, bool]:
    return {
        "model_load_attempted": False,
        "inference_executed": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
