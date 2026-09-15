# Phase 18 Implementation Log — CS407

Date: 2026-09-11
Branch: `phase18/story-intelligence` only
Starting HEAD: `32b8acb588fcac6ccf715c0ac072ea44e42c624a`

## Goal

Reduce a real execution-time gap before the first Genuine Golden Visual PNG by making FLUX.2 pipeline construction independently fail closed against network/model-download fallback. Preserve the existing factual, identity, sentiment, zero-cost, semantic-publication, visual-quality, Human Review, Golden Quality, publication, and Seeds 2–4 authority gates.

## Review before changes

- CS406 (`32b8acb588fcac6ccf715c0ac072ea44e42c624a`) was reviewed first.
- Phase 18 Story Intelligence Verification run `34596252738` for CS406 completed successfully.
- `main` was inspected read-only and was not modified.
- The Golden v6 workflow already sets `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`, and preflights pinned local model-cache evidence.
- The concrete FLUX.2 factory pinned `FLUX2_KLEIN_4B_REVISION`, but its `from_pretrained` call did not independently pass `local_files_only=True`. Therefore a direct invocation outside that workflow, or future environment drift, could permit Hugging Face resolution to attempt network access instead of failing immediately on a missing approved snapshot.

## Added

### `tests/test_phase18_flux2_local_cache_only.py`

Regression coverage proving that:

1. The approved FLUX.2 model ID is loaded at the immutable approved revision.
2. Pipeline loading receives `local_files_only=True` explicitly.
3. BF16 dtype remains bound to the loader request.
4. Sequential CPU offload behavior remains unchanged.
5. A missing local snapshot propagates as a hard failure with no alternate loader invocation or fallback.
6. An unapproved model revision remains blocked before any loader call.

## Modified

### `engine/intelligence/flux2_klein_diffusers.py`

Changed the concrete pipeline-loader call to include:

```python
local_files_only=True
```

The module/factory documentation now states that real pipeline construction is explicitly local-cache-only and must fail closed if the approved immutable snapshot is absent.

This is intentionally defense-in-depth with the workflow's offline environment and model-cache preflights; it does not replace them.

## Deleted

Nothing.

## Dependency changes

None.

## Gate impact

No authority gate was relaxed or opened.

- Factual/news verification: unchanged.
- Entity/identity verification: unchanged.
- Sentiment and loser-respect policy: unchanged.
- `$0-local`: strengthened at the concrete FLUX loader boundary.
- Approved immutable FLUX revision: unchanged and still mandatory.
- CUDA/native-BF16 requirement: unchanged.
- Qwen semantic inspection: unchanged.
- SemanticPublicationGate/publication authority: unchanged and fail-closed.
- Human visual review: still required and not approved by this change.
- Golden Quality: still false until human review.
- `publication_ready`: remains false.
- Seeds 2–4: remain unauthorized.

## Commits

- `2922322e0b1141854732dda06c747baf32ece79d` — hard-lock FLUX.2 loading to approved local cache only.
- `57064f1884b371bbbd709dc00358cdfc413c81b0` — add regression coverage for the local-cache-only loader boundary.

## Testing

The new tests are CPU-only and use injected fake loader/torch objects; they do not load model weights, perform network access, require CUDA, or create a PNG.

Repository CI was triggered by the commits. CS407 must not be called terminal-green until the Phase 18 Story Intelligence Verification for the final CS407 HEAD completes successfully.

No compatible CUDA/native-BF16 execution was available in this work session, so the first Genuine Golden PNG was not fabricated or claimed.

## Remaining blocker

A real self-hosted NVIDIA runner is still required with all of the following:

- labels matching the Golden v6 workflow (`self-hosted`, `linux`, `x64`, `gpu`, `cuda`, `bf16`, `pul7sar-phase18`),
- CUDA-enabled PyTorch,
- native BF16 support,
- sufficient live VRAM, host RAM, and storage,
- the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in the local cache,
- compatible Diffusers/Transformers runtime.

With CS407, if the FLUX.2 snapshot is not present locally, the actual pipeline factory itself now refuses network fallback even if the surrounding workflow/environment protections are accidentally bypassed.
