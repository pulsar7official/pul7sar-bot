# Phase 18 Implementation Log — CS435

## Scope

Branch: `phase18/story-intelligence` only. `main` was read-only and was not modified.

CS435 closes a remaining pre-GPU diagnostic gap before the first genuine Golden Visual PNG. The shared execution blocker probe already verified the approved generation package/runtime contract, CUDA/BF16, live VRAM, host RAM, working filesystem headroom, and exact local-only Qwen/FLUX snapshots. However, the authoritative resource path later runs `Qwen25VLReadinessProbe` before FLUX generation to prove that the documented public Qwen2.5-VL Transformers API and Pillow runtime are actually coherent on the host. A host could therefore pass the early blocker probe and still fail later at semantic runtime readiness.

## Added

- `docs/PHASE18_IMPLEMENTATION_LOG_435.md`

## Modified

- `tools/phase18_probe_first_golden_execution_blocker.py`
  - Reuses `Qwen25VLReadinessProbe` directly; no parallel semantic readiness policy was invented.
  - Adds a non-model-loading semantic runtime qualification record before authoritative preflight.
  - Requires the semantic runtime to be ready, bound to the approved Qwen model identity, `$0-local`, and authority-closed.
  - Adds fail-closed blocker codes:
    - `SEMANTIC_RUNTIME_NOT_READY`
    - `SEMANTIC_RUNTIME_MODEL_ID_DRIFT`
    - `SEMANTIC_RUNTIME_ZERO_COST_DRIFT`
    - `SEMANTIC_RUNTIME_AUTHORITY_DRIFT`
  - Persists the `semantic_runtime` diagnostic record in the blocker receipt.
  - Advances the blocker receipt schema from `pul7sar-phase18-first-golden-execution-blocker-probe-v5` to `...-v6`.
  - Still performs no model loading, download, generation, queue mutation, PNG creation, human approval, or publication.

- `tests/test_phase18_first_golden_execution_blocker_probe.py`
  - Adds a deterministic ready semantic-runtime fixture so CPU CI does not need CUDA or Qwen weights.
  - Extends the all-ready case to require semantic runtime readiness and the approved Qwen identity.
  - Extends the aggregate blocked-host case to require `SEMANTIC_RUNTIME_NOT_READY`.
  - Adds regression coverage proving that Qwen public-API/runtime incoherence blocks authoritative preflight.
  - Adds regression coverage proving that semantic model identity, cost-mode, or authority drift blocks readiness.
  - Updates the expected blocker-probe schema to v6.

## Deleted

None.

## Gate preservation

No prompts, seeds, generation parameters, approved Qwen/FLUX model IDs, immutable revisions, dependencies, or publication rules were changed.

The following remain fail-closed and unchanged:

- factual verification
- entity/identity verification
- loser/respectful sentiment neutrality
- `$0-local` execution
- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`
- no network model download
- native BF16 requirement
- semantic-publication gates
- human visual review
- Golden-quality review
- publication authority
- Seeds 2–4 authority

The blocker receipt remains explicitly non-authoritative with:

- `network_download_authorized=false`
- `generation_authorized=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

## Tests / verification

The new regression coverage is part of the repository's existing Phase 18 unittest discovery and Story Intelligence Verification workflow. CS434 was terminal-green before CS435 work began.

CS435 requires the exact final branch SHA to pass Story Intelligence Verification before it can be called terminal-green.

## Remaining blocker to first genuine Golden PNG

No genuine Golden Visual PNG was created in CS435.

Actual Candidate 1 execution still requires a compatible self-hosted NVIDIA host with all of the following simultaneously true:

- CUDA-enabled PyTorch and at least one real CUDA device
- native BF16
- approved GPU identity / compute capability
- sufficient total and live-free VRAM
- sufficient currently available system RAM
- sufficient working filesystem headroom
- approved generation runtime contract
- coherent Qwen2.5-VL public semantic runtime (`Qwen25VLReadinessProbe` ready)
- exact approved immutable Qwen2.5-VL snapshot locally resolvable
- exact approved immutable FLUX.2 snapshot locally resolvable
- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`
- `PUL7SAR_PHASE18_COST_MODE=$0-local`
- no network model download

If such a host is unavailable, the project must remain blocked rather than fabricating a Golden PNG.