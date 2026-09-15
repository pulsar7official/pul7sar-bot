# Phase 18 Change Set 356 — Canonical Child Inventory-Bound Execution Edge

## Objective

Close the direct-child bypass around CS354 snapshot byte binding without weakening any existing factual, identity, sentiment, zero-cost, semantic-publication, visual-quality, Golden, human-review, or publication gate.

## Problem

CS354 bound the launch manifest to a deterministic inventory of the exact already-local Qwen Image snapshot. CS355 then required that inventory inside the mandatory preload host diagnostic before the manifest-bound launcher could start the canonical child.

However, the canonical child entry point `tools/phase18_run_one_shot_canonical_inference.py` still imported the historical CS292 `verify_gpu_host_launch_manifest_for_execution` verifier directly. That verifier proves authorization, CS257 evidence, snapshot path/revision, and inference-setting equality, but does not independently require the CS354 byte inventory.

The normal launcher path remained protected, but a direct invocation of the child could therefore attempt to satisfy only the historical manifest contract. The production inference edge should not depend on callers always passing through the outer launcher.

## Implementation

`engine/intelligence/qwen_image_inventory_bound_launch_manifest.py` now exposes:

`verify_inventory_bound_gpu_host_launch_manifest_for_execution(...)`

The verifier composes two existing authorities in fail-closed order:

1. replay CS354 exact snapshot byte inventory;
2. replay CS292 concrete invocation binding;
3. require both replays to resolve to the same manifest digest and inventory.

The canonical child now imports only this inventory-bound execution verifier for its pre-prompt/pre-model execution gate.

## Resulting execution chain

```text
inventory-bound launch manifest
→ CS355 preload inventory + host gate
→ canonical child starts
→ CS356 exact snapshot-byte replay
→ CS292 exact invocation replay
→ story-bound prompt extraction
→ authorization / CS260 replay
→ CS352 pre-load inventory
→ from_pretrained(local_files_only=True, BF16)
→ CS353 post-load inventory
→ one genuine canonical inference
→ exact PNG/provenance/attestation
→ downstream factual/identity/sentiment/semantic/visual/Golden gates
```

## Authority boundaries

CS356 does not load a model by itself, execute inference, create pixels, approve facts, approve identity, approve sentiment, approve semantics, approve visual quality, approve Golden quality, approve human review, execute SemanticPublicationGate, materialize a Genuine Golden PNG, mark publication readiness, or publish/upload anything.

No network fallback, model download, paid fallback, retry loop, synthetic success, or authority shortcut was added.

## Tests

`tests/test_phase18_qwen_image_inventory_bound_execution_edge.py` covers:

- snapshot byte replay occurs before concrete invocation replay;
- snapshot byte drift stops before the historical execution verifier runs;
- disagreement between the two verifier replays fails closed;
- the canonical child imports the inventory-bound verifier rather than directly importing the historical execution verifier;
- the child retains local-only/no-network declarations.
