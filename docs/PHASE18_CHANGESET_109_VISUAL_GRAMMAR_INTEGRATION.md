# PUL7SAR Phase 18 — Change Set 109

## Provider-Agnostic Visual Grammar Integration

Change Set 109 advances Phase 18 toward the first genuine Golden Visual while reducing an architectural over-dependence on full football-pitch imagery.

The branch already contained a provider-agnostic `VisualGrammar` contract. This change connects that contract to the actual Story-to-Visual decision and generation-package compiler, so art direction is now resolved before a provider is chosen and can explicitly say when a sports surface must be absent, partial/deterministic, or full/deterministic.

## Added behavior

### Story decision now carries visual grammar
`StoryToVisualOrchestrator` now creates and returns a `VisualGrammarDecision` alongside the editorial plan. This keeps copy, editorial angle, visual family, production mode, camera language, fantasy restraint, generated elements and deterministic ownership inside one auditable decision.

Important consequence: a football story no longer inherits a full-pitch requirement merely because the sport is football.

Examples enforced by tests:
- confirmed transfer -> no sport-surface dependency;
- result -> partial deterministic surface only;
- tactics -> full deterministic surface and no generative geometry;
- low-confidence verified-asset fallback -> no generated elements.

### Generation package consumes visual grammar
`GenerationPackageCompiler.compile(...)` now accepts an optional `VisualGrammarDecision`.

When supplied, provider-neutral prompt guidance is added for:
- camera language;
- fantasy restraint;
- environment direction;
- lighting direction;
- composition direction;
- sport-surface visibility.

Surface policy is explicit:
- `none`: do not make a pitch/court/rink/track/stadium surface the visual subject;
- `partial_deterministic`: allow only restrained incidental context and forbid exact generated markings;
- `full_deterministic`: reserve a compatible region but still forbid the generator from owning exact surface/tactical geometry.

The package metadata also records the visual-grammar contract, provider-agnostic flag, surface visibility, camera language, fantasy level, generated elements, deterministic elements and forbidden generated elements.

## Safety and ownership preserved
- PUL7SAR brand name remains redacted from the image-model prompt.
- Generated platform branding remains forbidden.
- Exact club/competition marks remain deterministic assets.
- Scores, exact data and typography remain deterministic.
- Fact Lock, Identity Verification, sentiment/result neutrality and semantic-publication gates are unchanged.
- `$0-local`, FLUX.2 Klein 4B, BF16, seeds and canvases are unchanged.
- Golden 8.5 minimum / 9.0+ elite thresholds are unchanged.
- This integration is provider-agnostic; FLUX remains the current zero-cost execution path but the visual identity is no longer coupled to one generator.

## Files modified
- `engine/intelligence/story_to_visual_orchestrator.py`
- `engine/intelligence/generation_package.py`
- `tests/test_phase18_story_to_visual_orchestrator.py`
- `tests/test_phase18_generation_layout.py`

## Files added
- `docs/PHASE18_CHANGESET_109_VISUAL_GRAMMAR_INTEGRATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_109.md`

## Files deleted
- None.

## Why this materially reduces the remaining gap
The next genuine Candidate 1 should be generated from a story-specific art-direction contract rather than a generic football-world assumption. That makes it possible for transfer, injury, contract, statement and similar news to avoid unnecessary stadium/pitch imagery, while result/tactics cases retain deterministic geometry only when editorially justified.

This change does not fabricate a GPU result. A genuine Golden Hybrid v5 PNG still requires a compatible CUDA/BF16 execution host.
