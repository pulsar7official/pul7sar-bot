# PUL7SAR Phase 18 — Implementation Log 149

## Branch isolation

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence`
- `main` was reviewed but never modified, merged, force-updated or used as a write target.
- Starting Phase 18 HEAD observed: `c9d8d1200b27ee0191c49288243dcbabd3d42cef`.
- `main` HEAD observed: `a9fc6285fecfbdb283a7936937ee240e447f4985`.
- At the comparison point after code/test additions, Phase 18 remained `diverged` from `main`, 1349 commits ahead and 134 behind.

## Existing state reviewed first

The starting branch already had:

1. repository/reference integrity preflight;
2. shared Qwen + FLUX cache-budget preflight;
3. strict Qwen runtime/model preparation;
4. provider-neutral Original Scene runtime admission for Golden Candidate 1;
5. native-BF16 FLUX.2 Klein 4B first-PNG execution;
6. admission receipt SHA pin/replay and first-PNG provenance replay;
7. Golden Hybrid v5 handoff without rerunning FLUX;
8. Qwen BASE_SCENE ownership QA;
9. deterministic texture-preserving football Hybrid composition;
10. Qwen HYBRID_SURFACE semantic/alignment QA;
11. SHA-sealed human-review packet integrity;
12. explicit human acceptance and sealed Golden review gates downstream.

The starting HEAD was fully green in GitHub Actions. Story Intelligence Verification run `32849965746 / 2582` completed with `success`, and all returned companion Phase 18 workflows for the same commit also completed successfully.

## Gap identified

The branch had two operational GPU entry styles:

- `.github/workflows/phase18-gpu-smoke.yml` exposed the individual GPU/provenance/semantic stages in detail;
- `tools/phase18_colab_first_golden_bootstrap.py` had become the stricter orchestration path that already reaches the SHA-sealed Candidate 1 human-review packet using the Original Scene contract.

There was no dedicated self-hosted GitHub workflow that invoked the strict bootstrap as the canonical single entrypoint and then independently replayed the bootstrap evidence plus the exact Base/Hybrid PNG hashes before artifact upload.

That gap did not weaken existing gates, but it meant the safest Colab path and the simplest self-hosted GitHub path were operationally different.

## Change Set 149 — Canonical First Golden Review Workflow

### Added

- `.github/workflows/phase18-first-golden-review.yml`
  - manual `workflow_dispatch` only;
  - requires exact confirmation token `RUN_PHASE18_FIRST_GOLDEN_REVIEW`;
  - checks out only `phase18/story-intelligence`;
  - requires `[self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]`;
  - proves CUDA-enabled PyTorch exists and refuses to install/replace PyTorch automatically;
  - invokes `tools/phase18_colab_first_golden_bootstrap.py` as the strict Candidate 1 entrypoint;
  - validates `pul7sar-first-golden-colab-bootstrap-v2` and Candidate 1 / `$0-local` identity;
  - replays SHA-256 and byte-size for repository integrity, shared cache budget, Qwen cache and sealed-review receipt;
  - replays SHA-256 and PNG signatures for the exact Base and Hybrid files shown to the human reviewer;
  - asserts Human approval, Golden approval, Publication Readiness and Seeds 2–4 authorization remain false;
  - uploads the sealed review/evidence directories only after the strict bootstrap and replay checks.

- `tests/test_phase18_first_golden_review_workflow.py`
  - locks manual-only and Phase-18-only execution;
  - locks the self-hosted CUDA/BF16 runner labels;
  - proves the workflow uses the strict Original Scene → sealed review path;
  - prevents PyTorch auto-install and paid-provider/secret drift;
  - proves bootstrap evidence and review-image hashes are replayed;
  - proves Human/Golden/Publication/Seeds 2–4 authority stays closed;
  - proves artifact upload happens after bootstrap and replay.

- `docs/PHASE18_CHANGESET_149_CANONICAL_FIRST_GOLDEN_REVIEW_WORKFLOW.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_149.md`

### Modified

Nothing. The change is additive.

### Deleted

Nothing.

## Gates preserved

No change was made to:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B selection;
- native BF16 requirement;
- Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact-fact/entity-mark/sport-geometry exclusions;
- Original Scene runtime admission;
- Qwen BASE_SCENE or HYBRID_SURFACE inspection;
- deterministic football geometry;
- first-PNG provenance/evidence replay;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate;
- final Publication Readiness.

The new workflow cannot grant human approval, Golden approval, Seeds 2–4 authorization or publication authority.

## Test status

The starting HEAD `c9d8d1200b27ee0191c49288243dcbabd3d42cef` was verified green by Story Intelligence Verification run `32849965746 / 2582` and all returned companion Phase 18 workflows.

Change Set 149 code, workflow and regression tests have been committed to `phase18/story-intelligence`. GitHub Actions must be checked on the new HEAD before Change Set 149 is described as fully CI-green.

## Genuine Golden PNG status

No Golden Hybrid v5 PNG was fabricated. The environment available to this automation still does not provide a compatible NVIDIA CUDA + native-BF16 host capable of running the locked FLUX.2 Klein 4B + Qwen Candidate 1 path.

## Remaining path to first genuine Golden Visual

Preferred self-hosted entrypoint after this change:

`workflow_dispatch Phase 18 First Golden Review → strict repository/runtime/cache/Qwen checks → Original Scene admission → Candidate 1 genuine PNG → admission/provenance replay → BASE_SCENE ownership QA → deterministic football Hybrid → HYBRID_SURFACE QA → sealed SHA-bound human-review packet → explicit human acceptance → sealed human-approved Golden 8.5/9.0 review → exact brand/typography → SemanticPublicationGate → final publication readiness`

Seeds 2–4 remain unauthorized until Candidate 1 is genuinely rendered, reviewed and accepted.
