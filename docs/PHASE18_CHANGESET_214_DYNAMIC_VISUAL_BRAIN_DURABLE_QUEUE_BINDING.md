# Phase 18 Change Set 214 — Dynamic Visual Brain Durable Queue Binding

## Purpose

Close the execution boundary between a measured, renderer-safe Dynamic Visual Brain local admission and the durable GPU worker queue.

Before this change, Phase 18 could prove which story-specific concept was selected, translate it into an identity-neutral renderer prompt, qualify a `$0-local` runtime, and compile the exact `LocalBackendGenerationRequest`. The generic queue could persist a `LocalGenerationHandoff`, but there was no Dynamic Visual Brain-specific fail-closed bridge proving that the queued job preserved the same story fingerprint, concept hashes, renderer-prompt hash, Original Scene hash, request identity, and protected-layer ownership.

## Added

- `engine/intelligence/dynamic_visual_brain_queue_binding.py`
  - validates the renderer-safe local admission contract;
  - revalidates `$0-local`, semantic inspection, human review, and generator authority boundaries;
  - SHA-seals the exact admitted request into a `LocalGenerationHandoff`;
  - replays the handoff before queue persistence;
  - creates a deterministic durable `GenerationJob` identity from the handoff payload SHA;
  - stores Dynamic Visual Brain story/concept/renderer hashes in immutable queue metadata;
  - supports idempotent reuse only when the existing durable job is byte/metadata compatible;
  - rejects branch drift, request identity drift, concept/prompt hash drift, unsafe authority drift, and repository path escape.

- `tools/phase18_enqueue_dynamic_visual_brain.py`
  - CPU-only CLI for binding an existing SHA-protected local request plus its measured Dynamic Visual Brain admission receipt into the durable Phase 18 queue;
  - does not run FLUX or Qwen;
  - does not grant Golden or publication authority.

- `tests/test_phase18_dynamic_visual_brain_queue_binding.py`
  - exact successful queue binding;
  - deterministic/idempotent retry;
  - concept SHA drift rejection;
  - renderer-prompt SHA drift rejection;
  - paid-cost/publication-authority rejection;
  - repository path-escape rejection;
  - existing queue-job tamper rejection.

## Preserved gates

No factual, entity/identity, sentiment/neutrality, zero-cost, semantic, Visual Critic, Golden-quality, brand, typography, or publication gate is weakened.

The queued job explicitly preserves:

- `cost_mode = $0-local`;
- `generated_branding_allowed = false`;
- `generated_exact_facts_allowed = false`;
- `generated_sport_geometry_allowed = false`;
- `semantic_inspection_required = true`;
- `human_visual_review_required = true`;
- `golden_quality_approved = false`;
- `publication_ready = false`.

## Why this reduces the remaining Golden gap

The next compatible GPU host no longer needs an informal handoff between Dynamic Visual Brain admission and the worker queue. The exact story-specific concept and identity-neutral renderer request that were admitted are now the same SHA-protected request the worker may lease.

The remaining blocker is still genuine compatible `$0-local` GPU execution. This Change Set does not fabricate a PNG or claim Golden quality.
