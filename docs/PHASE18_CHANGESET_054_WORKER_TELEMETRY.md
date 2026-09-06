# PUL7SAR Phase 18 — Change Set 054

## Durable GPU worker heartbeat and measured raw-generation capacity

### Purpose
Turn the first genuine GPU execution into operational evidence for 24/7 scaling instead of a one-off demo. This change set does not invent throughput before a real PNG exists and does not treat raw generation as publication readiness.

### Added
- `engine/intelligence/worker_telemetry.py`
  - immutable `WorkerHeartbeat`
  - immutable `GenerationPerformanceSample`
  - dependency-free `FilesystemWorkerTelemetryStore`
  - `GenerationCapacityEstimator`
  - `RawGenerationCapacityReport`
- `tests/test_phase18_worker_telemetry.py`
  - heartbeat round-trip
  - append-only performance samples
  - fail-closed/no-estimate behavior before a genuine successful GPU sample
  - measured throughput calculation from successful samples only
  - invalid utilization rejection
  - filesystem-safe worker identity validation

### Modified
- `tools/phase18_gpu_worker.py`
  - writes a durable heartbeat when the CUDA/BF16 worker becomes ready
  - updates heartbeat after every worker cycle
  - records elapsed time for every non-idle generation cycle
  - records worker/GPU/VRAM/dtype/outcome metadata
  - derives raw images/hour and images/day only from genuine successful samples
  - exposes a configurable utilization factor; default is 0.70
  - labels estimates explicitly as `raw_generation_only_not_publication_capacity`

### Safety properties
- No `main` modification.
- No production publishing modification.
- No paid provider or API introduced.
- No CUDA/BF16 fallback introduced.
- No fake PNG or synthetic success sample is created.
- Zero successful GPU samples => capacity remains `unproven`, with no numerical images/day claim.
- A generated PNG is not counted as publishable output; semantic and Golden quality gates remain separate and mandatory.

### Why this materially reduces the production gap
Once candidate 1 runs on a real compatible GPU, the same worker that generates it now automatically records the observed latency and hardware context. PUL7SAR can then measure, rather than guess, how many raw generations a worker can sustain and how many workers would be required for a target daily volume.

### Remaining blocker to first genuine PNG
A compatible CUDA GPU host with native BF16 support and sufficient VRAM must execute the already locked FLUX.2 Klein handoff. GitHub CPU CI cannot satisfy that requirement and no result is fabricated in its absence.
