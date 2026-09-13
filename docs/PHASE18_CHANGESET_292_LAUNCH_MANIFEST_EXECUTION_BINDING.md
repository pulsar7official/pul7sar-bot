# Phase 18 Change Set 292 — Launch Manifest Execution Binding

## Objective

Change Set 292 closes the remaining bypass between the CS291 GPU Host Launch Manifest and the actual one-shot Qwen-Image production inference edge.

CS291 could build and verify a complete pre-inference manifest, but the production inference CLI could still be invoked directly without presenting that manifest. CS292 makes the launch manifest mandatory and fail-closed at the concrete execution edge.

## Production-edge rule

`tools/phase18_run_one_shot_canonical_inference.py` now requires `--launch-manifest`.

Before prompt extraction, model import/load, authorization consumption, or inference, the CLI calls:

`verify_gpu_host_launch_manifest_for_execution(...)`

The verifier first fully replays the CS291 manifest and then proves that the actual invocation is exactly the attested invocation.

The following must match the manifest:

- repository-relative generation-authorization path;
- repository-relative CS257 evidence directory;
- resolved immutable local Qwen snapshot path;
- approved snapshot revision;
- width;
- height;
- seed;
- inference steps;
- guidance scale.

Any drift fails closed. There is no fallback to an unattested invocation.

## Execution-contract byte binding

The launch manifest now byte-binds nine execution-contract sources:

- `engine/intelligence/approved_model_revisions.py`
- `engine/intelligence/qwen_image_gpu_readiness.py`
- `engine/intelligence/qwen_image_gpu_host_launch_manifest.py`
- `engine/intelligence/qwen_image_local_inference_runtime.py`
- `engine/intelligence/qwen_image_one_shot_canonical_inference.py`
- `engine/intelligence/qwen_image_local_inference_provenance.py`
- `engine/intelligence/qwen_image_story_bound_canonical_prompt.py`
- `engine/intelligence/qwen_image_story_bound_generation_authorization.py`
- `tools/phase18_run_one_shot_canonical_inference.py`

This means a manifest becomes invalid if the code that defines the launch verifier, story-bound prompt, authorization replay, local runtime, inference execution, or provenance changes after the manifest was created.

## Authority boundaries

CS292 grants no new visual or publication authority.

A valid launch manifest still records:

- `model_load_attempted = false`
- `inference_executed = false`
- `genuine_canonical_inference_executed = false`
- `semantic_approved = false`
- `human_visual_review_approved = false`
- `golden_quality_approved = false`
- `genuine_golden_png_created = false`
- `publication_ready = false`

The inference CLI may proceed only after the pre-launch contract is verified. A successful future inference remains only a canonical candidate and must pass the existing factual, identity, sentiment, semantic, composition, visual-quality, human-review, brand, typography, semantic-publication, Genuine-Golden, and publication-readiness gates.

## Zero-cost and model constraints

No zero-cost constraint was relaxed. The launch manifest continues to require:

- `$0-local` cost mode;
- `network_allowed = false`;
- `local_files_only = true`;
- native BF16;
- sequential CPU offload;
- `Qwen/Qwen-Image-2512`;
- approved immutable revision `2ce1c28560fbc62c9f5531e076b237d3575330a9`.

No download, paid API, network fallback, free-form prompt, retry loop, semantic override, Golden override, or publication override was added.

## Regression coverage

CS292 adds regression coverage proving that:

- an invocation identical to the launch manifest is accepted by the execution-binding verifier;
- seed/settings drift is rejected before model load;
- generation-authorization path drift is rejected;
- the expanded nine-source execution contract is byte-bound;
- all prior CS291 cross-story, measured-envelope, evidence-drift, and manifest-tampering protections remain active.

The regression suite is CPU/synthetic control-plane coverage only. It does not claim a Qwen model load, CUDA inference, production candidate PNG, or Genuine Golden PNG.

## Remaining external blocker

A genuine production run still requires a compatible zero-cost NVIDIA CUDA host with CUDA-enabled PyTorch, native BF16, a compatible `QwenImagePipeline`, sequential CPU offload support, the exact already-local approved snapshot, and sufficient real VRAM/system RAM demonstrated by actual model load and inference.
