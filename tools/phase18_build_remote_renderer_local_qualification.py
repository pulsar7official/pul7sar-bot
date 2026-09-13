#!/usr/bin/env python3
"""Build a non-authoritative local qualification docket from remote renderer research."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.remote_renderer_local_qualification import (
    RemoteRendererLocalQualificationDocketBuilder,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert a byte-bound remote research leader into a local-qualification docket only"
    )
    parser.add_argument("--research-ledger", required=True)
    parser.add_argument(
        "--output",
        default="output/phase18_remote_renderer/local-qualification-docket.json",
    )
    args = parser.parse_args()

    repo_root = Path.cwd().resolve()
    output = Path(args.output).resolve()
    if not output.is_relative_to(repo_root):
        raise ValueError(f"REMOTE_LOCAL_QUALIFICATION_PATH_ESCAPE: {output}")

    docket = RemoteRendererLocalQualificationDocketBuilder(repo_root).build(
        research_ledger_path=Path(args.research_ledger),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(docket, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(docket, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
