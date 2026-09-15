# Phase 18 Implementation Log — CS483

## Scope

Activate the already CPU-tested canonical PNG encoding evidence chain in the first genuine Golden v6 workflow, on `phase18/story-intelligence` only. `main` is not modified.

## Baseline reviewed

- Branch: `phase18/story-intelligence`
- Starting SHA: `010fb9afb639385275bbd67bd6feae6768b50604` (CS482)
- CS482 GitHub Actions: 12 workflow runs were present; reviewed runs were completed successfully before this change set.
- CS482 repaired the canonical verifier to consume the CS481 structural evidence v3 contract.

## Changes

### Modified — `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`

The Golden critical path now:

1. proves complete Candidate 1 PNG structure;
2. immediately verifies canonical RGB8 truecolour/non-interlaced encoding from that exact structure evidence;
3. performs post-generation approved snapshot/runtime replay;
4. packages the exact Human Review bundle;
5. binds zero-cost network evidence;
6. binds PNG structural evidence;
7. binds canonical RGB8 encoding evidence;
8. replays the exact closed-set review bundle;
9. independently replays zero-cost, PNG structure, and canonical RGB8 bindings;
10. replays immutable tracked source immediately before success upload.

The immutable checkout proof now also requires:

- `tools/phase18_verify_first_genuine_golden_png_canonical_encoding.py`
- `tools/phase18_bind_png_canonical_encoding_to_review_bundle.py`

New evidence paths:

- `output/phase18_gpu_smoke/first-genuine-golden-v6-png-canonical-encoding.json`
- `evidence/png_canonical_encoding.json` inside the Human Review bundle
- `output/phase18_gpu_smoke/first-genuine-golden-v6-png-canonical-review-binding.json`

### Modified — `tests/test_phase18_first_golden_fresh_workflow.py`

Added regression coverage requiring the canonical verifier and binder to be present and enforcing ordering:

`PNG structure -> canonical RGB8 verify -> package -> PNG structure bind -> canonical bind -> closed-set replay -> PNG structure replay -> canonical replay -> tracked-source replay -> upload`.

The test also pins the exact evidence paths and tool invocations.

### Added — `docs/PHASE18_IMPLEMENTATION_LOG_483.md`

This implementation record.

### Deleted

None.

## Gates preserved

No factual/source-consensus, identity/entity, sentiment/loser-respect, SemanticPublicationGate, zero-cost/offline-only, network isolation, exact model/runtime provenance, CUDA/native-BF16, Human Visual Review, Golden-quality, publication, or Seeds 2–4 authority was weakened.

No paid API, model download path, network fallback, CPU generation fallback, FP16 fallback, or FP32 fallback was added.

Canonical verification remains evidence-only and does not grant Human Review approval, Golden approval, publication readiness, or Seeds 2–4 authority.

## Testing status

CS482 was reviewed before modification and its GitHub Actions baseline was successful. The CS483 workflow regression test is committed together with the workflow activation. New GitHub Actions runs for the final CS483 HEAD must complete before CS483 can be called terminal-green.

## First Genuine Golden PNG status

No First Genuine Golden Visual PNG is claimed or fabricated in this change set.

The remaining execution blocker is a compatible self-hosted NVIDIA runner satisfying all existing requirements simultaneously: CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, approved runtimes, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already available locally under `$0-local` / offline-only execution.

## Material gap reduced

Before CS483, canonical RGB8 verification and bundle binding existed but were not on the live Golden workflow. After CS483, a future real Candidate 1 cannot reach a successful Human Review artifact upload unless its exact PNG has passed canonical RGB8 verification, that proof has been cryptographically bound into the same review bundle, the closed-set bundle replay accepts it, and an independent canonical binding replay succeeds before upload.
