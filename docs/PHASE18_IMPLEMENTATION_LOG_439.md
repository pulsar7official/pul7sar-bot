# Phase 18 Implementation Log — CS439

## Scope

CS439 adds a single fail-closed runner that executes the existing unified first-Golden pre-GPU proof and immediately attests the exact receipt bytes against the immutable Phase 18 source commit. This is preparatory integration work toward the first genuine Golden Visual PNG and does not grant generation or publication authority.

## Branch safety

- Target branch: `phase18/story-intelligence` only.
- `main` was reviewed only and was not modified.
- No `main.py` change was introduced.

## Added

### `tools/phase18_run_first_golden_pre_gpu_attested.py`

Adds one atomic CLI entry point for the two already-established gates:

1. `phase18_probe_first_golden_pre_gpu.inspect()`
2. `phase18_attest_first_golden_pre_gpu_receipt.attest()`

The runner:

- requires an immutable 40-character expected commit SHA;
- constrains receipt, attestation, and optional summary outputs to the repository;
- writes the pre-GPU receipt before attestation;
- attests the exact receipt bytes against the same expected commit;
- fails closed if either stage is not ready;
- rejects network, generation, publication, or Seeds 2–4 authority drift;
- performs no download, model loading, image generation, queue mutation, publication, or seed expansion.

Schema: `pul7sar-phase18-first-golden-attested-pre-gpu-run-v1`.

### `tests/test_phase18_first_golden_attested_pre_gpu_runner.py`

Regression coverage verifies:

- source/environment receipt is written before attestation;
- successful receipt + attestation is the only ready path;
- a non-ready pre-GPU receipt fails closed;
- failed receipt attestation fails closed;
- generation-authority drift fails closed;
- invalid immutable SHA prevents either probe from running;
- receipt and attestation cannot share the same path;
- output paths cannot escape the repository.

## Modified

None.

## Deleted

None.

## Preserved contracts

CS439 does not change:

- factual gates;
- real-person/entity identity gates;
- neutral result/sentiment policy;
- semantic-publication gates;
- visual-quality or Human Visual Review gates;
- prompts;
- Candidate 1 seed;
- generation parameters;
- approved Qwen2.5-VL model ID/revision;
- approved FLUX.2 model ID/revision;
- dependency versions;
- `$0-local` policy;
- offline/local-only model-resolution policy;
- publication authority;
- Seeds 2–4 authority.

## Why this materially reduces the remaining gap

The canonical, JIT, and offload workflows currently have separate source-isolation and execution-blocker steps. CS437 and CS438 introduced a stronger unified proof plus byte-level attestation, but consuming both directly in YAML would require repeated multi-command integration in every heavy workflow. CS439 reduces that integration surface to one command and one success/failure boundary, making the next workflow change smaller and less error-prone while preserving all existing downstream CUDA/resource/model/generation gates as defense in depth.

## Test status

The new regression suite is committed and will be exercised by the repository's existing Phase 18 verification CI on the exact CS439 branch head. Until those workflow runs complete successfully, CS439 must not be described as terminal-green.

## Remaining blocker to first genuine Golden Visual PNG

No genuine Golden PNG is claimed by CS439. Actual Candidate 1 generation still requires a compatible self-hosted NVIDIA execution host satisfying all existing requirements together, including CUDA-enabled PyTorch, a real CUDA device, native BF16, approved GPU/resource thresholds, sufficient live VRAM/RAM/filesystem headroom, compatible generation and semantic runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots locally resolvable with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and `PUL7SAR_PHASE18_COST_MODE=$0-local`.

The next safe step is to bind this single attested runner into the canonical, JIT, and offload workflows immediately after immutable checkout/branch reattachment and before their existing CUDA-heavy execution path, while retaining their current downstream blocker and resource checks as defense in depth.
