# Phase 18 Change Set 244 — First Genuine Production Gate Verifier

## Scope

Change Set 244 advances the non-GPU side of the first Genuine Golden Visual path by implementing the first real production-backed semantic replay verifier: `zero_cost_policy`.

This change does **not** authorize canonical generation. Five required fresh-story gates still lack genuine production adapters, the canonical production registry remains atomically empty, no model weights are loaded, no inference is executed, and no Golden PNG is claimed.

## Why this is a real verifier

The new verifier does not echo a receipt and is not a fixture/stub. It reads the exact evidence bytes, parses a strict JSON evidence contract, binds the evidence to the same story snapshot, enforces `$0-local`, requires a `local_free` billing class, rejects payment-method requirements, rejects external paid API use, requires local-only canonical execution, and re-evaluates provider economics using the existing production `DevelopmentCostPolicy`.

The existing development cost policy remains the underlying economics policy. Change Set 244 intentionally strengthens the canonical Golden-trial replay boundary beyond the generic development allowance: a free-tier remote provider is rejected even where generic development evaluation might allow it, because the canonical target remains `$0-local`.

## Added

- `engine/intelligence/qwen_image_zero_cost_policy_gate_verifier.py`
- `tests/test_phase18_qwen_image_zero_cost_policy_gate_verifier.py`
- `docs/PHASE18_CHANGESET_244_FIRST_PRODUCTION_ZERO_COST_VERIFIER.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_244.md`

## Modified

- `engine/intelligence/qwen_image_production_gate_verifier_registry.py`
  - documentation now records that the first genuine adapter exists;
  - registry remains empty under an atomic six-gate cutover policy.

## Deleted

None.

## Evidence contract

The zero-cost verifier requires exactly these evidence fields:

- `schema`
- `gate_id`
- `story_snapshot_sha256`
- `cost_mode`
- `provider_id`
- `billing_class`
- `requires_payment_method`
- `external_paid_api_used`
- `canonical_execution_local_only`

Required semantic state:

- schema: `pul7sar-phase18-zero-cost-policy-evidence-v1`
- gate: `zero_cost_policy`
- story SHA: exact current story snapshot
- cost mode: `$0-local`
- billing class: `local_free`
- payment method required: `false`
- external paid API used: `false`
- canonical execution local only: `true`

The replay output recomputes evidence SHA-256 and byte size from the actual file and emits deterministic verification details for Change Set 238 to bind against the original gate receipt.

## Production provenance

The canonical adapter `replay_zero_cost_policy_gate` declares:

- stable verifier ID/version;
- gate ID `zero_cost_policy`;
- `PUL7SAR_PRODUCTION_BACKED = True`;
- the actual source callable object `verify_zero_cost_policy_evidence`;
- source module/callable metadata compatible with Change Set 241 source-object/source-byte binding.

## Atomic registry policy

Although the zero-cost adapter is genuine, `GATE_REPLAY_VERIFIERS` remains empty until all six required adapters exist. This is intentional. Change Set 238 requires an exact six-gate ordered verifier set; a partial registry cannot execute a valid semantic replay. Keeping the canonical registry empty prevents partial wiring from being confused with a runnable production replay set.

## Gates preserved

No weakening was made to Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, Story Semantic Preflight, Semantic/Layer Ownership, visual quality, human review, exact brand/typography, or SemanticPublicationGate.

The following remain false/unproven until later stages:

- `fresh_story_gates_passed`
- `canonical_generation_authorized`
- `model_weights_loaded`
- `inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

## Remaining gap

Production semantic adapters still required:

1. `fact_lock`
2. `entity_identity_verification`
3. `sentiment_neutrality`
4. `story_semantic_preflight`
5. `semantic_layer_ownership`

`zero_cost_policy` is now implemented as the first genuine production-backed verifier.

After all six exist: atomic registry cutover → Change Set 241 readiness → genuine fresh Change Set 238 semantic replay → explicit generation authorization → compatible `$0-local` CUDA execution → Genuine Golden PNG → semantic/layer QA → byte-bound Visual Critic → human review → Golden quality threshold → exact brand/typography → SemanticPublicationGate.
