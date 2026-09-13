# Phase 18 Change Set 199 — Dynamic Visual Brain Original Scene Bridge

## Purpose

Change Set 198 froze the complete story-specific concept competition and one explicit selected concept before rendering.  Change Set 199 connects that immutable editorial decision to the existing provider-neutral Original Scene runtime contract without choosing a renderer, model, paid provider, or publication path.

## Added

- `engine/intelligence/dynamic_visual_brain_original_scene.py`
  - replays the full concept lock before creating an execution-facing request;
  - rejects story, competition, selected-concept, and scene-prompt drift;
  - emits an `OriginalSceneRequest` using the existing `GENERATIVE_EVENT_ATMOSPHERE` / `ATMOSPHERE` contract;
  - keeps person-led stories identity-neutral unless a later, separately qualified identity-conditioned route is used;
  - reserves readable text, PUL7SAR identity, exact scores, exact numbers, crests, entity marks, and exact sport geometry for deterministic downstream composition;
  - requires semantic inspection;
  - selects no provider or generator and grants no publication authority.
- `tests/test_phase18_dynamic_visual_brain_original_scene.py`
  - provider-neutral atmosphere request coverage;
  - identity-safe person-led coverage;
  - exact-score/entity-mark ownership for results;
  - competition/selected-concept drift rejection;
  - authority drift rejection;
  - seed validation.

## Why this materially reduces the remaining gap

The Dynamic Visual Brain is no longer only a preview surface.  A selected story-specific concept now has a fail-closed bridge into the same Original Scene contract already used by the qualified local-runtime architecture.

The next renderer-facing chain can therefore be built without re-inventing policy:

`verified story -> dynamic competition -> concept SHA lock -> OriginalSceneRequest -> measured $0-local runtime qualification -> genuine PNG -> semantic/Visual Critic evidence -> human Golden review`

The bridge deliberately uses the identity-neutral atmosphere runtime.  It never converts a person's name into permission to synthesize that person's likeness.

## Preserved gates

No Fact, Identity, Sentiment/Neutrality, zero-cost, semantic-publication, geometry, brand, typography, provenance, Visual Critic, or Golden quality gate is weakened.

## Deleted

Nothing.

## Production isolation

`main` and `main.py` are not modified by this change set.
