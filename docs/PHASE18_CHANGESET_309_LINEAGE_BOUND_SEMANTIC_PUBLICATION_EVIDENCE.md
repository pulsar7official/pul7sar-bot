# Phase 18 Change Set 309 — Lineage-Bound Semantic Publication Evidence

## Purpose

Close the last proven evidence-substitution surface immediately before Genuine Golden materialization.

CS283 already requested a real repository `SemanticPublicationGate` execution, but CS284 v1 accepted an external JSON evidence file after checking only Story SHA and composed-PNG SHA during execution.  Its replay verifier did not repeat even those two raw-evidence checks.  Therefore a same-story/same-PNG evidence payload could carry a different `GenerationPackage`, `BaseSceneEvidence`, or `VisionVerifierProfile` without proving that the payload belonged to the exact CS283/CS282 run.

## Contract

CS284 is upgraded to v2.  Before `SemanticPublicationGate.evaluate(...)` may run, the evidence envelope must now:

- use `pul7sar-phase18-semantic-publication-evidence-v2`;
- bind the exact CS283 request by repository-relative path, file SHA-256, byte size, and receipt SHA-256;
- bind the exact CS282 final-semantic parent already embedded in CS283;
- bind the exact composed PNG metadata, not only its SHA;
- bind the exact inherited generation context;
- repeat Story/PNG/CS282 lineage inside `GenerationPackage.metadata`;
- repeat Story/PNG/CS282 lineage inside `BaseSceneEvidence.provenance`;
- make `BaseSceneEvidence.output_ref` point at the exact composed PNG repository path;
- prove `VisionVerifierProfile.local_zero_cost=true` and `requires_network=false` before gate evaluation;
- bind the verifier envelope to `$0-local`, `network_allowed=false`, and `local_files_only=true`.

The identical lineage checks are replayed by `verify_semantic_publication_execution`; verification may no longer ignore raw evidence Story/PNG lineage.

## Authority boundaries

This change does **not** decide whether a visual is semantically publishable.  `SemanticPublicationGate` remains the sole decision authority at CS284.  CS309 does not create pixels, approve identity, relax factual/sentiment rules, bypass Human Review, or set `genuine_golden_png_created` / `publication_ready`.

The evidence envelope remains evidence input; this change proves which exact run it belongs to and reasserts zero-cost/offline execution.  Pixel authenticity still depends on the already-required upstream semantic, identity, visual-quality, Human Review, brand, and typography lineage plus the gate's own evaluation.

## Files

Added:
- `engine/intelligence/qwen_image_semantic_publication_evidence_lineage.py`
- `tests/test_phase18_qwen_image_semantic_publication_evidence_lineage.py`
- this Change Set document
- `docs/PHASE18_IMPLEMENTATION_LOG_309.md`

Modified:
- `engine/intelligence/qwen_image_composed_candidate_semantic_publication_execution.py`

Deleted: none.
