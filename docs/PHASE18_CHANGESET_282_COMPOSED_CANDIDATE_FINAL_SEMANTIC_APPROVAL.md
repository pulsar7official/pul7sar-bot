# Phase 18 Change Set 282 — Composed Candidate Final Semantic Approval

CS282 grants final semantic authority to the exact composed PNG only after CS281 final composed-visual approval and the exact CS273 HYBRID_SURFACE semantic-QA receipt are re-verified against the same Story and byte-identical PNG.

## Authority boundary

CS282 may set `semantic_approved=true` while preserving `genuine_golden_png_created=false` and `publication_ready=false`. It does not execute, replace, weaken, or bypass `SemanticPublicationGate`.

## Required upstream evidence

- valid CS281 receipt;
- CS281 must prove composed visual, human review, final presentation, exact brand integrity, and typography integrity;
- exact CS273 receipt transitively bound by CS281;
- CS273 must prove composition execution, composed-byte admission, semantic inspection execution, and HYBRID_SURFACE semantic approval;
- Story SHA and exact PNG path/SHA-256/byte-size must match.

The final semantic receipt remains byte-bound to the same PNG. Any source-receipt or PNG byte drift fails closed.

## Preserved gates

The factual, identity, sentiment/loser-respect, zero-cost, visual-quality, human-review, exact-brand, typography, and composed-visual gates remain transitively required by the verified upstream chain. Publication remains independently governed by the existing `SemanticPublicationGate` and later Genuine Golden creation authority.

## Files

- `engine/intelligence/qwen_image_composed_candidate_final_semantic_approval.py`
- `tests/test_phase18_qwen_image_composed_candidate_final_semantic_approval.py`
- `tools/phase18_approve_composed_candidate_final_semantic.py`
- this document
- `docs/PHASE18_IMPLEMENTATION_LOG_282.md`
