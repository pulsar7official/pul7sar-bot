# Phase 18 Implementation Log 290 — Local Inference Provenance

## Baseline

- Branch: `phase18/story-intelligence` only.
- Baseline HEAD: `f9afb414d227121c68d5c2218b71bbb98bb89f42` (CS289).
- CS289 `Phase 18 Story Intelligence Verification`: terminal `success` before CS290 work began (run `33379813148`, run number `4362`).
- `main` observed read-only at `368e8e07a6c5926a770a75f8fc0c506143845cf2`.
- No merge, rebase, force update, commit, or file write was performed on `main`.

## Why this change was necessary

CS289 hardened the actual one-shot inference edge so the Qwen pipeline loads only the exact approved local snapshot with no network fallback. CS262 already emitted a successful canonical inference receipt that binds the story authorization, prompt, runtime fingerprint, settings, one-shot consumption, and PNG bytes.

The remaining auditability gap was that the successful canonical receipt did not independently bind the candidate PNG to the exact CS289 local-only execution-contract source bytes and canonical local snapshot path/revision. CS290 closes that gap without introducing another approval gate.

## Added

1. `engine/intelligence/qwen_image_local_inference_provenance.py`
   - revalidates the successful CS262 canonical inference receipt;
   - requires genuine canonical inference to have executed;
   - requires all downstream semantic/quality/Golden/publication authority to remain false;
   - requires `$0-local`;
   - validates the exact approved canonical Qwen snapshot revision;
   - byte-binds the canonical receipt and candidate PNG;
   - byte-binds the CS289 runtime loader and canonical inference CLI source files;
   - emits an independently hashed `local_inference_provenance.json` receipt;
   - provides a verifier that reopens all repository byte bindings and fails closed on drift.

2. `tests/test_phase18_qwen_image_local_inference_provenance.py`
   - successful provenance build regression;
   - premature downstream-authority rejection;
   - snapshot-revision-drift rejection;
   - execution-contract-source byte-drift rejection;
   - provenance digest-tamper rejection.

3. `docs/PHASE18_CHANGESET_290_LOCAL_INFERENCE_PROVENANCE.md`
   - documents the build prerequisites, evidence bindings, verification behavior, CLI integration and authority boundary.

4. `docs/PHASE18_IMPLEMENTATION_LOG_290.md`
   - this implementation record.

## Modified

1. `tools/phase18_run_one_shot_canonical_inference.py`
   - after a successful CS262 inference receipt is verified, automatically builds `local_inference_provenance.json`;
   - immediately verifies that new provenance receipt before returning success;
   - prints the verified provenance alongside the canonical inference receipt;
   - retains the no-free-form-prompt, no-retry, local-only snapshot and all downstream authority boundaries.

## Deleted

- None.

## Authority preserved

CS290 does not weaken, replace or bypass Fact Lock, entity/identity verification, sentiment neutrality, semantic ownership, composition QA, visual-quality selection, Human Review, exact Brand/Typography, final semantic approval, `SemanticPublicationGate`, CS285 Genuine Golden materialization, or CS286 publication readiness.

A successful CS290 receipt can attest only that a genuine canonical candidate was produced through the local-only execution edge. It cannot set `semantic_approved`, `human_visual_review_approved`, `golden_quality_approved`, `genuine_golden_png_created`, or `publication_ready`.

## Zero-cost and provenance contract

- cost mode: `$0-local` only;
- model: `Qwen/Qwen-Image-2512`;
- revision: `2ce1c28560fbc62c9f5531e076b237d3575330a9`;
- local snapshot path must be canonical `snapshots/<revision>`;
- snapshot directory must exist at provenance-build time;
- `network_allowed=false`;
- `local_files_only=true`;
- sequential CPU offload remains required by the bound execution contract;
- canonical receipt and PNG bytes are independently rebound;
- CS289 runtime-loader and canonical-CLI source bytes are independently rebound.

## Commits in this change set

- `6339390e7fd71040fb6aed63b42e5c05bbe2922f` — add local inference provenance receipt/verification module.
- `b4e93fb58877513e96c34f9c30bdf64782f70a0b` — add provenance regressions.
- `eae6999d6dc91e64b31faa8cdaa0dbb31c91bc50` — integrate provenance into canonical inference CLI.
- `f4e34de96e2c026aade0b4b11c55130e0cdaccb2` — document CS290 contract.

The implementation-log commit is the final commit in this change set.

## Testing

The repository's discover-based Phase 18 CPU validator automatically includes `tests/test_phase18_qwen_image_local_inference_provenance.py`.

The new tests intentionally mock only the pre-existing successful CS262 verifier result and use synthetic candidate bytes; they test control/evidence behavior only and do not claim genuine Qwen inference or visual quality.

Terminal CI status must be checked on the final CS290 HEAD before the change set is described as CI-green.

## Genuine execution status and exact blocker

No production Qwen inference or Golden PNG is fabricated by CS290. The execution environment available to this run still does not provide a compatible NVIDIA CUDA/BF16 host for the real local-snapshot model load and inference.

A genuine attempt still requires one zero-cost host with:

- NVIDIA CUDA visible to CUDA-enabled PyTorch;
- native BF16;
- compatible `QwenImagePipeline`;
- sequential CPU offload support;
- exact already-local approved Qwen snapshot revision;
- sufficient VRAM and system RAM demonstrated by the real model-load/inference itself.

## Remaining gap

1. On a compatible zero-cost NVIDIA host, run CS287 static preflight against the exact local snapshot.
2. Run CS288 genuine local model-load attestation.
3. Run the CS290-integrated one-shot canonical inference CLI. A successful run now automatically produces and verifies local execution provenance for the real candidate PNG.
4. Feed that same candidate through the existing semantic, identity/pixel, visual-quality, Human Review, Brand/Typography, final composed/final semantic and `SemanticPublicationGate` chain.
5. Only after those authorities succeed may CS285 materialize exact bytes as `genuine_golden_visual.png`, followed by CS286 publication readiness.

No production Genuine Golden PNG is claimed by this change set.
