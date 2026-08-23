# PUL7SAR Phase 18 — Current Story-to-Visual Architecture

Status: active development on `phase18/story-intelligence`.

This document is the canonical snapshot of the current architecture. Older numbered change-set documents remain historical implementation notes.

## Core principle

PUL7SAR does **not** write a finished news caption and then ask an image model to interpret it.

The system makes one editorial decision that jointly determines:
- what the verified story means,
- which angle is strongest,
- how the short news copy should be phrased,
- what the visual anchor should be,
- what must be exact,
- what may be generated,
- what geometry is required,
- which visual production mode is safe,
- what fallback to use if a capability is unavailable,
- which contextual PUL7SAR accent state is appropriate.

## Pipeline

`Article / source evidence`
→ `StoryAnalyzer / explicit metadata normalization`
→ `Fact Lock`
→ `EventFactSchema`
→ `FactLockedEditorialAdapter`
→ `EditorialAngleCandidate[]`
→ `VisualAwareEditorialAngleSelector`
→ `EditorialHeadlineGrammar + EditorialCopyBuilder`
→ `SportVisualRuleRegistry`
→ `SceneComplexityPolicy`
→ `DeterministicGeometryCapabilityRegistry`
→ `StoryToVisualOrchestrator`
→ `DynamicBrandResolver`
→ `HybridVisualLayerPlanner`
→ `VisualExecutionPlanCompiler`
→ `HybridBaseSceneContractCompiler`
→ `EditorialVisualAuthorizationGate`
→ production actions:
  - safe generative atmosphere only when useful,
  - deterministic geometry/data/typography,
  - verified identities/entity marks,
  - deterministic dynamic PUL7SAR brand,
→ `HybridLayerQualityGate` for generated-layer leakage
→ deterministic/verified composition
→ receipt-backed `HybridVisualEvidence`
→ `HybridVisualQualityGate` for required-layer completion
→ semantic verification
→ strict Golden visual-quality gate
→ final export.

## Editorial-event taxonomy

The current `EditorialEvent` vocabulary covers result, live moment, preview, confirmed transfer, transfer rumour, contract, injury, comeback, suspension, retirement, appointment, dismissal, statement, record, award, trophy, draw, table, tactics, officiating, controversy, financial news, organization news, schedule, qualification, elimination and general stories.

Every event owns an explicit fact schema. Missing required facts fail before visual planning.

## Visual production modes

### `HYBRID`
Use generation for atmosphere/depth/light only; exact layers remain deterministic or verified.

### `DETERMINISTIC_COMPOSITION`
Use code and exact assets where the story is fundamentally geometry/data driven, such as tactics, tables, draws and schedules.

### `VERIFIED_ASSET_EDITORIAL`
Use verified subject/entity assets plus controlled design for sensitive, low-confidence or geometry-capability-limited stories.

### `GENERATIVE_SCENE`
Reserved for cases where generation is genuinely safe and useful. It is not the default owner of exact text, identity, geometry or branding.

## Layer ownership

| Layer | Owner |
|---|---|
| atmosphere, lighting, depth, non-factual texture | generative when authorized |
| sport surface geometry | deterministic renderer when required |
| hero identity | verified asset / identity-verified depiction |
| team/competition marks | verified exact asset |
| score/statistics/table/date | deterministic |
| editorial typography | deterministic |
| PUL7SAR structure + contextual 7/pulse accent | deterministic dynamic brand layer |

Generated PUL7SAR text, pseudo-logos, fake scores, fake statistics, fake club crests and generated exact sport geometry are architectural violations, not aesthetic imperfections.

## Dynamic PUL7SAR brand

PUL7SAR does not use one context-blind color state and does not ask diffusion to draw its identity.

Stable:
- brand structure,
- wordmark spelling,
- 7 position,
- pulse geometry once explicitly approved,
- placement rules and visual hierarchy.

Dynamic:
- the accent applied to the **7 + pulse**.

Default accent: PUL7SAR Red `#E10600`.

A contextual hero color may replace the red only when:
- Story Intelligence establishes one unambiguous visual hero,
- hero confidence is at least 0.85,
- explicit verified palette evidence exists,
- palette confidence is at least 0.80.

Ambiguous multi-entity stories, unknown palette evidence and low-confidence heroes return to PUL7SAR Red rather than choosing a side or guessing a color.

`DynamicBrandContrastResolver` preserves the verified accent and may add a minimal white/dark keyline when local contrast is weak instead of silently changing the story color.

The brand-geometry registry is fail-closed: an approved code-native wordmark/pulse recipe cannot render until its exact font reference, pulse path and explicit approval reference have been supplied. This prevents the system from inventing a logo merely because a raster logo file is absent.

## Brand-name redaction from generation

Golden Hybrid v5 introduces a stronger rule than a negative prompt: **the protected platform-name token is absent from the actual image-model prompt.**

The diffusion model receives generic instructions such as “fully unbranded”, “no platform names”, and “no readable text”. It is not repeatedly shown the word it is being told not to draw.

Both `GenerationPackageCompiler` and `LocalBackendRequestCompiler` fail if the final generative prompt contains `PUL7SAR` or `PULSAR`. The portable request records `brand_name_redacted_from_generation_prompt=true`.

Final PUL7SAR identity is added only after generation.

## Scene-complexity rule

The visual system uses the minimum physical complexity needed by the story.

A football transfer does not need a full football pitch. An injury does not need a generated stadium. A record may be better as a verified hero + exact number. A result can use partial deterministic sport context. Tactics may require the full deterministic surface because the surface geometry is itself part of the information.

When exact geometry is required but no renderer exists, PUL7SAR either removes that surface from a safe partial-context design or blocks the visual path entirely. It never asks diffusion to improvise missing exact geometry.

## Current sport-rule coverage

