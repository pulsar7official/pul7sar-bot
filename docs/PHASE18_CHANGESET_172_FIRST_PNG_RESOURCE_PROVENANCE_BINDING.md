# Phase 18 Change Set 172 — First-PNG Resource Provenance Binding

## Scope

Branch: `phase18/story-intelligence` only. `main` is not modified, merged, force-updated, or used as a write target.

## Why this change exists

Change Set 171 made the post-lease/pre-FLUX GPU and host-RAM decision durable by writing a tamper-evident execution-resource receipt for the concrete leased attempt. A remaining provenance gap still existed: first-PNG postflight verified the PNG, executor result, proof metadata, model/seed/request identity, BF16, and `$0-local`, but it did not require the exact lease-bound resource receipt that allowed that successful attempt to enter FLUX.

That gap is now closed. A Golden Candidate 1 PNG cannot pass first-PNG provenance replay unless the execution-resource receipt for the same `job_id` and same successful `attempt` also replays successfully.

## Added / modified

### `engine/intelligence/execution_resource_evidence.py`

Extended the existing evidence store with fail-closed replay verification. The verifier now:

- requires a succeeded job with a positive attempt;
- requires the exact schema `pul7sar-lease-bound-execution-resource-v1`;
- binds `job_id`, `request_id`, `attempt`, `payload_sha256`, `provider_id`, and `model_id` to the succeeded job;
- validates a safe worker identity and timezone-aware observation time;
- rechecks native BF16 and `$0-local` claims;
- rechecks recorded live-free VRAM against the recorded required VRAM floor;
- rechecks recorded live available system RAM against the recorded required RAM floor;
- rejects queue/generation/semantic/Golden/publication authority drift;
- constrains the evidence path to the repository when a repository root is supplied;
- returns SHA-256 and byte size for downstream provenance binding.

### `engine/intelligence/first_png_provenance_postflight.py`

First-PNG provenance now requires `execution_resource_receipt` in addition to executor result and proof metadata. It fails closed on missing, escaped, malformed, identity-drifted, attempt-drifted, or resource-invalid evidence.

Successful postflight now records:

- execution-resource receipt path;
- execution-resource SHA-256 and byte size;
- worker ID and attempt;
- observation time;
- exact GPU evidence;
- exact host-memory evidence.

This stage still grants no semantic, Golden-quality, brand, typography, export, or publication authority.

### `tools/phase18_verify_first_png_provenance.py`

Added `--execution-resource-receipt`. When omitted, the command resolves the canonical attempt-bound path:

`output/phase18_worker_results/<job-id>-attempt-<attempt>-execution-resource.json`

The command remains CPU-only and does not mutate the queue or create pixels.

### Regression alignment

`tests/test_phase18_gpu_worker_live_requalification.py` was aligned with the stronger Change Set 171 design. The leased execution path now intentionally calls `_record_lease_bound_execution_evidence(...)`, whose helper performs `_requalify_execution_host(...)` and persists the receipt before FLUX. The test now verifies that actual stronger chain rather than expecting the older direct helper call inside the service constructor.

### Tests expanded

- `tests/test_phase18_execution_resource_evidence.py`
  - replay of a genuine written receipt against the succeeded attempt;
  - attempt drift rejection;
  - live-free VRAM floor rejection;
  - repository path escape rejection.
- `tests/test_phase18_first_png_provenance_postflight.py`
  - successful first-PNG replay requires execution resources;
  - execution-resource SHA/worker/attempt are returned;
  - RAM tampering is rejected;
  - attempt drift is rejected;
  - resource-evidence path escape is rejected.

## Preserved gates

No change was made to:

- Fact Lock / source consensus;
- Entity and Identity Verification;
- Sentiment / Neutrality / loser-respect rules;
- `$0-local` policy;
- pinned FLUX.2 Klein 4B and Qwen revisions;
- native BF16 policy;
- total/live-free VRAM or host-RAM gates;
- safe Diffusers offload policy;
- request/seed/canvas/SHA locks;
- generated text/branding/exact-fact/entity-mark/sport-geometry prohibitions;
- Qwen `BASE_SCENE` / `HYBRID_SURFACE` gates;
- deterministic football geometry;
- Golden minimum `8.5` / elite `9.0+` thresholds;
- Exact Brand / Typography integrity;
- SemanticPublicationGate.

## Deleted

Nothing.

## Genuine Golden PNG status

No genuine Golden Hybrid v5 Candidate 1 PNG was fabricated or claimed in this change set. The exact external blocker remains availability of a real host that simultaneously proves NVIDIA CUDA, native BF16, sufficient total/live-free VRAM, safe local Diffusers offload/runtime, sufficient live system RAM through lease/execution, pinned FLUX/Qwen revisions, stable runtime fingerprint, and `$0-local` execution.

When such a host becomes available, the successful PNG will now be provenance-bound end-to-end to the final resource state immediately before FLUX execution, not only to prompt/model/seed/executor metadata.
