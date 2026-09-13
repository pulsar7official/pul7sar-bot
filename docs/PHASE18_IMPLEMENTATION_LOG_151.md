# PUL7SAR Phase 18 — Implementation Log 151

## Branch isolation

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Starting Phase 18 HEAD observed: `033fe4e899e3c0f4038ebf3b5b8617999d359f85`.
- `main` HEAD observed during this run: `a94710381bcd6a1cb152672a65b89aee6dcf1bb7`.
- Starting comparison: Phase 18 remained `diverged` from `main`, 1355 commits ahead and 136 behind.
- `main` was reviewed but never modified, merged, force-updated or used as a write target.

## Existing state reviewed first

Change Set 150 was rechecked before new writes. Story Intelligence Verification run `32862193539 / 2610` completed with `success`, and every returned companion Phase 18 workflow for the same starting HEAD also completed with `success`.

The canonical first-Golden workflow was already manual, self-hosted CUDA/BF16 only, `$0-local`, pinned to the immutable dispatch SHA, and fail-closed on branch identity, Candidate 1 identity, Qwen readiness, FLUX readiness, provenance/evidence replay, BASE_SCENE/HYBRID_SURFACE gates, deterministic football geometry, human review, Golden authority and publication authority.

## Gap identified

The immutable checkout introduced in Change Set 150 still used `fetch-depth: 1`. The workflow then fetched only `main` with a bounded history and attempted `git merge-base origin/main HEAD`.

Because Phase 18 is a long-lived branch with substantial divergence from `main`, the shallow boundary on the Phase 18 side can make the genuine merge-base unreachable even when it exists in repository history. That would cause a valid self-hosted GPU run to fail before model execution for a repository-history reason that can be eliminated safely.

This was a pre-GPU reproducibility/isolation gap, not a model-quality, semantic-quality or publication-quality gap.

## Change Set 151 — Complete-Ancestry First-Golden Workflow

### Modified

- `.github/workflows/phase18-first-golden-review.yml`
  - keeps immutable `${{ github.sha }}` checkout;
  - changes checkout history to `fetch-depth: 0` so the Phase 18 side of the merge-base is never an arbitrary shallow boundary;
  - keeps an explicit read-only `main` fetch but removes the bounded `--depth` guess;
  - preserves fail-closed merge-base establishment;
  - preserves the `main.py` isolation check;
  - leaves all CUDA/Qwen/FLUX/Candidate-1/evidence/human-review behavior unchanged.

- `tests/test_phase18_first_golden_review_workflow.py`
  - requires `fetch-depth: 0`;
  - rejects regression to `fetch-depth: 1`;
  - requires the explicit unbounded read-only `main` fetch;
  - rejects a bounded `--depth=` fetch in this canonical workflow;
  - preserves all existing immutable-SHA, zero-cost, gate-closure and artifact-order assertions.

### Added

- `docs/PHASE18_CHANGESET_151_COMPLETE_ANCESTRY_FIRST_GOLDEN_WORKFLOW.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_151.md`

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
- Human review requirement;
- Golden `8.5` minimum / `9.0+` elite thresholds;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate;
- final Publication Readiness.

Seeds 2–4 remain unauthorized.

## Test status

- Change Set 150 starting HEAD `033fe4e899e3c0f4038ebf3b5b8617999d359f85` is confirmed green in Story Intelligence Verification run `32862193539 / 2610`; all returned companion Phase 18 workflows for that same commit also completed with `success`.
- Change Set 151 workflow and regression-test changes have been committed on `phase18/story-intelligence`.
- Fresh GitHub Actions runs triggered by the new commits must complete before Change Set 151 is described as fully CI-green.

## Genuine Golden PNG status

No Golden Hybrid v5 PNG was fabricated. The current automation environment still does not expose a compatible NVIDIA CUDA + native-BF16 host capable of executing the locked FLUX.2 Klein 4B + Qwen Candidate 1 path.

## Remaining path

The preferred canonical path is now:

`immutable Phase 18 dispatch SHA with complete ancestry → repository/runtime/cache/Qwen checks → Original Scene admission → Candidate 1 genuine PNG → admission/provenance replay → BASE_SCENE ownership QA → deterministic football Hybrid → HYBRID_SURFACE QA → sealed SHA-bound human review → explicit human acceptance → sealed Golden 8.5/9.0 → exact brand/typography → SemanticPublicationGate → final publication readiness`

No Seeds 2–4 should run before Candidate 1 is genuinely rendered and accepted.
