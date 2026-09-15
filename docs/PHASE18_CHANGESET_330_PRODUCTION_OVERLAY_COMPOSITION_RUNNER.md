# Phase 18 Change Set 330 — Production Overlay Composition Runner

## Purpose

CS330 closes the concrete runner gap between the existing CS270 deterministic-composition preflight and the CS271 one-shot composition boundary without weakening any downstream authority.

The repository already had strong CS269/CS270/CS271 contracts and multiple Pillow-based compositors, but CS321 still required an operator-supplied repository-local runner. The existing `FinalHybridComposer` cannot be passed directly to CS271: it is a class API rather than the required top-level `(preflight, output_path, repo_root)` callable, and its dynamic brand drawing does not match the CS268 ownership rule that `pul7sar_brand` is a verified-asset layer.

CS330 therefore adds a deliberately narrow production runner:

`engine/intelligence/qwen_image_production_overlay_composition_runner.py`

Entrypoint:

`compose_visual(preflight, output_path, repo_root)`

Runner ID:

`pul7sar-phase18-production-overlay-composer-v1`

## Supported production contract

Deterministic layers are accepted only with:

`pul7sar-phase18-full-canvas-rgba-overlay-v1`

The associated CS270 payload file must be an exact repository-byte-bound PNG whose dimensions already equal the canonical candidate canvas.

Verified-asset layers are read from the exact CS269 receipt chained through CS270. They must likewise already be full-canvas transparent PNG overlays. The runner never resizes, guesses placement, synthesizes text, reconstructs a logo, invents a score, or changes identity pixels.

The generative `atmosphere_base` is the canonical candidate itself. Other layers are alpha-composited in the exact `composition_layers` order supplied by the verified CS269 receipt.

## Fail-closed behavior

The runner rejects:

- a non-ready CS270 preflight;
- candidate/source files outside the repository;
- symlinked or byte-drifted bindings;
- CS269 story or candidate lineage drift;
- a CS269 receipt that is not composition-request-ready;
- unsupported deterministic renderer contracts;
- missing deterministic payloads;
- non-PNG overlays;
- any overlay whose dimensions differ from the candidate canvas;
- unexpected generative layers or layer source types;
- missing `atmosphere_base`.

## Authority boundary

CS330 is a pixel composer only. It does not perform or grant:

- Qwen generation;
- factual approval;
- identity approval;
- sentiment approval;
- semantic approval;
- Golden-quality approval;
- human visual review;
- Genuine Golden materialization;
- publication readiness or publication side effects.

Those authorities remain exclusively in the existing Phase 18 gates.

## Why full-canvas overlays first

This is intentionally conservative. It establishes a genuine project-native production path that can compose the first low-risk Golden candidate without introducing a new placement language at the same time. A later contract can support structured placement only after its geometry, font, brand, asset, and byte-lineage semantics are independently specified and tested.

For the first genuine Golden attempt, stories that do not require a human identity layer are the safest initial target. Identity-bearing visuals remain supported only when the verified asset has already been materialized as an exact full-canvas overlay by an independently approved process.

## Zero-cost and network policy

The runner uses Pillow only. It performs no model inference and no network access. CS321 already forces Hugging Face/Transformers offline during runner import. No paid or remote fallback is introduced.

## Remaining external blocker

CS330 does not solve the genuine Qwen inference host requirement. A genuine canonical candidate still requires the approved zero-cost CUDA/BF16 execution environment and exact already-local pinned model/verifier assets. No synthetic Golden PNG is created by this change set.
