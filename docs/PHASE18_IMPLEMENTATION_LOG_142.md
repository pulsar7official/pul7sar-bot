# PUL7SAR Phase 18 — Implementation Log 142

## Scope

Branch: `phase18/story-intelligence` only.

`main` was reviewed before implementation and was not modified, merged, force-updated, or used as a write target.

At the start of this change set, the observed Phase 18 head was `647de06dc5dcce642bda018318725b18335fd24c`; the observed `main` head was `8af6411547eabd893233e501ce1442c7aba8ded6`. The branch comparison reported `diverged`, ahead by 1248 commits and behind by 121 commits.

The starting Phase 18 head was CI-green: Story Intelligence Verification run `32818544870 / 2343` and the visible companion Phase 18 CPU workflows completed successfully.

The starting head already contained the new story-specific `VisualConceptDirector` and its routing through `StoryToVisualOrchestrator`. Change Set 142 advances that work into the actual generation package and Golden Hybrid v5 portable handoff.

## Change Set 142 — Visual Concept Generation Binding

### Problem addressed

The story pipeline could select a visual concept before renderer execution, but `GenerationPackageCompiler` did not accept that concept. As a result, the selected picture idea was not guaranteed to reach FLUX.2 even though VisualGrammar and scene information did.

A second issue affected the Golden season-opener benchmark: generic event news with no verified context photograph needed a way to use a cinematic generated atmosphere without implying that a specific real stadium, club, match or person had been verified. The previous event fallback was intentionally minimal and therefore could conflict with the Golden benchmark's legitimate need for a generic football atmosphere.

A third integration gap became visible after the initial package change: the provider-neutral `GenerationPackage` could carry the concept metadata, but `LocalBackendRequestCompiler` did not yet propagate it into the portable FLUX handoff. That boundary is now explicitly covered.

### Added

- `docs/PHASE18_CHANGESET_142_VISUAL_CONCEPT_GENERATION_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_142.md`

### Modified

#### `engine/intelligence/visual_concept_director.py`

- added `VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE`;
- added `VisualConceptSignals.safe_generated_context`;
- added a safe event path that permits only non-identifying, non-factual generated atmosphere;
- explicitly forbids specific real venue identity and specific real-person depiction in that path;
- retained the minimal-symbol fallback when generated context is not authorized.

#### `engine/intelligence/story_to_visual_orchestrator.py`

- event-editorial stories now expose safe generated context by default only for `EVENT_EDITORIAL`;
- story metadata can explicitly disable it with `allow_generated_context=false`;
- no person, identity, club, result or exact-geometry ownership was transferred to generation.

#### `engine/intelligence/generation_package.py`

- added optional `visual_concept: VisualConceptDecision` input;
- binds concept archetype, hero direction and environment role into the actual generation prompt;
- records visual-concept contract/family/archetype/provider-agnostic/asset-priority/forbidden metadata;
- keeps `visual_concept_publication_ready=false`;
- filters brand-named concept motifs from the generative prompt so PUL7SAR/PULSAR prompt redaction remains intact.

#### `engine/intelligence/local_backend_execution.py`

- propagates visual-concept contract, family, archetype, provider-agnostic flag, selected-before-renderer flag, asset priorities, forbidden motifs and publication-false state from `GenerationPackage` into `LocalBackendGenerationRequest`;
- keeps the visual concept SHA/provenance boundary aligned with the existing VisualGrammar metadata path rather than inventing a parallel handoff format.

#### `engine/intelligence/provider_prompting.py`

- added deterministic FLUX-compatible positive reframes for `no specific identifiable real venue` and `no specific real-person depiction`;
- preserves the existing rule that a backend without native negative prompts may not silently drop any forbidden constraint.

#### `tools/phase18_build_golden_handoff.py`

- Golden Hybrid v5 now constructs an `EVENT_EDITORIAL` visual concept before compiling the FLUX.2 package;
- selects `generative_event_atmosphere` for the general season-opener benchmark;
- explicitly states that the generated stadium/event world is deliberately non-identifying;
- forbids implying a specific real venue, club, match or person;
- passes the visual concept into `GenerationPackageCompiler`;
- exposes the concept archetype in the CLI summary and portable-handoff metadata.

#### Tests

Updated:

- `tests/test_phase18_visual_concept_director.py`
- `tests/test_phase18_story_to_visual_orchestrator.py`
- `tests/test_phase18_generation_layout.py`
- `tests/test_phase18_local_backend_execution.py`
- `tests/test_phase18_golden_handoff.py`

Coverage now verifies safe generated event atmosphere, explicit minimal fallback, prompt propagation, package metadata propagation, provider-neutral → local handoff metadata propagation, brand-name redaction, complete positive reframing of non-identifying constraints, Golden venue/person non-identification and unchanged deterministic seed behavior.

### Deleted

Nothing.

## Safety and publication gates preserved

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

## Testing status

The branch head at the start of the work was verified green. The Change Set 142 code, tests and documentation were pushed to `phase18/story-intelligence`, and new GitHub Actions runs were triggered.

This log intentionally does not claim the new head is CI-green until the Story Intelligence verification run for the final code/test state has completed successfully.

## Remaining blocker to the first genuine Golden Visual PNG

A genuine Golden Hybrid v5 Candidate 1 still requires a compatible NVIDIA CUDA + BF16 host capable of running the locked FLUX.2 Klein 4B path and Qwen semantic stages.

The current automation environment does not provide that execution capability. No PNG, benchmark or visual-quality result was fabricated.

The next genuine GPU session should still run Candidate 1 only. The difference after Change Set 142 is that the portable handoff now carries the story-specific picture idea itself end-to-end from concept selection through the local FLUX request, rather than relying only on generic scene/family directions, while continuing to keep all exact factual, identity, brand, text and football-geometry layers outside generation.
