# Phase 18 — Change Set 354

## Inventory-Bound GPU Host Launch Manifest

CS354 closes the remaining gap between pre-inference authorization and the exact already-local Qwen snapshot bytes that a future zero-cost CUDA host will load.

Before CS354, the CS291/292 launch manifest bound the model id, approved revision, resolved snapshot path, story authorization, CS257 evidence, prompt contract, and inference settings. CS352/353 later protected snapshot bytes immediately around `from_pretrained`. The missing link was that the launch manifest itself did not preserve the CS352 deterministic snapshot inventory.

CS354 adds a compositional inventory-bound wrapper. It does not replace or weaken CS291/292. It first builds the existing manifest, computes the deterministic CS352 inventory for the exact resolved snapshot, seals that inventory into the final manifest digest, independently replays the original manifest verifier, and requires the live snapshot inventory to remain byte-identical.

The production manifest CLI now builds and verifies the inventory-bound form. The manifest-bound launcher also requires the inventory-bound verifier before it can derive or start the canonical subprocess. CS352/353 remain in place around the actual model load, so the chain now protects snapshot bytes across both intervals:

`manifest construction -> manifest replay / subprocess launch -> pre-load inventory -> from_pretrained -> post-load inventory`.

## Authority boundaries

CS354 performs no download, no network fallback, no model load, no inference, and no pixel creation. It grants no factual, freshness, identity, sentiment, semantic, visual-quality, Golden-quality, human-review, brand, typography, final-semantic, SemanticPublicationGate, Genuine Golden, publication-readiness, or external-publication authority.

The zero-cost and local-only constraints remain unchanged. The existing downstream factual, identity, sentiment/loser-respect, semantic-publication, and visual-quality gates remain mandatory.

## Files

Added:
- `engine/intelligence/qwen_image_inventory_bound_launch_manifest.py`
- `tests/test_phase18_qwen_image_inventory_bound_launch_manifest.py`
- `docs/PHASE18_CHANGESET_354_INVENTORY_BOUND_GPU_HOST_LAUNCH_MANIFEST.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_354.md`

Modified:
- `tools/phase18_qwen_image_gpu_host_launch_manifest.py`
- `engine/intelligence/qwen_image_manifest_bound_execution.py`

Deleted: none.

## Runtime limitation

CS354 is deliberately CPU-testable because it only hashes already-local snapshot bytes and replays manifests. Genuine Qwen inference still requires a compatible zero-cost CUDA host with CUDA-enabled PyTorch, native BF16, sufficient real RAM/VRAM, the approved Diffusers/Qwen runtime, and the exact approved already-local pinned model/verifier assets.
