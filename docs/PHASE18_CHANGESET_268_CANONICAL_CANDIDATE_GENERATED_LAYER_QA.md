# Phase 18 Change Set 268 — Canonical Candidate Generated-Layer QA

## Purpose

CS268 closes the gap between byte-bound candidate semantic/identity evidence and the existing hybrid visual-layer ownership gate. It evaluates only the generated/base candidate layer. It does **not** claim that deterministic typography, scores/data, exact sport geometry, verified entity marks, PUL7SAR branding, final composition, visual-critic approval, human review, Golden quality, or publication readiness already exist.

## Inputs

CS268 re-verifies and byte-binds:

1. CS264 Canonical Candidate Semantic Base QA.
2. CS265 Canonical Candidate Identity Requirement.
3. CS267 Pixel Identity Review Evidence **only when CS265 says pixel identity review is required**.
4. The exact canonical candidate PNG bytes referenced by those receipts.

A human candidate fails closed if CS267 evidence is absent, rejected, byte-drifted, story-drifted, or candidate-drifted. A non-human candidate must not provide CS267 evidence and does not receive a fabricated `identity_approved=true` state.

## Existing Gate Reuse

CS268 reuses `engine.intelligence.visual_layer_qa.HybridLayerQualityGate`; it does not create a parallel leakage policy.

CS264 semantic-layer evidence is converted into the existing `LayerLeakageEvidence` fields:

- generated text
- generated PUL7SAR/platform brand
- generated exact numbers/data
- generated entity marks
- generated sport geometry
- generated unverified identity

For identity-sensitive human candidates, `generated_unverified_identity_detected` remains fail-closed until exact CS267 evidence is verified and approved.

## Conservative Base-Candidate Ownership Plan

The candidate-stage plan deliberately treats the model as owner only of the atmospheric/non-factual base. Exact sport geometry, exact numbers/data and typography remain deterministic. Exact entity marks and PUL7SAR branding remain verified assets. A human hero is accepted only as a verified asset or a separately identity-verified depiction.

This is intentionally conservative. CS264 already requires generated exact numbers and generated sport geometry to be absent, so CS268 cannot weaken those upstream restrictions.

## Authority

The only new positive authority is:

- `generated_layer_qa_approved=true` when the existing hybrid layer gate passes and any mandatory identity review has passed.

The following remain false:

- `composition_executed`
- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `golden_quality_approved`
- `publication_ready`

Therefore a CS268 pass is **not** a Golden Visual and is not publication authority.

## Fail-Closed Properties

- source receipts are repository-contained and byte-bound;
- candidate PNG is reopened and byte-verified;
- upstream receipt digests are replayed;
- human identity evidence is mandatory when CS265 requires it;
- unexpected CS267 evidence for a non-human candidate is rejected;
- the existing HybridLayerQualityGate is replayed during verification;
- output directories are single-write and cannot be silently overwritten;
- final-composition and publication authority stay closed.

## Next Boundary

After a genuine candidate passes CS268, the next safe boundary is deterministic/verified-layer composition using the project-native composition contracts, followed by composed-visual semantic QA, Visual Critic, human review, Golden scoring, exact brand/typography enforcement and SemanticPublicationGate.
