# Phase 18 Implementation Log 276 — Authentic-Context Golden Quality Adjudication

## Branch safety baseline

- Repository: `pulsar7official/pul7sar-bot`
- Write branch: `phase18/story-intelligence` only.
- Reviewed starting branch SHA: `a7e1969a4c5ce42dff5e60486f5f018dd8832090`.
- `main` was read only. During this implementation its observed ref was `3e1ced144ad677779888688939d3f6dc33ca38f7`.
- No merge, rebase, force update, file write, or ref update was directed at `main`.

## Objective

Close the provenance gap identified after CS275: the existing `GoldenVisualEvaluation` requires `request_id` and `seed`, while CS275 owns only the reviewed score/blocker evidence. CS276 must invoke the existing `GoldenVisualQualitySelector` without caller-supplied or fabricated generation context.

Review of CS262/CS263 proved that the genuine one-shot inference receipt records `seed`, and CS263 re-verifies that receipt and carries both the seed and exact CS262 receipt digest. Review of CS272 proved that it retains the exact source-candidate PNG binding used for composition. Therefore CS276 can prove that the generation seed belongs to the exact base candidate whose descendant composed PNG CS275 reviewed.

## Added

1. `engine/intelligence/qwen_image_composed_candidate_golden_quality_adjudication.py`
   - re-verifies CS263, CS272 and CS275;
   - requires one Story SHA across all three receipts;
   - matches the canonical source PNG across CS263/CS272 by repository path, SHA-256, byte size and dimensions;
   - matches the composed PNG across CS272/CS275 by the same exact byte/dimension identity;
   - obtains the seed only from reverified CS263->CS262 provenance;
   - derives `request_id` deterministically as `qwen-cs262-<exact CS262 receipt_sha256>` rather than accepting caller input;
   - reconstructs `GoldenVisualScores` and `GoldenVisualBlockers` from CS275 admitted evidence;
   - invokes the repository's existing `GoldenVisualQualitySelector` / `GoldenVisualEvaluation` without duplicating thresholds or weights;
   - records weighted score, active blockers, tier and selector result;
   - allows `golden_quality_approved` to reflect only the existing Golden selector result;
   - keeps Human Review, final semantic approval, composed-visual approval, Genuine Golden PNG creation and publication authority closed;
   - provides a verifier that reopens all bound source receipts and recomputes the selector verdict.

2. `tests/test_phase18_qwen_image_composed_candidate_golden_quality_adjudication.py`
   - approved/Elite path uses only proven CS262 request context and seed;
   - hard blocker cannot be rescued by high scores;
   - base-candidate lineage drift fails closed;
   - composed-candidate lineage drift fails closed;
   - source-receipt byte tampering invalidates verification;
   - rehashed forged Golden verdict is rejected;
   - existing output directory is rejected.

3. `tools/phase18_adjudicate_composed_candidate_golden_quality.py`
   - build/verify CLI;
   - accepts only CS263/CS272/CS275 receipt paths and output path;
   - deliberately has no `--request-id`, `--seed`, score, blocker, or approval override input.

4. `docs/PHASE18_CHANGESET_276_COMPOSED_CANDIDATE_GOLDEN_QUALITY_ADJUDICATION.md`

5. `docs/PHASE18_IMPLEMENTATION_LOG_276.md`

## Modified during CS276 hardening

Only newly added CS276 files were modified.

- `engine/intelligence/qwen_image_composed_candidate_golden_quality_adjudication.py`
  - initial review found that a generic downstream-false tuple incorrectly expected the old CS263 schema to contain the later `composed_visual_approved` field;
  - hardened to stage-specific authority tuples matching the actual historical CS263, CS272 and CS275 schemas instead of retroactively imposing newer fields on older receipts.

- `tests/test_phase18_qwen_image_composed_candidate_golden_quality_adjudication.py`
  - aligned synthetic regression receipts with the actual CS275 authority schema, including explicit `visual_quality_review_approved=false`.

No pre-existing Fact Lock, Entity/Identity, Sentiment Neutrality, Zero-Cost, semantic/layer, inference, composition, Human Review, Golden threshold/weight, brand/typography, or SemanticPublicationGate implementation was changed.

## Deleted

None.

## Commits

- `cce6515c6d43fab6d2717f9aa22087a48ac0e82d` — initial CS276 adjudication engine.
- `6a0f1f50e81a8ee98633100f80b84353bbeff680` — CS276 regression coverage.
- `d6337ec5fe9eeb16461be649d24a019c476708da` — CS276 build/verify CLI.
- `b5e601d8fa121575a1f93d440b3c8862753a9bcd` — stage-specific authority-schema hardening.
- `93ee6cd8988e38d8d1c500466865046e05254274` — CS276 contract documentation.
- `d9978541af553b55b4b95d70d24e5af33589762d` — regression schema alignment.

## Authority after CS276

A valid CS276 receipt may truthfully report:

- `golden_quality_selector_executed=true`;
- `golden_quality_approved=true|false` according to the existing selector;
- `quality_tier=below_golden|golden|elite`.

It must still report:

- `composed_visual_approved=false`;
- `semantic_approved=false`;
- `human_visual_review_approved=false`;
- `genuine_golden_png_created=false`;
- `publication_ready=false`.

Thus even an Elite quality score cannot bypass independent Human Review, exact brand/typography work, final semantic/publication authority, or create a Genuine Golden PNG by declaration.

## Tests / CI

The CS276 unittest regression suite has been added. GitHub Actions is allowed to validate the repository-wide Phase 18 test surface after this log commit. No terminal CI success is claimed in this initial log until a completed successful run is observed on the executable CS276 state.

Synthetic PNG/file identities in unit tests are control-plane fixtures only. They are not claimed as Qwen inference or Golden pixels.

## Genuine GPU execution status

CS276 performs no GPU inference. No genuine candidate/composed/Golden PNG is created or claimed here. A real CS262 run remains a prerequisite for real production evidence to reach CS276.

The execution environment must still prove, together on one zero-cost host, NVIDIA CUDA, native BF16, sufficient live VRAM/system RAM, the exact pinned `Qwen/Qwen-Image-2512` revision, a compatible successful `QwenImagePipeline` load, and required sequential CPU offload. If those conditions are absent, genuine inference must remain blocked rather than fabricated.

## Remaining path

For a genuine candidate that passes CS276 Golden quality, the remaining independent promotion work is:

`CS276 Golden quality adjudication -> byte-bound Human Visual Review -> exact Brand/Typography verification -> final composed/semantic approval -> SemanticPublicationGate -> Genuine Golden PNG/publication authority`.

The next safe control-plane step is therefore to bind the existing Human Review contract to the exact CS276 adjudication and same composed PNG, while preserving rejection when Golden quality itself fails.
