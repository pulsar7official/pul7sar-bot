# Phase 18 Change Set 386 — CS360 Semantic Base QA Readiness Lineage

## Purpose

Carry the exact replay-verified CS351 CUDA/native-BF16 static-readiness receipt binding across the first post-generation semantic inspection boundary (CS360 / CS304 semantic Base QA), without creating a new gate or granting any downstream authority.

## Proven upstream path

`CS351 static readiness -> CS354 launch manifest -> CS357 postflight attestation -> CS358 canonical handoff -> CS359 candidate byte admission -> CS360 semantic Base QA`

CS359 already proves and exposes `static_readiness_receipt_verified=true` plus the exact readiness receipt path, SHA-256, and byte size. Before CS386, CS360 fresh-replayed CS359 and preserved Qwen snapshot-byte lineage, but did not retain the readiness binding as first-class downstream provenance.

## Production change

`engine/intelligence/qwen_image_canonical_candidate_semantic_base_qa.py`

- schema upgraded from `pul7sar-phase18-qwen-image-canonical-candidate-semantic-base-qa-v3` to `...-v4`;
- requires `static_readiness_receipt_verified=true` before semantic inspection;
- validates readiness path is repository-relative and traversal-free;
- validates readiness SHA-256 and positive byte size;
- writes the exact readiness binding into the CS360 receipt;
- fresh CS359 replay compares readiness path, SHA-256, and byte size during verification;
- recomputing the outer CS360 receipt digest cannot hide readiness-lineage drift.

## Tests

`tests/test_phase18_qwen_image_canonical_candidate_semantic_base_qa.py`

Added/extended regression coverage for:

- successful snapshot + readiness provenance propagation;
- rejecting unverified readiness before the semantic inspector is called;
- rejecting invalid readiness paths before semantic inspection;
- rejecting readiness SHA tampering even when the outer CS360 receipt digest is recomputed;
- preserving existing snapshot-lineage, exact candidate-byte, local-only, verifier-identity, semantic rejection, and authority-closure tests.

## Authority preservation

CS386 does not load Qwen-Image, generate or mutate pixels, upload, publish, or grant identity/Human Review/Golden/publication authority. Existing factual, identity, sentiment, zero-cost, semantic-publication, and visual-quality gates remain independent and fail-closed.

## Exact code-and-test SHA

`be97d7469eb211b6c67e5cbf3c7ad98e9830f1e9`

GitHub Actions is authoritative for terminal-green status; this changeset must not be described as terminal-green until the Phase 18 Story Intelligence Verification succeeds on this SHA or a later SHA containing identical production code and tests.
