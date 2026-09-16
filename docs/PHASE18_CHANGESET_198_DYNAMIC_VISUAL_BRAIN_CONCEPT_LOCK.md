# Phase 18 Change Set 198 — Dynamic Visual Brain Concept Lock

## Purpose

Phase 18 now has a deterministic, story-specific Dynamic Visual Brain that proposes materially different editorial concepts before rendering.  The remaining trust gap was that a concept could be previewed and then changed, replaced, or confused with another concept before pixels were generated.

Change Set 198 adds a tamper-evident pre-render concept lock.  The lock freezes the entire concept competition and one explicit selected concept *before* any renderer is authorized.

## Added

- `engine/intelligence/dynamic_visual_brain_lock.py`
  - canonical SHA-256 over every concept in the competition;
  - canonical SHA-256 over the explicitly selected concept;
  - independent SHA-256 over the selected scene prompt;
  - story fingerprint and editorial event binding;
  - fail-closed safety-marker checks;
  - fail-closed rejection of platform-name leakage;
  - explicit closure of generation, Golden, publication, and Seeds 2–4 authority.
- `tools/phase18_lock_dynamic_visual_brain_concept.py`
  - CPU-only CLI for locking one explicit concept from a UTF-8 story JSON payload;
  - repository-contained input/output paths;
  - no renderer, network, paid provider, queue mutation, or publication authority.
- `tests/test_phase18_dynamic_visual_brain_lock.py`
  - deterministic receipt replay;
  - competition hash changes when even an unselected alternative changes;
  - story-fingerprint binding;
  - missing/ambiguous concept rejection;
  - PUL7SAR/PULSAR prompt leakage rejection;
  - safety-marker rejection;
  - provider/publication authority drift rejection.

## Why this materially reduces the gap

The Visual Brain is now concept-diverse rather than seed-diverse.  That makes it important to prove which story-specific concept actually entered rendering.  This change prevents post-hoc concept substitution and prevents a Visual Critic decision for one concept from being attributed to a different pre-render idea.

The intended next end-to-end chain is:

`verified story -> dynamic concept competition -> explicit concept lock -> renderer admission -> genuine PNG -> concept/PNG-bound Visual Critic -> human Golden review`

No renderer is added here and no image is fabricated.

## Preserved fail-closed gates

This change does not modify or waive:

- Fact Lock;
- Entity/Identity Verification;
- Sentiment/Neutrality and loser-respect policy;
- `$0-local` policy;
- pinned FLUX/Qwen model revisions;
- CUDA/BF16/VRAM/RAM/offload/runtime resource gates;
- generated text/branding/exact fact/entity-mark/exact sport-geometry prohibitions;
- semantic/layer-ownership gates;
- Visual Critic hard failures;
- Golden `8.5` minimum / `9.0+` elite target;
- Exact Brand/Typography Integrity;
- SemanticPublicationGate.

## Deleted

Nothing.

## Production isolation

`main` and `main.py` are not modified by this change set.
