# Phase 18 Implementation Log — CS504

## Scope

Branch: `phase18/story-intelligence` only. `main` was not modified.

## Review result

Reviewed CS503 and the live authoritative Candidate-1 workflow. The workflow still invokes `phase18_run_first_genuine_golden_v6_canonical_attested.py` directly, while the CS499/CS500 freshness-bound launcher expects four specifically named authoritative pre-generation evidence files. The preflight-only workflow already has the safe capture primitives for zero-cost/network, runner/CUDA identity, approved local snapshot inventory, and execution blockers.

## Material change

Added `tools/phase18_capture_authoritative_pre_generation_evidence.py`, a fail-closed `$0-local` / offline-only orchestrator that produces the exact four filenames consumed by `phase18_run_first_genuine_golden_v6_canonical_fresh.py`:

- `first-genuine-golden-v6-zero-cost-network-guard.json`
- `first-genuine-golden-v6-runner-identity.json`
- `first-genuine-golden-v6-approved-snapshot-inventory.json`
- `first-genuine-golden-v6-execution-blocker-probe.json`

It then invokes the existing CS498 semantic+cryptographic binder and persists `first-genuine-golden-v6-authoritative-pre-generation-binding.json`. It refuses malformed source SHAs, non-`$0-local` mode, or non-offline model resolution before running any probe. It does not generate a PNG and leaves authoritative, network-download, generation, Human Review, Golden approval, publication, and Seeds 2-4 authority closed.

Added stdlib `unittest` regression coverage proving the exact evidence names, four-probe orchestration, binding inputs, authority closure, malformed-SHA rejection, and offline fail-closed behavior.

## Added

- `tools/phase18_capture_authoritative_pre_generation_evidence.py`
- `tests/test_phase18_authoritative_pre_generation_evidence_capture.py`
- `docs/PHASE18_IMPLEMENTATION_LOG_504.md`

## Modified

- None.

## Deleted

- None.

## Tested / verified

- Static review of `.github/workflows/phase18-first-genuine-golden-v6.yml`: live Candidate 1 still calls the canonical-attested launcher directly.
- Static review of `.github/workflows/phase18-first-golden-preflight-only.yml`: confirmed the four existing capture primitives and fail-closed CUDA/BF16/offline preflight behavior.
- Added unittest-only regression coverage so Phase 18 discovery does not require pytest.
- GitHub Actions for the final CS504 head must complete before CS504 can be called terminal-green.

## Gates preserved

No factual/source-consensus, identity/entity, sentiment/loser-respect, zero-cost/offline, semantic-publication, exact-model/runtime, CUDA/native-BF16, PNG structural/chunk/canonical, Human Visual Review, Golden-quality, publication, or Seeds 2-4 gate was weakened.

## Exact remaining gap

CS504 removes the authoritative evidence-filename/capture gap, but it intentionally does not claim activation: the live authoritative workflow must still invoke this capture step and route Candidate 1 through `phase18_run_first_genuine_golden_v6_canonical_fresh.py` rather than directly through the canonical-attested launcher. That activation must be done without truncating or reconstructing the large security-sensitive workflow from incomplete connector output, and must be regression-locked before GPU execution.

After CPU CI is green and activation is safely complete, the external execution blocker remains a compatible self-hosted NVIDIA host with CUDA-enabled PyTorch, a real CUDA device with native BF16, sufficient GPU/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` / offline-only execution.

No Golden PNG was fabricated or claimed.
