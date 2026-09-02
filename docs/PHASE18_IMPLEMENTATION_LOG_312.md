# Phase 18 Implementation Log 312 — GPU Preflight Schema Alignment

## Branch isolation

- Target branch: `phase18/story-intelligence`
- Starting HEAD: `c728fb47ff45d51c07d07231612225c8ceacdaff`
- `main` observed independently at start: `f8c7c703a2528838425193979a40b0abca8493af`
- No write, merge, rebase, reset, force-update, or other mutation of `main` was performed.

## Review finding

The first-Golden execution surface contained a concrete pre-inference contract mismatch:

- `tools/phase18_preflight_semantic_gpu.py` emits `pul7sar-phase18-semantic-gpu-preflight-v2`.
- `tools/phase18_first_png.py` requires `pul7sar-phase18-semantic-gpu-preflight-v2`.
- `.github/workflows/phase18-gpu-smoke.yml` still required `pul7sar-phase18-semantic-gpu-preflight-v1`.

Because the workflow is intentionally fail-closed, a qualified CUDA/BF16 host could have produced a valid v2 semantic-preflight receipt and then been rejected by the stale workflow assertion before FLUX generation. This was an execution-readiness defect, not a reason to loosen the semantic preflight.

## Added

- `tests/test_phase18_semantic_gpu_preflight_schema_alignment.py`
- `docs/PHASE18_CHANGESET_312_GPU_PREFLIGHT_SCHEMA_ALIGNMENT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_312.md`

## Modified

- `.github/workflows/phase18-gpu-smoke.yml`
  - Changed only the semantic GPU preflight schema assertion from v1 to the authoritative v2 value.
- `tests/test_phase18_semantic_gpu_preflight_schema_alignment.py`
  - Repaired the regression after the first CS312 CI run showed that the workflow expresses the four fail-closed authority checks through a loop rather than four unrolled string expressions.
  - The repaired regression now asserts the exact four-field gate tuple plus the generic `is not False` predicate; no workflow behavior was weakened.

## Deleted

- Nothing.

## Regression coverage

The new regression requires all three execution surfaces to agree on the v2 schema:

1. semantic-preflight producer,
2. first-PNG orchestrator,
3. dedicated GPU smoke workflow.

It also explicitly rejects the stale v1 schema in the workflow and reasserts the self-hosted CUDA/BF16 runner, `$0-local`, and fail-closed generation/publication flags.

## Gate preservation

No factual/freshness, entity/identity, sentiment-neutrality, loser-respect, zero-cost, local/offline, generated-layer QA, composition QA, Golden-quality, Human Visual Review, Exact Brand/Typography, Final Composed, Final Semantic, SemanticPublicationGate, Genuine Golden materialization, or final publication-readiness authority was weakened or bypassed.

CS312 does not generate pixels and grants no publication authority. It only removes an obsolete workflow-side schema expectation so that a truly compatible host can reach the already-defined downstream gates.

## Testing status

### First CS312 CI attempt

`Phase 18 Story Intelligence Verification` run `33600927350` reached the full Phase 18 discovery suite and ran **1,961 tests**. All pre-existing GPU-smoke workflow tests passed, and the new producer/orchestrator/workflow v2-alignment regression passed. The only failure was the second newly-added CS312 regression, which searched for an unrolled literal `payload.get("publication_ready") is not False` even though the workflow correctly enforces the same rule with:

`for field in ("generation_authorized", "queue_mutated", "png_created", "publication_ready")`

followed by the generic fail-closed predicate.

This was a test-expression defect, not a production/workflow defect. The regression was repaired to assert the actual canonical loop contract. No production or workflow semantics changed as part of that repair.

Final CI status for the repaired code-bearing HEAD must only be recorded after GitHub reports a completed result.

## Remaining blocker to a genuine Golden PNG

No genuine Golden PNG is claimed by this change. Actual materialization remains contingent on a zero-cost compatible self-hosted environment that proves CUDA-enabled PyTorch, native BF16, approved model/runtime compatibility, the exact approved local model snapshots/cache contracts, and enough RAM/VRAM for genuine inference. If those execution requirements are absent, the correct behavior remains fail-closed with no placeholder PNG.
