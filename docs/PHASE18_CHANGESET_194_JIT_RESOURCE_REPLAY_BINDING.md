# PUL7SAR Phase 18 — Change Set 194

## JIT Resource Replay Binding for the First Genuine Golden Editorial v6

### Problem

Change Set 193 added live GPU and host-RAM qualification immediately before Candidate 1 and sealed those two receipts into the strict Golden staging receipt. The strict staging path replayed those files immediately after generation, but the outer canonical offload workflow still treated the staging receipt itself as the terminal evidence boundary.

That left a nested-evidence gap: after staging was written, an outer workflow could verify the staging file hash without independently reopening and revalidating the JIT GPU/RAM receipts that staging references.

For the first genuine Golden PNG, the final workflow boundary should prove that the just-in-time resource evidence itself still exists, still hashes to the values recorded before generation, still meets the live VRAM/RAM floors, and still carries no publication/generation authority.

### Implemented

1. Added `engine/intelligence/golden_jit_resource_replay.py`.
   - CPU-safe evidence replay only.
   - Re-hashes the nested JIT GPU qualification and host-memory receipts.
   - Rejects repository path escape, hash/size drift, low live-free VRAM, low host RAM, model/runtime/cost drift, and authority drift.
   - Re-checks staging scalar resource values against the underlying receipts.
   - Emits a deterministic resource fingerprint SHA-256.

2. Added `tools/phase18_colab_first_genuine_jit_replay_locked.py`.
   - Delegates to the existing pre-model + actual-offload locked Golden v6 path.
   - Replays the exact inner resource lock and strict staging receipt by SHA.
   - Runs the new JIT resource replay verifier against the nested pre-execution evidence.
   - Binds the offload lock, inner resource lock, strict staging receipt, JIT replay receipt, and exact PNG by SHA-256.
   - Keeps human approval, Golden approval, publication, and Seeds 2-4 closed.

3. Added `.github/workflows/phase18-first-genuine-golden-v6-jit.yml`.
   - Manual/self-hosted only.
   - Immutable dispatch SHA with complete ancestry and Phase 18 branch reattachment.
   - Read-only main comparison and `main.py` isolation check.
   - Requires existing CUDA-enabled PyTorch; never replaces PyTorch automatically.
   - Executes the JIT-replay-locked Candidate 1 path.
   - Replays the outer evidence set and independently reruns nested JIT evidence verification before artifact upload.

4. Added regression coverage:
   - `tests/test_phase18_golden_jit_resource_replay.py`
   - `tests/test_phase18_first_genuine_golden_v6_jit_lock.py`
   - `tests/test_phase18_first_genuine_golden_v6_jit_workflow.py`

### Safety / quality gates preserved

No factual, identity, sentiment, zero-cost, semantic-publication, or visual-quality gate was weakened. In particular:

- Fact Lock remains fail-closed.
- Entity/Identity Verification remains fail-closed.
- Sentiment/Neutrality and respectful result treatment remain unchanged.
- `$0-local` remains mandatory.
- Pinned FLUX/Qwen model revisions remain mandatory.
- Native BF16 and live resource qualification remain mandatory.
- Safe pre-model offload and actual-executor offload binding remain mandatory.
- Generated text/branding/exact facts/entity marks/exact sport geometry remain prohibited.
- Qwen BASE_SCENE/layer ownership remains mandatory.
- Golden minimum `8.5` / elite target `9.0+` remain downstream.
- Exact Brand/Typography and SemanticPublicationGate remain downstream and closed.
- Seeds 2-4 remain unauthorized before genuine Candidate 1 succeeds and is visually accepted.

### Files

Added:

- `engine/intelligence/golden_jit_resource_replay.py`
- `tools/phase18_colab_first_genuine_jit_replay_locked.py`
- `.github/workflows/phase18-first-genuine-golden-v6-jit.yml`
- `tests/test_phase18_golden_jit_resource_replay.py`
- `tests/test_phase18_first_genuine_golden_v6_jit_lock.py`
- `tests/test_phase18_first_genuine_golden_v6_jit_workflow.py`
- `docs/PHASE18_CHANGESET_194_JIT_RESOURCE_REPLAY_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_194.md`

Modified: none.

Deleted: none.

### Genuine Golden PNG status

No PNG is claimed by this change set. The external blocker remains the absence, in the available execution environment, of a compatible self-hosted host that simultaneously proves NVIDIA CUDA, native BF16, sufficient live VRAM and host RAM, safe local Diffusers offload, pinned FLUX/Qwen snapshots, stable runtime fingerprint, sufficient post-cache disk headroom, and `$0-local` execution.
