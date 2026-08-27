# Phase 18 Change Set 196 — Canonical Real-Visual Validation Ledger

## Purpose

Phase 18 is engineering-complete but not publication-ready. The first real Golden Editorial v6 Candidate 1 proved the local FLUX path and was correctly rejected because of physically inconsistent partial football geometry. The next gap is no longer another architecture layer; it is disciplined real-image validation across the seven canonical story families.

This change set adds a fail-closed validation ledger so real PNG evidence can be recorded without seed cherry-picking, without turning an aesthetic score into publication authority, and without losing the factual, identity, sentiment, geometry, semantic or provenance gates.

## Added

- `engine/intelligence/visual_validation_ledger.py`
  - canonical seven-case ledger derived directly from `PHASE18_VISUAL_BENCHMARKS`;
  - genuine PNG signature + SHA-256 evidence helper;
  - explicit pending / rejected / accepted states;
  - acceptance requires every factual, identity, sentiment-neutrality, sport-geometry, protected-zone, crop, semantic and provenance check;
  - acceptance requires explicit owner visual approval and Golden score `>= 8.5`;
  - any hard blocker defeats acceptance regardless of score;
  - rejected candidates require a reason or hard blocker;
  - the ledger can never set `publication_ready=true` or claim final publication authority.
- `tools/phase18_build_visual_validation_ledger.py`
  - builds the canonical pending ledger under `output/phase18_visual_validation/ledger.json`;
  - can validate an existing ledger without overwriting its review evidence;
  - refuses output paths outside the repository.
- `tests/test_phase18_visual_validation_ledger.py`
  - canonical seven-case coverage;
  - real PNG signature verification;
  - mandatory owner acceptance and 8.5 floor;
  - broken sport geometry hard blocker defeats a 9.9 score;
  - rejected Candidate evidence remains publication-closed;
  - all seven accepted cases can mark multi-family visual validation complete while publication authority remains false.

## Modified

- `tools/phase18_completion_audit.py`
  - requires the validation-ledger engine and CLI;
  - verifies fail-closed ledger contract markers;
  - reports the canonical ledger schema and zero publication authority;
  - updates the next target to binding every real benchmark PNG into the ledger before owner-approved publication assets are considered.

## Deleted

Nothing.

## Gate preservation

No factual, identity, sentiment/neutrality, `$0-local`, semantic-publication, Golden-quality, exact-brand, typography, provenance or sport-geometry gate was weakened. `broken_sport_surface_geometry` remains a hard blocker that cannot be rescued by a high aesthetic score.

## Runtime / GPU status

No GPU result is fabricated by this change set. The already-observed real Golden Editorial v6 Candidate 1 remains rejected, not accepted. Further real visual validation still requires compatible execution and owner review. The ledger is CPU-safe preparatory infrastructure for recording those real outputs deterministically when they exist.
