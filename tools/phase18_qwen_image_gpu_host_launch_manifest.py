#!/usr/bin/env python3
"""Build or verify the CS291 pre-inference GPU-host launch manifest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.qwen_image_gpu_host_launch_manifest import (
    build_gpu_host_launch_manifest,
    verify_gpu_host_launch_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build/verify a zero-cost local Qwen GPU-host launch manifest")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--authorization", type=Path, required=True)
    build.add_argument("--cs257-run-dir", type=Path, required=True)
    build.add_argument("--snapshot-path", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--repo-root", type=Path, default=ROOT)
    build.add_argument("--width", type=int, default=1024)
    build.add_argument("--height", type=int, default=1024)
    build.add_argument("--steps", type=int, default=8)
    build.add_argument("--guidance-scale", type=float, default=1.0)
    build.add_argument("--seed", type=int, required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--repo-root", type=Path, default=ROOT)

    args = parser.parse_args()
    root = args.repo_root.resolve()
    if args.command == "build":
        payload = build_gpu_host_launch_manifest(
            args.authorization, args.cs257_run_dir, args.snapshot_path, args.output,
            repo_root=root, width=args.width, height=args.height, seed=args.seed,
            num_inference_steps=args.steps, guidance_scale=args.guidance_scale,
        )
    else:
        payload = verify_gpu_host_launch_manifest(args.manifest, repo_root=root)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
