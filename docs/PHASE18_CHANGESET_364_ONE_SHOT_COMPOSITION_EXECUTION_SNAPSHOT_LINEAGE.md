# Phase 18 Change Set 364 — One-Shot Composition Execution Snapshot Lineage

## Scope

CS364 closes the first verified downstream generator-lineage gap after CS363 inside the existing one-shot composition execution boundary (`qwen_image_canonical_candidate_one_shot_composition_execution.py`). It does not create a parallel gate and does not change the authority model.

## Proven gap

CS271 already performed a fresh `verify_composition_execution_preflight(...)` replay before rendering and again while verifying the execution receipt. It byte-bound the source preflight, candidate PNG, renderer source, renderer entrypoint, attempt-consumption record, and composed PNG. However, the exact Qwen-Image generator snapshot lineage established upstream was not sealed into either the pre-render attempt-consumption record or the final execution receipt.

That meant the execution boundary could prove which candidate and renderer bytes were used while failing to carry forward which exact approved generator snapshot bytes produced the candidate.

## Change

The existing CS271 schema is advanced to v2 and now requires, seals, and freshly re-verifies these upstream generator-lineage fields:

- `snapshot_byte_inventory_verified = true`
- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

The five fields are copied from the freshly verified CS363/CS270 preflight into both:

1. `composition_attempt_consumption.json`, written and fsynced before the renderer is invoked; and
2. `one_shot_composition_execution.json`, written only after a composed PNG is successfully produced and byte-bound.

Verification replays `verify_composition_execution_preflight(...)`, reconstructs the trusted lineage from that fresh replay, and compares it field-for-field against the sealed execution receipt. It also verifies that the durable pre-render consumption record carries the identical lineage.

A recomputed outer `receipt_sha256` therefore cannot hide snapshot inventory or generator revision tampering.

## Fail-closed behavior

CS364 rejects:

- unverified snapshot-byte inventory;
- malformed snapshot inventory SHA-256;
- non-positive snapshot file count or total bytes;
- missing/blank generator model revision;
- execution-receipt lineage drift after a fresh CS363 replay;
- consumption-record lineage drift;
- all existing candidate, renderer-source, runner-entrypoint, output-byte, dimension, preflight-receipt, and consumption-record drift conditions.

## Authority remains closed

CS364 records execution only. It deliberately keeps these fields false:

- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `golden_quality_approved`
- `publication_ready`

It grants no factual, identity, sentiment, semantic, human-review, Golden, brand/typography, final-semantic, SemanticPublicationGate, or external-publication authority.

## Zero-cost and execution policy

No dependency, model download, network-model fallback, paid fallback, synthetic inference, retry shortcut, or publication shortcut is introduced.

The first genuine Golden Visual PNG still requires a compatible zero-cost execution host with an NVIDIA CUDA GPU, CUDA-enabled PyTorch, native BF16 support, sufficient RAM/VRAM demonstrated under real Qwen-Image load/inference, the approved Qwen-Image/Diffusers runtime, and the exact approved already-local pinned generator/verifier assets.
