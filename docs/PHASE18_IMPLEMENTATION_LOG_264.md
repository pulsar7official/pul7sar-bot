# Phase 18 Implementation Log — Change Set 264

## Scope

Canonical Candidate Semantic Base QA. Branch-only work on `phase18/story-intelligence`. `main` was inspected before and during implementation and was never modified.

## Baseline reviewed before writing

- Phase 18 branch initially observed at `29f6654859f00897ca660bccb662487ceaa4085a` (Change Set 263 implementation log).
- `main` observed at `7cca9afed308492c15bda397d06ce3a393791d23` and remained read-only.
- The initial Story Intelligence Verification for CS263 (`33282154639`, run number `4067`) was found to have failed during unittest discovery because the new CS263 test imported undeclared `pytest`.
- Commit `268aef72372518470762143651bec61c7e21ca55` converted that suite to repository-native `unittest`; `docs/PHASE18_IMPLEMENTATION_LOG_263.md` was then corrected to record the failed run and fix rather than imply a green state.
- Existing post-generation contracts were read before CS264 implementation: `semantic_visual_verdict.py`, `semantic_layer_evidence.py`, `visual_layer_qa.py`, `hybrid_layer_planner.py`, `qwen25_vl_inspector.py`, `visual_brain.py`, and `visual_brain_critic_provenance.py`.

## Changes

### Added

1. `engine/intelligence/qwen_image_canonical_candidate_semantic_base_qa.py`
   - Replays `verify_canonical_candidate_byte_admission()` before inspection.
   - Reopens and SHA-256 binds the exact CS263 receipt and exact candidate PNG.
   - Rejects symlink/outside-repository/path drift and candidate byte drift.
   - Uses the existing approved `Qwen25VLSemanticInspector` in `BASE_SCENE` mode.
   - Pins semantic inspection to repository constants for `Qwen/Qwen2.5-VL-3B-Instruct`, immutable approved revision, verifier id, process-isolated profile, and minimum confidence `0.85`.
   - Reuses `SemanticVisualVerdictGate` rather than inventing alternate semantic pass criteria.
   - Requires readable text, platform brand, fake entity marks, exact numbers, illegal generated sport geometry, split/collage scenes, severe defects and subject-framing checks to be actually inspected and above the existing confidence floor.
   - Reuses `SemanticLayerEvidenceAdapter` and requires complete layer evidence for the base generated layer.
   - Records both pass and rejection receipts so a rejected candidate cannot lose provenance.
   - Provides an independent verifier that reopens CS263/candidate bytes and recomputes the semantic decision from the normalized verdict payload.
   - Explicitly keeps identity approval and all global semantic/Golden/human/publication authorities false.

2. `tests/test_phase18_qwen_image_canonical_candidate_semantic_base_qa.py`
   - Standard-library `unittest` only.
   - Covers a successful non-identity base semantic inspection without authority escalation.
   - Covers generated-text rejection and resulting layer evidence.
   - Covers candidate byte tampering after semantic receipt creation.
   - Covers semantic verifier identity drift.
   - Covers output overwrite rejection.
   - Uses a deterministic fake inspector only inside regression tests; production entry points do not accept external verdict files.

3. `tools/phase18_run_canonical_candidate_semantic_base_qa.py`
   - Production CLI that instantiates the real repository semantic inspector through CS264.
   - Performs no Qwen-Image generation.
   - Exits non-zero for a semantic rejection and never upgrades it into Golden/publication authority.

4. `docs/PHASE18_CHANGESET_264_CANONICAL_CANDIDATE_SEMANTIC_BASE_QA.md`
   - Defines the byte binding, existing gates reused, identity boundary, authority state and remaining path.

5. `docs/PHASE18_IMPLEMENTATION_LOG_264.md`
   - This record.

### Modified

- `tests/test_phase18_qwen_image_canonical_candidate_byte_admission.py`
  - Converted from `pytest` fixtures to standard-library `unittest` after the exact CI dependency failure was discovered.
- `docs/PHASE18_IMPLEMENTATION_LOG_263.md`
  - Corrected with the failed run id, exact `ModuleNotFoundError`, and the unittest-native remediation commit.

No pre-existing production gate, semantic-verdict implementation, visual-layer gate, Visual Critic, Human Review, Golden threshold, brand/typography implementation, generation runtime, or SemanticPublicationGate was modified.

### Deleted

