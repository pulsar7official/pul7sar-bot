# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the
`phase18/story-intelligence` branch. It records what changed, why it changed,
and what remains intentionally untouched.

## Change Set 001 — Branch creation
- Branch: `phase18/story-intelligence`
- Base: `main`
- Production behavior changed: **No**

## Change Set 002 — Story-intelligence contracts + Fact Lock foundation
- Added immutable story/identity/claim/visual-intent models.
- Added deterministic Fact Lock.
- Added regression tests.
- Production untouched.

## Change Set 003 — StoryAnalyzer + evidence-based identity gate
- Added deterministic StoryAnalyzer.
- Added IdentityEvidence / IdentityRequirements / IdentityVerifier.
- Added Charlie Hull and Sam Hickey identity regression protection.
- Added isolated Phase 18 CI.
- CI `32574409083`: SUCCESS.

## Change Set 004 — Classification, neutrality and Visual Family routing
- Added StoryClassifier and stable story scopes/types.
- Added EditorialNeutralityGate.
- Added VisualFamilyRouter.
- Result principle: celebrate the winner without humiliating the losing side.
- CI `32575035862`: SUCCESS.

## Change Set 005 — Perspective-aware results + Concept Director
- Winner, loser and PUL7SAR editorial emotion are modeled separately.
- PUL7SAR result perspective is forced to NEUTRAL.
- Concept Director adds anti-humiliation, anti-mockery, factual and identity constraints.
- CI `32575594345`: SUCCESS.

## Change Set 006 — Sentiment evidence + conservative resolver
- Providers produce SentimentEvidence, not final authority.
- Missing, weak or conflicting evidence falls back to NEUTRAL.
- CI changed to automatically discover Phase 18 tests.

## Change Set 007 — Generation Authorization + provider boundary
- Added GenerationAuthorizer.
- Added AuthorizedSceneGenerator and OriginalSceneProvider protocol.
- Denied factual/identity/sentiment/neutrality/concept states cannot call a provider.
- No external image API selected or invoked.
- CI `32576136095`: SUCCESS.

## Change Set 008 — Platform-aware Original Scene Specification

### Important production rule
A single PUL7SAR visual is not assumed to fit every platform. Each publishing
surface receives its own output profile and safe area. The scene is therefore
art-directed for the target canvas rather than blindly resized or center-cropped.

### Added

- `engine/intelligence/platform_profiles.py`
  - Adds `SocialPlatform`, `SafeArea`, `PlatformImageProfile`, and `PlatformProfileRegistry`.
  - Centralizes versioned PUL7SAR output presets so dimensions can be updated without changing story intelligence.
  - Current PUL7SAR presets:
    - Instagram Feed: `1080x1350` (4:5)
    - Instagram Story/Reel vertical surface: `1080x1920` (9:16)
    - Facebook Feed: `1200x1500` (4:5)
    - X Feed: `1600x900` (16:9)
    - Threads Feed: `1080x1350` (4:5)
    - TikTok Photo: `1080x1920` (9:16)
    - Telegram Post: `1280x720` (16:9)
  - Every profile carries a platform-specific safe area for critical faces, logos, score, headline and social footer.
  - Profiles are explicitly documented as PUL7SAR production presets, not permanent platform limits.

- `engine/intelligence/scene_spec.py`
  - Adds `OriginalSceneSpecification`, `SceneIdentityReference`, and `SceneSpecCompiler`.
  - Compiles an approved concept into a provider-neutral dry-run scene package.
  - Carries exact target width, height, aspect ratio and safe area.
  - Carries visual family, concept, hero subject, verified identity details, environment, composition, camera direction, emotional mood, palette strategy, required assets, visual copy, factual constraints and forbidden visual elements.
  - Unverified or partial real-person identity cannot enter the scene specification.
  - Factual constraints are copied only from locked FACT claims.
  - The specification remains `dry_run=True`; no external provider call happens here.

- `tests/test_phase18_platform_scene_spec.py`
  - Verifies each supported platform has a profile.
  - Verifies Instagram Story and TikTok vertical output behavior.
  - Verifies X and Telegram landscape behavior.
  - Verifies platform dimensions/safe areas reach the scene specification.
  - Verifies Sam Hickey-style verified identity metadata reaches the scene package.
  - Verifies unverified identity is blocked before scene compilation.

### Modified
- `engine/intelligence/__init__.py`
  - Exports platform-profile and scene-specification APIs.

### Deleted
- Nothing.

### External platform note
X currently documents that a single photo with a standard aspect ratio between
2:1 and 3:4 can display in full in a post. The chosen PUL7SAR X preset (16:9)
is inside that documented range. Other platform presets remain internal,
versioned PUL7SAR art-direction defaults and should be periodically reviewed.

### Production safety
- `main.py`: untouched.
- Telegram publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Existing renderer/templates: untouched.
- No external image provider invoked.
- No API key/secret added.

### Architecture after Change Set 008
`Article -> StoryAnalyzer -> Fact Lock -> Classification -> Identity -> Sentiment/Perspective -> Neutrality -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Original Scene Specification (dry run) -> future provider adapter -> existing composition/render layer`

### Next planned work
1. Build a provider-neutral Prompt/Generation Package compiler from `OriginalSceneSpecification`.
2. Add multi-platform batch compilation so one story can produce separate scene packages for all enabled publishing surfaces.
3. Add crop/safe-zone regression tests to guarantee logo, headline, score and social footer are never placed outside critical safe areas.
4. Add required exact-asset contracts for PUL7SAR logo/pulse, club crest and social icons.
5. Only after the dry-run generation package is inspectable should a real original-image provider be connected.
