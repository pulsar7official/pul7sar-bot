# Phase 18 Implementation Log 377 — CS347 Semantic Publication Request Snapshot Lineage

## Branch safety

Target branch: `phase18/story-intelligence` only.
Starting branch HEAD: `f38537dd51aeb35fda2143e105f4836df07dbc75`.
`main` was not modified, merged, rebased, reset, force-updated, or otherwise written.

## What changed

### Modified

1. `engine/intelligence/qwen_image_final_semantic_approval_to_semantic_publication_execution_request.py`
   - Raised CS347 schema from v1 to v2.
   - Added the five-field exact Qwen generator snapshot lineage.
   - Added strict snapshot shape/verification checks.
   - Added field-by-field snapshot comparison against fresh CS346 replay during verification.
   - Requires verified snapshot lineage before CS283 request creation.
   - Preserves independent SemanticPublicationGate authority and all false downstream authority states.

2. `tests/test_phase18_qwen_final_semantic_approval_to_semantic_publication_execution_request.py`
   - Updated CS346 fixture with real snapshot-lineage fields.
   - Added successful five-field propagation assertions.
   - Added fail-before-CS283 regression for unverified snapshot inventory.
   - Added rehashed snapshot-digest tamper regression against fresh CS346 replay.
   - Preserved tests for final semantic approval, premature publication authority, CS282 receipt drift, and forbidden shortcuts.

### Added

- `docs/PHASE18_CHANGESET_377_CS347_SEMANTIC_PUBLICATION_REQUEST_SNAPSHOT_LINEAGE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_377.md`

### Deleted

None.

### Dependencies

None added or changed.

## Commits

Production hardening commit: `51bacca9f403f4b614d3f21c91525a8e3760f651`.
Exact code-and-test-bearing commit: `0bce98bcd0f3d0d34d2dd13ac5e2906bfaf78c22`.
Changeset documentation commit: `3fe8d12be4f37ecfd00b9a0d56cf29d885acddb6`.

## Gate preservation

CS347 still only requests semantic-publication execution. It does not execute SemanticPublicationGate and cannot mark semantic publication allowed. It preserves:

- factual/freshness and story binding inherited from the verified upstream chain;
- Entity/Identity gates;
- sentiment neutrality / loser-respect gates;
- zero-cost policy;
- semantic and visual-quality review lineage;
- Human Visual Review;
- Final Presentation / Brand / Typography;
- Final Composed and Final Semantic approvals;
- independent SemanticPublicationGate authority;
- no Genuine Golden materialization before the independent gate;
- no publication readiness or authoritative state here.

Mandatory downstream states remain:

- `semantic_publication_gate_executed=false`
- `semantic_publication_allowed=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`
- `authoritative=false`

## Tests / CI

The targeted regressions are committed at `0bce98bcd0f3d0d34d2dd13ac5e2906bfaf78c22`.

Terminal result: `Phase 18 Story Intelligence Verification` run `34385536423`, run number `5265`, completed successfully on the exact code-and-test-bearing SHA `0bce98bcd0f3d0d34d2dd13ac5e2906bfaf78c22` on 2026-09-09. CS377 is therefore terminal-green.

## Genuine Golden blocker

No Genuine Qwen-Image PNG was fabricated or claimed. Real materialization still requires a compatible zero-cost CUDA execution host and the already-approved local pinned runtime/assets. CPU-only execution is not treated as equivalent evidence.

## Next proven boundary

The branch-local tree shows the next existing continuation after CS347/CS283: `qwen_image_semantic_publication_request_to_gate_execution.py`, followed by `qwen_image_semantic_publication_gate_to_genuine_golden_materialization.py`. Any subsequent hardening must inspect those existing contracts directly rather than introducing a parallel gate.
