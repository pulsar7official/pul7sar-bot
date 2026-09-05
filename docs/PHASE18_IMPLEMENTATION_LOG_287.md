# Phase 18 Implementation Log 287 — Qwen-Image GPU Static Preflight

## Baseline

- Branch: `phase18/story-intelligence`
- Baseline HEAD: `c3e572f60b55eb38603d6d266a068da0c83f5800` (CS286)
- CS286 `Phase 18 Story Intelligence Verification`: terminal `success` before CS287 work began.
- `main` was read-only throughout this change set. No merge, rebase, force update, commit, or file write was performed on `main`.

## Goal

After CS286 completed the downstream control-plane through Genuine Golden publication readiness, the remaining material blocker was genuine Qwen-Image execution. CS287 reduces that gap by making host/runtime incompatibilities machine-readable before an expensive model-load attempt, while preserving the zero-cost requirement and all existing approval authorities.

## Added

1. `engine/intelligence/qwen_image_gpu_readiness.py`
   - local-only static runtime probe for the pinned Qwen-Image revision.
   - reports CUDA, BF16, device, observed VRAM, `nvidia-smi`, Qwen pipeline importability, sequential CPU offload support, and snapshot revision.
   - never downloads, loads model weights, runs inference, creates a PNG, or grants approval/publication authority.

2. `tests/test_phase18_qwen_image_gpu_readiness.py`
   - CPU-only runtime fails closed.
   - a compatible mocked CUDA/BF16/runtime/snapshot can pass static preflight but still cannot claim genuine inference.
   - VRAM is diagnostic only; no unproven Qwen-specific threshold is invented.
   - wrong snapshot revision fails closed.

3. `tools/phase18_qwen_image_gpu_readiness.py`
   - JSON CLI for local inspection.
   - optional `--snapshot-path` references an already-local snapshot only.
   - `--require-static-ready` can fail CI/host setup without granting any downstream authority.

4. `docs/PHASE18_CHANGESET_287_QWEN_IMAGE_GPU_READINESS.md`
   - authority, safety and scope contract.

5. `docs/PHASE18_IMPLEMENTATION_LOG_287.md`
   - this implementation record.

## Modified / corrected during the change set

No pre-existing Phase 18 production or policy file was modified.

During CS287 development, the newly-added readiness module initially contained a provisional 20 GiB minimum-VRAM threshold. That threshold was removed before completion because no Qwen-specific repository contract established it. The final implementation records VRAM only as an observation and refuses to treat it as proof of resource sufficiency. Corresponding newly-added tests were corrected as well.

## Deleted

- None.

## Authority preserved

CS287 creates no factual, identity, sentiment, semantic, Golden-quality, human-review, brand/typography, final-composed, final-semantic, publication, materialization or publication-readiness approval.

Even a completely successful static preflight emits:

- `genuine_inference_executed=false`
- `ready_for_genuine_inference_claim=false`

It only opens the operational possibility of attempting a genuine model load on a compatible local zero-cost host.

## Commits in this change set

- `f14c33c6e2796a1491782a49b8c8a24d9db01d01` — add Qwen GPU readiness probe.
- `bc7095e60a30b3dbad92f0e46ea4eeec5f1a8b67` — add readiness regressions.
- `d21ca20ecf015792ac878a933d6a9d05ce25fbf5` — remove speculative VRAM threshold.
- `980c0fe622c4859435012f653092ab2fb45a9a16` — align regressions with fail-closed static preflight.
- `3f199edbc65a33039f26c567372252056b03aa08` — add readiness CLI.
- `c94b492213366df399c020426cc4e72d36224620` — document CS287 contract.

The final implementation-log commit follows this list.

## Testing status

The new regressions are committed for the repository's existing Phase 18 verification workflow. Terminal CI status must be checked on the final CS287 HEAD; no success is claimed here until GitHub reports it.

## Genuine execution blocker

The current execution environment remains unable to perform genuine CS262 Qwen-Image inference when it lacks CUDA-visible NVIDIA hardware, native BF16, a compatible CUDA PyTorch runtime, compatible `QwenImagePipeline`, the exact approved local model snapshot, and sufficient real host resources for a successful model-load/inference run.

CS287 deliberately distinguishes observable static compatibility from actual resource sufficiency. A model-load/inference result must not be fabricated from static metadata.

## Remaining gap

1. Run the CS287 static preflight on a genuinely compatible zero-cost NVIDIA host with the approved local Qwen snapshot.
2. If static preflight passes, execute the existing genuine Qwen generation path and capture real model-load/inference evidence.
3. Pass the resulting real PNG through the already-established factual, identity, sentiment, semantic, composition, Golden-quality, human, brand/typography, final semantic, SemanticPublication, materialization and publication-readiness chain.

No production Genuine Golden PNG is claimed by CS287.
