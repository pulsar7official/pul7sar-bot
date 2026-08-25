#!/usr/bin/env python3
"""Canonical Candidate 1 entrypoint with provider-neutral Original Scene admission.

The wrapper proves measured Original Scene runtime admission first, before the
existing first-PNG command is allowed to reach its durable queue. The delegated
first-PNG path retains all repository, CUDA/BF16, Qwen, FLUX, provenance and
publication gates and may not be bypassed by this wrapper.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ADMISSION_SCHEMA = "pul7sar-golden-original-scene-admission-v1"
EXPECTED_ADMISSION_STATUS = "GOLDEN_ORIGINAL_SCENE_RUNTIME_ADMITTED"
EXPECTED_COST_MODE = "$0-local"
EXPECTED_DTYPE = "bfloat16"


def _run_json(command: list[str], *, cwd: Path, label: str) -> dict[str, object]:
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} did not emit valid JSON: " + (completed.stderr or completed.stdout)[-2000:]) from exc
    if completed.returncode != 0:
        raise RuntimeError(f"{label} failed\n" + json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return payload


def _assert_admission(payload: dict[str, object]) -> None:
    failures: list[str] = []
    expected = {
        "schema": EXPECTED_ADMISSION_SCHEMA,
        "status": EXPECTED_ADMISSION_STATUS,
        "candidate": 1,
        "cost_mode": EXPECTED_COST_MODE,
        "resolved_dtype": EXPECTED_DTYPE,
        "runtime_ready": True,
        "semantic_inspection_required": True,
        "generated_branding_allowed": False,
        "generated_exact_facts_allowed": False,
        "generated_sport_geometry_allowed": False,
        "generation_authorized": False,
        "queue_mutated": False,
        "png_created": False,
        "semantic_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            failures.append(f"{key}={payload.get(key)!r}")
    if failures:
        raise RuntimeError("GOLDEN_ORIGINAL_SCENE_ADMISSION_CONTRACT_FAILED: " + "; ".join(failures))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Golden Candidate 1 only after Original Scene runtime admission")
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--batch-dir", default="output/phase18_handoffs/golden-batch")
    parser.add_argument("--admission-receipt", default="output/phase18_gpu_smoke/original-scene-runtime-admission.json")
    args, passthrough = parser.parse_known_args()

    repository_root = Path(args.repository_root).resolve()
    batch_dir = Path(args.batch_dir)
    manifest = batch_dir / "manifest.json"
    if not manifest.is_absolute():
        manifest = repository_root / manifest
    receipt = Path(args.admission_receipt)
    if not receipt.is_absolute():
        receipt = repository_root / receipt

    admission = _run_json(
        [
            sys.executable,
            str(repository_root / "tools" / "phase18_admit_golden_original_scene.py"),
            "--repository-root",
            str(repository_root),
            "--manifest",
            str(manifest),
            "--output",
            str(receipt),
        ],
        cwd=repository_root,
        label="Golden Original Scene runtime admission",
    )
    _assert_admission(admission)

    delegated = _run_json(
        [
            sys.executable,
            str(repository_root / "tools" / "phase18_first_png.py"),
            "--repository-root",
            str(repository_root),
            "--batch-dir",
            str(batch_dir),
            *passthrough,
        ],
        cwd=repository_root,
        label="Canonical first Golden PNG",
    )
    if delegated.get("publication_ready") is not False:
        raise RuntimeError("FIRST_PNG_WRAPPER_MAY_NOT_AUTHORIZE_PUBLICATION")

    payload = {
        "status": "FIRST_GOLDEN_PNG_ORIGINAL_SCENE_PATH_COMPLETE",
        "original_scene_admission": admission,
        "first_png": delegated,
        "original_scene_admission_receipt": str(receipt),
        "semantic_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
