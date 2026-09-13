# Phase 18 Change Set 275 — Composed Candidate Visual Quality Review Evidence

## Purpose
CS275 closes the gap between the byte-bound CS274 review request and the existing Golden Visual quality selector without fabricating Visual Critic scores.

## Contract
The external review JSON must bind the exact CS274 receipt and exact composed PNG and provide:
- schema `pul7sar-phase18-composed-candidate-visual-quality-external-review-v1`;
- story snapshot SHA-256;
- composed candidate PNG SHA-256;
- CS274 receipt SHA-256;
- `review_method = manual_visual_quality_review`;
- non-empty reviewer identity and notes;
- every `GoldenVisualScores` field;
- every `GoldenVisualBlockers` field.

Scores are validated by `GoldenVisualScores`, including the 0–10 bounds. Blockers must be explicit booleans. The weighted score and active blockers are derived from the existing quality contract, not supplied as trusted external conclusions.

## Authority boundary
A successful CS275 receipt means only that complete visual-quality evidence was admitted and bound to the correct bytes. It sets `visual_quality_review_executed=true` and `visual_quality_evidence_admitted=true`.

It deliberately keeps `visual_quality_review_approved`, `composed_visual_approved`, `semantic_approved`, `human_visual_review_approved`, `genuine_golden_png_created`, `golden_quality_approved`, and `publication_ready` false. Golden eligibility must be evaluated later by the existing `GoldenVisualQualitySelector`; Human Review and SemanticPublicationGate remain independent downstream authorities.

## Fail-closed properties
Verification reopens the CS274 request, composed PNG, and external evidence bytes. Any byte drift, story/candidate/request mismatch, incomplete score/blocker set, invalid score range, non-boolean blocker, or premature authority invalidates the receipt.

## GPU status
CS275 is control-plane only and does not claim Qwen-Image inference. A genuine Golden PNG still requires a compatible zero-cost CUDA/BF16 Qwen-Image runtime and the subsequent real generation/composition/review chain.
