# Phase 18 Change Set 273 — Composed Candidate Hybrid-Surface Semantic QA

## Purpose

Change Set 273 advances the first genuine Golden Visual path from exact composed-byte admission (CS272) into post-composition semantic inspection without weakening any existing authority boundary.

CS273 consumes the exact `composed_candidate.png` admitted by CS272 and reuses the repository's already-pinned `Qwen25VLSemanticInspector` with `SemanticInspectionStage.HYBRID_SURFACE`. It then evaluates that verdict through the existing `SemanticVisualVerdictGate` and `SemanticLayerEvidenceAdapter`.

This is intentionally not a Golden gate, Human Review gate, identity recognizer, or publication gate.

## Required upstream state

CS273 accepts only a CS272 receipt that re-verifies successfully and still proves:

- `composition_executed = true`
- `composed_candidate_bytes_admitted_for_post_composition_qa = true`
- `composed_visual_approved = false`
- `semantic_approved = false`
- `human_visual_review_approved = false`
- `genuine_golden_png_created = false`
- `golden_quality_approved = false`
- `publication_ready = false`

The exact CS272 receipt and the exact composed PNG are byte-bound to the CS273 receipt. Symlinks, repository escapes, and byte drift fail closed.

## Existing semantic stack reused

CS273 does not introduce a parallel vision policy. It reuses:

- pinned model: `Qwen/Qwen2.5-VL-3B-Instruct` through the existing approved revision registry;
- existing verifier identity from `qwen25_vl_inspector.py`;
- `SemanticInspectionStage.HYBRID_SURFACE`;
- `SemanticVisualVerdictGate`;
- `SemanticLayerEvidenceAdapter`;
- existing 0.85 minimum-confidence convention.

The HYBRID_SURFACE stage exists specifically for the post-deterministic-composition image. It checks that final sport geometry has plausible proportions, perspective and physical integration, while rejecting surviving generated/pseudo text, generated platform branding, invented marks, generated exact-number graphics, conflicting generated sport geometry, multi-panel scenes, severe defects, or unusable framing.

## Required post-composition checks

CS273 requires all of the following to be inspected at or above the minimum confidence and to pass:

- readable generated/pseudo text absence;
- generated platform-brand absence;
- fake entity-mark absence;
- single-scene integrity;
- severe-defect absence;
- usable subject/focal framing;
- sport-geometry alignment;
- generated exact-number absence;
- conflicting generated sport-geometry absence.

Missing/not-inspected evidence is never treated as clean evidence.

## Identity boundary

The current Qwen2.5-VL inspector deliberately returns no pixel-identity approval. CS273 therefore sets `identity_approval_in_scope = false` and does not manufacture an identity verdict.

Any human identity authority already required upstream remains governed by the dedicated CS265–CS267 identity path. Post-composition semantic success cannot substitute for that evidence.

## Authority granted

A successful run may set only:

- `semantic_inspection_executed = true`
- `hybrid_surface_semantic_qa_approved = true`

It must keep all broad downstream authorities closed:

- `composed_visual_approved = false`
- `semantic_approved = false`
- `human_visual_review_approved = false`
- `genuine_golden_png_created = false`
- `golden_quality_approved = false`
- `publication_ready = false`

This prevents one automated semantic inspector from becoming a shortcut around Human Review, Golden scoring, exact brand/typography verification, or `SemanticPublicationGate`.

## Verification behavior

The verifier reopens and checks:

1. the CS273 receipt digest;
2. the exact CS272 receipt bytes;
3. the CS272 receipt's own internal receipt digest through its verifier;
4. story binding;
5. the exact composed PNG binding and bytes;
6. pinned model ID, pinned revision, verifier ID, stage and minimum confidence;
7. normalized semantic verdict fields;
8. recomputed semantic-gate decision;
9. recomputed semantic-layer evidence;
10. the absence of premature downstream authority.

## Tests

Regression coverage includes:

- clean HYBRID_SURFACE pass without authority escalation;
- sport-geometry alignment failure;
- confidence below 0.85;
- surviving generated-text evidence;
- composed-PNG byte drift;
- CS272 receipt byte drift;
- premature Golden authority;
- semantic-verifier identity drift;
- existing-output-directory reuse.

Synthetic PNG bytes in tests are control-plane fixtures only. They are not Qwen outputs, production visuals, or Golden Visuals.

## Remaining path

CS273 removes the semantic gap immediately after composition. A genuine production path still requires a compatible zero-cost CUDA/BF16 host to execute the earlier Qwen-Image generation boundary, followed by the existing identity requirements where applicable, deterministic composition, CS272/CS273, then byte-bound Visual Critic, Human Review, Golden thresholding, exact Brand/Typography verification, and `SemanticPublicationGate`.
