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
   - output diagnostics now include the Golden prompt contract and character counts.

2. `engine/intelligence/local_backend_execution.py`
   - carries Golden prompt-budget audit metadata into the local portable handoff;
   - no change to zero-cost policy, constraint compilation, protected-name leak detection or exact-layer ownership.

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

A new CPU Regression suite was added and the repository's existing Phase 18 workflows were triggered by the commits. At the time this log entry was created, the final Change Set 161 CI result had not yet been confirmed; no success is claimed until GitHub reports an actual completed successful run.

## Genuine Golden PNG status

No new GPU image is claimed. The exact remaining execution blocker is an available host satisfying all of:

- NVIDIA CUDA;
- native BF16;
- sufficient total VRAM and live free VRAM for the pinned FLUX.2 Klein 4B runtime;
- pinned FLUX cache/runtime revision;
- pinned Qwen cache/runtime revision;
- runtime fingerprint stability across generation.

The current environment used for this implementation does not provide that compatible physical GPU execution path. Candidate 1 therefore remains ungener­ated under the newest architecture, and no fake PNG, synthetic benchmark or visual score was substituted.

## Next executable path

`immutable Phase 18 source -> runtime/model revision locks -> runtime fingerprint -> GPU/live-VRAM gates -> Original Scene admission -> Candidate 1 -> provenance replay -> BASE_SCENE ownership QA -> deterministic football Hybrid -> HYBRID_SURFACE QA -> sealed human review -> Golden 8.5/9.0`

Seeds 2–4 remain unauthorized until Candidate 1 is genuinely generated and accepted through the required semantic and visual review stages.
