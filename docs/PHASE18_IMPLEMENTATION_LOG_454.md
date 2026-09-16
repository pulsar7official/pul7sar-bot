# Phase 18 Implementation Log — CS454

## Scope

CS454 adds a deterministic, no-dispatch GPU attempt contract between the already-attested immutable handoff and the genuine canonical Candidate 1 launcher. The goal is to remove remaining operator ambiguity before a scarce compatible GPU attempt without granting generation or publication authority and without weakening any existing gate.

Branch: `phase18/story-intelligence` only. `main` was not modified.

## Pre-change state reviewed

- CS453 HEAD: `15b6f253ab4d11844eb8a718ffaa4b5dc763f38f`.
- `Phase 18 Story Intelligence Verification` push run #5784 and PR run #5785 on that exact SHA completed successfully.
- `Phase 18 CPU Verification Diagnostics` and the retrieved Phase 18 visual-study workflows on that SHA completed successfully.
- The canonical attested launcher already enforced:
  `attested pre-GPU -> immutable GPU handoff -> resource-locked Candidate 1 generation`.
- The remaining operational gap was that there was no single machine-readable packet binding the immutable handoff, required runner labels, exact canonical evidence paths, and canonical CLI invocation before the GPU attempt.

## Changes

### Added

`tools/phase18_prepare_first_golden_gpu_attempt.py`

- Consumes an existing `pul7sar-phase18-first-golden-gpu-handoff-v1` handoff.
- Requires the exact expected 40-character commit SHA.
- Replays branch, `$0-local`, offline-only, canonical-workflow, required-runner-label, eligibility, empty-blocker, and closed-authority requirements.
- Requires the existing canonical workflow and canonical launcher to exist in the repository.
- Emits a deterministic canonical command for the existing launcher with explicit paths for:
  - canonical resource-lock output;
  - pre-GPU receipt;
  - pre-GPU attestation;
  - pre-GPU summary;
  - immutable GPU handoff.
- Includes `--handoff` explicitly in the prepared canonical command so the exact handoff evidence path is unambiguous.
- Emits `workflow_dispatch_performed=false` and `png_created=false` and performs neither action itself.
- Keeps `authoritative_gate`, `network_download_authorized`, `generation_authorized`, `publication_ready`, and `seeds_2_to_4_authorized` false in every output.
- Fails closed on invalid SHA, missing/invalid handoff, commit/branch/cost/offline/workflow/runner-label drift, remaining blockers, ineligible handoff, or authority drift.

`tests/test_phase18_first_golden_gpu_attempt_contract.py`

- Verifies a valid immutable handoff produces the exact no-dispatch canonical attempt contract.
- Verifies the canonical command is commit-bound and explicitly carries `--handoff`.
- Verifies commit drift fails closed.
- Verifies generation-authority drift fails closed.
- Verifies required runner-label drift fails closed.
- Verifies invalid SHA and invalid JSON fail closed.
- Verifies no test path performs workflow dispatch or claims a PNG.

`docs/PHASE18_IMPLEMENTATION_LOG_454.md`

### Modified

None.

### Deleted

None.

## Gates preserved

CS454 does not change or weaken:

- factual verification and source-truth locks;
- real-person/entity identity verification;
- sentiment and loser-respect policy;
- SemanticPublicationGate;
- visual-quality or Human Review authority;
- Candidate 1 prompt, seed, dimensions, steps, guidance, or visual concept;
- Qwen2.5-VL or FLUX.2 model IDs/revisions;
- native BF16 requirement or FP16/FP32 substitution refusal;
- `$0-local`, `HF_HUB_OFFLINE=1`, or `TRANSFORMERS_OFFLINE=1` requirements;
- local-only model-cache policy;
- canonical/JIT/offload generation implementations;
- publication authority or Seeds 2–4 authority.

## Test intent

The central CPU verification suite remains authoritative. CS454 adds standard-library `unittest` coverage around the new no-dispatch attempt contract. No GPU result is fabricated and no workflow is dispatched by these tests.

## Remaining blocker

A First Genuine Golden Visual PNG still requires a compatible self-hosted NVIDIA execution host satisfying all existing fail-closed requirements simultaneously: CUDA-enabled PyTorch, a real CUDA device, native BF16, approved GPU/compute capability, sufficient live VRAM/RAM/cache headroom, compatible generation and semantic runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local`/offline-only policy.

When such a host is available, CS454 reduces the remaining human/operator gap to consuming the validated immutable handoff and executing the exact prepared canonical contract; it does not itself authorize or perform generation.
