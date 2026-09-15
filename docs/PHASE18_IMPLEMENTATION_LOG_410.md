# Phase 18 Implementation Log 410 — FLUX Cache-Proof Local-Only Hard Lock

## Scope

Branch: `phase18/story-intelligence` only. `main` was inspected read-only and was not modified.

This change set closes the remaining network-fallback gap in the FLUX.2 cache-proof path while preserving all factual, identity, sentiment, zero-cost, semantic-publication, visual-quality, provenance, and downstream authority gates.

## Starting state

- Phase branch starting HEAD: `8c28b14c969cbe31f09278c056b74e29b5b80acd`.
- CS409's `Phase 18 Story Intelligence Verification` run `34612820566` completed successfully on that exact SHA.
- The concrete FLUX.2 Diffusers loader was already hard-locked to the approved immutable revision with `local_files_only=True`.
- The Golden v6 workflow was already configured with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `$0-local`, exact approved model revisions, and downstream Human Review / Golden Quality / publication / Seeds 2–4 fail-closed gates.
- However, `tools/phase18_prefetch_flux2.py` still performed a local-only lookup first and, if the approved snapshot was absent, made a second `snapshot_download(...)` call without `local_files_only=True`. That meant the cache-proof tool itself was not independently fail-closed against network model resolution if invoked outside the protected workflow environment or under environment drift.

## Modified

### `tools/phase18_prefetch_flux2.py`

Converted the FLUX.2 model-cache step from a conditional prefetch/downloader into a strict local-cache proof:

- replaced the permissive `_cached_snapshot(...) -> str | None` helper with `_require_cached_snapshot(...) -> str`;
- the helper performs exactly one `snapshot_download(...)` resolution using the approved model ID, exact immutable approved revision, and `local_files_only=True`;
- missing local snapshot now fails immediately with `FLUX2_APPROVED_LOCAL_SNAPSHOT_REQUIRED`;
- removed the second direct network-capable `snapshot_download(...)` fallback from `main()`;
- retained exact immutable revision verification through `assert_snapshot_revision(...)`;
- retained the cached snapshot directory and `model_index.json` integrity checks;
- retained model-cache policy and post-resolution working-headroom checks;
- retained receipt schema `pul7sar-phase18-model-cache-v2` for compatibility with existing Golden v6 replay logic;
- made the zero-cost/offline receipt contract explicit with:
  - `downloaded_now = false`;
  - `network_download_authorized = false`;
  - `local_files_only = true`;
  - `cost_mode = "$0-local"`.

No model ID, approved revision, model license record, generation parameter, prompt, image composition logic, or dependency was changed.

### `tests/test_phase18_flux2_local_cache_only.py`

Extended the existing CS407 concrete-loader regression suite so it now protects both FLUX local-only boundaries:

- concrete Diffusers pipeline loading remains pinned to the approved revision and `local_files_only=True`;
- BF16 dtype and sequential CPU offload behavior remain covered;
- unapproved revisions remain rejected before the loader is called;
- the cache-proof helper must use the approved model ID and revision with `local_files_only=True`;
- a missing cache snapshot must fail after exactly one local-only resolution attempt with `FLUX2_APPROVED_LOCAL_SNAPSHOT_REQUIRED`;
- AST inspection requires zero direct `snapshot_download(...)` calls in cache-proof `main()` and exactly one guarded `_require_cached_snapshot(...)` call;
- source-contract regression checks require the explicit `downloaded_now=false`, `network_download_authorized=false`, and `local_files_only=true` receipt fields and reject restoration of the previous dynamic `downloaded_now` behavior.

## Added

- `docs/PHASE18_IMPLEMENTATION_LOG_410.md` (this log).

## Deleted

- No files deleted.
- Removed only the network-capable FLUX snapshot download fallback from the existing cache-proof tool.
- No factual, identity, sentiment, semantic-publication, visual-quality, provenance, Human Review, Golden Quality, publication, or Seeds 2–4 gate was removed or weakened.

## Commits

- `15945264d561ee2cebb3691efbc2239ce87d54e3` — hard-lock FLUX cache proof to the approved local snapshot.
- `2654dae9c1e322fbe053a8b3f7f470880d2413a0` — extend FLUX local-only regression coverage.

## Test / CI evidence

GitHub Actions started automatically for the exact functional SHA `2654dae9c1e322fbe053a8b3f7f470880d2413a0`.

At the time this implementation log was written:

- `Phase 18 Story Intelligence Verification` run `34630117595` / run number `5518` was `in_progress` on exact head SHA `2654dae9c1e322fbe053a8b3f7f470880d2413a0`;
- therefore CS410 is not described as terminal-green yet;
- no test success is fabricated or inferred before GitHub reports a terminal conclusion.

The next verification pass must confirm that the historical tests do not depend on the removed network-download behavior. Any such stale assertion must be repaired only if it tests obsolete source shape rather than a real safety requirement.

## Zero-cost and gate posture

Unchanged and fail-closed:

- Qwen2.5-VL exact approved immutable revision remains required and local-cache-only;
- FLUX.2 exact approved immutable revision remains required and is now local-cache-only at both cache-proof and concrete-loader boundaries;
- cost mode remains `$0-local`;
- factual, entity/identity, sentiment, semantic-publication, and visual-quality gates remain intact;
- provenance/source-binding/transport-attestation contracts remain intact;
- `human_visual_review_approved = false`;
- `golden_quality_approved = false`;
- `publication_ready = false`;
- `seeds_2_to_4_authorized = false`.

## Genuine Golden PNG status

No Genuine Golden Visual PNG was generated or claimed in CS410.

The non-substitutable execution blocker remains a compatible self-hosted NVIDIA runner satisfying the Golden v6 labels and runtime contract: CUDA-enabled PyTorch, native BF16, sufficient VRAM/RAM/storage, and the exact approved pinned Qwen2.5-VL and FLUX.2 snapshots already present in the local Hugging Face cache.

This change materially reduces the remaining gap because both model cache-proof paths and the concrete FLUX loader now fail closed rather than attempting network model acquisition when the approved local model state is incomplete.
