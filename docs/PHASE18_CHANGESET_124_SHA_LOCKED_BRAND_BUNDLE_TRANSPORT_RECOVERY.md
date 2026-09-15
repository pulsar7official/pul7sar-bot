# PUL7SAR Phase 18 — Change Set 124

## SHA-Locked Embedded Brand Bundle Transport Recovery

Change Set 124 repairs a CI blocker discovered while validating Change Set 123 without weakening brand integrity.

## Failure observed

GitHub Actions run `32741891562` / run 1830 reached the full discover-based Phase 18 suite and ran 857 tests. The new Change Set 123 semantic-first PNG tests passed, but two existing embedded-brand tests failed in `EmbeddedBrandMasterLoader` with:

`PUL7SAR_EMBEDDED_BRAND_BASE64_INVALID`

The failure occurred at strict `base64.b64decode(..., validate=True)` for the large repository-carried one-line bundle `assets/brand/pul7sar_reference_master_v1.zip.b64`.

The asset blob itself was not changed by Change Set 123. Its repository blob SHA remained the same when compared with the earlier verified branch state. The failure was therefore treated as a textual transport/checkout robustness problem, not as permission to replace or silently trust a different brand binary.

## Integrity-preserving repair

### `engine/intelligence/brand_embedded_master.py`

Added `_decode_bundle_text()` with a two-stage decode policy:

1. strict Base64 decoding is attempted first;
2. only if strict decoding rejects textual transport characters, a permissive Base64 transport decode is attempted;
3. regardless of which textual decode path succeeds, the decoded ZIP must still match the existing immutable bundle SHA-256:

`49ed35398dbb3a62460ff4ee52b7eea7b0db295b165271cef1126484d3d15d62`

4. every ZIP member must still match its existing pinned SHA-256 before any layer is exposed.

This does **not** make arbitrary bundle content acceptable. Ignored textual separators can only survive if the resulting binary bytes are exactly the already approved archive. Any binary drift still fails closed at the unchanged bundle SHA lock, and any member drift still fails at the member SHA locks.

### `tests/test_phase18_brand_embedded_master.py`

Added regression coverage proving that textual transport noise can be recovered to the same bytes while the production bundle SHA remains unchanged and mandatory.

The existing full-bundle and separated-layer tests remain intact and continue to exercise the actual repository-carried asset.

## Preserved invariants

Unchanged:

- bundle SHA-256;
- member SHA-256 values;
- source-reference SHA binding;
- study-only status of this reference-derived master;
- `publication_ready=false`;
- exact-brand publication approval requirements;
- Fact Lock, identity, sentiment/neutrality, zero-cost, semantic and Golden-quality gates;
- FLUX.2 Klein 4B and BF16;
- `main` and production behavior.

No new brand asset was substituted. No checksum was relaxed. No publication authority was granted.
