# Phase 18 Change Set 216 — Dynamic Visual Brain Ledger Provenance Binding

## Objective

Close the remaining gap between the durable Dynamic Visual Brain queue-to-critic chain and the canonical Phase 18 real-visual validation ledger.

Before this change, the ledger could record a candidate with a generic `provenance_passed=true` check, while the newer Dynamic Visual Brain path already had much stronger evidence proving:

`locked concept -> renderer-safe prompt -> measured admission -> sealed durable queue job -> succeeded worker execution -> exact PNG -> byte-bound Visual Critic`.

Change Set 216 adds an explicit bridge so Dynamic Visual Brain candidates can enter the canonical validation ledger only through the exact PNG already proven by the durable queue-to-critic receipt.

## Added

### `engine/intelligence/dynamic_visual_brain_ledger_binding.py`

New contract: `pul7sar-dynamic-visual-brain-ledger-binding-v1`.

The gate verifies:

- a canonical Phase 18 benchmark id;
- the queue-to-critic contract/status/branch;
- succeeded durable job state and positive attempt;
- `$0-local` execution;
- story/concept/renderer/original-scene hashes;
- exact current PNG bytes against the queue-to-critic `png_sha256`;
- Human Review remains required;
- Golden approval remains false;
- Publication readiness remains false.

It also provides `record_review(...)`, which injects `provenance_passed=true` only from a valid binding receipt. A Visual Critic rejection may be recorded as a rejected ledger case, but it can never be promoted to an accepted case.

### `tools/phase18_bind_dynamic_visual_to_ledger.py`

CPU-only CLI to bind a durable Dynamic Visual Brain candidate to one canonical benchmark case. It does not run FLUX/Qwen, mutate the queue, or authorize publication.

### `tests/test_phase18_dynamic_visual_brain_ledger_binding.py`

Regression coverage for:

- exact queue-to-critic PNG binding;
- PNG tampering after critic evidence;
- accepted ledger review with provenance injected from the binding;
- critic rejection remaining reject-only even with a high score;
- candidate path escape outside the repository.

## Safety preservation

Unchanged and fail-closed:

- Fact Lock / factual integrity;
- Entity and Identity Verification;
- sentiment and neutrality / loser-respect rules;
- `$0-local` policy;
- pinned model/runtime policies;
- generated text/branding/exact facts/entity marks/exact sport geometry prohibitions;
- semantic and layer-ownership gates;
- Visual Critic hard failures;
- explicit Human Review;
- Golden minimum `8.5` and elite target `9.0+`;
- Exact Brand and Typography Integrity;
- SemanticPublicationGate and final publication readiness.

The new binding cannot set `golden_quality_approved=true` or `publication_ready=true`.

## Result

The next genuine Dynamic Visual Brain candidate cannot enter the canonical multi-family validation ledger with a free-floating provenance checkbox. Its ledger candidate must be the same PNG bytes proven by the succeeded durable queue job and byte-bound Visual Critic chain.
