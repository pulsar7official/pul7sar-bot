# Phase 18 Implementation Log — CS479

## Scope

CS479 advances `phase18/story-intelligence` toward the first genuine Golden Visual PNG without touching `main` and without weakening factual, identity, sentiment, zero-cost, semantic-publication, provenance, Human Review, or visual-quality gates.

Starting branch HEAD reviewed before changes:

`e514e87cbef5e435eba5654e70b2389154c4d286`

The CS478 baseline was verified terminal-green in both Phase 18 Story Intelligence Verification and CPU Verification Diagnostics before CS479 work began.

## Gap identified

The existing Candidate 1 PNG structural verifier correctly proves PNG framing, CRCs, zlib termination, decoded scanline geometry, legal PNG filter bytes, non-interlaced raster layout, terminal IEND, and absence of trailing bytes. Its generic PNG parser intentionally accepts several standards-valid pixel formats.

The actual PUL7SAR platform normalization contract is narrower: `PillowPlatformCanvasNormalizer` explicitly converts the final normalized image to Pillow `RGB` and then saves it as PNG. Therefore a structurally valid palette, grayscale, RGBA, 16-bit, or interlaced PNG is not the canonical normalized artifact produced by that path even if it is a valid PNG file.

CS479 converts this existing production behavior into a standalone fail-closed verification contract before changing the critical Golden workflow.

## Added

### `tools/phase18_verify_first_genuine_golden_png_canonical_encoding.py`

New CPU-safe, stdlib-only verifier for the already-verified Candidate 1 structure report.

It requires:

- structure schema/status for the current first-Golden PNG structural verifier;
- branch `phase18/story-intelligence`;
- Candidate 1;
- `$0-local` and offline-only evidence;
- valid source commit SHA and PNG SHA-256;
- positive PNG byte count and dimensions;
- all upstream structural proof flags to remain true;
- exact canonical platform encoding:
  - PNG bit depth `8`;
  - PNG colour type `2` (truecolour RGB);
  - `3` channels;
  - `24` bits per pixel;
  - interlace method `0`;
- all sensitive authorities remain false.

On success it emits `pul7sar-phase18-first-genuine-golden-png-canonical-encoding-v1` with `canonical_platform_encoding_verified=true` while keeping Human Review, Golden-quality, publication, generation, network-download, and Seeds 2–4 authority closed.

### `tests/test_phase18_first_golden_png_canonical_encoding.py`

Regression coverage includes:

- successful RGB8/non-interlaced verification;
- RGBA rejection;
- 16-bit RGB rejection;
- interlaced rejection;
- incomplete upstream structural-proof rejection;
- publication-authority drift rejection;
- regression assertion that `PillowPlatformCanvasNormalizer` still performs `image.convert("RGB")` and saves PNG.

## Modified

None in CS479.

## Deleted

None in CS479.

## Critical-path activation status

The new canonical-encoding verifier is intentionally **not yet inserted into** `.github/workflows/phase18-first-genuine-golden-v6-fresh.yml` in CS479.

Reason: it is a new fail-closed contract. The safe sequencing is to land the CPU-safe verifier and its tests first, allow repository CI to validate it, and only then place it in the immutable Golden execution chain and bind its evidence into the Human Review bundle. This avoids making the GPU-critical path depend on code that has not yet passed the repository's own CPU verification.

No existing Golden gate was bypassed or weakened by keeping activation staged.

## Preserved gates and authorities

CS479 does not modify or relax:

- factual/source-consensus validation;
- entity/identity validation;
- sentiment and loser-respect policy;
- `SemanticPublicationGate`;
- approved Qwen2.5-VL and FLUX.2 model identities/revisions;
- `$0-local` / offline-only / no-download requirements;
- network guard and review-bundle evidence binding;
- CUDA, native BF16, VRAM/RAM/cache/filesystem requirements;
- generation/runtime/model snapshot provenance and replay;
- Candidate 1 freshness/source/runner/PNG-byte binding;
- PNG structural integrity gate;
- Human Visual Review requirement;
- Golden-quality threshold/approval;
- publication authority;
- Seeds 2–4 authority.

No paid API, network download path, CPU generation fallback, FP16 Golden fallback, FP32 Golden fallback, or fabricated GPU result was introduced.

## GPU status

No genuine Golden PNG was generated in CS479. The current execution context does not provide the compatible self-hosted NVIDIA/CUDA runtime required by the protected workflow. A real Candidate 1 still requires the approved local snapshots plus CUDA-enabled PyTorch, a real compatible CUDA device, native BF16, and sufficient live VRAM/RAM/cache/filesystem headroom under the existing `$0-local` offline contract.

## Remaining gap after CS479

After CS479 is confirmed green, the next safe step is to activate the canonical-encoding verifier in the first-Golden workflow immediately after the structural PNG gate, then cryptographically bind/replay that evidence in the exact Human Review bundle before upload. The genuine Golden PNG itself remains blocked until a compatible protected NVIDIA runner executes the already-fail-closed generation path.
