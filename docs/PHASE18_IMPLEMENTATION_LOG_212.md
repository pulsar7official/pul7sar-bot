# Phase 18 Implementation Log — Change Set 212

## Scope

**Change Set 212: Dynamic Visual Brain End-to-End Concept Binding**

Work performed only on `phase18/story-intelligence`. `main` was reviewed for isolation and was never modified.

## State reviewed before changes

- Phase 18 HEAD: `3e0a9c5990d62e60eedc52900e5c23e4d936d10c`.
- `main` HEAD reviewed independently: `813ef31d2647e4353ca604e60e48975c79d7d95e`.
- Baseline Story Intelligence Verification: GitHub Actions run `33084035748`, run number `3414`, conclusion `success`.
- All companion Phase 18 workflow runs returned for the same baseline HEAD were also `success`.
- Current engineering-preview/T4 paths remain explicitly non-Golden and `publication_ready=false`.

## Problem found

The current Dynamic Visual Brain correctly locks a story-specific concept before rendering and the measured local admission already embeds the following values in the SHA-protected generation request:

- story fingerprint;
- competition SHA-256;
- selected concept ID/SHA-256;
- scene-prompt SHA-256;
- Original Scene request SHA-256;
- `$0-local` and generator-ownership restrictions.

The durable FLUX executor result, however, did not independently expose this concept identity. The existing `VisualCriticProvenanceGate` could prove candidate/request/seed/payload and exact PNG bytes, but it could not prove the complete pre-render Dynamic Visual Brain lock/admission chain.

For a concept-diverse visual competition this is an important gap: a critic verdict must never be transferable from Concept A to a PNG generated from Concept B.

## Code changes

### Added — `engine/intelligence/dynamic_visual_brain_critic_binding.py`

New `DynamicVisualBrainCriticBindingGate`:

1. verifies canonical concept-lock contract and authority closure;
2. verifies canonical measured local-admission contract;
3. proves story fingerprint, competition hash, concept identity/hash and scene-prompt hash match between lock and admission;
4. proves Original Scene request SHA is bound;
5. verifies `$0-local`, semantic inspection, Human review and generator-ownership restrictions;
6. verifies the durable generation result carries the same Dynamic Visual Brain identity plus request/seed/provider/model;
7. delegates PNG/candidate/payload and critic-quality replay to the existing `VisualCriticProvenanceGate` rather than replacing it;
8. leaves Human review required and Golden/publication authority false.

### Modified — `tools/phase18_flux2_execute.py`

Added a fail-closed Dynamic Visual Brain executor-provenance seam.

For Dynamic Visual Brain requests only, the executor now copies a strict whitelist of already-SHA-protected handoff identity into the durable result:

- `dynamic_visual_brain_contract`;
- `dynamic_visual_brain_story_fingerprint`;
- `dynamic_visual_brain_competition_sha256`;
- `dynamic_visual_brain_selected_concept_id`;
- `dynamic_visual_brain_selected_concept_sha256`;
- `dynamic_visual_brain_scene_prompt_sha256`;
- `dynamic_visual_brain_original_scene_request_sha256`;
- `dynamic_visual_brain_selection_locked_before_rendering`;
- top-level `concept_id` for the existing Visual Critic provenance contract.

Before generation it rejects malformed hashes or any drift in `$0-local`, generated branding, exact facts, exact sport geometry, semantic-inspection requirement, Human-review requirement or publication authority.

Non-Dynamic requests remain backward-compatible and receive no extra Dynamic Visual Brain fields.

### Added — `tools/phase18_verify_dynamic_visual_brain_critic_binding.py`

CPU-only replay CLI. It does not run FLUX, mutate a queue, call a paid API, or open publication. It writes a machine-readable binding receipt only after concept/admission/generation/PNG/critic evidence all replay successfully.

### Added — `tests/test_phase18_dynamic_visual_brain_critic_binding.py`

Regression coverage for:

- clean exact concept/PNG binding;
- concept-hash substitution;
- local-admission publication-authority drift;
- Visual Critic geometry hard failure;
- PNG tampering after critic evidence.

### Added — `tests/test_phase18_dynamic_visual_brain_executor_provenance.py`

Regression coverage for:

- executor metadata propagation;
- backward compatibility for non-Dynamic requests;
- generator/publication authority drift;
- missing/malformed hashes.

### Added — documentation

- `docs/PHASE18_CHANGESET_212_DYNAMIC_VISUAL_BRAIN_END_TO_END_CONCEPT_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_212.md`

## Commits produced in this work

- `d0b28b91ad1981640a5c716fcb59c44c72952c53` — bind Dynamic Visual Brain hashes into executor result.
- `35aead2e819d892171e3ec060963de3c1795b658` — add concept/admission-to-critic binding gate.
- `a764b2073e6a41e9b468916f34a33e20f301ed4f` — expose top-level concept ID for existing Visual Critic provenance.
- `15c7cd3a1ba4160a17990464a7d436d9982857b1` — align binding gate to current Visual Critic provenance API.
- `779534829166395a22f1270a106ff5561bc5aaff` — add critic-binding regression suite.
- `b976cb9faf0d5a9d3ab216344fb0700a4e94f64d` — add executor-provenance regression suite.
- `b3086c0552f19bff0475141c21f7dee3b9c0890c` — document Change Set 212.
- `6e39816a989d1c32d4facde1fa2bac545c432a9b` — add CPU replay CLI.

## Deleted

Nothing.

## Safety / quality invariants preserved

No gate was relaxed or bypassed:

- Fact Lock unchanged;
- Entity/Identity Verification unchanged;
- Sentiment/Neutrality and loser-respect unchanged;
- `$0-local` remains mandatory;
- FLUX/Qwen pinned-model and runtime/resource policies unchanged;
- generated platform branding remains forbidden;
- generated exact facts/numbers remain forbidden;
- generated entity marks remain forbidden;
- exact sport geometry remains outside generator ownership;
- Semantic/Layer Ownership inspection remains mandatory;
- Visual Critic hard failures remain fail-closed;
- Human review remains mandatory after critic approval;
- Golden quality remains `8.5` minimum / `9.0+` elite target;
- Exact Brand/Typography Integrity remains downstream;
- SemanticPublicationGate remains downstream;
- `publication_ready=false` throughout this Change Set.

## Testing

Baseline CI before this work was green: Story Intelligence Verification `33084035748 / 3414` = `success`, with all returned companion workflows also successful.

New regression tests have been committed on `phase18/story-intelligence`. Final CI status for the new HEAD must be read from GitHub Actions after the run completes; do not treat Change Set 212 as CI-green until that result is observed.

## Golden Visual status

No new Golden PNG was fabricated in this change. Existing engineering-preview/T4 work remains explicitly non-Golden.

The next genuine GPU-generated concept can now be audited through:

`Verified Story → SHA-locked Dynamic Visual Brain concept → measured $0-local admission → SHA-protected local handoff → genuine FLUX result carrying the same concept hashes → exact PNG bytes → byte-bound Visual Critic → Human Golden Review`

## Remaining blocker / next material step

A new genuine Golden-quality candidate still requires a compatible `$0-local` execution host satisfying the approved CUDA/precision/VRAM/RAM/offload/model/runtime evidence gates. If such a host is unavailable, no PNG should be fabricated.

When a genuine Dynamic Visual Brain candidate is generated, persist the concept-lock and local-admission receipts alongside the generation result and critic evidence, run the new CPU replay CLI, and allow Human Golden Review only if the end-to-end binding succeeds and all existing semantic/visual gates remain green.
