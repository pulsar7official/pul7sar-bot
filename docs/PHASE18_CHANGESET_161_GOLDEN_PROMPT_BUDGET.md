# Phase 18 Change Set 161 — Golden Prompt Budget

## Purpose

Reduce the remaining visual-risk gap before the first genuine Golden Hybrid v5 PNG by removing repeated art-direction prose from the benchmark-only FLUX.2 Klein 4B scene prompt, while preserving every factual and exact-layer policy boundary.

The CPU Golden artifact produced before this change compiled Candidate 1 to an 8,352-character local prompt. Inspection showed substantial repetition between the rich provider-neutral scene description and the mandatory positive reframes generated from the same hard constraints. For a 4B local image model, that repetition is unnecessary prompt load and can dilute the primary visual hierarchy.

## Design

`engine/intelligence/golden_prompt_budget.py` introduces the benchmark-specific contract:

- `pul7sar-golden-prompt-budget-v1`
- scene-description budget: 1,200 characters
- benchmark lock: `golden-visual-season-opener-hybrid-v5`

The compact description keeps the intended picture idea: one coherent premium football-stadium atmosphere at dusk, generic/non-identifiable venue, grounded photographic depth, restrained partial turf context, protected editorial negative space, and exact regulation geometry deferred to deterministic composition.

Crucially, compaction does **not** remove or rewrite `GenerationPackage.negative_constraints` or `GenerationPackage.factual_constraints`. Those tuples continue through the existing `PromptConstraintCompiler`, including all provider-positive reframes needed by FLUX because this local backend has no native negative-prompt channel.

The compactor also fails closed unless:

- generated sport geometry remains forbidden;
- generated branding remains forbidden;
- the visual concept was selected before renderer execution;
- the package belongs to the current Golden Hybrid v5 benchmark;
- no PUL7SAR/PULSAR brand token enters the compact scene prompt.

## Runtime integration

`tools/phase18_build_golden_handoff.py` now applies the Golden prompt budget **after** the generic provider-neutral `GenerationPackageCompiler` and **before** `LocalBackendRequestCompiler`.

This preserves the reusable generic story-to-visual architecture while optimizing only the controlled Golden benchmark. The local handoff records the prompt-budget contract, the scene-prompt character budget, the actual compact scene-prompt length, and confirmation that policy boundaries were preserved.

`engine/intelligence/local_backend_execution.py` now carries those audit fields into `LocalBackendGenerationRequest.metadata`; it does not change prompt-policy enforcement or zero-cost execution policy.

## Regression coverage

`tests/test_phase18_golden_prompt_budget.py` verifies:

- exact negative and factual constraint tuples survive compaction unchanged;
- non-Golden packages cannot use the benchmark compactor;
- relaxed generated-geometry or generated-brand ownership is rejected;
- the actual Golden handoff carries the prompt-budget receipt;
- the final local prompt remains below a meaningful character ceiling while retaining factual and mandatory policy sections;
- the protected platform name remains absent from the model prompt.

## Safety / publication invariants

Unchanged:

- Fact Lock and factual integrity;
- Entity / Identity Verification;
- Sentiment and neutrality policy;
- `$0-local` execution policy;
- immutable FLUX.2 Klein 4B and Qwen revisions;
- native BF16 and GPU qualification gates;
- Candidate/request/seed/canvas/SHA locks;
- generated text, branding, exact facts, entity marks and sport geometry prohibitions;
- Qwen BASE_SCENE and HYBRID_SURFACE inspection;
- deterministic football geometry;
- provenance/evidence replay;
- Golden 8.5 minimum / 9.0+ elite quality thresholds;
- Exact Brand Integrity, Typography Integrity and SemanticPublicationGate.

## Files

Added:

- `engine/intelligence/golden_prompt_budget.py`
- `tests/test_phase18_golden_prompt_budget.py`
- `docs/PHASE18_CHANGESET_161_GOLDEN_PROMPT_BUDGET.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_161.md`

Modified:

- `tools/phase18_build_golden_handoff.py`
- `engine/intelligence/local_backend_execution.py`

Deleted: none.

`main` / `main.py`: not modified.

## Genuine-PNG status

No genuine new GPU PNG is claimed by this change set. The remaining physical blocker is still an available NVIDIA CUDA host with native BF16 and sufficient live free VRAM to run the pinned FLUX.2 Klein 4B revision and pinned Qwen semantic verifier. This change is CPU-safe preparatory work intended to improve Candidate 1's signal-to-noise ratio when that host becomes available.
