#!/usr/bin/env python3
"""Emit the CPU-only Phase 18 pre-GPU repository-integrity receipt."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.pre_gpu_repository_integrity import PreGpuRepositoryIntegrityGate


def _branch(repository_root: Path) -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repository_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to resolve current git branch")
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 18 CPU repository integrity before GPU work")
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--output", default="output/phase18_gpu_smoke/repository-integrity.json")
    args = parser.parse_args()

    repository_root = Path(args.repository_root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = repository_root / output

    receipt = PreGpuRepositoryIntegrityGate().inspect(
        repository_root=repository_root,
        branch=_branch(repository_root),
    )
    payload = receipt.to_dict()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt.ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
