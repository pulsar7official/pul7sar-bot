#!/usr/bin/env python3
"""Seal and enqueue one measured Dynamic Visual Brain local request.

This is a CPU-only persistence boundary. It never runs FLUX or Qwen and cannot
open Golden or publication gates.
"""
from __future__ import annotations

import argparse
from dataclasses import fields
import json
from pathlib import Path
import subprocess

from engine.intelligence.dynamic_visual_brain_local_admission import DynamicVisualBrainLocalAdmissionReceipt
from engine.intelligence.dynamic_visual_brain_queue_binding import DynamicVisualBrainQueueBindingGate
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff


def _branch() -> str:
    return subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()


def _load_admission(path: Path) -> DynamicVisualBrainLocalAdmissionReceipt:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw.get("admission"), dict):
        raw = raw["admission"]
    expected = {field.name for field in fields(DynamicVisualBrainLocalAdmissionReceipt)}
    if set(raw) != expected:
        missing = sorted(expected - set(raw))
        extra = sorted(set(raw) - expected)
        raise ValueError(f"DYNAMIC_VISUAL_BRAIN_ADMISSION_RECEIPT_FIELDS_INVALID missing={missing} extra={extra}")
    return DynamicVisualBrainLocalAdmissionReceipt(**raw)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bind a measured Dynamic Visual Brain request to the durable Phase 18 queue")
    parser.add_argument("--request-handoff", required=True, help="Existing SHA-protected local request handoff")
    parser.add_argument("--admission", required=True, help="DynamicVisualBrainLocalAdmissionReceipt JSON")
    parser.add_argument("--sealed-handoff", default="output/phase18_dynamic_visual_brain/durable-request.json")
    parser.add_argument("--queue-root", default="output/phase18_generation_queue")
    parser.add_argument("--receipt", default="output/phase18_dynamic_visual_brain/queue-binding.json")
    parser.add_argument("--job-id")
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()

    branch = _branch()
    request = LocalGenerationHandoff.read(args.request_handoff)
    admission = _load_admission(Path(args.admission))
    _, receipt = DynamicVisualBrainQueueBindingGate.bind_and_enqueue(
        branch=branch,
        request=request,
        admission=admission,
        handoff_path=args.sealed_handoff,
        queue_root=args.queue_root,
        repository_root=Path.cwd(),
        job_id=args.job_id,
        max_attempts=args.max_attempts,
    )

    target = Path(args.receipt)
    resolved = target.resolve() if target.is_absolute() else (Path.cwd() / target).resolve()
    try:
        resolved.relative_to(Path.cwd().resolve())
    except ValueError as exc:
        raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_RECEIPT_OUTSIDE_REPOSITORY") from exc
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
