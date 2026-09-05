# PUL7SAR Phase 18 — Change Set 068: Exact Branding Exclusion

## Trigger
The second genuine Golden Visual proof showed two independent visual failures:
1. malformed association-football pitch geometry; and
2. a generated text treatment spelling `PUL7SAR` inside the AI-created base scene.

The latter is not the approved PUL7SAR logo and violates the project architecture: exact PUL7SAR branding must be applied only by deterministic post-composition from approved assets.

## Root cause
The generation package already instructed the model not to imitate PUL7SAR branding, but the instruction was not sufficiently explicit for the observed FLUX.2 output. The provider also has no native negative-prompt channel in the current path, so exact brand exclusion must be represented as deterministic positive provider instructions and verified in the Golden handoff before GPU execution.

## Changes

### `engine/intelligence/generation_package.py`
Strengthens the universal AI base-scene contract:
- zero generated PUL7SAR lettering;
- never spell `PUL7SAR`, `PULSAR`, or approximations;
- no generated PUL7SAR wordmark, number-7 treatment, pulse mark, badge, watermark or signature;
- neutral/unbranded advertising boards, banners, screens and sponsor surfaces;
- no legible words, letters, numerals, pseudo-text or fake logos in the AI base scene;
- exact branding and typography remain deterministic post-composition assets.

Adds metadata:
- `generated_branding_allowed=false`.

### `engine/intelligence/provider_prompting.py`
Adds a deterministic positive reframe for:
`no generated branding, wordmarks, readable text, or pseudo-text`

This keeps FLUX-like providers fail-closed rather than silently dropping the constraint.

### `engine/intelligence/golden_visual_quality.py`
Adds hard blocker:
`generated_platform_brand_or_wordmark`

A visually strong candidate is rejected if the generative model invents PUL7SAR branding or a substitute platform wordmark.

### `tools/phase18_build_golden_handoff.py`
Golden benchmark advances to `golden-visual-general-season-opener-v4`.

The benchmark now combines:
- one continuous scene;
- regulation association-football pitch geometry;
- zero generated platform branding/text;
- exact PUL7SAR branding only after generation.

### `tools/phase18_build_golden_batch.py`
Manifest advances to `pul7sar-golden-batch-v4` and records:
- `generated_branding_allowed=false`;
- `brand_composition_policy=exact_assets_only_after_generation`.

### `tools/phase18_verify_golden_batch.py`
V4 fails closed unless the manifest and SHA-protected prompts preserve the brand-exclusion lock before GPU inference.

### Regression tests
Updated:
- `tests/test_phase18_unified_scene_policy.py`
- `tests/test_phase18_golden_visual_quality.py`

The tests verify provider reframing, v4 manifest policy, prompt markers, tampered branding permission rejection, and the new hard blocker.

## Production isolation
Untouched:
- `main`
- `main.py`
- Telegram production publishing
- legacy production image path

No paid API, production secret, model weight or font file was added.

## Next validation
Pull the Phase 18 branch into Colab, run the targeted tests, then generate only v4 Candidate 1. The candidate must be judged simultaneously on:
1. single continuous composition;
2. regulation football-pitch geometry;
3. absence of generated PUL7SAR branding/text;
4. premium editorial quality.

Only after Candidate 1 clears these basic visual contracts should GPU time be spent on Candidates 2–4.
