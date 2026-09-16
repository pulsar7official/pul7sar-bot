# Phase 18 Change Set 355 — Preload Inventory-Bound Host Gate

## Objective

Close the remaining gap between the CS354 inventory-bound launch manifest and the mandatory preload host diagnostic. The preload diagnostic must replay the same inventory-bound manifest before checking static GPU readiness or the live CS260 host identity.

## Change

`engine/intelligence/qwen_image_preload_host_diagnostic.py` now imports the CS354 inventory-bound verifier instead of the historical path/revision-only launch verifier. If the exact already-local Qwen snapshot bytes drift, preload fails before GPU readiness probing, runtime identity probing, model load, subprocess launch, inference, or pixel creation.

The diagnostic also records `snapshot_inventory_bound=true` only after successful inventory-bound manifest replay.

## Security / authority properties

CS355 does not:

- download model assets;
- permit network or paid fallback;
- load Qwen;
- execute inference;
- create or alter any candidate PNG;
- grant factual/freshness, identity, sentiment/loser-respect, semantic, visual-quality, Golden-quality, human-review, brand, typography, Final Composed, Final Semantic, SemanticPublicationGate, Genuine Golden, publication-readiness, upload, or external-publication authority.

## Production ordering after CS355

`inventory-bound manifest -> inventory-bound preload diagnostic -> static GPU readiness + live CS260 identity -> canonical child -> CS352 pre-load inventory -> from_pretrained(local_files_only=True, BF16) -> CS353 post-load inventory -> genuine inference`.

## Tests

Regression coverage proves that the preload diagnostic invokes the inventory-bound verifier, preserves all non-authority fields, and stops before readiness probing when snapshot-byte drift is reported.
