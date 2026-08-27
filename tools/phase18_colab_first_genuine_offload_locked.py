#!/usr/bin/env python3
"""Pre-model FLUX offload lock around the canonical first genuine Golden v6 path.

The wrapper proves the installed Diffusers FLUX.2 offload capability before the
resource/model-cache/runtime/semantic lock is allowed to begin model work. It
then replays the host identity against the inner resource lock and proves that
the real FLUX executor used the exact safe offload mode selected by preflight.
The preflight, actual-execution provenance, host qualification and inner resource
lock are sealed by SHA-256.

It never authorizes human acceptance, Golden quality, publication, or Seeds 2-4.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
OFFLOAD_GPU_HOST = ROOT / "output" / "phase18_gpu_smoke" / "offload-gpu-host-qualification.json"
OFFLOAD_PREFLIGHT = ROOT / "output" / "phase18_gpu_smoke" / "flux2-offload-preflight.json"
INNER_RESOURCE_LOCK = ROOT / "output" / "phase18_gpu_smoke" / "first-genuine-golden-v6-resource-lock.json"
ACTUAL_OFFLOAD_PROVENANCE = ROOT / "output" / "phase18_gpu_smoke" / "first-genuine-golden-v6-actual-offload-provenance.json"
FINAL = ROOT / "output" / "phase18_gpu_smoke" / "first-genuine-golden-v6-offload-lock.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.approved_model_revisions import FLUX2_KLEIN_4B_MODEL_ID
from engine.intelligence.golden_offload_provenance import GoldenOffloadProvenanceLock


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_LOCK_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _inside_repo(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_LOCK_PATH_ESCAPES_REPOSITORY")
    return target


def _load(path: Path) -> dict[str, object]:
    target = _inside_repo(path)
    if not target.is_file():
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_OFFLOAD_EVIDENCE_MISSING:{target}")
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_EVIDENCE_INVALID")
    return payload


def _record(path: Path) -> dict[str, object]:
    target = _inside_repo(path)
    if not target.is_file():
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_OFFLOAD_EVIDENCE_MISSING:{target}")
    data = target.read_bytes()
    return {"path": str(target), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def _write(path: Path, payload: dict[str, object]) -> None:
    target = _inside_repo(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _run(command: list[str], *, label: str) -> None:
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"{label}_FAILED:{completed.returncode}")


def _validate_host(host: dict[str, object]) -> None:
    if host.get("eligible") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_HOST_NOT_ELIGIBLE")
    if host.get("model_id") != FLUX2_KLEIN_4B_MODEL_ID:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_HOST_MODEL_DRIFT")
    if host.get("runtime_kind") != "local_cuda" or host.get("cuda_available") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_HOST_CUDA_NOT_PROVEN")
    if host.get("bf16_supported") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_HOST_BF16_NOT_PROVEN")
    if host.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_HOST_COST_MODE_DRIFT")
    if not isinstance(host.get("gpu_name"), str) or not str(host.get("gpu_name")).strip():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_HOST_IDENTITY_NOT_PROVEN")
    for field in ("gpu_vram_gb", "gpu_free_vram_gb", "required_vram_gb"):
        value = host.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) <= 0:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_OFFLOAD_HOST_{field.upper()}_INVALID")
    if float(host["gpu_free_vram_gb"]) < float(host["required_vram_gb"]):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_HOST_LIVE_VRAM_BELOW_FLOOR")


def _validate_offload(offload: dict[str, object], host: dict[str, object]) -> None:
    if offload.get("schema") != "pul7sar-phase18-flux2-offload-preflight-v1":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_SCHEMA_DRIFT")
    if offload.get("branch") != EXPECTED_BRANCH or offload.get("ready") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_NOT_READY")
    if offload.get("model_id") != FLUX2_KLEIN_4B_MODEL_ID:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_MODEL_DRIFT")
    if offload.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_COST_MODE_DRIFT")
    for field in (
        "model_loaded",
        "downloads_performed",
        "generation_authorized",
        "queue_mutated",
        "png_created",
        "semantic_approved",
        "golden_quality_approved",
        "publication_ready",
    ):
        if offload.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_OFFLOAD_AUTHORITY_DRIFT:{field}")

    total_vram = offload.get("gpu_vram_gb")
    host_total_vram = host.get("gpu_vram_gb")
    if isinstance(total_vram, bool) or not isinstance(total_vram, (int, float)):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_TOTAL_VRAM_INVALID")
    if abs(float(total_vram) - float(host_total_vram)) > 1e-6:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_TOTAL_VRAM_HOST_DRIFT")

    minimum = offload.get("model_offload_minimum_total_vram_gb")
    if isinstance(minimum, bool) or not isinstance(minimum, (int, float)) or float(minimum) <= 0:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_THRESHOLD_INVALID")
    expected_low_vram = float(total_vram) <= float(minimum)
    if offload.get("low_vram_host") is not expected_low_vram:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_LOW_VRAM_CLASSIFICATION_DRIFT")

    selected = offload.get("selected_safe_mode")
    if expected_low_vram:
        if selected != "sequential_cpu" or offload.get("sequential_cpu_offload_available") is not True:
            raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_LOW_VRAM_SEQUENTIAL_NOT_PROVEN")
    else:
        if selected == "sequential_cpu":
            if offload.get("sequential_cpu_offload_available") is not True:
                raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_SEQUENTIAL_CAPABILITY_DRIFT")
        elif selected == "model_cpu":
            if offload.get("model_cpu_offload_available") is not True:
                raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_MODEL_CPU_CAPABILITY_DRIFT")
        else:
            raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_SAFE_MODE_UNPROVEN")


def _validate_inner(inner: dict[str, object], initial_host: dict[str, object]) -> dict[str, object]:
    if inner.get("schema") != "pul7sar-first-genuine-golden-v6-resource-lock-v4":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_INNER_SCHEMA_DRIFT")
    if inner.get("status") != "FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_INNER_NOT_VERIFIED")
    if inner.get("branch") != EXPECTED_BRANCH or inner.get("candidate") != 1:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_INNER_IDENTITY_DRIFT")
    if inner.get("cost_mode") != "$0-local" or inner.get("native_bf16_proven") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_INNER_EXECUTION_POLICY_DRIFT")
    if inner.get("gpu_eligible") is not True or inner.get("runtime_stable_across_generation") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_INNER_RESOURCE_RUNTIME_DRIFT")
    for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
        if inner.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_OFFLOAD_INNER_AUTHORITY_DRIFT:{field}")

    evidence = inner.get("evidence")
    if not isinstance(evidence, dict):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_INNER_EVIDENCE_MISSING")
    record = evidence.get("gpu_host_qualification")
    if not isinstance(record, dict) or not isinstance(record.get("path"), str):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_INNER_GPU_EVIDENCE_MISSING")
    inner_host = _load(Path(str(record["path"])))
    _validate_host(inner_host)
    for field in ("gpu_name", "model_id", "compute_capability", "bf16_supported", "runtime_kind", "cost_mode"):
        if inner_host.get(field) != initial_host.get(field):
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_OFFLOAD_HOST_REPLAY_DRIFT:{field}")
    if abs(float(inner_host["gpu_vram_gb"]) - float(initial_host["gpu_vram_gb"])) > 1e-6:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_HOST_REPLAY_DRIFT:gpu_vram_gb")
    return inner_host


def _bind_actual_offload(inner: dict[str, object], offload: dict[str, object]) -> dict[str, object]:
    staging_value = inner.get("staging_receipt")
    if not isinstance(staging_value, str) or not staging_value.strip():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_STAGING_RECEIPT_MISSING")
    staging = _inside_repo(Path(staging_value))
    receipt = GoldenOffloadProvenanceLock().verify(
        repository_root=ROOT,
        preflight_receipt=OFFLOAD_PREFLIGHT,
        staging_receipt=staging,
    )
    if receipt.get("selected_safe_offload_mode") != offload.get("selected_safe_mode"):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_PROVENANCE_PREFLIGHT_MODE_DRIFT")
    if receipt.get("actual_offload_mode") != offload.get("selected_safe_mode"):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_ACTUAL_MODE_DRIFT")
    if receipt.get("actual_offload_mode_bound") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_ACTUAL_MODE_NOT_BOUND")
    if receipt.get("publication_ready") is not False or receipt.get("golden_quality_approved") is not False:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_PROVENANCE_AUTHORITY_DRIFT")
    _write(ACTUAL_OFFLOAD_PROVENANCE, receipt)
    return receipt


def run(*, force: bool = False, output: Path = FINAL) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_LOCK_BRANCH_BLOCKED")

    _run(
        [sys.executable, str(ROOT / "tools" / "phase18_qualify_gpu_host.py"), "--output", str(OFFLOAD_GPU_HOST)],
        label="FIRST_GENUINE_GOLDEN_OFFLOAD_GPU_QUALIFICATION",
    )
    initial_host = _load(OFFLOAD_GPU_HOST)
    _validate_host(initial_host)

    _run(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_preflight_flux2_offload.py"),
            "--host-qualification",
            str(OFFLOAD_GPU_HOST),
            "--output",
            str(OFFLOAD_PREFLIGHT),
        ],
        label="FIRST_GENUINE_GOLDEN_OFFLOAD_PREFLIGHT",
    )
    offload = _load(OFFLOAD_PREFLIGHT)
    _validate_offload(offload, initial_host)

    command = [
        sys.executable,
        str(ROOT / "tools" / "phase18_colab_first_genuine_resources_locked.py"),
        "--output",
        str(INNER_RESOURCE_LOCK),
    ]
    if force:
        command.append("--force")
    _run(command, label="FIRST_GENUINE_GOLDEN_OFFLOAD_INNER_RESOURCE_LOCK")

    inner = _load(INNER_RESOURCE_LOCK)
    _validate_inner(inner, initial_host)
    actual_offload = _bind_actual_offload(inner, offload)

    png_value = inner.get("png")
    if not isinstance(png_value, str) or not png_value.strip():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_PNG_MISSING")
    png = _inside_repo(Path(png_value))
    if not png.is_file() or png.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_PNG_INVALID")
    png_sha = hashlib.sha256(png.read_bytes()).hexdigest()
    if inner.get("png_sha256") != png_sha:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_OFFLOAD_PNG_SHA_DRIFT")

    evidence = {
        "offload_gpu_host_qualification": _record(OFFLOAD_GPU_HOST),
        "flux2_offload_preflight": _record(OFFLOAD_PREFLIGHT),
        "actual_offload_provenance": _record(ACTUAL_OFFLOAD_PROVENANCE),
        "inner_resource_lock": _record(INNER_RESOURCE_LOCK),
    }
    payload: dict[str, object] = {
        "schema": "pul7sar-first-genuine-golden-v6-offload-lock-v2",
        "status": "FIRST_GENUINE_GOLDEN_V6_ACTUAL_OFFLOAD_RESOURCE_LOCK_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": "$0-local",
        "model_id": FLUX2_KLEIN_4B_MODEL_ID,
        "safe_offload_preflight_bound": True,
        "actual_offload_mode_bound": True,
        "low_vram_host": offload.get("low_vram_host"),
        "selected_safe_offload_mode": offload.get("selected_safe_mode"),
        "actual_offload_mode": actual_offload.get("actual_offload_mode"),
        "diffusers_version": offload.get("diffusers_version"),
        "actual_offload_provenance": str(ACTUAL_OFFLOAD_PROVENANCE),
        "inner_resource_lock": str(INNER_RESOURCE_LOCK),
        "png": str(png),
        "png_sha256": png_sha,
        "png_bytes": png.stat().st_size,
        "evidence": evidence,
        "human_visual_review_required": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "next_gate": "human Golden visual review at 8.5 minimum / 9.0+ elite target; exact brand/typography and SemanticPublicationGate remain downstream",
    }
    target = _inside_repo(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-model and actual-execution offload-lock the canonical first genuine Golden Editorial v6 Candidate 1")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--output", type=Path, default=FINAL)
    args = parser.parse_args()
    payload = run(force=args.force, output=args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
