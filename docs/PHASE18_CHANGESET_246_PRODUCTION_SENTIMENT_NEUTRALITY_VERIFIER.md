# Phase 18 Change Set 246 — Production Sentiment / Neutrality Verifier

## Purpose

Change Set 246 advances the pre-Golden semantic replay path by implementing a genuine production-backed `sentiment_neutrality` gate instead of treating candidate metadata or a test fixture as semantic verification.

This change does **not** authorize image generation, reuse generated pixels, approve semantics, approve a human review, award a Golden score, or make any asset publishable.

## Added production policy

`engine/intelligence/sentiment_neutrality.py` introduces a deterministic, conservative editorial policy that evaluates publication-facing story copy for:

- humiliating, mocking, degrading, shame-oriented, or inferiority-oriented language;
- unsupported emotional-state attribution;
- explicit opponent/losing-side context for competitive-result stories;
- non-empty editorial text fields;
- explicit source-backed emotional attribution when a non-degrading emotional state is reported.

The policy supports high-confidence English and Arabic rejection terms. Ambiguous rhetoric is not promoted into a factual or neutral statement by this gate.

## Added production replay verifier

`engine/intelligence/qwen_image_sentiment_neutrality_gate_verifier.py` re-reads exact JSON evidence bytes, verifies the evidence schema, gate ID, story SHA-256, and verifier identity/version, then recomputes the policy decision from the editorial text itself.

The successful replay result byte-binds the evidence via SHA-256 and byte size. A cross-story evidence file is rejected.

The adapter exposes Change Set 241 provenance metadata and binds a replay-compatible production source callable. The underlying editorial decision is delegated to the deterministic production sentiment policy.

## Regression coverage

`tests/test_phase18_qwen_image_sentiment_neutrality_gate_verifier.py` covers:

- respectful competitive-result copy passes;
- degrading loser/opponent language fails closed;
- Arabic humiliating language fails closed;
- unsupported emotional attribution fails closed;
- a source-backed non-degrading emotional attribution may pass;
- a competitive result without opponent/loser semantic context fails closed;
- cross-story evidence fails closed;
- verifier identity drift fails closed;
- empty publication-facing copy fails closed;
- production provenance metadata points at the actual replay-compatible verifier callable.

## Atomic registry policy

The canonical `GATE_REPLAY_VERIFIERS` registry remains empty. Phase 18 continues to require an atomic six-gate cutover. A partial registry must never be mistaken for a production-executable replay set.

After this change the implemented genuine adapters are:

1. `fact_lock`
2. `sentiment_neutrality`
3. `zero_cost_policy`

Still required before atomic registry cutover:

1. `entity_identity_verification`
2. `story_semantic_preflight`
3. `semantic_layer_ownership`

## Authority remains fail-closed

This change does not make any of the following true:

- `production_semantic_replay_executed`
- `fresh_story_gates_passed`
- `canonical_generation_authorized`
- `canonical_pixels_reusable`
- `model_weights_loaded`
- `inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

## Golden execution blocker

No genuine Golden PNG is claimed by this change. Canonical generation still requires a compatible, zero-cost local runtime that proves the Phase 18 CUDA/BF16/VRAM/RAM/model-revision/Diffusers/QwenImagePipeline/offload contract before inference is allowed.
