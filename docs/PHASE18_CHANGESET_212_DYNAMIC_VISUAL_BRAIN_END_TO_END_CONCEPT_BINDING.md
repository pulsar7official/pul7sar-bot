# Phase 18 Change Set 212 — Dynamic Visual Brain End-to-End Concept Binding

## Objective

Close the remaining provenance gap between a story-specific Dynamic Visual Brain concept selected before rendering and the exact PNG/Visual Critic decision produced after rendering.

A concept must not be able to win by inheriting a critic decision from another concept, request, seed, or PNG. This change therefore carries the SHA-locked Dynamic Visual Brain identity into the durable FLUX executor result and adds a fail-closed binding gate from concept lock + measured local admission through exact PNG bytes and the existing Visual Critic provenance.

## Branch isolation

- Target branch: `phase18/story-intelligence` only.
- `main` was reviewed but never modified, merged, force-updated, or used as a write target.
- Baseline Phase 18 HEAD reviewed before this change: `3e0a9c5990d62e60eedc52900e5c23e4d936d10c`.
- Baseline `main` reviewed independently: `813ef31d2647e4353ca604e60e48975c79d7d95e`.
- Baseline Story Intelligence Verification run `33084035748 / 3414` was `success`, as were all companion Phase 18 workflows returned for that HEAD.

## Added

### `engine/intelligence/dynamic_visual_brain_critic_binding.py`

Adds `DynamicVisualBrainCriticBindingGate` and a tamper-evident receipt. The gate verifies:

1. the concept lock is the canonical `pul7sar-dynamic-visual-brain-concept-lock-v1` contract;
2. the concept was selected before rendering and cannot authorize generation, Human approval, Golden approval, publication, or seeds 2–4;
3. the local admission is the canonical `$0-local` Dynamic Visual Brain admission and matches the same story fingerprint, competition SHA, concept ID/SHA, scene-prompt SHA, request ID, and seed;
4. branding, exact facts, and exact sport geometry remain outside generator ownership;
5. semantic inspection and human review remain mandatory;
6. the durable generation result repeats the exact locked Dynamic Visual Brain hashes plus the Original Scene request SHA;
7. the generation result remains a real visual proof, `$0-local`, and `publication_ready=false`;
8. the existing `VisualCriticProvenanceGate` independently replays candidate/request/seed/payload identity and exact PNG bytes;
9. Visual Critic acceptance remains only a critic decision — Human review is still required, Golden quality remains false, and publication remains false.

### `tests/test_phase18_dynamic_visual_brain_critic_binding.py`

Regression coverage for:

- successful exact concept/request/PNG binding;
- selected-concept hash drift;
- local-admission publication-authority drift;
- Visual Critic geometry hard failure remaining rejected;
- PNG tampering after critic evidence.

### `tests/test_phase18_dynamic_visual_brain_executor_provenance.py`

CPU-only regression coverage for the executor metadata seam:

- whitelisted Dynamic Visual Brain identity is copied into the durable result;
- non-Dynamic requests remain backward-compatible;
- generator/publication authority drift is rejected before execution;
- missing or invalid Dynamic Visual Brain hashes fail closed.

## Modified

### `tools/phase18_flux2_execute.py`

The real FLUX.2 executor now exposes a strictly whitelisted set of SHA-protected Dynamic Visual Brain identity fields from the already-verified local handoff into its durable result:

- Dynamic Visual Brain contract;
- story fingerprint;
- competition SHA-256;
- selected concept ID and SHA-256;
- scene-prompt SHA-256;
- Original Scene request SHA-256;
- selection-locked-before-rendering flag;
- top-level `concept_id` for compatibility with the existing byte-bound Visual Critic provenance contract.

The executor refuses this propagation if any required hash is malformed or if `$0-local`, generator ownership, semantic-review, human-review, or publication authority has drifted. No new authority is granted to generation.

## Deleted

Nothing.

## Gates preserved

No factual, identity, sentiment, zero-cost, semantic-publication, or visual-quality gate was weakened. In particular:

- Fact Lock remains unchanged;
- Entity/Identity Verification remains unchanged;
- Sentiment/Neutrality and loser-respect policy remain unchanged;
- generation remains `$0-local`;
- protected platform branding, exact facts, entity marks, and exact sport geometry remain outside generator ownership;
- semantic inspection remains mandatory;
- Visual Critic hard failures remain fail-closed;
- Human visual review remains mandatory after critic acceptance;
- Golden floor remains `8.5`, with `9.0+` elite target;
- Exact Brand/Typography Integrity and SemanticPublicationGate remain downstream and mandatory;
- `publication_ready` remains false throughout this change.

## Why this materially reduces the Golden gap

The Dynamic Visual Brain is now concept-diverse rather than seed-diverse. That makes concept identity a first-class provenance requirement. Before this change, the local request carried the correct story/concept hashes, while the durable FLUX result and Visual Critic replay did not independently prove the full chain.

After this change the intended chain is:

`Verified Story → SHA-locked concept → measured $0-local admission → exact FLUX request → durable result carrying the same concept hashes → exact PNG bytes → byte-bound Visual Critic → Human Golden Review`

A concept can no longer win using a critic verdict that belongs to a different concept or PNG.

## Validation status

The baseline HEAD was CI-green before this change. New code and tests have been pushed to `phase18/story-intelligence`; final CI for Change Set 212 must be read from the resulting GitHub Actions run before this change is called CI-green.

## Remaining blocker

This change does not fabricate a new Golden PNG. A new genuine candidate still requires a compatible local/self-hosted execution host satisfying the currently approved `$0-local` runtime/resource/model contracts. Existing engineering-preview paths remain non-Golden and cannot substitute for a Golden-quality result.
