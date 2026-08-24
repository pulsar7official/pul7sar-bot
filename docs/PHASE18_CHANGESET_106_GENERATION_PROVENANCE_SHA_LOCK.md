# PUL7SAR Phase 18 — Change Set 106: Generation Provenance SHA Lock

Branch: `phase18/story-intelligence` only. `main` is not modified.

## Problem closed
Change Set 105 SHA-bound the Colab summary and the candidate PNG separately, but the review bundle still trusted that the PNG named in the summary was the same registered visual proof produced by the durable FLUX executor result. A stale or replaced PNG path could therefore survive into CPU review if the surrounding summary identity fields still looked valid.

## Added
- `engine/intelligence/generation_provenance_lock.py`
  - replays the durable executor result before Candidate review;
  - requires `REAL_VISUAL_PROOF_GENERATED`, `$0-local`, `bfloat16`, exact request ID, seed, model ID and handoff payload SHA;
  - requires the executor PNG path to resolve to the exact Candidate base PNG;
  - requires the registered visual-proof metadata file to exist and match request ID, seed, model, cost mode and exact output path;
  - computes SHA-256 for the proof PNG, executor result JSON and proof metadata JSON;
  - rejects repository path escape;
  - never grants semantic, Golden-quality or publication approval.
- `tests/test_phase18_generation_provenance_lock.py`
  - verifies exact proof/executor/metadata hashing;
  - rejects executor identity drift, PNG path drift, metadata output drift, precision downgrade and cost-mode drift.

## Modified
- `engine/intelligence/golden_candidate_review_bundle.py`
  - Candidate review now requires successful `GENERATION_PROVENANCE_LOCK_VERIFIED` before pitch diagnostics;
  - embeds executor-result SHA, proof-metadata SHA, resolved dtype and cost mode into the review bundle;
  - verifies the provenance-lock base SHA equals the exact PNG bytes used for diagnostics.
- `tests/test_phase18_golden_candidate_review_bundle.py`
  - fixtures now include a durable executor result and registered proof metadata;
  - asserts the review bundle carries the provenance hashes and remains non-publication;
  - rejects executor precision drift before any pitch review is prepared.

## Deleted
Nothing.

## Safety and quality invariants
Unchanged: Fact Lock, Identity Verification, Sentiment/Neutrality, `$0-local`, FLUX.2 Klein 4B, BF16, seeds/canvases, generated-branding exclusion, deterministic football geometry ownership, SemanticPublicationGate, Golden 8.5/9.0 thresholds, exact-brand integrity and publication readiness.

No paid provider, secret, model weights, font file, fake PNG, fabricated benchmark or fabricated review score is added.

## Why this reduces the remaining gap
The first genuine Candidate 1 will now enter CPU review only if the exact PNG bytes can be replayed back to the durable zero-cost BF16 executor result and registered proof metadata. This prevents stale or substituted visual proof bytes from being mistaken for the GPU result that passed the generation contract.
