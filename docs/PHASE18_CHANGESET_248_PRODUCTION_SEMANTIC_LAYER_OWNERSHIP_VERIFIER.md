# Phase 18 Change Set 248 — Production Semantic / Layer Ownership Verifier

## Purpose

Change Set 248 closes the fifth of six production semantic replay adapter gaps required before the Change Set 238 fresh-story semantic replay can be wired atomically.

The new `semantic_layer_ownership` gate enforces the architectural boundary already established by `HybridVisualLayerPlanner` and `HybridLayerQualityGate`: Qwen-Image may own atmosphere, depth, mood, environment and other non-factual texture, while exact information remains outside unconstrained diffusion.

This Change Set does **not** authorize model loading, inference, Golden acceptance, branding approval, human approval, or publication.

## Production policy

`engine/intelligence/semantic_layer_ownership.py` adds a deterministic, fail-closed replay policy with a byte-bound evidence schema.

For a canonical Qwen candidate it requires:

- `atmosphere_base` to be generative and limited to non-factual atmosphere;
- exact sport-surface geometry to be deterministic when the story actually requires exact geometry;
- identity-sensitive hero material to be a verified asset when a primary identity is present;
- exact entity marks to remain verified assets;
- scores, statistics, dates and exact numbers to remain deterministic;
- editorial typography to remain deterministic;
- the exact PUL7SAR brand to remain a verified asset;
- no duplicate, unknown, reordered, or source-drifted canonical layer declarations;
- literal Boolean control flags rather than truthy substitutes;
- zero leakage findings from the existing `HybridLayerQualityGate` for generated text, platform branding, exact numbers, entity marks, unverified identity, or deterministic sport geometry.

The verifier rereads the evidence bytes and returns their SHA-256 and byte size. Story SHA, gate ID, evidence schema, verifier ID and verifier version are checked before semantic acceptance.

## Production replay adapter

`engine/intelligence/qwen_image_semantic_layer_ownership_gate_verifier.py` exposes the Change Set 238-compatible three-argument replay callable and the Change Set 241 provenance metadata.

`PUL7SAR_SOURCE_CALLABLE_OBJECT` points directly at `verify_semantic_layer_ownership_evidence` in the production policy module, so readiness binds the policy source bytes rather than only the adapter wrapper.

## Regression coverage

`tests/test_phase18_qwen_image_semantic_layer_ownership_gate_verifier.py` covers:

- a canonical identity-sensitive + exact-geometry layer plan;
- a story without identity-sensitive hero material or exact sport geometry;
- generated typography leakage;
- generated platform-brand leakage;
- generated exact-number leakage;
- generated entity-mark leakage;
- generated unverified-identity leakage;
- generated deterministic sport-geometry leakage;
- an attempt to assign the exact data layer to the generative model;
- a missing verified hero layer for an identity-sensitive story;
- cross-story evidence reuse;
- verifier identity drift;
- non-Boolean control flags;
- production source-object provenance;
- source evidence SHA-256 and byte-size reporting.

Tests use the repository's standard-library `unittest` convention and add no dependency.

## Registry state

The canonical registry remains intentionally empty:

```python
GATE_REPLAY_VERIFIERS = {}
```

After Change Set 248, five genuine production-backed adapters exist:

1. `fact_lock`
2. `entity_identity_verification`
3. `sentiment_neutrality`
4. `zero_cost_policy`
5. `semantic_layer_ownership`

Only `story_semantic_preflight` remains. The six-gate registry cutover stays atomic to prevent a partial set from being mistaken for executable production replay.

## Authority remains closed

This Change Set does not make any of the following true:

- `production_semantic_replay_executed`
- `fresh_story_gates_passed`
- `canonical_generation_authorized`
- `model_weights_loaded`
- `inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

Fact Lock, entity/identity verification, sentiment/neutrality, `$0-local`, semantic-publication, Visual Critic, Human Review, Golden score thresholds, Exact Brand and Exact Typography remain independent fail-closed gates.

## GPU status

No CUDA or Qwen-Image inference is performed by this Change Set. A genuine Golden PNG remains blocked until a zero-cost local host can prove the full pinned runtime contract: NVIDIA CUDA, native BF16, sufficient live VRAM and system RAM, the exact pinned `Qwen/Qwen-Image-2512` snapshot/revision, a compatible `Diffusers/QwenImagePipeline`, successful sequential CPU offload, and canonical local-only `$0` execution.
