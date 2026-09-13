# Phase 18 Change Set 100 — Tamper-evident pitch selection lock

## Goal
Bind an explicitly human-reviewed football camera preset to the exact genuine FLUX base and exact diagnostic variant bytes without rerunning FLUX or silently promoting a diagnostic image into a publication asset.

## Added
- `engine/intelligence/football_pitch_selection.py`
  - Requires a valid `COLAB_PITCH_REVIEW_READY` receipt with `selection_is_manual=true`.
  - Requires the source review and diagnostic manifest to remain `publication_ready=false`.
  - Replays the genuine base SHA-256 from the diagnostic manifest.
  - Resolves the selected preset against the exact diagnostic variant shown during review.
  - Replays the selected variant SHA-256 and requires its prior artifact-integrity result to remain valid.
  - Copies the selected diagnostic bytes into a locked artifact and verifies the copied SHA-256 is byte-identical.
  - Emits `FOOTBALL_PITCH_SELECTION_LOCKED` with an explicit list of gates that remain unwaived.
- `tools/phase18_lock_pitch_selection.py`
  - Phase-18-branch-only CLI.
  - Defaults to the Candidate-specific Colab pitch-review receipt.
  - Does not invoke FLUX, Qwen, any paid API, or any provider.
- `tests/test_phase18_football_pitch_selection.py`
  - Locks only an explicit manual selection.
  - Rejects auto/missing selection.
  - Rejects any review that claims publication readiness.
  - Rejects base tampering after diagnostics.
  - Rejects selected-variant tampering after review.
  - Confirms the locked output remains byte-identical to the reviewed diagnostic variant.

## Modified
- The Phase 18 implementation log is extended to Change Set 100.

## Deleted
- Nothing.

## Why this reduces the remaining gap
Change Set 099 made camera selection reviewable but did not create a durable, tamper-evident bridge from that human decision to the next quality stage. Change Set 100 turns the reviewed preset into a stable artifact bound to the exact genuine base and diagnostic bytes. After the first real Candidate 1 base exists, PUL7SAR can review all placements once, lock the chosen placement without another FLUX inference, then run hybrid semantic/alignment inspection against that exact locked image. This isolates geometry iteration from scarce GPU generation while preserving every publication gate.

## Safety and quality invariants
- `main` / `main.py` are not modified.
- Fact Lock, identity verification, sentiment/neutrality, semantic layer ownership, SemanticPublicationGate, Golden visual thresholds, exact-brand integrity, typography integrity and final publication readiness remain mandatory.
- The selection lock never auto-selects a preset.
- `publication_ready` is always false.
- FLUX.2 Klein 4B, BF16, seeds/canvases and `$0-local` are unchanged.
- No paid provider, secret, model weights, font files, fake PNG, or fabricated benchmark is introduced.

## Next gate
Run hybrid semantic/alignment inspection on the exact locked artifact. Only if that succeeds can the artifact proceed to Golden visual quality review; brand/typography and final publication readiness remain later independent gates.
