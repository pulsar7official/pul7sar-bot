# Phase 18 Implementation Log — CS455

## Title
First-Golden GPU Attempt Content Binding

## Branch scope
- Repository: `pulsar7official/pul7sar-bot`
- Branch: `phase18/story-intelligence` only
- `main` was not modified.

## Starting state
CS454 was reviewed first at exact branch HEAD `32e8e916ad80426287b5b56473e9d52607803f53`. The retrieved GitHub checks for that commit were completed successfully. CS454 already provided a deterministic, exact-commit-bound first-Golden GPU attempt contract, but the contract identified its source handoff, canonical workflow, and canonical launcher by path without cryptographically binding their file contents.

## Problem closed in CS455
A prepared GPU attempt contract could become stale if any of the following files changed after preparation but before a later consumer replayed the contract:

1. the attested GPU handoff;
2. `.github/workflows/phase18-first-genuine-golden-v6.yml`;
3. `tools/phase18_run_first_genuine_golden_v6_canonical_attested.py`.

The expected commit remains immutable, but explicitly recording file digests makes the attempt package independently replayable and closes this content-level TOCTOU ambiguity.

## Changes

### Modified: `tools/phase18_prepare_first_golden_gpu_attempt.py`
- Added standard-library SHA-256 hashing only; no dependency was introduced.
- Added deterministic SHA-256 capture for the source GPU handoff.
- Added deterministic SHA-256 capture for the canonical workflow.
- Added deterministic SHA-256 capture for the canonical attested launcher.
- Added these fields to the existing v1 attempt contract without changing its authority semantics:
  - `source_handoff_sha256`
  - `canonical_workflow_sha256`
  - `canonical_launcher_sha256`
- Existing fail-closed blockers remain unchanged.
- Missing canonical files still block readiness.
- Invalid handoff JSON still blocks readiness while its raw file digest is retained as diagnostic evidence.

### Modified: `tests/test_phase18_first_golden_gpu_attempt_contract.py`
- Added exact SHA-256 assertions for all three content-bound files.
- Added 64-hex-length contract assertions.
- Added a regression test proving the handoff digest changes when handoff bytes change.
- Preserved commit-drift, authority-drift, runner-label-drift, invalid-SHA, and invalid-JSON fail-closed tests.
- Preserved assertions that no workflow dispatch or PNG creation is claimed by this preparation layer.

### Added: `docs/PHASE18_IMPLEMENTATION_LOG_455.md`
This implementation record.

## Deleted
None.

## Production behavior intentionally unchanged
CS455 does not dispatch a workflow and does not load Qwen2.5-VL or FLUX.2. It does not generate an image and does not authorize publication or Seeds 2–4. It does not alter Candidate 1 prompt, seed, dimensions, steps, guidance, approved model identities/revisions, native-BF16 requirements, zero-cost policy, or offline-only policy.

The following authorities remain closed in the attempt contract:

- `authoritative_gate=false`
- `network_download_authorized=false`
- `generation_authorized=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

## Preserved gates
- factual verification and fact locks;
- person/entity identity verification;
- sentiment and loser-respect policy;
- `$0-local` execution requirement;
- `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` requirements;
- no network model download;
- native BF16 requirement and rejection of FP16/FP32 quality substitution;
- approved Qwen2.5-VL and FLUX.2 identities/revisions;
- SemanticPublicationGate;
- visual-quality and Human Review authority;
- immutable branch/commit binding;
- canonical attested pre-GPU/handoff/resource/runtime/semantic path.

## Test status
The new regression coverage was committed so the repository's existing Phase 18 central verification and CPU diagnostics can exercise it. At the moment this log is written, CS455 has just been pushed and no terminal-green claim is made for the new HEAD until GitHub CI completes.

## Remaining blocker to the first genuine Golden Visual PNG
No PNG was fabricated or claimed. The remaining execution blocker is still availability of a compatible self-hosted NVIDIA runner satisfying the complete existing execution contract simultaneously: CUDA-enabled PyTorch, a real CUDA device, native BF16, approved GPU/compute capability, sufficient live-free VRAM/RAM/cache/filesystem headroom, compatible generation and Qwen semantic runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` and offline-only operation.

## Material gap reduction
CS455 makes the pre-attempt package content-addressed. A future execution/replay layer can now reject a stale or swapped handoff/workflow/launcher by digest before consuming the scarce GPU attempt, rather than trusting paths alone.
