# Phase 18 Change Set 163 — Verified Venue Marker Restore

## Scope

Branch: `phase18/story-intelligence` only. `main` is not modified.

## Problem found

Story Intelligence Verification run `32924186220 / 2820` executed 1,173 Phase 18 tests and failed on one regression only:

`test_phase18_golden_handoff.GoldenVisualHandoffTests.test_golden_request_uses_real_phase18_layout_and_zero_cost_model`

The compact Golden v5 prompt still expressed the same non-identifying venue policy, but the provider positive reframe no longer contained the older fail-closed marker:

` specific real venue identity without verified reference `

The remaining 1,172 tests passed, including zero-cost, identity, neutrality, deterministic football geometry, semantic gates, provenance, Qwen, FLUX model-revision locks, and Golden quality gates.

## Change

`engine/intelligence/provider_prompting.py`

The canonical positive reframe for `no specific identifiable real venue` now explicitly says:

> Treat any specific real venue identity without verified reference as forbidden...

and retains the existing instruction to use a deliberately non-identifying venue with generic architecture and no distinctive landmark, signage, club-specific decoration, or other cue implying a particular real stadium or arena.

This restores the exact fail-closed semantic marker without expanding the compact scene prompt, weakening provider constraint translation, or allowing venue claims.

## Safety invariants preserved

- Fact Lock unchanged.
- Entity/Identity Verification unchanged.
- Sentiment/Neutrality unchanged.
- `$0-local` unchanged.
- FLUX.2 Klein 4B model and pinned revision unchanged.
- Qwen model and pinned revision unchanged.
- Native BF16 requirement unchanged.
- Candidate/request/seed/canvas/SHA locks unchanged.
- Generated branding, text, exact facts, entity marks, and sport geometry remain forbidden.
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` gates unchanged.
- Deterministic football geometry unchanged.
- Golden quality floor remains 8.5 minimum / 9.0+ elite.
- Exact Brand/Typography and SemanticPublicationGate unchanged.
- No PNG, benchmark score, or GPU result is fabricated.

## Files

Added:
- `docs/PHASE18_CHANGESET_163_VERIFIED_VENUE_MARKER_RESTORE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_163.md`

Modified:
- `engine/intelligence/provider_prompting.py`

Deleted: none.

## Remaining blocker

A genuine Golden Hybrid v5 Candidate 1 still requires a compatible NVIDIA CUDA host with native BF16 and sufficient live free VRAM to run the pinned FLUX.2 Klein 4B revision and pinned Qwen semantic verifier. CPU CI cannot produce that PNG, and no substitute result is accepted.
