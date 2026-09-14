# Phase 18 Implementation Log — CS472

## Scope

CS472 closes a remaining `$0-local` enforcement gap before the first genuine Golden Editorial v6 Candidate 1 execution. The existing workflow asserted `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, local-only model resolution, pinned snapshots, and `network_download_authorized=false`; however, those controls govern approved model-resolution paths and policy evidence rather than every arbitrary Python socket opened by a third-party dependency.

CS472 adds process-local, fail-closed outbound network isolation for the strict Golden workflow while preserving local loopback/AF_UNIX IPC needed by local runtimes. Branch scope remains `phase18/story-intelligence` only. `main` is not modified.

## Starting state reviewed

Starting HEAD: `60bb5c455c1dd6d238acca59cd27882b13c5d5f7` (CS471).

The retrieved GitHub Actions runs for this exact SHA include completed successful Phase 18 checks. CS471 therefore moved beyond its previously pending state. No genuine Golden PNG is claimed; the compatible self-hosted NVIDIA execution environment remains the decisive execution dependency.

## Changes

### Added

- `engine/intelligence/zero_cost_network_guard.py`
  - Adds a stdlib-only network guard suitable for activation before third-party model libraries import.
  - Activates only when the existing strict contract is simultaneously asserted: `PUL7SAR_PHASE18_COST_MODE=$0-local`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1`.
  - Denies external IPv4/IPv6 `connect`, `connect_ex`, `create_connection`, and non-loopback `getaddrinfo` operations before network I/O.
  - Preserves IPv4/IPv6 loopback and AF_UNIX/local IPC.
  - Sets `PUL7SAR_PHASE18_NETWORK_GUARD_ACTIVE=1` inside guarded Python processes.
  - Does not authorize downloads, generation, publication, or any downstream authority.

- `sitecustomize.py`
  - Uses Python's standard startup hook to install the guard before application/model imports.
  - The existing Golden workflow already exports `PYTHONPATH=.`, so the hook is available to every Python process in that workflow without changing Candidate 1 parameters or model code.
  - Ordinary development/CI remains unaffected unless all three strict zero-cost/offline assertions are present.

- `tests/test_phase18_zero_cost_network_guard.py`
  - Proves all three existing offline/$0-local assertions are required for activation.
  - Proves loopback and AF_UNIX destinations are allowed while external IP/hostname destinations are denied by policy.
  - Launches an isolated Python subprocess under the exact strict environment and proves `sitecustomize` activates before an attempted `example.com:443` socket, which is rejected with the Phase 18 fail-closed error before network I/O.
  - Locks the Golden workflow's existing `PYTHONPATH`, `$0-local`, `HF_HUB_OFFLINE`, and `TRANSFORMERS_OFFLINE` contract so future workflow drift cannot silently bypass startup isolation.

- `docs/PHASE18_IMPLEMENTATION_LOG_472.md`

### Modified

- None.

### Deleted

- None.

## Gate preservation

CS472 does not relax or replace any existing gate. It adds an independent runtime enforcement layer underneath the existing zero-cost/local-only evidence. The following remain mandatory and fail-closed:

- factual/source-consensus verification;
- entity and identity verification;
- sentiment and loser-respect rules;
- exact approved Qwen2.5-VL and FLUX.2 revisions and local snapshots;
- CUDA-enabled PyTorch, real CUDA device, native BF16 and resource headroom;
- immutable branch/source/runner provenance;
- pre/post generation runtime and model-snapshot replay;
- freshness/source/PNG binding;
- `SemanticPublicationGate` and semantic inspection;
- exact Human Review bundle packaging/replay;
- human Golden-quality approval before publication or Seeds 2–4.

Sensitive authorities remain closed:

- `authoritative_gate=false`
- `network_download_authorized=false`
- `generation_authorized=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

## Why this materially reduces the remaining gap

A compatible GPU attempt can now rely on two independent layers: library-specific offline/local-cache controls and a Python socket boundary that rejects unexpected external connections from dependencies that do not honor Hugging Face/Transformers offline settings. This reduces the risk that the first scarce GPU attempt violates `$0-local` because of telemetry, metadata lookup, or another incidental Python network path.

The guard intentionally allows loopback/local IPC and therefore does not forbid local CUDA/model execution merely to prove zero-cost isolation.

## Validation intent

The decisive validation is the repository's discover-based Phase 18 CPU/Story Intelligence suite on the exact CS472 HEAD. The new subprocess regression test requires no real network and no GPU: the external destination is rejected by the guard before any socket I/O occurs.

No GPU result or Golden PNG is claimed by CS472.

## Remaining blocker to the first genuine Golden PNG

A genuine PNG still requires a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, a visible CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, compatible approved runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally. If that execution environment is unavailable, no Golden PNG may be fabricated or inferred.
