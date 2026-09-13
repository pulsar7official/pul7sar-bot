# PUL7SAR Phase 18 — Change Set 148

## Staged Review Original Scene Admission Binding

### Goal

Close the remaining chain-of-custody gap between the preferred `phase18_first_png_original_scene.py` entrypoint and the later Colab Golden human-review staging path.

Change Set 147 already pins the Original Scene runtime-admission receipt before Candidate 1 generation and replays it afterward. Before this change, `phase18_colab_first_golden_review.py` consumed the returned admission payload but independently re-hashed the persisted receipt later when building the review packet. It did not require that the staging layer itself consume the exact SHA/byte-size evidence produced by the Change Set 147 postflight.

### Modified

- `tools/phase18_colab_first_golden_review.py`
  - requires `original_scene_admission_replayed=true` from the preferred Original Scene first-PNG wrapper;
  - requires a repository-contained admission-receipt path and verifies it is the canonical staging receipt;
  - requires the wrapper-provided `original_scene_admission_sha256` and `original_scene_admission_bytes` values;
  - replays the current receipt bytes against those values before any Hybrid handoff is allowed;
  - rechecks the same SHA and byte size immediately before writing the human-review packet;
  - stores the wrapper-proven SHA, byte size and replay flag directly in `pul7sar-first-golden-human-review-packet-v2` instead of deriving a fresh unrelated admission digest.

- `tests/test_phase18_colab_first_golden_review.py`
  - locks the postflight-binding check before Hybrid handoff;
  - locks `original_scene_admission_replayed=true` as a required input;
  - locks the wrapper-provided SHA/size fields into the human-review packet;
  - locks fail-closed behavior if the receipt drifts before packet creation.

### Added

- `docs/PHASE18_CHANGESET_148_STAGED_REVIEW_ADMISSION_BINDING.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_148.md`

### Deleted

Nothing.

### Gates preserved

No factual, identity, sentiment, zero-cost, semantic-publication or visual-quality gate was relaxed. The change adds evidence replay only and cannot grant semantic approval, Golden approval, Seeds 2–4 authorization or publication authority.

The generator remains FLUX.2 Klein 4B on the current `$0-local` native-BF16 path; exact sport geometry remains deterministic downstream; Qwen BASE_SCENE and HYBRID_SURFACE inspection remain mandatory for the strict Golden route.
