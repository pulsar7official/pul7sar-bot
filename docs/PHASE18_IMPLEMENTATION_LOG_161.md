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
   - exact Golden v5 semantic-marker preservation;
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
   - removed the invalid assumption that generic `GenerationPackageCompiler` propagates a benchmark label or precomputed generated-sport-geometry field;
   - the trusted Golden builder supplies `benchmark_id` explicitly;
   - geometry ownership is proven from the real hybrid-base-scene contract plus `reserved_base_scene_content`;
   - preserves exact unified-scene and Golden-v5 semantic safety markers inside the compact scene budget, including the code-owned reserved surface, no field/court/rink lines, deterministic surface replacement, fully unbranded base, and platform-name exclusion markers.

4. `tests/test_phase18_golden_prompt_budget.py` after CI feedback
   - fixtures mirror the real generic package contract;
   - tests fail closed for benchmark drift, branding relaxation, missing hybrid contract, missing code-owned sport geometry, or loss of any exact v5 semantic marker.

### Deleted

None.

## Gate preservation

No relaxation was made to Fact Lock / factual integrity, Entity and Identity Verification, Sentiment / neutrality, `$0-local` economics, pinned FLUX.2 Klein 4B revision, pinned Qwen revision, native BF16, total/live-free VRAM and lease-bound GPU requalification, Candidate/request/seed/canvas/SHA locks, generated text/branding/exact facts/entity marks/sport-geometry prohibitions, Original Scene runtime admission, Qwen BASE_SCENE/HYBRID_SURFACE, deterministic football geometry, provenance/evidence replay, Golden 8.5 minimum / 9.0+ elite thresholds, Exact Brand Integrity, Typography Integrity, or SemanticPublicationGate / Final Publication Readiness.

The optimization leaves `negative_constraints` and `factual_constraints` unchanged. Provider-positive reframing remains mandatory because the current local FLUX backend has no native negative-prompt path.

## Tests / CI chronology

- Run `32920828364` / `2794`: failed in CPU discovery because the initial compactor incorrectly expected benchmark-only metadata inside the generic provider-neutral `GenerationPackage`. Fixed by supplying benchmark identity at the trusted Golden builder boundary and checking real generic ownership fields.
- Run `32921129263` / `2800`: executed 1,173 Phase 18 tests. Dedicated GoldenPromptBudget tests passed, while existing Golden smoke/batch tests exposed exact textual safety markers that must remain present. No verifier was weakened.
- Run `32921315894` / `2804`: after restoring unified-scene/non-identifying visual markers, all three direct Golden handoff tests and the new prompt-budget tests passed. The remaining failures precisely identified five current v5 semantic markers enforced by both `golden_smoke.py` and `phase18_verify_golden_batch.py`: `reserved surface region plain and unmarked`, `no field/court/rink lines`, `the exact surface will be replaced by deterministic code after generation`, `fully unbranded`, and `platform names`. These exact markers were then restored inside the 1,200-character compact scene prompt; corresponding regression assertions were added. Companion visual-study workflows for the same code line were otherwise successful.
- Corrected code/test HEAD: `f2673ae893cb6122d5a0f6eccf096e15af0acd35`. Story Intelligence run `32921494672` / `2810` is in progress at the time of this log update. No final CI success is claimed until that run completes successfully.

## Genuine Golden PNG status

No new GPU image is claimed. The exact remaining physical execution blocker is an available host satisfying NVIDIA CUDA, native BF16, sufficient total and live-free VRAM for the pinned FLUX.2 Klein 4B runtime, pinned FLUX and Qwen cache/runtime revisions, and runtime-fingerprint stability across generation.

The current implementation environment does not provide that compatible physical GPU execution path. Candidate 1 therefore remains ungenerated under the newest architecture; no fake PNG, synthetic benchmark, or visual score was substituted.

## Next executable path

`immutable Phase 18 source -> runtime/model revision locks -> runtime fingerprint -> GPU/live-VRAM gates -> Original Scene admission -> Candidate 1 -> provenance replay -> BASE_SCENE ownership QA -> deterministic football Hybrid -> HYBRID_SURFACE QA -> sealed human review -> Golden 8.5/9.0`

Seeds 2–4 remain unauthorized until Candidate 1 is genuinely generated and accepted through the required semantic and visual review stages.
