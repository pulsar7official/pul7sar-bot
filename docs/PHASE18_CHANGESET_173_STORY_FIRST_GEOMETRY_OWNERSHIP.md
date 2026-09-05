# Phase 18 Change Set 173 — Story-First Geometry Ownership

## Scope

This change set is limited to `phase18/story-intelligence`. `main` and `main.py` are not modified.

Golden editorial v6 moved generic football PREVIEW coverage to `context_only` sport-surface visibility. A contextual glimpse of turf may improve depth, but an editorial preview does not require deterministic pitch replacement and the image generator must still never receive authority to invent exact football markings or regulation geometry.

## Problem closed

`LocalBackendRequestCompiler` previously inferred two different decisions from the same condition:

1. whether the generator may own sport geometry; and
2. whether deterministic surface replacement is required.

That coupling was valid for the older Hybrid v5 contract but became wrong for Editorial v6. With `context_only` visibility and no reserved deterministic pitch region, the old inference could produce:

- `generated_sport_geometry_allowed = true`; and
- `hybrid_surface_replacement_required = false`.

The second value is correct for story-first v6 PREVIEW, but the first is unsafe: incidental turf does not grant FLUX authority to fabricate exact pitch markings or geometry.

## Implementation

### Modified — `engine/intelligence/local_backend_execution.py`

The compiler now separates geometry ownership from replacement need.

- VisualGrammar surface modes `none`, `context_only`, `partial_deterministic`, and `full_deterministic` all keep `generated_sport_geometry_allowed = false`.
- `context_only` and `none` do not force deterministic surface replacement.
- `partial_deterministic` and `full_deterministic` require deterministic replacement when the hybrid base-scene contract is active.
- Explicit legacy reserved geometry also continues to require deterministic replacement.
- Packages that predate VisualGrammar metadata keep the previous reserved-content fallback for compatibility.

This preserves the v6 story-first principle: the sport surface is optional context, not a template and not a generator-owned exact layer.

### Modified — `tests/test_phase18_local_backend_execution.py`

Added regression coverage proving:

- `context_only` forbids generated exact sport geometry while keeping replacement disabled; and
- `partial_deterministic` forbids generated geometry and requires deterministic replacement.

Existing zero-cost, prompt-redaction, visual-concept, provenance, seed and canvas tests remain intact.

## Safety / policy preservation

No factual, identity, sentiment, neutrality, cost, semantic-publication or Golden visual-quality gate is weakened.

Unchanged constraints include:

- `$0-local` execution only;
- protected platform branding excluded from generation;
- exact factual content excluded from generation;
- exact sport geometry excluded whenever VisualGrammar declares a known surface mode;
- deterministic exact layers remain downstream-owned when required;
- Qwen semantic inspection and publication gates remain fail-closed;
- Golden quality thresholds remain unchanged.

## Deleted files

None.

## Genuine Golden PNG status

No PNG is claimed by this change set. A genuine Golden Visual still requires a compatible local CUDA/BF16 execution host. This change reduces the remaining gap by ensuring the new story-first v6 request reaches the local backend with correct geometry ownership before GPU execution.
