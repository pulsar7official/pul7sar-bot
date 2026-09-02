# Phase 18 Change Set 312 — GPU Preflight Schema Alignment

## Scope

Change Set 312 removes a fail-closed contract drift in the dedicated first-Golden GPU workflow without weakening any factual, identity, sentiment, zero-cost, semantic-publication, visual-quality, human-review, brand, or publication gate.

## Proven gap

`tools/phase18_preflight_semantic_gpu.py` emits:

`pul7sar-phase18-semantic-gpu-preflight-v2`

and `tools/phase18_first_png.py` requires that same v2 contract. The dedicated `.github/workflows/phase18-gpu-smoke.yml` was still checking for the retired v1 schema. Therefore an otherwise compatible self-hosted CUDA/BF16 machine could complete semantic preflight successfully and still be stopped before FLUX generation by workflow-only schema drift.

## Changes

- Align `.github/workflows/phase18-gpu-smoke.yml` with the authoritative v2 semantic GPU preflight contract.
- Add a regression that requires the producer, first-PNG orchestrator, and GPU workflow to agree on v2 and rejects reintroduction of v1 in the workflow.
- Reassert in regression coverage that the workflow remains self-hosted CUDA/BF16, `$0-local`, and unable to self-authorize generation side effects or publication through semantic preflight.

## Authority boundaries preserved

This change does not create a PNG, authorize a queue mutation, authorize publication, change any model-quality threshold, change factual or entity evidence, relax sentiment neutrality or loser respect, bypass semantic QA, bypass Human Visual Review, or change SemanticPublicationGate authority. It only makes the existing GPU execution surface consume the contract already emitted and required elsewhere.

## Runtime boundary

A genuine first Golden PNG still requires an actually available compatible self-hosted CUDA/BF16 machine with the approved local model/runtime chain. CPU-only execution must continue to fail before generation rather than fabricate an image.
