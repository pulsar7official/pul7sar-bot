# Phase 18 Change Set 338 — Hybrid-Surface Semantic QA → Visual-Quality Review Request

## Purpose

CS338 closes the exact-lineage handoff between the CS337 semantic-QA checkpoint
and the existing CS274 Visual Quality Review Request.

It consumes one exact CS337 checkpoint, independently reverifies CS337, requires
that CS273 HYBRID_SURFACE semantic QA passed, reopens and independently
reverifies the exact CS273 receipt selected by CS337, invokes the existing CS274
request builder for those same composed PNG bytes, independently reverifies
CS274, and stops before CS275 Visual Quality Review Evidence.

## Execution path

`CS337 semantic pass -> independent CS337 replay -> exact selected CS273 replay -> CS274 Visual Quality Review Request -> independent CS274 replay -> STOP`

A CS337/CS273 semantic rejection cannot advance to CS274.

## Safety and authority boundaries

CS338:

- does not generate, compose, resize, or alter pixels;
- does not generate or infer Visual Critic scores;
- reuses the existing byte-bound Golden Visual Quality contract through CS274;
- requires the exact CS337-selected CS273 receipt and exact composed PNG bytes;
- does not execute CS275 visual-quality evidence;
- does not grant visual-quality approval merely because a review was requested;
- does not automate Human Review;
- does not grant global semantic, Golden, Genuine Golden, or publication authority;
- introduces no network or paid fallback.

Only `visual_quality_review_requested=true` is newly allowed. The following
remain false:

- `visual_quality_review_executed`
- `visual_quality_review_approved`
- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

The CS338 checkpoint is explicitly non-authoritative.

## Files

Added:

- `engine/intelligence/qwen_image_hybrid_surface_semantic_qa_to_visual_quality_review_request.py`
- `tests/test_phase18_qwen_hybrid_surface_semantic_qa_to_visual_quality_review_request.py`
- `tools/phase18_continue_hybrid_surface_semantic_qa_to_visual_quality_review_request.py`
- `docs/PHASE18_CHANGESET_338_HYBRID_SURFACE_SEMANTIC_QA_TO_VISUAL_QUALITY_REVIEW_REQUEST.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_338.md`

Modified existing production gates: none.

Deleted: none.

## Remaining gap

A genuine Golden Visual still requires a genuine Qwen-Image canonical candidate
from a compatible zero-cost CUDA/BF16 execution host. Once genuine composed
bytes reach CS338, the next safe continuation is CS275 genuine Visual Quality
Review Evidence, followed by CS276 Golden Quality Adjudication and the remaining
Human Review, presentation/brand, final composed, final semantic,
SemanticPublicationGate, CS285 Genuine Golden materialization, and CS286
readiness gates.
