# Phase 18 Change Set 215 — Dynamic Queue-to-Critic Binding

## Goal

Close the remaining durable execution gap between a SHA-sealed Dynamic Visual Brain queue job and the PNG later evaluated by the byte-bound Visual Critic chain.

Before this change, Phase 18 could prove all of the following independently:

- the selected story-specific concept was locked before rendering;
- the renderer prompt was identity-neutral and SHA-bound;
- the measured `$0-local` request was sealed into the durable queue;
- the generated PNG carried Dynamic Visual Brain identity;
- Visual Critic evidence was bound to the PNG bytes and the selected concept.

The missing proof was that the **succeeded durable queue job** was the exact execution that produced the PNG entering the critic chain.

## Added

### `engine/intelligence/dynamic_visual_brain_queue_critic_binding.py`

New contract: `pul7sar-dynamic-visual-brain-queue-critic-binding-v1`.

The new fail-closed gate verifies:

1. the queue-binding receipt uses the current Dynamic Visual Brain durable-queue contract and Phase 18 branch;
2. the sealed handoff file still has the exact SHA recorded before enqueue;
3. the handoff payload SHA still matches the queue-binding receipt;
4. the durable queue contains the same job ID and the job is actually `succeeded`;
5. request ID, provider, model, payload SHA, handoff path and protected metadata still match the admitted concept;
6. the durable succeeded-job JSON is itself SHA-bound into the final receipt;
7. the worker generation result is `REAL_VISUAL_PROOF_GENERATED` and matches request/seed/provider/model/payload/concept/renderer hashes and `$0-local` policy;
8. the job result path, generation-result PNG path and actual repository PNG resolve to the same file;
9. the existing renderer-safe Dynamic Visual Brain Critic Binding is replayed;
10. critic story/concept/request/seed/payload/renderer/PNG identity matches the durable queue execution exactly.

The resulting receipt preserves:

- `human_visual_review_required=true`;
- `golden_quality_approved=false`;
- `publication_ready=false`.

### `tools/phase18_verify_dynamic_visual_brain_queue_critic_binding.py`

CPU-only replay command for the full durable queue -> generation -> critic chain. It does not run FLUX or Qwen, does not mutate the queue, and cannot grant publication authority.

### `tests/test_phase18_dynamic_visual_brain_queue_critic_binding.py`

Regression coverage includes:

- successful binding of a succeeded durable job to the same critic-reviewed PNG;
- durable queue concept-metadata drift;
- generation-result renderer-prompt drift;
- critic concept/PNG identity drift;
- rejection of non-succeeded durable jobs.

## Files changed

### Added

- `engine/intelligence/dynamic_visual_brain_queue_critic_binding.py`
- `tools/phase18_verify_dynamic_visual_brain_queue_critic_binding.py`
- `tests/test_phase18_dynamic_visual_brain_queue_critic_binding.py`
- `docs/PHASE18_CHANGESET_215_DYNAMIC_QUEUE_TO_CRITIC_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_215.md`

### Modified

- None in existing generation/runtime code. Change Set 215 is additive over the current durable queue and Visual Critic contracts.

### Deleted

- None.

## Gate preservation

Unchanged and still fail-closed:

- factual integrity / Fact Lock;
- Entity and Identity Verification;
- sentiment, neutrality and loser-respect policy;
- `$0-local` execution only;
- pinned/qualified generation and semantic model policies;
- generated branding/text/exact facts/entity marks/exact sport geometry prohibitions;
- semantic and layer-ownership gates;
- Visual Critic hard failures;
- explicit Human Review;
- Golden minimum `8.5` and elite target `9.0+`;
- Exact Brand Integrity and Typography Integrity;
- SemanticPublicationGate and final publication readiness.

## Genuine Golden Visual status

This change does not fabricate or claim a new GPU PNG. Existing genuine rejected visual evidence remains evidence, not success. The target remains the first **accepted** Genuine Golden Visual PNG.

The current execution environment still lacks an approved compatible `$0-local` GPU host with the required CUDA/precision/VRAM/RAM/offload/model/runtime evidence. Change Set 215 reduces the remaining software gap by making the future durable worker execution cryptographically continuous all the way into the critic-reviewed PNG.
