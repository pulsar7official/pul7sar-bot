# Phase 18 Change Set 188 — Post-Cache Headroom Binding

## Goal

Bind the post-download FLUX cache headroom proof introduced in Change Set 187 into the canonical first genuine Golden Editorial v6 resource lock, so Candidate 1 cannot proceed merely because the pre-download cache budget was sufficient.

## Problem closed

`phase18_prefetch_flux2.py` already re-measures the live Hugging Face cache filesystem after the exact pinned FLUX.2 Klein 4B snapshot exists and fails below the conservative working-space floor. However, `phase18_colab_first_genuine_resources_locked.py` only validated the FLUX cache schema, model identity, revision, cost mode and canonical snapshot path. It did not explicitly require or bind `working_headroom_ready` and the nested post-cache decision before Runtime Fingerprint and Candidate 1.

This left the post-cache disk proof enforced by the prefetch process but not promoted into the canonical resource-lock contract.

## Changes

- Strengthened `_validate_flux_cache()` in `tools/phase18_colab_first_genuine_resources_locked.py`.
- The first-Golden resource lock now requires:
  - `working_headroom_ready == true`;
  - `working_headroom_after_cache` to exist;
  - `eligible == true`;
  - reason `post_cache_working_headroom_ready`;
  - numeric positive `free_gib` and `minimum_working_free_gib`;
  - non-negative integer `free_bytes`;
  - `free_gib >= minimum_working_free_gib`.
- The validated live post-cache values are bound into the final resource-lock receipt as:
  - `post_cache_working_headroom_bound`;
  - `post_cache_free_gib`;
  - `post_cache_required_gib`.
- The existing FLUX model-cache receipt remains SHA-256-bound in the resource-lock evidence map, so the exact receipt that passed the headroom check is the one carried forward.
- Added regression coverage that accepts valid headroom and rejects missing readiness and below-floor evidence.

## Gates preserved

No factual, identity, sentiment/neutrality, zero-cost, model-revision, BF16, GPU/VRAM/RAM, semantic-publication, brand, typography or Golden visual-quality gate was weakened. No new provider or paid path was introduced. Seeds 2–4 remain unauthorized.

## GPU status

No genuine Golden Editorial v6 PNG was produced by this change set. A compatible self-hosted NVIDIA CUDA host with native BF16, sufficient live VRAM/RAM, safe local Diffusers execution, exact pinned FLUX/Qwen snapshots and `$0-local` execution is still required.
