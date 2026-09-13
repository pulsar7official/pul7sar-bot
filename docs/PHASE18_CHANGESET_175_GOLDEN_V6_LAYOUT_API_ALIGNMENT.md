# Phase 18 Change Set 175 — Golden v6 Layout API Alignment

## Purpose

Repair the remaining current-API migration blocker in the story-first Golden Editorial v6 builder without weakening any factual, identity, sentiment, zero-cost, semantic, geometry-ownership, visual-quality or publication gate.

## Failure analyzed

Story Intelligence Verification run `32983444631` executed 1,226 Phase 18 tests. The direct first-PNG/Qwen-v2 tests from Change Set 174 passed, but 34 Golden-related tests failed from one shared builder exception:

`TypeError: DeterministicLayoutPlanner.plan() got an unexpected keyword argument 'platform'`

The current deterministic layout contract is profile-first:

`plan(profile: PlatformImageProfile, requirements: LayoutRequirements = ..., *, entity_accent_hex=None)`

The Golden v6 builder still used an older semantic-parameter call (`platform`, `sentiment`, `exact_score_required`, `dominant_entity`).

## Change

### Modified `tools/phase18_build_golden_handoff.py`

- replaced the stale layout call with `DeterministicLayoutPlanner().plan(profile)`;
- retained the default PREVIEW layout requirements: hero, logo, headline and social footer; no score or crest;
- removed the now-unused sentiment import;
- did not introduce result, identity or winner semantics into a generic PREVIEW layout;
- kept the story-first v6 contracts unchanged:
  - `context_only` football surface visibility;
  - generated exact sport geometry forbidden;
  - no deterministic pitch replacement for this generic PREVIEW;
  - visual concept selected before renderer;
  - story focal hierarchy before sport surface;
  - generated branding forbidden;
  - dynamic deterministic brand/typography downstream;
  - `$0-local` FLUX handoff;
  - publication remains blocked.

## Deleted

None.

## Quality and safety impact

This is API alignment only. It does not lower any visual-quality threshold or change the Golden creative policy. The purpose is to let the current story-first v6 handoff build again so CPU verification can reach the actual Golden policy assertions and, later, a compatible GPU can execute Candidate 1 without failing on stale deterministic-layout arguments.

## GPU status

No genuine Golden PNG is claimed. A compatible NVIDIA CUDA/native-BF16/resource-qualified host is still required for real FLUX/Qwen execution. No placeholder or fabricated visual result was produced.