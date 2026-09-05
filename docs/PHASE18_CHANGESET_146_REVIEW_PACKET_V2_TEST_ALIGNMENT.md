# PUL7SAR Phase 18 — Change Set 146

## Review Packet v2 Regression Alignment

### Why this change was needed

Change Set 145 correctly upgraded the first-Golden review packet integrity contract to `pul7sar-first-golden-human-review-packet-v2` and made the measured Original Scene runtime-admission receipt a mandatory SHA-bound evidence file. The production integrity code was correct, but one older regression fixture in `tests/test_phase18_first_golden_review_packet_integrity.py` still constructed the historical v1 packet with seven files.

GitHub Actions therefore failed before the rest of Phase 18 validation could continue. The failure was explicit and fail-closed:

`FIRST_GOLDEN_REVIEW_INTEGRITY_PACKET_CONTRACT_MISMATCH`

The fix updates the test evidence to the current production contract rather than weakening the runtime gate.

### Modified

- `tests/test_phase18_first_golden_review_packet_integrity.py`
  - uses `pul7sar-first-golden-human-review-packet-v2`;
  - adds `original_scene_runtime_admission` as the eighth mandatory evidence file;
  - records and validates `original_scene_runtime_admission_sha256`;
  - updates the expected sealed evidence count from seven to eight;
  - asserts that the manifest and verification payload report the Original Scene admission as bound;
  - adds regression coverage proving that post-seal tampering of the Original Scene admission is detected.

### Added

- `docs/PHASE18_CHANGESET_146_REVIEW_PACKET_V2_TEST_ALIGNMENT.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_146.md`

### Deleted

Nothing.

### Security / quality posture

No production gate was weakened. In particular, this change does not modify Fact Lock, Identity Verification, Sentiment/Neutrality, `$0-local`, FLUX.2 Klein 4B, native BF16, Qwen BASE_SCENE/HYBRID_SURFACE inspection, deterministic football geometry, generation provenance replay, Golden 8.5/9.0 thresholds, Exact Brand/Typography Integrity, SemanticPublicationGate, or Publication Readiness.

The Original Scene runtime-admission receipt remains mandatory and SHA-bound before the sealed Golden review stage can be trusted.
