# Phase 18 Implementation Log — Change Set 266

## Baseline and branch safety

- Working branch: `phase18/story-intelligence` only.
- Baseline HEAD reviewed before writes: `e44ab61fe2b1ae1eb04c9b3c4f8be63ccaef538b`.
- Baseline CS265 Story Intelligence Verification was confirmed `success` before new production work began.
- `main` was reviewed read-only at `7cca9afed308492c15bda397d06ce3a393791d23`.
- No commit, merge, rebase, force-update, or other write to `main` was performed.

## Review finding before CS266

Before creating the next identity layer, the CS265 verifier was re-read. The review found a provenance weakness: initial CS265 verification re-opened identity evidence but did not independently re-open/replay the source CS264 receipt and exact candidate PNG bytes.

That gap was closed first:

- `ed221b4cce0f27674d8c728884e8219d74dc255b` — CS265 now byte-binds/replays CS264, re-opens candidate bytes, checks story/receipt linkage, recomputes identity semantics, human targets, and the review-required decision.
- `2bb3c0a3d2f42d6354e6c5afcd6da325e45ad6f0` — added candidate-drift and CS264-drift regressions alongside identity-evidence drift coverage.
- `485807b391de48607a50b0916950b8a1fef07da2` — updated CS265 implementation log to record the finding and fix.

No authority was added by this hardening.

## CS266 purpose

No existing repository verifier was found that can truthfully establish the identity of a generated human face from the candidate pixels. The existing general semantic inspector is explicitly not treated as person-identity evidence. CS266 therefore creates a byte-bound pixel-identity review request rather than inventing a model, confidence threshold, or identity verdict.

## Added

1. `engine/intelligence/qwen_image_canonical_candidate_pixel_identity_review_request.py`
   - Replays the hardened CS265 verifier.
   - Binds the exact CS265 receipt, candidate PNG bytes, story SHA, identity evidence, and canonical human targets.
   - Requires non-empty source-backed `identity_source_refs` for every human review target.
   - Creates an immutable review contract requiring canonical-person match, no substitution, no conflicting/ambiguous identity, and use of source-backed references.
   - Explicitly records that the general semantic scene verdict is not identity evidence and that no automatic identity threshold has been defined.
   - Fails closed without a compatible identity-review execution.
   - Never grants identity, semantic, Human Review, Golden, or publication authority.

2. `tests/test_phase18_qwen_image_canonical_candidate_pixel_identity_review_request.py`
   - Uses standard-library `unittest` only.
   - Covers human review request creation without approval.
   - Covers non-human no-review classification without manufacturing approval.
   - Rejects missing source-backed references for a human target.
   - Rejects candidate-byte drift after request creation.
   - Rejects source-CS265-byte drift after request creation.

3. `tools/phase18_build_canonical_candidate_pixel_identity_review_request.py`
   - CPU-only request builder/verifier.
   - Does not accept an identity verdict and cannot approve identity.

4. `docs/PHASE18_CHANGESET_266_CANONICAL_CANDIDATE_PIXEL_IDENTITY_REVIEW_REQUEST.md`

5. `docs/PHASE18_IMPLEMENTATION_LOG_266.md`

## CS266 commits before this log

- `0a2388c3b8b39cd89f08e2420458274dca0da1c5` — CS266 engine.
- `ad5039d61fab0ff85450f1de64840e0e6ee2e1ad` — CS266 regression coverage.
- `d5af6cc545e2dcf4b1efb50f5ad9b4350c0d96c7` — CS266 CPU-only CLI.
- `9dd241d807eb54cf46953f1fa7e25964aca87131` — CS266 contract documentation.

## Modified

- `engine/intelligence/qwen_image_canonical_candidate_identity_requirement.py` — CS265 provenance hardening before CS266.
- `tests/test_phase18_qwen_image_canonical_candidate_identity_requirement.py` — CS265 provenance regressions.
- `docs/PHASE18_IMPLEMENTATION_LOG_265.md` — hardening record.

No pre-existing Fact Lock, identity policy, sentiment policy, zero-cost policy, semantic-layer ownership gate, generation authority, Visual Critic, Human Review, Golden threshold, exact brand/typography gate, or SemanticPublicationGate implementation was weakened or bypassed.

## Deleted

None.

## Authority state

CS266 may establish only the state of a review request:

- `pixel_identity_review_required=true|false`
- `pixel_identity_review_request_created=true` only when review is required

It always keeps:

- `pixel_identity_review_executed=false`
- `identity_approved=false`
- `semantic_approved=false`
- `human_visual_review_approved=false`
- `genuine_golden_png_created=false`
- `golden_quality_approved=false`
- `publication_ready=false`

## Runtime / CUDA check

The available execution environment was re-checked during this change set:

- `torch_version=2.10.0+cpu`
- `cuda_available=False`
- `torch_cuda_version=None`
- `bf16_supported=False`
- `nvidia-smi` not present

Therefore no genuine Qwen Image model load, inference, candidate PNG, identity verdict, or Golden PNG is claimed.

The live-generation blocker remains an available `$0-local` host that simultaneously proves NVIDIA CUDA, native BF16, sufficient live VRAM/RAM, the exact pinned `Qwen/Qwen-Image-2512` revision, compatible `QwenImagePipeline`, successful model load, and sequential CPU offload.

## Testing state

The CS265 baseline at `e44ab61fe2b1ae1eb04c9b3c4f8be63ccaef538b` was confirmed green before this work. New CS265-hardening and CS266 commits must be validated by the Phase 18 Story Intelligence Verification workflow; terminal CI status is not claimed until GitHub reports it.

## Remaining gap

For a genuine generated candidate with human targets, the next identity step must consume this exact CS266 request and produce compatible pixel-identity evidence against the bound source-backed references. Until such an execution exists and passes, identity approval must remain false. After identity, the candidate still must pass Hybrid Layer QA, byte-bound Visual Critic, Human Review, Golden scoring (minimum 8.5; elite 9.0), exact Brand/Typography integrity, and SemanticPublicationGate.
