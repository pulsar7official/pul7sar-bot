# PUL7SAR Phase 18 — Change Set 105: Genuine Candidate Review Bundle

## Purpose
Reduce the gap after the first genuine CUDA/BF16 Candidate 1 generation without spending GPU time on additional seeds. One verified Colab Golden Hybrid v5 base PNG can now be bound to its generation summary and expanded into the full CPU-only football pitch diagnostic matrix in a single fail-closed step.

## Added
- `engine/intelligence/golden_candidate_review_bundle.py`
- `tools/phase18_prepare_candidate_review.py`
- `tests/test_phase18_golden_candidate_review_bundle.py`
- `docs/PHASE18_CHANGESET_105_GENUINE_CANDIDATE_REVIEW_BUNDLE.md`

## Behavior
`GoldenCandidateReviewBundleBuilder` requires:
- branch exactly `phase18/story-intelligence`;
- Golden contract exactly `pul7sar-golden-batch-v5`;
- a genuine generated/reused Colab base status, never a prepare-only status;
- the expected Candidate identity;
- `publication_ready=false`;
- exact FLUX.2 Klein 4B model identity;
- valid 64-hex payload SHA-256;
- generated branding forbidden;
- generated sport geometry forbidden;
- deterministic hybrid surface replacement still required;
- a real repository-scoped PNG with the PNG signature.

It computes SHA-256 over the genuine base and the source summary, then runs the existing `FootballPitchDiagnosticBuilder` across every approved camera preset. The base PNG must remain byte-identical. The resulting bundle explicitly keeps all downstream gates closed:
- semantic layer ownership not yet approved;
- pitch selection not yet locked;
- HYBRID_SURFACE semantic review not yet approved;
- Golden quality not yet approved;
- publication not ready.

## CLI
After Candidate 1 exists:

```bash
PYTHONPATH=. python tools/phase18_prepare_candidate_review.py --candidate 1
```

Default input is `output/phase18_colab/latest.json`; default output is `output/phase18_candidate_review/candidate-01`.

## Why this materially reduces the remaining gap
Previously the first genuine base had to be followed by separate manual discovery of the PNG and a second explicit pitch-diagnostic command. Change Set 105 creates a single SHA-bound review bundle from that one GPU result. No additional FLUX seed is needed merely to evaluate deterministic football placement.

## Security / quality invariants
Unchanged:
- `main` and `main.py` are not modified.
- Fact Lock remains fail-closed.
- Identity verification remains fail-closed.
- Sentiment / neutrality remain unchanged.
- `$0-local` policy remains unchanged.
- FLUX.2 Klein 4B, BF16, seeds and canvases remain unchanged.
- SemanticPublicationGate remains mandatory.
- Golden thresholds remain 8.5 minimum / 9.0+ elite; hard blockers override score.
- Generated PUL7SAR branding remains forbidden.
- Exact brand/logo/typography integrity remains a separate downstream requirement.
- No paid provider, secret, model weight, font file, fake PNG, fabricated benchmark or fabricated review score is added.
