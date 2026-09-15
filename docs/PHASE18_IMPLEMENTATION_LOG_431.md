# Phase 18 Implementation Log 431

## Scope

CS431 advances `phase18/story-intelligence` only. `main` remains read-only and is not modified.

## Reviewed state

- CS430 head: `0d0a25bb6ee76091d4079b4628b917c0f961abc9`.
- CS430 Story Intelligence Verification run `34721068262` completed successfully on the exact CS430 head.
- `main` was observed read-only at `c1e828fe965a17037749f8d0a5bc5443a150f2c3` during this change set.
- No genuine Golden PNG was present or fabricated.
- The CS429/CS430 blocker probe already proved offline mode, `$0-local`, CUDA presence, native BF16, and exact locally resolvable pinned Qwen/FLUX snapshots, but it did not reuse the authoritative live free-VRAM or host-memory qualification policies that run later in the Golden path.

## Problem closed in CS431

A host could satisfy the early blocker probe because CUDA and BF16 were present while still lacking enough currently free GPU VRAM for the approved FLUX.2 candidate or enough currently available system RAM for the sequential-offload path. The canonical resource lock would reject that host later, but the early diagnostic receipt could incorrectly report `ready_for_authoritative_golden_preflight=true`.

That mismatch weakened the usefulness of the blocker receipt and could waste a scarce compatible self-hosted GPU execution opportunity.

## Changes

### Modified

- `tools/phase18_probe_first_golden_execution_blocker.py`
  - Raises the receipt schema to `pul7sar-phase18-first-golden-execution-blocker-probe-v3`.
  - Reuses `LocalRuntimeProbe` plus `GpuHostQualificationPolicy` against the already-approved `FLUX2_KLEIN_4B_LOCAL` candidate.
  - Therefore records and enforces the same live GPU identity, total VRAM, **free VRAM**, native BF16, compute capability, and model VRAM floor used by the authoritative GPU qualification path.
  - Reuses `HostMemoryQualificationProbe`, including the existing first-Golden available-system-RAM floor.
  - Adds fail-closed blocker codes `GPU_HOST_NOT_GOLDEN_QUALIFIED` and `HOST_MEMORY_NOT_READY`.
  - Adds independent zero-cost drift blockers for both resource receipts.
  - Embeds the full non-authoritative GPU-qualification and host-memory reports in the blocker receipt so the exact resource reason remains inspectable.
  - Preserves local-only Hugging Face snapshot resolution for the exact pinned Qwen2.5-VL and FLUX.2 revisions.
  - Performs no model download, model loading, generation, queue mutation, publication decision, or downstream authority grant.

- `tests/test_phase18_first_golden_execution_blocker_probe.py`
  - Updates the ready fixture for schema v3.
  - Injects deterministic ready GPU and host-memory qualification receipts so unit discovery remains CPU-safe.
  - Adds regression coverage proving CUDA+BF16 alone are insufficient when live free VRAM is below the approved model floor.
  - Adds regression coverage proving insufficient currently available host RAM blocks readiness before authoritative preflight.
  - Adds regression coverage for zero-cost drift inside the new resource qualification evidence.
  - Preserves the existing offline, immutable-snapshot, and local-resolution regressions.

### Added

- `docs/PHASE18_IMPLEMENTATION_LOG_431.md`

### Deleted

- None.

## Gates preserved

CS431 does not change factual gates, entity/identity verification, sentiment neutrality, semantic-publication controls, visual-quality thresholds, prompts, seeds, generation parameters, dependencies, approved model identities, or immutable revisions.

No paid inference, network model download, precision downgrade, automatic publication, Human Visual Review approval, Golden quality approval, or Seeds 2-4 authorization is introduced.

The final authority state remains fail-closed:

- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

## Test intent

Repository CI must prove:

1. Python/unittest discovery remains valid after the blocker schema update.
2. A nominal CUDA+BF16 host cannot be reported ready if authoritative live free-VRAM qualification fails.
3. A nominal CUDA+BF16 host cannot be reported ready if available system RAM is below the existing first-Golden floor.
4. `$0-local`, both offline flags, exact immutable local Qwen/FLUX snapshots, and non-authoritative downstream state remain mandatory.
5. Existing canonical/JIT blocker-probe integration remains compatible with the stronger readiness semantics.

## Remaining gap to first genuine Golden PNG

A genuine Candidate 1 still requires an actually available self-hosted NVIDIA execution host that passes the now-aligned early and authoritative gates: CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient **live free VRAM**, sufficient currently available system RAM, sufficient local storage/working headroom, and both exact approved Qwen2.5-VL and FLUX.2 immutable snapshots locally resolvable with network model access disabled.

CS431 does not fabricate that environment or a PNG. It materially narrows the remaining execution gap by ensuring the earliest persisted blocker receipt now uses the same live GPU-resource and host-memory policies that would otherwise reject the host later in the Golden path.
