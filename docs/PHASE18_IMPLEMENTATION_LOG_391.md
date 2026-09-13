# Phase 18 Implementation Log 391 — Genuine Golden v6 Local-Cache-Only Enforcement

Date: 2026-09-10
Branch: `phase18/story-intelligence`
Starting HEAD: `a37ca53a6e58911c73067c6ce490413f65ccd71e`
Production/workflow change commit: `20eb458eed4b2350ff5cdfaacc24ac3992c7849a`
Scope: harden the existing first-genuine-Golden v6 execution path so `$0-local` cannot silently turn into a network model-fetch during Candidate 1 execution.

## Repository state reviewed first

- `phase18/story-intelligence` was confirmed at `a37ca53a6e58911c73067c6ce490413f65ccd71e` before this changeset.
- `Phase 18 Story Intelligence Verification` run `34516684618` / run number `5402` completed with conclusion `success` on that exact starting SHA.
- `main` was inspected read-only at `86e23081e8373720c287872d03d47185b0c946fe` and was not modified, merged, rebased, reset, or force-updated.

## Proven gap

The canonical execution workflow `.github/workflows/phase18-first-genuine-golden-v6.yml` declares `PUL7SAR_PHASE18_COST_MODE=$0-local`, but the helper programs it invokes can legitimately call Hugging Face `snapshot_download(...)` without `local_files_only=True` if their exact pinned snapshots are absent from the cache.

This was verified in both model paths:

- `tools/phase18_prefetch_qwen.py` first probes with `local_files_only=True`, but if the pinned Qwen snapshot is absent it falls back to a normal `snapshot_download(...)` and records `downloaded_now=true`.
- `tools/phase18_prefetch_flux2.py` has the same pattern for the pinned FLUX.2 snapshot and records `downloaded_now=true` after such a fetch.

That behavior is acceptable for a generic prefetch utility, so those utilities were deliberately not changed. It is not acceptable for the canonical First Genuine Golden v6 execution seam, whose documented execution requirement is approved already-local pinned resources under the `$0-local` contract.

## Change implemented

Modified `.github/workflows/phase18-first-genuine-golden-v6.yml` only.

The job environment now sets:

- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`

The CUDA qualification step also proves both environment variables are exactly `1` before continuing and reports the model-cache mode as `offline-local-only`.

The post-generation evidence replay now additionally requires:

- semantic preflight `model_downloaded_now == false`;
- Qwen cache receipt `downloaded_now == false`;
- FLUX cache receipt `downloaded_now == false`.

Therefore a First Genuine Golden v6 run cannot pass by silently fetching missing model bytes during the execution. The exact approved pinned snapshots must already resolve from the local Hugging Face cache.

## Gate preservation

No factual, freshness, identity, sentiment/loser-respect, semantic-publication, generated-layer, visual-quality, human-review, Golden-quality, or publication authority was opened or weakened.

This changeset does not create a PNG, does not perform inference, does not authorize Seeds 2–4, does not set `golden_quality_approved`, and does not set `publication_ready`.

The change is stricter than the previous workflow because model-network fallback is now explicitly disabled on the canonical v6 execution path.

## Files

### Modified

- `.github/workflows/phase18-first-genuine-golden-v6.yml`

### Added

- `docs/PHASE18_IMPLEMENTATION_LOG_391.md`

### Deleted

- None.

### Dependencies

- None added, removed, or changed.

## Testing / verification

Pre-change evidence:

- Starting SHA `a37ca53a6e58911c73067c6ce490413f65ccd71e` is terminal-green via Phase 18 Story Intelligence Verification run `34516684618` / #5402.
- The existing Qwen and FLUX prefetch implementations were inspected and the network-fallback gap was confirmed from live branch source before modifying the workflow.

Post-change verification is CI-dependent. The workflow-only code SHA is `20eb458eed4b2350ff5cdfaacc24ac3992c7849a`. This log commit follows it. Do not describe CS391 as terminal-green until the Phase 18 verification workflow reports `completed/success` on the applicable exact SHA.

No genuine inference test is claimed because the currently available execution host still lacks compatible NVIDIA CUDA/native-BF16 execution.

## Remaining gap to first genuine Golden PNG

A genuine Candidate 1 still requires a purpose-qualified self-hosted runner labeled `self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18`, CUDA-enabled PyTorch, native BF16, sufficient VRAM/RAM/storage, and now the exact approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in its local Hugging Face cache.

Only a real dispatch of `.github/workflows/phase18-first-genuine-golden-v6.yml` from `phase18/story-intelligence` can produce candidate PNG bytes. Those bytes must still pass all existing semantic/layer/runtime/staging checks and later independent visual/human/Golden/publication gates before any Golden or publication claim is valid.
