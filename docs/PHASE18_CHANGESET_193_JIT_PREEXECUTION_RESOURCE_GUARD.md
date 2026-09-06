# PUL7SAR Phase 18 — Change Set 193

## Just-in-Time Pre-Execution Resource Guard for Golden Editorial v6

### Purpose

The canonical Golden Editorial v6 path already performed GPU, VRAM and host-RAM qualification before model-cache and runtime work. That evidence materially reduced risk, but it was still an early snapshot rather than a final proof immediately before Candidate 1 entered the strict generation command.

On a shared or long-running self-hosted GPU, another process can consume CUDA memory or system RAM after model/cache qualification. The worker-based queue path already has lease-bound resource requalification, but the current strict Golden v6 Colab/self-hosted staging path executes Candidate 1 directly and therefore needed its own final just-in-time resource boundary.

### Implemented

`tools/phase18_colab_first_genuine_golden.py` now performs, immediately before delegating Candidate 1:

1. a fresh `phase18_qualify_gpu_host.py` measurement written to `candidate-01-jit-gpu-qualification.json`;
2. fail-closed validation of CUDA, native BF16, model identity, `$0-local`, live-free VRAM and resource-policy authority;
3. a fresh `phase18_preflight_host_memory.py` measurement written to `candidate-01-jit-host-memory.json`;
4. fail-closed validation of live available system RAM and authority closure;
5. SHA-256 + byte-size sealing of both receipts before Candidate 1 starts;
6. replay of both receipts after generation/semantic staging to reject resource-evidence mutation during execution.

The successful first-genuine staging receipt now records the sealed GPU/RAM evidence and the exact live resource floors observed immediately before generation.

### Safety properties

This change does not authorize generation from the resource checks themselves. The JIT receipts must remain incapable of:

- downloading or loading model weights;
- using paid APIs;
- mutating the durable queue;
- granting semantic approval;
- granting Golden quality approval;
- granting publication readiness.

The existing factual, identity, sentiment/neutrality, `$0-local`, pinned model revision, BF16, semantic/layer, Golden quality, exact brand/typography and SemanticPublicationGate contracts remain unchanged.

### Regression coverage

Added `tests/test_phase18_first_genuine_golden_jit_resources.py` covering:

- valid CUDA/BF16/live-VRAM JIT qualification;
- rejection when live-free VRAM falls below the Golden floor;
- rejection of paid/illegal resource authority;
- valid live host-RAM qualification;
- rejection when live host RAM falls below the first-Golden floor;
- detection of JIT receipt byte drift during generation;
- source-order regression proving JIT guard → Candidate 1 → resource replay → genuine candidate verification.

### Files

Modified:

- `tools/phase18_colab_first_genuine_golden.py`

Added:

- `tests/test_phase18_first_genuine_golden_jit_resources.py`
- `docs/PHASE18_CHANGESET_193_JIT_PREEXECUTION_RESOURCE_GUARD.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_193.md`

Deleted: none.

`main` and `main.py` are not modified by this change set.
