# Phase 18 Change Set 295 — Manifest-Bound GPU Launcher

## Purpose

CS295 reduces the remaining operational gap to the first genuine Qwen Image PNG without adding a new approval authority.

Before CS295, the production canonical inference CLI correctly required the CS291/292 launch manifest, but the operator still had to repeat the manifest's authorization path, CS257 evidence path, local snapshot path, seed, dimensions, inference steps, and guidance scale on the command line. CS292 would reject drift, but manual duplication remained an avoidable failure mode on a future zero-cost CUDA host.

CS295 adds a manifest-only launcher. The operator supplies only:

- the verified launch manifest;
- a new repository-local output directory;
- optionally the repository root through the CLI.

Every story/model/inference value is recovered from the launch manifest after the full existing verifier replays it.

## Security and gate preservation

The launcher does not accept:

- a prompt or negative prompt;
- authorization or CS257 paths;
- model ID or revision;
- a snapshot override;
- width or height;
- seed;
- inference steps;
- guidance scale;
- network enablement;
- semantic approval;
- Golden approval;
- publication approval.

`PUL7SAR_PHASE18_COST_MODE` must already equal `$0-local` before an execution argv can be produced.

The launcher invokes `tools/phase18_run_one_shot_canonical_inference.py` without a shell. That canonical CLI independently replays CS292 before prompt extraction/model load and, after a successful genuine inference, requires CS290 provenance plus the CS293/294 launch-to-output postflight seal before success can be returned.

Therefore CS295 cannot weaken Fact/Identity/Sentiment, semantic ownership, visual-quality, Human Review, Exact Brand/Typography, SemanticPublicationGate, Genuine Golden materialization, or publication-readiness authority.

## Added

- `engine/intelligence/qwen_image_manifest_bound_execution.py`
- `tools/phase18_run_manifest_bound_canonical_inference.py`
- `tests/test_phase18_qwen_image_manifest_bound_execution.py`
- this contract document
- `docs/PHASE18_IMPLEMENTATION_LOG_295.md`

## Modified

None.

## Deleted

None.

## Test intent

CPU-only regressions verify that:

1. authorization/evidence/snapshot/settings are taken from the verified manifest, not operator flags;
2. `$0-local` is mandatory before execution planning;
3. output must be a new repository-local path;
4. execution uses a shell-free subprocess argv and propagates the canonical CLI exit code.

These tests do not claim a model load, CUDA execution, generated PNG, Golden Visual, or publication readiness.

## Remaining external blocker

A genuine output still requires a compatible zero-cost host with NVIDIA CUDA, CUDA-enabled PyTorch, native BF16 support, compatible `QwenImagePipeline`, sequential CPU offload, the exact already-local approved Qwen snapshot, and sufficient real VRAM/RAM. CS295 only removes manual launch-argument duplication once such a host is available.
