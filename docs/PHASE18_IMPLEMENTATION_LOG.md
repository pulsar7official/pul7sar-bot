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

## Change Set 003 — StoryAnalyzer + evidence-based identity gate

### Added

- `engine/intelligence/story_analyzer.py`
  - Adds the first deterministic `article -> StoryBrief` adapter.
  - Accepts the production article shape (`title`, `summary`, `sport`, etc.)
    without importing `main.py`.
  - Supports explicit overrides from later intelligence providers.
  - Normalizes explicit sentiment labels but does **not** infer sentiment from
    prose yet.
  - Preserves source tracing (`link`, `source`, `published`) as metadata without
    promoting those values into factual claims.
  - Does not silently infer entity identity, event completion, or missing story
    state.

- `engine/intelligence/identity.py`
  - Adds `IdentityEvidence`, `IdentityRequirements`, and `IdentityVerifier`.
  - Separates evidence discovery from the safety decision that allows a real
    person to appear in a generated visual.
  - Uses name normalization plus contextual constraints such as sport, role,
    gender, nationality, and team/affiliation.
  - Fails closed on name mismatch, context mismatch, weak evidence, or
    high-confidence provider conflict.
  - Only returns `depiction_allowed=True` when status is `VERIFIED` and the
    minimum confidence threshold is met.
  - Contains no network or LLM calls; future external providers must supply the
    evidence explicitly.

- `tests/test_phase18_identity_verifier.py`
  - Adds the Charlie Hull regression: golf/female verifies, wrong-gender
    candidate is rejected.
  - Adds the Sam Hickey regression: boxing/Scottish/middleweight verifies, a
    golf candidate with the same name is rejected.
  - Tests high-confidence source conflicts, low-confidence results, and name
    normalization.

- `tests/test_phase18_story_analyzer.py`
  - Verifies compatibility with the current article dictionary shape.
  - Verifies that transfer `approach` is not silently upgraded to `completed`.
  - Verifies entity-neutral multi-league stories remain entity-neutral.
  - Verifies positive and negative sentiment remain distinct signals.
  - Verifies unknown sentiment and malformed entity collections fail closed.

- `.github/workflows/phase18-intelligence.yml`
  - Adds isolated CI for Phase 18 intelligence files only.
  - Performs Python syntax checks.
  - Runs the Phase 18 model, identity, and analyzer test suites.
  - Adds an isolation gate that rejects imports from `main.py` inside
    `engine/intelligence`.
  - Uses `contents: read`; the workflow itself has no write permission.

### Modified

- `engine/intelligence/__init__.py`
  - Exports the StoryAnalyzer and identity-verification APIs through the package
    boundary.

- `engine/intelligence/story_analyzer.py`
  - Tightened metadata validation after initial creation so malformed metadata
    fails with `StoryAnalysisError` instead of leaking a generic conversion
    exception.

### Deleted

- Nothing.

### Production safety

- `main.py`: untouched.
- Production workflows: untouched.
- Telegram publishing: untouched.
- `USE_VISUAL_ENGINE`: untouched.
- Existing rendering pipeline and templates: untouched.
- Legacy image search/rendering: untouched.
- Existing `engine/entities` normalization behavior: untouched.

### Important architectural decision

Identity verification is now intentionally split into two future-facing stages:

`Identity Provider(s) -> IdentityEvidence -> IdentityVerifier -> IdentityPlan`

The provider may later use structured sports databases, authoritative web
sources, or another retrieval strategy. The verifier remains deterministic and
conservative. This prevents a search provider from directly granting depiction
permission merely because it returned a same-name result.

### Current limitation

No automatic provider exists yet, so Phase 18 cannot independently discover or
verify Charlie Hull, Sam Hickey, or another real person from the web. The safety
contract and regression protection are now present; provider integration is a
later change set.

### Next planned change set

Build the first **Story Classification layer** for:

1. explicit entity extraction candidates,
2. event/story type normalization,
3. sentiment classification contract,
4. general-vs-entity-led story routing,
5. the first `VisualFamily` router without image generation.
