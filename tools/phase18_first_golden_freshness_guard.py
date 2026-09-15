#!/usr/bin/env python3
"""Capture/replay mutable first-Golden artifacts to reject stale-success evidence.

This tool is CPU-safe and performs no generation, model loading, network access,
publication, or queue mutation. A pre-attempt baseline can be captured before a
GPU attempt. A post-attempt verification then proves that every mutable receipt
required for Candidate 1 was created or changed relative to that baseline, and
that the staging/resource-lock receipts agree on the same valid PNG bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
BASELINE_SCHEMA = "pul7sar-phase18-first-golden-freshness-baseline-v1"
VERIFY_SCHEMA = "pul7sar-phase18-first-golden-freshness-verification-v1"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

LATEST = Path("output/phase18_colab/latest.json")
SEMANTIC = Path("output/phase18_visual_proof/editorial/candidate-01-golden-editorial-v6-receipt.json")
STAGING = Path("output/phase18_visual_proof/editorial/candidate-01-first-genuine-golden-staging.json")
RESOURCE_LOCK = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-resource-lock.json")
MUTABLE = {
    "generation_summary": LATEST,
    "semantic_receipt": SEMANTIC,
    "staging_receipt": STAGING,
    "resource_lock": RESOURCE_LOCK,
}


def _inside_repo(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FIRST_GOLDEN_FRESHNESS_PATH_ESCAPES_REPOSITORY")
    return target


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _record(path: Path) -> dict[str, Any]:
    target = _inside_repo(path)
    if not target.is_file():
        return {"path": str(target), "exists": False, "sha256": None, "bytes": None, "mtime_ns": None}
    stat = target.stat()
    return {
        "path": str(target),
        "exists": True,
        "sha256": _sha256(target),
        "bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def _closed_authorities() -> dict[str, bool]:
    return {
        "generation_authorized": False,
        "network_download_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def capture() -> dict[str, Any]:
    return {
        "schema": BASELINE_SCHEMA,
        "branch_required": EXPECTED_BRANCH,
        "cost_mode_required": "$0-local",
        "offline_required": True,
        "artifacts": {label: _record(path) for label, path in MUTABLE.items()},
        **_closed_authorities(),
    }


def _load_json(path: Path) -> dict[str, Any]:
    target = _inside_repo(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("FIRST_GOLDEN_FRESHNESS_INVALID_JSON_PAYLOAD")
    return payload


def _changed(before: dict[str, Any], after: dict[str, Any]) -> bool:
    if before.get("exists") is not True:
        return after.get("exists") is True
    if after.get("exists") is not True:
        return False
    return (
        before.get("sha256") != after.get("sha256")
        or before.get("bytes") != after.get("bytes")
        or before.get("mtime_ns") != after.get("mtime_ns")
    )


def verify(baseline: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    if baseline.get("schema") != BASELINE_SCHEMA:
        blockers.append("FRESHNESS_BASELINE_SCHEMA_DRIFT")
    if baseline.get("branch_required") != EXPECTED_BRANCH:
        blockers.append("FRESHNESS_BASELINE_BRANCH_DRIFT")
    if baseline.get("cost_mode_required") != "$0-local" or baseline.get("offline_required") is not True:
        blockers.append("FRESHNESS_BASELINE_POLICY_DRIFT")
    for field in _closed_authorities():
        if baseline.get(field) is not False:
            blockers.append(f"FRESHNESS_BASELINE_AUTHORITY_DRIFT_{field.upper()}")

    before = baseline.get("artifacts")
    if not isinstance(before, dict):
        before = {}
        blockers.append("FRESHNESS_BASELINE_ARTIFACTS_MISSING")

    after = {label: _record(path) for label, path in MUTABLE.items()}
    changed: dict[str, bool] = {}
    for label in MUTABLE:
        prior = before.get(label)
        if not isinstance(prior, dict):
            changed[label] = False
            blockers.append(f"FRESHNESS_BASELINE_RECORD_MISSING_{label.upper()}")
            continue
        changed[label] = _changed(prior, after[label])
        if after[label].get("exists") is not True:
            blockers.append(f"FRESHNESS_POST_ARTIFACT_MISSING_{label.upper()}")
        elif not changed[label]:
            blockers.append(f"FRESHNESS_POST_ARTIFACT_STALE_{label.upper()}")

    png_path: str | None = None
    png_sha: str | None = None
    if after["staging_receipt"].get("exists") is True and after["resource_lock"].get("exists") is True:
        try:
            staging = _load_json(STAGING)
            resource = _load_json(RESOURCE_LOCK)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, RuntimeError):
            blockers.append("FRESHNESS_POST_RECEIPT_INVALID_JSON")
        else:
            staging_png = staging.get("png")
            resource_png = resource.get("png")
            if not isinstance(staging_png, str) or not staging_png.strip():
                blockers.append("FRESHNESS_STAGING_PNG_PATH_MISSING")
            elif staging_png != resource_png:
                blockers.append("FRESHNESS_PNG_PATH_DRIFT")
            else:
                try:
                    target = _inside_repo(Path(staging_png))
                except RuntimeError:
                    blockers.append("FRESHNESS_PNG_PATH_INVALID")
                else:
                    if not target.is_file():
                        blockers.append("FRESHNESS_PNG_MISSING")
                    else:
                        with target.open("rb") as handle:
                            if handle.read(8) != PNG_SIGNATURE:
                                blockers.append("FRESHNESS_PNG_SIGNATURE_INVALID")
                        actual_sha = _sha256(target)
                        if staging.get("png_sha256") != actual_sha or resource.get("png_sha256") != actual_sha:
                            blockers.append("FRESHNESS_PNG_SHA_DRIFT")
                        else:
                            png_path = str(target)
                            png_sha = actual_sha

    return {
        "schema": VERIFY_SCHEMA,
        "branch_required": EXPECTED_BRANCH,
        "cost_mode_required": "$0-local",
        "offline_required": True,
        "artifacts_after": after,
        "artifacts_changed": changed,
        "png": png_path,
        "png_sha256": png_sha,
        "fresh_attempt_evidence": not blockers,
        "blockers": blockers,
        **_closed_authorities(),
    }


def _write(path: Path, payload: dict[str, Any]) -> None:
    target = _inside_repo(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture or replay freshness of mutable first-Golden Candidate 1 evidence")
    sub = parser.add_subparsers(dest="command", required=True)
    capture_parser = sub.add_parser("capture")
    capture_parser.add_argument("--output", type=Path, required=True)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--baseline", type=Path, required=True)
    verify_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "capture":
        payload = capture()
        _write(args.output, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    baseline = _load_json(args.baseline)
    payload = verify(baseline)
    _write(args.output, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["fresh_attempt_evidence"] is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
