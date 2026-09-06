# PUL7SAR Phase 18 — Change Set 184

## Immutable Qwen semantic preflight in the canonical Golden Editorial v6 workflow

### Goal

Remove a remaining pre-FLUX semantic reproducibility gap in the canonical self-hosted Golden Editorial v6 workflow without weakening any factual, identity, sentiment, zero-cost, semantic-publication, or visual-quality gate.

### Problem found

The canonical `.github/workflows/phase18-first-genuine-golden-v6.yml` already pinned the Phase 18 source SHA and required self-hosted CUDA/native BF16 before Candidate 1. The strict staging path later required Qwen BASE_SCENE approval and recorded the approved Qwen model identity.

However, the workflow did not explicitly run the existing `phase18_preflight_semantic_gpu.py` before Candidate 1. That left a practical gap: the immutable Qwen snapshot/cache and exact semantic runtime could be discovered too late, after entering the generation path.

### Changes

#### Modified `.github/workflows/phase18-first-genuine-golden-v6.yml`

- Added a fail-closed semantic preflight before the resource/runtime-locked Candidate 1 step.
- Runs `tools/phase18_preflight_semantic_gpu.py` on the same self-hosted CUDA host.
- Requires the `pul7sar-phase18-semantic-gpu-preflight-v2` contract.
- Verifies exact `Qwen/Qwen2.5-VL-3B-Instruct` identity and the approved immutable upstream revision.
- Verifies `resolved_snapshot_revision` equals the approved revision and `revision_pinned=true`.
- Requires `$0-local`, semantic runtime readiness, semantic model readiness and CUDA availability.
- Requires `generation_authorized=false`, `queue_mutated=false`, `png_created=false`, and `publication_ready=false` from the preflight.
- Replays the same semantic-preflight receipt after Candidate 1 staging before artifact upload.
- Cross-checks the strict staging receipt against the approved Qwen model/revision.

#### Modified `tests/test_phase18_first_genuine_golden_v6_workflow.py`

- Regression-locks semantic preflight before Candidate 1 execution.
- Requires Qwen model/revision/snapshot evidence in the canonical workflow.
- Requires zero-cost and authority-closed semantic preflight semantics.
- Requires semantic identity replay before artifact upload.

### Safety / quality contract

No existing gate is weakened. Candidate 1 still cannot authorize human acceptance, Golden approval, publication, or Seeds 2-4. The change only moves immutable semantic-model proof earlier and replays it later.

### Genuine PNG status

No PNG is fabricated by this change. Genuine Golden Editorial v6 Candidate 1 still requires a compatible self-hosted NVIDIA CUDA/native-BF16 environment with adequate live GPU/system memory and the approved local runtime stack.
