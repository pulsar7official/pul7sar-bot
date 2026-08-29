# Phase 18 Change Set 258 — Story-Bound Controlled Trial Request

## Purpose

Change Set 258 closes the CPU-side gap between a successful Change Set 257 fresh-story semantic replay and the existing Change Set 233 controlled Golden-trial preflight contract for `Qwen/Qwen-Image-2512`.

The new layer binds the exact CS257 story snapshot, semantic replay bytes, and CS233 preflight-contract bytes into one deterministic request artifact. It is deliberately **not** a generation gate.

## Guarantees

The builder fails closed unless all of the following are true:

- the source CS257 run is inside the repository and is not a symlink;
- the CS257 run receipt has the canonical schema;
- `production_semantic_replay_executed=true`;
- `fresh_story_gates_passed=true`;
- all CS257 downstream generation/Golden/publication authorities remain false;
- the four CS257 artifacts are present in canonical order and still match their recorded SHA-256 and byte sizes;
- the semantic replay belongs to the same story snapshot, has `fresh_story_gates_passed=true`, and confirms all gate-specific verifiers executed;
- the CS233 preflight contract remains byte-valid, digest-valid, `$0-local`, locked, requires live same-host recheck, preserves the six required fresh-story gates, pixel boundaries, post-generation gates, and Golden thresholds 8.5 / 9.0;
- every authority field that CS233 requires to remain false is still false.

## Output authority

A successful CS258 request may carry:

- `production_semantic_replay_executed=true`
- `fresh_story_gates_passed=true`
- `live_same_host_recheck_required=true`

It must keep all of the following false:

- `live_host_recheck_passed`
- `controlled_trial_preflight_valid`
- `canonical_generation_authorized`
- `model_weights_loaded`
- `inference_executed`
- `genuine_canonical_inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

Therefore CS258 cannot create, approve, reuse, or publish pixels.

## Files

- `engine/intelligence/qwen_image_story_bound_controlled_trial_request.py`
- `tests/test_phase18_qwen_image_story_bound_controlled_trial_request.py`
- `tools/phase18_build_story_bound_controlled_trial_request.py`
- `docs/PHASE18_IMPLEMENTATION_LOG_258.md`

## Remaining path

The next runtime boundary is a genuine live same-host recheck against the exact locked Qwen-Image-2512 runtime contract. Only after that future gate passes may a later layer consider `controlled_trial_preflight_valid=true`; canonical generation authorization must remain a separate explicit authority.
