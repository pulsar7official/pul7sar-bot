# Phase 18 — Change Set 284: Semantic Publication Execution

## Purpose

CS284 is the first post-CS283 stage that executes the repository's real `SemanticPublicationGate`. It does not accept an externally supplied publication verdict and it does not create a Genuine Golden PNG.

## Inputs

1. A verified CS283 semantic-publication execution request.
2. An external JSON evidence document, stored inside the repository work tree for byte binding, containing:
   - the exact Story Snapshot SHA-256;
   - the exact composed-candidate PNG SHA-256;
   - a serialized `GenerationPackage`;
   - a serialized `BaseSceneEvidence`;
   - a serialized zero-cost `VisionVerifierProfile`.

## Evaluation

CS284 reconstructs the repository dataclasses and calls `SemanticPublicationGate().evaluate(...)` directly. Therefore `semantic_publication_allowed` is derived only from the existing repository gate.

The gate independently evaluates base-scene acceptance, zero-cost/local semantic-verifier completeness, identity requirement consistency, and verified identity-reference continuity.

## Fail-closed invariants

- CS283 must still verify against the current repository policy bytes.
- The execution-evidence file is byte-bound by repository-relative path, SHA-256 and byte size.
- Story SHA and composed PNG SHA must match CS283.
- Unknown verifier capabilities are rejected.
- Paid/non-local or network-dependent verification cannot become eligible under the zero-cost policy.
- Identity-required scenes need identity verification capability and matching reference IDs.
- No CLI argument can override `semantic_publication_allowed`.
- Even `semantic_publication_allowed=true` leaves `genuine_golden_png_created=false` and `publication_ready=false`.

## Authority boundary

CS284 may establish:

- `semantic_publication_gate_executed=true`
- `semantic_publication_allowed=true|false`

It may not establish:

- `genuine_golden_png_created=true`
- `publication_ready=true`

Those remain downstream authorities tied to the existence and byte identity of a real production PNG.
