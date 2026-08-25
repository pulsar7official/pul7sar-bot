# PUL7SAR Phase 18 — Change Set 142

## Story-specific Visual Concept binding into the real generation handoff

### Purpose

The branch already contained a provider-agnostic `VisualConceptDirector` and `StoryToVisualOrchestrator` routing, but the concept decision stopped before `GenerationPackageCompiler`. That meant a story could select a strong concept such as decisive moment, verified portrait, score monument or event concept while the image model still received only the older specification/VisualGrammar directions.

Change Set 142 closes that gap and makes the selected picture idea part of the portable FLUX.2 handoff without transferring ownership of facts, identity, branding, text, scores, crests or exact sport geometry to the generator.

### Added behavior

- `VisualConceptSignals.safe_generated_context` distinguishes safe, non-factual atmosphere generation from fabricated real-world context.
- `VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE` allows general previews/events to use a photorealistic but deliberately non-identifying sports world when no verified context photograph exists.
- The default minimal-symbol fallback remains available when generated context is explicitly disabled.
- `StoryToVisualOrchestrator` enables safe generated context only for `EVENT_EDITORIAL` and allows story metadata to disable it with `allow_generated_context=false`.
- `GenerationPackageCompiler` accepts an optional `VisualConceptDecision` and binds its archetype, hero direction and environment role into the actual generation prompt.
- Concept-specific forbidden motifs are propagated only when they are safe to expose to the image model; any motif containing the PUL7SAR/PULSAR brand name is withheld from the generative prompt so the existing brand-name redaction remains intact.
- Visual-concept provenance is recorded in generation-package metadata for downstream handoff and QA.
- Golden Hybrid v5 now explicitly selects `generative_event_atmosphere` before FLUX.2 and forbids implying a specific real venue, club, match or person.

### First-Golden impact

The next genuine Candidate 1 will no longer be guided only by the generic season-opener scene specification. Its portable FLUX.2 handoff now also carries a story-specific visual-concept contract that states the picture idea before renderer execution.

For the season-opener benchmark, the intended generated layer is:

- one continuous premium football atmosphere;
- non-identifying stadium/event world;
- no claim that the venue is a specific real stadium;
- no real-person depiction;
- no generated readable text, platform branding or exact sport geometry;
- only restrained partial turf context for later deterministic geometry.

This keeps the cinematic direction needed for the Golden Visual while preserving factual and identity integrity.

### Tests expanded

Regression coverage now includes:

- safe generated event atmosphere selection;
- explicit fallback to a minimal event symbol when generated context is disabled;
- visual-concept propagation into the generation prompt;
- concept metadata propagation into the portable handoff;
- continued PUL7SAR/PULSAR prompt redaction;
- Golden v5 non-identifying venue/person constraints;
- deterministic behavior for identical seed/request inputs.

### Safety gates preserved

No weakening or bypass was introduced for:

- Fact Lock;
- entity/identity verification;
- sentiment/neutrality and respectful losing-side treatment;
- `$0-local` policy;
- FLUX.2 Klein 4B lock;
- native BF16 lock;
- Candidate/seed/canvas locks;
- generated text/branding/exact-number/entity-mark/sport-geometry exclusions;
- Qwen BASE_SCENE semantic/layer ownership gate;
- deterministic football geometry and artifact-integrity replay;
- Qwen HYBRID_SURFACE semantic/alignment gate;
- human-review SHA locks;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- exact brand and typography integrity;
- SemanticPublicationGate.

No paid provider, hosted GPU fallback, secret, fake PNG, fake benchmark or publication bypass was added.
