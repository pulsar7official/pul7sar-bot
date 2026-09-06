#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from engine.intelligence.qwen_image_runtime_envelope_plan import build_runtime_envelope_plan


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build CPU-only Qwen Image runtime-envelope measurement plan")
    parser.add_argument("admission", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    admission_path = args.admission.resolve()
    admission = json.loads(admission_path.read_text(encoding="utf-8"))
    plan = build_runtime_envelope_plan(admission, admission_file_sha256=sha256_file(admission_path))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(plan["plan_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
