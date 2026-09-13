# Phase 18 Change Set 178 — Golden v6 Local Backend API Alignment

## Scope

Branch: `phase18/story-intelligence` only. `main` and `main.py` were not modified, merged, force-updated, or used as write targets.

## Why this change was required

The current Golden Editorial v6 builder had completed the migration to the Profile-first layout API but still invoked `LocalBackendRequestCompiler.compile_portable_handoff()` with the obsolete keyword `profile=`. The current compiler contract accepts `model=` plus an explicit `backend=`.

Story Intelligence Verification run `32991990098` executed 1,240 Phase 18 tests and failed with 34 errors that shared this root cause:

`TypeError: LocalBackendRequestCompiler.compile_portable_handoff() got an unexpected keyword argument 'profile'`

The failure cascaded through Golden handoff, batch, smoke, Original Scene admission, prompt-budget, unified-scene, and Golden batch verification tests. Companion Phase 18 visual workflows on the same source commit were otherwise successful, and the strict first-genuine-Golden tests themselves passed.

## Code change

Updated `tools/phase18_build_golden_handoff.py` to call the current local-backend compiler contract:

- `model=FLUX2_KLEIN_4B_LOCAL`
- `backend=FLUX2_KLEIN_4B_LOCAL.runtime_adapter`

instead of the obsolete `profile=FLUX2_KLEIN_4B_LOCAL` argument.

This keeps the already-approved zero-cost model identity and resolves the backend from the model's locked runtime adapter (`diffusers`) rather than hard-coding a parallel value.

## Gates preserved

No factual, identity, sentiment, neutrality, cost, semantic, or visual-quality policy was relaxed. The change preserves:

- Fact Lock and sports fact integrity.
- Entity/Identity Verification.
- Sentiment/Neutrality and loser-respect rules.
- `$0-local` execution only.
- Pinned FLUX and Qwen revisions.
- Native BF16 and GPU/VRAM/RAM/offload/runtime-fingerprint gates.
- Candidate/request/seed/canvas/SHA locks.
- No generated platform branding, readable text, exact facts, entity marks, or exact sport geometry.
- Qwen semantic inspection.
- Golden quality floor `8.5` and elite tier `9.0+`.
- Exact Brand Integrity, Typography Integrity, and SemanticPublicationGate.
- Golden Editorial v6 story-first `context_only` surface policy with no preview pitch replacement.
- Seeds 2–4 remain unauthorized until genuine Candidate 1 is visually accepted.

## Files

### Modified

- `tools/phase18_build_golden_handoff.py`

### Added

- `docs/PHASE18_CHANGESET_178_GOLDEN_V6_LOCAL_BACKEND_API_ALIGNMENT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_178.md`

### Deleted

- None.

## Test status

The preceding failing run was `32991990098` with 1,240 tests and 34 errors caused by the obsolete compiler keyword. A fresh Story Intelligence Verification run is required on the corrected branch head before this change set may be described as CI-green.

## Genuine Golden PNG status

No genuine Golden Editorial v6 Candidate 1 PNG is claimed in this change set. The remaining execution blocker is external: no currently available host in this environment proves all required conditions simultaneously — NVIDIA CUDA, native BF16, sufficient total/live-free VRAM, sufficient live system RAM through lease/execution, safe local Diffusers offload/runtime, pinned FLUX/Qwen revisions, stable runtime fingerprint, and `$0-local` execution.

The next genuine path remains:

`immutable Phase 18 source → pinned runtime/models → resource gates → strict Candidate 1 generation → exact PNG/provenance replay → Qwen BASE_SCENE ownership approval → composition-map lock → human Golden review → Golden 8.5/9.0 → exact brand/typography → SemanticPublicationGate`
