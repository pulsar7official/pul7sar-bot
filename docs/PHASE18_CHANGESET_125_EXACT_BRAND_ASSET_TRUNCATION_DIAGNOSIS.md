# PUL7SAR Phase 18 — Change Set 125

## Exact Embedded Brand Asset Truncation Diagnosis

Change Set 125 records the exact root cause of the embedded reference-brand CI blocker and makes that failure explicit and fail-closed.

## Root cause proven by CI

GitHub Actions run `32742612700` / run 1855 showed that the repository-carried file:

`assets/brand/pul7sar_reference_master_v1.zip.b64`

contains a literal text marker at character index 10000:

`[...ELLIPSIZATION...]`

The diagnostic evidence was:

- encoded length: `20021`
- invalid character count: `8`
- first invalid character: `[` at index `10000`
- permissively decoded SHA-256: `6d52edb21cccad78545f54a0be3d129e22721a43ab4b5deb1e8a3c1ee60e451a`
- expected approved bundle SHA-256 remains: `49ed35398dbb3a62460ff4ee52b7eea7b0db295b165271cef1126484d3d15d62`

This proves that the text asset is not merely affected by whitespace or a harmless separator. Actual Base64 source characters were removed and replaced by an ellipsization marker. The approved binary archive therefore cannot be reconstructed safely from the current repository text alone.

## Code hardening

### `engine/intelligence/brand_embedded_master.py`

Added explicit detection of known truncation markers before Base64 decoding.

A literal ellipsization marker now fails with:

`PUL7SAR_EMBEDDED_BRAND_TRANSPORT_TRUNCATED`

before permissive Base64 fallback is considered.

Permissive decoding remains available only for non-destructive separator noise and still cannot authorize any bytes unless the decoded archive reproduces the existing pinned bundle SHA-256 and all member SHA-256 values.

This prevents a truncated asset from being misclassified as recoverable transport noise.

### `tests/test_phase18_brand_embedded_master.py`

Added regression coverage proving that a literal ellipsization marker is rejected fail-closed.

## Recovery policy

The corrupted study asset must not be "fixed" by:

- accepting the corrupted decoded SHA;
- changing the expected bundle SHA to the corrupted bytes;
- generating substitute masks or texture and pretending they are the original bundle;
- bypassing the embedded-brand integrity test;
- promoting an approximate study asset into a publication master.

Safe recovery requires one of:

1. restoring the exact original Base64/ZIP bytes from a verified historical source or artifact that reproduces the pinned bundle and member SHA values; or
2. deliberately replacing the study bundle through a new separately reviewed asset contract, with explicit provenance and without claiming continuity with the original SHA-locked bundle.

The first option is preferred.

## Relation to Golden Visual progress

This blocker is in a study-only reference-brand artifact and does not justify weakening the Golden Hybrid generation, semantic, or publication gates. The first genuine FLUX Candidate 1 remains separately blocked by unavailable compatible CUDA/BF16 execution in the current environment.
