#!/usr/bin/env python3
"""Build a non-authoritative explicit local-model declaration from a research docket."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.remote_renderer_local_candidate import RemoteRendererExplicitLocalCandidateBuilder


def main() -> int:
    parser = argparse.ArgumentParser(description="Declare an explicit curated local model candidate for a remote renderer research leader")
    parser.add_argument("--qualification-docket", required=True)
    parser.add_argument("--local-model-candidate-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output = Path(args.output).resolve()
    if not output.is_relative_to(repo_root):
        raise SystemExit("REMOTE_LOCAL_CANDIDATE_OUTPUT_PATH_ESCAPE")

    declaration = RemoteRendererExplicitLocalCandidateBuilder(repo_root).build(
        qualification_docket_path=Path(args.qualification_docket),
        local_model_candidate_id=args.local_model_candidate_id,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(declaration, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(declaration, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
