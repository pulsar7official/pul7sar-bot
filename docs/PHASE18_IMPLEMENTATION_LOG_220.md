# Phase 18 Implementation Log — Change Set 220

## Branch isolation

Target branch: `phase18/story-intelligence` only.

State reviewed before writing:
- Phase 18 HEAD: `3bf5ad5a25ca8a9d84c680d31b8589539a2845f0`
- `main` was reviewed independently and later observed at `198accbdce120034c4df9cff270eb46347c5f77e` due an independent posted-history update.
- branch comparison remained `diverged`.

No file was written to `main`; no merge, force-update, or `main.py` modification was performed.

## Baseline CI evidence

Change Set 219 is verified green.

For Phase 18 commit `3bf5ad5a25ca8a9d84c680d31b8589539a2845f0`, the GitHub workflow set includes:
- Phase 18 Story Intelligence Verification run `33120266380` / run number `3540`: `success`;
- Composition Matrix Verification run `33120266612`: `success`;
- Event Editorial Visual Study run `33120267508`: `success`;
- Tactical Intelligence Visual Study run `33120266512`: `success`;
- Result Statement Visual Study run `33120266395`: `success`;
- Premium Hybrid Result Visual Study run `33120266379`: `success`;
- Event Hybrid Context Study run `33120266371`: `success`;
- Data Monument Visual Study run `33120266392`: `success`;
- Verified Match Result Visual Study run `33120265706`: `success`; and
- Adaptive Brand Pixel Verification run `33120266386`: `success`.

This closes the pending-CI note left in Implementation Log 219.

## Gap identified

The isolated ZeroGPU renderer benchmark was already:
- entity-neutral;
- platform-name-free;
- PNG/SHA-bound;
- engineering-only; and
- prohibited from canonical Golden or publication authority.

However, renderer comparison still lacked a durable research ledger binding human quality judgments to the exact benchmark PNG bytes. A reviewer could otherwise record scores for one output while a benchmark report later pointed at different bytes, or a visually attractive result with a hard geometry/pseudo-text/entity failure could be remembered as the preferred renderer without reproducible evidence.

Because canonical CUDA execution is currently unavailable, improving the quality of renderer selection research is safe preparatory work that reduces the risk of wasting a future qualified `$0-local` GPU session.

## Implemented work

### Commit `bfca2c9bf18c9f8e897a8d2e1c112be0127daba2`
Added:
- `engine/intelligence/remote_renderer_research_ledger.py`

Behavior:
- accepts only remote benchmark schema v3 and `$0-remote-zerogpu-study`;
- requires entity-neutral engineering-only authority closure;
- replays output PNG signature, SHA-256, byte size, prompt SHA, renderer and seed continuity;
- requires human-review evidence bound to the exact output SHA;
- scores editorial composition, photorealism, geometry integrity, scene continuity, entity neutrality, and text/brand cleanliness;
- applies hard blockers for broken geometry, pseudo-text, identifiable entity cues, collage/multi-scene output, and generated brand/crest;
- permits only a research-only leader, never canonical admission;
- always preserves `canonical_golden_eligible=false`, `semantic_approved=false`, `golden_quality_approved=false`, and `publication_ready=false`.

### Commit `74895a2a99195f2db463ce7c25c317b8755bc3df`
Added:
- `tools/phase18_build_remote_renderer_research_ledger.py`

Behavior:
- CPU-only research-ledger builder/replay utility;
- repository-path constrained;
- no FLUX/Qwen execution;
- no queue mutation;
- no paid-provider or publication authority.

### Commit `f9cbd1954a2006aebf728beac2eda9580eecbfbd`
Added:
- `tests/test_phase18_remote_renderer_research_ledger.py`

Regression coverage:
- successful byte-bound research ledger;
- PNG tampering detection;
- hard blocker defeating a 9.9 score;
- review/output SHA mismatch rejection;
- remote result canonical-authority drift rejection;
- path-escape rejection.

### Commit `6d22393bdb22eb30f80c432345f2cb81844163e8`
Added:
- `docs/PHASE18_CHANGESET_220_REMOTE_RENDERER_RESEARCH_LEDGER.md`

### Documentation commit
Added:
- `docs/PHASE18_IMPLEMENTATION_LOG_220.md`

## Added / modified / deleted

Added:
- `engine/intelligence/remote_renderer_research_ledger.py`
- `tools/phase18_build_remote_renderer_research_ledger.py`
- `tests/test_phase18_remote_renderer_research_ledger.py`
- `docs/PHASE18_CHANGESET_220_REMOTE_RENDERER_RESEARCH_LEDGER.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_220.md`

Modified production/runtime files:
- none.

Deleted:
- none.

## Gates preserved

No canonical gate was weakened or bypassed.

Still fail-closed:
- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality and respectful loser treatment;
- canonical `$0-local` execution policy;
- generated text/branding/exact facts/entity marks/exact sport geometry exclusions;
- pinned/model/runtime evidence requirements;
- Semantic and Layer Ownership gates;
- byte-bound Visual Critic hard failures;
- explicit Human Review;
- Golden quality floor 8.5 and 9.0+ elite target;
- Exact Brand Integrity;
- Typography Integrity; and
- SemanticPublicationGate.

The new remote research ledger remains explicitly non-canonical:
- `cost_mode = $0-remote-zerogpu-study`;
- `research_only = true`;
- `canonical_admission_required = true`;
- `canonical_golden_eligible = false`;
- `semantic_approved = false`;
- `golden_quality_approved = false`;
- `publication_ready = false`.

## Test status for Change Set 220

The code, CLI, regression tests, and documentation have been pushed to `phase18/story-intelligence`.

GitHub Actions is expected to run on the resulting branch head. Final Change Set 220 CI status must be taken only from a completed Story Intelligence Verification run on the new head. No CI result is fabricated in this log.

## Golden Visual progress / remaining blocker

No new accepted canonical Golden Visual PNG was generated in Change Set 220.

The repository already has genuine rejected visual attempts; the target remains the first accepted genuine canonical Golden Visual PNG.

Canonical generation remains externally blocked until an approved `$0-local` host is available with the required combination of CUDA, supported precision, sufficient live VRAM and system RAM, safe local offload/runtime, pinned model evidence, and the existing semantic/provenance gates.

Change Set 220 reduces the remaining gap without weakening that rule: remote ZeroGPU output can now be compared by exact bytes and hard-failure-aware human research scores, helping identify which renderer behavior is worth future canonical qualification. A remote research leader still cannot be promoted into Golden evidence directly.
