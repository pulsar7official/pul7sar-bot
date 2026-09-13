# Phase 18 Change Set 319 — Deterministic Composition Preparation Checkpoint

## Objective

Reduce the operator gap between an approved CS268 generated-layer candidate and deterministic composition without fabricating or auto-authoring any composition input.

CS319 introduces one non-authoritative preparation checkpoint that reuses the existing CS269 and CS270 contracts. It accepts only explicit repository files supplied by the operator/project and stops before any pixel composition is executed.

## Contract

Input lineage begins with an exact CS268 receipt whose `generated_layer_qa_approved` value is `true`. The checkpoint independently replays that receipt and requires all downstream authorities to remain closed.

The checkpoint then requires an explicit repository-bound CS269 composition input manifest. It does not synthesize editorial typography, PUL7SAR brand assets, verified identity/entity assets, exact sport geometry, score/data payloads, or renderer contracts.

If CS269 is READY and an explicit repository-bound deterministic payload manifest is supplied, the checkpoint builds and independently replays CS270. CS270 reopens each deterministic payload file and requires its SHA-256 digest and renderer contract to match the exact CS269 request.

## Fail-closed outcomes

The checkpoint reports exactly one of four preparation states:

- `COMPOSITION_INPUT_MANIFEST_BLOCKED`
- `DETERMINISTIC_PAYLOAD_MANIFEST_REQUIRED`
- `DETERMINISTIC_PAYLOAD_BINDING_BLOCKED`
- `COMPOSITION_EXECUTION_PREFLIGHT_READY`

`COMPOSITION_EXECUTION_PREFLIGHT_READY` is not composition execution. It only means the exact, repository-bound CS269/CS270 inputs are coherent enough for the already-existing composition execution stage to be considered next.

## Authority boundary

CS319 is explicitly non-authoritative and always keeps these fields false:

- `composition_executed`
- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

It does not modify factual, freshness, identity, sentiment/loser-respect, `$0-local`, semantic-publication, Golden-quality, human-review, brand/typography, or publication gates.

## Security and provenance properties

- Output must remain inside the repository.
- Composition and payload manifests must already exist as repository files.
- CS268, CS269 and CS270 are independently replay-verified.
- Story SHA and exact candidate binding must remain identical across the entire checkpoint.
- Missing payload files remain explicit blockers.
- No network, model inference, renderer invocation, image decode/re-encode, or publication side effect is introduced.

## Why this materially reduces the Golden gap

Before CS319, after CS268 the operator had to manually coordinate CS269 and CS270 and determine whether the remaining blocker belonged to the composition-input layer or to deterministic payload materialization.

CS319 turns that into one fail-closed checkpoint while preserving the deliberate requirement that factual text, verified marks/assets, geometry, and deterministic payload bytes come from their proper owners rather than being invented by orchestration code.
