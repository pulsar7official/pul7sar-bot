# PUL7SAR Phase 18 — Implementation Log 161

## Scope / branch safety

- Repository: `pulsar7official/pul7sar-bot`
- Write target: `phase18/story-intelligence` only.
- `main` was reviewed separately and was not modified, merged, rebased, force-updated, or used as a write target.
- Starting Phase 18 HEAD reviewed for this work: `ed24d4be0c0c3815f25423000e26e46ca775f34d` (Change Set 160).
- Change Set 160 verification was confirmed before new work: `Phase 18 Story Intelligence Verification` run `32916663466`, run number `2792`, conclusion `success`.

## Evidence reviewed before implementation

The successful CPU Golden batch artifact from run `32916663466` was inspected directly. Candidate 1's compiled local FLUX prompt measured **8,352 characters**. The prompt repeated several art-direction ideas across:

1. the rich generic `GenerationPackage.scene_prompt`;
2. the factual-constraint section;
3. provider-positive reframes for all hard visual constraints;
4. the final clean-base-scene instruction.

The hard constraints themselves are required and remain intact. The safe optimization target was therefore the benchmark-specific scene prose, not factual/identity/semantic/geometry policy.

## Change Set 161 — Golden Prompt Budget

### Added

1. `engine/intelligence/golden_prompt_budget.py`
   - new contract `pul7sar-golden-prompt-budget-v1`;
   - Golden Hybrid v5 benchmark lock;
   - deterministic 1,200-character scene-description budget;
   - compact single-scene football-atmosphere direction;
   - fail-closed checks for generated geometry, generated branding, visual-concept ownership and platform-name leakage;
   - uses `dataclasses.replace` so all non-scene `GenerationPackage` fields and exact constraint tuples survive unchanged.

2. `tests/test_phase18_golden_prompt_budget.py`
   - exact negative/factual constraint preservation;
   - non-Golden rejection;
   - relaxed geometry/brand ownership rejection;
   - actual Golden handoff integration;
   - final compiled-prompt ceiling;
   - protected platform-name absence.

3. `docs/PHASE18_CHANGESET_161_GOLDEN_PROMPT_BUDGET.md`

4. `docs/PHASE18_IMPLEMENTATION_LOG_161.md`

### Modified

1. `tools/phase18_build_golden_handoff.py`
   - generic provider-neutral package is still built first;
   - GoldenPromptBudget is applied only to the controlled v5 benchmark before local compilation;
   - benchmark identity is supplied explicitly at this trusted Golden builder boundary because the generic compiler intentionally does not propagate arbitrary benchmark-only scene metadata;
   - output diagnostics include the Golden prompt contract and character counts.

2. `engine/intelligence/local_backend_execution.py`
   - carries Golden prompt-budget audit metadata into the local portable handoff;
   - no change to zero-cost policy, constraint compilation, protected-name leak detection or exact-layer ownership.

3. `engine/intelligence/golden_prompt_budget.py` after CI feedback
   - removed the invalid assumption that generic `GenerationPackageCompiler` propagates a `benchmark` label or a precomputed `generated_sport_geometry_allowed` field;
   - the trusted Golden builder now supplies `benchmark_id` explicitly;
   - geometry ownership is proven from the generic package's real `hybrid_base_scene_contract` plus `reserved_base_scene_content`;
   - restored compact versions of the existing unified-scene, non-identifiable venue/person, European-football, partial-surface and no-collage policy markers required by Golden smoke/batch verification, while remaining inside the 1,200-character scene budget.

4. `tests/test_phase18_golden_prompt_budget.py` after CI feedback
   - fixtures mirror the real generic package contract;
   - tests still fail closed for benchmark drift, branding relaxation, missing hybrid contract, or missing code-owned sport geometry.

### Deleted

None.

## Gate preservation

No relaxation was made to:

- Fact Lock / factual integrity;
- Entity and Identity Verification;
- Sentiment / neutrality;
- `$0-local` economics;
- pinned FLUX.2 Klein 4B revision;
- pinned Qwen revision;
- native BF16 requirement;
- total/live free-VRAM and lease-bound GPU requalification;
- Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact facts/entity marks/sport-geometry prohibitions;
- Original Scene runtime admission;
- Qwen BASE_SCENE and HYBRID_SURFACE gates;
- deterministic football geometry and artifact-integrity replay;
- Golden visual-quality thresholds: 8.5 minimum, 9.0+ elite;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate / Final Publication Readiness.

The optimization intentionally leaves `negative_constraints` and `factual_constraints` unchanged. Provider-positive reframing remains mandatory because the current local FLUX backend has no native negative-prompt path.

## Tests / CI

The first full Story Intelligence run for the initial implementation, run `32920828364` / run number `2794`, failed in `Syntax and discover validation`. Root cause: the first compactor implementation expected benchmark/exact-geometry fields that the generic provider-neutral `GenerationPackageCompiler` intentionally does not publish. That contract mismatch was corrected without broadening permissions.

The second Story Intelligence run, `32921129263` / run number `2800`, executed **1,173 Phase 18 tests** and failed with 5 failures / 7 errors. The new dedicated prompt-budget tests themselves all passed. The remaining failures revealed that legacy/current Golden smoke and batch verification intentionally uses exact textual safety markers as an additional fail-closed lock. Compaction had retained the equivalent rules semantically through factual/provider-positive policy but had changed some exact marker wording, causing the verifier to reject the handoff before downstream assertions.

This second failure was corrected by restoring concise versions of the required markers directly inside the compact scene prompt, including:

- `one single continuous full-bleed editorial image`;
- `Never use collage, montage, split-screen, grid, diptych, triptych`;
- `European football` / `season-opening`;
- explicit non-identifiable venue and no real-person claims;
- restrained partial sport-surface context and no full-pitch visual dominance.

These phrases are safety/visual-contract markers rather than decorative prose, so they were preserved instead of weakening or rewriting the existing Golden verifier. The compact scene text remains inside the locked 1,200-character budget. A new corrected head was pushed after this finding. Final Story Intelligence CI success for that corrected head is not claimed until an actual completed successful run is observed.

## Genuine Golden PNG status

No new GPU image is claimed. The exact remaining execution blocker is an available host satisfying all of:

- NVIDIA CUDA;
- native BF16;
- sufficient total VRAM and live free VRAM for the pinned FLUX.2 Klein 4B runtime;
- pinned FLUX cache/runtime revision;
- pinned Qwen cache/runtime revision;
- runtime fingerprint stability across generation.

The current environment used for this implementation does not provide that compatible physical GPU execution path. Candidate 1 therefore remains ungenerated under the newest architecture, and no fake PNG, synthetic benchmark or visual score was substituted.

## Next executable path

`immutable Phase 18 source -> runtime/model revision locks -> runtime fingerprint -> GPU/live-VRAM gates -> Original Scene admission -> Candidate 1 -> provenance replay -> BASE_SCENE ownership QA -> deterministic football Hybrid -> HYBRID_SURFACE QA -> sealed human review -> Golden 8.5/9.0`

Seeds 2–4 remain unauthorized until Candidate 1 is genuinely generated and accepted through the required semantic and visual review stages.
