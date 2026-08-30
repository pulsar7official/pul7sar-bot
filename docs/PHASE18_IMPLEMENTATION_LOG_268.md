# Phase 18 Implementation Log 268 — Canonical Candidate Generated-Layer QA

## Branch Safety / Baseline

- Repository: `pulsar7official/pul7sar-bot`
- Write branch: `phase18/story-intelligence` only.
- Baseline branch HEAD reviewed before changes: `13a592d9309fad9955b7fcbf0b0c6120d9285480`.
- `main` was reviewed separately and never used as a write target. During this run it advanced independently; the latest observed `main` SHA before this log update was `b8beec010e496b8b14cb835717c29f235b58b20c`.
- No merge, rebase, force-update, commit, file write, or branch update was performed on `main`.

## Existing Contracts Reviewed

Before implementation, CS268 reviewed and reused:

- `engine/intelligence/visual_layer_qa.py`
  - `HybridLayerQualityGate`
  - `LayerLeakageEvidence`
- `engine/intelligence/hybrid_layer_planner.py`
  - `HybridLayerPlan`
  - `VisualLayer`
  - `LayerSource`
- CS264 Canonical Candidate Semantic Base QA and its exact `semantic_layer_evidence` payload.
- CS265 Canonical Candidate Identity Requirement.
- CS267 Pixel Identity Review Evidence.

No new parallel visual-leakage standard was introduced.

## Code Changes

### Added

1. `engine/intelligence/qwen_image_canonical_candidate_generated_layer_qa.py`
   - Initial commit `48d05f26728887cd5462644d0e63dc425372433d`.
   - Adds byte-bound CS264/CS265/CS267 replay.
   - Reopens exact candidate PNG bytes.
   - Reuses `HybridLayerQualityGate`.
   - Requires approved CS267 evidence for identity-sensitive human candidates.
   - Does not fabricate identity approval for non-human candidates.
   - Keeps composition, Golden, human-review and publication authority closed.

2. `tests/test_phase18_qwen_image_canonical_candidate_generated_layer_qa.py`
   - Initial commit `384d43752e90bea5567b0f3b29aab15cab5521ec`.
   - Standard-library `unittest` coverage for human identity requirement, non-human path, generated-text leakage, candidate-byte drift and no-overwrite behavior.

3. `tools/phase18_run_canonical_candidate_generated_layer_qa.py`
   - Commit `0f323fc9d9c5a7e1a3b64b5e0a1ae3a7647021b1`.
   - CPU/control-plane CLI for executing and immediately re-verifying CS268.

4. `docs/PHASE18_CHANGESET_268_CANONICAL_CANDIDATE_GENERATED_LAYER_QA.md`
   - Commit `17caf621d8b5b32bba0782b913ccce1aaaf989f7`.
   - Documents scope, authority and fail-closed behavior.

5. `docs/PHASE18_IMPLEMENTATION_LOG_268.md`
   - Initial commit `146da2b8b91cd823aeb5ee1b2031bc75ca55c930`.

### Hardening During Review

A self-review found that CS264 already carries `generated_unverified_identity_detected`. The first CS268 implementation derived that field only from the CS265/CS267 identity state, which could suppress an upstream semantic-inspector warning after a manual identity approval or on a non-human classification. That would weaken evidence rather than compose it fail-closed.

The implementation was hardened so the effective leakage flag is now:

`CS264.generated_unverified_identity_detected OR (pixel_identity_review_required AND NOT identity_approved)`

Therefore an upstream unverified-identity warning can never be erased by CS267 approval. Conflicting evidence blocks the candidate.

- Engine hardening commit: `74433e23c91e6d43b9fe680d8cf7b302a890fcab`.
- Regression hardening commit: `f2468f21ca39bc5dd8d08abf69b6007360fe7c58`.
- Added regression: upstream `generated_unverified_identity_detected=true` remains true and triggers `generated_identity_leaked_into_verified_identity_layer` even when CS267 separately says identity review approved.

### Modified Existing Production/Gate Files

None. Only the newly added CS268 engine/test files were modified during hardening.

### Deleted

None.

## Authority State

A CS268 pass may set only:

- `generated_layer_qa_approved=true`
- `identity_approved=true` only for a human candidate whose exact CS267 evidence independently approved identity **and** for which no upstream unverified-identity leakage evidence remains.

For a non-human candidate `identity_approved` remains false; absence of a required human identity is represented by CS265 classification rather than fabricated approval.

CS268 always keeps false:

- `composition_executed`
- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `golden_quality_approved`
- `publication_ready`

## Tests / CI

Regression tests use `unittest` only, matching the repository's Phase 18 CI discovery contract. Coverage includes:

- human candidate + exact approved CS267 evidence;
- fail-closed missing human identity evidence;
- non-human path without fabricated identity approval;
- generated-text leakage rejection through the existing hybrid gate;
- preservation/rejection of upstream unverified-identity evidence;
- candidate-byte drift invalidation;
- output-directory no-overwrite behavior.

The first CI run for implementation-log SHA `146da2b8b91cd823aeb5ee1b2031bc75ca55c930` started successfully but became superseded by the hardening commits. Terminal CI status must therefore be read from the latest CS268 SHA; no green claim is recorded until that exact executable state reaches terminal success.

## Runtime / Genuine PNG State

Current execution environment was checked directly during this run:

- `torch_version=2.10.0+cpu`
- `cuda_available=False`
- `torch_cuda_version=None`
- `bf16_supported=False`
- `nvidia-smi` unavailable

CS268 itself is safe CPU/control-plane preparatory work and does not perform image generation. No Qwen-Image-2512 model load, genuine inference, Genuine Candidate PNG, Pixel Identity verdict, Golden score, or Genuine Golden Visual PNG was fabricated.

The genuine generation boundary remains blocked until one `$0-local` host can prove the already-pinned runtime requirements, including NVIDIA CUDA, native BF16, sufficient live VRAM/RAM, exact pinned `Qwen/Qwen-Image-2512`, successful `QwenImagePipeline` load and sequential CPU offload.

## Remaining Path

`genuine story -> upstream factual/identity/sentiment/semantic/zero-cost/ownership gates -> CS257 replay -> CS258-260 runtime qualification -> CS261 authorization -> CS262 one-shot genuine inference -> CS263 byte admission -> CS264 semantic base QA -> CS265 identity requirement -> CS266 identity review request -> CS267 identity evidence when required -> CS268 generated-layer ownership QA -> deterministic/verified composition -> composed-visual semantic QA -> Visual Critic -> Human Review -> Golden >=8.5 / elite >=9.0 -> exact Brand/Typography -> SemanticPublicationGate`
