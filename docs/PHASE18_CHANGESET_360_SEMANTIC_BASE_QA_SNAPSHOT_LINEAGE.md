# Phase 18 Change Set 360 — Semantic Base QA Snapshot Lineage

## Purpose

Preserve the exact Qwen-Image generator snapshot byte lineage across the first real post-CS359 consumer: the existing CS304 canonical-candidate semantic base-scene QA contract.

CS359 already proves and seals the exact candidate bytes plus the approved local Qwen-Image snapshot inventory at post-generation byte admission. Before CS360, CS304 freshly replayed CS359 but only carried candidate/story/handoff bindings into its own receipt, dropping the generator snapshot inventory as first-class downstream evidence.

CS360 upgrades the existing CS304 contract rather than introducing a parallel gate.

## Contract change

`engine/intelligence/qwen_image_canonical_candidate_semantic_base_qa.py` now:

- upgrades `CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA` from v2 to v3;
- requires the fresh CS359 admission replay to expose `snapshot_byte_inventory_verified=true`;
- validates and preserves:
  - `snapshot_inventory_sha256`;
  - `snapshot_file_count`;
  - `snapshot_total_bytes`;
  - the Qwen-Image generator `model_revision`;
- seals those fields into the CS304 semantic-base receipt digest;
- on receipt verification, freshly replays CS359 again and requires every sealed snapshot-lineage field to exactly match fresh upstream evidence;
- fails closed if the lineage is missing, malformed, or drifts even when an attacker recomputes the outer CS304 receipt digest.

The Qwen2.5-VL semantic inspector revision remains independently pinned inside `semantic_inspector`; the top-level `model_revision` preserved by CS360 is the generator-model lineage inherited from CS359, not a replacement for verifier identity.

## Authority preservation

CS360 does not broaden CS304 authority. It may record `semantic_base_scene_approved` only according to the existing pinned semantic verdict stack. It still cannot grant identity approval, full semantic approval, Human Visual Review, Golden quality, branding/presentation approval, Final Semantic approval, SemanticPublicationGate authority, Genuine Golden materialization, publication readiness, or external publication.

The existing `$0-local`, `network_allowed=false`, and `local_files_only=true` upstream requirements remain mandatory. CS360 adds no model download, paid execution fallback, network model fallback, synthetic inference, retry shortcut, upload, or publication path.

## Regression requirements

Coverage must prove that:

1. valid CS359 snapshot lineage is preserved through a successful CS304 run and replay;
2. missing snapshot-inventory verification fails closed before semantic inspection can establish a usable receipt;
3. malformed generator revision fails closed;
4. snapshot inventory tampering is rejected even after recomputing the outer CS304 receipt digest;
5. existing generated-text rejection, candidate-byte tamper rejection, source-authority, local-only, verifier-identity, immutable-output, and no-authority-escalation behavior remains intact.

## Genuine Golden status

This change set performs no Qwen-Image generation and creates no production `canonical_candidate.png` or `genuine_golden_visual.png`. The first Genuine Golden remains gated by genuine compatible zero-cost CUDA/BF16 execution followed by the complete factual, identity, sentiment, semantic, visual, Human, Golden, presentation, final-semantic, and SemanticPublicationGate chain.
