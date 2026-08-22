# PUL7SAR Phase 18 — Implementation Log

This document is the authoritative implementation journal for Phase 18 on the `phase18/story-intelligence` branch.

## Change Sets 001–009
Previously documented foundation: Fact Lock, StoryAnalyzer, identity verification, classification, neutrality, Visual Family routing, perspective-aware result sentiment, Concept Director, sentiment resolver, Generation Authorization, platform profiles, Original Scene Specification, exact assets, layout safety, multi-platform batch generation packages. All production paths remain isolated.

## Change Set 010 — Deterministic platform layout planner
- Deterministic protected geometry for hero/logo/crest/score/headline/footer.
- Separate portrait, vertical and landscape art direction.
- CI `32577397716`: SUCCESS.

## Change Set 011 — Layout-aware Generation Package
- Generation package carries exact geometry and accent color.
- CI `32577621033`: SUCCESS.

## Change Set 012 — Cross-platform dry-run manifest
- Inspectable canvas/safe-area/layout/assets/facts/negative constraints per platform.
- CI `32577945352`: SUCCESS.

## Change Set 013 — Entity theme, exact brand semantics, destination social assets
- Verified palette resolver with PUL7SAR-red fallback.
- Exact wordmark vs tintable 7/pulse semantics.
- Destination-only social icon filtering.
- CI `32578124530`: SUCCESS.

## Change Set 014 — Inspectable brand/theme manifest + end-to-end regression fixture
- Manifest v2 exposes verified theme and brand plan.
- Seven-platform synthetic transfer-story regression fixture.
- CI `32578343142`: SUCCESS.

## Change Set 015 — Provider capability and eligibility layer
- Models provider features, output limits and reference limits.
- Explicit eligibility and ordered fallback policy.
- CI `32579225091`: SUCCESS.

## Change Set 016 — Provider-neutral execution plan
- AI provider generates only the base scene.
- Official logos, crests, social icons, score typography and final copy are applied later by PUL7SAR.
- Strict stages: generate -> exact assets -> editorial text -> quality -> export.
- CI `32579444426`: SUCCESS.

## Change Set 017 — Deterministic post-generation composition + quality gate
- Exact official assets and final editorial text are post-composited outside the image model.
- Asset SHA-256 integrity support and fail-closed composition validation.
- CI `32580744885`: SUCCESS.

## Change Set 018 — Deterministic typography + final export authorization

### Purpose
Make final text rendering and export deterministic, inspectable and fail-closed. The image model is not trusted to render the final headline, score or platform footer.

### Added
- `engine/intelligence/typography.py`
  - Adds `FontReference`, `TextStyle`, `TextRole`, `TextAlign`, `TextBox`, `TextLayout`, `TypographyDecision`, `DeterministicTypographyEngine`, and `Pul7sarTypographyPolicy`.
  - Fonts are referenced by configured IDs/family names and optional SHA-256; no font file is bundled or guessed by the intelligence layer.
  - Headline, score and social-footer roles have independent size bounds, line limits, alignment and overflow policy.
  - Default policy prohibits silent headline truncation/ellipsis.
  - Score and footer are single-line roles.
  - The engine shrinks text deterministically within approved min/max bounds and fails closed if it cannot fit the approved layout box.
  - Latin-only uppercase support never mutates Arabic/non-Latin text.
  - Current fit estimation is deterministic/conservative and is explicitly a contract until a concrete renderer supplies exact glyph metrics.

- `engine/intelligence/final_export.py`
  - Adds `FinalComposedOutput`, `ExportAuthorization`, and `FinalExportGate`.
  - Final export re-runs post-composition quality checks.
  - Rejects final platform/canvas mismatch.
  - Requires a base-scene reference and composed-output reference.
  - Every rendered text role must use an approved style and exact approved geometry.
  - Missing, duplicated or unexpected rendered text roles fail closed.
  - Unapproved fonts, out-of-bounds font sizes, excessive line count and prohibited truncation fail closed.
  - Successful export receives a non-empty authorization token; denied export never receives a token.

### Added tests
- `tests/test_phase18_typography_export.py`
  - headline fitting without silent truncation
  - overlong/tiny-box failure
  - one-line score
  - compact one-line footer
  - complete valid export authorization
  - missing rendered headline rejection
  - wrong text geometry rejection
  - unapproved font rejection

### Modified
- `engine/intelligence/__init__.py`
  - Exports typography and final-export APIs.

### Production safety
- `main.py`: untouched.
- Telegram publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Production renderer/templates: untouched.
- No external image provider invoked.
- No font file added or exposed.
- No production secret/API key added.

### Architecture after Change Set 018
`Article -> Story Intelligence -> factual / identity / sentiment / neutrality gates -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme -> Destination Assets -> Deterministic Layout -> Generation Package -> Provider Eligibility -> Execution Plan -> AI Base Scene -> PostCompositionPlanner -> Asset Integrity / Composition Quality -> Deterministic Typography -> FinalExportGate -> Platform Export`

### Next planned work
1. Verify Change Set 018 CI.
2. Add visual-quality evidence for the AI base scene before official assets/text are composited: resolution, subject framing, identity-reference confidence, blank protected regions and generation defect flags.
3. Add a base-scene acceptance gate so a poor generation never reaches the branding/composition layer.
4. Add a provider adapter interface that produces this evidence without binding Phase 18 to one vendor.
5. Only after the base-scene quality gate is green should a real provider be evaluated/connected.
