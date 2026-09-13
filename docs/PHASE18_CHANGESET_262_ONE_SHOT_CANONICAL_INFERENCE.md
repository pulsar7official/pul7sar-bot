# Phase 18 — Change Set 262: One-Shot Canonical Inference Boundary

## Purpose

Change Set 262 closes the software boundary immediately after Change Set 261 generation authorization without pretending that a compatible CUDA host is present. It prepares one genuine Qwen Image 2512 canonical inference attempt while preserving every downstream semantic, visual-quality, brand, human-review, and publication gate.

A successful CS262 inference produces a **canonical candidate PNG**, not a Golden Visual. Golden status remains impossible until the existing post-generation gates pass.

## Canonical execution boundary

`engine/intelligence/qwen_image_one_shot_canonical_inference.py`:

- revalidates the exact CS261 story-bound generation authorization immediately before execution;
- requires the exact pinned `Qwen/Qwen-Image-2512` revision and `$0-local` cost mode;
- requires the observed runtime fingerprint to match the runtime fingerprint authorized by CS261;
- restricts inference to the already measured runtime envelope: at most 1024×1024, at most 8 inference steps, and guidance scale 1.0;
- SHA-256 binds prompt bytes, negative-prompt bytes, seed, dimensions, step count, guidance, authorization bytes, runtime fingerprint, and final PNG bytes;
- consumes the CS261 authorization **before** the inference callback using an exclusive `O_EXCL` claim file;
- permanently burns that authorization if inference fails or the returned image fails PNG validation;
- publishes `canonical_candidate.png` only when returned bytes contain a valid PNG signature/IHDR and exact requested dimensions;
- emits a byte-bound success receipt while keeping all Golden/publication authorities false;
- independently revalidates the success receipt, authorization bytes, consumption-claim bytes, PNG bytes, dimensions, same-story identity, same-runtime identity, model revision, and downstream authority state.

There is intentionally no retry loop. A second visual attempt requires a new explicit upstream authorization rather than silently reusing the first authorization.

## Story-bound canonical prompt

Review during implementation found an additional semantic substitution risk: CS261 binds a story and runtime, but accepting a free-form prompt at the final inference edge could pair a valid story authorization with text describing a different story.

`engine/intelligence/qwen_image_story_bound_canonical_prompt.py` closes that gap. The production prompt is deterministically derived from the exact evidence bytes bound by the CS257 evidence manifest after independent semantic replay. It consumes:

- Fact Lock required facts;
- canonical Entity/Identity names;
- Sentiment Neutrality state;
- Story Semantic Preflight editorial request and proposed visual plan;
- Zero-Cost evidence as part of the replayed six-gate set;
- Semantic Layer Ownership boundaries.

The derived prompt explicitly limits generation to approved generative elements and forbids exact text, score/statistics, logos/crests/wordmarks, competition marks, unverified identities, invented facts/emotions, and other deterministic/verified overlay content. Competitive-result visuals explicitly preserve respectful treatment of the losing side.

The prompt contract is cross-bound to the same story SHA and CS261 authorization digest. Evidence byte drift or a cross-story authorization fails closed.

## Live GPU entry point

`tools/phase18_run_one_shot_canonical_inference.py` is the future live-host entry point. It accepts **no free-form prompt file**. It requires the CS257 run and CS261 authorization, derives the canonical prompt from the replayed evidence, revalidates CS260, checks CUDA/native BF16, loads the exact pinned QwenImagePipeline in bfloat16, enables sequential CPU offload, compares the complete live runtime identity with CS260, and then delegates exactly one `pipeline(...)` call to CS262.

A successful call may set only the inference execution facts (`inference_executed=true`, `genuine_canonical_inference_executed=true`). It must leave:

- `genuine_golden_png_created=false`
- `semantic_approved=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`

## Required downstream path

After a genuine candidate exists, it must still pass the existing byte-bound post-generation sequence:

1. Semantic / Layer QA
2. Visual Critic
3. Human visual review
4. Golden quality threshold (minimum 8.5; elite 9.0)
5. Exact Brand / Typography overlay ownership
6. SemanticPublicationGate

No CS262 artifact bypasses or weakens these requirements.

## Current execution status

No genuine Qwen inference was executed while implementing this change set. The available execution environment does not provide the proven compatible CUDA/BF16 host required by CS259/CS260. Therefore no genuine candidate PNG and no Golden Visual PNG are claimed by this change set.
