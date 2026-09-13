# PUL7SAR Phase 18 — Change Set 070: Exact Logo Integrity Gate

## Trigger
The v4 generation policy now forbids FLUX from inventing PUL7SAR branding, but deterministic post-composition still had one integrity gap: a PUL7SAR logo `asset_id` could pass the post-composition quality gate without a declared immutable checksum. That would allow a wrong local file to be substituted later while still using the expected symbolic asset ID.

## Changes

### `engine/intelligence/post_composition.py`
- Adds strict SHA-256 normalization for declared asset digests.
- The PUL7SAR logo now requires a valid 64-hex checksum in its approved asset metadata before final composition can pass.
- A matching runtime `AssetIntegrityRecord` is mandatory for the PUL7SAR logo bytes.
- Missing declared checksum, missing runtime integrity evidence, or checksum mismatch fails closed.
- Existing rules remain: exactly one PUL7SAR logo must be composited and the exact wordmark/logo may not be tinted.
- Other checksum-declared exact assets continue to use their existing integrity validation.

### `tests/test_phase18_post_composition.py`
Adds explicit regression coverage that:
- a checksum-verified exact logo passes;
- a symbolic logo asset without a declared SHA-256 is rejected;
- a declared logo without a runtime integrity record is rejected;
- a mismatched logo checksum is rejected;
- existing tint/platform/canvas rules remain enforced.

## Why this matters
The AI image generator is now responsible only for the clean base scene. The approved PUL7SAR logo must be a real deterministic asset, and the final composition gate can no longer accept the name `pul7sar-logo` as proof that the correct logo bytes were used.

## Safety
Unchanged: `main`, `main.py`, production publishing, factual/identity/sentiment locks, `$0-local`, model/dtype/seed/canvas locks, SemanticPublicationGate and Golden quality thresholds. No asset bytes, model weights, fonts or paid provider were added. No file was deleted.

## Remaining requirement
The approved production logo asset itself still needs to be resolved to an actual repository/runtime file with its locked SHA-256 before final PUL7SAR composition can become publication-ready. This change intentionally fails closed until that exact asset is available.
