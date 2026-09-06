# PUL7SAR Phase 18 — Change Set 137

## First Golden Review Packet Integrity Seal

### Goal

Reduce the remaining operational gap after the first genuine Candidate 1 GPU run without weakening any factual, identity, sentiment, zero-cost, semantic or Golden visual-quality gate.

Change Set 136 could stage the exact provenance-bound Base PNG and semantically approved Hybrid PNG for human review. The packet already recorded image hashes, but the complete review state still depended on several separate receipts and the decision template remaining unchanged after staging.

### Added

- `engine/intelligence/first_golden_review_packet_integrity.py`
  - seals the Candidate 1 human-review packet to the exact bytes of:
    - first-PNG result receipt;
    - Hybrid handoff receipt;
    - Hybrid semantic continuation receipt;
    - human-review bundle receipt;
    - human-review decision template;
    - review Base PNG;
    - review Hybrid PNG;
  - records SHA-256 and byte size for each evidence file;
  - records the packet SHA-256;
  - calculates a canonical manifest SHA-256;
  - rejects repository path escape, duplicate evidence paths, invalid PNG signatures, review-image SHA drift, authority drift, Candidate drift, branch drift and cost-mode drift;
  - supports replay verification against current bytes.

- `tools/phase18_seal_first_golden_review_packet.py`
  - builds the integrity manifest and immediately replay-verifies it;
  - writes an independent verification receipt;
  - cannot approve the human review, Golden quality, Seeds 2-4, or publication.

- `tools/phase18_colab_first_golden_review_sealed.py`
  - preferred one-command staging entrypoint for the next compatible GPU/Colab session;
  - delegates generation, provenance, BASE_SCENE/HYBRID_SURFACE QA and review staging to the already qualified Change Set 136 wrapper;
  - then seals and replay-verifies the complete human-review packet;
  - stops before any human decision or Golden scoring.

- Regression tests:
  - `tests/test_phase18_first_golden_review_packet_integrity.py`;
  - `tests/test_phase18_colab_first_golden_review_sealed.py`.

### Modified

No existing generation, semantic, quality, publication or production runtime file was modified.

### Deleted

Nothing.

### Gates preserved

The new integrity layer cannot change or bypass:

- Fact Lock;
- entity/identity verification;
- sentiment and losing-side neutrality;
- `$0-local` / zero paid-provider policy;
- FLUX.2 Klein 4B and native BF16 locks;
- Candidate 1 / seed / canvas locks;
- generated readable text, PUL7SAR brand, score/number, entity-mark and exact-sport-geometry exclusions;
- Qwen BASE_SCENE and HYBRID_SURFACE inspection;
- deterministic football geometry ownership;
- Golden 8.5 minimum / 9.0+ elite thresholds;
- exact brand and typography integrity;
- SemanticPublicationGate.

The sealed wrapper explicitly keeps `human_visual_review_approved=false`, `golden_quality_approved=false`, `publication_ready=false`, and `seeds_2_to_4_authorized=false`.

### Preferred next GPU command

On a compatible CUDA/BF16 host, the preferred staging command becomes:

```bash
PYTHONPATH=. python tools/phase18_colab_first_golden_review_sealed.py
```

If Candidate 1 and both semantic stages succeed, the command returns only after the exact Base/Hybrid review packet has been SHA-sealed and replay-verified. Human acceptance remains a separate explicit step.
