# PUL7SAR Phase 18 — Change Set 130

## First-PNG Provenance Postflight Integration

This change keeps all work on `phase18/story-intelligence` and does not modify `main`.

## Problem closed

The self-hosted GPU smoke workflow already required the First-PNG provenance postflight before evidence sealing, but the direct one-command entrypoint `tools/phase18_first_png.py` could still report either a newly generated Candidate 1 PNG or a previously succeeded durable job without replaying that same provenance postflight first.

That created a path-dependent trust gap: the workflow path was stricter than the direct first-PNG command.

## Changes

### `tools/phase18_first_png.py`

- added an explicit First-PNG provenance postflight stage;
- requires `FIRST_GOLDEN_PNG_PROVENANCE_POSTFLIGHT_VERIFIED`;
- requires Candidate 1 and the exact durable job ID;
- requires `$0-local` and `bfloat16` to replay successfully;
- requires `semantic_approved=false`, `golden_quality_approved=false`, and `publication_ready=false`;
- verifies the postflight PNG path matches the PNG that the one-command flow is about to report;
- applies the same replay to both newly generated output and an already-succeeded reusable Candidate 1 job;
- records the postflight receipt path in one-command evidence and emits the postflight payload in the final JSON result.

### `tests/test_phase18_first_png_preflight.py`

Added regression coverage proving:

- the generation path runs provenance postflight before reporting `FIRST_REAL_GOLDEN_PNG_GENERATED`;
- the reuse path runs provenance postflight before reporting `FIRST_REAL_GOLDEN_PNG_ALREADY_EXISTS`;
- postflight requires `$0-local`, BF16, Candidate 1 and the locked job identity;
- semantic, Golden-quality and publication authority remain false;
- the PNG returned by postflight must be the same PNG the command reports.

## Security / quality invariants preserved

No change was made to Fact Lock, identity verification, sentiment/neutrality, FLUX.2 Klein 4B, native BF16, Qwen semantic inspection, deterministic football geometry, SemanticPublicationGate, Golden visual thresholds, exact brand/typography integrity, seed/canvas locks, or the `$0-local` policy.

No fake PNG, paid provider, hosted-GPU fallback, precision downgrade or publication shortcut was introduced.

## Why this reduces the gap to the first genuine Golden Visual

There is now one provenance standard for both supported GPU entry paths. A Candidate 1 durable job reaching `succeeded` is never sufficient by itself. Before the direct one-command path can report success or reuse, the current PNG bytes, executor result, proof metadata, request identity, payload SHA, cost mode and precision must replay successfully.

The remaining generation blocker is still external: a compatible NVIDIA CUDA/BF16 host is required to execute FLUX.2 Klein 4B and produce the genuine Candidate 1 PNG under the current architecture.
