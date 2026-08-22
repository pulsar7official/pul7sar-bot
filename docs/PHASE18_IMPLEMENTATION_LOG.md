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
- Deterministic headline/score/footer style and fit contracts.
- Final export authorization requires approved typography, geometry and post-composition quality.
- CI `32580980268`: SUCCESS.

## Change Set 019 — Base-scene visual acceptance gate

### Purpose
Reject weak or unsafe AI-generated base scenes before any official PUL7SAR branding, crest, score, headline or social footer is composited.

### Added
- `engine/intelligence/base_scene_quality.py`
  - `SubjectFramingEvidence`
  - `IdentityVisualEvidence`
  - `ProtectedRegionEvidence`
  - `GenerationDefectEvidence`
  - `BaseSceneEvidence`
  - `BaseSceneAcceptanceDecision`
  - `BaseSceneVisualAcceptanceGate`

### Fail-closed checks
- exact output resolution vs GenerationPackage canvas
- exact reduced aspect ratio
- required subject presence
- approved subject framing/crop
- usable hero region
- framing confidence threshold
- required identity match against verified reference IDs
- identity confidence threshold
- protected overlay regions remain sufficiently clear
- duplicate/missing protected-region evidence
- generation defect evidence (e.g. anatomy/equipment defects)
- forbidden visual detections
- safe crop potential
- provider provenance evidence

### Protected-region rule
The hero box is intentionally occupied by the generated subject and is not required to be blank. Every other approved composition region (logo, headline, score, crest, footer, etc.) must provide evidence that it remains sufficiently clear for deterministic overlays.

### Provenance
Provider provenance is required. Missing provenance fails closed. A missing provider request ID currently produces a warning so adapters can be integrated incrementally while still preserving a provider/model evidence record.

### Added tests
- `tests/test_phase18_base_scene_quality.py`
  - clean scene acceptance
  - resolution rejection
  - identity mismatch rejection
  - low identity-confidence rejection
  - busy headline-region rejection
  - missing protected-region evidence rejection
  - generation-defect rejection
  - forbidden-visual rejection
  - unsafe-crop rejection
  - missing-provenance rejection
  - missing request ID warning

### Modified
- `engine/intelligence/__init__.py`
  - Exports base-scene evidence and acceptance APIs.

### Production safety
- `main.py`: untouched.
- Telegram publishing: untouched.
- Legacy image sourcing/rendering: untouched.
- Production renderer/templates: untouched.
- No external image provider invoked.
- No production secret/API key added.

### Architecture after Change Set 019
`Article -> Story Intelligence -> factual / identity / sentiment / neutrality gates -> Visual Family -> Concept Director -> Generation Authorization -> Platform Profile -> Scene Specification -> Verified Theme -> Destination Assets -> Deterministic Layout -> Generation Package -> Provider Eligibility -> Execution Plan -> AI Base Scene -> BaseSceneVisualAcceptanceGate -> PostCompositionPlanner -> Asset Integrity / Composition Quality -> Deterministic Typography -> FinalExportGate -> Platform Export`

### Next planned work
1. Verify Change Set 019 CI.
2. Add a provider-adapter evidence contract that translates vendor output into `BaseSceneEvidence` without trusting vendor-specific payloads elsewhere in the domain.
3. Add regeneration/retry policy with bounded attempts and explicit rejection reasons.
4. Add candidate ranking so several generated scenes can be evaluated and the best accepted scene selected deterministically.
5. Only then evaluate/connect a real image provider behind the existing authorization, eligibility and quality gates.
