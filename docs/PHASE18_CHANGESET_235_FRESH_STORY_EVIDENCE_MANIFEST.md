# Phase 18 — Change Set 235: Fresh Story Evidence Manifest

## Purpose

Change Set 235 closes a byte-substitution gap between the locked controlled Golden-trial preflight contract and future canonical generation authorization.

Change Set 233 already requires fresh evidence for:

1. `fact_lock`
2. `entity_identity_verification`
3. `sentiment_neutrality`
4. `story_semantic_preflight`
5. `zero_cost_policy`
6. `semantic_layer_ownership`

Change Set 235 binds the exact repository-resident bytes supplied for all six requirements. It deliberately does **not** interpret those artifacts as approvals and therefore cannot set `fresh_story_gates_passed=true`.

## Security / evidence properties

The manifest:

- requires the exact Change Set 233 gate set and canonical order;
- requires one distinct non-empty repository-resident file per gate;
- rejects path escape outside the repository and symbolic-link evidence;
- records repository-relative path, byte size, and SHA-256 for every evidence file;
- re-opens every evidence file during replay and compares current bytes to the bound SHA-256 and size;
- binds itself to the locked Change Set 233 preflight-contract digest;
- keeps gate-specific semantic verification, same-story verification, and evidence-freshness verification mandatory for the later authorization layer.

## Authority boundary

A successful Change Set 235 manifest proves only that all required evidence **bytes are bound**. It does not prove that the evidence is correct, fresh, mutually consistent, or approved by its canonical gate verifier.

The following remain false:

- `fresh_story_gates_passed`
- `controlled_trial_preflight_valid`
- `runtime_floor_proven`
- `local_runtime_qualified`
- `canonical_generation_authorized`
- `canonical_pixels_reusable`
- `queue_mutated`
- `model_weights_loaded`
- `inference_executed`
- `genuine_golden_png_created`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

## Files

Added:

- `engine/intelligence/qwen_image_fresh_story_evidence_manifest.py`
- `tools/phase18_build_qwen_fresh_story_evidence_manifest.py`
- `tests/test_phase18_qwen_image_fresh_story_evidence_manifest.py`
- `docs/PHASE18_CHANGESET_235_FRESH_STORY_EVIDENCE_MANIFEST.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_235.md`

No canonical generation, publication, or `main` file is modified by this change set.

## Regression coverage

The canonical `unittest` suite now exercises:

- successful binding without authority;
- missing/reordered required gate evidence;
- byte substitution after binding;
- repository path escape;
- duplicate evidence file reuse across gates;
- forged generation authority even after manifest re-hashing;
- removal of later semantic/freshness verification requirements;
- parent preflight cost-mode tampering.

## Remaining runtime blocker

No genuine Golden PNG is claimed. The current execution environment still lacks an available self-hosted NVIDIA runtime that proves the exact pinned Qwen Image 2512 stack with CUDA, native BF16, sufficient live VRAM/RAM, compatible Diffusers/QwenImagePipeline, sequential CPU offload, and canonical `$0-local` execution.
