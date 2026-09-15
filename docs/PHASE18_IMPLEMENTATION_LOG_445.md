# Phase 18 Implementation Log — CS445

## Scope

CS445 integrates the already-reviewed canonical attested launcher from CS444 directly into the authoritative `Phase 18 First Genuine Golden Editorial v6` workflow on `phase18/story-intelligence` only.

No write was made to `main`.

## Starting state

- Phase 18 branch start SHA: `c1035613eaee642ccb4c26d2b156cdd0c90ec212`.
- CS444 was terminal-green before CS445 began: the exact-SHA Phase 18 Story Intelligence Verification push and pull-request runs completed successfully.
- The canonical workflow still invoked `tools/phase18_colab_first_genuine_resources_locked.py` directly after its existing execution-blocker and CUDA/native-BF16 checks.
- CS444 had already provided `tools/phase18_run_first_genuine_golden_v6_canonical_attested.py`, but the canonical workflow had not yet consumed it.

## Changes

### Modified

- `.github/workflows/phase18-first-genuine-golden-v6.yml`
  - Requires the canonical attested launcher to exist during immutable branch reattachment.
  - Preserves the existing first-Golden execution-blocker probe.
  - Preserves the existing explicit CUDA-enabled PyTorch and native-BF16 proof.
  - Replaces the workflow's direct invocation of `phase18_colab_first_genuine_resources_locked.py` with `phase18_run_first_genuine_golden_v6_canonical_attested.py`.
  - Binds the launcher to the immutable dispatch SHA through `--expected-commit "$DISPATCH_SHA"`.
  - Writes distinct canonical pre-GPU receipt, attestation, and summary evidence under `output/phase18_gpu_smoke/`.
  - Preserves the same canonical resource-lock output path consumed by all downstream replay/provenance checks.
  - Preserves all downstream local-only model receipt verification, runtime/semantic/resource replay, PNG SHA replay, source-commit binding, source-bound artifact replay, artifact upload, and GitHub transport attestation steps.

### Added

- `tests/test_phase18_first_golden_canonical_attested_workflow_integration.py`
  - Standard-library `unittest` regression coverage.
  - Verifies exact dispatch-SHA binding.
  - Verifies the direct canonical generation invocation has been removed from the workflow and is owned by the attested launcher instead.
  - Verifies defense-in-depth ordering remains execution blocker -> CUDA/native BF16 -> attested canonical launcher -> downstream evidence replay.
  - Verifies `$0-local`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and rejection of FP16/FP32 substitution remain present.
  - Verifies the three attested pre-GPU evidence paths remain distinct and fall under uploaded evidence.
  - Verifies Phase 18 branch/main isolation and downstream source/upload provenance steps remain present.

- `docs/PHASE18_IMPLEMENTATION_LOG_445.md`
  - This implementation record.

### Deleted

- Nothing.

## Commit sequence before this log commit

- `7e6e4e05fe48c325b9dff2683a3e63df3c3abfe8` — canonical workflow integration.
- `c34ad4e3675b3b1be09e764253505902e2c2a9e2` — initial integration regression test.
- `f413c558ffef05951058075ba0e370b75905df64` — simplify the direct-entrypoint assertion so the test remains unambiguously standard-library Python.

## Security and quality invariants preserved

CS445 does not change:

- story facts or factual verification gates;
- entity/person identity verification;
- result/sentiment neutrality rules;
- SemanticPublicationGate behavior;
- visual-quality thresholds or Human Visual Review authority;
- Candidate 1 prompt, seed, generation parameters, model IDs, or immutable model revisions;
- Qwen2.5-VL or FLUX.2 approved identities;
- dependency versions;
- native BF16 requirement;
- zero-cost requirement;
- local-cache-only model resolution;
- publication authority;
- Seeds 2–4 authority.

No automatic model download was authorized. No FP16/FP32 quality substitution was introduced.

## Canonical execution order after CS445

```text
immutable workflow dispatch SHA
        ↓
exact Phase 18 checkout + main.py isolation
        ↓
existing first-Golden execution blocker
        ↓
existing explicit CUDA/native-BF16/offline proof
        ↓
CS444 canonical attested launcher
        ↓
CS439 attested source + host pre-GPU contract
        ↓
existing resource-locked Candidate 1 entrypoint
        ↓
existing local-only/runtime/semantic/resource evidence replay
        ↓
existing PNG SHA + source-commit provenance replay
        ↓
existing artifact transport attestation
        ↓
Human Visual Review remains required
```

The extra attestation is defense-in-depth. It does not replace any downstream gate.

## Genuine Golden PNG status

CS445 does not fabricate or simulate a Golden PNG. A genuine Candidate 1 PNG still requires a compatible self-hosted NVIDIA execution host satisfying the repository's existing fail-closed contract, including:

- CUDA-enabled PyTorch and at least one real CUDA device;
- native BF16 support;
- approved GPU identity / compute capability;
- sufficient live-free VRAM;
- sufficient currently available host RAM;
- sufficient filesystem/cache headroom;
- compatible generation runtime;
- coherent Qwen2.5-VL semantic runtime;
- exact approved Qwen2.5-VL snapshot already locally resolvable;
- exact approved FLUX.2 snapshot already locally resolvable;
- `PUL7SAR_PHASE18_COST_MODE=$0-local`;
- `HF_HUB_OFFLINE=1`;
- `TRANSFORMERS_OFFLINE=1`;
- no network model download and no FP16/FP32 fallback.

If those requirements are unavailable, the canonical path must fail closed before claiming a genuine Golden result.
