#!/usr/bin/env python3
"""Run one genuine, story-authorized Qwen Image 2512 canonical inference attempt.

The production entry point accepts no free-form prompt. Prompt bytes are derived
inside this command from the exact CS257 evidence set that passed independent semantic
replay, then cross-bound to the same CS261 generation authorization. The actual model
load is locked to the exact already-local approved snapshot with no network fallback.

Change Set 292 additionally makes the CS291 GPU-host launch manifest mandatory at the
production edge. The manifest is fully replayed before prompt extraction or model load,
and its authorization, CS257 directory, snapshot path/revision, seed, dimensions,
steps, and guidance scale must exactly match this invocation. This closes the direct
CLI bypass around pre-launch attestation while preserving every downstream gate.

There is no retry loop. A claimed authorization is burned even when inference or PNG
validation fails. A successful result is only a canonical candidate; all downstream
quality and publication gates remain closed. CS290 emits local-only provenance for the
successful candidate. CS294 additionally materializes and immediately replays CS293's
launch-to-output attestation before the command may return success, binding the same
pre-launch manifest to the exact produced PNG and post-inference provenance.
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run exactly one CS261-authorized, CS257-prompt-bound Qwen Image 2512 inference attempt"
    )
    parser.add_argument("--launch-manifest", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--cs257-run-dir", type=Path, required=True)
    parser.add_argument(
        "--snapshot-path",
        type=Path,
        required=True,
        help="Exact already-local approved Qwen/Qwen-Image-2512 snapshots/<revision> directory",
    )
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

    launch_manifest_path = _repo_file(
        args.launch_manifest,
        repo_root,
        "QWEN_CANONICAL_INFERENCE_CLI_LAUNCH_MANIFEST_OUTSIDE_REPOSITORY",
    )
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
    snapshot_path = args.snapshot_path.expanduser().resolve()
    output_dir = _repo_output(args.output_dir, repo_root)

    # CS292: replay the entire pre-launch contract before prompt extraction, model
    # import/load, authorization consumption, or inference. Any invocation drift is
    # fatal and no fallback path exists.
    from engine.intelligence.qwen_image_gpu_host_launch_manifest import (
        verify_gpu_host_launch_manifest_for_execution,
    )

    launch_manifest = verify_gpu_host_launch_manifest_for_execution(
        launch_manifest_path,
        authorization_path=authorization_path,
        cs257_run_dir=cs257_run_dir,
        snapshot_path=snapshot_path,
        repo_root=repo_root,
        width=args.width,
        height=args.height,
        seed=args.seed,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance_scale,
    )

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

    from engine.intelligence.qwen_image_local_inference_runtime import (
        load_local_inference_runtime,
    )

    torch = None
    pipeline = None
    try:
        torch, pipeline, _live_identity = load_local_inference_runtime(
            cs260=cs260,
            snapshot_path=snapshot_path,
        )

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

        from engine.intelligence.qwen_image_local_inference_provenance import (
            build_local_inference_provenance,
            verify_local_inference_provenance,
        )

        provenance_path = run.output_dir / "local_inference_provenance.json"
        build_local_inference_provenance(
            run.receipt_path,
            snapshot_path,
            provenance_path,
            repo_root=repo_root,
        )
        verified_provenance = verify_local_inference_provenance(
            provenance_path, repo_root=repo_root
        )

        # CS294: a successful production inference may not return success until the
        # exact CS292 pre-launch manifest is joined to the verified CS290 postflight
        # provenance and canonical PNG. The attestation itself grants no quality,
        # semantic, Golden, or publication authority.
        from engine.intelligence.qwen_image_launch_to_output_attestation import (
            build_launch_to_output_attestation,
            verify_launch_to_output_attestation,
        )

        launch_to_output_path = run.output_dir / "launch_to_output_attestation.json"
        build_launch_to_output_attestation(
            launch_manifest_path,
            provenance_path,
            launch_to_output_path,
            repo_root=repo_root,
        )
        verified_launch_to_output = verify_launch_to_output_attestation(
            launch_to_output_path, repo_root=repo_root
        )

        print(
            json.dumps(
                {
                    "launch_manifest_sha256": launch_manifest.get("manifest_sha256"),
                    "canonical_inference": verified,
                    "local_inference_provenance": verified_provenance,
                    "launch_to_output_attestation": verified_launch_to_output,
                    "story_bound_prompt_contract": bound_prompt.contract,
                    "model_snapshot": str(snapshot_path),
                    "network_allowed": False,
                    "local_files_only": True,
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
