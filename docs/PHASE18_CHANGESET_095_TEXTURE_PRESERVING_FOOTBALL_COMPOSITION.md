# PUL7SAR Phase 18 — Change Set 095

## Texture-preserving deterministic football composition

### Problem observed in the genuine engineering proof
The previous deterministic football compositor proved regulation geometry by painting an opaque flat-green polygon over the generated stadium. The result was technically measurable but visually unacceptable: it looked like a tactical-board graphic pasted over a photographic scene and destroyed the underlying turf texture, lighting and environmental integration.

This change does **not** change FLUX.2 Klein 4B or weaken the pre-composition semantic layer gate. The existing Hybrid v5 rule remains: the base scene must first prove that model-generated exact football geometry is absent. Only after that proof may deterministic geometry be added.

### Added behavior
- `FootballHybridComposer` now uses `texture_preserving_pitch_overlay_v1`.
- The photographic base remains visible through the pitch region.
- A conservative green surface-normalisation tint is composited at alpha 54 instead of replacing the pitch at alpha 255.
- Deterministic mowing-band tint remains subtle (alpha 24).
- Regulation lines, circles, penalty areas, marks and arcs remain deterministic and are still projected through the existing camera-aware geometry system.
- The compositor rejects attempts to restore the old opaque tactical-board surface through its public API.

### Receipt / integrity changes
`FootballHybridCompositionReceipt` now records:
- `composition_mode=texture_preserving_pitch_overlay_v1`
- `source_texture_preserved=true`
- the actual surface normalisation opacity.

`HybridArtifactIntegrityGate` now requires the texture-preserving mode, requires source texture preservation, rejects surface opacity outside 24..96, and still replays input/output SHA-256 evidence. Deterministic geometry remains required.

The compatibility field `generated_pitch_markings_replaced` is retained for existing receipt consumers. Under Hybrid v5 its meaning is that final visible exact markings are owned by deterministic code after the base semantic gate has proved model-generated exact sport geometry absent; it does not authorize generative pitch markings.

### Tests
Updated/expanded:
- `tests/test_phase18_football_hybrid_composer.py`
  - real PNG + new receipt contract
  - source turf pixel variation survives composition
  - opacity 255 is rejected at the compositor API boundary
- `tests/test_phase18_hybrid_artifact_integrity.py`
  - valid current receipt
  - tamper rejection
  - legacy opaque surface rejection
  - non-texture-preserving receipt rejection
- `tests/test_phase18_hybrid_evidence_builder.py`
  - deterministic geometry requires a hash-valid current texture-preserving receipt
  - legacy opaque/unproven receipt cannot satisfy geometry completion

### Unchanged safety and quality gates
- `main` / `main.py`: untouched.
- Fact Lock: unchanged.
- Identity verification: unchanged.
- Sentiment / neutrality: unchanged.
- `$0-local`: unchanged.
- FLUX.2 Klein 4B, BF16, seeds and canvases: unchanged.
- Base-scene semantic layer gate remains mandatory for the quality path.
- SemanticPublicationGate: unchanged and mandatory for publication.
- Golden visual thresholds remain 8.5 minimum / 9.0+ elite with hard blockers overriding numeric scores.
- Exact PUL7SAR logo integrity remains unresolved and therefore final publication composition remains blocked.

### Remaining gap
A genuine latest-architecture Candidate 1 still requires a compatible CUDA/BF16 host. The next real GPU run should produce only Candidate 1 and visually verify that the deterministic football geometry now reads as part of the photographed stadium rather than as an opaque graphic overlay. If Qwen semantic QA is unavailable, only engineering review is permitted and `publication_ready` must remain false.
