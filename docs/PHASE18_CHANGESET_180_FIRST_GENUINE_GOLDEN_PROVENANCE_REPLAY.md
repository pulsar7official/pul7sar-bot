# PUL7SAR Phase 18 — Change Set 180

## First Genuine Golden Provenance Replay

### Purpose

Golden Editorial v6 already had a strict Candidate 1 staging wrapper that refused Engineering Proof fallback and required Qwen BASE_SCENE/layer-ownership approval on the exact generated PNG. One important gap remained: the staging decision trusted provenance fields already copied into `output/phase18_colab/latest.json`, but did not replay the durable executor result and proof metadata again at the exact boundary where a PNG becomes eligible for human Golden review.

That gap matters because a stale or tampered summary could otherwise keep the correct benchmark/composition/semantic fields while pointing at evidence whose model revision, cost mode, precision tier, request identity, or durable metadata no longer matches the generated PNG.

### Implementation

`tools/phase18_colab_first_genuine_golden.py` now:

- requires the approved `black-forest-labs/FLUX.2-klein-4B` model identity;
- requires `GENERATION_PROVENANCE_LOCK_VERIFIED`, never the FP16/T4 engineering-preview provenance tier;
- requires native `bfloat16`, `golden_reference`, and `$0-local` before human-review staging;
- requires a real request ID, integer seed, and valid payload SHA-256;
- replays `GenerationProvenanceLock` against the exact Candidate 1 PNG at staging time;
- therefore revalidates the durable executor result, proof metadata, PNG identity, pinned FLUX upstream revision, request ID, seed, payload SHA, cost mode, and precision tier;
- requires the replayed PNG SHA to equal the staged PNG SHA;
- writes the replayed executor-result and proof-metadata SHA-256 values into the staging receipt;
- upgrades the staging receipt contract to `pul7sar-first-genuine-golden-staging-v2`.

The wrapper still requires Golden Editorial v6 `context_only`, no deterministic pitch replacement, the locked composition map, successful Qwen semantic inspection, complete layer-ownership inspection, and the exact same PNG path in generation and semantic receipts.

### Regression coverage

`tests/test_phase18_first_genuine_golden.py` now creates realistic durable executor/proof-metadata fixtures and verifies:

- successful review-only staging is bound to executor and proof-metadata hashes;
- the pinned FLUX model revision is recorded;
- `$0-local`, native BF16, and `golden_reference` are mandatory;
- T4/FP16 engineering-preview provenance is rejected;
- model or zero-cost drift is rejected before review;
- executor cost tampering is detected by provenance replay;
- proof-metadata model-revision tampering is detected by provenance replay;
- semantic, composition-map, pitch-replacement, and PNG-identity gates remain fail-closed.

### Gates unchanged

No factual, identity, sentiment/neutrality, zero-cost, semantic-publication, brand, typography, or Golden visual-quality gate was weakened. Human visual review remains mandatory. Golden quality remains false at this stage. Publication remains false. Seeds 2–4 remain unauthorized.

### Deleted

None.
