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

The repository commits produced by this change are intended to be validated by the existing Phase 18 GitHub Actions verification suite plus the new static contract regression. Final CI status should be recorded only after GitHub reports a completed result for the code-bearing CS312 HEAD.

## Remaining blocker to a genuine Golden PNG

No genuine Golden PNG is claimed by this change. Actual materialization remains contingent on a zero-cost compatible self-hosted environment that proves CUDA-enabled PyTorch, native BF16, approved model/runtime compatibility, the exact approved local model snapshots/cache contracts, and enough RAM/VRAM for genuine inference. If those execution requirements are absent, the correct behavior remains fail-closed with no placeholder PNG.
