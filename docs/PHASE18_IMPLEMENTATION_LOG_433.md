# Phase 18 Implementation Log 433 — First-Golden Cache Working-Headroom Alignment

## Scope

Branch: `phase18/story-intelligence` only. `main` is read-only and must not be modified, merged, rebased, reset, or ref-updated.

CS433 closes a remaining early-diagnostic gap before the first genuine Golden Visual Candidate 1. The shared blocker probe already proved offline-only model resolution, exact immutable Qwen/FLUX snapshots, CUDA/native BF16, live GPU qualification, and available host RAM. However, it only recorded free cache-filesystem space and did not enforce the same post-cache working-headroom floor that the approved FLUX local-cache preflight enforces later.

The repository already defines this authoritative execution floor through `ModelCacheHeadroomPolicy`: at least 8 GiB of live free space must remain after model caching for runtime scratch files, receipts, and artifacts. CS433 reuses that existing policy rather than inventing a new threshold.

## Modified

- `tools/phase18_probe_first_golden_execution_blocker.py`
  - Reuses `ModelCacheHeadroomPolicy` in the non-authoritative shared blocker probe.
  - Adds fail-closed `CACHE_WORKING_HEADROOM_NOT_READY` when the approved post-cache working-space floor is not met.
  - Persists the full `cache_headroom` decision alongside the existing GPU, host-memory, and exact-model-cache evidence.
  - Uses the policy decision as the source for reported live cache-filesystem free GiB.
  - Bumps the diagnostic schema from `pul7sar-phase18-first-golden-execution-blocker-probe-v3` to `...-v4`.
  - Does not download models, load models, generate pixels, mutate queues, or open publication/Seeds authority.

- `tests/test_phase18_first_golden_execution_blocker_probe.py`
  - Makes cache-headroom evidence deterministic in unit tests instead of relying on the CI runner's actual free disk.
  - Extends the all-green fixture to require the approved 8 GiB working-space floor.
  - Adds regression coverage proving that 7 GiB free blocks readiness even when CUDA, native BF16, live VRAM, system RAM, and both exact local snapshots are otherwise ready.
  - Extends the composite blocked-host test to include the filesystem-headroom blocker.
  - Updates expected blocker-probe schema to v4.

## Added

- `docs/PHASE18_IMPLEMENTATION_LOG_433.md`
  - This implementation record.

## Deleted

None.

## Deliberately unchanged

- Prompts, seeds, generation parameters, image composition, and visual-quality thresholds.
- Approved Qwen/FLUX model IDs and immutable revisions.
- Dependencies and provider selection.
- Factual, entity/identity, neutral-sentiment, semantic-publication, and visual-quality gates.
- `$0-local` and local-files-only model resolution.
- Human Visual Review remains mandatory after a real PNG exists.
- `human_visual_review_approved=false`, `golden_quality_approved=false`, `publication_ready=false`, and `seeds_2_to_4_authorized=false` remain the required pre-review state.
- Network model downloads remain unauthorized.

## Why this materially reduces the remaining gap

The canonical resource lock already rejects a FLUX cache receipt when its post-cache working headroom is below the approved 8 GiB floor. Before CS433, that failure could occur only later in the resource/model-cache chain even though the shared blocker probe had reported the filesystem's free space. The shared probe now fails before heavy Golden execution on exactly the same policy, preserving a precise diagnostic receipt and reducing the chance of wasting the first compatible self-hosted GPU opportunity on a predictable local-storage failure.

Because canonical, JIT, and offload workflows all invoke the shared blocker probe before their heavy CUDA path, this single change applies the same early storage diagnostic to all three paths without weakening or duplicating their later authoritative checks.

## Testing

Regression coverage is provided by `tests/test_phase18_first_golden_execution_blocker_probe.py` and remains compatible with the repository's `unittest` discovery contract. Exact-head GitHub Actions verification must complete successfully before CS433 is described as terminal-green.

## Remaining blocker

No genuine Golden Visual PNG is claimed by CS433. Candidate 1 still requires a real self-hosted NVIDIA execution host with CUDA-enabled PyTorch, at least one CUDA device, native BF16, sufficient total/live-free VRAM, sufficient currently available system RAM, at least the approved 8 GiB post-cache working-space floor, and the exact approved Qwen2.5-VL and FLUX.2 immutable snapshots already resolvable locally with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and `PUL7SAR_PHASE18_COST_MODE=$0-local`.
