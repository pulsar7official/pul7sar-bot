# Phase 18 Change Set 298 — Mandatory Preload Launch Gate

## Purpose

CS297 introduced an aggregate, non-inference preload host diagnostic, but the manifest-bound production launcher could still invoke the canonical inference subprocess without first requiring that diagnostic to pass. CS296 would still fail closed before Qwen model loading, but the aggregate diagnostic remained optional at the launcher edge.

CS298 closes that operational gap. The manifest-bound launcher now requires the CS297 diagnostic to report `ready_for_model_load_attempt=true` with an empty blocker list before it starts the canonical subprocess.

## Production behavior

`engine/intelligence/qwen_image_manifest_bound_execution.py` now imports and replays `inspect_preload_host(...)` after building the manifest-derived, shell-free canonical argv and before `subprocess.run(...)`.

If any blocker remains, `QwenPreloadHostNotReadyError` is raised with a normalized, deduplicated blocker tuple. The canonical subprocess is not started.

A diagnostic is accepted only when all of the following remain explicitly false:

- `model_load_attempted`
- `inference_executed`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

This prevents the non-authoritative diagnostic layer from being treated as downstream approval evidence.

## Preserved gates

CS298 does not alter or bypass:

- factual/freshness locks;
- entity and identity verification;
- sentiment neutrality and loser-respect rules;
- story-bound prompt and authorization evidence;
- `$0-local` execution policy;
- exact local Qwen snapshot and pinned revision policy;
- CS260 runtime identity requirements;
- CS287/CS296 static and exact pre-model-load enforcement;
- semantic approval;
- generated-layer/composition QA;
- visual-quality and Golden adjudication;
- human visual review;
- exact brand/typography requirements;
- `SemanticPublicationGate`;
- Genuine Golden materialization or publication readiness.

## Tests

`tests/test_phase18_qwen_image_manifest_bound_execution.py` now covers:

- normalized multi-blocker propagation;
- rejection of premature authority in a preload diagnostic;
- proof that `subprocess.run` is not called when preload blockers remain;
- proof that shell-free canonical execution still occurs only after a ready diagnostic;
- existing `$0-local`, manifest-derived settings, and repository-local output requirements.

The tests are control-plane/unit tests. They do not constitute Qwen model loading, CUDA inference, or a Genuine Golden PNG.

## Remaining execution blocker

A real Golden candidate still requires a compatible zero-cost host providing NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, compatible Diffusers/QwenImagePipeline, sequential CPU offload, the exact approved local Qwen snapshot, the CS260-authorized runtime identity, and sufficient RAM/VRAM demonstrated by genuine model load and inference.
