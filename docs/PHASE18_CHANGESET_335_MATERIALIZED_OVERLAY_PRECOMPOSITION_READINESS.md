# Phase 18 Change Set 335

## Materialized Overlay Precomposition Readiness

CS335 removes the manual control-plane gap between the CS334 materialized-overlay manifest bundle and the already-existing CS269, CS270, and CS331 gates.

The continuation is deliberately bounded **before CS271 one-shot composition**. It never invokes the production composer, never consumes the one-shot attempt, never creates or changes pixels, and never upgrades semantic, brand-publication, human-review, Golden, or publication authority.

## Inputs

- exact repository-bound CS268 generated-layer QA receipt;
- exact repository-bound CS334 materialized-overlay composition manifest bundle;
- repository root;
- a new output directory.

The supported first-Golden target remains the low-risk CS334 target whose required non-generative layers are limited to `editorial_typography` and `pul7sar_brand`. Identity-sensitive required layers remain fail-closed upstream.

## Required replay

CS335 must:

1. reopen the CS334 bundle and its exact CS269/CS270 manifest bytes;
2. require CS334 `composition_input_binding_ready=true` while all downstream authorities remain false;
3. invoke the original CS269 builder and independently verify its receipt;
4. require `composition_request_ready=true` on the same story and candidate bytes;
5. invoke the original CS270 builder and independently verify its receipt;
6. require `composition_execution_ready=true` on the same story and candidate bytes;
7. invoke the original CS331 builder and independently verify its receipt;
8. require `overlay_execution_ready=true` on the same story and candidate bytes;
9. bind the resulting CS269, CS270, and CS331 receipts into one non-authoritative checkpoint.

The independent CS335 verifier must reopen the full chain and prove that CS270 points to the exact CS269 receipt and CS331 points to the exact CS270 receipt.

## Authority boundary

CS335 may set only:

- `precomposition_execution_ready=true`

It must keep:

- `cs271_attempt_consumed=false`
- `composition_executed=false`
- `composed_visual_approved=false`
- `semantic_approved=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`
- `authoritative=false`

Readiness is not permission to publish and is not evidence that any composed or Golden PNG exists.

## Preserved gates

CS335 does not weaken or replace Fact/Freshness, Entity/Identity, sentiment neutrality, loser-respect, `$0-local`, Generated-Layer QA, deterministic/verified ownership, visual-quality, Human Review, Exact Brand/Typography, Final Composed Approval, Final Semantic Approval, `SemanticPublicationGate`, CS285, or CS286.

## Runtime boundary

CS335 is CPU/control-plane only. It must contain no model loading, Qwen inference, network fallback, image rendering/composition, upload, or publish side effect.

A genuine Golden Visual remains blocked until a compatible zero-cost CUDA/BF16 host can produce the genuine candidate and the real approved overlays can traverse this chain and the downstream composition/semantic/visual/human/brand/publication gates.
