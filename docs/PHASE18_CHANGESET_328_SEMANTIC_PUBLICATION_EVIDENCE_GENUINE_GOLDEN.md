# Phase 18 — Change Set 328: Semantic Publication Evidence → Genuine Golden

## Purpose

CS328 removes the manual lineage-selection gap between a CS327 semantic-publication request, a real pre-existing CS284 `SemanticPublicationGate` execution receipt, and CS285 Genuine Golden materialization.

It does **not** execute CS284, infer or override `semantic_publication_allowed`, generate pixels, alter pixels, or grant publication readiness.

## Required inputs

- an exact repository-local CS327 checkpoint in `SEMANTIC_PUBLICATION_EXECUTION_EVIDENCE_REQUIRED` state;
- the exact CS283 receipt selected by that checkpoint;
- a pre-existing repository-local CS284 receipt whose own verifier can replay the bound evidence through the repository `SemanticPublicationGate`;
- the exact composed PNG bytes already bound by CS327/CS283/CS284.

## Fail-closed lineage

Before CS285 can be called, CS328 requires:

1. CS327 schema/status/authority invariants;
2. current composed-PNG SHA-256 and byte-size equality with the CS327 binding;
3. independent CS283 verification and exact Story/PNG continuity;
4. independent CS284 verification, which itself re-runs `SemanticPublicationGate` from its bound `GenerationPackage`, `BaseSceneEvidence`, and `VisionVerifierProfile` evidence;
5. exact CS284 → CS283 source binding by repository path, SHA-256, byte size, and CS283 `receipt_sha256`;
6. `semantic_publication_gate_executed=true`;
7. `semantic_publication_allowed=true` from the verified repository gate;
8. an empty `semantic_publication_failures` list;
9. no premature Genuine-Golden or publication-ready state.

Any rejection, Story drift, receipt substitution, or composed-byte drift stops before CS285 materialization.

## Genuine Golden materialization

Only after the preceding checks does CS328 invoke the existing CS285 `materialize_genuine_golden_visual` contract. CS285 validates PNG framing/CRC/dimensions, copies the already-approved composed PNG byte-for-byte, and verifies the materialized artifact independently.

CS328 then requires the source composed PNG and Genuine Golden PNG to retain identical SHA-256 and byte size. No image generation, re-encoding, resizing, branding edit, text edit, or other pixel mutation is permitted.

## Authority boundary

Successful CS328 may report:

- `composed_visual_approved=true`;
- `semantic_approved=true`;
- `semantic_publication_gate_executed=true`;
- `semantic_publication_allowed=true`;
- `byte_identity_preserved=true`;
- `genuine_golden_png_created=true`.

It must retain:

- `publication_ready=false`;
- checkpoint `authoritative=false`.

CS286 remains a separate final publication-readiness authority and is intentionally not invoked by CS328.

## Safety and cost posture

The change does not modify factual/freshness, identity/entity, sentiment neutrality/loser-respect, zero-cost/local-only, semantic, visual-quality, Human Visual Review, brand, typography, or publication policies. Hugging Face/Transformers/Datasets are forced to offline mode defensively before deterministic CS285 materialization.

## Runtime limitation

CS328 closes a downstream wiring gap only. It does not remove the requirement for a genuine upstream candidate and composed production PNG. If compatible zero-cost CUDA/BF16 execution and approved already-local Qwen assets are unavailable, no genuine Golden result may be claimed.
