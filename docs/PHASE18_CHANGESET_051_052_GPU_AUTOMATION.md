# PUL7SAR Phase 18 — Change Sets 051–052

## Purpose
Move the Golden Visual path from a manually invoked GPU proof toward a continuously runnable, fail-closed generation worker without touching production `main`.

## Change Set 051 — Provider-neutral generation job/worker contracts

Added:
- `engine/intelligence/generation_jobs.py`
- `engine/intelligence/generation_worker.py`
- `tests/test_phase18_generation_worker.py`

The new contracts define an explicit lifecycle:

`queued -> leased -> running -> succeeded | retryable_failed -> queued | terminal_failed`

Safety properties:
- one immutable request/provider/model/payload-SHA identity per job;
- bounded retry count;
- lease ownership and expiry validation;
- CUDA/BF16/provider/model capability matching;
- executor-result identity cross-check before success;
- terminal failure for identity drift or capability mismatch;
- retry only for explicitly retryable execution failures;
- no silent provider, model, prompt, precision, or cost-mode downgrade.

## Change Set 052 — Durable queue and real FLUX worker execution boundary

Added:
- `engine/intelligence/generation_job_store.py`
- `engine/intelligence/flux_worker_executor.py`
- `tools/phase18_enqueue_generation.py`
- `tools/phase18_gpu_worker.py`
- `tests/test_phase18_generation_job_store.py`
- `tests/test_phase18_flux_worker_executor.py`

Modified:
- `engine/intelligence/__init__.py` to export the worker infrastructure.
- `docs/PHASE18_IMPLEMENTATION_LOG.md` to record Change Sets 051–052.

### Durable filesystem queue
`FilesystemGenerationJobStore` is the first concrete `GenerationJobStore` adapter. It is deliberately dependency-free and intended for one machine or multiple worker processes sharing one filesystem. It is not treated as a substitute for a distributed queue.

Key properties:
- state encoded by dedicated directories;
- exclusive enqueue prevents duplicate job IDs;
- atomic `os.replace` claim moves a queued job into leased state;
- a second worker cannot claim the same queued file after the first atomic move;
- state saves move the job between state directories without intentionally keeping duplicate state copies;
- timezone-aware timestamps survive JSON persistence;
- unsafe filesystem job IDs are rejected.

### Locked FLUX subprocess executor
`Flux2SubprocessLockedExecutor` connects the generic worker to the existing real `tools/phase18_flux2_execute.py` path.

It does not pass prompt, model, seed, or canvas values on the command line. Those remain inside the already SHA-256-protected handoff.

Before execution it verifies:
- handoff file exists;
- job SHA equals handoff `payload_sha256`;
- handoff cryptographic integrity still passes;
- request ID matches;
- provider/model match the locked job.

After execution it requires:
- dedicated result JSON;
- status `REAL_VISUAL_PROOF_GENERATED`;
- resolved dtype exactly `bfloat16`;
- a real existing PNG path;
- provider/model/request identity returned by the executor.

CUDA OOM, timeouts and selected transient runtime errors can be retried within the job's bounded retry policy. Integrity, dtype, or proof-shape failures are not silently retried into a weaker configuration.

### Enqueue command
`tools/phase18_enqueue_generation.py` converts an existing versioned handoff into an immutable durable job. It copies only locked identity fields and safe metadata into the queue record.

Example:

```bash
PYTHONPATH=. python tools/phase18_enqueue_generation.py \
  --handoff output/phase18_handoffs/golden-batch/candidate-01.json \
  --queue-root output/phase18_generation_queue \
  --job-id golden-candidate-01
```

### Continuous GPU worker
`tools/phase18_gpu_worker.py` is the first continuous worker entry point. At startup it proves:
- approved FLUX.2 Klein provider/model;
- CUDA runtime readiness;
- FLUX-specific Diffusers pipeline availability;
- native BF16 support/resolution;
- `$0-local` execution boundary.

Only then does it consume jobs. It supports one-cycle execution for smoke testing and continuous polling for unattended operation.

Example smoke cycle:

```bash
PYTHONPATH=. python tools/phase18_gpu_worker.py \
  --worker-id gpu-worker-01 \
  --queue-root output/phase18_generation_queue \
  --once
```

Example continuous worker:

```bash
PYTHONPATH=. python tools/phase18_gpu_worker.py \
  --worker-id gpu-worker-01 \
  --queue-root output/phase18_generation_queue
```

## What this closes
The first real Golden PNG no longer requires the image-generation logic to be manually orchestrated command-by-command. Once a compatible GPU host has the repository, model dependencies and handoff files, the path can be:

`locked handoff -> enqueue -> durable lease -> GPU worker -> existing real FLUX executor -> exact canvas normalization -> visual proof PNG`

This is a real automation boundary, not a fake image-generation substitute.

## What remains blocked
No compatible CUDA/BF16 GPU is available inside the current GitHub CPU execution environment, so no genuine FLUX PNG is claimed by this change set.

Remaining production-scale infrastructure after the first real GPU proof:
1. execute candidate 1 on a compatible GPU and capture real timing/VRAM metrics;
2. run the full four-seed Golden batch and apply semantic + 8.5/9.0 visual gates;
3. replace or complement the filesystem store with a true distributed queue for multi-host scaling;
4. add worker heartbeat/lease recovery and observability before 24/7 production;
5. benchmark images/minute and cost per accepted image before sizing tens/hundreds of daily images;
6. keep verified-person reference resolution blocked until identity-reference execution is implemented and similarity gates remain intact.

## Production isolation
- `main.py`: untouched.
- Telegram publishing: untouched.
- legacy production renderer: untouched.
- no paid API or provider added.
- no secrets added.
- no model weights committed.
- no fake PNG generated.
