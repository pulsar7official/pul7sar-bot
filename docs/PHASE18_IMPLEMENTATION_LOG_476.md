# Phase 18 Implementation Log — CS476

## Scope

Branch: `phase18/story-intelligence` only. `main` was not modified.

CS476 begins by repairing the concrete CS475 CPU/CI regression, then materially tightens the first-Golden PNG acceptance boundary. The failed CS475 CRC unit test was corrupting the final byte of the `IEND` chunk type rather than a CRC byte, so the production verifier correctly rejected the malformed chunk as `CHUNK_TYPE_INVALID` while the test incorrectly expected `CRC_INVALID`.

## Added

No new production path, workflow, generation fallback, network path, or authority grant was added.

Additional test coverage was added inside the existing PNG structural test module for:

- exact decompressed scanline byte count;
- valid PNG filter-byte range for every row;
- fail-closed rejection of Adam7/interlaced Candidate 1 until all seven pass geometries are explicitly verified.

## Modified

- `tools/phase18_verify_first_genuine_golden_png_structure.py`
  - advances structural evidence schema from v1 to v2;
  - replaces permissive `zlib.decompress(...)` acceptance with `zlib.decompressobj()` and requires exact stream termination (`eof=true`, no `unused_data`, no `unconsumed_tail`);
  - computes channels, bits-per-pixel, bytes per scanline and the exact expected decompressed byte count from `IHDR`;
  - requires the decoded raster length to match that geometry exactly;
  - verifies every scanline filter byte is one of PNG filter types 0–4;
  - records deterministic raster-layout evidence in the verifier output;
  - fail-closes on interlaced Candidate 1 rather than pretending Adam7 pass structure was validated.

- `tests/test_phase18_first_golden_png_structure.py`
  - repairs the CS475 CRC fixture so it mutates an actual CRC byte while preserving the `IEND` chunk type;
  - asserts exact-zlib and scanline-layout evidence for a valid minimal RGB8 PNG;
  - adds short decoded-raster rejection;
  - adds invalid filter-byte rejection;
  - adds explicit interlaced/Adam7 fail-closed coverage;
  - preserves authority-drift and workflow-ordering tests.

## Deleted

None.

## CI regression found during review

Before CS476, exact CS475 HEAD `65b52faa3ad94ef94fd8bce6d168361c5873b3d7` had both `Phase 18 Story Intelligence Verification` and `Phase 18 CPU Verification Diagnostics` complete with failure. The Story Intelligence job failed specifically at `Syntax and discover validation`; CPU diagnostics preserved a nonzero validator result. This was therefore treated as a real blocker and repaired before claiming further progress.

## Test intent

The verifier remains stdlib-only and CPU-safe. The strengthened checks operate only on synthetic unit-test PNGs or the already-generated, cryptographically bound Candidate 1 file. No test creates or claims a genuine Golden Visual.

The critical acceptance property after CS476 is stronger than “PNG signature + CRC + zlib decoded”: for the canonical non-interlaced Candidate 1, the decompressed IDAT raster must have exactly the byte geometry implied by `IHDR`, every row must start with a legal PNG filter byte, and the zlib stream must terminate without hidden trailing compressed payload.

## Authority state preserved

The existing verifier still requires and emits:

- `authoritative_gate=false`
- `network_download_authorized=false`
- `generation_authorized=false`
- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`

No factual, identity/entity, sentiment/loser-respect, SemanticPublicationGate, Human Visual Review, Golden-quality, model-revision, CUDA/native-BF16, `$0-local`, offline-only, freshness, provenance, runtime-replay, review-bundle, or publication gate is weakened.

No CPU, FP16 or FP32 generation fallback is added. No paid API, download path or network bypass is added.

## Remaining blocker

The first genuine Golden Visual PNG still requires a compatible self-hosted NVIDIA execution environment with CUDA-enabled PyTorch, a real CUDA device, native BF16 support, sufficient live VRAM/RAM/cache/filesystem headroom, the approved runtime stack, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already available locally under the `$0-local`/offline-only contract.

Until that canonical GPU path executes successfully, CS476 only repairs CI and tightens the PNG raster-integrity acceptance boundary; it does not fabricate or claim a Golden PNG.