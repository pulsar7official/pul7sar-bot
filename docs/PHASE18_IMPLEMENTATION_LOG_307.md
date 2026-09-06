# Phase 18 Implementation Log 307 — Exact Golden Adjudication Lineage

## Scope

Branch: `phase18/story-intelligence` only.

`main` is read-only for this change set and was not modified, merged, rebased, or force-updated.

Starting HEAD: `ea308326fe8ab8f349bfb7b9e317e7b24a387828` (terminal-green CS306 repair).

## Review performed before writing

The downstream audit continued from CS268 through the first composed-candidate Golden-quality authority edge.

CS269 deterministic composition request, CS270 composition execution preflight, CS271 one-shot composition execution, CS272 composed-candidate byte admission, CS273 HYBRID_SURFACE semantic QA, CS274 visual-quality review request, and CS275 visual-quality evidence admission each re-open/re-verify their exact immediate predecessor and exact candidate/composed bytes. No independent multi-receipt substitution gap was found in those single-source transitions.

The first concrete multi-source gap was CS276 Golden Quality Adjudication, which independently accepted CS263 + CS272 + CS275.

Two production defects were confirmed:

1. **Legacy CS263 contract incompatibility.** CS276 still required `inference_executed`, top-level `seed`, and `source_cs262_receipt`, while current CS303 sealed admission v2 exposes `genuine_canonical_inference_executed`, `handoff_sealed`, `candidate_bytes_admitted_for_post_generation_qa`, `source_canonical_inference_receipt`, and `inference_settings`. A genuine current candidate would therefore be blocked at Golden adjudication despite passing upstream gates.
2. **Cross-run provenance substitution.** CS276 verified the three receipts independently and compared story/PNG bindings, but did not prove that the supplied CS263 was the exact admission embedded in the CS272 lineage or that supplied CS272 was the exact receipt embedded in the CS275 lineage.

## Added

- `docs/PHASE18_CHANGESET_307_EXACT_GOLDEN_ADJUDICATION_LINEAGE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_307.md`

## Modified

- `engine/intelligence/qwen_image_composed_candidate_golden_quality_adjudication.py`
- `tests/test_phase18_qwen_image_composed_candidate_golden_quality_adjudication.py`

Production changes:

1. Upgraded CS276 schema to `pul7sar-phase18-qwen-image-composed-candidate-golden-quality-adjudication-v2`.
2. Replaced legacy CS263 authority requirements with the current CS303 sealed-admission requirements.
3. Added mandatory `$0-local`, `network_allowed=false`, and `local_files_only=true` checks at Golden adjudication.
4. Replaced legacy `source_cs262_receipt` generation context with `source_canonical_inference_receipt`.
5. Replaced legacy top-level seed with the sealed `inference_settings.seed`.
6. Added exact-lineage replay from CS272 through CS271 -> CS270 -> CS269 -> CS268 -> CS264 -> exact CS303 candidate admission.
7. Added exact-lineage replay from CS275 through CS274 -> CS273 -> exact CS272 receipt.
8. Added path + SHA-256 + byte-size + receipt-digest equality checks between supplied and lineage-derived receipts.
9. Applied the lineage checks both while building and while verifying CS276 receipts.
10. Kept the existing `GoldenVisualQualitySelector`, score fields, blocker fields, thresholds and approval semantics unchanged.

Test changes:

11. Migrated CS276 fixtures from the pre-CS303 admission shape to current sealed-admission v2 fields.
12. Added regression coverage for legacy authority rejection.
13. Added regression coverage for zero-cost/local-only enforcement.
14. Added regression coverage for CS263 -> CS272 cross-run substitution rejection.
15. Added regression coverage for CS272 -> CS275 cross-run substitution rejection.
16. Preserved blocker fail-closed behavior and downstream authority checks.

## Deleted

None.

## Safety / authority preservation

No factual, identity, sentiment, loser-respect, semantic-publication, visual-quality, Human Review, brand/typography or publication gate was weakened.

CS276 may set only `golden_quality_approved` according to the existing selector. It still cannot set:

- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `publication_ready`

The human review and final semantic/publication chain remains mandatory downstream.

## Testing status

The code-bearing CS307 HEAD `95b94d80e378c681219466e4806afb25d38d65e4` completed `Phase 18 Story Intelligence Verification` run `33511031031` / run number `4529` with `completed / success`.

Successful steps included:

- `Syntax and discover validation`;
- completion and production isolation;
- visual-study handoff build and verification;
- cross-platform composition matrix build and publication-block verification;
- project-native editorial visual study;
- adaptive/self-contained brand verification;
- Golden editorial v6 build and verification;
- legacy-logo non-canonical assertion;
- all declared artifact uploads.

The other nine visible Phase 18 workflows on the same code-bearing HEAD also completed successfully. No production enforcement was relaxed to obtain this result.

This implementation-log update is documentation-only and records the already completed verification; it does not alter executable code, schemas, tests, thresholds, or authority.

## Genuine PNG execution status

CS307 is control-plane/provenance work. It does not constitute Qwen model loading or visual inference.

The first genuine Golden Visual still requires a compatible zero-cost host with NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, the CS260-authorized compatible QwenImagePipeline/Diffusers runtime, sequential CPU offload, the exact approved already-local Qwen snapshot, and sufficient RAM/VRAM demonstrated by a real model load and inference.

No `canonical_candidate.png`, composed production PNG, or Genuine Golden PNG is claimed by this change set unless those real execution steps occur and all downstream gates pass.
