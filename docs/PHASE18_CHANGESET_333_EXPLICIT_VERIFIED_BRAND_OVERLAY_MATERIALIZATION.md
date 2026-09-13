# Phase 18 Change Set 333 — Explicit Verified Brand Overlay Materialization

## Purpose

Close the remaining production-layer assembly gap for `pul7sar_brand` without drawing, redesigning, resizing, recoloring, tinting, or auto-placing the PUL7SAR mark.

CS333 accepts an already-rendered native-RGBA PNG brand tile whose exact bytes are declared in an operator manifest, plus explicit `x/y` coordinates. It materializes those exact pixels onto a transparent candidate-sized RGBA canvas.

## Safety boundary

This change is deliberately **not** a brand-approval authority. The existing embedded/reference brand master remains study/reference material, and publication still requires the downstream exact-brand/human review gates.

The manifest must keep `owner_brand_approval_required=true`. A successful CS333 receipt therefore records:

- `overlay_materialized=true`
- `brand_publication_approved=false`
- `owner_brand_approval_required=true`
- `composition_executed=false`
- `semantic_approved=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`
- `authoritative=false`

## Exact-input requirements

The materializer requires:

- contract `pul7sar-phase18-explicit-verified-brand-overlay-materialization-v1`;
- `layer_name=pul7sar_brand`;
- `layer_source=verified_asset`;
- exact Story SHA-256;
- candidate repository path, SHA-256, byte size, width, and height;
- exact brand-tile repository path, SHA-256, and byte size;
- native RGBA PNG brand tile with non-empty alpha;
- explicit non-negative `x/y` placement fully inside the candidate canvas.

It rejects repository escape/symlink inputs and byte/dimension drift.

## What it does not do

CS333 performs no Qwen generation, network access, image resize, typography selection, logo geometry synthesis, auto-placement, color adaptation, composition approval, semantic approval, Golden approval, or publication readiness decision.

## Relationship to the Golden path

CS332 can materialize explicit deterministic typography. CS333 can now materialize an explicit verified-brand tile into the same full-canvas overlay contract consumed by CS330/CS331. Both remain inputs to the existing ownership, byte-preflight, composition, semantic, visual, human, brand/typography, SemanticPublicationGate, CS285, and CS286 authorities.

A genuine Golden PNG is still impossible in the current execution environment because the host is CPU-only and has no compatible CUDA/BF16 Qwen-Image execution path.
