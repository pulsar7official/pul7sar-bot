"""Aggregate, non-inference host diagnostic for the Phase 18 Qwen Image path.

CS355 upgrades the mandatory preload diagnostic to replay the CS354
inventory-bound launch manifest. The exact already-local Qwen snapshot bytes are
therefore revalidated inside the same diagnostic that checks static readiness and
the live CS260 host identity, before the launcher may start the canonical child.

This module remains pre-model-load and non-authoritative: it does not download or
load Qwen, execute inference, create pixels, approve semantics/visual quality, or
grant Golden/publication authority.
"""
from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any, Mapping

from .qwen_image_inventory_bound_launch_manifest import (
    verify_inventory_bound_gpu_host_launch_manifest as verify_gpu_host_launch_manifest,
)
from .qwen_image_gpu_readiness import inspect_qwen_image_gpu_readiness
from .qwen_image_local_inference_runtime import _expected_identity, _pre_model_load_identity
from .qwen_image_story_bound_generation_authorization import (
    verify_live_pipeline_receipt,
    verify_story_bound_generation_authorization,
)

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


def inspect_preload_host(launch_manifest_path: Path, *, repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    manifest = verify_gpu_host_launch_manifest(launch_manifest_path, repo_root=root)
    auth = manifest.get("authorization")
    auth_rel = auth.get("repository_relative_path") if isinstance(auth, Mapping) else None
    if not isinstance(auth_rel, str) or Path(auth_rel).is_absolute():
        raise ValueError("QWEN_PRELOAD_DIAGNOSTIC_AUTHORIZATION_BINDING_INVALID")
    authorization = verify_story_bound_generation_authorization(root / auth_rel, repo_root=root)
    source = authorization.get("source_live_pipeline_recheck")
    cs260_rel = source.get("repository_relative_path") if isinstance(source, Mapping) else None
    if not isinstance(cs260_rel, str) or Path(cs260_rel).is_absolute():
        raise ValueError("QWEN_PRELOAD_DIAGNOSTIC_CS260_BINDING_INVALID")
    cs260 = verify_live_pipeline_receipt(root / cs260_rel, repo_root=root)
    expected = _expected_identity(cs260)

    snapshot = manifest.get("snapshot")
    snapshot_path = snapshot.get("resolved_path") if isinstance(snapshot, Mapping) else None
    if not isinstance(snapshot_path, str) or not snapshot_path:
        raise ValueError("QWEN_PRELOAD_DIAGNOSTIC_SNAPSHOT_BINDING_INVALID")

    readiness = inspect_qwen_image_gpu_readiness(snapshot_path=snapshot_path)
    blockers = list(readiness.blockers)
    observed = None
    if readiness.static_preflight_passed:
        try:
            torch = import_module("torch")
            diffusers = import_module("diffusers")
            observed = _pre_model_load_identity(torch=torch, diffusers=diffusers)
            blockers.extend(compare_preload_identity(observed, expected))
        except Exception as exc:
            blockers.append(f"host_identity_probe_failed:{type(exc).__name__}")

    payload = {
        "schema": SCHEMA,
        "story_snapshot_sha256": manifest.get("story_snapshot_sha256"),
        "launch_manifest_sha256": manifest.get("manifest_sha256"),
        "snapshot_path": snapshot_path,
        "snapshot_inventory_bound": True,
        "static_preflight_passed": bool(readiness.static_preflight_passed),
        "observed_preload_identity": observed,
        "blockers": sorted(set(blockers)),
    }
    payload["ready_for_model_load_attempt"] = not payload["blockers"]
    payload.update(non_authority_fields())
    return payload
