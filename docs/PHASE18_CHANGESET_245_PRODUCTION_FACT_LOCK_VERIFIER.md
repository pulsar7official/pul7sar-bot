# Phase 18 Change Set 245 — Production Fact Lock Verifier

## Purpose

Advance the first genuine Golden Visual path by converting the existing deterministic `FactLock` enforcement into a real production-backed replay verifier for the `fact_lock` gate, without changing generation authority or the canonical six-gate registry.

## Why this is genuine production logic

`engine/intelligence/fact_lock.py` already implements deterministic factual-safety enforcement. It separates explicit `FACT` claims from `SAFE_INFERENCE` and `FORBIDDEN`, rejects publishability when forbidden claims exist, and requires an exact normalized fact to be present at a configured confidence floor instead of silently inferring it.

Change Set 245 wraps that existing production behavior in the Phase 18 replay contract. It does not discover facts, call a model, or claim that an upstream classification is true merely because it exists. The evidence must already contain byte-bound classified claims. The verifier then independently reconstructs `LockedClaim` objects and re-runs `FactLock` semantics.

## Evidence contract

Schema: `pul7sar-phase18-fact-lock-evidence-v1`

Required top-level fields, in canonical order:

1. `schema`
2. `gate_id`
3. `story_snapshot_sha256`
4. `minimum_fact_confidence`
5. `claims`
6. `required_facts`

Each claim must contain, in canonical order:

1. `text`
2. `kind`
3. `source`
4. `confidence`
5. `metadata`

Additional fail-closed rules:

- every `FACT` must carry a non-empty source;
- `required_facts` must be non-empty and normalized-unique;
- a `SAFE_INFERENCE` cannot satisfy `require_fact`;
- any `FORBIDDEN` claim causes semantic rejection;
- every required fact must be an explicit `FACT` at or above `minimum_fact_confidence`;
- evidence must belong to the exact story snapshot SHA supplied to replay;
- verifier ID/version in the receipt must match the production adapter.

## Production provenance

Adapter: `replay_fact_lock_gate`

Source verifier: `verify_fact_lock_evidence`

Verifier ID: `pul7sar.production.fact_lock`

Verifier version: `1.0.0`

The adapter declares the source callable object required by the Change Set 241 source-object/source-byte readiness contract.

## Authority boundaries

This Change Set grants only a genuine production implementation for one semantic replay gate. It does **not** mutate the canonical production registry and does not set any of the following to true:

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

The canonical registry remains fail-closed until all six genuine production-backed adapters are available for an atomic cutover.

## Tests

`tests/test_phase18_qwen_image_fact_lock_gate_verifier.py` covers:

- successful replay of a source-backed required fact;
- forbidden-claim rejection;
- safe-inference refusal as a required fact;
- missing fact source rejection;
- confidence-floor rejection;
- cross-story evidence rejection;
- duplicate normalized required-fact rejection;
- receipt verifier-identity rejection;
- production provenance metadata.

## Remaining production adapters

After this Change Set, genuine implementations exist for:

- `fact_lock`
- `zero_cost_policy`

Still required before atomic registry cutover:

- `entity_identity_verification`
- `sentiment_neutrality`
- `story_semantic_preflight`
- `semantic_layer_ownership`

## Golden PNG blocker

No image inference is executed by this Change Set. A genuine canonical Golden Visual still additionally requires a compatible zero-cost local runtime proving NVIDIA CUDA, native BF16, adequate VRAM/RAM, the exact pinned Qwen/Qwen-Image-2512 revision, compatible `QwenImagePipeline`, and successful sequential CPU offload before canonical generation may be authorized.
