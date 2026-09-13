# Phase 18 — Change Set 283

## Semantic Publication Execution Request

CS283 creates a fail-closed request to execute the repository's existing `SemanticPublicationGate` against the exact CS282-approved story/image lineage.

It deliberately does **not** execute, replace, weaken, or emulate `SemanticPublicationGate`. The existing gate remains authoritative for base-scene acceptance, zero-cost semantic-verifier eligibility, identity-required intent, and verified identity-reference consistency.

### Preconditions

CS282 must verify successfully and must prove:

- `composed_visual_approved=true`
- `semantic_approved=true`
- `genuine_golden_png_created=false`
- `publication_ready=false`

The exact composed PNG is reopened and byte-verified.

### Policy-source binding

The request binds the exact repository bytes of:

- `engine/intelligence/semantic_publication_gate.py`
- `engine/intelligence/base_scene_quality.py`
- `engine/intelligence/vision_verification_policy.py`
- `engine/intelligence/generation_package.py`

Any subsequent byte drift invalidates the request rather than silently evaluating under changed publication policy.

### Authority boundaries

CS283 may set only `semantic_publication_execution_requested=true`.

It must keep all of the following closed:

- `semantic_publication_gate_executed=false`
- `semantic_publication_allowed=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`

A later evidence/execution stage must reconstruct the real `GenerationPackage`, real `BaseSceneEvidence`, and real zero-cost `VisionVerifierProfile`, execute the existing `SemanticPublicationGate`, and bind its decision to this request and the exact PNG bytes.

### Preserved gates

No factual, identity, sentiment, loser-respect, zero-cost, Golden-quality, human-review, brand, typography, composed-visual, semantic, or publication gate is modified by CS283.
