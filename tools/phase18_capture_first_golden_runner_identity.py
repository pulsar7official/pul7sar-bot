#!/usr/bin/env python3
"""Capture immutable, non-secret runner/CUDA identity evidence for First Genuine Golden v6.

This tool is local-only and fail-closed. It does not generate images, load model
weights, access the network, approve Human Review, publish, or mutate any queue.
It records the GitHub Actions runner identity and CUDA device facts that can be
bound into the final Golden evidence manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
from typing import Any

SCHEMA = "pul7sar-phase18-first-golden-runner-identity-v1"
EXPECTED_REPOSITORY = "pulsar7official/pul7sar-bot"
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def capture() -> dict[str, Any]:
    import torch

    runner_name = os.environ.get("RUNNER_NAME", "").strip()
    runner_os = os.environ.get("RUNNER_OS", "").strip()
    runner_arch = os.environ.get("RUNNER_ARCH", "").strip()
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    ref_name = os.environ.get("GITHUB_REF_NAME", "").strip()
    sha = os.environ.get("GITHUB_SHA", "").strip()
    run_id = os.environ.get("GITHUB_RUN_ID", "").strip()
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "").strip()
    job = os.environ.get("GITHUB_JOB", "").strip()

    blockers: list[str] = []
    if not runner_name:
        blockers.append("RUNNER_NAME_MISSING")
    if runner_os != "Linux":
        blockers.append("RUNNER_OS_NOT_LINUX")
    if runner_arch != "X64":
        blockers.append("RUNNER_ARCH_NOT_X64")
    if repository != EXPECTED_REPOSITORY:
        blockers.append("REPOSITORY_IDENTITY_DRIFT")
    if ref_name != EXPECTED_BRANCH:
        blockers.append("BRANCH_IDENTITY_DRIFT")
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        blockers.append("SOURCE_SHA_INVALID")
    if not run_id:
        blockers.append("GITHUB_RUN_ID_MISSING")
    if not run_attempt:
        blockers.append("GITHUB_RUN_ATTEMPT_MISSING")
    if os.environ.get("PUL7SAR_PHASE18_COST_MODE") != EXPECTED_COST_MODE:
        blockers.append("COST_MODE_DRIFT")
    if os.environ.get("HF_HUB_OFFLINE") != "1" or os.environ.get("TRANSFORMERS_OFFLINE") != "1":
        blockers.append("OFFLINE_MODE_DRIFT")

    cuda_available = bool(torch.cuda.is_available())
    cuda_runtime = torch.version.cuda
    device_count = int(torch.cuda.device_count()) if cuda_available else 0
    native_bf16 = bool(torch.cuda.is_bf16_supported()) if cuda_available else False
    if not cuda_available or not cuda_runtime or device_count < 1:
        blockers.append("CUDA_RUNTIME_UNAVAILABLE")
    if not native_bf16:
        blockers.append("NATIVE_BF16_UNAVAILABLE")

    devices: list[dict[str, Any]] = []
    if cuda_available:
        for index in range(device_count):
            props = torch.cuda.get_device_properties(index)
            devices.append(
                {
                    "index": index,
                    "name": props.name,
                    "name_sha256": _sha256_text(props.name),
                    "compute_capability": [int(props.major), int(props.minor)],
                    "total_memory_bytes": int(props.total_memory),
                    "multi_processor_count": int(props.multi_processor_count),
                }
            )

    return {
        "schema": SCHEMA,
        "repository": repository,
        "branch": ref_name,
        "source_commit_sha": sha,
        "workflow_run_id": run_id,
        "workflow_run_attempt": run_attempt,
        "github_job": job,
        "runner": {
            "name_sha256": _sha256_text(runner_name) if runner_name else None,
            "os": runner_os,
            "arch": runner_arch,
            "python_platform": platform.platform(),
            "python_machine": platform.machine(),
        },
        "runtime": {
            "torch_version": torch.__version__,
            "cuda_available": cuda_available,
            "cuda_runtime": cuda_runtime,
            "cuda_device_count": device_count,
            "native_bf16": native_bf16,
            "devices": devices,
        },
        "cost_mode": EXPECTED_COST_MODE,
        "offline_only": True,
        "blockers": blockers,
        "runner_identity_verified": blockers == [],
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = capture()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_name(args.output.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(args.output)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["blockers"]:
        raise SystemExit(";".join(payload["blockers"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
