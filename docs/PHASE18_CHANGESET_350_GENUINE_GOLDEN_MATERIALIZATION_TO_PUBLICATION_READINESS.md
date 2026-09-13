# Phase 18 — Change Set 350
## Genuine Golden Materialization → Publication Readiness

### Scope
Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

This change set connects the current exact CS349 checkpoint to the repository's existing CS286 Genuine Golden publication-readiness contract. It does not modify `main`, generate pixels, mutate pixels, execute SemanticPublicationGate again, publish, upload, or invent external authority.

## Existing contracts reused

### CS349
`engine/intelligence/qwen_image_semantic_publication_gate_to_genuine_golden_materialization.py`

CS349 independently replays the allowed CS284 semantic-publication result, invokes existing CS285, preserves exact source/Golden byte identity, and stops with:

- `genuine_golden_png_created=true`
- `publication_ready=false`
- `authoritative=false`

### CS285
`engine/intelligence/qwen_image_genuine_golden_materialization.py`

CS285 validates the PNG container and materializes `genuine_golden_visual.png` from the exact CS284-approved composed bytes. It does not generate or alter image pixels and deliberately leaves publication readiness false.

### CS286
`engine/intelligence/qwen_image_genuine_golden_publication_readiness.py`

CS286 is the existing final Qwen-chain readiness contract. It:

1. re-verifies exact CS285;
2. re-opens the exact composed source and Genuine Golden PNG;
3. requires exact byte identity;
4. validates the Golden PNG structure/dimensions again;
5. records `publication_ready=true` only for that verified artifact;
6. performs no actual publication/upload side effect.

## CS350 continuation

New module:

`engine/intelligence/qwen_image_genuine_golden_materialization_to_publication_readiness.py`

The continuation executes only this lineage:

```text
exact CS349
  → independent CS349 replay
  → exact CS349-selected CS285 receipt
  → independent CS285 replay
  → require Golden/source byte identity
  → existing CS286 exactly once
  → independent CS286 replay
  → publication_ready=true
  → STOP before any external publish/upload authority
```

## Admission rules

CS350 rejects the path if any of the following is true:

- CS349 schema/status is not exact;
- CS349 does not carry the already-established composed, semantic, semantic-publication, byte-identity, and Genuine Golden authorities;
- CS349 already claims publication readiness or external authority before CS286;
- the CS285 receipt selected by CS349 cannot be reopened exactly;
- the CS285 receipt hash drifts;
- CS285 story, composed PNG, Golden PNG, or authority state drifts from CS349;
- source and Golden SHA-256 or byte size differ;
- CS286 does not return its exact schema/status;
- CS286 story, source/Golden bindings, dimensions, generation context, score, tier, or upstream authorities drift from CS285;
- the final Golden PNG binding changes.

All failures are fail-closed.

## Authority boundary

CS350 may record:

- `composed_visual_approved=true`
- `semantic_approved=true`
- `semantic_publication_gate_executed=true`
- `semantic_publication_allowed=true`
- `byte_identity_preserved=true`
- `genuine_golden_png_created=true`
- `publication_ready=true`

CS350 deliberately keeps:

- `authoritative=false`

This is important: repository publication readiness is not an upload, social-media post, API publication call, or other external side effect. No such operation is introduced here.

## Preserved upstream gates

CS350 does not weaken or bypass any upstream requirement. The exact lineage entering it already contains the factual/freshness, entity/identity, sentiment-neutrality/loser-respect, zero-cost/offline, semantic QA, visual-quality, Golden-quality, Human Visual Review, Presentation/Brand/Typography, Final Composed, Final Semantic, and real SemanticPublicationGate decisions. CS350 only replays their downstream materialization/readiness lineage.

## Regression coverage

`tests/test_phase18_qwen_genuine_golden_materialization_to_publication_readiness.py` covers:

- exact CS349 → CS285 → existing CS286 once-only success;
- preservation of exact Golden bytes;
- rejection of premature CS349 publication readiness;
- rejection of CS285 receipt-hash drift before CS286;
- rejection of CS286 Golden binding drift;
- static guards against model loading, network fallback, re-materialization, SemanticPublicationGate re-execution, upload/publish calls, and external `authoritative=true` shortcuts.

## Runtime caveat

CS350 does not make a production Genuine Golden artifact exist by itself. A real artifact still requires a genuine Qwen candidate produced on an approved zero-cost compatible runtime and the complete upstream gate chain to succeed on that candidate. In the currently measured execution environment, PyTorch is CPU-only and no compatible CUDA GPU is available; therefore no production Golden PNG is claimed by this change set.
