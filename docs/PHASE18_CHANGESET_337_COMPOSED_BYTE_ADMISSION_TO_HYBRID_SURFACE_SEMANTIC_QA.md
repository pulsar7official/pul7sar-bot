# Phase 18 Change Set 337 — Composed-Byte Admission → Hybrid-Surface Semantic QA

## Purpose

CS337 closes the exact-lineage handoff between the production-composed byte
admission produced by CS336 and the existing CS273 HYBRID_SURFACE semantic QA.

It consumes one exact CS336 checkpoint, independently reverifies CS336, reopens
and independently reverifies the exact CS272 receipt selected by CS336, runs the
existing pinned CS273 semantic inspection against those exact composed PNG
bytes, independently reverifies CS273, and stops before CS274.

## Execution path

`CS336 exact checkpoint -> independent CS336 replay -> exact selected CS272 replay -> CS273 HYBRID_SURFACE semantic QA -> independent CS273 replay -> STOP`

A CS273 rejection is recorded as rejection evidence. It must not progress to
visual-quality review.

## Safety and authority boundaries

CS337:

- does not generate pixels;
- does not compose or alter pixels;
- does not request or execute CS274 visual-quality review;
- does not fabricate semantic verdicts;
- forces Hugging Face / Transformers / Datasets offline execution before CS273;
- fails closed when the exact pinned local semantic-verifier assets are absent;
- preserves exact Story, source-candidate, composed-PNG and CS272 receipt lineage;
- keeps global `semantic_approved=false` even when the scoped CS273
  `hybrid_surface_semantic_qa_approved=true`;
- grants no Human Review, Golden Quality, Genuine Golden, or publication authority.

The following remain false:

- `visual_quality_review_requested`
- `visual_quality_review_executed`
- `visual_quality_review_approved`
- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

The CS337 checkpoint is explicitly non-authoritative.

## Files

Added:

- `engine/intelligence/qwen_image_composed_byte_admission_to_hybrid_surface_semantic_qa.py`
- `tests/test_phase18_qwen_composed_byte_admission_to_hybrid_surface_semantic_qa.py`
- `tools/phase18_continue_composed_byte_admission_to_hybrid_surface_semantic_qa.py`
- `docs/PHASE18_CHANGESET_337_COMPOSED_BYTE_ADMISSION_TO_HYBRID_SURFACE_SEMANTIC_QA.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_337.md`

Modified existing production gates: none.

Deleted: none.

## Remaining gap

A genuine Golden Visual still requires a genuine Qwen-Image canonical candidate
from a compatible zero-cost CUDA/BF16 execution host, followed by the existing
post-CS273 visual-quality evidence/adjudication, Human Visual Review,
presentation/brand review, final composed and semantic approvals,
SemanticPublicationGate, CS285 Genuine Golden materialization and CS286
readiness.

CS337 deliberately does not advance to CS274; the next safe continuation must
consume only a CS337 semantic pass and preserve these authorities.
