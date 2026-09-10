# Phase 18 Implementation Log 387 — CS305 Identity-Requirement Readiness Lineage

## Scope reviewed first

- Target repository: `pulsar7official/pul7sar-bot`.
- Write branch only: `phase18/story-intelligence`.
- Starting feature HEAD: `66b6981dbfa7e4fe32b328a7dd028174a53b12ed`.
- `main` was reviewed read-only at `982abb899b285ab147d0d315f7273a7b0dbccaf6`; no merge, rebase, reset, force-update, or file write was performed against `main`.
- The direct consumer reviewed after CS360 is `engine/intelligence/qwen_image_canonical_candidate_identity_requirement.py` (CS305 identity-requirement classification).

## Gap proven

CS360 already carries and fresh-replays the exact CS351 static CUDA/native-BF16 readiness binding. CS305 verifies CS360 and derives identity evidence from the candidate launch lineage, but its v2 receipt dropped the readiness binding before pixel-identity review classification. This was a provenance continuity gap, not a missing identity or publication authority.

## Modified

### `engine/intelligence/qwen_image_canonical_candidate_identity_requirement.py`

- schema `v2 -> v3`;
- added `_is_sha256()` and `_readiness_lineage()` validation;
- requires `static_readiness_receipt_verified=true` before candidate-lineage identity derivation;
- validates readiness repository-relative path, SHA-256, and positive byte size;
- carries `static_readiness_receipt` and `static_readiness_receipt_verified=true` into CS305;
- fresh verification of CS360 compares readiness path, SHA-256, and byte size exactly;
- keeps all premature authorities closed.

### `tests/test_phase18_qwen_image_canonical_candidate_identity_requirement.py`

- added positive readiness-lineage propagation coverage;
- added unverified-readiness rejection before identity-lineage derivation;
- added readiness SHA tamper rejection after recomputing outer `receipt_sha256`;
- retained existing identity-evidence byte-drift, candidate-byte, source-byte, lineage and no-independent-CS257-selector coverage.

## Added

- `docs/PHASE18_CHANGESET_387_CS305_IDENTITY_REQUIREMENT_READINESS_LINEAGE.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_387.md`

## Deleted

None.

## Dependencies

None added or changed.

## Test status

Pending repository CI after the exact code-and-test-bearing commit is created. Do not treat CS387 as terminal-green until `Phase 18 Story Intelligence Verification` completes with `success` on that exact SHA.

## Gate preservation

No factual/freshness, Entity/Identity, sentiment neutrality/loser-respect, `$0-local`, semantic QA, visual-quality, Human Visual Review, Golden Quality, Final Presentation/Brand/Typography, Final Composed, Final Semantic, SemanticPublicationGate, Genuine-Golden materialization, publication-readiness, or external-publication authority was bypassed or duplicated.

CS305 still only classifies whether pixel-identity review is required. It cannot create identity approval, final semantic approval, Human Review approval, Golden approval, `genuine_golden_png_created`, or `publication_ready`. It performs no Qwen-Image generation, pixel mutation, network fallback, paid execution, upload, or publication.

## Genuine Golden PNG status

No production Genuine Golden PNG is created or claimed by CS387. Compatible CUDA/GPU execution remains required for genuine Qwen-Image inference; the available execution environment for this run does not provide a usable NVIDIA CUDA device/runtime.
