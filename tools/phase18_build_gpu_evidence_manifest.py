#!/usr/bin/env python3
"""Build a tamper-evident manifest for the first real Golden GPU proof."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.golden_evidence_bundle import build_golden_evidence_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Phase 18 Golden GPU evidence manifest")
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--result", default="output/phase18_gpu_smoke/first-png-result.json")
    parser.add_argument("--output", default="output/phase18_gpu_smoke/evidence-manifest.json")
    parser.add_argument("--include", action="append", default=[])
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    result_path = Path(args.result)
    if not result_path.is_absolute():
        result_path = root / result_path
    extra = []
    for value in args.include:
        path = Path(value)
        extra.append(path if path.is_absolute() else root / path)

    manifest = build_golden_evidence_manifest(
        repository_root=root,
        result_path=result_path,
        additional_paths=extra,
    )

    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    output.resolve().relative_to(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
