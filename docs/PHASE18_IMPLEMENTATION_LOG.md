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

### Core production rule
Official brand assets and final editorial typography are deterministic post-generation elements. The image model never becomes the source of truth for PUL7SAR branding, team crests, score text, or platform footer content.

### Added
- `engine/intelligence/post_composition.py`
  - Adds `CompositionRole`, `CompositionElement`, `PostCompositionPlan`, `PostCompositionPlanner`, `AssetIntegrityRecord`, `CompositionQualityDecision`, and `PostCompositionQualityGate`.
  - Maps approved exact assets to deterministic layout roles.
  - PUL7SAR wordmark/logo remains untinted.
  - Team/club crests remain untinted.
  - Only a PUL7SAR pulse/7 asset explicitly marked `TINTABLE_ACCENT` may receive the package accent color.
  - Headline, score and destination handle are rendered outside the image model and require corresponding approved layout boxes.
  - Optional assets are skipped when their role is not present in the approved story layout rather than being forced into the visual.

### Asset integrity
- `AssetIntegrityRecord` adds a strict SHA-256 contract.
- If an asset declares an expected `metadata.sha256`, the quality gate requires a matching runtime integrity record before export.
- Missing or mismatched checksums fail closed.
- Duplicate integrity records are rejected by the quality gate.

### Quality gate
The post-composition quality gate rejects:
- platform mismatch
- canvas mismatch
- missing approved layout boxes
- unknown asset IDs
- missing required asset integrity evidence
- checksum mismatches
- missing or duplicated PUL7SAR logo placement
- tinted PUL7SAR wordmark/logo
- tinted team/club crest

### Added tests
- `tests/test_phase18_post_composition.py`
  - exact assets and text are planned outside the image model
  - only the pulse/7 receives entity accent
  - missing text geometry fails closed
  - valid SHA-256 evidence passes
  - checksum mismatch fails closed
  - wordmark tint is rejected
  - team crest tint is rejected
  - platform/canvas mismatch fails

### Modified
- `engine/intelligence/__init__.py`
  - Exports post-composition and integrity APIs.

### Production safety
- `main.py`: untouched.
- Telegram publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Production renderer/templates: untouched.
- No external image provider invoked.
- No production secret/API key added.

### Architecture after Change Set 017
`Article -> Story Intelligence -> factual / identity / sentiment / neutrality gates -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme -> Destination Assets -> Deterministic Layout -> Generation Package -> Provider Eligibility -> Execution Plan -> AI Base Scene -> PostCompositionPlanner -> Asset Integrity + PostCompositionQualityGate -> platform export`

### Next planned work
1. Verify Change Set 017 CI.
2. Add explicit deterministic text-style contracts for headline, score and footer: font-family reference, size bounds, weight, line count and overflow policy.
3. Add composition-output contract and final export gate.
4. Add visual-quality evidence contract for generated base scene before post-composition.
5. After those gates are green, evaluate the first real provider adapter behind the existing authorization and eligibility layers.
