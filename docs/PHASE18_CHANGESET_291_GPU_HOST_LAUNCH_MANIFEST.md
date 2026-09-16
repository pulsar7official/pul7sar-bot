# Phase 18 Change Set 291 — GPU Host Launch Manifest

## Purpose

CS291 closes a pre-execution handoff gap between the already-locked local-only canonical inference edge (CS289/CS290) and the future zero-cost CUDA host that must execute the first genuine Qwen-Image candidate.

It does **not** load Qwen, execute inference, create pixels, approve semantics, create a Golden artifact, or grant publication readiness.

## Contract

A launch manifest can be built only from an existing story-bound generation authorization and its CS257 evidence set. Construction replays the canonical prompt contract, verifies the exact approved `Qwen/Qwen-Image-2512` snapshot revision, and reuses the CS262 measured inference envelope.

The manifest byte-binds:

- the exact generation authorization file;
- every regular file in the referenced CS257 evidence directory;
- the story-bound prompt contract;
- immutable model ID/revision and resolved local snapshot path;
- width, height, seed, step count, and guidance scale;
- the execution-contract source bytes for approved revisions, GPU readiness, local runtime loading, one-shot inference, local inference provenance, and the production inference CLI.

The manifest fixes `cost_mode=$0-local`, `network_allowed=false`, `local_files_only=true`, native BF16 required, and sequential CPU offload required.

## Fail-closed behavior

Verification reopens every repository byte binding, re-verifies the generation authorization, rebuilds the story-bound prompt contract, rechecks the snapshot revision, revalidates the measured inference envelope, and rejects any changed execution-contract source.

All downstream authority remains false, including genuine inference, semantic approval, Golden-quality approval, Genuine Golden creation, and publication readiness.

## Why this materially reduces the remaining gap

When a compatible free NVIDIA host becomes available, the exact inputs for the one permitted attempt can be validated before model load or authorization consumption. Host transfer/configuration drift therefore fails before expensive GPU work begins instead of being discovered after the execution edge has already started.
