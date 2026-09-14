#!/usr/bin/env python3
"""Capture fail-closed evidence that Phase 18 $0-local network isolation is active.

This probe performs only synthetic connection attempts that the process-local guard
must reject before DNS or socket I/O occurs. It never requires external network
access and does not weaken the existing offline/model/cache gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
from typing import Callable

from engine.intelligence import zero_cost_network_guard as guard

SCHEMA = "pul7sar-phase18-zero-cost-network-guard-evidence-v1"
BLOCK_MARKER = "PUL7SAR_PHASE18_ZERO_COST_NETWORK_BLOCKED"
EXPECTED_BRANCH = "phase18/story-intelligence"


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def _expect_blocked(name: str, action: Callable[[], object]) -> dict[str, object]:
    try:
        action()
    except PermissionError as exc:
        message = str(exc)
        if BLOCK_MARKER not in message:
            raise SystemExit(f"{name}: wrong PermissionError: {message}") from exc
        return {"name": name, "blocked": True, "marker": BLOCK_MARKER}
    except Exception as exc:  # pragma: no cover - fail closed with exact diagnostic
        raise SystemExit(f"{name}: unexpected exception {type(exc).__name__}: {exc}") from exc
    raise SystemExit(f"{name}: external network path was not blocked")


def capture() -> dict[str, object]:
    if os.environ.get("PUL7SAR_PHASE18_COST_MODE") != "$0-local":
        raise SystemExit("zero-cost guard evidence requires PUL7SAR_PHASE18_COST_MODE=$0-local")
    if os.environ.get("HF_HUB_OFFLINE") != "1" or os.environ.get("TRANSFORMERS_OFFLINE") != "1":
        raise SystemExit("zero-cost guard evidence requires both offline flags")
    if not guard.contract_requests_guard():
        raise SystemExit("zero-cost guard contract is not active")
    if not guard.guard_active():
        raise SystemExit("sitecustomize did not activate the zero-cost network guard")
    if os.environ.get("PUL7SAR_PHASE18_NETWORK_GUARD_ACTIVE") != "1":
        raise SystemExit("zero-cost network guard activation marker is missing")

    branch = _git("branch", "--show-current")
    source_sha = _git("rev-parse", "HEAD")
    if branch != EXPECTED_BRANCH:
        raise SystemExit(f"unexpected branch for Golden execution: {branch}")
    if len(source_sha) != 40 or any(ch not in "0123456789abcdef" for ch in source_sha):
        raise SystemExit("invalid source commit SHA")

    checks: list[dict[str, object]] = []
    checks.append(
        _expect_blocked(
            "socket.connect_ipv4",
            lambda: socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("198.51.100.1", 443)),
        )
    )
    checks.append(
        _expect_blocked(
            "socket.connect_ex_ipv4",
            lambda: socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(("198.51.100.1", 443)),
        )
    )
    checks.append(
        _expect_blocked(
            "socket.create_connection",
            lambda: socket.create_connection(("198.51.100.1", 443), timeout=0.01),
        )
    )
    checks.append(
        _expect_blocked(
            "socket.getaddrinfo_external_dns",
            lambda: socket.getaddrinfo("example.invalid", 443),
        )
    )

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "ready": True,
        "source_branch": branch,
        "source_sha": source_sha,
        "cost_mode": "$0-local",
        "hf_hub_offline": True,
        "transformers_offline": True,
        "sitecustomize_guard_active": True,
        "network_download_authorized": False,
        "external_network_paths_blocked": True,
        "synthetic_checks": checks,
        "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    payload["evidence_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    payload = capture()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
