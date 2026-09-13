# PUL7SAR Phase 18 — Golden Hybrid v5 Engineering Record

## Why v5 exists

The first real GPU proofs established that a diffusion model can produce a valid PNG but cannot be trusted to own every factual/structural pixel. Two failures were especially important:

1. malformed football-field proportions and markings,
2. generated pseudo-platform text/wordmark.

Golden Hybrid v5 changes ownership rather than adding another longer prompt.

## Architecture change

### Before
`story -> prompt -> diffusion draws complete stadium/pitch/branding scene`

### v5
`story -> editorial/visual plan -> atmosphere-only generation -> deterministic football surface replacement -> verified/deterministic exact layers -> QA`

## Dynamic brand system

### Added
- `engine/intelligence/dynamic_brand.py`
- `engine/intelligence/dynamic_brand_contrast.py`
- `engine/intelligence/dynamic_brand_geometry.py`

### Rules
- default **7 + pulse** accent: `#E10600`,
- contextual accent requires one unambiguous hero + strong verified palette evidence,
- ambiguous multi-entity stories return to red,
- brand structure never belongs to diffusion,
- low contrast adds a keyline instead of changing the verified accent,
- code-native brand geometry remains fail-closed until its exact font/pulse recipe is explicitly approved.

`docs/BRAND_GUIDELINES.md` was upgraded to the dynamic-brand policy.

## Brand-name prompt redaction

### Modified
- `engine/intelligence/generation_package.py`
- `engine/intelligence/local_backend_execution.py`
- `engine/intelligence/provider_prompting.py`
- `engine/intelligence/hybrid_base_scene_contract.py`

The image-model prompt no longer repeats `PUL7SAR` / `PULSAR` even in negative instructions.

Instead it receives generic constraints:
- fully unbranded,
- no platform names,
- no readable text,
- no logos/wordmarks,
- exact branding later.

Both generation-package and local-backend boundaries fail closed if the protected platform token appears in the final generative prompt.

This is intentional: telling a diffusion model repeatedly “do not write X” still exposes X as a token and can increase the chance of pseudo-wordmark generation.

## Football deterministic surface

### Added
- `engine/intelligence/football_pitch_placement.py`
- `engine/intelligence/football_hybrid_composer.py`

### Expanded
- `engine/intelligence/football_pitch_renderer.py`

The final football surface is based on the existing 105m × 68m world geometry and projective homography.

v5 adds:
- validated image-space pitch quadrilaterals,
- camera presets,
- opaque surface replacement,
- exact white markings,
- centre/penalty marks,
- deterministic mowing bands,
- durable composition receipt.

The opaque replacement is important: wrong generated pitch markings cannot remain visible underneath the deterministic layer.

## Hybrid base-scene contract

### Added
`engine/intelligence/hybrid_base_scene_contract.py`

When football geometry belongs to code, generation receives only:
- stadium atmosphere,
- lighting,
- depth,
- crowd/environment mood,
- a plain unmarked surface region.

It is explicitly told not to paint field/court/rink markings in that reserved region.

## Receipt-backed QA

### Added
`engine/intelligence/hybrid_evidence_builder.py`

Final QA does not consider geometry “done” merely because a plan requested it. A football surface counts as completed only when a real `FootballHybridCompositionReceipt` proves:
- deterministic geometry applied,
- generated markings replaced,
- opaque surface (`255`).

## Unified execution plan

### Added
`engine/intelligence/visual_execution_plan.py`

The CPU-side plan now carries:
- headline,
- visual family,
- production mode,
- base-scene ownership contract,
- geometry executor,
- camera preset,
- dynamic brand accent/reason,
- exact layer ownership,
- hard verification requirements.

## Golden benchmark migration

### Modified
- `tools/phase18_build_golden_handoff.py`
- `tools/phase18_build_golden_batch.py`
- `tools/phase18_verify_golden_batch.py`
- `engine/intelligence/golden_smoke.py`
- `tools/phase18_colab_runner.py`

### Active contract
- benchmark: `golden-visual-season-opener-hybrid-v5`
- manifest: `pul7sar-golden-batch-v5`
- composition: `single_continuous_scene`
- geometry owner: `deterministic_football_pitch_projective_v1`
- generated sport geometry: forbidden
- deterministic surface replacement: required
- camera preset: `high_wide_central`
- generated platform branding: forbidden
- brand policy: `dynamic_deterministic_after_generation`

## Colab simplification

### Added / upgraded
- `tools/phase18_cpu_validate.py`
- `tools/phase18_colab_one_command.py`

The intended next Colab interaction is one command after the checkout exists:

```python
%cd /content/pul7sar-bot
%run tools/phase18_colab_one_command.py --candidate 1 --force
```

Flow:
1. fast-forward protected branch,
2. discover and run all Phase 18 CPU tests,
3. build/verify Golden Hybrid v5,
4. execute one atmosphere-only FLUX candidate,
5. deterministically replace football surface,
6. display hybrid proof.

It does **not** declare publication readiness. Dynamic brand geometry, typography, semantic inspection and final Golden visual-quality review remain separate gates.

## CI

`.github/workflows/phase18-intelligence.yml` now targets Golden Hybrid v5 and uses discover-based Phase 18 validation before building/verifying handoffs.

## Tests added / changed in this v5 block

- `tests/test_phase18_dynamic_brand.py`
- `tests/test_phase18_dynamic_brand_contrast.py`
- `tests/test_phase18_dynamic_brand_geometry.py`
- `tests/test_phase18_editorial_dynamic_brand_integration.py`
- `tests/test_phase18_football_hybrid_composer.py`
- `tests/test_phase18_hybrid_base_scene_contract.py`
- `tests/test_phase18_hybrid_evidence_builder.py`
- `tests/test_phase18_visual_execution_plan.py`
- `tests/test_phase18_brand_prompt_redaction.py`
- v5 migrations for Golden batch, unified scene, smoke and Colab-runner tests.

## Deliberately not claimed yet

- No Golden Hybrid v5 GPU visual has been accepted yet.
- The new full CPU suite has not yet been observed executing successfully in the live Colab runtime after these latest changes.
- The final code-native wordmark/pulse geometry is not approved yet; the registry intentionally refuses to invent it.
- Final typography/brand composition is not yet part of the v5 GPU proof.

These are explicit remaining gates, not hidden assumptions.
