# Phase 18 Implementation Log — CS488

## Scope
Activate the already CPU-validated Candidate 1 PNG chunk-semantics verifier in the real First Genuine Golden v6 critical path, without changing `main` and without weakening any factual, identity, sentiment, zero-cost, semantic-publication, provenance, CUDA/BF16, Human Review, Golden-quality, or publication authority gate.

## Baseline reviewed
- Branch: `phase18/story-intelligence`
- Baseline SHA: `c7552460a443bc8a5dc134001422a69f753a8943` (CS487)
- CS487 GitHub Actions review: Story Intelligence Verification #6027 succeeded; CPU Verification Diagnostics #229 succeeded; all other returned Phase 18 workflow runs for the exact SHA were successful.
- `main` was not modified.

## Changes
### Modified
- `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`
  - Added `tools/phase18_verify_first_genuine_golden_png_chunk_semantics.py` to immutable tracked-source presence checks.
  - Added a fail-closed `Prove Candidate 1 PNG chunk semantics before review packaging` step immediately after full PNG structural verification and before canonical RGB8 verification / model-runtime replay / Human Review packaging.
  - The step consumes the exact structure-v3 evidence and exact Candidate 1 bytes already bound to the source commit, and writes `output/phase18_gpu_smoke/first-genuine-golden-v6-png-chunk-semantics.json`.
  - No publication or generation authority is granted by this evidence.

### Added
- `docs/PHASE18_IMPLEMENTATION_LOG_488.md`

### Deleted
- None.

## Preserved gates
- factual/source-consensus gate: unchanged
- entity/identity verification: unchanged
- sentiment / loser-respect neutrality: unchanged
- `$0-local`, HF offline, Transformers offline: unchanged
- no network download authority: unchanged
- `SemanticPublicationGate`: unchanged
- exact source commit and tracked-source replay: unchanged
- approved model snapshot/runtime replay: unchanged
- real CUDA + native BF16 requirement: unchanged
- no FP16/FP32 or CPU generation substitution: unchanged
- PNG structure-v3 and canonical RGB8 gates: unchanged and still required
- Human Visual Review and Golden-quality approval: still manual and closed
- publication and Seeds 2–4 authorities: still closed

## Why this materially reduces the remaining gap
Before CS488, chunk-semantics verification existed and had CPU tests, but a real GPU Candidate 1 could bypass it because the Golden workflow did not invoke it. CS488 moves that verifier into the real fail-closed execution path. A generated PNG containing an unknown critical chunk, reserved-bit violation, non-consecutive IDAT sequence, or invalid PLTE ordering can no longer proceed to review packaging.

## Validation state
The baseline CS487 is CI-green. CS488 requires fresh GitHub Actions validation on its new HEAD before it can be called terminal-green. The chunk-semantics verifier itself was already repaired in CS487 and its CPU/Story Intelligence suites passed on the baseline.

## Remaining work
1. Wait for / inspect CS488 CPU and Story Intelligence CI.
2. If green, bind the chunk-semantics evidence cryptographically into the exact Human Review bundle and add independent replay before success upload, rather than merely leaving the evidence in GPU diagnostics.
3. Do not fabricate a Golden PNG. Actual Candidate 1 generation remains blocked until a compatible self-hosted NVIDIA runner is available with CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` / offline-only constraints.
