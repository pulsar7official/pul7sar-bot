# Phase 18 Change Set 311 — Closed-World Final Publication Authority

## Purpose

CS311 hardens the final CS286 publication-readiness receipt without changing the successful canonical output shape or broadening any authority.

The audit after CS310 confirmed that CS286 already re-verifies the exact CS285 materialization, re-opens the exact source and Genuine Golden PNG bytes, validates PNG structure/dimensions, checks byte identity, checks the CS285 receipt SHA, and re-derives the duplicated story/generation/quality/approval state before granting `publication_ready=true`.

The remaining gap was envelope malleability: a caller could add an unknown top-level field or an unknown policy key, recompute `receipt_sha256`, and the former verifier would still accept the receipt because it validated required fields but did not reject unrecognized ones. At the final publication authority boundary this could create semantic ambiguity for downstream consumers.

## Change

`engine/intelligence/qwen_image_genuine_golden_publication_readiness.py` now defines:

- `PUBLICATION_POLICY`: the exact canonical final-readiness policy.
- `PUBLICATION_RECEIPT_FIELDS`: the exact closed-world set of accepted CS286 receipt keys.
- `_require_exact_publication_envelope()`: rejects missing or extra top-level fields and requires exact policy equality.

The builder uses the same canonical policy object, and the verifier invokes the closed-world envelope check after validating schema/status/receipt digest and before consuming any publication authority.

## Security / authority effect

CS311 is fail-closed. It does not:

- generate, edit, decode/re-encode, or publish image bytes;
- relax factual/freshness or entity/identity requirements;
- relax sentiment neutrality or loser-respect rules;
- relax `$0-local`, offline, or local-files-only generation requirements;
- bypass Generated-Layer, Composition, Golden Quality, Human Review, Brand/Typography, Final Composed, Final Semantic, or `SemanticPublicationGate` approvals;
- allow CS286 to publish anything as a side effect.

It only removes ambiguity from the final signed readiness envelope.

## Canonical compatibility

The successful receipt produced by the CS286 builder has the same schema identifier and the same intended field/value shape as before. Previously valid canonical receipts remain canonical. Receipts that relied on undeclared extra fields or policy keys are now rejected by design.

## Regression coverage

The CS286 test suite now covers:

- exact closed-world envelope acceptance;
- rejection of an unknown top-level authority field;
- rejection of a missing canonical field;
- rejection of an unknown policy authority key;
- rejection of a weakened canonical policy value;
- existing CS285 authority and repository-bound output checks.

## Golden Visual status

CS311 does not fabricate a Genuine Golden Visual. Real materialization still requires the genuine upstream Qwen candidate and all visual/semantic gates to succeed. If the available runtime has no compatible CUDA/BF16 execution path, the project remains correctly blocked before genuine inference.
