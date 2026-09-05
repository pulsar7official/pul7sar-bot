# Phase 18 Change Set 168 — Host-Memory Workflow Regression Repair

## Scope

Branch: `phase18/story-intelligence` only.

`main` and `main.py` were not modified, merged, force-updated, or used as write targets.

## Why this change was necessary

The current branch head at the start of this change set was `eaa622243fbfc11569e9abfe22a9e2ca4aa263ed` (Change Set 167). GitHub Actions run `32944740034` showed that every visible companion Phase 18 workflow passed, but `Phase 18 Story Intelligence Verification` failed during the discover validation stage.

The failure was isolated to one regression test:

`test_phase18_first_golden_host_memory_workflow.Phase18FirstGoldenHostMemoryWorkflowTests.test_immutable_phase18_source_and_main_isolation_precede_gpu_execution`

The production workflow itself already had the correct order:

1. immutable Phase 18 source checkout and branch reattachment;
2. `main.py` isolation check;
3. CUDA proof;
4. actual Candidate 1 execution through `phase18_colab_first_golden_host_memory_locked.py`.

The test used `self.text.index("phase18_colab_first_golden_host_memory_locked.py")`, which matched an earlier `test -f tools/phase18_colab_first_golden_host_memory_locked.py` source-presence assertion inside the isolation step instead of the later executable command. That created a false ordering failure even though the workflow was correctly ordered.

## Changes

### Modified

- `tests/test_phase18_first_golden_host_memory_workflow.py`
  - execution-order assertions now target the concrete invocation:
    - `python tools/phase18_colab_first_golden_host_memory_locked.py`
  - artifact-order assertions use the same concrete invocation marker.
  - source-presence checks remain intact and continue to prove the workflow contains the required tool.

### Added

- `docs/PHASE18_CHANGESET_168_HOST_MEMORY_WORKFLOW_REGRESSION_REPAIR.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_168.md`

### Deleted

- Nothing.

## Safety / policy invariants preserved

This change does not alter generation, factual, identity, sentiment, neutrality, cost, semantic, geometry, quality, branding, typography, or publication logic.

The following remain unchanged and fail-closed:

- Fact Lock and source consensus;
- Entity/Identity Verification;
- Sentiment/Neutrality and loser-respect policy;
- `$0-local` execution only;
- native BF16 requirement;
- total/live-free VRAM qualification;
- host-memory qualification;
- safe FLUX offload qualification;
- immutable Candidate/request/seed/canvas/SHA locks;
- generated text/branding/exact-fact/entity-mark/sport-geometry exclusion;
- Qwen `BASE_SCENE` and `HYBRID_SURFACE` semantic inspection;
- deterministic football geometry and integrity replay;
- Golden `8.5 minimum / 9.0+ elite` thresholds;
- Exact Brand and Typography integrity;
- SemanticPublicationGate and final publication readiness.

## Testing

The failure from run `32944740034` was diagnosed from the actual GitHub Actions job log. The code fix was committed as `b924880b43907a5e6333d3db6a56805d9a823e93`.

A new Story Intelligence verification run is expected from this branch update. Do not claim CI-green status until that run completes successfully.

## Remaining blocker toward first genuine Golden PNG

No genuine new Golden Hybrid v5 PNG is claimed in this change set.

The external blocker remains a compatible execution host that proves all of the following at runtime:

- NVIDIA CUDA;
- native BF16;
- sufficient total and live-free VRAM;
- sufficient live system RAM;
- safe Diffusers offload path;
- required local model/runtime readiness;
- `$0-local` execution.

Once such a host is available, the canonical path remains Candidate 1 only, followed by provenance replay, `BASE_SCENE`, deterministic football Hybrid composition, `HYBRID_SURFACE`, sealed human review, and Golden 8.5/9.0 review before any Seeds 2–4 authorization.
