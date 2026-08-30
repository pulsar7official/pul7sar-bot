# Phase 18 Change Set 265 — Canonical Candidate Identity Requirement

CS265 closes the gap between byte-bound semantic base-scene QA and person-identity QA.

It does **not** decide whether a generated face is the correct real person. Instead, it replays CS264, binds the exact upstream `entity_identity_verification` evidence from the CS257 fresh-story run, re-evaluates the deterministic entity-resolution policy, and classifies whether the candidate contains story identities that require a separate pixel-identity review.

For human kinds (`person`, `player`, `coach`, `manager`, `athlete`, `referee`, `official`) the receipt sets `pixel_identity_review_required=true` and records the exact canonical identity targets. It never sets `identity_approved=true`.

For non-human stories the requirement may be false, but CS265 still does not grant semantic, human-review, Golden, brand, typography, or publication authority.

The receipt is byte-bound to the exact identity evidence used by the fresh-story semantic chain. Later evidence drift invalidates verification.

This change remains CPU-only and zero-cost. It does not load Qwen Image, run image inference, inspect a face, or create a Golden PNG.
