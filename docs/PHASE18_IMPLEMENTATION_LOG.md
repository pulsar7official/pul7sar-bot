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
- `engine/intelligence/__init__.py`: package boundary.
- `engine/intelligence/models.py`: immutable story, claim, identity, sentiment and visual-intent contracts.
- `engine/intelligence/fact_lock.py`: deterministic factual-safety gate.
- `tests/test_story_intelligence_models.py`: contract and Fact Lock regression tests.

### Safety
- No production file modified.
- `main.py`, Telegram, legacy rendering, templates and `USE_VISUAL_ENGINE` untouched.

## Change Set 003 — StoryAnalyzer + evidence-based identity gate

### Added
- `engine/intelligence/story_analyzer.py`: deterministic article-to-StoryBrief adapter.
- `engine/intelligence/identity.py`: evidence/requirements/verifier split for real-person identity.
- `tests/test_phase18_identity_verifier.py`: Charlie Hull and Sam Hickey regression protection.
- `tests/test_phase18_story_analyzer.py`: transfer-state, general-story and sentiment-signal tests.
- `.github/workflows/phase18-intelligence.yml`: isolated read-only Phase 18 CI.

### Modified
- `engine/intelligence/__init__.py`: exported StoryAnalyzer and identity APIs.

### Validation
- Draft PR #1 opened and kept unmerged.
- CI run `32574409083`: SUCCESS.
- Syntax, intelligence tests and production-isolation gate all passed.

## Change Set 004 — Story classification, result neutrality and Visual Family routing

### Editorial principle added

PUL7SAR may celebrate a winner but must not humiliate the losing side. The loser
may be absent, respectfully represented, or shown with realistic disappointment.
Mockery, degrading symbolism, domination symbolism, exaggerated shame and
humiliating treatment are rejected. Even a verified harsh sporting context does
not authorize ridicule or degradation.

This rule applies to clubs, teams, athletes, institutions and their audiences.
The visual objective is to amplify the winner's moment rather than attack the
loser.

### Added

- `engine/intelligence/classification.py`
  - Stable enums for `StoryType`, `StoryScope`, and `EntityKind`.
  - `EntityCandidate` is explicitly a candidate, never a verified identity.
  - `StoryClassification` validates general/entity-led/multi-entity scope.
  - `StoryClassifier` normalizes explicit story-type signals without inventing
    missing facts.

- `engine/intelligence/neutrality.py`
  - Adds `EditorialNeutralityGate`.
  - Adds `ResultVisualTreatment`, `LoserTreatment`, and `NeutralityDecision`.
  - Fails closed on mocking copy, degrading symbolism, domination symbolism,
    exaggerated shame, or humiliating loser treatment.
  - Allows celebration of the winner, respectful loser treatment, loser absence,
    and proportionate realistic disappointment.
  - Verified harsh context may support a serious/realistic mood but never
    overrides the anti-humiliation rules.

- `engine/intelligence/visual_router.py`
  - Adds `VisualFamily`: RESULTS, TRANSFERS, MATCHDAY, PLAYER_STORIES,
    SERIOUS_NEWS, ORGANIZATION, GENERAL_WORLD.
  - Routes result stories through the neutrality gate.
  - Routes person-led stories through identity verification requirements.
  - Keeps transfer concepts from visually implying an unverified completed
    signing.
  - Routes general multi-league/editorial stories to a brand-led world and marks
    the color strategy as `brand_red`.
  - Entity-led stories use `adaptive_entity_palette` as the high-level strategy.

- `tests/test_phase18_classification_router.py`
  - General multi-league story -> GENERAL_WORLD / brand red / no hero entity.
  - Result -> RESULTS + mandatory neutrality gate.
  - Transfer approach -> TRANSFERS without completed-signing implication.
  - Sam Hickey-style player story -> PLAYER_STORIES + identity gate.
  - General scope cannot secretly carry entity candidates.

- `tests/test_phase18_neutrality.py`
  - Winner celebration is allowed.
  - Losing side may be absent or respectful.
  - Realistic disappointment is allowed.
  - Humiliation, mocking copy, degrading/domination symbolism and exaggerated
    shame are rejected.
  - Verified harsh context still cannot authorize mockery.

### Modified

- `engine/intelligence/__init__.py`
  - Exports classification, neutrality and routing APIs.

- `.github/workflows/phase18-intelligence.yml`
  - Adds syntax checks and unit tests for Change Set 004 modules.
  - Retains `contents: read` and production-isolation enforcement.

### Deleted
- Nothing.

### Production safety
- `main.py`: untouched.
- Telegram publishing: untouched.
- `USE_VISUAL_ENGINE`: untouched.
- Legacy image sourcing/rendering: untouched.
- Existing templates/render pipeline: untouched.
- Existing entity normalizer: untouched.
- Existing structural QualityVerifier: untouched.

### Architecture after Change Set 004

`Article -> StoryAnalyzer -> Fact Lock -> Classification -> Identity Gate -> Neutrality Policy -> Visual Family Router -> VisualIntent -> future concept/generation layer -> existing renderer`

The router chooses visual grammar only. It does not generate images, choose a
specific pose, or bypass identity/factual/neutrality gates.

### Next planned work

1. Add a sentiment-classification provider contract rather than relying only on
   explicit sentiment labels.
2. Add editorial role/perspective for results so winner and loser sentiments are
   modeled separately instead of collapsing the whole story into one emotion.
3. Add Concept Director contracts with forbidden-concept constraints from Fact
   Lock, Identity Gate and Neutrality Gate.
4. Only after those gates are stable, begin the first original-scene provider.
