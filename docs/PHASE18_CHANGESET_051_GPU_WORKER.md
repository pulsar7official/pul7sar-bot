# PUL7SAR Phase 18 — Change Set 051

## Production GPU worker foundation

Change Set 051 shifts the next Phase 18 step from notebook-centric execution toward an automatable, horizontally scalable GPU-worker architecture without touching production `main`.

### Added

#### `engine/intelligence/generation_jobs.py`
Introduces provider-neutral durable job contracts:
- explicit job state machine: `queued -> leased -> running -> succeeded|failed`
- bounded retry accounting (`attempt`, `max_attempts`)
- lease owner and lease expiry metadata
- locked `request_id`, provider, model and handoff SHA-256 identity
- immutable metadata
- worker capability declaration for provider/model/CUDA/BF16/VRAM/concurrency
- fail-closed capability matching

The contracts intentionally do not depend on Redis, SQS, Celery, Kubernetes, RunPod, Modal, Colab, or a specific GPU vendor. Queue and compute infrastructure remain replaceable adapters.

#### `engine/intelligence/generation_worker.py`
Adds a single-cycle worker service around an injected queue store and locked generation executor.

Worker behavior:
1. lease at most one compatible job
2. verify lease ownership and expiry
3. verify provider/model/CUDA/BF16 capability before execution
4. increment bounded attempt count
5. execute through an injected locked executor
6. reject any returned result whose request ID, SHA-256, provider or model differs from the leased job
7. requeue only explicitly retryable failures while attempts remain
8. make identity drift/capability mismatch terminal
9. never lower the Golden BF16 requirement or existing quality/publication thresholds

The service is deliberately queue-backend neutral so future production deployment can use a persistent queue while local/test execution can use an in-memory or filesystem adapter.

#### `tests/test_phase18_generation_worker.py`
Adds eight `unittest` regression cases covering:
- illegal state-transition rejection
- successful exact-identity execution
- terminal rejection of executor identity drift
- retryable GPU failure requeue
- retry exhaustion
- BF16 fail-closed behavior
- expired lease rejection
- idle worker behavior

The test file was immediately converted from pytest-style functions to `unittest.TestCase` because the repository Phase 18 CI intentionally runs `unittest discover`; this ensures the new tests are actually executed, not only syntax-checked.

### Verification
GitHub Actions run `32600686895` completed successfully on commit `2dd97e902524849b00e0859bd259211dbb667f2b`.

The existing Phase 18 workflow syntax-checks all intelligence modules/tests, runs the full Phase 18 unittest suite, verifies production isolation, rebuilds the Golden handoff and four-candidate batch, verifies batch integrity, and uploads the handoff artifacts.

### Production isolation
- `main.py`: untouched
- `main` branch: untouched
- Telegram publishing: untouched
- legacy image sourcing/rendering: untouched
- no paid image API connected
- no secrets added
- no GPU vendor dependency added

### Architectural effect
Phase 18 can now evolve from a manual notebook proof toward:

`GenerationPackage -> SHA-256 Handoff -> Durable Job Queue -> Capability-matched GPU Worker -> Locked Executor -> Real PNG -> Semantic/Golden Quality Gates -> PostComposition -> Export`

The queue/worker layer does not replace Fact Lock, Identity Lock, Sentiment, Neutrality, SemanticPublicationGate, or Golden Visual scoring. It only provides durable automated transport and execution semantics around them.

### Remaining blocker to first genuine PNG
A compatible CUDA runtime still has to execute the locked FLUX.2 Klein handoff. GitHub CPU CI cannot truthfully generate the image, and no fake PNG is produced.

### Immediate next work
1. Add a concrete durable queue adapter suitable for a continuously running worker, while remaining isolated from `main`.
2. Add an executor adapter that invokes the already verified Phase 18 FLUX.2 command path and maps its dedicated result JSON into `WorkerExecutionResult`.
3. Add worker telemetry/throughput fields needed to size production capacity (generation latency, retries, GPU busy time).
4. Run candidate 1 on a compatible CUDA/BF16 worker and register the first genuine PNG.
