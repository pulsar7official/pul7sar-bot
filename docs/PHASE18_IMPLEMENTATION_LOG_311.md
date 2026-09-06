# Phase 18 Implementation Log 311 — Closed-World Final Publication Authority

## Scope

Branch: `phase18/story-intelligence` only.

Starting HEAD: `626e6ccfd5d9fc9a56c9de06fdcaff393e24df16` (CS310).

`main` was treated as read-only. No merge, rebase, reset, force-update, file write, or other mutation was performed against `main`.

## Audit result

The post-CS310 audit inspected CS286 (`qwen_image_genuine_golden_publication_readiness.py`), the final authority that may set `publication_ready=true` after a verified CS285 Genuine Golden materialization.

CS286 already had strong upstream lineage behavior:

- it binds and re-opens the CS285 receipt from the repository;
- it calls `verify_genuine_golden_materialization()`;
- it validates the CS285 schema and required authority bits;
- it checks the embedded CS285 receipt SHA;
- it re-opens the exact composed source PNG and Genuine Golden PNG;
- it enforces byte identity and validates PNG dimensions;
- during verification it re-derives story SHA, source/golden PNG bindings, dimensions, generation context, weighted score, quality tier, and approval states from the verified CS285 receipt.

Therefore no duplicate lineage wrapper was added.

### Proven gap

The CS286 verifier accepted required fields/policy values but did not reject unknown fields. A receipt could therefore be modified by adding an undeclared top-level field or undeclared policy key and then recomputing `receipt_sha256`; the old verifier would accept it if all required values remained intact.

Because CS286 is the final `publication_ready=true` authority, unknown authority-looking keys create an avoidable semantic-interpretation surface for any later consumer even though they do not change the canonical PUL7SAR decision logic itself.

## Code changes

### Modified

`engine/intelligence/qwen_image_genuine_golden_publication_readiness.py`

- Added `PUBLICATION_POLICY` as the single canonical policy map used by build and verify paths.
- Added `PUBLICATION_RECEIPT_FIELDS` as the exact accepted CS286 receipt key set.
- Added `_require_exact_publication_envelope()`.
- The helper rejects both missing and additional top-level receipt fields.
- The helper requires the policy map to equal the canonical policy exactly; unknown policy keys and weakened values are rejected.
- The builder now emits `dict(PUBLICATION_POLICY)` instead of constructing a separate literal.
- The verifier performs the exact-envelope check after schema/status/digest validation and before consuming publication authority.
- Existing exact CS285 replay, byte identity, PNG validation, and state re-derivation remain intact.

`tests/test_phase18_qwen_image_genuine_golden_publication_readiness.py`

- Added exact-envelope acceptance coverage.
- Added unknown top-level authority-field rejection.
- Added missing canonical field rejection.
- Added unknown policy authority-key rejection.
- Added weakened canonical policy rejection.
- Preserved the existing CS285 authority and repository-bound output tests.

### Added

- `docs/PHASE18_CHANGESET_311_CLOSED_WORLD_FINAL_PUBLICATION_AUTHORITY.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_311.md`

### Deleted

None.

## Authority boundaries preserved

CS311 does not change the conditions that produce a valid canonical final-readiness receipt. It narrows what the verifier accepts.

It does not weaken or bypass:

- factual/freshness locks;
- entity/identity verification;
- sentiment neutrality and loser-respect constraints;
- `$0-local`, offline, and local-files-only execution contracts;
- Semantic Base QA or Generated-Layer QA;
- composition/post-composition QA;
- Golden Visual Quality adjudication;
- Human Visual Review;
- Exact Brand/Typography and presentation evidence;
- Final Composed Visual Approval;
- Final Semantic Approval;
- `SemanticPublicationGate` execution;
- exact-byte Genuine Golden materialization.

CS286 still has no publication side effect. `publication_ready=true` remains a readiness authority only.

## Commits

- `e3e0d6a9a48bff2d67f1efa9e9a781b614c6a77a` — harden CS286 final publication authority envelope.
- `960fdfb3214b8c27a2dd1062cd7e03ea1090ed20` — add closed-world CS286 regressions.
- `0bcdd9541a5991cde3d8aa7e038077b7c445e923` — document CS311 contract.
- implementation-log commit: this document commit.

## Testing

CS310 was confirmed terminal-green before CS311 work began.

CS311 GitHub Actions status must be evaluated on the final CS311 HEAD. Do not claim terminal-green until the workflow for that exact code lineage completes successfully.

## Genuine Golden execution status

No Qwen image inference, canonical candidate, composed production PNG, or Genuine Golden PNG is claimed by this change set.

The current execution environment must still be checked for the required genuine-generation runtime. A real Golden Visual remains blocked if the host does not provide compatible NVIDIA CUDA execution, CUDA-enabled PyTorch, native BF16 support, the authorized QwenImagePipeline/Diffusers stack, the exact approved already-local Qwen snapshot, sequential CPU offload support, and sufficient RAM/VRAM demonstrated by a real model load and inference.

## Remaining gap

After CS311, the final post-materialization readiness envelope is closed-world and exact-lineage-derived. The primary remaining gap to the first Genuine Golden Visual is no longer a CS286 provenance ambiguity; it is genuine upstream image inference on an authorized compatible zero-cost runtime, followed by successful execution of the already-preserved QA/approval chain through CS285 and CS286.
