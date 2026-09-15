# Phase 18 Implementation Log — CS475

## Scope

Branch: `phase18/story-intelligence` only. `main` was not modified.

CS475 closes a remaining byte-level gap between a cryptographically bound Candidate 1 file and a genuinely well-formed PNG suitable to advance toward Human Visual Review. Prior gates bound the PNG signature, byte size and SHA-256, but an eight-byte PNG signature plus a stable digest does not by itself prove that the file is a complete structurally valid PNG stream.

## Added

- `tools/phase18_verify_first_genuine_golden_png_structure.py`
  - stdlib-only, CPU-safe, offline verifier;
  - consumes the existing fresh/source-bound manifest and exact recorded Candidate 1 PNG;
  - replays branch, Candidate 1, `$0-local`, offline-only, SHA-256, byte-size and closed-authority state;
  - rejects symlink PNG inputs;
  - verifies PNG signature and complete chunk framing;
  - verifies every chunk CRC;
  - requires one valid first `IHDR`, non-zero dimensions and a valid PNG bit-depth/color-type combination;
  - requires at least one `IDAT` and proves the concatenated IDAT zlib stream decompresses;
  - requires terminal zero-length `IEND` and rejects any trailing bytes;
  - emits deterministic structural evidence without granting Human Review, Golden quality, publication, or Seeds 2–4 authority.

- `tests/test_phase18_first_golden_png_structure.py`
  - valid minimal PNG acceptance;
  - trailing-byte rejection;
  - CRC drift rejection;
  - publication-authority drift rejection;
  - workflow ordering assertion proving the gate executes before post-generation snapshot/runtime replay, review packaging and artifact upload.

## Modified

- `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml`
  - adds the structural verifier to immutable checkout proof;
  - runs `Prove complete Candidate 1 PNG structure before review packaging` immediately after the fresh/source-bound manifest exists and before snapshot/runtime replay and packaging;
  - writes `output/phase18_gpu_smoke/first-genuine-golden-v6-png-structure.json`;
  - preserves the exact self-hosted CUDA/BF16 labels, `$0-local`, offline-only policy, pinned GitHub Actions, model revision gates, factual/identity/sentiment gates, SemanticPublicationGate, Human Visual Review boundary and all closed authorities.

## Deleted

None.

## Test intent

CS475 is intentionally GPU-independent at unit-test level. Its structural parser uses only the Python standard library, so CI can test valid and malformed PNG byte streams without generating an image. The genuine Candidate 1 path remains GPU-gated and no PNG is fabricated by this change set.

## Authority state preserved

The verifier requires and emits:

- `authoritative_gate=false`
- `network_download_authorized=false`
- `generation_authorized=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

No CPU, FP16 or FP32 generation fallback is added. No paid API, download path, network fallback or semantic-publication bypass is added.

## Remaining blocker

The first genuine Golden Visual PNG still requires a compatible self-hosted NVIDIA execution environment with CUDA-enabled PyTorch, a real CUDA device, native BF16 support, adequate live VRAM/RAM/cache/filesystem headroom, the approved runtime stack, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already available locally under the `$0-local`/offline-only contract.

Until that environment executes the canonical Candidate 1 path, CS475 only tightens the acceptance boundary; it does not claim that a genuine Golden PNG exists.
