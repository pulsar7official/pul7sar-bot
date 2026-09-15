# Phase 18 Implementation Log 289 — Local-Only Canonical Inference Edge

## Baseline

- Branch: `phase18/story-intelligence` only.
- Baseline HEAD: `aa07f68699e9f3a92ec147f7e9f0a422767a0625` (CS288).
- CS288 `Phase 18 Story Intelligence Verification`: terminal `success` before CS289 work began (run `33374997027`, run number `4353`).
- `main` observed read-only at `368e8e07a6c5926a770a75f8fc0c506143845cf2`.
- No merge, rebase, force update, commit, or file write was performed on `main`.

## Why this change was necessary

The repository already had a genuine one-shot canonical Qwen Image inference CLI from CS262-era work. Reviewing its current branch implementation exposed one remaining zero-cost/reproducibility gap: at the actual inference edge it called `QwenImagePipeline.from_pretrained(model_id, revision=...)`. The revision was pinned, but a missing local cache entry could still cause network access/download. CS287 and CS288 had since established a stricter execution contract: exact already-local immutable snapshot, `$0-local`, BF16, and sequential CPU offload.

CS289 aligns the real inference edge with that newer contract rather than adding another approval gate.

## Added

1. `engine/intelligence/qwen_image_local_inference_runtime.py`
   - requires exact `$0-local` before any model operation;
   - re-runs CS287 static readiness against the supplied snapshot;
   - requires the exact approved Qwen snapshot revision;
   - loads the local snapshot with `torch.bfloat16` and `local_files_only=True`;
   - enables sequential CPU offload;
   - replays the live runtime identity against the CS260 evidence bound into CS261 authorization;
   - does not call the pipeline and grants no downstream authority.

2. `tests/test_phase18_qwen_image_local_inference_runtime.py`
   - zero-cost lock regression;
   - preflight-failure regression;
   - exact-local-snapshot/BF16/local-files-only/offload regression;
   - runtime-identity-drift regression.

3. `docs/PHASE18_CHANGESET_289_LOCAL_ONLY_CANONICAL_INFERENCE_EDGE.md`
   - records the execution contract and authority limits.

4. `docs/PHASE18_IMPLEMENTATION_LOG_289.md`
   - this implementation record.

## Modified

1. `tools/phase18_run_one_shot_canonical_inference.py`
   - removed the direct model-id/revision load path from the live inference edge;
   - added required `--snapshot-path` input;
   - delegates model loading to `load_local_inference_runtime(...)`;
   - therefore cannot silently download weights when the approved local snapshot is absent;
   - retains CS257 story-bound canonical prompt reconstruction, CS261 authorization verification, single-shot execution, and all downstream authority boundaries.

## Deleted

- None.

## Authority preserved

CS289 does not weaken or replace Fact Lock, entity/identity verification, sentiment neutrality, semantic layer ownership, visual-quality selection, Human Review, exact Brand/Typography, final semantic approval, `SemanticPublicationGate`, CS285 Genuine Golden materialization, or CS286 publication readiness.

A successful canonical inference is still only a candidate. No new code path in CS289 can set `semantic_approved`, `genuine_golden_png_created`, or `publication_ready`.

## Zero-cost and immutable execution policy

- cost mode: `$0-local` only;
- model: `Qwen/Qwen-Image-2512`;
- revision: `2ce1c28560fbc62c9f5531e076b237d3575330a9`;
- actual load source: exact local `snapshots/<revision>` path;
- `local_files_only=True` mandatory;
- native BF16 mandatory through CS287 preflight;
- sequential CPU offload mandatory;
- no retry loop and no hidden download fallback.

## Commits in this change set

- `b3aeaebfcfd3582a1723465db89a235bb9218de0` — add local-only inference runtime loader.
- `5f4ee17ff8b8b07f46cb5067f8bfac3c4cd8abca` — lock canonical inference CLI to local approved snapshot.
- `4a7e1045f9466d7ad0062d741c4c30307b79d12a` — add local inference runtime regressions.
- `f80a84717ee8dee27edfeafa5d604027da84f302` — document CS289 contract.

The implementation-log commit is the final commit in this change set.

## Testing

The repository's discover-based Phase 18 CPU validator automatically includes `tests/test_phase18_qwen_image_local_inference_runtime.py`. The new tests use mocks only for host-dependent CUDA/model behavior and explicitly do not claim a genuine inference result.

Terminal CI status must be checked on the final CS289 HEAD before the change set is described as CI-green.

## Genuine execution status and exact blocker

No production Qwen inference or Golden PNG is fabricated by CS289. The execution environment available to this run does not expose a compatible NVIDIA CUDA/BF16 host, so the real local-snapshot load and one-shot inference cannot be executed here.

A genuine attempt still requires one zero-cost host with:

- NVIDIA CUDA visible to CUDA-enabled PyTorch;
- native BF16;
- compatible `QwenImagePipeline`;
- sequential CPU offload support;
- exact already-local approved Qwen snapshot revision;
- sufficient VRAM and system RAM demonstrated by the real load/inference itself.

## Remaining gap

1. On the compatible zero-cost NVIDIA host, run CS287 against the exact local snapshot.
2. Run CS288 to prove genuine local model load/offload on that host.
3. Run the CS289-hardened `phase18_run_one_shot_canonical_inference.py` with the same exact snapshot and a valid CS261 authorization / CS257 story evidence set.
4. If a real canonical PNG is produced, pass it through the existing semantic, identity/pixel, visual-quality, Human Review, Brand/Typography, final composed/final semantic, `SemanticPublicationGate`, CS285 materialization, and CS286 publication-readiness chain.

No production Genuine Golden PNG is claimed by this change set.
