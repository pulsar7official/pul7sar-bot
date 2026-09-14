#!/usr/bin/env python3
"""Capture a deterministic, zero-cost inventory for approved local model snapshots.

This tool performs no downloads and no model loading. It proves that the exact
Qwen2.5-VL and FLUX.2 snapshot directories selected by the Phase 18 contract are
locally present, non-empty, structurally readable, and resolve only inside the
Hugging Face cache root. The inventory fingerprint is intentionally based on
paths, sizes, and local blob targets so it is fast enough to run before the rare
first-Golden GPU attempt without hashing multi-gigabyte weights end-to-end.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)

EXPECTED_BRANCH = "phase18/story-intelligence"


def _cache_root(env: dict[str, str] | None = None, home: Path | None = None) -> Path:
    values = os.environ if env is None else env
    if values.get("HF_HUB_CACHE"):
        return Path(values["HF_HUB_CACHE"]).expanduser().resolve()
    if values.get("HF_HOME"):
        return (Path(values["HF_HOME"]).expanduser() / "hub").resolve()
    base = Path.home() if home is None else home
    return (base / ".cache" / "huggingface" / "hub").resolve()


def _snapshot_path(cache_root: Path, model_id: str, revision: str) -> Path:
    owner, repo = model_id.split("/", 1)
    return cache_root / f"models--{owner}--{repo}" / "snapshots" / revision


def _sha256_json(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _inside(path: Path, root: Path) -> bool:
    path = path.resolve()
    root = root.resolve()
    return path == root or root in path.parents


def _iter_files(snapshot: Path) -> Iterable[Path]:
    yield from sorted((path for path in snapshot.rglob("*") if path.is_file()), key=lambda p: p.as_posix())


def _inventory_snapshot(*, cache_root: Path, model_id: str, revision: str) -> dict[str, object]:
    snapshot = _snapshot_path(cache_root, model_id, revision)
    blockers: list[str] = []
    files: list[dict[str, object]] = []

    if not snapshot.is_dir():
        blockers.append("SNAPSHOT_DIRECTORY_MISSING")
    else:
        for path in _iter_files(snapshot):
            resolved = path.resolve()
            if not _inside(resolved, cache_root):
                blockers.append("SNAPSHOT_FILE_ESCAPES_CACHE_ROOT")
                continue
            stat = resolved.stat()
            entry: dict[str, object] = {
                "path": path.relative_to(snapshot).as_posix(),
                "size_bytes": int(stat.st_size),
                "is_symlink": path.is_symlink(),
            }
            if path.is_symlink():
                entry["resolved_cache_path"] = resolved.relative_to(cache_root).as_posix()
            files.append(entry)

    if not files:
        blockers.append("SNAPSHOT_FILE_SET_EMPTY")

    total_bytes = sum(int(item["size_bytes"]) for item in files)
    inventory_payload = {
        "model_id": model_id,
        "revision": revision,
        "files": files,
        "total_bytes": total_bytes,
    }
    return {
        "model_id": model_id,
        "revision": revision,
        "snapshot_path": str(snapshot),
        "file_count": len(files),
        "total_bytes": total_bytes,
        "inventory_sha256": _sha256_json(inventory_payload),
        "files": files,
        "ready": not blockers,
        "blockers": sorted(set(blockers)),
    }


def inspect(*, env: dict[str, str] | None = None, home: Path | None = None) -> dict[str, object]:
    values = dict(os.environ if env is None else env)
    blockers: list[str] = []
    if values.get("PUL7SAR_PHASE18_COST_MODE") != "$0-local":
        blockers.append("ZERO_COST_MODE_NOT_ASSERTED")
    if values.get("HF_HUB_OFFLINE") != "1":
        blockers.append("HF_HUB_OFFLINE_NOT_1")
    if values.get("TRANSFORMERS_OFFLINE") != "1":
        blockers.append("TRANSFORMERS_OFFLINE_NOT_1")

    cache_root = _cache_root(values, home)
    qwen = _inventory_snapshot(
        cache_root=cache_root,
        model_id=QWEN25_VL_3B_MODEL_ID,
        revision=QWEN25_VL_3B_REVISION,
    )
    flux = _inventory_snapshot(
        cache_root=cache_root,
        model_id=FLUX2_KLEIN_4B_MODEL_ID,
        revision=FLUX2_KLEIN_4B_REVISION,
    )
    if qwen["ready"] is not True:
        blockers.append("QWEN_APPROVED_SNAPSHOT_INVENTORY_NOT_READY")
    if flux["ready"] is not True:
        blockers.append("FLUX_APPROVED_SNAPSHOT_INVENTORY_NOT_READY")

    combined = {
        "qwen_inventory_sha256": qwen["inventory_sha256"],
        "flux_inventory_sha256": flux["inventory_sha256"],
    }
    return {
        "schema": "pul7sar-phase18-approved-snapshot-inventory-v1",
        "branch_required": EXPECTED_BRANCH,
        "cost_mode": "$0-local",
        "offline_only": True,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "cache_root": str(cache_root),
        "qwen": qwen,
        "flux": flux,
        "combined_inventory_sha256": _sha256_json(combined),
        "ready": not blockers,
        "blockers": sorted(set(blockers)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture approved local Phase 18 model snapshot inventory")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = inspect()
    target = args.output if args.output.is_absolute() else ROOT / args.output
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("SNAPSHOT_INVENTORY_OUTPUT_ESCAPES_REPOSITORY")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if payload["ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
