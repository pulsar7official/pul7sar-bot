#!/usr/bin/env python3
"""Report all pre-model-load blockers for the verified Phase 18 Qwen launch."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.qwen_image_preload_host_diagnostic import inspect_preload_host


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a GPU host without loading Qwen weights")
    parser.add_argument("--launch-manifest", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    report = inspect_preload_host(args.launch_manifest, repo_root=args.repo_root)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    if args.require_ready and not report["ready_for_model_load_attempt"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
