# Phase 18 Change Set 334 — Materialized Overlay Composition Manifest Binding

## Purpose

CS334 removes a manual control-plane gap between the explicit overlay materializers (CS332/CS333) and the existing CS269/CS270 composition contracts for the lowest-risk first Genuine Golden target.

The supported first-target profile intentionally requires no human-identity layer. Its required non-generative layers are limited to:

- `editorial_typography` — deterministic, materialized and independently replayed through CS332;
- `pul7sar_brand` — verified asset, materialized by CS333 from an exact byte-bound tile and explicit placement.

If CS268 requires any additional non-generative layer, including `human_identity`, CS334 fails closed. It does not synthesize a substitute or silently omit the layer.

## Production primitive

`engine/intelligence/qwen_image_materialized_overlay_composition_manifest_bundle.py`

Schema:

`pul7sar-phase18-materialized-overlay-composition-manifest-bundle-v1`

CS334 consumes:

1. an approved CS268 generated-layer QA receipt;
2. an independently verifiable CS332 typography materialization receipt;
3. the exact CS333 brand manifest;
4. the exact CS333 brand receipt and its exact output bytes.

It verifies same-story/same-candidate lineage, exact repository byte bindings, layer ownership, the CS330 full-canvas renderer contract, brand tile digest/size, explicit brand placement, canvas dimensions, and the continuing absence of brand/publication authority.

It then writes exactly two control-plane artifacts:

- a CS269 `pul7sar-phase18-deterministic-composition-input-manifest-v1` manifest;
- a CS270 `pul7sar-phase18-deterministic-composition-payload-manifest-v1` manifest.

CS334 does not invoke a renderer, does not perform Qwen inference, and does not replace CS269 or CS270 verification. The generated manifests must still pass the original CS269 and CS270 gates before CS331/CS271/CS330 composition may occur.

## Fail-closed rules

CS334 rejects at minimum:

- CS268 not approved;
- story or candidate lineage drift;
- CS332 receipt drift or typography output byte drift;
- CS333 contract/ownership drift;
- candidate, brand-tile, brand-output, placement, or canvas drift between CS333 manifest and receipt;
- premature brand, semantic, visual, Golden, or publication authority;
- unsupported required non-generative layers;
- typography/brand ownership drift from the CS268 hybrid plan;
- repository path escape, symlink substitution, missing files, or digest/size drift.

## Authority boundary

A successful bundle may set only:

`composition_input_binding_ready = true`

It must keep:

- `composition_executed = false`
- `semantic_approved = false`
- `human_visual_review_approved = false`
- `golden_quality_approved = false`
- `genuine_golden_png_created = false`
- `publication_ready = false`

PUL7SAR owner/final brand approval remains pending. CS334 does not grant brand publication authority.

## Preserved gates

CS334 does not weaken or bypass Fact/Freshness, Entity/Identity, sentiment neutrality, loser-respect, `$0-local`, generated-layer QA, CS269/270, CS331 readiness, CS271 one-shot execution, CS330 composition, post-composition semantic QA, Visual Critic, Human Review, exact Brand/Typography Review, Final Composed Approval, Final Semantic Approval, `SemanticPublicationGate`, CS285 Genuine Golden materialization, or CS286 publication readiness.

## Genuine Golden impact

Before CS334, correctly materialized CS332/CS333 overlays still required a human/operator to manually translate their byte evidence into the two manifests expected by CS269/CS270. CS334 makes that translation deterministic and fail-closed for the first low-risk no-human-identity target.

A genuine candidate is still required upstream; CS334 does not fabricate one.
