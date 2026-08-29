#!/usr/bin/env python3
"""Run one genuine, story-authorized Qwen Image 2512 canonical inference attempt.

The production entry point accepts no free-form prompt. Prompt bytes are derived
inside this command from the exact CS257 evidence set that passed independent semantic
replay, then cross-bound to the same CS261 generation authorization. This preserves
Fact Lock, entity identity, sentiment neutrality, semantic ownership, and zero-cost
boundaries at the final inference edge.

There is no retry loop. A claimed authorization is burned even when inference or PNG
validation fails. A successful result is only a canonical candidate; all downstream
quality and publication gates remain closed.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _repo_file(path: Path, repo_root: Path, code: str) -> Path:
    candidate = path if path.is_absolute() else repo_root / path
    if candidate.is_symlink():
        raise RuntimeError(code)
    resolved = candidate.resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise RuntimeError(code) from exc
    if not resolved.is_file():
        raise RuntimeError(code)
    return resolved


def _repo_dir(path: Path, repo_root: Path, code: str) -> Path:
    candidate = path if path.is_absolute() else repo_root / path
    if candidate.is_symlink():
        raise RuntimeError(code)
    resolved = candidate.resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise RuntimeError(code) from exc
    if not resolved.is_dir():
        raise RuntimeError(code)
    return resolved


def _repo_output(path: Path, repo_root: Path) -> Path:
    candidate = path if path.is_absolute() else repo_root / path
    if candidate.exists():
        raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_OUTPUT_ALREADY_EXISTS")
    resolved_parent = candidate.parent.resolve()
    try:
        resolved_parent.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_OUTPUT_OUTSIDE_REPOSITORY") from exc
    if not resolved_parent.is_dir():
        raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_OUTPUT_PARENT_INVALID")
    return resolved_parent / candidate.name


def _load_cs260_from_authorization(
    authorization_path: Path, repo_root: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    from engine.intelligence.qwen_image_story_bound_generation_authorization import (
        verify_live_pipeline_receipt,
        verify_story_bound_generation_authorization,
    )

    authorization = verify_story_bound_generation_authorization(
        authorization_path, repo_root=repo_root
    )
    source = authorization.get("source_live_pipeline_recheck")
    if not isinstance(source, Mapping):
        raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_CS260_BINDING_INVALID")
    relative = source.get("repository_relative_path")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_CS260_PATH_INVALID")
    cs260_path = _repo_file(
        repo_root / relative,
        repo_root,
        "QWEN_CANONICAL_INFERENCE_CLI_CS260_OUTSIDE_REPOSITORY",
    )
    cs260 = verify_live_pipeline_receipt(cs260_path, repo_root=repo_root)
    return authorization, cs260


def _collect_live_pipeline(cs260: Mapping[str, Any]):
    try:
        import torch
        import diffusers
        from diffusers import QwenImagePipeline
    except Exception as exc:  # pragma: no cover - GPU-host dependent
        raise RuntimeError(
            f"QWEN_CANONICAL_INFERENCE_CLI_SOFTWARE_IMPORT_FAILED:{type(exc).__name__}"
        ) from exc

    from engine.intelligence.approved_model_revisions import (
        QWEN_IMAGE_2512_MODEL_ID,
        QWEN_IMAGE_2512_REVISION,
    )
    from engine.intelligence.qwen_image_runtime_envelope_plan import DTYPE, OFFLOAD_MODE

    if not torch.cuda.is_available():
        raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_CUDA_UNAVAILABLE")
    if not hasattr(torch.cuda, "is_bf16_supported") or not torch.cuda.is_bf16_supported():
        raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_NATIVE_BF16_UNAVAILABLE")

    device = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(device)
    total_gib = float(props.total_memory) / float(1024 ** 3)
    pipeline = QwenImagePipeline.from_pretrained(
        QWEN_IMAGE_2512_MODEL_ID,
        revision=QWEN_IMAGE_2512_REVISION,
        torch_dtype=torch.bfloat16,
    )
    if pipeline.__class__.__name__ != "QwenImagePipeline":
        raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_PIPELINE_CLASS_INVALID")
    pipeline.enable_sequential_cpu_offload()

    live = {
        "gpu_name": torch.cuda.get_device_name(device),
        "gpu_total_vram_gb": total_gib,
        "torch_version": str(torch.__version__),
        "cuda_version": str(torch.version.cuda),
        "diffusers_version": str(diffusers.__version__),
        "pipeline_class": pipeline.__class__.__name__,
        "dtype": DTYPE,
        "offload_mode": OFFLOAD_MODE,
        "native_bf16": True,
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "weights_loaded": True,
        "sequential_cpu_offload_enabled": True,
    }
    expected = cs260.get("observed_runtime_identity")
    if not isinstance(expected, Mapping) or set(live) != set(expected):
        raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_RUNTIME_IDENTITY_FIELDS_DRIFT")
    for field, value in live.items():
        wanted = expected.get(field)
        if field == "gpu_total_vram_gb":
            if not isinstance(wanted, (int, float)) or isinstance(wanted, bool):
                raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_RUNTIME_VRAM_INVALID")
            if abs(float(value) - float(wanted)) > 0.05:
                raise RuntimeError(
                    "QWEN_CANONICAL_INFERENCE_CLI_RUNTIME_IDENTITY_DRIFT:gpu_total_vram_gb"
                )
        elif value != wanted:
            raise RuntimeError(
                f"QWEN_CANONICAL_INFERENCE_CLI_RUNTIME_IDENTITY_DRIFT:{field}"
            )
    return torch, pipeline


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run exactly one CS261-authorized, CS257-prompt-bound Qwen Image 2512 inference attempt"
    )
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--cs257-run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--guidance-scale", type=float, default=1.0)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    authorization_path = _repo_file(
        args.authorization,
        repo_root,
        "QWEN_CANONICAL_INFERENCE_CLI_AUTHORIZATION_OUTSIDE_REPOSITORY",
    )
    cs257_run_dir = _repo_dir(
        args.cs257_run_dir,
        repo_root,
        "QWEN_CANONICAL_INFERENCE_CLI_CS257_OUTSIDE_REPOSITORY",
    )
    output_dir = _repo_output(args.output_dir, repo_root)

    from engine.intelligence.qwen_image_story_bound_canonical_prompt import (
        build_story_bound_canonical_prompt,
    )

    bound_prompt = build_story_bound_canonical_prompt(
        cs257_run_dir,
        authorization_path,
        repo_root=repo_root,
    )
    prompt = bound_prompt.prompt
    negative_prompt = bound_prompt.negative_prompt

    authorization, cs260 = _load_cs260_from_authorization(
        authorization_path, repo_root
    )
    if authorization.get("story_snapshot_sha256") != bound_prompt.story_snapshot_sha256:
        raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_PROMPT_CROSS_STORY")
    expected_fingerprint = authorization.get("expected_runtime_fingerprint_sha256")
    if expected_fingerprint != cs260.get("expected_runtime_fingerprint_sha256"):
        raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_RUNTIME_FINGERPRINT_DRIFT")

    torch = None
    pipeline = None
    try:
        torch, pipeline = _collect_live_pipeline(cs260)

        from engine.intelligence.qwen_image_one_shot_canonical_inference import (
            CanonicalInferenceImage,
            execute_one_shot_canonical_inference,
            verify_one_shot_canonical_inference,
        )

        def one_inference() -> CanonicalInferenceImage:
            generator = torch.Generator(device="cpu").manual_seed(args.seed)
            kwargs: dict[str, Any] = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": args.width,
                "height": args.height,
                "num_inference_steps": args.steps,
                "guidance_scale": args.guidance_scale,
                "generator": generator,
            }
            result = pipeline(**kwargs)
            images = getattr(result, "images", None)
            if not images or len(images) != 1:
                raise RuntimeError("QWEN_CANONICAL_INFERENCE_CLI_SINGLE_IMAGE_REQUIRED")
            image = images[0]
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            width, height = image.size
            return CanonicalInferenceImage(
                png_bytes=buffer.getvalue(), width=int(width), height=int(height)
            )

        run = execute_one_shot_canonical_inference(
            authorization_path,
            output_dir,
            repo_root=repo_root,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=args.width,
            height=args.height,
            seed=args.seed,
            num_inference_steps=args.steps,
            guidance_scale=args.guidance_scale,
            observed_runtime_fingerprint_sha256=str(expected_fingerprint),
            inference_callable=one_inference,
        )
        verified = verify_one_shot_canonical_inference(
            run.receipt_path, repo_root=repo_root
        )
        print(
            json.dumps(
                {
                    "canonical_inference": verified,
                    "story_bound_prompt_contract": bound_prompt.contract,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    finally:
        if pipeline is not None:
            del pipeline
        if torch is not None and torch.cuda.is_available():
            torch.cuda.empty_cache()


if __name__ == "__main__":
    raise SystemExit(main())
