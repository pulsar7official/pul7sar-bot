#!/usr/bin/env python3
"""Replay a Phase 18 Golden GPU evidence manifest and fail closed on drift."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.golden_evidence_bundle import verify_golden_evidence_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 18 Golden GPU evidence manifest")
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--manifest", default="output/phase18_gpu_smoke/evidence-manifest.json")
    parser.add_argument("--receipt", default="output/phase18_gpu_smoke/evidence-verification.json")
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    manifest_path = manifest_path.resolve()
    manifest_path.relative_to(root)
    if not manifest_path.is_file():
        raise FileNotFoundError(f"evidence manifest is missing: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    verification = verify_golden_evidence_manifest(
        repository_root=root,
        manifest=manifest,
    )

    receipt = Path(args.receipt)
    if not receipt.is_absolute():
        receipt = root / receipt
    receipt = receipt.resolve()
    receipt.relative_to(root)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(verification, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(verification, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
