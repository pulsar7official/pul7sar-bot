# Phase 18 Implementation Log — CS491

## Scope
Activate the already-tested PNG chunk-semantics review-bundle binder on the real First Genuine Golden v6 critical path, without weakening any existing authority, provenance, zero-cost, semantic-publication, or visual-quality gate.

## Baseline reviewed
- Branch: `phase18/story-intelligence` only.
- Baseline HEAD: `77ce2fc1f99acb6a3466b969d918b39caa496739` (CS490).
- GitHub reported 12 Phase 18 workflow runs for the baseline SHA; the returned completed runs were successful.
- `main` was not modified.
- CS490 had already upgraded chunk-semantic evidence to v2 with an intrinsic SHA-256 dependency on the exact structure-v3 evidence bytes and had corresponding CPU-safe tests.

## Changes
### Modified
- `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`
  - Added `tools/phase18_bind_png_chunk_semantics_to_review_bundle.py` to immutable tracked-source presence checks.
  - Added fail-closed chunk-semantics binding immediately after structure binding and before canonical RGB8 binding.
  - Added independent chunk-semantics binding replay before canonical replay, tracked-source replay, and success upload.
  - The binding consumes `first-genuine-golden-v6-png-chunk-semantics.json` and writes `first-genuine-golden-v6-png-chunk-semantics-review-binding.json` on replay.

### Added
- `docs/PHASE18_IMPLEMENTATION_LOG_491.md`

### Deleted
- None.

## Critical-path order after CS491
`Candidate 1 -> source/runner/PNG binding -> PNG structure-v3 -> chunk-semantics-v2 -> canonical RGB8 -> exact model/runtime replay -> Human Review packaging -> zero-cost bind -> structure bind -> chunk-semantics bind -> canonical bind -> exact bundle replay -> zero-cost replay -> structure replay -> chunk-semantics replay -> canonical replay -> immutable tracked-source replay -> success upload`.

## Gates preserved
No changes weaken or bypass:
- factual/source-consensus gates;
- identity/entity gates;
- sentiment and loser-respect gates;
- `SemanticPublicationGate`;
- `$0-local`, offline-only, and network-isolation requirements;
- immutable source binding and `main` isolation;
- exact approved model snapshot/runtime provenance;
- real CUDA + native BF16 requirement with no FP16/FP32 substitution;
- PNG structural, chunk-semantic, and canonical RGB8 requirements;
- Human Visual Review and Golden-quality approval;
- publication authority and Seeds 2–4 authority, which remain closed.

No paid API, model-download path, CPU generation fallback, FP16 fallback, or FP32 fallback was added.

## Testing and verification
- Baseline CS490 CI was reviewed before modification; GitHub reported 12 Phase 18 runs for the baseline SHA and the returned completed runs were successful.
- The activated binder is the CS489/CS490 binder whose unit tests cover successful bind/replay, exact upstream structure SHA-256 linkage, missing structure evidence, structure-byte drift, semantic-evidence drift, false semantic verification, old schema rejection, forged upstream hashes, and publication-authority drift.
- CS491 itself must be treated as pending until GitHub Actions completes on its new exact HEAD. No terminal-green claim is made in this log.

## First Genuine Golden PNG status
Not generated in this change set. No GPU result is fabricated.

The remaining execution blocker is a compatible self-hosted NVIDIA environment with all of the following simultaneously available: CUDA-enabled PyTorch, a real CUDA device, native BF16 support, sufficient VRAM/RAM/cache/filesystem headroom, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under `$0-local` and offline-only constraints.

## Remaining gap
After CS491 becomes CI-green, the chunk-semantic evidence graph is no longer merely diagnostic: it is cryptographically bound into the same Human Review bundle and independently replayed before success upload. Unless CI exposes a concrete defect or another material evidence-graph gap is found, the primary remaining gap is execution of Candidate 1 on the compatible NVIDIA runner followed by Human Visual Review / Golden-quality approval.