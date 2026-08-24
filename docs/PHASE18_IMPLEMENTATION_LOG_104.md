# PUL7SAR Phase 18 — Implementation Log Continuation 104

This file is the authoritative continuation record for Change Set 104 on `phase18/story-intelligence`. It supplements earlier Phase 18 implementation logs. No production branch is modified.

## Branch review before change
- Repository: `pulsar7official/pul7sar-bot`.
- Target branch: `phase18/story-intelligence` only.
- Comparison with `main` at the start of this run: `diverged`, 770 commits ahead and 80 behind.
- Base `main` commit observed: `c98e186d9b832b83e98b1991af3966574d219b61`.
- `main` / `main.py` were not used as a write target.
- No new genuine Golden Hybrid v5 GPU PNG is claimed in this run.

## Change Set 104 — Final Composer Football Integrity Alignment

### Added
- `docs/PHASE18_CHANGESET_104_FINAL_COMPOSER_FOOTBALL_INTEGRITY.md`.
- `docs/PHASE18_IMPLEMENTATION_LOG_104.md`.

### Modified
- `engine/intelligence/final_hybrid_composer.py`
  - replaces the stale `surface_opacity == 255` football check with `HybridArtifactIntegrityGate`;
  - therefore consumes the same texture-preserving, feathered, SHA-replayed football contract used by current Hybrid v5;
  - introduces optional `precomposed_football_receipt` evidence for already composed football bytes;
  - requires the receipt output SHA to equal the exact final-composer base SHA;
  - forbids requesting both newly composed and precomposed football geometry;
  - no longer reports deterministic geometry as applied when no verified football evidence exists.
- `tests/test_phase18_final_hybrid_composer.py`
  - adds regression coverage for the current low-opacity texture-preserving football contract;
  - adds regression coverage preventing false deterministic-geometry claims;
  - adds SHA-binding and mutually-exclusive precomposed/new-composition tests;
  - retains the existing missing-base and unapproved-brand protections.

### Deleted
- Nothing.

## Why this was necessary before the first new Golden Visual
Change Sets 095–097 deliberately moved football composition away from the old opaque green tactical-board proof to a photographic, texture-preserving surface. `FinalHybridComposer` was an older downstream boundary and still expected the obsolete `surface_opacity=255` contract. A genuine future Candidate 1 could therefore pass modern Hybrid QA and then fail later during exact brand/typography composition for the wrong reason.

The same code also returned `deterministic_geometry_applied=true` whenever `apply_football_geometry` was false, even when no receipt proved geometry. Change Set 104 removes that false-positive evidence path.

## Architecture after Change Set 104
`Genuine FLUX Candidate 1 -> Base semantic/layer gate -> CPU pitch diagnostics -> explicit human preset review -> SHA-locked pitch selection -> locked-pitch Qwen HYBRID_SURFACE review -> SHA-bound Golden Visual review -> FinalHybridComposer using verified current football evidence -> exact approved brand/typography -> SemanticPublicationGate -> final publication readiness`

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
- Updated tests are CPU-safe and included by the existing `tests/test_phase18_*.py` discovery workflow.
- The Phase 18 workflow should trigger from these engine/test/docs changes.
- At the time this log entry is created, the final GitHub Actions result for Change Set 104 is not yet recorded here. Do not describe Change Set 104 as CI-green until the workflow reports success.
- No GPU result is claimed by this Change Set.

## Remaining work
1. Obtain compatible CUDA/BF16 execution and generate Golden Hybrid v5 Candidate 1 only.
2. Require the genuine FLUX base to pass semantic layer ownership.
3. Run pitch diagnostics on that exact base, make an explicit human preset selection and SHA-lock the chosen variant.
4. Run locked-pitch Qwen HYBRID_SURFACE semantic/alignment review.
5. If semantic review passes, complete the SHA-bound Golden visual review against the same bytes.
6. Only if `golden_quality_approved=true`, feed verified football evidence into the corrected final compositor and add exact approved brand/typography.
7. Resolve and SHA-lock the approved PUL7SAR logo/brand geometry/font assets before publication composition.
8. Run SemanticPublicationGate and final publication-readiness checks; no earlier stage can waive them.
