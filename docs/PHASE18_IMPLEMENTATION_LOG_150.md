# PUL7SAR Phase 18 — Implementation Log 150

## Branch isolation

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- Starting Phase 18 HEAD observed: `e25ed7ccd6d628bf69f1d090937d68e2e75a3c60`.
- `main` HEAD observed during this run: `a94710381bcd6a1cb152672a65b89aee6dcf1bb7`.
- After the Change Set 150 code/test commits, Phase 18 remained `diverged` from `main`, 1353 commits ahead and 136 behind at the comparison point.
- `main` was reviewed but never modified, merged, force-updated or used as a write target.

## Existing state reviewed first

The starting HEAD already contained the canonical manual self-hosted workflow introduced in Change Set 149. GitHub Actions for that starting HEAD were checked before new writes: Story Intelligence Verification run `32855789116 / 2597` completed with `success`, and every returned companion Phase 18 workflow for the same commit also completed with `success`.

The canonical workflow already preserved Candidate 1 only, `$0-local`, CUDA/BF16, Original Scene admission, Qwen BASE_SCENE/HYBRID_SURFACE, deterministic football geometry, provenance/evidence replay, sealed human review, Golden authority closure, and publication closure.

## Gap identified

The workflow checked out the moving branch name `phase18/story-intelligence` after dispatch. If the branch advanced between dispatch and checkout, a scarce GPU run could execute a different commit from the one that triggered it.

The workflow also attempted to protect `main.py` using a shallow checkout plus an error-suppressed comparison. If `origin/main` or a usable merge-base was unavailable, that check could silently produce no match instead of failing closed.

This was a reproducibility and branch-isolation gap, not a visual-quality or model-quality gap.

## Change Set 150 — Immutable First-Golden Workflow Source

### Modified

- `.github/workflows/phase18-first-golden-review.yml`
  - requires dispatch from `refs/heads/phase18/story-intelligence`;
  - validates the dispatched SHA;
  - checks out immutable `${{ github.sha }}` rather than a moving branch ref;
  - verifies runner HEAD equals the dispatched SHA;
  - fetches `main` read-only with enough history to establish a merge-base;
  - fails closed when no merge-base exists;
  - checks merge-base-to-HEAD changes for `main.py` without suppressing Git errors;
  - leaves the strict Candidate 1 pipeline and all downstream evidence replay unchanged.

- `tests/test_phase18_first_golden_review_workflow.py`
  - now locks dispatch-ref identity, immutable SHA checkout and HEAD equality;
  - locks explicit `main` fetch + merge-base behavior;
  - prevents restoration of the previous stderr-suppressed `main.py` check.

### Added

- `docs/PHASE18_CHANGESET_150_IMMUTABLE_FIRST_GOLDEN_WORKFLOW_SOURCE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_150.md`

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

Starting HEAD `e25ed7ccd6d628bf69f1d090937d68e2e75a3c60` was fully green in the returned Phase 18 GitHub Actions runs, including Story Intelligence Verification `32855789116 / 2597`.

Change Set 150 code and regression tests have been committed. A fresh GitHub Actions run on the new HEAD must be checked before Change Set 150 is described as fully CI-green.

## Genuine Golden PNG status

No Golden Hybrid v5 PNG was fabricated. This automation environment still does not expose a compatible NVIDIA CUDA + native-BF16 host capable of executing the locked FLUX.2 Klein 4B + Qwen Candidate 1 path.

## Remaining path

The preferred self-hosted path remains the canonical first-Golden workflow, now pinned to the exact dispatch SHA:

`immutable Phase 18 dispatch SHA → repository/runtime/cache/Qwen checks → Original Scene admission → Candidate 1 genuine PNG → admission/provenance replay → BASE_SCENE ownership QA → deterministic football Hybrid → HYBRID_SURFACE QA → sealed SHA-bound human review → explicit human acceptance → sealed Golden 8.5/9.0 → exact brand/typography → SemanticPublicationGate → final publication readiness`

No Seeds 2–4 should run before Candidate 1 is genuinely rendered and accepted.
