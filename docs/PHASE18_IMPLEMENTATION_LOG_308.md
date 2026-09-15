# Phase 18 Implementation Log 308 — Exact Final Composed Approval Lineage

## Starting state reviewed

- Repository: `pulsar7official/pul7sar-bot`
- Working branch only: `phase18/story-intelligence`
- Starting branch HEAD: `527cb864e3339807ac2328dfddbcb695e6ceec72`
- `main` observed independently at `f74d4013ea55ce54d473c203efc3a87738e7db00`
- No write, merge, rebase, reset, force-update, or other mutation was performed on `main`.

The downstream path after CS307 was reviewed before editing. CS277 Human Visual Review Request and CS278 Human Visual Review Evidence are unary, byte-bound stages that replay their immediate predecessors. CS279 and CS280 likewise carry the exact Human Review lineage into exact Brand/Typography presentation review.

## Proven gap

CS281 Final Composed Visual Approval is the first downstream multi-input aggregation edge reviewed in this run. It receives CS273 and CS280 independently.

Prior to CS308, CS281 verified both receipts and required matching Story SHA plus identical composed PNG path/SHA/byte size. However, CS280 transitively contains an exact review chain:

`CS280 -> CS279 -> CS278 -> CS277 -> CS276 -> CS275 -> CS274 -> CS273`

CS281 did not compare its independently supplied CS273 receipt with that transitive CS273. Therefore a different valid CS273 run for the same Story and PNG could theoretically be substituted at the aggregation edge.

## Code changes

### Modified

`engine/intelligence/qwen_image_composed_candidate_final_composed_visual_approval.py`

- upgraded CS281 schema from v1 to v2;
- added replay imports for CS274 through CS279 review lineage;
- added exact receipt-binding helpers;
- added verified source traversal that checks repository-relative byte binding and receipt SHA at each transition;
- added transitive derivation of the CS273 receipt embedded in the CS280 lineage;
- requires the supplied CS273 and derived CS273 to match on repository path, SHA-256, byte size, and receipt SHA-256;
- performs the exact-lineage check during both build and verification;
- records the stronger lineage requirement in policy metadata;
- preserves semantic, Genuine Golden, and publication authority as false.

`tests/test_phase18_qwen_image_composed_candidate_final_composed_visual_approval.py`

- added an exact-lineage success regression;
- added rejection of same-Story/same-PNG CS273 from another run;
- added rejection of receipt-digest drift with the same file binding;
- preserved prior semantic, Story/PNG drift, and premature-authority regressions.

### Added

- `docs/PHASE18_CHANGESET_308_EXACT_FINAL_COMPOSED_APPROVAL_LINEAGE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_308.md`

### Deleted

None.

## Authority and safety preservation

No factual, identity, sentiment, loser-respect, zero-cost, local/offline execution, visual-quality, Human Review, exact Brand/Typography, semantic-publication, or publication-readiness gate was removed or relaxed.

CS281 v2 may only open `composed_visual_approved=true` after exact lineage coherence. It still requires:

- `semantic_approved=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`

Human Visual Review and final presentation evidence remain external evidence contracts; CS308 does not synthesize or auto-approve either verdict.

## Tests

The code-bearing CS308 lineage through commit `05e7d996e19cc45d3fa1b3dedb50ce5f0b09a946` completed the Phase 18 Story Intelligence Verification push run `33528721400` successfully.

Successful stages include:

- CPU dependency installation;
- Syntax and discover validation;
- Completion and production isolation;
- visual-study handoff build and verification;
- cross-platform composition matrix build;
- publication-block verification;
- project-native editorial visual study;
- adaptive/self-contained reference brand verification;
- Golden editorial v6 build and verification;
- legacy-logo non-canonical assertion;
- all configured artifact uploads.

The parallel visual workflow checks observed on the same code-bearing SHA also completed successfully, while the duplicate PR Story Intelligence run was still finishing when this log was synchronized. No failing check was observed for the code-bearing SHA.

## Genuine Golden execution blocker

No Genuine Golden PNG was fabricated. Runtime re-measurement in this run showed:

- `PyTorch = 2.10.0+cpu`
- `CUDA available = false`
- `torch.version.cuda = None`
- `CUDA device count = 0`
- `native BF16 = false`
- `nvidia-smi = unavailable`

Compatible GPU execution is still required for the first real Qwen candidate. The execution host must provide the already-approved zero-cost/local runtime conditions, including NVIDIA CUDA, CUDA-enabled PyTorch, native BF16 support, compatible authorized QwenImagePipeline/Diffusers runtime, exact approved local model snapshot, and sufficient RAM/VRAM demonstrated by a real model load and inference.

Control-plane work in CS308 materially reduces the remaining gap by preventing cross-run semantic-review substitution immediately before final composed-visual authority.
