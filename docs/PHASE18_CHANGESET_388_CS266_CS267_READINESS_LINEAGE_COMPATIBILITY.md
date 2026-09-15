# Phase 18 Change Set 388 — CS266 → CS267 Readiness Lineage Compatibility

## Purpose

Close the regression introduced when CS266 Pixel Identity Review Request was upgraded to schema v2 to preserve CS351 CUDA/native-BF16 static-readiness provenance, while ensuring the immediate CS267 Pixel Identity Review Evidence consumer does not drop that provenance.

## Scope

Branch: `phase18/story-intelligence` only. `main` is read-only and is not modified.

This change set covers two linked boundaries:

1. CS266 carries the exact replay-verified `static_readiness_receipt` from CS305 into the pixel-identity review request.
2. CS267 accepts CS266 v2 and carries the same readiness binding into external pixel-identity review evidence, while freshly replaying CS266 during verification and comparing the readiness binding field-by-field.

## Production changes

### CS266

Schema upgraded to `pul7sar-phase18-qwen-image-canonical-candidate-pixel-identity-review-request-v2` and now carries:

- `static_readiness_receipt.repository_relative_path`
- `static_readiness_receipt.sha256`
- `static_readiness_receipt.byte_size`
- `static_readiness_receipt_verified=true`

CS266 verification freshly replays CS305 and rejects readiness authority absence, malformed readiness metadata, or readiness receipt drift.

### CS267

Schema upgraded to `pul7sar-phase18-qwen-image-canonical-candidate-pixel-identity-review-evidence-v2`.

CS267 now:

- requires CS266 to match the imported CS266 schema;
- requires `static_readiness_receipt_verified=true` before admitting external identity evidence;
- copies the exact readiness binding into the CS267 evidence receipt;
- freshly replays CS266 during verification;
- compares the CS267 readiness binding with the fresh CS266 readiness binding;
- rejects outer-receipt recomputation attempts that try to hide readiness tampering;
- preserves all downstream semantic, human-review, Golden, and publication authorities as false.

## Regression coverage

CS267 tests now use CS266 v2 fixtures and cover:

- successful readiness propagation;
- readiness authority missing before external evidence admission;
- readiness digest tampering even when the outer CS267 receipt digest is recomputed;
- existing candidate digest mismatch rejection;
- external review byte drift rejection;
- CS266 request byte drift rejection;
- reviewer identity requirement;
- identity rejection when a required check fails.

## Safety and authority boundaries

This change set does not perform face recognition, model inference, pixel generation or mutation, upload, paid execution, network fallback, or publication. It does not grant final semantic approval, human visual review approval, Golden quality approval, Genuine Golden PNG creation, or publication readiness.

The factual/freshness, Entity/Identity, sentiment and loser-respect, zero-cost local-only, semantic-publication, and visual-quality gates remain fail-closed and independent.

## Exact code-and-test SHA

`bcd5d60e22d0dc57feb591b376f15f1dff5c97a5`

CI result must be recorded in the implementation log after GitHub Actions completes. Until then CS388 is not terminal-green.
