# PUL7SAR Phase 18 — Implementation Log 152

## Branch isolation

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Starting Phase 18 HEAD observed: `95b6b20326a9f9d47679b74549cc17729f1ba3fd`.
- `main` HEAD observed during this run: `a94710381bcd6a1cb152672a65b89aee6dcf1bb7`.
- Starting comparison: Phase 18 remained `diverged` from `main`, 1359 commits ahead and 136 behind.
- PR #1 remained open, Draft and unmerged.
- `main` was reviewed only and was never modified, merged, force-updated or used as a write target.

## Existing state reviewed first

The starting Phase 18 HEAD was rechecked before new writes. Story Intelligence Verification run `32868671312 / 2628` completed with `success`; every returned companion Phase 18 workflow for the same commit also completed with `success`.

The canonical first-Golden workflow already had:

- manual `workflow_dispatch` confirmation;
- self-hosted CUDA/BF16-only execution;
- `$0-local` policy;
- immutable `${{ github.sha }}` checkout;
- complete Git ancestry for merge-base isolation;
- fail-closed `main.py` isolation;
- strict Qwen/FLUX Candidate 1 staging;
- provenance/evidence replay;
- BASE_SCENE and HYBRID_SURFACE semantic gates;
- deterministic football geometry;
- sealed human-review staging;
- Human/Golden/Publication authority closed by default.

## Gap identified

The immutable raw-SHA checkout introduced for reproducibility leaves Git in detached-HEAD state.

The strict Phase 18 runtime intentionally checks the active branch using `git branch --show-current` and requires exactly `phase18/story-intelligence`. This is enforced by both `tools/phase18_colab_first_golden_bootstrap.py` and the repository-integrity preflight.

Therefore the canonical self-hosted GPU workflow could pass its immutable-SHA proof and still fail before any useful Candidate 1 work because the runtime would observe an empty current branch name.

This was a genuine pre-GPU execution blocker hidden by CPU workflow-text tests. It was not a visual-quality, semantic-quality or publication-quality failure.

## Change Set 152 — Immutable Branch Reattachment

### Modified

- `.github/workflows/phase18-first-golden-review.yml`
  - preserves immutable `${{ github.sha }}` checkout and `fetch-depth: 0`;
  - proves `HEAD` equals the dispatched SHA before reattachment;
  - creates/reattaches a local `phase18/story-intelligence` branch at the exact dispatched SHA using `git checkout -B`;
  - proves the active branch name is exactly `phase18/story-intelligence`;
  - proves `HEAD` still equals the immutable dispatched SHA after reattachment;
  - performs this before CUDA and before the strict Candidate 1 bootstrap;
  - keeps read-only `main` fetch, merge-base proof and `main.py` isolation unchanged.

- `tests/test_phase18_first_golden_review_workflow.py`
  - adds regression coverage for exact branch reattachment to `$DISPATCH_SHA`;
  - requires branch proof after reattachment;
  - requires a second HEAD/SHA proof;
  - requires reattachment to happen before CUDA and before the Candidate 1 bootstrap;
  - preserves all existing zero-cost, evidence replay and gate-closure assertions.

### Added

- `docs/PHASE18_CHANGESET_152_IMMUTABLE_BRANCH_REATTACHMENT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_152.md`

### Deleted

Nothing.

## Gates preserved

No change was made to:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B;
- native BF16;
- Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact-fact/entity-mark/sport-geometry exclusions;
- Original Scene runtime admission;
- Qwen BASE_SCENE or HYBRID_SURFACE inspection;
- deterministic football geometry;
- first-PNG provenance/evidence replay;
- mandatory human visual review;
- Golden `8.5` minimum / `9.0+` elite thresholds;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate;
- final Publication Readiness.

Seeds 2–4 remain unauthorized.

## Test status

- Starting HEAD `95b6b20326a9f9d47679b74549cc17729f1ba3fd` is confirmed green in Story Intelligence Verification run `32868671312 / 2628`; every returned companion Phase 18 workflow for that same commit also completed with `success`.
- Change Set 152 workflow/test changes have been pushed to `phase18/story-intelligence`.
- Fresh GitHub Actions runs triggered by the new commits must complete before Change Set 152 is described as fully CI-green.

## Genuine Golden PNG status

No Golden Hybrid v5 PNG was fabricated.

The current automation environment still does not expose a compatible NVIDIA CUDA + native-BF16 host capable of executing the locked FLUX.2 Klein 4B + Qwen Candidate 1 path. The exact external blocker remains GPU execution availability, not a missing CPU-side implementation claim.

## Remaining path

The canonical path is now:

`immutable dispatch SHA → exact local Phase 18 branch reattachment at the same SHA → complete ancestry/main isolation → repository/runtime/cache/Qwen checks → Original Scene admission → Candidate 1 genuine PNG → admission/provenance replay → BASE_SCENE ownership QA → deterministic football Hybrid → HYBRID_SURFACE QA → sealed SHA-bound human review → explicit human acceptance → sealed Golden 8.5/9.0 → exact brand/typography → SemanticPublicationGate → final publication readiness`

No Seeds 2–4 should run before Candidate 1 is genuinely rendered and accepted.
