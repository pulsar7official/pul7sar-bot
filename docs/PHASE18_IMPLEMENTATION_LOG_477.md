# Phase 18 Implementation Log — CS477

## Scope

Branch only: `phase18/story-intelligence`.

This checkpoint does not modify `main`, does not authorize publication, does not create a Golden PNG, does not introduce network/model downloads, and does not add CPU/FP16/FP32 generation fallbacks.

## Reviewed starting state

Starting HEAD: `3332e8ec4985113c9f3baf3973952b13be57ad44` (CS476).

GitHub Actions showed that CS476 was **not terminal-green**. `verify-story-intelligence` and `cpu-diagnostics` both failed in CPU validation. The uploaded CPU diagnostics artifact identified the exact regression:

`tests/test_phase18_first_golden_png_structure.py` imported `pytest`, while the canonical Phase 18 CPU verification installs/runs the `unittest` suite and does not install pytest. The loader therefore failed with `ModuleNotFoundError: No module named 'pytest'` before the PNG-structure tests could run.

## Changes

### Modified

- `tests/test_phase18_first_golden_png_structure.py`
  - Removed the accidental `pytest` dependency.
  - Converted the tests to stdlib `unittest.TestCase`.
  - Replaced the pytest `tmp_path` fixture with `tempfile.TemporaryDirectory()`.
  - Replaced `pytest.raises(...)` with `self.assertRaisesRegex(...)`.
  - Preserved the CS476 assertions for full PNG structure, CRC failure, trailing bytes, decoded scanline size, filter-byte validation, fail-closed Adam7 handling, authority drift, and workflow ordering.

### Added

- `tools/phase18_bind_png_structure_to_review_bundle.py`
  - CPU-safe, stdlib-only binder/replayer for the already-generated PNG structure evidence.
  - Verifies the structure report is for the same branch, source SHA, Candidate 1 and PNG SHA as the exact Human Review bundle.
  - Requires all structural proof flags to be true: CRC, exact IDAT/zlib termination, decoded scanline layout, scanline filter validity, terminal IEND, no trailing bytes, and non-interlaced canonical output.
  - Requires every authority field to remain closed.
  - Copies the exact structure report bytes into `evidence/png_structure.json`, records SHA-256 and byte size in `review-bundle-manifest.json`, and provides an independent replay mode that rejects byte drift.
  - This tool is deliberately preparatory in CS477: it is not yet wired into the Golden workflow. Integration must occur only after its CPU tests are green.

- `tests/test_phase18_png_structure_review_binding.py`
  - Verifies successful bind/replay.
  - Rejects PNG identity drift.
  - Rejects incomplete structure evidence.
  - Rejects authority drift.
  - Rejects evidence byte drift after binding.
  - Uses only Python stdlib/unittest.

- `docs/PHASE18_IMPLEMENTATION_LOG_477.md`
  - This record.

### Deleted

None.

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

## Testing status at commit time

The local execution environment available to this automation cannot resolve `github.com`, so a clean local clone/full suite was not available. This is treated as an execution-environment limitation, not as a passing test result.

GitHub Actions is the canonical test authority for this checkpoint. CS477 must not be described as terminal-green until the exact final HEAD completes the Phase 18 CPU verification successfully.

## Remaining path to first genuine Golden PNG

1. Confirm CS477 CPU CI is green.
2. If green, wire `phase18_bind_png_structure_to_review_bundle.py` into the exact Golden workflow after review-bundle packaging and before closed-set replay/upload, with workflow-order regression coverage.
3. Execute the genuine Candidate 1 path only on the required self-hosted NVIDIA runner with CUDA-enabled PyTorch, a real CUDA device, native BF16, sufficient VRAM/RAM/cache/filesystem headroom, approved runtimes, and the exact approved local Qwen2.5-VL and FLUX.2 snapshots under `$0-local`/offline-only.
4. Do not fabricate a PNG if that compatible GPU environment is unavailable.
