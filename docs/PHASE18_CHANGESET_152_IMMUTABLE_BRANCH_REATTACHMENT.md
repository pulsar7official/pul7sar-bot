# PUL7SAR Phase 18 — Change Set 152

## Immutable dispatch SHA with runtime-visible Phase 18 branch identity

### Problem found

The canonical first-Golden workflow intentionally checked out `${{ github.sha }}` so the rare GPU run could never drift to a newer moving branch head after `workflow_dispatch`.

That immutable checkout is correct, but `actions/checkout` leaves Git in detached-HEAD state when a raw commit SHA is checked out. The strict Candidate 1 runtime is deliberately fail-closed on the current branch name: `tools/phase18_colab_first_golden_bootstrap.py` and the repository-integrity preflight require `git branch --show-current` to equal `phase18/story-intelligence`.

Therefore the canonical workflow could prove the correct immutable SHA and still fail before Candidate 1 simply because the runtime saw an empty branch name. CPU workflow-text tests could not expose this because they did not execute the self-hosted GPU path.

### Fix

`.github/workflows/phase18-first-golden-review.yml` now:

1. checks out the immutable dispatched SHA with complete ancestry;
2. proves `HEAD == $DISPATCH_SHA`;
3. creates/reattaches a **local** `phase18/story-intelligence` branch at that exact immutable SHA using:
   `git checkout -B phase18/story-intelligence "$DISPATCH_SHA"`;
4. proves the branch name is exactly `phase18/story-intelligence`;
5. proves again that `HEAD` is still exactly the dispatched SHA;
6. only then performs main-isolation, CUDA, bootstrap, FLUX/Qwen and review work.

This does **not** follow the moving remote branch. The local branch name exists solely so fail-closed Phase 18 runtime contracts can see the expected branch while the commit identity remains pinned to the dispatch SHA.

### Regression coverage

`tests/test_phase18_first_golden_review_workflow.py` now requires:

- immutable SHA checkout;
- complete ancestry;
- exact local Phase 18 branch reattachment to `$DISPATCH_SHA`;
- branch-name proof;
- a second HEAD/SHA proof after reattachment;
- branch reattachment before CUDA and before the strict Candidate 1 bootstrap.

### Gates preserved

No change was made to:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- `$0-local`;
- FLUX.2 Klein 4B;
- native BF16;
- Candidate/request/seed/canvas/SHA locks;
- Original Scene runtime admission;
- generated text/branding/exact-fact/entity-mark/sport-geometry exclusions;
- Qwen BASE_SCENE or HYBRID_SURFACE inspection;
- deterministic football geometry;
- provenance/evidence replay;
- mandatory human review;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate;
- final Publication Readiness.

Seeds 2–4 remain unauthorized.

### Files changed

Modified:

- `.github/workflows/phase18-first-golden-review.yml`
- `tests/test_phase18_first_golden_review_workflow.py`

Added:

- `docs/PHASE18_CHANGESET_152_IMMUTABLE_BRANCH_REATTACHMENT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_152.md`

Deleted: nothing.

`main` was not modified.
