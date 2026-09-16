# PUL7SAR Phase 18 — Change Set 108

## Receipt-backed Hybrid Geometry Evidence

### Scope
Branch: `phase18/story-intelligence` only. Production `main` is not modified.

### Problem closed
`HybridVisualQualityGate` now requires an auditable `DeterministicGeometryReceipt` whenever the layer plan requires deterministic sport geometry. The preceding builder still emitted only `deterministic_geometry_applied=true` after validating a `FootballHybridCompositionReceipt`, so the real Golden Hybrid v5 path could correctly render and validate football geometry yet still reach the quality gate without the compact receipt that the gate now requires.

### Added behavior
`HybridVisualEvidenceBuilder` now converts a **hash-valid, texture-preserving** `FootballHybridCompositionReceipt` into a provider-neutral `DeterministicGeometryReceipt` only after `HybridArtifactIntegrityGate` succeeds.

The emitted receipt records:
- renderer contract: `football_pitch_projective_v1`;
- integrity status: `REGULATION_FOOTBALL_GEOMETRY_READY`;
- exact hybrid output path;
- camera preset and canvas;
- texture-preserving composition mode;
- source-texture preservation flag;
- surface normalization opacity and inward feather;
- final hybrid output SHA-256.

If the football artifact is missing, tampered, legacy opaque, outside the current texture-preserving contract, or otherwise fails the integrity replay, the builder emits **neither** a geometry-complete boolean **nor** a geometry receipt.

### Why this matters for the first genuine Golden Visual
The real Candidate 1 path already uses `HybridVisualEvidenceBuilder` before `HybridVisualQualityGate`. This change makes the gate consume evidence derived from the actual deterministic football artifact rather than a standalone boolean claim. It closes a mismatch introduced by the recent gate hardening and prevents a future GPU result from being blocked merely because the receipt bridge was absent.

### Tests
`tests/test_phase18_hybrid_evidence_builder.py` now verifies that:
- a genuine texture-preserving football composition produces both `deterministic_geometry_applied=true` and a valid receipt;
- the receipt carries the approved renderer ID, integrity status, output path and output SHA;
- legacy/opaque or otherwise invalid football receipts produce no geometry receipt;
- byte tampering after composition invalidates both the boolean and the compact receipt;
- non-geometry inspection evidence remains preserved.

### Invariants preserved
No changes were made to:
- Fact Lock;
- identity verification;
- sentiment or result neutrality;
- `$0-local` policy;
- FLUX.2 Klein 4B, BF16, seeds, canvases or generation controls;
- Base Scene semantic/layer ownership;
- Qwen publication-grade semantic requirements;
- SemanticPublicationGate;
- Golden visual thresholds (8.5 minimum / 9.0+ elite);
- exact PUL7SAR brand/logo/typography integrity requirements.

No paid provider, secret, model weight, font file, fake PNG, fabricated benchmark or fabricated review score is introduced.

### Remaining blocker
A new Golden Hybrid v5 Candidate 1 still requires a compatible CUDA/BF16 host. No GPU result is claimed by this change set.