Nothing.

## Commits in this continuation

- `268aef72372518470762143651bec61c7e21ca55` — make CS263 regressions unittest-native.
- `be9b446e2464437c90b5dcb1d4f9743b0a69bffe` — record CS263 CI dependency failure and fix.
- `eaaa6783e77fd6effc832c8a67ab973e31b5c350` — add CS264 byte-bound semantic base QA engine.
- `2c6e0111385d5c6d8f96f0bb548b1bd6b90aa493` — add CS264 semantic QA regressions.
- `e946606c112293b4718751abc741206cd86281c4` — add real semantic QA CLI.
- `543382ab6b846c1617828afe86e2df57a3008418` — document CS264 contract.
- `3d00e9f9081a00c84ea130fe60d8a0abafe0166b` — initial CS264 implementation log; this exact SHA was tested by Story Intelligence Verification run `33284394700` / run number `4081` and completed successfully.
- final documentation commit: created by this green-status log update.

## Existing contracts preserved and reused

CS264 deliberately builds on, rather than replaces:

- `SemanticVisualVerdictGate`: missing/not-inspected checks and sub-threshold confidence remain blockers.
- `SemanticLayerEvidenceAdapter`: missing layer checks never become implicit clean evidence.
- `Qwen25VLSemanticInspector`: model/revision/verifier/stage behavior remains canonical.
- `HybridLayerQualityGate`: remains a downstream full-layer-ownership gate; CS264 prepares its semantic leakage evidence but does not bypass it.
- `VisualCriticGate` and `VisualCriticProvenanceGate`: remain downstream and unchanged.

Fact Lock, Entity/Identity Verification, Sentiment Neutrality, Story Semantic Replay, Zero-Cost qualification, Exact Brand/Typography, Human Review, Golden thresholds and `SemanticPublicationGate` remain unchanged.

## Authority after CS264

A real passing semantic base-scene inspection may establish only:

- `semantic_inspection_executed = true`
- `semantic_base_scene_approved = true`

It must still report:

- `identity_approved = false`
- `semantic_approved = false`
- `genuine_golden_png_created = false`
- `human_visual_review_approved = false`
- `golden_quality_approved = false`
- `publication_ready = false`

This separation is intentional because the current semantic inspector does not produce identity-validity evidence, and a base generative scene is not the final deterministic/verified-layer composite.

## Testing status

- The exact cause of the previous CS263 Story Intelligence Verification failure was identified and fixed before CS264 was built.
- CS264 regression tests are unittest-native and were discovered by the canonical workflow.
- Phase 18 Story Intelligence Verification run `33284394700` / run number `4081` on SHA `3d00e9f9081a00c84ea130fe60d8a0abafe0166b` completed with **success**.
- `Syntax and discover validation`, `Completion and production isolation`, visual-study handoff construction/verification, cross-platform result composition checks, self-contained brand ownership, Golden editorial v6 verification, and the legacy-logo non-canonical assertion all completed successfully.
- The final log-only commit does not alter executable code; its own workflow state may be newer than the tested implementation SHA and must not be confused with the verified code result above.

## Genuine PNG / GPU status

No genuine Qwen-Image candidate and no Genuine Golden Visual PNG were created in CS264. This change set is post-generation semantic control-plane work.

The generation blocker remains the absence of one proven compatible `$0-local` host satisfying, together: NVIDIA CUDA, native BF16, sufficient live VRAM/system RAM, the exact pinned `Qwen/Qwen-Image-2512` revision, successful `QwenImagePipeline.from_pretrained()`, and successful sequential CPU offload. No model-load, inference, PNG, semantic pass, critic score, Human Review, Golden score, or publication result is fabricated.

The separate Qwen2.5-VL semantic inspector is also fail-closed at runtime: if its dependencies/model execution are unavailable, the production CS264 CLI does not synthesize a clean verdict.

## Remaining gap

The repository now has a continuous planned chain from genuine source bytes through one-shot generation, candidate byte admission, and exact-byte semantic base-scene QA. Remaining work after a real candidate exists is to bind identity-specific evidence where required, feed the complete semantic leakage evidence into the existing final hybrid-layer ownership gate after deterministic/verified composition, bind Visual Critic evidence to the same final pixels, obtain Human Review, enforce Golden minimum `8.5` / elite `9.0`, apply exact brand/typography treatment, and finally pass `SemanticPublicationGate`.
