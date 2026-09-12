# Phase 18 Implementation Log 415

## Scope

Branch: `phase18/story-intelligence` only. `main` was reviewed read-only and was not modified.

This change set advances the First Genuine Golden Editorial v6 path by making the CS414 local-only Qwen/FLUX receipt verifier an explicit mandatory gate inside the real Golden v6 workflow before evidence replay continues.

## Starting state

Starting Phase 18 HEAD: `471bdbb273595dacb1d1d42ab45f52e8cc4046f0`.

The Phase 18 Story Intelligence Verification run for that SHA (`34671519679`, run number `5550`) completed successfully. The Golden v6 workflow already required the self-hosted CUDA/BF16 runner, `$0-local`, offline Hugging Face/Transformers resolution, exact model-cache/resource/runtime/semantic staging evidence, source binding, artifact replay, and transport attestation.

CS414 had added `tools/phase18_verify_local_only_model_receipts.py`, but the First Genuine Golden v6 workflow did not yet invoke that verifier as a mandatory runtime gate.

## Modified

### `.github/workflows/phase18-first-genuine-golden-v6.yml`

Added an explicit existence check for `tools/phase18_verify_local_only_model_receipts.py` during immutable branch/source isolation.

Added a new fail-closed step immediately after the resource/runtime/semantic locked Candidate 1 execution and before the existing Golden evidence replay:

`Verify Qwen and FLUX receipts are immutable local-only before Golden replay`

The step invokes the CS414 verifier against the exact runtime receipts:

- `output/phase18_gpu_smoke/qwen-model-cache.json`
- `output/phase18_gpu_smoke/flux-model-cache.json`

It writes:

- `output/phase18_gpu_smoke/first-genuine-golden-v6-local-only-model-receipts.json`

The workflow then requires the verification receipt to prove all of the following before continuing:

- status is `PHASE18_LOCAL_ONLY_MODEL_RECEIPTS_VERIFIED`
- `cost_mode == "$0-local"`
- `network_download_authorized == false`
- `local_files_only == true`
- `generation_authorized == false`
- `publication_ready == false`
- `seeds_2_to_4_authorized == false`

This does not replace the existing replay checks. It adds an independent mandatory local-only proof before replay.

## Added

### `tests/test_phase18_first_genuine_golden_v6_local_only_receipt_gate.py`

Regression coverage verifies that:

1. the local-only receipt verifier is required by the workflow checkout/isolation contract;
2. the verifier executes before the existing Golden evidence replay step;
3. the exact Qwen and FLUX runtime receipt paths are used;
4. the local-only verification output is persisted under `output/phase18_gpu_smoke/**`, so it is included by the existing evidence artifact upload;
5. `$0-local`, `network_download_authorized=false`, and `local_files_only=true` are required;
6. generation/publication/Seeds 2-4 authority remains closed;
7. the self-hosted CUDA/BF16 runner and offline environment requirements remain unchanged.

## Deleted

Nothing.

## Gates preserved

No factual, identity, sentiment, semantic-publication, visual-quality, human-review, Golden-quality, or publication authority gate was weakened.

No model ID, immutable model revision, prompt, generation parameter, dependency, or publication behavior was changed.

`main` was not modified.

The workflow still requires:

- `self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18`
- CUDA-enabled PyTorch already installed on the runner
- native BF16 support
- `$0-local`
- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`
- approved Qwen2.5-VL and FLUX.2 immutable snapshots already present in canonical local Hugging Face cache

## First Genuine Golden PNG status

No PNG was fabricated or claimed.

The remaining non-substitutable blocker is an available compatible self-hosted NVIDIA execution host meeting the Golden v6 runner contract, with CUDA-enabled PyTorch, native BF16, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present locally.

Once that host exists, the workflow now has an additional mandatory fail-closed proof that the model receipts themselves authorize no network download and were resolved with local-files-only semantics before Golden replay can continue.
