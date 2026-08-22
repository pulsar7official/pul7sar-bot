# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the
`phase18/story-intelligence` branch. It records what changed, why it changed,
and what remains intentionally untouched.

## Change Set 001 — Branch creation

- Branch: `phase18/story-intelligence`
- Base: `main`
- Production behavior changed: **No**
- Files changed: **None**
- Purpose: isolate Phase 18 work from the production branch.

## Change Set 002 — Story-intelligence contracts + Fact Lock foundation

### Added

- `engine/intelligence/__init__.py`
  - Creates the Phase 18 intelligence package boundary.
  - Exposes only the first stable contracts and the Fact Lock gate.
  - Does not import or mutate `main.py` production behavior.

- `engine/intelligence/models.py`
  - Adds immutable domain contracts for story meaning and visual safety:
    - `ClaimKind`
    - `LockedClaim`
    - `Sentiment`
    - `StoryBrief`
    - `IdentityStatus`
    - `IdentityPlan`
    - `VisualIntent`
  - Keeps editorial/story intelligence separate from `RenderContext`.
  - Prevents real-person depiction unless identity status is `VERIFIED`.
  - Uses immutable metadata mappings to prevent downstream accidental mutation.

- `engine/intelligence/fact_lock.py`
  - Adds a deterministic factual-safety boundary.
  - No LLM calls, no network calls, no fact discovery.
  - Accepts pre-classified claims and controls which claims may drive copy or
    visuals.
  - `FORBIDDEN` claims are never returned as usable.
  - `assert_publishable()` fails closed when forbidden claims exist.
  - `require_fact()` requires an exact locked fact at a requested confidence
    level rather than silently converting an inference into a fact.

- `tests/test_story_intelligence_models.py`
  - Verifies immutable claim metadata and confidence validation.
  - Verifies that `depiction_allowed=True` requires verified identity.
  - Adds regression-shaped examples around Charlie Hull, Sam Hickey, and an
    unconfirmed Arsenal transfer state.
  - Verifies Fact Lock filtering and fail-closed behavior.

### Modified

- No existing production file was modified.
- No existing Visual Engine component was modified.
- No workflow was modified in this change set.

### Deleted

- Nothing.

### Production safety

- `main.py`: untouched.
- `USE_VISUAL_ENGINE`: untouched and remains governed by existing production
  configuration.
- Telegram publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Existing templates: untouched.
- Existing entity normalizer: untouched.
- Existing `QualityVerifier`: untouched.

### Architectural role

Phase 18 now has an explicit domain layer that can sit before the current
rendering pipeline:

`Article -> Story Intelligence -> Fact Lock -> Identity/Sentiment/Visual Intent -> existing rendering engine`

The new code does **not** yet perform automatic entity discovery, web identity
verification, sentiment classification, visual-family routing, concept
selection, or image generation. Those remain later Phase 18 change sets.

### Next planned change set

Build the first deterministic `StoryAnalyzer` / input adapter and explicit
identity-verification result contract, then add regression tests for:

1. Charlie Hull -> golf / female / correct entity context.
2. Sam Hickey -> boxing / Scottish / middleweight context.
3. Transfer rumor/approach -> never upgrade to completed signing.
4. General multi-league story -> general PUL7SAR world rather than one club.
5. Positive vs negative story -> distinct sentiment signal before art direction.
