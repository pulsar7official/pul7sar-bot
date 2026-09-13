#!/usr/bin/env python3
"""Build a byte-bound, non-canonical renderer research ledger."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.remote_renderer_research_ledger import RemoteRendererResearchLedgerBuilder


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Phase 18 remote renderer research ledger")
    parser.add_argument("--benchmark-report", required=True)
    parser.add_argument("--human-review", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    builder = RemoteRendererResearchLedgerBuilder(repo_root=ROOT)
    payload = builder.build(
        benchmark_report_path=Path(args.benchmark_report),
        human_review_path=Path(args.human_review),
    )
    output = Path(args.output).resolve()
    if not output.is_relative_to(ROOT.resolve()):
        raise ValueError(f"REMOTE_RESEARCH_PATH_ESCAPE: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