Explicit visual rules currently cover more than thirty sport families including football, basketball, tennis, padel, badminton, volleyball, handball, baseball, American football, rugby, cricket, golf, boxing, MMA, wrestling, judo, taekwondo, athletics, Formula 1, motorsport, swimming, cycling, rowing, sailing, ice hockey, winter sports, table tennis, snooker, darts, gymnastics, weightlifting, equestrian and esports.

Unknown sports receive a conservative fallback instead of fabricated geometry knowledge.

## Deterministic football geometry

Policy requirement and implementation readiness are separate.

Current implemented deterministic sport renderer:
- football: `football_pitch_projective_v1`

The football geometry system owns a stable **105m × 68m** reference surface and exact primitives for boundary/halfway lines, centre circle/mark, penalty areas, goal areas, penalty marks, penalty arcs and corner arcs.

`FootballPitchProjectionPlanner` maps these world coordinates into the image via a four-corner projective transform.

`FootballPitchPlacementPlanner` defines validated editorial camera/surface placements such as `HIGH_WIDE_CENTRAL`, `ELEVATED_ENDLINE` and `SIDELINE_OBLIQUE`.

`PillowFootballPitchRenderer` creates the actual opaque RGBA surface, exact markings, centre/penalty marks and deterministic mowing bands.

`FootballHybridComposer` replaces the entire reserved generative field region with that opaque deterministic surface, so malformed model-generated pitch markings cannot survive underneath it.

The composition receipt proves:
- deterministic geometry was applied,
- old generated markings were replaced,
- surface opacity is 255,
- deterministic mowing texture was applied.

Other sports may already declare exact-geometry requirements in `SportVisualRuleRegistry`, but they remain `UNAVAILABLE` until an actual deterministic renderer exists.

## Hybrid base-scene ownership

For scenes whose sport surface is deterministic, the image model is asked for:
- stadium/arena atmosphere,
- lighting,
- depth,
- crowd/environment mood,
- non-factual texture,
- a **plain unmarked surface region** reserved for deterministic replacement.

It is explicitly not asked for field/court/rink lines or exact sport geometry.

When hero identity belongs to a verified asset layer, the base-scene contract also asks the model not to invent a recognizable real-person face and to preserve usable composition space.

## Angle selection

When multiple verified angles are possible, the system ranks them by both editorial value and visual reliability.

Hard blocks:
- fact confidence below production floor,
- unverified required identity,
- invented-scene dependency,
- identity confidence below the locked threshold.

Visual penalties include excessive subjects, exact-text burden, exact-geometry burden, verbose copy and sensitive editorial treatment. A slightly less important but much safer angle can therefore be selected over a visually hostile one.

## Fact integrity

`EventFactSchemaRegistry` defines required/optional/exact slots for every event type.

`FactLockedEditorialAdapter` requires every used slot to be backed by an existing `LockedClaim(kind=FACT)` with matching slot metadata. Safe inference does not become fact merely because it would make a better image.

## QA stages

### Pre-composition leakage QA — `HybridLayerQualityGate`
Rejects generative leakage into deterministic/verified layers, including generated text, platform branding, exact numbers, entity marks, unverified identity and model-owned exact sport geometry.

### Receipt-backed evidence — `HybridVisualEvidenceBuilder`
A deterministic layer is not marked complete merely because the plan requested it. Football geometry completion requires a valid real `FootballHybridCompositionReceipt` proving opaque surface replacement.

### Final hybrid completion QA — `HybridVisualQualityGate`
Requires the exact layers that the plan demanded to actually be present: deterministic geometry, deterministic dynamic brand, deterministic typography, verified identity where applicable; also blocks severe generation defects and collage/split-scene output.

## Golden Hybrid v5

The active benchmark is:
- benchmark: `golden-visual-season-opener-hybrid-v5`
- manifest: `pul7sar-golden-batch-v5`
- geometry owner: `deterministic_football_pitch_projective_v1`
- `generated_sport_geometry_allowed=false`
- `hybrid_surface_replacement_required=true`
- camera preset: `high_wide_central`
- `generated_branding_allowed=false`
- branding policy: `dynamic_deterministic_after_generation`

This supersedes v4’s attempt to make FLUX draw a regulation pitch through increasingly detailed prompt constraints.

## CPU regression strategy

`tools/phase18_cpu_validate.py` uses discovery rather than a hand-maintained module list:
- syntax-check Phase 18 intelligence modules,
- discover all `test_phase18_*.py` tests,
- block GPU work on any regression.

A broad event-by-sport matrix exercises more than 800 editorial planning combinations without GPU generation.

## Colab policy

Colab is a GPU execution environment, not the source of project logic. GitHub remains authoritative.

The new target interaction is one command after the branch is present:

```python
%cd /content/pul7sar-bot
%run tools/phase18_colab_one_command.py --candidate 1 --force
```

The one-command flow:
1. fast-forwards the protected branch,
2. runs all discover-based Phase 18 CPU validation,
3. builds/verifies Golden Hybrid v5,
4. executes/reuses one atmosphere-only FLUX candidate,
5. replaces the reserved football surface with deterministic regulation geometry,
6. displays the hybrid proof.

It still reports `publication_ready=false`; exact final dynamic-brand geometry, typography and final visual QA remain separate gates.

## Current GPU position

GPU execution of FLUX.2 Klein on Tesla T4 has already been proven technically with sequential CPU offload. Earlier proofs were rejected for collage, malformed football geometry and generated pseudo-branding.

No Golden Hybrid v5 GPU proof has yet been accepted. The next GPU run is intended to test the new architecture, not another longer prompt.

## Production isolation

Phase 18 remains isolated on `phase18/story-intelligence`. The production entrypoint must remain untouched until the new pipeline clears its end-to-end gates.
