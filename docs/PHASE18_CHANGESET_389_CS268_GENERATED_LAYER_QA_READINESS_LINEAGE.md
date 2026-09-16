# Phase 18 Change Set 389 — CS268 Generated-Layer QA Readiness Lineage

## Scope

This change set advances the canonical Qwen-Image candidate path without changing `main` and without claiming genuine inference, Golden materialization, or publication authority.

Starting branch HEAD: `788cc1e5d8ee91705f04c2f08d44427cf5cc6ace`.

The real downstream consumer after CS267 was confirmed to be CS268 Generated-Layer QA. The no-Pixel-Identity-Review branch reaches CS268 directly after CS265; the identity-required branch reaches CS268 only after CS266/CS267 evidence is available.

## Gap closed

Before CS389, CS268 preserved exact generator snapshot-byte lineage but did not preserve the first-class `static_readiness_receipt` lineage that CS360/CS305/CS266/CS267 now carry from CS351. This created a provenance drop before the base candidate entered generated-layer ownership/leakage QA.

## Production change

Modified `engine/intelligence/qwen_image_canonical_candidate_generated_layer_qa.py`.

- Schema advanced from `pul7sar-phase18-qwen-image-canonical-candidate-generated-layer-qa-v2` to `...-v3`.
- Added structural validation for the replay-verified CS351 readiness binding:
  - `repository_relative_path`
  - `sha256`
  - `byte_size`
  - `static_readiness_receipt_verified=true`
- CS268 now derives readiness lineage from freshly verified CS264 and requires exact equality in freshly verified CS265 before generated-layer QA executes.
- When Pixel Identity Review is required, CS268 additionally requires exact readiness equality in freshly verified CS267 before accepting `identity_approved=true`.
- The CS268 receipt now carries the exact readiness binding and marks it verified.
- Verification replays CS264/CS265 and, when required, CS267, then compares the stored readiness binding against fresh upstream evidence. Recomputing the outer CS268 digest does not hide readiness drift.
- Policy now records `static_cuda_readiness_lineage_preserved=true`.

Production commit: `3a30197d27de1b1582d32f2847e569e994600762`.

## Regression coverage

Modified `tests/test_phase18_qwen_image_canonical_candidate_generated_layer_qa.py`.

Added fixtures carrying the readiness binding through CS264, CS265, CS266 and CS267, plus regressions covering:

- successful readiness propagation into CS268;
- rejection when CS264 lacks readiness authority before the generated-layer gate runs;
- rejection when required CS267 identity evidence carries a different readiness binding;
- rejection after readiness SHA tampering even when the outer CS268 `receipt_sha256` is recomputed.

Existing snapshot inventory, snapshot tamper, candidate-byte drift, generated-text leakage, unverified-identity leakage, identity-required evidence, no-fabricated-identity and output-isolation coverage remains in place.

Exact code-and-test-bearing commit: `4739ca48db94accc0320cb6553b6f03a41a0e0cc`.

## Preserved authority boundaries

CS389 does not load Qwen-Image, execute inference, mutate pixels, compose deterministic layers, upload artifacts, publish content, use paid execution, or introduce a network-model fallback.

At the CS268 boundary the following remain closed: `composition_executed`, `composed_visual_approved`, `semantic_approved`, `human_visual_review_approved`, `genuine_golden_png_created`, `golden_quality_approved`, and `publication_ready`.

Factual/freshness, entity/identity, sentiment/loser-respect, zero-cost/local-only, semantic QA, visual-quality, Human Review, Brand/Typography, Final Composed, Final Semantic, SemanticPublicationGate, Genuine-Golden materialization and external publication authority remain separate fail-closed gates.

## Genuine Golden status

No production `canonical_candidate.png` or `genuine_golden_visual.png` is claimed by this change set. Genuine Qwen-Image inference still requires a compatible zero-cost NVIDIA CUDA host with CUDA-enabled PyTorch, native BF16, sufficient RAM/VRAM and the approved already-local pinned model assets.
