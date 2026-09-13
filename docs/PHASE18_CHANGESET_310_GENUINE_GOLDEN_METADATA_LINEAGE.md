# Phase 18 Change Set 310 — Genuine Golden Metadata Lineage

## Purpose

CS310 hardens the CS285 Genuine Golden materialization verifier so every materialization metadata field that is consumed by the downstream CS286 publication-readiness authority remains derived from the exact successfully re-verified CS284 SemanticPublicationGate execution.

The change does not generate pixels, alter pixels, change quality thresholds, grant semantic approval, or grant publication readiness.

## Proven gap

CS285 already re-opened the exact CS284 receipt and the exact composed PNG, verified SemanticPublicationGate authority, validated PNG structure, and enforced byte identity for the materialized Golden PNG.

However, before CS310, `verify_genuine_golden_materialization()` did not re-compare all CS285 metadata against the re-verified CS284 receipt. In particular, these fields were emitted by CS285 and then consumed by CS286:

- `generation_context`
- `weighted_score`
- `quality_tier`
- the CS285 materialization `policy`

A syntactically self-consistent CS285 receipt could therefore have those fields changed and have its unkeyed content digest recomputed while still retaining an exact valid CS284 binding and byte-identical PNGs. CS286 subsequently copied the metadata into its final `publication_ready=true` receipt.

This was a provenance-integrity gap, not a pixel-generation or SemanticPublicationGate bypass.

## Production hardening

`engine/intelligence/qwen_image_genuine_golden_materialization.py` now:

1. Defines one canonical `MATERIALIZATION_POLICY` used by both build and verification.
2. Re-confirms the re-opened CS284 schema during CS285 verification.
3. Calls `_require_materialization_receipt_matches_cs284()` before accepting a CS285 receipt.
4. Requires exact equality with the verified CS284 values for:
   - story snapshot SHA-256;
   - source composed PNG binding;
   - generation context;
   - weighted score;
   - quality tier.
5. Requires the materialization policy to equal the canonical fail-closed policy exactly.
6. Keeps the existing exact source-CS284 receipt binding, source/materialized PNG byte identity checks, PNG structure/CRC checks, and `publication_ready=false` boundary.

## Regression coverage

`tests/test_phase18_qwen_image_genuine_golden_materialization.py` now covers:

- acceptance of exact CS284-derived materialization metadata;
- generation-context drift rejection;
- weighted-score drift rejection;
- quality-tier drift rejection;
- materialization-policy drift rejection;
- the pre-existing PNG integrity and CS284 authority checks.

## Preserved gates

CS310 does not modify or bypass:

- factual/freshness locks;
- entity/identity verification;
- sentiment neutrality or loser-respect policy;
- `$0-local`, offline, or local-files-only requirements;
- Semantic Base QA or Generated-Layer QA;
- composition QA;
- Golden visual-quality adjudication;
- Human Visual Review;
- exact Brand/Typography review;
- Final Composed Approval;
- Final Semantic Approval;
- `SemanticPublicationGate`;
- exact-byte Genuine Golden materialization;
- separate publication-readiness authority.

CS285 continues to assert `genuine_golden_png_created=true` only after successful materialization and continues to assert `publication_ready=false`.

## Runtime reality

CS310 does not claim a production Golden PNG. A genuine artifact still requires the upstream Qwen-Image generation path to run on a compatible zero-cost CUDA/BF16 host and then pass every existing factual, identity, sentiment, semantic, visual-quality, human, brand, publication, and exact-byte gate.
