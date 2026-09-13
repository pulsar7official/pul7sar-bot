# Phase 18 — Change Set 264: Canonical Candidate Semantic Base QA

## Purpose

Bind the exact CS263-admitted `canonical_candidate.png` bytes to the repository's existing semantic visual-verification stack before any Visual Critic, Human Review, Golden scoring, brand/typography composition, or semantic publication decision.

CS264 does not introduce a parallel visual-quality system. It reuses:

- `Qwen25VLSemanticInspector` with the immutable approved `Qwen/Qwen2.5-VL-3B-Instruct` revision;
- `SemanticInspectionStage.BASE_SCENE`;
- `SemanticVisualVerdictGate`;
- `SemanticLayerEvidenceAdapter`.

## Why this boundary exists

CS263 proves which candidate bytes came from the one-shot canonical inference path, but byte admission alone says nothing about what is visible in those pixels. The first post-generation semantic boundary therefore needs to inspect the exact admitted bytes and fail closed on generated text, platform branding, fake entity marks, exact numbers, illegal generated sport geometry, collage/split scenes, severe defects, weak subject framing, missing inspection fields, or confidence below the existing 0.85 floor.

## Byte and provenance binding

Before semantic inference CS264:

1. reruns `verify_canonical_candidate_byte_admission()`;
2. requires the upstream semantic/story/runtime/generation gates represented by CS263 to remain true;
3. requires all downstream Golden/semantic-human/publication authorities to remain false;
4. reopens the exact CS263 receipt and exact candidate PNG;
5. rechecks repository containment, symlink rejection, SHA-256, byte size, story SHA, and CS263 receipt digest.

The output receipt binds the exact CS263 receipt bytes, exact candidate PNG bytes, pinned semantic model id/revision, semantic verifier id, inspection stage, confidence floor, normalized verdict, and derived layer-leakage evidence.

## Existing semantic gates reused

`SemanticVisualVerdictGate` is invoked with:

- `identity_required=False` at this base-scene boundary;
- `geometry_alignment_required=False` because deterministic hybrid geometry has not yet been composed;
- `exact_numbers_absence_required=True`;
- `generated_sport_geometry_absence_required=True`;
- `minimum_confidence=0.85`.

`SemanticLayerEvidenceAdapter` is then required to produce complete evidence for text, platform brand, entity marks, exact numbers, and generated sport geometry. A missing or low-confidence check cannot become an implicit clean result.

## Identity boundary

CS264 deliberately does **not** claim identity approval. The current Qwen2.5-VL base-scene inspector returns no `identity_valid` evidence, while Phase 18 identity-sensitive subjects require verified-asset / identity-specific evidence. Therefore even a passing CS264 receipt contains:

- `identity_approved=false`;
- `semantic_approved=false`.

This prevents non-identity semantic inspection from silently replacing the dedicated Entity/Identity gate.

## Authority after CS264

A successful live semantic inspection may set only:

- `semantic_inspection_executed=true`;
- `semantic_base_scene_approved=true`.

It never sets:

- `genuine_golden_png_created=true`;
- `semantic_approved=true`;
- `human_visual_review_approved=true`;
- `golden_quality_approved=true`;
- `publication_ready=true`.

A rejected semantic inspection is also recorded as a byte-bound receipt with `semantic_base_scene_approved=false`; rejection is evidence, not a reason to erase provenance.

## Production CLI

`tools/phase18_run_canonical_candidate_semantic_base_qa.py` instantiates the real repository semantic inspector. No test double or caller-supplied verdict is accepted by that production entry point. The semantic model load/inference path remains fail-closed if its local dependencies or model execution are unavailable.

## What remains

After a genuine CS262 PNG exists and passes CS263/CS264, the next boundaries remain:

1. identity-specific evidence when the story requires a real identifiable subject;
2. full hybrid layer-ownership QA after deterministic/verified layers are composed;
3. byte-bound Visual Critic evidence;
4. Human Review;
5. Golden quality threshold (minimum 8.5, elite 9.0);
6. exact PUL7SAR brand/typography treatment;
7. SemanticPublicationGate.

CS264 is not a substitute for any of those gates.
