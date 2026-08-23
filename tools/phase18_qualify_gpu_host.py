"""Qualify a host for the first Phase 18 Golden GPU execution.

Usage:
    PYTHONPATH=. python tools/phase18_qualify_gpu_host.py \
      --output output/phase18_gpu_host/qualification.json

The command installs nothing, downloads nothing, and never mutates the queue.
Exit code 0 means the observed host satisfies PUL7SAR's current Golden hardware
policy. Exit code 2 means the host is not proven suitable.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.gpu_host_qualification import GpuHostQualificationPolicy
from engine.intelligence.local_runtime import LocalRuntimeProbe
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


def build_report() -> dict[str, object]:
    runtime = LocalRuntimeProbe().detect()
    qualification = GpuHostQualificationPolicy().evaluate(
        runtime=runtime,
        model=FLUX2_KLEIN_4B_LOCAL,
    )
    report = qualification.as_dict()
    report["policy"] = {
        "queue_mutation": False,
        "downloads_model_weights": False,
        "installs_dependencies": False,
        "uses_paid_api": False,
        "required_dtype": "bfloat16",
        "required_provider": FLUX2_KLEIN_4B_LOCAL.provider_id,
        "required_model": FLUX2_KLEIN_4B_LOCAL.model_id,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = build_report()
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if bool(report["eligible"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
