# PUL7SAR Phase 18 — Change Set 151

## Complete-Ancestry First-Golden Workflow

### Problem

Change Set 150 correctly pinned the canonical first-Golden workflow to the immutable dispatch SHA and made the `main.py` isolation check fail closed when no merge-base could be established.

However, the workflow still checked out the immutable Phase 18 commit with `fetch-depth: 1` and only fetched `main` with a bounded depth. On a long-lived branch that is substantially diverged from `main`, the Phase 18 checkout can mark the dispatched HEAD as a shallow boundary. Fetching only `main` does not guarantee that Git can traverse the Phase 18 side far enough to reach the real shared ancestor.

That means a valid GPU session could fail at `git merge-base origin/main HEAD` before any model work, purely because repository ancestry was intentionally truncated by checkout depth.

### Change

The canonical `.github/workflows/phase18-first-golden-review.yml` now:

- checks out the immutable `${{ github.sha }}` with `fetch-depth: 0`;
- keeps the explicit read-only `main` fetch, but removes an arbitrary depth limit;
- establishes the merge-base only from complete reachable ancestry;
- continues to fail closed if no merge-base exists;
- continues to reject any `main.py` modification between merge-base and the immutable Phase 18 HEAD.

No model, prompt, generation, semantic, visual-quality or publication behavior changed.

### Regression lock

`tests/test_phase18_first_golden_review_workflow.py` now requires:

- `fetch-depth: 0` for the immutable checkout;
- absence of `fetch-depth: 1`;
- an unbounded explicit read-only `main` fetch;
- no `--depth=` fallback in that fetch;
- the existing fail-closed merge-base and `main.py` isolation checks.

### Why this materially reduces the gap to the first genuine Golden PNG

The first compatible self-hosted CUDA/BF16 window is scarce. The canonical workflow should not consume that opportunity only to fail before GPU work because Git history was artificially shallow. Change Set 151 removes that avoidable repository-history failure mode while preserving the immutable source commit introduced in Change Set 150.

### Preserved gates

Unchanged:

- branch-only development on `phase18/story-intelligence`;
- no writes to `main`;
- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- `$0-local`;
- FLUX.2 Klein 4B;
- native BF16;
- Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact-fact/entity-mark/sport-geometry exclusions;
- Original Scene runtime admission;
- Qwen BASE_SCENE and HYBRID_SURFACE inspection;
- deterministic football geometry;
- provenance/evidence replay;
- explicit human review;
- Golden `8.5` minimum / `9.0+` elite thresholds;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate;
- final Publication Readiness.

Seeds 2–4 remain unauthorized.
