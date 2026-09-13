# Phase 18 Implementation Log — CS285

## Baseline

- Working branch: `phase18/story-intelligence`
- Baseline SHA: `2d72dd3c209d09bfa5bd8b588c59cf42fb5b25c7`
- Baseline CS284 `verify-story-intelligence`: completed / success.
- `main` was read only and was not modified, merged, rebased, or force-updated by this change set.
- Observed `main` SHA during this change set: `368e8e07a6c5926a770a75f8fc0c506143845cf2`.

## Goal

Materially reduce the remaining gap to the first genuine Golden Visual by creating the first downstream authority that can actually materialize a `genuine_golden_visual.png`, but only from the exact already-approved composed bytes after a real CS284 repository `SemanticPublicationGate` decision returns `semantic_publication_allowed=true`.

## Added

1. `engine/intelligence/qwen_image_genuine_golden_materialization.py`
   - Re-verifies CS284 and requires real semantic-publication allowance.
   - Rejects semantic-publication failures and premature Golden/publication state.
   - Re-opens the exact repository-bound composed PNG.
   - Validates PNG signature, chunk framing, chunk CRCs, IHDR dimensions, terminal IEND, and absence of trailing bytes.
   - Writes `genuine_golden_visual.png` as an exact byte-for-byte copy without decoding/re-encoding or pixel mutation.
   - Verifies source/materialized SHA-256 and byte-size identity.
   - Emits an immutable materialization receipt with `genuine_golden_png_created=true` while keeping `publication_ready=false`.
   - Verifier re-opens CS284, source PNG, and materialized PNG and fails on any byte or authority drift.

2. `tests/test_phase18_qwen_image_genuine_golden_materialization.py`
   - Valid PNG container/dimension regression.
   - CRC corruption rejection.
   - Non-PNG payload rejection.
   - Missing CS284 publication allowance rejection.
   - CS284 failure-state rejection.
   - Premature Golden/publication-state rejection.

3. `tools/phase18_materialize_genuine_golden_visual.py`
   - Build/verify CLI only.
   - No approval, allowed, Golden, publication-ready, image-substitution, or pixel-edit override argument exists.

4. `docs/PHASE18_CHANGESET_285_GENUINE_GOLDEN_MATERIALIZATION.md`
   - Exact-byte Genuine-Golden materialization contract and authority boundaries.

5. `docs/PHASE18_IMPLEMENTATION_LOG_285.md`
   - This implementation record.

## Modified

- No pre-existing production, policy, gate, workflow, or test file was modified.

## Deleted

- Nothing.

## Commits before this log

- `6a4bc87bf6946313c6f1e565c2cab265780ae2bd` — CS285 Genuine Golden materialization authority.
- `27ee05b29158450698a7e477707743c48ff92946` — CS285 regressions.
- `7293337b09e6a2c8cf128cc2cf30ce30565ab52a` — CS285 CLI.
- `1a5f6ba55f015e8b8d6f79051c0bbf60358e5910` — CS285 contract documentation.

## Preserved gates

CS285 does not modify or bypass factual locks, entity/identity verification, sentiment neutrality and loser-respect rules, zero-cost constraints, Golden-quality adjudication, human visual review, exact brand/typography review, final composed approval, final semantic approval, or `SemanticPublicationGate`.

The stage cannot invent `semantic_publication_allowed=true`; it accepts that authority only from a successfully re-verified CS284 receipt whose decision was produced by the repository gate itself.

CS285 performs no image generation or pixel transformation. The Golden artifact must be byte-identical to the CS284-approved composed candidate.

Even after real materialization, CS285 records:

- `genuine_golden_png_created=true`
- `publication_ready=false`

Publication readiness therefore remains a separate final authority.

## Testing state

Focused regression coverage was added for PNG structural integrity and CS284 authority boundaries. GitHub Actions is expected to execute automatically on the final CS285 SHA. A terminal success is not claimed in this log until observed.

## Genuine Golden execution blocker

No production Genuine Golden PNG is claimed in this change set. The current automation runtime does not expose a compatible NVIDIA CUDA/BF16 GPU for genuine CS262 Qwen-Image inference. The exact upstream runtime blocker remains a zero-cost host that simultaneously provides compatible NVIDIA CUDA, native BF16 support, sufficient live VRAM/system RAM, the pinned Qwen-Image revision, a compatible `QwenImagePipeline`, and the required sequential CPU offload behavior.

Because no genuine CS262 production candidate can be generated in this runtime, there is no honest production CS284 `semantic_publication_allowed=true` receipt to feed into CS285. Tests use only synthetic control-plane PNG bytes and never claim a production Golden artifact.

## Remaining path

1. Obtain genuine CS262 Qwen-Image inference on a compatible zero-cost GPU host.
2. Carry the real candidate through the existing byte/factual/identity/sentiment/semantic/composition/quality/human/brand/typography chain.
3. Execute CS284 on the exact production composed PNG and require `semantic_publication_allowed=true`.
4. Execute CS285 to materialize the exact production bytes as `genuine_golden_visual.png` and produce Genuine-Golden evidence.
5. Add/execute a final publication-readiness authority that consumes the verified CS285 receipt without altering image bytes.
