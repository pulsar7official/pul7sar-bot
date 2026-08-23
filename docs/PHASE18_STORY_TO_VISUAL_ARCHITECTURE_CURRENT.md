# PUL7SAR Phase 18 — Current Story-to-Visual Architecture

Status: active development on `phase18/story-intelligence`.

This document is the canonical snapshot of the current architecture. Older numbered change-set documents remain historical implementation notes; where numbering overlaps because the architecture evolved rapidly during live GPU diagnosis, this file describes the current intended system.

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
- what fallback to use if a capability is unavailable.

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
→ `HybridVisualLayerPlanner`
→ `EditorialVisualAuthorizationGate`
→ production actions:
  - safe generative atmosphere only when useful,
  - deterministic geometry/data/typography,
  - verified identities/marks/PUL7SAR assets,
→ `HybridLayerQualityGate` for generated-layer leakage
→ deterministic/verified composition
→ `HybridVisualQualityGate` for required-layer completion
→ semantic verification
→ strict Golden visual-quality gate
→ final export.

## Editorial-event taxonomy

The current `EditorialEvent` vocabulary covers:
- result,
- live moment,
- preview,
- confirmed transfer,
- transfer rumour,
- contract,
- injury,
- comeback,
- suspension,
- retirement,
- appointment,
- dismissal,
- statement,
- record,
- award,
- trophy,
- draw,
- table,
- tactics,
- officiating,
- controversy,
- financial news,
- organization news,
- schedule,
- qualification,
- elimination,
- general stories.

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
| PUL7SAR logo / number 7 / pulse / social footer | exact verified asset |

Generated PUL7SAR text, pseudo-logos, fake scores, fake statistics, fake club crests and generated exact sport geometry are architectural violations, not aesthetic imperfections.

## Scene-complexity rule

The visual system uses the minimum physical complexity needed by the story.

A football transfer does not need a full football pitch. An injury does not need a generated stadium. A record may be better as a verified hero + exact number. A result can use partial deterministic sport context. Tactics may require the full deterministic surface because the surface geometry is itself part of the information.

When exact geometry is required but no renderer exists, PUL7SAR either removes that surface from a safe partial-context design or blocks the visual path entirely. It never asks diffusion to improvise the missing exact geometry.

## Current sport-rule coverage

Explicit visual rules currently cover more than thirty sport families including football, basketball, tennis, padel, badminton, volleyball, handball, baseball, American football, rugby, cricket, golf, boxing, MMA, wrestling, judo, taekwondo, athletics, Formula 1, motorsport, swimming, cycling, rowing, sailing, ice hockey, winter sports, table tennis, snooker, darts, gymnastics, weightlifting, equestrian and esports.

Unknown sports receive a conservative fallback instead of fabricated geometry knowledge.

## Deterministic geometry capability

Policy requirement and implementation readiness are separate.

Current implemented deterministic sport renderer:
- football: `football_pitch_projective_v1`

The football geometry system owns a stable 105m × 68m reference surface and exact primitives for boundary/halfway lines, centre circle/mark, penalty areas, goal areas, penalty marks, penalty arcs and corner arcs. A projective homography maps those world coordinates into a four-corner image plane, and a Pillow renderer creates the actual RGBA overlay.

Other sports may already declare exact-geometry requirements in `SportVisualRuleRegistry`, but they remain `UNAVAILABLE` in `DeterministicGeometryCapabilityRegistry` until an actual renderer exists.

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
Rejects generative leakage into deterministic/verified layers, including generated text, PUL7SAR branding, exact numbers, entity marks, unverified identity and model-owned exact sport geometry.

### Final hybrid completion QA — `HybridVisualQualityGate`
Requires the exact layers that the plan demanded to actually be present: deterministic geometry, exact PUL7SAR brand, deterministic typography, verified identity where applicable; also blocks severe generation defects and collage/split-scene output.

These two gates are intentionally distinct: the first protects ownership boundaries in the base scene; the second verifies that final composition did not omit required exact layers.

## CPU regression strategy

Before GPU use, the Colab runner now includes the Story-to-Visual, fact-schema, angle-selection, sport-rule, geometry-capability, hybrid-layer, authorization, QA and football geometry/projection regressions.

A broad event-by-sport matrix exercises more than 800 editorial planning combinations without GPU generation. Every combination must either produce an explicitly authorized visual action plan or fail closed with a known capability blocker.

## Colab policy

Colab is a GPU execution environment, not the source of project logic. GitHub remains authoritative.

The target interaction remains one command:

```python
%cd /content/pul7sar-bot
%run tools/phase18_colab_runner.py --update --candidate 1
```

The runner must refuse stale Golden manifests, wrong branches, failed CPU regressions, incompatible GPU readiness and identity/SHA mismatches before wasting GPU time.

## Branding

The generative model must never draw the PUL7SAR logo or wordmark. Final branding uses an exact approved asset with integrity verification. The repository currently contains candidate image assets, but the final approved logo file must be visually confirmed before its checksum is locked into final composition.

## Current GPU position

GPU execution of FLUX.2 Klein on Tesla T4 has been proven technically with sequential CPU offload. Earlier real proofs were rejected for collage, malformed football geometry and generated pseudo-PUL7SAR branding. No new GPU generation should be treated as useful evidence until the current hybrid architecture and exact-asset path are validated through CPU preflight.

## Production isolation

`main.py` remains byte-identical between `main` and `phase18/story-intelligence` at the current checked state. Phase 18 work remains isolated from the production publisher.
