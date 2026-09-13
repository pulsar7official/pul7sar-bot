# Phase 18 Change Set 269 — Canonical Candidate Deterministic Composition Request

## Purpose

CS269 creates the fail-closed handoff between an exact CS268-approved generated/base candidate and the deterministic/verified composition stage. It does **not** render a composed image and it does not grant semantic, Golden, human-review, or publication authority.

## Inputs

1. An exact CS268 receipt that independently verifies with `generated_layer_qa_approved=true`.
2. The exact candidate PNG already bound by CS268.
3. A repository-resident composition-input manifest using schema `pul7sar-phase18-deterministic-composition-input-manifest-v1`.

## Ownership preservation

CS269 reuses the `hybrid_layer_plan` carried by CS268, which itself is evaluated against the existing `HybridLayerQualityGate`. A manifest may not change a layer's owner.

- `generative`: only the already-admitted base candidate may own the generative layer.
- `deterministic`: the manifest must name a renderer contract and bind the deterministic payload by SHA-256.
- `verified_asset`: the manifest must bind the exact repository file bytes by repository-relative path, SHA-256, and byte size.
- `optional`: absence is allowed only when the upstream plan marks the layer optional.

Required non-generative layers missing from the manifest leave the request blocked. Unknown layers and source-owner drift are rejected.

## Byte/provenance replay

The builder and verifier reject symlinked or repository-escaping paths. The verifier reopens and rehashes:

- the CS268 receipt,
- the candidate PNG,
- the composition manifest,
- every supplied verified asset.

It then recomputes the normalized plan/manifest relationship. Changing any bound bytes invalidates the request.

## Authority

The only new positive authority is:

`composition_request_ready=true`

when all required composition inputs are complete and correctly owned.

The following remain false even for a ready request:

- `composition_executed`
- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `golden_quality_approved`
- `publication_ready`

A ready request is therefore permission to enter deterministic/verified composition, not evidence that composition happened.

## Zero-cost and safety posture

CS269 introduces no paid service, external API, model call, or renderer dependency. It is a CPU/control-plane contract and does not weaken Fact Lock, Entity/Identity, Sentiment Neutrality, Zero-Cost, Semantic Publication, Visual Critic, Human Review, Golden thresholds, or Exact Brand/Typography requirements.

## Next boundary

The next production boundary should consume only a verified CS269 request, execute the existing deterministic/verified composition implementation, save the composed PNG atomically, and bind those exact output bytes before any post-composition semantic/layer QA is permitted.
