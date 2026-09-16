# PUL7SAR Phase 18 — Implementation Log 163

## Branch isolation

- Target branch: `phase18/story-intelligence`.
- `main` was reviewed but not modified, merged, force-updated, or used as a write target.
- Branch state at review time: `diverged`; Phase 18 was 1,441 commits ahead of `main` and 159 behind.
- Reviewed Phase 18 HEAD before this change: `89c4e197f5304e2bc70b812ba5c237ecc405e119`.
- Reviewed `main` HEAD: `6b77770630c2f4ce84b67c477b291eca058ee182`.

## CI diagnosis carried into this change

Story Intelligence Verification run `32924186220 / 2820` completed with `failure` in `Syntax and discover validation` after running 1,173 Phase 18 tests.

Exactly one regression failed:

`test_phase18_golden_handoff.GoldenVisualHandoffTests.test_golden_request_uses_real_phase18_layout_and_zero_cost_model`

Expected marker missing from the compiled prompt:

` specific real venue identity without verified reference `

The compiled prompt still contained the new compact policy (`must not imply a specific real venue`) and the generic non-identifying venue reframe, so the issue was compatibility with the existing fail-closed Golden handoff contract, not a relaxation of venue policy.

## Code change

### Modified — `engine/intelligence/provider_prompting.py`

The `_NON_IDENTIFYING_VENUE` positive reframe now begins by explicitly forbidding any `specific real venue identity without verified reference`, then retains the existing generic-architecture/no-landmark/no-club-cue instructions.

Reason:

1. restore the exact Golden v5 fail-closed contract that CI enforces;
2. keep the compact Golden scene prompt intact rather than re-expanding benchmark art direction;
3. preserve provider-positive reframe completeness for FLUX-like runtimes without native negative prompts;
4. preserve factual safety by making the venue constraint stricter and explicit rather than weakening the regression test.

## Added

- `docs/PHASE18_CHANGESET_163_VERIFIED_VENUE_MARKER_RESTORE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_163.md`

## Modified

- `engine/intelligence/provider_prompting.py`

## Deleted

None.

## Gates preserved

Unchanged and still fail-closed:

- factual integrity / Fact Lock;
- Entity/Identity Verification;
- Sentiment and result neutrality;
- `$0-local` execution policy;
- pinned FLUX.2 Klein 4B model revision;
- pinned Qwen semantic model revision;
- native BF16 and GPU/live-free-VRAM qualification;
- lease-bound GPU requalification;
- Candidate/request/seed/canvas/SHA locks;
- prohibition on generated platform branding, exact text/numbers, entity marks, and sport geometry;
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` semantic gates;
- deterministic football geometry ownership;
- provenance/evidence replay;
- Golden Visual Quality: 8.5 minimum, 9.0+ elite;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate and final publication readiness.

## Tests

Pre-change evidence:

- Story Intelligence Verification `32924186220 / 2820`: failed one of 1,173 Phase 18 tests, specifically the venue marker regression above.
- Companion Phase 18 workflows on the same source HEAD completed successfully.

Post-change status:

- Code fix commit: `95b871939b5a8ab278085579a6a6daaf07944d20`.
- CI for the new documentation/code HEAD is expected to run automatically; do not record it as green until GitHub reports a completed successful Story Intelligence Verification run.

## Golden PNG status

No new Golden Hybrid v5 PNG exists from this change. CPU CI cannot produce a genuine FLUX.2 Klein Candidate 1. No placeholder, fake visual, synthetic benchmark score, or publication claim was created.

Exact external blocker remains a real host that simultaneously proves:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live free VRAM for the locked FLUX.2 Klein 4B path;
- pinned FLUX and Qwen snapshots;
- stable runtime fingerprint through generation and semantic inspection.

When such a host becomes available, continue with Candidate 1 only, then provenance replay → `BASE_SCENE` ownership QA → deterministic football Hybrid → `HYBRID_SURFACE` QA → sealed human review → Golden 8.5/9.0. Seeds 2–4 remain unauthorized until Candidate 1 is genuinely produced and accepted.
