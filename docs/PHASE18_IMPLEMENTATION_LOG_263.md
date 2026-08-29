# Phase 18 Implementation Log — Change Set 263

## Scope

Canonical Candidate Byte Admission. Branch-only work on `phase18/story-intelligence`. `main` was inspected only and was never modified.

## Baseline reviewed before writing

- Phase 18 branch baseline: `6301c43ea4f4f31927a5339b53e467f4fb229d6c` (Change Set 262 implementation log).
- `main` observed before this change set: `7cca9afed308492c15bda397d06ce3a393791d23`.
- Existing CS262 verifier was read before implementation. It already revalidates CS261 authorization, one-shot consumption, model/revision/cost/runtime bindings, candidate SHA-256/byte size, and PNG dimensions; it deliberately keeps all Golden/semantic/human/publication authority false.

## Changes

### Added

1. `engine/intelligence/qwen_image_canonical_candidate_byte_admission.py`
   - Reuses `verify_one_shot_canonical_inference()` rather than duplicating upstream inference semantics.
   - Reopens and SHA-256 binds exact CS262 receipt bytes and exact `canonical_candidate.png` bytes.
   - Rechecks PNG signature/IHDR and dimensions.
   - Carries story/model/revision/runtime/prompt/inference provenance forward.
   - Emits a SHA-256-sealed admission receipt.
   - Provides an independent verifier that reopens source receipt and candidate bytes.
   - Rejects symlinks, outside-repository paths, byte drift, dimension drift, premature downstream authority and output overwrite.

2. `tests/test_phase18_qwen_image_canonical_candidate_byte_admission.py`
   - Covers exact candidate admission without quality-authority escalation.
   - Covers candidate byte tampering.
   - Covers attempted premature Golden authority.
   - Covers symlinked candidate rejection.
   - Covers pre-existing output rejection.
   - Synthetic PNG bytes exist only as control-plane regression fixtures and are never treated as genuine Qwen output.

3. `tools/phase18_admit_canonical_candidate_bytes.py`
   - CPU-only CLI for CS262-to-CS263 byte admission and immediate verification.
   - Performs no model loading and no inference.

4. `docs/PHASE18_CHANGESET_263_CANONICAL_CANDIDATE_BYTE_ADMISSION.md`
   - Defines purpose, authority boundary, fail-closed behavior and remaining path.

5. `docs/PHASE18_IMPLEMENTATION_LOG_263.md`
   - This implementation record.

### Modified

No pre-existing production, verifier, generation, visual-quality, branding, or publication file was modified in this change set.

### Deleted

Nothing.

## Commits

- `17202e2852851f00ab171f8db542c317514647af` — add canonical candidate byte-admission engine.
- `c10c17f0d9e0ea6bfd44db877ab09a7a72cab315` — add CS263 regressions.
- `78cedbebf0ab5a3f3fffc1b6148125dc25fe1f46` — add CPU-only candidate-admission CLI.
- `522032370c9c048a99fabb13f8a6e2c22bdb5505` — document CS263 contract.
- final documentation commit: created by this log update.

## Preserved gates

CS263 does not weaken or replace Fact Lock, Entity/Identity Verification, Sentiment Neutrality, Story Semantic Preflight/replay, Zero-Cost qualification, semantic/layer ownership, Visual Critic, Human Review, Golden thresholds, exact brand/typography work, or SemanticPublicationGate.

The only new positive authority is:

`candidate_bytes_admitted_for_post_generation_qa = true`

The following remain mandatory `false`:

`genuine_golden_png_created`, `semantic_approved`, `human_visual_review_approved`, `golden_quality_approved`, `publication_ready`.

## Testing status

The new regression suite has been committed so the repository's Phase 18 GitHub Actions can discover and execute it. CI terminal status must be checked after this log commit; success is not claimed in advance.

## Genuine PNG status / exact blocker

No genuine candidate PNG and no Genuine Golden Visual PNG were created by this change set. CS263 is post-generation control-plane preparation only.

The last directly observed execution environment remained CPU-only (`torch 2.10.0+cpu`, CUDA unavailable, no PyTorch CUDA version, native BF16 unavailable, `nvidia-smi` absent). A real CS262 run still requires one compatible $0-local same host that satisfies CUDA, native BF16, sufficient VRAM/RAM, exact pinned Qwen/Qwen-Image-2512 revision, successful `QwenImagePipeline.from_pretrained()`, and sequential CPU offload.

## Remaining gap

Once a real CS262 candidate exists, CS263 can immediately byte-admit it without any manual trust gap. The next safe work is to connect this exact byte admission to the existing post-generation semantic/layer and visual-quality contracts without creating parallel approval semantics. A candidate can become Golden only after all downstream semantic, Visual Critic, human, Golden-score, exact-brand/typography, and publication gates succeed.
