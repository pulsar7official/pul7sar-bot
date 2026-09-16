# Phase 18 Implementation Log 395 — Golden v6 Evidence Artifact Replay Hardening

## Scope

Branch: `phase18/story-intelligence` only.

`main` was reviewed read-only at `064fd78cefdf033722e1ca81353a617a3753c43d`. No merge, rebase, reset, force-update, or file write was performed on `main`.

Starting Phase 18 HEAD for this changeset: `4c6aaa1d01d81864955cb625b65eb50aa026d0b0`.

## Why this changeset exists

CS393/CS394 made the downloaded First Genuine Golden v6 artifact replay verifier capable of safely rebasing runner-recorded `output/...` paths and validating the final PNG signature, SHA-256, byte count, and fail-closed downstream authorities.

A remaining provenance gap was identified: the final resource-lock receipt binds nine upstream evidence files by path, SHA-256, and byte count, but the CPU-safe post-download artifact verifier did not independently replay those evidence records. The in-workflow replay does perform this check before upload, but a downloaded artifact verifier should not rely only on the final receipt plus PNG after the artifact leaves the producing runner.

CS395 closes that gap without performing model inference, network access, publication, or any authority elevation.

## Code changes

### Modified

- `tools/phase18_verify_first_genuine_golden_v6_artifact.py`
  - Added the exact nine-file evidence inventory expected from the v6 resource lock:
    - `gpu_host_qualification`
    - `host_memory_preflight`
    - `cache_budget`
    - `semantic_preflight`
    - `qwen_model_cache`
    - `flux_model_cache`
    - `runtime_fingerprint_pre`
    - `runtime_fingerprint_post`
    - `strict_golden_staging`
  - Generalized safe `output/...` artifact rebasing so the same topology rules protect PNG and evidence files.
  - Requires the evidence mapping to contain exactly the expected set.
  - Recomputes every evidence file SHA-256 from downloaded bytes.
  - Rechecks every evidence file byte count.
  - Rejects invalid, missing, ambiguous, non-output-rooted, or path-escaping evidence files.
  - Rebinds `staging_receipt` to the exact replay-verified `strict_golden_staging` evidence file.
  - Returns `evidence_files_verified=9` only after all evidence records pass replay.
  - Continues to leave Human Review, Golden Quality, Seeds 2–4, and publication authority closed.

- `tests/test_phase18_verify_first_genuine_golden_v6_artifact.py`
  - Fixture now creates all nine bound evidence files.
  - Positive coverage verifies all nine files in both retained-`output/` and upload-artifact LCA-flattened layouts.
  - Added rejection coverage for evidence byte/SHA tampering.
  - Added rejection coverage for incomplete evidence inventory.
  - Added rejection coverage for `staging_receipt` binding drift.
  - Existing PNG tamper, byte-count, publication-authority, non-output-rooted path, and ambiguous-path tests remain.

### Added

- `docs/PHASE18_IMPLEMENTATION_LOG_395.md`

### Deleted

- Nothing.

### Dependencies

- No dependency changes.

## Commits

- Production verifier hardening: `a54b013905d1cc8f06964bef0b20d49007365546`
- Exact code-and-test-bearing SHA: `2dc1da38a7b73940af3882e4ed7b4a9988a19dec`

## Verification state

The pre-CS395 code-and-test SHA `0925964e6a6f1221dd2cf3f7a442b5e996c7769f` is confirmed `verify-story-intelligence: completed/success`, establishing CS394 as green before this change.

For CS395, GitHub created `verify-story-intelligence` for exact code-and-test SHA `2dc1da38a7b73940af3882e4ed7b4a9988a19dec` (Actions run `34547997521`). At documentation time it is queued, so CS395 must not yet be described as terminal-green.

## Runtime blocker status

The available execution host was rechecked during CS395:

- `torch=2.10.0+cpu`
- `cuda_available=False`
- `torch_cuda_version=None`
- `cuda_device_count=0`
- `bf16_supported=False`
- `nvidia-smi=unavailable`

Therefore this host cannot honestly execute the genuine CUDA/BF16 First Golden v6 inference path.

The genuine PNG still requires a compatible `$0-local` self-hosted NVIDIA runner with CUDA-enabled PyTorch, native BF16 support, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already present locally. No placeholder, fixture, synthetic PNG, or previous artifact is promoted as a Genuine Golden Visual.

## Gate preservation

CS395 does not grant or bypass factual/freshness, Entity/Identity, sentiment-neutrality/loser-respect, zero-cost, semantic-publication, generated-layer, visual-quality, Human Review, Golden Quality, or publication authority. It only strengthens independent post-download provenance replay.

Expected downstream state remains fail-closed:

- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

## Remaining gap

1. Wait for exact-SHA CS395 CI to complete successfully; diagnose and correct only verified failures if it does not.
2. Execute `.github/workflows/phase18-first-genuine-golden-v6.yml` only on an eligible self-hosted `$0-local` CUDA/native-BF16 host with all pinned model assets already local.
3. Download the resulting artifact and run the hardened CPU-safe replay verifier against the final receipt, all nine evidence files, and PNG bytes.
4. Only after that may the generated Candidate 1 proceed to the separate human visual-quality review and later Golden/publication gates.