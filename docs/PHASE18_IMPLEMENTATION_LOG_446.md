# Phase 18 Implementation Log — CS446

## Scope

CS446 locks the command-line contract between the attested first-Golden pre-GPU runner and every Phase 18 execution path that consumes it, on `phase18/story-intelligence` only.

No write was made to `main`.

## Starting state

- Phase 18 branch start SHA: `bc56b073a74e6e303ddcc58b2c5b058f36b8b691`.
- CS445 was terminal-green before CS446 began: the exact-SHA Story Intelligence Verification push and pull-request runs had completed successfully.
- Canonical, JIT, offload, and host-readiness paths were already using the attested pre-GPU contract.
- Direct inspection confirmed the current host-readiness workflow uses the runner's actual flags (`--expected-commit`, `--receipt`, `--attestation`, `--summary`). No production CLI mismatch was present in the starting HEAD.
- The remaining risk was regression drift: the workflows and Python entrypoints could later diverge without a focused cross-path test.

## Changes

### Added

- `tests/test_phase18_first_golden_attested_cli_contract.py`
  - Standard-library `unittest` only.
  - Extracts `argparse` flags independent of one-line vs multi-line formatting.
  - Verifies the attested pre-GPU runner exposes the current evidence flags and rejects stale `*-out` aliases.
  - Verifies host-readiness, JIT, and offload workflows invoke the attested runner with the immutable dispatch SHA plus `--receipt`, `--attestation`, and `--summary`.
  - Verifies those direct paths retain `$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1`.
  - Verifies the canonical workflow invokes the canonical attested launcher with the same evidence contract and immutable dispatch SHA.
  - Verifies the canonical launcher's parser exposes the flags consumed by the workflow.
  - Verifies the attested runner and canonical launcher continue to keep network download, publication, and Seeds 2–4 authority closed.

- `docs/PHASE18_IMPLEMENTATION_LOG_446.md`
  - This implementation record.

### Modified

- `tests/test_phase18_first_golden_attested_cli_contract.py`
  - Follow-up in the same CS after initial creation: made argument discovery formatting-independent so multi-line `argparse.add_argument(...)` definitions in the canonical launcher are handled correctly.

### Deleted

- Nothing.

## Commit sequence before this log commit

- `8d7cd807ca4fcc9f7a41f6b6634cb222e2ad2ad7` — add the cross-path attested CLI contract regression test.
- `1a2b317bce1a10bd72fcb4cb27c033432ce0c4db` — make parser flag extraction robust to multi-line formatting.

## Security and quality invariants preserved

CS446 does not change production generation code or workflow behavior. It does not change:

- story facts or factual verification gates;
- person/entity identity verification;
- sentiment/result neutrality rules;
- SemanticPublicationGate behavior;
- visual-quality thresholds or Human Visual Review authority;
- Candidate 1 prompt, seed, or generation parameters;
- Qwen2.5-VL or FLUX.2 model IDs/revisions;
- dependency versions;
- native BF16 requirement;
- `$0-local` requirement;
- offline/local-cache-only model resolution;
- publication authority;
- Seeds 2–4 authority.

No automatic model download was authorized. No FP16/FP32 substitution was introduced.

## Why this materially reduces the remaining gap

A compatible self-hosted GPU is scarce and should not be consumed by an avoidable orchestration failure. CS446 makes the CLI hand-off between the immutable source/host attestation layer and all first-Golden entry paths a regression-tested contract. This prevents a future flag rename or workflow typo from wasting the first compatible CUDA/BF16 execution before the real model/cache/resource gates are reached.

## Genuine Golden PNG status

No PNG was generated or simulated by CS446.

A genuine Candidate 1 PNG still requires a compatible self-hosted NVIDIA host satisfying the existing fail-closed contract, including CUDA-enabled PyTorch, a real CUDA device, native BF16, approved GPU identity/compute capability, sufficient live-free VRAM, sufficient available host RAM and filesystem/cache headroom, compatible generation and Qwen semantic runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already locally resolvable under `$0-local` and offline-only execution.

Until those runtime conditions are demonstrated on a matching runner, generation must remain fail-closed and no Golden result may be claimed.
