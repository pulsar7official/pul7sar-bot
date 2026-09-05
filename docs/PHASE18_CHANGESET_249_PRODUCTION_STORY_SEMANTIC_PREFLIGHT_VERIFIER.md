# Phase 18 Change Set 249 — Production Story Semantic Preflight Verifier

## Purpose

Change Set 249 implements the sixth required production semantic replay adapter: `story_semantic_preflight`.

This gate does not duplicate Fact Lock, entity/identity verification, sentiment/neutrality, zero-cost policy, or layer-ownership verification. It deterministically replays PUL7SAR's existing `StoryVisualEditorialEngine` against the exact story-bound evidence and ensures that a Qwen generation request is semantically appropriate for that story and matches the project-native visual grammar.

Passing this gate grants no CUDA, generation, visual-quality, Golden, human-review, Exact Brand/Typography, or publication authority.

## Evidence contract

`engine/intelligence/story_semantic_preflight.py` requires a strict evidence object containing:

- the common story snapshot SHA-256;
- an explicit literal-Boolean Qwen generation request;
- the editorial request: event, sport, story core, editorial angle, short headline, subjects, stakes, sentiment, exact assets, geometry requirements and confidence;
- the proposed visual plan: visual family, production mode, scene concept, generated elements and forbidden generated elements.

The verifier reconstructs the project-native plan with `StoryVisualEditorialEngine` and requires exact agreement with the proposed visual grammar.

## Qwen applicability boundary

A Qwen generation request fails closed when the recomputed production mode is not `hybrid` or `generative_scene`.

This means, for example:

- low-confidence stories that the editorial engine demotes to `verified_asset_editorial` cannot silently enter the Qwen canonical generation path;
- data/table/tactics-style stories that require deterministic composition cannot be routed through Qwen simply because a generation request flag was set.

## Exact-content boundary

The proposed generated-elements list must exactly equal the list emitted by the project-native editorial engine. The proposed forbidden-generated-elements list must also match exactly.

This prevents a downstream request from adding scores, statistics, logos, headline text, or other exact content to the model-owned semantic scope.

## Policy source drift binding

In addition to evidence SHA-256 and byte size, the semantic verification details bind the actual `story_visual_editorial.py` source bytes by SHA-256 and byte size. A later change to the project-native editorial policy therefore invalidates an older semantic replay receipt even if the external evidence file itself is unchanged.

## Production adapter

`engine/intelligence/qwen_image_story_semantic_preflight_gate_verifier.py` exposes the Change Set 238 three-argument replay signature and Change Set 241 production provenance metadata.

The source callable object points directly to `verify_story_semantic_preflight_evidence` in the production policy module.

## Regression coverage

`tests/test_phase18_qwen_image_story_semantic_preflight_gate_verifier.py` covers:

- a canonical football result mapping to Score Monument + hybrid production;
- source evidence SHA/size binding;
- editorial-policy source SHA/size binding;
- low-confidence demotion away from Qwen generation;
- deterministic table stories being rejected from the Qwen generation path;
- visual-family drift;
- scene-concept drift;
- attempts to add an exact score to generated elements;
- attempts to remove club crests from the forbidden-generated contract;
- cross-story evidence reuse;
- verifier identity drift;
- non-Boolean Qwen request flags;
- a false Qwen request being unable to pass Qwen generation preflight;
- production source-object provenance.

Tests use standard-library `unittest` and introduce no dependency.

## Six-gate status

With Change Set 249 code present, genuine production-backed adapters exist for all six required gate IDs:

1. `fact_lock`
2. `entity_identity_verification`
3. `sentiment_neutrality`
4. `story_semantic_preflight`
5. `zero_cost_policy`
6. `semantic_layer_ownership`

The canonical registry must still remain fail-closed until the new adapter's CI is observed green and the atomic cutover is made deliberately in the required gate order.

## Authority remains closed

Change Set 249 by itself does not make any of the following true:

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

## GPU status

No CUDA or Qwen inference occurs here. The first genuine Golden PNG still requires a compatible zero-cost local CUDA/BF16 runtime with sufficient VRAM/RAM, the exact pinned Qwen-Image-2512 revision, compatible Diffusers/QwenImagePipeline, successful sequential CPU offload and canonical local-only execution.
