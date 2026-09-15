# Phase 18 Change Set 332 — Explicit Typography Overlay Materialization

## Scope

CS332 closes one narrow upstream execution gap before CS331/CS330 composition: converting already-authored, repository-bound deterministic typography tiles into the exact full-canvas RGBA overlay required by the production composer.

This change does **not** design typography, choose coordinates, select fonts, wrap text, resize tiles, generate brand pixels, generate identity pixels, run Qwen, execute composition, approve semantics, approve visual quality, or grant publication authority.

## New production contract

`engine/intelligence/qwen_image_explicit_overlay_materializer.py`

Manifest schema:

`pul7sar-phase18-explicit-overlay-materialization-manifest-v1`

Receipt schema:

`pul7sar-phase18-explicit-overlay-materialization-v1`

Materializer ID:

`pul7sar-phase18-explicit-rgba-tile-materializer-v1`

Downstream renderer contract:

`pul7sar-phase18-full-canvas-rgba-overlay-v1`

## Ownership boundary

CS332 intentionally accepts only:

- `layer_name = editorial_typography`
- `layer_source = deterministic`

It rejects `verified_asset`.  In particular, CS332 cannot derive or reposition the `pul7sar_brand` layer.  Brand pixels remain under the verified-asset ownership path established before this change.

## Explicit geometry requirement

Every tile must be an existing repository-bound native RGBA PNG and must provide explicit integer:

- `x`
- `y`
- `z_index`

The z-index values must be unique.  Tiles must fit fully within the canvas.  No resize, center, crop, transform, fallback, inferred positioning, or layout repair is permitted.

The manifest is also bound to:

- the exact story snapshot SHA-256;
- the exact canonical candidate PNG bytes;
- the exact candidate canvas dimensions;
- the exact renderer contract;
- every exact input tile byte binding.

## Output

On success CS332 creates:

- `editorial_typography_overlay.png` — native RGBA, exact candidate canvas size, partially transparent;
- `explicit_overlay_materialization.json` — replayable receipt binding the manifest, candidate, tile inputs, exact geometry, and output bytes.

The output PNG uses fixed PNG write options and no metadata-dependent design decisions.

## Authority boundary

Successful materialization grants only:

`overlay_materialized = true`

It explicitly retains:

- `composition_executed = false`
- `composed_visual_approved = false`
- `semantic_approved = false`
- `human_visual_review_approved = false`
- `golden_quality_approved = false`
- `genuine_golden_png_created = false`
- `publication_ready = false`

The output still must be admitted into the deterministic composition payload lineage and pass CS270, CS331, CS271/CS330, all composed-image semantic/visual/human gates, SemanticPublicationGate, and CS285 before a Genuine Golden PNG can exist.

## Security and quality properties

The implementation is fail-closed for:

- repository path escape or symlinks;
- byte drift in candidate, manifest, or tiles;
- non-PNG or non-RGBA source tiles;
- fully transparent source tiles;
- canvas mismatch;
- negative/out-of-bounds placement;
- duplicate z-order;
- source/ownership drift;
- renderer-contract drift;
- receipt digest drift;
- downstream authority appearing prematurely.

It performs no network access and contains no model inference path.

## Why this reduces the Golden gap

Before CS332, CS330/CS331 required a full-canvas deterministic `editorial_typography` overlay but the repository had no narrow production primitive that could materialize that canvas without making new layout decisions.

CS332 makes the final placement transformation executable while keeping design authority upstream: once an authoritative typography renderer/layout process has produced exact RGBA tiles and exact coordinates, the Phase 18 pipeline can deterministically materialize the full-canvas overlay expected by CS331/CS330 without guessing anything.

The remaining typography-side gap is therefore reduced from "full-canvas overlay materialization" to "produce/approve the exact typography tiles and explicit geometry manifest."  The verified PUL7SAR brand overlay remains a separate ownership-preserving gap.
