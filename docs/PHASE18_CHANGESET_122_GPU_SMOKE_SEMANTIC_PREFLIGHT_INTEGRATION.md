# PUL7SAR Phase 18 — Change Set 122

## GPU Smoke Semantic Preflight Integration

This change advances `phase18/story-intelligence` only. `main` remains untouched.

## Problem

Change Set 121 introduced a standalone fail-closed semantic GPU preflight, but the self-hosted Golden GPU smoke workflow could still reach FLUX model preparation and Candidate 1 generation without first proving that the exact Qwen runtime and approved local Qwen snapshot were ready on the same CUDA host.

That gap could waste a scarce compatible GPU window: FLUX could generate a valid base scene and only afterwards reveal that semantic inspection was unavailable.

## Changes

### `.github/workflows/phase18-gpu-smoke.yml`

The manual self-hosted GPU smoke now runs:

1. explicit execution confirmation;
2. protected Phase 18 checkout/isolation;
3. CUDA-enabled PyTorch proof;
4. Phase 18 GPU dependency installation;
5. **semantic GPU preflight** using `tools/phase18_preflight_semantic_gpu.py`;
6. exact FLUX.2 Klein cache/prefetch;
7. FLUX/BF16 readiness;
8. locked Candidate 1 generation;
9. PNG and publication-gate verification;
10. tamper-evident evidence build/replay;
11. artifact upload.

The semantic preflight is validated in-workflow for:

- schema `pul7sar-phase18-semantic-gpu-preflight-v1`;
- branch `phase18/story-intelligence`;
- exact model `Qwen/Qwen2.5-VL-3B-Instruct`;
- `$0-local` cost mode;
- semantic runtime ready;
- semantic model ready;
- CUDA available;
- `generation_authorized=false`;
- `queue_mutated=false`;
- `png_created=false`;
- `publication_ready=false`.

The preflight runs before FLUX model preparation and before any Candidate generation.

The final GPU evidence manifest now also includes:

- `semantic-preflight.json`;
- `qwen-model-cache.json`;
- existing FLUX model-cache/readiness/host qualification evidence.

This binds the semantic-side readiness proof into the same replayable evidence package as the genuine PNG generation.

### `tests/test_phase18_gpu_smoke_workflow.py`

Regression coverage now proves:

- semantic preflight is present in the self-hosted workflow;
- it executes before FLUX prefetch/readiness/generation;
- the exact Qwen model and fail-closed gate fields are checked;
- Qwen preflight/cache receipts are included in the final tamper-evident evidence manifest;
- `$0-local`, explicit self-hosted CUDA/BF16 labels, and no-provider-secret rules remain enforced.

## Deleted

Nothing.

## Preserved invariants

No changes were made to:

- `main` / `main.py`;
- Fact Lock, source/state integrity, or source consensus;
- identity verification;
- sentiment and result neutrality;
- FLUX.2 Klein 4B model selection;
- BF16 requirement;
- seed/canvas locks;
- generated text/brand/score/crest/exact-geometry exclusions;
- Qwen semantic publication requirements;
- SemanticPublicationGate;
- Golden visual thresholds (`8.5` minimum / `9.0+` elite);
- exact brand/typography integrity;
- `$0-local` policy.

No Fake PNG, paid API, hosted GPU fallback, provider substitution, or publication bypass was introduced.

## Result

The self-hosted GPU path can no longer reach FLUX Candidate 1 unless the semantic inspection runtime and exact Qwen model are already proven ready on that host. This reduces the remaining operational gap to the first genuine Golden Hybrid v5 PNG without weakening any factual, identity, semantic, or visual-quality gate.
