# Phase 18 Implementation Log — CS426

## Scope

CS426 repairs CPU validation for the JIT local-only provenance regression introduced in CS425. All work remains restricted to `phase18/story-intelligence`; `main` is read-only.

## Reviewed baseline

- Starting Phase 18 HEAD: `ff6835a4beeb2c5553e6ed9b8cba8cb5169fa0fb` (CS425).
- `Phase 18 Story Intelligence Verification` run `34706591349` completed with `failure` on that exact SHA.
- The failing job was `verify-story-intelligence`; the first failing step was `Syntax and discover validation`.
- No GPU execution occurred; all later production/handoff steps were skipped.

## Exact CPU-side blocker found

`tests/test_phase18_first_genuine_golden_v6_jit_local_only_provenance.py` used `pytest` module-level import, `@pytest.mark.parametrize`, and pytest-style test functions.

The canonical Phase 18 CPU validator executes `python -m unittest discover -v -s tests -p test_phase18_*.py`, while repository `requirements.txt` does not install `pytest`. The new regression therefore introduced an undeclared test dependency into the official CI discovery path.

This was a test-harness defect only. No evidence indicates a failure in the JIT production lock, CUDA/BF16 gates, local-only provenance logic, or image-generation path.

## Modified

### `tests/test_phase18_first_genuine_golden_v6_jit_local_only_provenance.py`

- Removed the `pytest` dependency entirely.
- Converted the regression suite to `unittest.TestCase`, matching the repository's canonical Phase 18 CPU validation harness.
- Replaced `@pytest.mark.parametrize` with a deterministic case table executed through `self.subTest(...)`.
- Replaced `pytest.raises(...)` with `self.assertRaisesRegex(...)`.
- Preserved the same positive and negative local-only provenance coverage.
- Preserved workflow-order assertions proving local-only replay occurs before artifact upload.
- Preserved branch isolation, offline flags, and closed downstream-authority assertions.
- Added the standard `unittest.main()` entrypoint.

## Added

### `docs/PHASE18_IMPLEMENTATION_LOG_426.md`

This implementation log records the observed CS425 CI failure, root cause, exact repair, unchanged safety contracts, and remaining GPU blocker.

## Deleted

None.

## Intentionally unchanged

- No production Python changes.
- No workflow changes.
- No prompt changes.
- No seed changes.
- No image-generation parameter changes.
- No approved Qwen/FLUX model ID or immutable revision changes.
- No dependency additions; specifically, `pytest` was not added to `requirements.txt`.
- No weakening of factual, entity/identity, sentiment, zero-cost, semantic-publication, or visual-quality gates.
- No write, merge, rebase, reset, or ref update to `main`.

## Validation state

The repair commit is `8de016d700a016646cb84fe156bd50711f52d538` on `phase18/story-intelligence`. CI must complete on the final CS426 HEAD before CS426 can be described as terminal-green.

## Remaining blocker to the first genuine Golden PNG

CS426 does not fabricate a PNG. Genuine Candidate 1 generation still requires a compatible self-hosted NVIDIA runner with CUDA-enabled PyTorch, at least one CUDA device, native BF16, sufficient VRAM/RAM/storage, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already available in the canonical local Hugging Face cache. Network model downloads remain forbidden under `$0-local`.

The downstream authorities remain closed:

- `human_visual_review_approved=false`
- `golden_quality_approved=false`
- `publication_ready=false`
- `seeds_2_to_4_authorized=false`
