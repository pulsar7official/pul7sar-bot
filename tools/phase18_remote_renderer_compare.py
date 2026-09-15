#!/usr/bin/env python3
"""Compare remote ZeroGPU renderers as a non-canonical Phase 18 engineering study.

This tool is deliberately isolated from the canonical `$0-local` Golden path.
It may call public Hugging Face ZeroGPU Spaces to compare renderer quality, but
its outputs can never authorize Semantic approval, Golden approval, or
publication. Branding, typography, verified identity, exact facts, and exact
sport geometry remain outside the renderer. Remote benchmark prompts must also
stay entity-neutral: they may study visual quality, but they may not smuggle a
real club, venue, or color-coded entity identity into the renderer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
from typing import Any


SCHEMA = "pul7sar-phase18-remote-renderer-benchmark-v3"
COST_MODE = "$0-remote-zerogpu-study"
PLATFORM_TOKENS = ("PUL7SAR", "PULSAR")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ENTITY_NEUTRAL_MARKER = "no identifiable real club or venue cues"
# These fragments encode the known real-club/venue identity hints that existed
# in the current transfer renderer study. This lane is intentionally anonymous;
# verified entity identity belongs to canonical verified-asset paths instead.
FORBIDDEN_ENTITY_CUES = (
    "north london",
    "tottenham",
    "spurs",
    "manchester city",
    "man city",
    "deep navy and clean white destination atmosphere",
    "cool sky-blue traces",
)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _validate_prompt(prompt: str) -> str:
    value = prompt.strip()
    if not value:
        raise ValueError("prompt file is empty")
    upper = value.upper()
    leaked = [token for token in PLATFORM_TOKENS if token in upper]
    if leaked:
        raise ValueError(f"REMOTE_RENDERER_PLATFORM_NAME_LEAK: {', '.join(leaked)}")

    lowered = value.lower()
    entity_cues = [cue for cue in FORBIDDEN_ENTITY_CUES if cue in lowered]
    if entity_cues:
        raise ValueError(f"REMOTE_RENDERER_ENTITY_CUE_LEAK: {entity_cues}")

    required_markers = (
        "identity must remain non-recognizable",
        "one continuous physical scene only",
        "no readable text",
        "no club crest",
        "no sponsor mark",
        ENTITY_NEUTRAL_MARKER,
    )
    missing = [marker for marker in required_markers if marker not in lowered]
    if missing:
        raise ValueError(f"REMOTE_RENDERER_SAFETY_MARKER_MISSING: {missing}")
    return value


def _client(space: str):
    from gradio_client import Client

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    kwargs = {"hf_token": token} if token else {}
    return Client(space, **kwargs)


def _copy_result(result: Any, target: Path) -> dict[str, Any]:
    """Persist one returned image and prove that the resulting bytes are PNG."""
    candidate = result
    if isinstance(candidate, (tuple, list)) and candidate:
        candidate = candidate[0]
    if isinstance(candidate, dict):
        candidate = candidate.get("path") or candidate.get("name") or candidate.get("url")
    if hasattr(candidate, "name"):
        candidate = candidate.name
    if not isinstance(candidate, str):
        raise RuntimeError(f"unsupported Gradio image result type: {type(candidate)!r}")
    source = Path(candidate)
    if not source.is_file():
        raise FileNotFoundError(f"Gradio result file not found: {candidate}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    payload = target.read_bytes()
    if not payload.startswith(PNG_SIGNATURE):
        raise RuntimeError("REMOTE_RENDERER_OUTPUT_NOT_PNG")
    return {
        "output": str(target.resolve()),
        "output_sha256": _sha256_bytes(payload),
        "output_bytes": len(payload),
    }


def _report(*, renderer: str, space: str, output_evidence: dict[str, Any], seed: int,
            prompt_sha256: str, elapsed_seconds: float) -> dict[str, Any]:
    return {
        "renderer": renderer,
        "space": space,
        **output_evidence,
        "seed": seed,
        "prompt_sha256": prompt_sha256,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "cost_mode": COST_MODE,
        "entity_neutral_benchmark": True,
        "verified_identity_asset_used": False,
        "verified_venue_asset_used": False,
        "engineering_benchmark_only": True,
        "canonical_golden_eligible": False,
        "semantic_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }


def render_qwen(*, prompt: str, output: Path, seed: int, prompt_sha256: str) -> dict[str, Any]:
    client = _client("Qwen/Qwen-Image-2512")
    started = time.monotonic()
    result = client.predict(
        prompt,
        seed,
        False,
        "3:4",
        4.0,
        40,
        True,
        api_name="/infer",
    )
    evidence = _copy_result(result, output)
    return _report(
        renderer="qwen-image-2512",
        space="Qwen/Qwen-Image-2512",
        output_evidence=evidence,
        seed=seed,
        prompt_sha256=prompt_sha256,
        elapsed_seconds=time.monotonic() - started,
    )


def render_flux2_dev(*, prompt: str, output: Path, seed: int, prompt_sha256: str) -> dict[str, Any]:
    client = _client("black-forest-labs/FLUX.2-dev")
    started = time.monotonic()
    result = client.predict(
        prompt,
        None,
        seed,
        False,
        768,
        1024,
        30,
        4.0,
        True,
        api_name="/infer",
    )
    evidence = _copy_result(result, output)
    return _report(
        renderer="flux2-dev",
        space="black-forest-labs/FLUX.2-dev",
        output_evidence=evidence,
        seed=seed,
        prompt_sha256=prompt_sha256,
        elapsed_seconds=time.monotonic() - started,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Qwen Image 2512 vs FLUX.2 dev ZeroGPU")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--seed", type=int, default=1902001)
    args = parser.parse_args()

    prompt_path = Path(args.prompt_file)
    prompt = _validate_prompt(prompt_path.read_text(encoding="utf-8"))
    prompt_sha256 = _sha256_text(prompt)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    jobs = (
        ("qwen-image-2512", render_qwen, output_dir / "qwen-image-2512.png"),
        ("flux2-dev", render_flux2_dev, output_dir / "flux2-dev.png"),
    )
    for name, fn, output in jobs:
        print(f"\n=== {name} ===", flush=True)
        try:
            report = fn(
                prompt=prompt,
                output=output,
                seed=args.seed,
                prompt_sha256=prompt_sha256,
            )
            reports.append(report)
            print(json.dumps(report, indent=2), flush=True)
        except Exception as exc:
            failure = {"renderer": name, "error": f"{type(exc).__name__}: {exc}"}
            failures.append(failure)
            print(json.dumps(failure, indent=2), flush=True)

    payload = {
        "schema": SCHEMA,
        "status": "REMOTE_RENDERER_ENGINEERING_BENCHMARK_COMPLETE" if reports else "REMOTE_RENDERER_ENGINEERING_BENCHMARK_FAILED",
        "prompt_file": str(prompt_path.resolve()),
        "prompt_sha256": prompt_sha256,
        "successful": reports,
        "failures": failures,
        "cost_mode": COST_MODE,
        "paid_provider_configured": False,
        "entity_neutral_benchmark": True,
        "verified_identity_asset_used": False,
        "verified_venue_asset_used": False,
        "engineering_benchmark_only": True,
        "canonical_golden_eligible": False,
        "semantic_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "human_visual_review_required": True,
    }
    result_path = Path(args.result)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + json.dumps(payload, indent=2, ensure_ascii=False), flush=True)
    return 0 if reports else 1


if __name__ == "__main__":
    raise SystemExit(main())
