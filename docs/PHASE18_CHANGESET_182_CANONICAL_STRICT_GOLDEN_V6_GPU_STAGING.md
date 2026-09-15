# Phase 18 Change Set 182 — Canonical Strict Golden v6 GPU Staging

## Purpose

Close the remaining execution-source and workflow gap between the current story-first Golden Editorial v6 contract and the first genuine Candidate 1 GPU run.

The prior strict v6 staging entrypoint correctly refused Engineering Proof fallback, but it delegated to `phase18_colab_one_command.py`, which always performed `git pull --ff-only` before GPU work. That behavior is useful for interactive Colab, but it is incompatible with an immutable GitHub workflow dispatch because the source tree could move after the workflow had already admitted a specific commit SHA.

At the same time, the existing host-memory first-Golden workflow still represented the older sealed Hybrid review path rather than the current Golden Editorial v6 story-first staging contract.

## Changes

### 1. Immutable-source mode for the v6 one-command flow

`tools/phase18_colab_one_command.py`

- Added `--skip-update`.
- Default interactive behavior is unchanged: the command still performs `git pull --ff-only origin phase18/story-intelligence` unless the flag is supplied.
- `--skip-update` is intended only for callers that already pinned and reattached the exact Phase 18 dispatch SHA.
- No semantic, factual, identity, zero-cost, or publication gate was relaxed.

### 2. Strict genuine-Golden staging now preserves the admitted commit

`tools/phase18_colab_first_genuine_golden.py`

- Always delegates with `--strict-semantic` and `--skip-update`.
- Engineering Proof fallback remains impossible in this path.
- Candidate remains locked to Candidate 1.
- BF16, `$0-local`, pinned FLUX provenance, pinned Qwen verifier identity, composition-map lock, semantic approval, and layer-ownership approval remain mandatory.
- Human review, Golden scoring, exact brand/typography, and publication remain downstream.

### 3. Resource-locked strict v6 staging wrapper

Added `tools/phase18_colab_first_genuine_resources_locked.py`.

Before strict Candidate 1 staging it now proves:

- live CUDA GPU eligibility;
- native BF16 support;
- current live-free VRAM at or above the model floor;
- `$0-local` cost mode;
- live host-memory readiness.

It then runs the strict genuine-Golden v6 entrypoint and SHA-binds:

- GPU-host qualification receipt;
- host-memory preflight receipt;
- strict Golden v6 staging receipt;
- the exact resulting PNG.

The output contract is:

`pul7sar-first-genuine-golden-v6-resource-lock-v1`

with status:

`FIRST_GENUINE_GOLDEN_V6_RESOURCE_LOCK_VERIFIED`

The wrapper cannot authorize human acceptance, Golden quality, publication, or Seeds 2-4.

### 4. Canonical self-hosted GPU workflow for Golden Editorial v6

Added `.github/workflows/phase18-first-genuine-golden-v6.yml`.

The workflow is:

- manual only;
- self-hosted only;
- CUDA/BF16-labelled only;
- `$0-local` only;
- pinned to the immutable dispatch SHA;
- reattached locally to `phase18/story-intelligence` at the same SHA;
- complete-ancestry aware;
- fail-closed if `main.py` differs from the merge-base.

It runs the resource-locked strict v6 staging wrapper, replays all evidence SHA-256 values, rechecks the exact PNG signature/SHA, and keeps all downstream authority gates closed.

### 5. Regression coverage

Added `tests/test_phase18_first_genuine_golden_v6_workflow.py` to lock:

- `--skip-update` use in strict staging;
- preservation of default interactive update behavior;
- GPU qualification before host-memory qualification before strict generation;
- manual/self-hosted/immutable workflow behavior;
- absence of paid-provider or automatic PyTorch replacement paths;
- evidence replay before artifact upload;
- continued closure of Golden/publication/Seeds 2-4 authority.

## Files

### Added

- `tools/phase18_colab_first_genuine_resources_locked.py`
- `.github/workflows/phase18-first-genuine-golden-v6.yml`
- `tests/test_phase18_first_genuine_golden_v6_workflow.py`
- `docs/PHASE18_CHANGESET_182_CANONICAL_STRICT_GOLDEN_V6_GPU_STAGING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_182.md`

### Modified

- `tools/phase18_colab_one_command.py`
- `tools/phase18_colab_first_genuine_golden.py`

### Deleted

- None.

## Gates preserved

No changes were made to:

- Fact Lock;
- Entity / Identity Verification;
- Sentiment / Neutrality policy;
- `$0-local` policy;
- pinned FLUX revision;
- pinned Qwen revision / verifier identity;
- native BF16 requirement;
- GPU VRAM / live-free VRAM gates;
- host-memory gate;
- Candidate/request/seed/canvas/SHA locks;
- generated text / branding / exact facts / entity marks / exact sport-geometry prohibitions;
- Qwen BASE_SCENE semantic and layer-ownership gates;
- Golden 8.5 minimum / 9.0+ elite target;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate.

## Genuine PNG status

No new Golden Editorial v6 PNG is claimed by this change set. A genuine result still requires an actually available self-hosted host proving NVIDIA CUDA, native BF16, sufficient live VRAM, sufficient live system RAM, safe local Diffusers execution, pinned FLUX/Qwen revisions, and `$0-local` execution.

This change materially reduces the remaining gap by ensuring that the next compatible GPU run executes the current strict v6 path from an immutable source commit and produces a resource/SHA-bound Candidate 1 artifact rather than using the older Hybrid review workflow or allowing a late branch update.
