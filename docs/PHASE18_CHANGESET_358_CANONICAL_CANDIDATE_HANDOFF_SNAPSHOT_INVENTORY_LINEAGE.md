# Phase 18 Changeset 358 — Canonical Candidate Handoff Snapshot Inventory Lineage

## Purpose

CS358 extends the sealed canonical-candidate handoff so the exact CS357 Qwen snapshot-byte inventory is carried as first-class evidence into downstream QA. This does not grant approval. It prevents later semantic/composition/visual/Golden stages from seeing a genuine candidate handoff whose compact model-byte lineage is weaker than the attestation that produced it.

## Production change

`engine/intelligence/qwen_image_canonical_candidate_handoff.py` now:

- requires `snapshot_byte_inventory_verified=true` on the replay-verified CS357 launch-to-output attestation;
- validates the attested snapshot inventory digest, file count, total byte count, and model revision;
- requires the inventory revision to equal the attested approved model revision;
- seals the compact inventory evidence into the handoff digest;
- replays CS357 during handoff verification and requires the sealed inventory evidence to equal the freshly replayed attestation evidence;
- fails closed on missing inventory authority, invalid inventory shape, revision drift, or receipt drift.

## Gate preservation

CS358 does not alter factual/freshness, Entity/Identity, sentiment/loser-respect, semantic, visual-quality, Golden-quality, Human Visual Review, Brand/Typography, Final Composed, Final Semantic, SemanticPublicationGate, Genuine Golden materialization, or publication-readiness logic.

It does not download models, permit network model fallback, introduce paid execution, fabricate inference, create a Golden PNG, publish content, or grant publication authority.

## Regression coverage

`tests/test_phase18_qwen_image_canonical_candidate_handoff.py` now verifies that:

- valid CS357 snapshot inventory evidence is sealed into the handoff;
- the handoff refuses an attestation without explicit snapshot-byte-inventory verification;
- inventory evidence tampering is rejected even when an attacker recomputes the outer handoff digest;
- existing exact-source byte drift and authority-tampering protections remain intact.

## Resulting execution lineage

The intended genuine execution chain is now:

`inventory-bound launch -> preload inventory replay -> canonical child inventory replay -> pre-load inventory -> from_pretrained(local-only BF16) -> post-load inventory -> genuine Qwen PNG -> CS357 postflight inventory replay -> CS358 sealed candidate handoff with identical inventory evidence -> downstream factual/identity/sentiment/semantic/visual/Golden gates`.
