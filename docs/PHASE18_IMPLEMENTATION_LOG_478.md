# Phase 18 Implementation Log — CS478

## Scope

Branch only: `phase18/story-intelligence`.

This checkpoint does not modify `main`, does not authorize publication, does not create or fabricate a Golden PNG, does not introduce network/model downloads, and does not add CPU/FP16/FP32 generation fallbacks.

## Reviewed starting state

Starting HEAD: `1beabab3698819ce46b6eed6d89e6d75de9112ad` (CS477).

GitHub Actions for the exact CS477 HEAD are terminal-green for the Phase 18 Story Intelligence Verification and CPU Verification Diagnostics. That clears the prerequisite documented in CS477 for activating the already-tested PNG-structure review-bundle binder in the critical Golden workflow.

## Changes

### Modified

- `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`
  - Added `tools/phase18_bind_png_structure_to_review_bundle.py` to the immutable Phase 18 source/tool presence proof.
  - After the exact Human Review bundle is packaged and after zero-cost network evidence is bound, binds the previously verified Candidate 1 PNG structure report into the bundle as `evidence/png_structure.json`.
  - The binder requires the same branch, source commit, Candidate 1 identity, PNG SHA-256, `$0-local`/offline-only policy, complete structural proof and closed authorities.
  - Runs the generic exact closed-set Human Review bundle replay after the PNG structure evidence has been added, so that the new evidence file and manifest entry are covered by closed-set byte/SHA verification.
  - Adds an independent PNG structure binding replay after the generic bundle replay and zero-cost network replay, and before tracked-source replay and success upload.
  - Writes the independent replay result to `output/phase18_gpu_smoke/first-genuine-golden-v6-png-structure-review-binding.json`.

- `tests/test_phase18_first_golden_fresh_workflow.py`
  - Added regression coverage requiring the PNG structure binder tool to be part of immutable source proof.
  - Requires the structure report to precede review packaging.
  - Requires packaging -> zero-cost bind -> PNG structure bind -> exact closed-set bundle replay -> zero-cost replay -> PNG structure replay -> tracked-source replay -> success upload ordering.
  - Requires the exact structure evidence and replay output paths.

### Added

- `docs/PHASE18_IMPLEMENTATION_LOG_478.md`
  - This record.

### Deleted

None.

## Critical-path result

The relevant end of the Golden workflow is now:

`Candidate 1 -> PNG structural verification -> post-generation model/runtime replay -> exact Human Review bundle packaging -> zero-cost network evidence bind -> PNG structure evidence bind -> exact closed-set bundle replay -> zero-cost network replay -> PNG structure replay -> immutable tracked-source replay -> success upload`

The PNG structural proof therefore no longer exists only as a pre-packaging diagnostic. It is now cryptographically represented in the Human Review artifact manifest, included in the closed file set, and independently replayed before upload.

## Gates preserved

No factual/source-consensus, entity/identity, sentiment/loser-respect, zero-cost, offline-only, semantic-publication, Human Visual Review, Golden-quality, source provenance, runner/CUDA/native-BF16, model snapshot/runtime replay, or publication/Seeds authority gate was weakened.

The sensitive authorities remain required to be false:

- `authoritative_gate=false`
- `network_download_authorized=false`
- `generation_authorized=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

No paid API, network/model download path, CPU generation fallback, FP16 substitution, FP32 substitution, or automatic publication path was added.

## Testing status at commit time

CS477 is terminal-green in GitHub Actions before this activation.

The CS478 regression test is stdlib/unittest and checks workflow ordering/text without GPU execution. GitHub Actions on the exact final CS478 HEAD remains the canonical CI authority; CS478 must not be described as terminal-green until those runs complete successfully.

The local execution environment available to this automation still cannot resolve `github.com`, so a local clean clone/full-suite execution is unavailable and is not counted as a passing result.

## Remaining path to first genuine Golden PNG

1. Confirm exact final CS478 HEAD is terminal-green in Phase 18 CPU/Story Intelligence verification.
2. Execute the genuine Candidate 1 path only on the required self-hosted NVIDIA runner with CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, approved runtimes, and the exact approved local Qwen2.5-VL and FLUX.2 snapshots under `$0-local`/offline-only.
3. Let the now-complete provenance/PNG/network/runtime/source review chain fail closed on any mismatch.
4. Do not fabricate a PNG if that compatible GPU execution environment is unavailable.
