# Phase 18 Change Set 387 — CS305 Identity-Requirement Readiness Lineage

## Objective

Preserve the exact replay-verified CS351 CUDA/native-BF16 static-readiness receipt through the first identity-requirement classification boundary after CS360 Semantic Base QA, without adding any new generation, identity approval, semantic approval, Golden, publication, network, or paid-execution authority.

## Proven gap

CS360 schema v4 already carries `static_readiness_receipt` plus `static_readiness_receipt_verified=true`. CS305 freshly verifies CS360 and then derives identity evidence from the candidate launch lineage, but schema v2 did not carry the CS351 readiness binding in its own receipt. That created a provenance continuity drop immediately before pixel-identity review classification.

## Implementation

`engine/intelligence/qwen_image_canonical_candidate_identity_requirement.py` is advanced from schema v2 to v3.

The receipt now requires and carries:

- `static_readiness_receipt.repository_relative_path`
- `static_readiness_receipt.sha256`
- `static_readiness_receipt.byte_size`
- `static_readiness_receipt_verified=true`

`run_identity_requirement()` validates the readiness binding before invoking candidate-lineage identity derivation. `verify_identity_requirement()` freshly replays CS360, re-extracts the verified readiness binding, and compares it exactly with the CS305 receipt. Recomputing the outer CS305 receipt digest cannot hide a rewritten readiness SHA/path/size.

## Gates preserved

This change does not create or imply:

- generated-face identity approval;
- final semantic approval;
- Human Visual Review approval;
- Golden Quality approval;
- Genuine Golden PNG creation;
- publication readiness or external publication authority;
- network-model fallback or paid execution.

Factual/freshness, Entity/Identity, sentiment neutrality/loser-respect, zero-cost local execution, semantic QA, visual-quality, Human Review, Brand/Typography, Final Composed, Final Semantic, SemanticPublicationGate, Genuine-Golden materialization, and publication-readiness remain separate fail-closed authorities.

## Test intent

Regression coverage proves positive readiness propagation, rejects an unverified readiness source before identity-lineage derivation, and rejects readiness digest tampering even after recomputing the outer CS305 receipt digest. Existing candidate-byte, source-byte, identity-evidence, lineage and premature-authority tests remain in place.
