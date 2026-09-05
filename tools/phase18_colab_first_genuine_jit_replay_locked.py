#!/usr/bin/env python3
"""JIT-resource replay lock for the first genuine Golden Editorial v6 Candidate 1.

This wrapper delegates to the existing pre-model/actual-offload locked path, then
replays the strict staging receipt's just-in-time GPU and host-memory evidence.
It binds the outer offload lock, inner resource lock, strict staging receipt and
JIT replay receipt by SHA-256 before Candidate 1 can be described as ready for
human Golden review.

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
OFFLOAD_LOCK = ROOT / "output" / "phase18_gpu_smoke" / "first-genuine-golden-v6-offload-lock.json"
JIT_REPLAY = ROOT / "output" / "phase18_gpu_smoke" / "first-genuine-golden-v6-jit-resource-replay.json"
FINAL = ROOT / "output" / "phase18_gpu_smoke" / "first-genuine-golden-v6-jit-lock.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.golden_jit_resource_replay import verify_golden_jit_resource_replay


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode != 0:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_LOCK_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _inside_repo(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_LOCK_PATH_ESCAPES_REPOSITORY")
    return target


def _load(path: Path) -> dict[str, object]:
    target = _inside_repo(path)
    if not target.is_file():
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_JIT_EVIDENCE_MISSING:{target}")
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_EVIDENCE_INVALID")
    return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record(path: Path) -> dict[str, object]:
    target = _inside_repo(path)
    if not target.is_file():
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_JIT_EVIDENCE_MISSING:{target}")
    return {"path": str(target), "sha256": _sha256(target), "bytes": target.stat().st_size}


def _validate_record(record: object, *, label: str) -> Path:
    if not isinstance(record, dict) or not isinstance(record.get("path"), str):
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_JIT_{label}_RECORD_MISSING")
    path = _inside_repo(Path(str(record["path"])))
    if not path.is_file():
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_JIT_{label}_FILE_MISSING")
    if record.get("sha256") != _sha256(path) or record.get("bytes") != path.stat().st_size:
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_JIT_{label}_REPLAY_DRIFT")
    return path


def _write(path: Path, payload: dict[str, object]) -> None:
    target = _inside_repo(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def run(*, force: bool = False, output: Path = FINAL) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_LOCK_BRANCH_BLOCKED")

    command = [
        sys.executable,
        str(ROOT / "tools" / "phase18_colab_first_genuine_offload_locked.py"),
        "--output",
        str(OFFLOAD_LOCK),
    ]
    if force:
        command.append("--force")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_JIT_INNER_OFFLOAD_LOCK_FAILED:{completed.returncode}")

    outer = _load(OFFLOAD_LOCK)
    if outer.get("schema") != "pul7sar-first-genuine-golden-v6-offload-lock-v2":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_OFFLOAD_SCHEMA_DRIFT")
    if outer.get("status") != "FIRST_GENUINE_GOLDEN_V6_ACTUAL_OFFLOAD_RESOURCE_LOCK_VERIFIED":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_OFFLOAD_NOT_VERIFIED")
    if outer.get("branch") != EXPECTED_BRANCH or outer.get("candidate") != 1 or outer.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_OFFLOAD_IDENTITY_DRIFT")
    if outer.get("safe_offload_preflight_bound") is not True or outer.get("actual_offload_mode_bound") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_OFFLOAD_MODE_NOT_BOUND")
    if outer.get("selected_safe_offload_mode") != outer.get("actual_offload_mode"):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_OFFLOAD_MODE_DRIFT")
    for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
        if outer.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_JIT_OFFLOAD_AUTHORITY_DRIFT:{field}")

    outer_evidence = outer.get("evidence")
    if not isinstance(outer_evidence, dict):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_OFFLOAD_EVIDENCE_MISSING")
    inner_path = _validate_record(outer_evidence.get("inner_resource_lock"), label="INNER_RESOURCE_LOCK")
    inner = _load(inner_path)
    if inner.get("schema") != "pul7sar-first-genuine-golden-v6-resource-lock-v4":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_INNER_SCHEMA_DRIFT")
    if inner.get("candidate") != 1 or inner.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_INNER_IDENTITY_DRIFT")
    for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
        if inner.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_JIT_INNER_AUTHORITY_DRIFT:{field}")

    inner_evidence = inner.get("evidence")
    if not isinstance(inner_evidence, dict):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_INNER_EVIDENCE_MISSING")
    staging_path = _validate_record(inner_evidence.get("strict_golden_staging"), label="STRICT_STAGING")
    if inner.get("staging_receipt") != str(staging_path):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_STAGING_PATH_DRIFT")
    staging = _load(staging_path)

    jit = verify_golden_jit_resource_replay(repository_root=ROOT, staging=staging)
    _write(JIT_REPLAY, jit)

    png_value = outer.get("png")
    if not isinstance(png_value, str) or not png_value.strip():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_PNG_MISSING")
    png = _inside_repo(Path(png_value))
    if not png.is_file() or png.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_PNG_INVALID")
    png_sha = _sha256(png)
    if outer.get("png_sha256") != png_sha or inner.get("png_sha256") != png_sha or staging.get("png_sha256") != png_sha:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_JIT_PNG_BINDING_DRIFT")

    payload: dict[str, object] = {
        "schema": "pul7sar-first-genuine-golden-v6-jit-lock-v1",
        "status": "FIRST_GENUINE_GOLDEN_V6_JIT_RESOURCE_REPLAY_LOCK_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": "$0-local",
        "jit_pre_execution_resource_replay_bound": True,
        "jit_resource_fingerprint_sha256": jit.get("resource_fingerprint_sha256"),
        "selected_safe_offload_mode": outer.get("selected_safe_offload_mode"),
        "actual_offload_mode": outer.get("actual_offload_mode"),
        "png": str(png),
        "png_sha256": png_sha,
        "png_bytes": png.stat().st_size,
        "evidence": {
            "offload_lock": _record(OFFLOAD_LOCK),
            "inner_resource_lock": _record(inner_path),
            "strict_golden_staging": _record(staging_path),
            "jit_resource_replay": _record(JIT_REPLAY),
        },
        "human_visual_review_required": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "next_gate": "human Golden visual review at 8.5 minimum / 9.0+ elite target; exact brand/typography and SemanticPublicationGate remain downstream",
    }
    _write(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="JIT-resource replay lock the first genuine Golden Editorial v6 Candidate 1")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--output", type=Path, default=FINAL)
    args = parser.parse_args()
    payload = run(force=args.force, output=args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
