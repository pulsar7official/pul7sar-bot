# Phase 18 Change Set 320 — Exact Composition Callable Provenance

## Purpose

Change Set 320 closes a provenance gap at the CS271 one-shot deterministic composition execution boundary.

Before this change, CS271 byte-bound the declared `runner_source_path`, but the Python `compose_fn` callable supplied by the caller was not proven to originate from that exact source file. A caller could therefore declare one repository-local runner source while executing a different callable and still produce a structurally valid CS271 receipt.

CS320 makes the executable callable itself part of the fail-closed provenance boundary.

## Scope

CS320 strengthens:

- `engine/intelligence/qwen_image_canonical_candidate_one_shot_composition_execution.py`
- the corresponding CS271 regression suite.

It does **not** implement a renderer, synthesize editorial payloads, render a production image, perform model inference, approve visual quality, or publish anything.

## Required execution invariants

Before the one-shot composition attempt is consumed, CS271 now requires all of the following:

1. `compose_fn` is a synchronous callable.
2. Python can resolve the callable's source file.
3. The callable source file is inside the repository.
4. The callable source file resolves to the exact same repository-relative file as the byte-bound `runner_source_path`.
5. The callable is a named, top-level Python function rather than a lambda, nested function, method, or opaque callable object.
6. The entrypoint name exists as a top-level function definition in the bound runner source.

The resolved `runner_entrypoint` is written into both the attempt-consumption evidence and the CS271 receipt.

Replay verification reopens the exact runner bytes, parses the source again, confirms the recorded entrypoint still exists in that bound source, and requires the consumption evidence and final CS271 receipt to agree on the runner source, runner ID, and entrypoint.

## Authority boundary

CS320 does not widen CS271 authority.

A successful execution may only establish:

- `composition_executed = true`

It must continue to leave all of the following false:

- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `genuine_golden_png_created`
- `publication_ready`

All factual, identity, sentiment/loser-respect, zero-cost, semantic-publication, and visual-quality gates remain downstream and unchanged.

## Security effect

The CS271 receipt no longer means merely:

> these runner-source bytes were named while some callable produced the image.

It now means:

> the callable that was permitted to cross the one-shot composition boundary was resolved from the exact repository-local runner source whose bytes are recorded in the receipt, and its named top-level entrypoint is replay-verifiable from those same bytes.

This materially reduces the gap to a genuine composed candidate without inventing a renderer or bypassing any approval gate.
