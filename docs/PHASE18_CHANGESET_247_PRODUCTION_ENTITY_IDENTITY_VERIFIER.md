# Phase 18 Change Set 247 — Production Entity / Identity Verifier

## Purpose

Change Set 247 implements the fourth genuine production-backed semantic replay adapter required before the atomic six-gate registry cutover: `entity_identity_verification`.

The implementation deliberately does **not** promote `engine/entities/normalizer.py` into an identity verifier. Normalization is reused only as a deterministic helper. Identity verification remains a separate fail-closed policy that requires source-backed canonical entities, unique alias ownership, exact story-reference resolution, and approved non-generated exact entity assets.

## Added production policy

`engine/intelligence/entity_identity_verification.py`

The policy requires:

- exact story SHA binding;
- a non-empty canonical entity set;
- stable canonical entity IDs;
- non-empty kind and display name;
- at least one explicit identity source reference per canonical entity;
- deterministic alias normalization;
- rejection of aliases that resolve to more than one canonical entity;
- every story-visible entity reference to resolve uniquely to its expected canonical entity;
- rejection of unknown/mismatched expected IDs;
- byte-bound exact-asset SHA-256 values;
- exact entity assets to use `origin == approved_exact_asset`;
- exact entity assets to be explicitly `generated == false` and approved for exact use.

This prevents a generated crest/logo/mark from satisfying identity verification merely because it resembles the intended entity.

## Added replay adapter

`engine/intelligence/qwen_image_entity_identity_gate_verifier.py`

The adapter exposes Change Set 241 production provenance metadata and binds `PUL7SAR_SOURCE_CALLABLE_OBJECT` directly to `verify_entity_identity_evidence(...)` in the production semantic policy module, so readiness binds the source bytes containing the actual identity semantics rather than only a wrapper.

## Added regression coverage

`tests/test_phase18_qwen_image_entity_identity_gate_verifier.py`

Coverage includes:

- successful source-backed unique bilingual alias resolution;
- alias collision rejection;
- expected-entity mismatch rejection;
- missing identity-source rejection;
- generated exact-entity-asset rejection;
- unapproved exact-asset origin rejection;
- cross-story evidence rejection;
- verifier identity drift rejection;
- production source-object provenance binding.

## Authority boundary

Change Set 247 does not modify the canonical six-gate registry. Partial registration remains forbidden. Passing this gate alone grants none of the following:

- production semantic replay completion;
- fresh-story-gate completion;
- canonical generation authorization;
- model loading or inference;
- canonical pixel reuse;
- semantic approval;
- visual-quality or Golden approval;
- human approval;
- publication readiness.

After this change set, four of six genuine adapters exist: Fact Lock, Entity/Identity, Sentiment/Neutrality, and Zero-cost. Story Semantic Preflight and Semantic/Layer Ownership remain required before atomic registry cutover.
