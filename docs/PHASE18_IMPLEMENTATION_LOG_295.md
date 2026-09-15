# Phase 18 Implementation Log 295 — Manifest-Bound GPU Launcher

## Branch safety

Work was performed only on `phase18/story-intelligence`. `main` was treated as read-only and was not committed to, merged, rebased, force-updated, or otherwise modified.

Starting Phase 18 branch HEAD for this change set:

`e9a2c2e051189b789901424265ca51075a4f951c`

CS294 Story Intelligence verification was confirmed `completed / success` before CS295 work began.

## Objective

Reduce the remaining human-error surface between a verified CS291/292 GPU-host launch manifest and the first genuine production Qwen inference.

The canonical inference CLI already failed closed on any manifest/invocation mismatch, but the operator still had to copy authorization, CS257 evidence, snapshot, seed, dimensions, steps, and guidance into a second command. CS295 removes that duplicated input surface.

## Added

### `engine/intelligence/qwen_image_manifest_bound_execution.py`

Introduces a manifest-derived execution edge that:

- fully replays `verify_gpu_host_launch_manifest(...)` first;
- requires `PUL7SAR_PHASE18_COST_MODE=$0-local`;
- derives authorization path from the verified manifest;
- derives CS257 evidence directory from the verified manifest;
- derives immutable local snapshot path from the verified manifest;
- derives width, height, seed, steps, and guidance from the verified manifest;
- requires a new repository-local output directory;
- constructs an argv list for the existing canonical production inference CLI;
- invokes it without `shell=True`;
- propagates the canonical CLI exit code rather than converting a failure into success.

The module does not load the model or create image pixels itself and grants no downstream authority.

Commit: `36409ce81b479df84299e916efbe2444480fdf75`

### `tools/phase18_run_manifest_bound_canonical_inference.py`

Adds a minimal production launcher that accepts only:

- `--launch-manifest`
- `--output-dir`
- `--repo-root`

It deliberately has no prompt/model/snapshot/settings/approval override flags.

Commit: `b7dc350421eca8e54881dbd82cd94ce824843dfd`

### `tests/test_phase18_qwen_image_manifest_bound_execution.py`

Adds CPU-only regressions for:

- exact manifest-derived argv construction;
- mandatory `$0-local` lock;
- rejection of existing or repository-external output directories;
- shell-free subprocess execution;
- propagation of a non-zero canonical inference exit code.

No mocked test result is represented as genuine Qwen output or Golden Visual evidence.

Commit: `01d398ad216f057f1be2ae5ed26754eace02bc44`

### `docs/PHASE18_CHANGESET_295_MANIFEST_BOUND_GPU_LAUNCHER.md`

Documents the scope, security properties, authority boundaries, test intent, and remaining GPU blocker.

Commit: `10d22c9c240981c7bfa7a1097cc11094829d878a`

### `docs/PHASE18_IMPLEMENTATION_LOG_295.md`

This implementation log.

## Modified

None.

The existing canonical inference CLI was intentionally not weakened or replaced. CS295 delegates to it, so CS292 pre-launch replay and CS293/294 postflight sealing remain mandatory inside the canonical edge itself.

## Deleted

None.

## Gate preservation

CS295 does not alter or bypass:

- factual/freshness locks;
- entity and identity verification;
- sentiment neutrality and loser-respect constraints;
- story-bound prompt ownership;
- `$0-local` zero-cost policy;
- local-files-only model policy;
- semantic approval;
- composition and generated-layer QA;
- visual-quality adjudication;
- Human Review;
- Exact Brand/Typography;
- `SemanticPublicationGate`;
- Genuine Golden PNG materialization;
- publication readiness.

The launcher has no authority fields and cannot set any of those states to true.

## Testing status

The new tests are part of the repository's `test_phase18_*.py` discovery surface and are expected to run under the existing Phase 18 Story Intelligence CI. The final workflow state must be checked on the resulting branch HEAD; no CI success is claimed until GitHub reports a terminal successful result.

## Genuine GPU execution status

No Qwen model load, CUDA/BF16 inference, genuine canonical candidate PNG, production composed PNG, or Genuine Golden PNG was fabricated in this change set.

The execution environment available to the automation remains non-GPU for genuine Qwen execution. The external blocker remains a zero-cost host that simultaneously provides:

- NVIDIA CUDA device;
- CUDA-enabled PyTorch;
- native BF16 support;
- compatible `QwenImagePipeline`;
- sequential CPU offload support;
- exact already-local approved Qwen Image snapshot/revision;
- sufficient real VRAM and system RAM demonstrated by actual model load/inference.

## Remaining path

`verified launch manifest`
→ `CS295 manifest-only launcher`
→ existing CS292 canonical preflight replay
→ genuine local Qwen model load
→ one-shot story-bound inference
→ CS290 local provenance
→ mandatory CS293/294 launch-to-output seal
→ factual/identity/sentiment/semantic/composition/visual-quality gates
→ Human Review
→ Exact Brand/Typography
→ real `SemanticPublicationGate`
→ CS285 exact-byte `genuine_golden_visual.png`
→ CS286 publication readiness.
