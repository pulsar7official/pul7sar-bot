# Phase 18 Change Set 143 — Original Scene Runtime Bridge

## Purpose

Advance PUL7SAR from story-specific visual-concept selection toward a provider-agnostic original-scene synthesis seam without weakening the existing zero-cost, semantic, identity, factual, geometry or publication gates.

## Added contracts

### `original_scene_runtime_contract.py`

Defines a provider-agnostic `OriginalSceneRequest` and an explicit runtime qualification contract. Generation owns only original non-factual scene pixels. Exact text, scores, platform identity and club crests remain deterministic compositor-owned layers. Identity-conditioned synthesis requires verified identity references and a downstream identity-fidelity gate.

### `original_scene_execution_gate.py`

Fail-closed admission gate. Missing, unqualified, externally dependent, non-portable, non-original or semantically unchecked runtimes are rejected. Admission never implies publication readiness.

### `original_scene_request_builder.py`

Translates a renderer-independent `VisualConceptDecision` into either atmosphere synthesis or identity-conditioned synthesis. Deterministic concepts never enter the generator runtime.

### `original_scene_local_bridge.py`

Connects the new provider-agnostic request contract to the existing local `$0` execution stack only after measured `LocalGenerationReadinessReport` evidence exists.

The bridge:

- derives qualification from the actual selected model and readiness report rather than model naming;
- requires `local_cuda`, a proven model runtime floor, a matching provider/model/backend identity and `$0-local` economics;
- admits FLUX.2 Klein 4B only for atmosphere synthesis under the current model-role contract;
- does not silently promote the engineering FLUX profile into an identity-conditioned runtime;
- reuses `PromptConstraintCompiler` so FLUX-like runtimes cannot silently drop forbidden constraints;
- reserves branding, exact facts and exact sport geometry for deterministic downstream composition;
- requires semantic inspection after generation;
- keeps `publication_ready=false` in both the bridge receipt and local generation request metadata.

## Tests

Added regression coverage for:

- missing/unqualified original-scene runtimes;
- measured ready CUDA admission;
- CPU/unready rejection;
- runtime-kind mismatch;
- prohibition on silently treating FLUX.2 Klein as an identity-conditioned runtime;
- `$0-local` request compilation;
- protected platform-name redaction;
- exact-fact/brand/sport-geometry reservation;
- readiness identity drift;
- fail-closed handling of forbidden visual claims that have no deterministic provider translation.

## Files

Added:

- `engine/intelligence/original_scene_runtime_contract.py`
- `engine/intelligence/original_scene_execution_gate.py`
- `engine/intelligence/original_scene_request_builder.py`
- `engine/intelligence/original_scene_local_bridge.py`
- `tests/test_phase18_original_scene_runtime_contract.py`
- `tests/test_phase18_original_scene_execution_gate.py`
- `tests/test_phase18_original_scene_request_builder.py`
- `tests/test_phase18_original_scene_local_bridge.py`
- this document

Deleted: nothing.

## Gates preserved

No change was made to Fact Lock, identity verification, neutrality/sentiment, `$0-local`, FLUX.2 Klein 4B, BF16, seed/canvas locks, Qwen BASE_SCENE/HYBRID_SURFACE inspection, deterministic football geometry, Golden 8.5/9.0 quality thresholds, exact brand/typography integrity or `SemanticPublicationGate`.

No paid provider, secret, hosted-GPU fallback, fake PNG or publication bypass was introduced.

## Remaining integration step

The new bridge now proves that a story-specific provider-agnostic scene request can be admitted by the measured local runtime and compiled into a locked local request. The next integration step is to bind the Golden Candidate 1 runtime path to this admission seam after GPU readiness, while retaining the existing Golden Hybrid v5 handoff/provenance format and all downstream semantic/human/Golden review gates.
