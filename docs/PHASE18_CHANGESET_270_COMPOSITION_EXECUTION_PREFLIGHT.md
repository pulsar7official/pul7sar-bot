# Phase 18 Change Set 270 — Composition Execution Preflight

## Purpose

CS269 proved that a canonical candidate had a complete composition request and that each deterministic layer declared a renderer contract plus a payload SHA-256. It did **not** bind that digest to a concrete payload file. That meant an actual renderer still lacked a repository-verifiable byte source for deterministic instructions.

CS270 closes that gap without rendering pixels.

## Contract

CS270 consumes a READY CS269 receipt and a deterministic-payload manifest. For every deterministic layer declared by CS269, CS270 requires:

- the exact layer name;
- the exact CS269 renderer contract;
- a repository-relative payload file binding;
- SHA-256 and byte-size verification of that file;
- equality between the payload file's actual SHA-256 and CS269 `payload_sha256`.

The payload manifest is additionally bound to the same story snapshot SHA-256 and exact candidate PNG SHA-256.

Unknown payload layers, renderer-contract drift, payload-byte drift, candidate-byte drift, CS269 receipt drift, symlinks, paths outside the repository, and output overwrite are fail-closed.

## Authority

A successful CS270 may set only:

`composition_execution_ready = true`

It MUST keep all of the following false:

- `composition_executed`
- `composed_visual_approved`
- `semantic_approved`
- `human_visual_review_approved`
- `genuine_golden_png_created`
- `golden_quality_approved`
- `publication_ready`

CS270 is therefore an executable-input preflight, not a renderer and not a quality or publication gate.

## Why this materially reduces the Golden gap

Before CS270, the remaining composition executor could not locate deterministic instructions from the CS269 receipt alone; it knew only their hashes. After CS270, every deterministic instruction stream is concrete, immutable, repository-bound, and reproducible. The next safe step can therefore invoke the existing renderer/compositor against exact candidate bytes, exact verified assets, and exact deterministic payload bytes, then byte-bind the composed PNG for post-composition QA.
