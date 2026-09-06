# Phase 18 Change Set 101 — Locked Pitch Semantic Review

## Purpose
Close the gap between Change Set 100's tamper-evident manual pitch-selection lock and the existing Golden visual-quality/publication gates. A locked pitch artifact must now pass a replayed HYBRID_SURFACE semantic/alignment review before any Golden-quality claim can be considered.

## Added
- `engine/intelligence/football_pitch_semantic_review.py`
  - Replays SHA-256 for the locked pitch PNG and requires equality with both the lock's `locked_png_sha256` and source-variant SHA.
  - Requires the selection lock to remain manual, integrity-proven, selection-only, and explicitly non-publication.
  - Requires all downstream factual, identity, sentiment, semantic-publication, Golden-quality, exact-brand, typography, and publication-readiness gates to remain unwaived.
  - Evaluates a normalized `SemanticVisualVerdict` with `SemanticVisualVerdictGate` at confidence >= 0.85.
  - Requires geometry alignment, exact-number absence, and absence of a second/conflicting generated sport-geometry layer.
  - Emits `FOOTBALL_PITCH_SEMANTIC_REVIEW_COMPLETE`, always `publication_ready=false` and `golden_quality_approved=false`.
- `tools/phase18_review_locked_pitch.py`
  - Phase-18-only CLI.
  - Requires Qwen runtime readiness before inference.
  - Runs Qwen with `SemanticInspectionStage.HYBRID_SURFACE` against the locked PNG.
  - Persists the normalized semantic/alignment review receipt.
  - Returns non-zero when semantic approval fails.
- `tests/test_phase18_football_pitch_semantic_review.py`
  - Clean locked artifact can pass the semantic/alignment stage without becoming publication-ready.
  - Bad pitch alignment fails closed.
  - Missing conflicting-geometry inspection fails closed.
  - Locked-PNG byte tampering is rejected before a semantic claim.
  - Downstream gate lists cannot be weakened.

## Modified
- No pre-existing runtime, generation prompt, model control, factual gate, identity gate, neutrality gate, quality threshold, or publication gate was modified.

## Deleted
- Nothing.

## Safety / quality invariants
- Target branch only: `phase18/story-intelligence`.
- `main` and `main.py` remain untouched.
- FLUX.2 Klein 4B, BF16, seeds, canvases, and `$0-local` remain unchanged.
- Fact Lock, identity verification, sentiment/neutrality, SemanticPublicationGate, Golden 8.5/9.0 thresholds, exact brand integrity, typography integrity, and final publication readiness remain mandatory.
- `semantic_approved=true` is not a Golden-quality or publication claim.
- No paid provider, secret, model weights, font files, fake PNG, or fabricated benchmark is introduced.

## Why this materially reduces the remaining GPU gap
Once a genuine Candidate 1 exists and a human picks a pitch preset, the exact reviewed bytes are already locked by Change Set 100. Change Set 101 now provides the missing executable gate that takes those exact bytes through HYBRID_SURFACE semantic/alignment inspection before Golden scoring. No second FLUX inference is needed to move from camera selection into semantic QA, and a tampered or poorly integrated pitch cannot reach Golden review.

## Remaining external blocker
A genuine latest-architecture Candidate 1 still requires a compatible CUDA/BF16 host. This change does not fabricate a GPU result and does not claim a new Golden PNG.
