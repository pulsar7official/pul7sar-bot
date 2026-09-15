# Phase 18 Implementation Log 432 — Offload Blocker Probe and Offline/BF16 Parity

## Scope

Branch: `phase18/story-intelligence` only. `main` was read-only and was not modified, merged, rebased, reset, or ref-updated.

This change set closes a pre-execution parity gap in the First Genuine Golden v6 offload fallback. Before CS432, the canonical and JIT paths asserted Hugging Face/Transformers offline mode and recorded the shared first-Golden execution blocker probe before CUDA preflight, while the offload workflow did neither and only checked `torch.cuda.is_available()`.

## Modified

- `.github/workflows/phase18-first-genuine-golden-v6-offload.yml`
  - Added `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` at job scope.
  - Added the shared non-authoritative first-Golden blocker probe before the offload CUDA preflight.
  - Persisted its receipt under `output/phase18_gpu_smoke/`, already covered by the workflow's `if: always()` artifact upload.
  - Strengthened CUDA preflight to fail closed on cost-mode drift, offline-mode drift, missing CUDA runtime, missing CUDA device, or lack of native BF16 support.
  - Explicitly rejects FP16/FP32 substitution.
  - Preserved immutable branch isolation, offload provenance replay, factual/identity/sentiment/semantic/visual gates, and all downstream authority closures.

## Added

- `tests/test_phase18_first_genuine_golden_v6_offload_blocker_probe_integration.py`
  - Protects probe-before-CUDA ordering.
  - Protects `$0-local`, HF/Transformers offline-only execution, CUDA runtime/device checks, native BF16, and no FP16/FP32 substitution.
  - Protects always-uploaded blocker evidence and `main` isolation.
  - Protects Human Visual Review, Golden Quality, publication, and Seeds 2–4 authority closures.

- `docs/PHASE18_IMPLEMENTATION_LOG_432.md`
  - This implementation record.

## Deleted

None.

## Deliberately unchanged

- Prompts, seeds, generation parameters, approved Qwen/FLUX model IDs and immutable revisions.
- Factual, entity/identity, neutral-sentiment, semantic-publication, and visual-quality gates.
- Human review remains mandatory after a real PNG exists.
- `human_visual_review_approved=false`, `golden_quality_approved=false`, `publication_ready=false`, and `seeds_2_to_4_authorized=false` remain the required pre-review state.
- Network model downloads remain unauthorized.

## Testing intent

The repository-wide Phase 18 `unittest` discovery is expected to include the new regression suite. The exact-head GitHub Actions verification result must be observed before CS432 can be called terminal-green.

## Remaining blocker

No genuine Golden Visual PNG is claimed by this change set. Candidate 1 still requires a real self-hosted NVIDIA execution host with CUDA-enabled PyTorch, at least one CUDA device, native BF16, sufficient live free VRAM/system RAM/local storage, and the exact approved Qwen2.5-VL and FLUX.2 snapshots locally resolvable with network model downloads disabled. The shared blocker receipt now executes before the offload fallback's CUDA work, so an unsuitable host should fail with preserved diagnostic evidence instead of an ambiguous early failure.
