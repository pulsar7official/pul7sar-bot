# Phase 18 Change Set 062 — Replayable Golden GPU evidence verification

## Purpose

Change Set 061 made the first genuine Golden GPU proof tamper-evident by hashing the PNG, first-PNG result, and supporting receipts. Change Set 062 closes the remaining integrity gap: the generated evidence manifest can now be replayed and verified independently before artifact upload or after artifact download.

This is integrity verification only. It does **not** authorize publication, replace semantic verification, relax identity or sentiment requirements, or satisfy the Golden Visual quality floor.

## Added

### `verify_golden_evidence_manifest`

`engine/intelligence/golden_evidence_bundle.py` now exposes a deterministic verifier that:

- requires the exact `pul7sar-golden-gpu-evidence-v1` schema;
- requires `publication_ready=false`;
- requires non-empty job and request identities;
- requires a canonical 64-hex generation payload SHA-256;
- recomputes the canonical manifest SHA-256 with `manifest_sha256` excluded from the signed payload;
- rejects duplicate evidence paths;
- confines every evidence path to the repository root;
- replays file size and SHA-256 checks against current bytes;
- requires the recorded PNG to be part of the evidence file set;
- rechecks the PNG signature after all hash checks;
- returns a separate `pul7sar-golden-gpu-evidence-verification-v1` receipt with `publication_ready=false`.

The builder was also tightened to reject a first-PNG result that lacks job identity, request identity, or a canonical generation payload SHA-256.

### Verification command

New command:

```bash
PYTHONPATH=. python tools/phase18_verify_gpu_evidence_manifest.py \
  --manifest output/phase18_gpu_smoke/evidence-manifest.json \
  --receipt output/phase18_gpu_smoke/evidence-verification.json
```

The command writes a machine-readable verification receipt and exits nonzero on manifest drift, evidence byte drift, size drift, missing files, path escape, invalid PNG signature, or publication-gate mutation.

## Modified GPU workflow

`.github/workflows/phase18-gpu-smoke.yml` now performs:

`real PNG -> evidence manifest build -> evidence replay verification -> artifact upload`

The artifact is not uploaded as a successful proof path until the manifest has been replayed against the actual bytes present on the self-hosted GPU runner. The verification receipt is included under `output/phase18_gpu_smoke/**`.

The workflow remains:

- manual only;
- pinned to `phase18/story-intelligence`;
- self-hosted Linux/x64/CUDA/BF16 only;
- `$0-local` only;
- free of paid-provider secrets;
- unable to self-authorize publication.

## Tests

Regression coverage now includes:

- successful hash replay;
- preservation of `publication_ready=false`;
- rejection of noncanonical payload SHA-256;
- rejection of manifest metadata tampering;
- rejection of evidence byte/size tampering;
- independent repository-path confinement even if an attacker recomputes the outer manifest digest;
- GPU workflow ordering that requires evidence replay after manifest creation and before artifact upload.

## Production safety

No production file was modified. In particular:

- `main` was not modified;
- `main.py` was not modified;
- Telegram publishing was not modified;
- legacy image sourcing/rendering was not modified;
- no paid image provider or API was added;
- no secret was added;
- no model weights were committed;
- no fake PNG, fake GPU receipt, or fake performance sample was created;
- Fact Lock, identity, sentiment, semantic publication, and Golden Visual quality gates remain unchanged.

## Remaining blocker

A genuine Golden PNG still requires a compatible NVIDIA CUDA/BF16 execution host to run the locked FLUX.2 Klein handoff. Change Set 062 does not claim that execution happened. It ensures that when the first real result is produced, the entire evidence bundle can be independently replayed and proven byte-for-byte before semantic and visual review.
