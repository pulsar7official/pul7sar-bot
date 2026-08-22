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

### Validation
- Draft PR #1 opened and kept unmerged.
- CI run `32574409083`: SUCCESS.

## Change Set 004 — Story classification, result neutrality and Visual Family routing

### Editorial principle
PUL7SAR may celebrate a winner but must not humiliate the losing side. The loser
may be absent, respectfully represented, or shown with realistic disappointment.
Mockery, degrading symbolism, domination symbolism, exaggerated shame and
humiliating treatment are rejected.

### Added
- `engine/intelligence/classification.py`
- `engine/intelligence/neutrality.py`
- `engine/intelligence/visual_router.py`
- `tests/test_phase18_classification_router.py`
- `tests/test_phase18_neutrality.py`

### Validation
- CI run `32575035862`: SUCCESS.

## Change Set 005 — Perspective-aware results + Concept Director

### Added

- `engine/intelligence/perspective.py`
  - Separates the emotional perspective of winner, loser and PUL7SAR editorial voice.
  - Enforces `NEUTRAL` as the editorial result perspective.
  - Prevents a winner's positive sentiment from becoming a platform-level bias.

- `engine/intelligence/concept_director.py`
  - Adds `ConceptBrief`, `ProposedConcept`, `ConceptConstraint` and `ConceptDirector`.
  - Introduces family-specific forbidden-concept constraints.
  - Result concepts inherit anti-humiliation, anti-mockery, anti-degrading-symbolism and anti-exaggerated-shame rules.
  - Transfer concepts inherit `NO_UNVERIFIED_SIGNING`.
  - Matchday concepts inherit `NO_INVENTED_RESULT`.
  - Player stories inherit `NO_UNVERIFIED_IDENTITY`.
  - Serious news inherits `NO_SENSATIONAL_HARM`.
  - A concept cannot bypass `EditorialNeutralityGate` merely by claiming compliance.

- `tests/test_phase18_perspective_concept.py`
  - Verifies separate winner/loser/editorial sentiments.
  - Verifies editorial neutrality cannot be changed to positive/negative.
  - Verifies result constraints are mandatory.
  - Verifies humiliating concepts remain blocked even if they claim to acknowledge constraints.

### Modified
- `engine/intelligence/__init__.py`: exports perspective and concept APIs.
- `.github/workflows/phase18-intelligence.yml`: includes new tests.

### Validation
- CI run `32575594345`: SUCCESS.
- Syntax, tests and production-isolation gate passed.

## Change Set 006 — Sentiment evidence + conservative resolver

### Added

- `engine/intelligence/sentiment.py`
  - Adds `SentimentProvider` protocol for future rules/LLM providers.
  - Adds `SentimentEvidence`, which requires a source and confidence.
  - Adds `SentimentResolver` as the stable authority over provider suggestions.
  - No evidence -> `NEUTRAL`.
  - Low-confidence evidence -> `NEUTRAL`.
  - Strong conflicting evidence -> `NEUTRAL` with `conflicted=True`.
  - A provider suggestion is evidence, not authority over editorial tone.

- `tests/test_phase18_sentiment.py`
  - Covers no evidence, low confidence, strong positive, high-confidence conflict, and source validation.

### Modified
- `engine/intelligence/__init__.py`: exports sentiment APIs.
- `.github/workflows/phase18-intelligence.yml`: switched to discovery for all `test_phase18_*.py` tests so later Phase 18 tests are included automatically.

### Deleted
- Nothing.

### Production safety
- No production integration.
- No model/API provider wired.
- No image generation wired.

## Change Set 007 — Generation Authorization + original-scene provider boundary

### Purpose
Create the final mandatory safety boundary before any future original image provider can be invoked.

### Added

- `engine/intelligence/generation_authorization.py`
  - Adds `GenerationAuthorizer`.
  - Aggregates Fact Lock, identity requirements, sentiment conflict state and Concept Director validation.
  - Produces an explicit `GenerationAuthorization` allow/deny decision.
  - Denied decisions never contain an authorization token.
  - Allowed decisions require the internal Phase 18 authorization token.
  - If identity is required, generation is denied unless status is `VERIFIED` and `depiction_allowed=True`.
  - High-confidence sentiment conflict blocks generation rather than guessing a mood.
  - Forbidden factual claims block generation.
  - Neutrality/concept failures block generation.

- `engine/intelligence/generation_provider.py`
  - Adds `OriginalSceneProvider` protocol without choosing a vendor.
  - Adds `OriginalSceneRequest` and `OriginalSceneResult` contracts.
  - Adds `AuthorizedSceneGenerator`, the wrapper that validates authorization before calling a provider.
  - A denied authorization prevents provider invocation entirely.
  - This makes Generation Authorization an architectural requirement instead of a coding convention.

- `tests/test_phase18_generation_authorization.py`
  - Safe result can be authorized.
  - Forbidden claim blocks generation.
  - Missing or partial identity blocks generation when required.
  - Verified identity passes the identity gate.
  - Conflicted sentiment blocks generation.
  - Humiliating concept blocks generation.

- `tests/test_phase18_generation_provider.py`
  - Valid authorization permits provider invocation.
  - Denied authorization prevents the provider from being called at all.
  - Invalid output dimensions are rejected before provider execution.

### Modified
- `engine/intelligence/__init__.py`: exports generation authorization/provider contracts.

### Deleted
- Nothing.

### Production safety
- `main.py`: untouched.
- Telegram publishing: untouched.
- `USE_VISUAL_ENGINE`: untouched.
- Legacy image sourcing/rendering: untouched.
- Existing renderer/templates: untouched.
- No external image provider selected or invoked.
- No secret/API key added.

### Architecture after Change Set 007

`Article -> StoryAnalyzer -> Fact Lock -> Classification -> Identity Verification -> Sentiment Evidence/Resolution -> Perspective Separation -> Neutrality Gate -> Visual Family Router -> Concept Director -> Generation Authorizer -> AuthorizedSceneGenerator -> future OriginalSceneProvider -> existing composition/render layer`

The future provider cannot be reached through the intended Phase 18 path unless the request has passed the factual, identity, sentiment, neutrality and concept gates.

### Next planned work

1. Define the **Original Scene Specification** that translates an authorized concept into provider-neutral scene requirements: subject, environment, camera, mood, palette, exact assets, forbidden elements and output format.
2. Add a deterministic Prompt/Scene Compiler that never invents facts beyond Fact Lock and ConceptBrief.
3. Add provider capability abstraction and fallback strategy without choosing a paid provider yet.
4. Build a dry-run vertical slice that produces a complete generation package without calling any external image API.
5. Only after that package is inspectable and regression-tested should the first real original-image provider be connected.
