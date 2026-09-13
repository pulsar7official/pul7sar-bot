# PUL7SAR Phase 18 — Implementation Log Continuation 106

This file is the authoritative continuation record for Change Set 106 on `phase18/story-intelligence`. No production branch is modified.

## Branch review before change
- Repository: `pulsar7official/pul7sar-bot`.
- Target branch: `phase18/story-intelligence` only.
- Comparison with `main` at the start of this run: `diverged`, 780 commits ahead and 80 behind.
- Base `main` commit observed: `c98e186d9b832b83e98b1991af3966574d219b61`.
- PR #1 remained open, Draft and unmerged; observed pre-change head: `15428845951bcd3a2dea46d29e57a25cd6390953`.
- `main` / `main.py` were not used as write targets.
- No new genuine Golden Hybrid v5 GPU PNG is claimed in this run.

## Prior verification state
- The previously observed Change Set 105 head `15428845951bcd3a2dea46d29e57a25cd6390953` has GitHub Actions Run `32687833122` / run `1438` completed with `success`.
- That verifies the pre-106 Phase 18 CPU suite and Golden Hybrid v5 contract; it is not a GPU visual-quality claim.

## Change Set 106 — Generation Provenance SHA Lock

### Added
- `engine/intelligence/generation_provenance_lock.py`
  - replays the durable executor result and registered visual-proof metadata;
  - requires exact request ID, seed, model, payload SHA, `$0-local` and `bfloat16`;
  - requires the executor PNG and proof-metadata output reference to resolve to the exact base PNG used for review;
  - computes SHA-256 for the proof PNG, executor result JSON and proof metadata JSON;
  - rejects path escape and remains explicitly non-publication.
- `tests/test_phase18_generation_provenance_lock.py`
  - covers valid replay plus executor identity drift, PNG path drift, metadata output drift, precision downgrade and cost-mode drift.
- `docs/PHASE18_CHANGESET_106_GENERATION_PROVENANCE_SHA_LOCK.md`.
- `docs/PHASE18_IMPLEMENTATION_LOG_106.md`.

### Modified
- `engine/intelligence/golden_candidate_review_bundle.py`
  - now requires successful generation-provenance replay before any pitch diagnostics are prepared;
  - records executor-result SHA, proof-metadata SHA, resolved dtype and cost mode in the Candidate review bundle;
  - cross-checks the provenance base SHA against the exact PNG bytes used for diagnostics.
- `tests/test_phase18_golden_candidate_review_bundle.py`
  - fixtures now contain the durable executor result and registered proof metadata;
  - asserts provenance fields and rejects executor dtype drift before CPU pitch review.

### Deleted
- Nothing.

## Why this advances the first genuine Golden Visual
Compatible CUDA/BF16 execution remains the external hard blocker for a new Candidate 1. Change Set 106 materially reduces the gap after that run: the Candidate can no longer enter visual review solely because a Colab summary points at a valid PNG. The exact bytes must replay back to the durable FLUX executor result and registered proof metadata under the same request, seed, model, payload SHA, BF16 and `$0-local` contract.

Current path:
`Genuine Candidate 1 -> generation provenance SHA lock -> candidate review bundle -> Base semantic/layer gate -> human pitch preset review -> SHA pitch lock -> locked-pitch Qwen HYBRID_SURFACE review -> SHA-bound Golden 8.5/9.0 review -> FinalHybridComposer -> exact approved brand/typography -> SemanticPublicationGate -> publication readiness`.

## Gates and invariants unchanged
- `main` / `main.py`: untouched.
- Telegram and legacy production publishing: untouched.
- Fact Lock: unchanged and fail-closed.
- Identity verification: unchanged and fail-closed.
- Sentiment / neutrality: unchanged.
- `$0-local`: unchanged.
- FLUX.2 Klein 4B, BF16, seeds/canvases and generation controls: unchanged.
- Base semantic layer ownership remains mandatory.
- SemanticPublicationGate remains mandatory.
- Golden thresholds remain 8.5 minimum / 9.0+ elite; hard blockers override score.
- Generated PUL7SAR branding remains forbidden.
- Exact PUL7SAR logo/brand/typography integrity remains a separate downstream requirement.
- No paid provider, secret, model weights, font files, fake PNG, fabricated benchmark or fabricated review score was added.

## Test state
- Change Set 106 adds CPU-safe unittest coverage under the existing `test_phase18_*.py` discovery pattern.
- GitHub Actions result for the final Change Set 106 head must be observed before this log may claim CI success.
- No GPU result is claimed by this Change Set.

## Remaining work
1. Obtain a compatible CUDA/BF16 host and generate Golden Hybrid v5 Candidate 1 only.
2. Run the Candidate review preparation; generation provenance must replay successfully first.
3. Require the genuine base to pass semantic layer ownership.
4. Review deterministic pitch variants and explicitly select one; SHA-lock the exact chosen bytes.
5. Run locked-pitch Qwen HYBRID_SURFACE semantic/alignment review.
6. Complete the SHA-bound Golden visual review against those same bytes.
7. Only if `golden_quality_approved=true`, enter the corrected final compositor and add exact approved brand/typography.
8. Resolve and SHA-lock the approved PUL7SAR logo/brand geometry/font assets before publication composition.
9. Run SemanticPublicationGate and final publication-readiness checks; no earlier stage can waive them.
