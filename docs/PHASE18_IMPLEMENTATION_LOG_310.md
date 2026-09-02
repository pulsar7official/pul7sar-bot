# Phase 18 Implementation Log — CS310

## Baseline

- Working branch: `phase18/story-intelligence` only.
- Baseline SHA: `bd188ed17b179abffd560a8252b1af10438b3a2f` (CS309 terminal-green baseline).
- `main` was read-only and was not modified, merged, rebased, reset, or force-updated by CS310.
- Observed `main` SHA during this change set: `f8c7c703a2528838425193979a40b0abca8493af`.

## Review performed before modification

The downstream path was reviewed from CS309/CS284 SemanticPublicationGate execution through CS285 Genuine Golden materialization and CS286 publication readiness.

CS285 already imported `CS284_SCHEMA` dynamically, so the CS309 upgrade of CS284 to schema v2 did not itself create a schema-compatibility blocker. CS285 also already re-verified CS284, re-opened the exact composed PNG, validated the PNG container and CRCs, wrote the Golden PNG byte-for-byte, and kept `publication_ready=false`.

The proven gap was narrower and downstream-relevant: the CS285 verifier did not re-bind all metadata later consumed by CS286 to the exact verified CS284 state. A CS285 receipt with the exact valid CS284 source and byte-identical PNGs could have its `generation_context`, `weighted_score`, `quality_tier`, or materialization policy changed and its content digest recomputed. CS286 then copies those fields into its final `publication_ready=true` receipt.

## Modified

### `engine/intelligence/qwen_image_genuine_golden_materialization.py`

- Added canonical `MATERIALIZATION_POLICY`.
- Added `_require_materialization_receipt_matches_cs284()`.
- CS285 verification now re-confirms the CS284 schema.
- CS285 verification now requires exact CS284-derived equality for:
  - `story_snapshot_sha256`;
  - `source_composed_candidate_png`;
  - `generation_context`;
  - `weighted_score`;
  - `quality_tier`.
- CS285 verification now requires exact canonical materialization policy equality.
- The builder now emits the same canonical policy constant used by the verifier.
- Existing CS284 receipt binding, SemanticPublicationGate authority checks, PNG structural/CRC validation, source/Golden byte identity, Genuine-Golden authority, and `publication_ready=false` boundary remain intact.

### `tests/test_phase18_qwen_image_genuine_golden_materialization.py`

- Expanded the CS284 fixture with the metadata that CS285 legitimately derives from it.
- Added an exact-lineage acceptance regression.
- Added rejection regressions for:
  - generation-context drift;
  - weighted-score drift;
  - quality-tier drift;
  - materialization-policy drift.
- Preserved existing PNG-integrity and semantic-publication-authority regressions.

## Added

1. `docs/PHASE18_CHANGESET_310_GENUINE_GOLDEN_METADATA_LINEAGE.md`
2. `docs/PHASE18_IMPLEMENTATION_LOG_310.md`

## Deleted

- Nothing.

## Commits before this log

- `08ae8065e5951a9b39c0c7e2d765645965f08e78` — bind CS285 materialization metadata to exact CS284 state.
- `eb098be39b0bfa4ac7e6efb66cd40c3f683a4333` — add CS310 lineage-drift regressions.
- `d89b6e7ecef25de085bc025a2a34b13c9ab30e09` — add CS310 contract documentation.

## Authority and gate preservation

CS310 does not alter any approval score or threshold and does not grant new image-generation, semantic, human-review, publication, or pixel-edit authority.

Preserved unchanged:

- factual/freshness locks;
- entity/identity verification;
- sentiment neutrality and loser-respect;
- `$0-local`, offline, and local-files-only constraints;
- Semantic Base QA and Generated-Layer QA;
- composition and post-composition QA;
- Golden visual-quality adjudication;
- Human Visual Review;
- exact Brand/Typography review;
- Final Composed Approval;
- Final Semantic Approval;
- repository `SemanticPublicationGate`;
- exact-byte Genuine Golden materialization;
- CS286 as the separate final publication-readiness authority.

CS285 still cannot create pixels. It may only materialize exact already-approved composed bytes after a real CS284 `semantic_publication_allowed=true` result. Its receipt still records `publication_ready=false`.

## Testing state

Focused source-level regressions were added in the repository test suite. GitHub Actions is expected to execute automatically on the CS310 branch HEAD. A terminal-green result must not be claimed until the workflow completes successfully on a commit containing the production and regression changes.

## Genuine Golden runtime blocker

No production Genuine Golden PNG is claimed by CS310.

The current execution environment still requires a compatible zero-cost host that simultaneously provides NVIDIA CUDA, CUDA-enabled PyTorch, native BF16 support, the approved compatible QwenImagePipeline/Diffusers runtime, the exact approved already-local Qwen snapshot, sequential CPU offload behavior, and sufficient live VRAM/system RAM for real model loading and inference.

Without genuine upstream Qwen-Image inference, there is no honest production canonical candidate to carry through the factual, identity, sentiment, semantic, visual-quality, human, brand, SemanticPublicationGate, CS285 materialization, and CS286 readiness chain.

## Remaining path

1. Obtain genuine zero-cost CUDA/BF16 Qwen-Image execution with the approved local model/runtime contract.
2. Generate the real canonical candidate and carry it through all existing byte/factual/identity/sentiment/semantic/composition/quality/human/brand gates.
3. Execute CS284 v2 and require real `semantic_publication_allowed=true` on the exact production composed PNG.
4. Execute hardened CS285 to materialize those exact approved bytes as `genuine_golden_visual.png`.
5. Execute CS286 to grant final publication-readiness evidence without modifying pixels or publishing externally.
