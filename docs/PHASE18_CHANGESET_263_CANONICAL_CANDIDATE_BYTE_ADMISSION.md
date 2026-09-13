# Phase 18 — Change Set 263: Canonical Candidate Byte Admission

## Purpose

Change Set 263 creates the narrow post-generation boundary between a successful Change Set 262 one-shot canonical inference and the existing downstream visual-quality stack.

It does **not** perform inference, semantic pixel approval, Visual Critic scoring, human review, Golden scoring, brand/typography approval, or publication approval.

## Contract

The admission builder must first execute `verify_one_shot_canonical_inference()` against the exact CS262 receipt. It then reopens the exact `canonical_candidate.png` bytes and verifies:

- the source receipt remains inside the repository and is not a symlink;
- the candidate remains inside the repository and is not a symlink;
- SHA-256 and byte size equal the values bound by CS262;
- PNG signature/IHDR are structurally present;
- PNG width/height equal both the CS262 PNG metadata and requested generation dimensions;
- story, model, revision, cost mode, prompt bindings, runtime fingerprint, seed, steps and guidance provenance are carried forward;
- successful inference authority exists while every downstream quality/publication authority remains closed.

A successful CS263 receipt may assert only that the exact candidate bytes are admitted for post-generation QA.

## Authority boundary

A successful receipt preserves:

- `production_semantic_replay_executed = true`
- `fresh_story_gates_passed = true`
- `controlled_trial_preflight_valid = true`
- `canonical_generation_authorized = true`
- `inference_executed = true`
- `genuine_canonical_inference_executed = true`
- `candidate_bytes_admitted_for_post_generation_qa = true`

It must keep:

- `genuine_golden_png_created = false`
- `semantic_approved = false`
- `human_visual_review_approved = false`
- `golden_quality_approved = false`
- `publication_ready = false`

Thus a real PNG remains a **candidate**, not a Golden Visual.

## Fail-closed behavior

CS263 rejects byte drift, dimension drift, source/candidate symlinks, paths outside the repository, malformed receipts, premature authority, cross-story provenance drift inherited from CS262 verification, and an already-existing output directory.

The receipt is itself SHA-256 sealed and its verifier reopens both the source CS262 receipt and candidate PNG before accepting the admission.

## Zero-cost and factual safety

No network model invocation or paid service is introduced. The layer consumes only a CS262 result whose upstream authorization already required the factual, identity, sentiment, zero-cost, semantic replay, same-host runtime, and one-shot generation contracts. CS263 cannot bypass or weaken those gates because it invokes the CS262 verifier rather than trusting copied booleans.

## Remaining path

`CS262 genuine canonical candidate -> CS263 exact byte admission -> semantic/layer pixel QA -> byte-bound Visual Critic -> human review -> Golden >= 8.5 (elite >= 9.0) -> exact brand/typography -> SemanticPublicationGate`.
