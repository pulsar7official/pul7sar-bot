#!/usr/bin/env python3
"""Fail-closed verifier for Phase 18 local-only Qwen and FLUX cache receipts.

This module is intentionally CPU-safe and network-free. It verifies that both
approved model-cache receipts prove exact immutable model identity, canonical
snapshot revision binding, $0-local execution, no runtime download, no network
download authorization, and local-files-only resolution. It never performs
model loading, inference, generation, publication, or queue mutation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
    assert_snapshot_revision,
)


QWEN_SCHEMA = "pul7sar-phase18-qwen-model-cache-v2"
FLUX_SCHEMA = "pul7sar-phase18-model-cache-v2"
STATUS = "PHASE18_LOCAL_ONLY_MODEL_RECEIPTS_VERIFIED"


def _load_receipt(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("PHASE18_MODEL_RECEIPT_INVALID")
    return payload


def _verify_common_local_only_contract(payload: dict[str, object], *, label: str) -> None:
    if payload.get("ready") is not True:
        raise RuntimeError(f"{label}_CACHE_NOT_READY")
    if payload.get("revision_pinned") is not True:
        raise RuntimeError(f"{label}_REVISION_NOT_PINNED")
    if payload.get("cost_mode") != "$0-local":
        raise RuntimeError(f"{label}_COST_MODE_DRIFT")
    if payload.get("downloaded_now") is not False:
        raise RuntimeError(f"{label}_RUNTIME_DOWNLOAD_DETECTED")
    if payload.get("network_download_authorized") is not False:
        raise RuntimeError(f"{label}_NETWORK_DOWNLOAD_AUTHORITY_DRIFT")
    if payload.get("local_files_only") is not True:
        raise RuntimeError(f"{label}_LOCAL_FILES_ONLY_UNPROVEN")


def verify_qwen_receipt(payload: dict[str, object]) -> dict[str, object]:
    if payload.get("schema") != QWEN_SCHEMA:
        raise RuntimeError("QWEN_CACHE_SCHEMA_DRIFT")
    _verify_common_local_only_contract(payload, label="QWEN")
    if payload.get("model_id") != QWEN25_VL_3B_MODEL_ID:
        raise RuntimeError("QWEN_MODEL_ID_DRIFT")
    if payload.get("model_revision") != QWEN25_VL_3B_REVISION:
        raise RuntimeError("QWEN_MODEL_REVISION_DRIFT")
    if payload.get("resolved_snapshot_revision") != QWEN25_VL_3B_REVISION:
        raise RuntimeError("QWEN_RESOLVED_REVISION_DRIFT")
    snapshot = payload.get("snapshot_path")
    if not isinstance(snapshot, str) or not snapshot.strip():
        raise RuntimeError("QWEN_SNAPSHOT_PATH_MISSING")
    try:
        assert_snapshot_revision(snapshot, QWEN25_VL_3B_REVISION)
    except (RuntimeError, ValueError) as exc:
        raise RuntimeError("QWEN_SNAPSHOT_PATH_REVISION_DRIFT") from exc
    return payload


def verify_flux_receipt(payload: dict[str, object]) -> dict[str, object]:
    if payload.get("schema") != FLUX_SCHEMA:
        raise RuntimeError("FLUX_CACHE_SCHEMA_DRIFT")
    _verify_common_local_only_contract(payload, label="FLUX")
    if payload.get("model_id") != FLUX2_KLEIN_4B_MODEL_ID:
        raise RuntimeError("FLUX_MODEL_ID_DRIFT")
    if payload.get("model_revision") != FLUX2_KLEIN_4B_REVISION:
        raise RuntimeError("FLUX_MODEL_REVISION_DRIFT")
    if payload.get("resolved_snapshot_revision") != FLUX2_KLEIN_4B_REVISION:
        raise RuntimeError("FLUX_RESOLVED_REVISION_DRIFT")
    snapshot = payload.get("snapshot_path")
    if not isinstance(snapshot, str) or not snapshot.strip():
        raise RuntimeError("FLUX_SNAPSHOT_PATH_MISSING")
    try:
        assert_snapshot_revision(snapshot, FLUX2_KLEIN_4B_REVISION)
    except (RuntimeError, ValueError) as exc:
        raise RuntimeError("FLUX_SNAPSHOT_PATH_REVISION_DRIFT") from exc
    return payload


def verify_receipts(qwen_receipt: Path, flux_receipt: Path) -> dict[str, object]:
    qwen = verify_qwen_receipt(_load_receipt(qwen_receipt))
    flux = verify_flux_receipt(_load_receipt(flux_receipt))
    return {
        "schema": "pul7sar-phase18-local-only-model-receipt-verification-v1",
        "status": STATUS,
        "cost_mode": "$0-local",
        "network_download_authorized": False,
        "local_files_only": True,
        "qwen_model_id": qwen["model_id"],
        "qwen_model_revision": qwen["model_revision"],
        "flux_model_id": flux["model_id"],
        "flux_model_revision": flux["model_revision"],
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 18 Qwen/FLUX cache receipts are immutable and local-only")
    parser.add_argument("qwen_receipt", type=Path)
    parser.add_argument("flux_receipt", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = verify_receipts(args.qwen_receipt, args.flux_receipt)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
