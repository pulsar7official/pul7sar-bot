# PUL7SAR Phase 18 — Engineering Completion / Visual Validation Handoff

## Meaning of engineering completion

Phase 18 may be called **engineering-complete** only when the full Phase 18 CPU suite, Story Intelligence workflow, all Phase 18 visual-study workflows, Golden Editorial v6 build/verifier, completion audit and production-isolation checks pass on the same branch head.

Engineering completion is **not** a publication claim. Publication remains fail-closed until real multi-family PNGs pass owner visual review, final brand/typography assets are approved, verified-subject assets are publication-safe, target-runtime semantic inspection is proven on final candidates, and explicit final approval is given.

## Architecture frozen for validation

- GitHub/PUL7SAR is the orchestration and deterministic-composition source of truth.
- Colab/GPU is an optional engineering probe, not a daily production dependency.
- Generation and semantic QA are separated: a successful generated PNG is durably saved and displayed before Qwen can run.
- Golden-reference BF16 and explicit FP16 engineering-preview execution remain distinct precision tiers.
- Generated imagery may own atmosphere and non-identifying scene pixels only.
- Exact branding, readable editorial text, exact scores, exact club marks, verified identity, and story-required exact sport geometry remain deterministic or verified-asset owned.
- Publication readiness remains fail-closed at every stage.

## Canonical Candidate 1 rejection

The first real Golden Editorial v6 Candidate 1 proved that the local FLUX path can produce a coherent PNG, but it is **rejected** as a Golden visual.

The critical sports-geometry defect was an isolated partial goal frame appearing in an implausible physical relationship to the visible touchline/camera angle. The image may look photographically plausible at first glance, but the sport geometry is physically inconsistent.

This failure is now a canonical regression example, not an aesthetic preference.

## Sports geometry integrity policy

Contract: `exact_verified_or_visually_indeterminate`.

When exact sport geometry is not a verified story dependency:

- `partial_sport_geometry_allowed = false`;
- isolated/partial goal frames or nets are forbidden;
- penalty-area and goal-area lines are forbidden;
- corner arcs/flags are forbidden;
- centre circles/halfway lines and tactical/regulation markings are forbidden;
- regulation geometry must remain outside frame, fully occluded or visually indeterminate;
- an impossible goal-to-touchline/endline relationship is both a sport-geometry failure and a severe visual defect;
- `partial_sport_geometry_hallucination_is_hard_failure = true`;
- `broken_sport_surface_geometry` is a hard blocker and cannot be rescued by a high aesthetic score.

The rule is propagated through Golden handoff construction, prompt compaction, provider constraint translation, local backend handoff metadata, candidate batch manifests, pre-GPU verification, Colab runtime admission, Qwen semantic inspection and human review instructions.

## Validation phase after engineering completion

Do not tune by random seed hunting. Validate by story family and repair causes instead of cherry-picking outputs.

Required real visual validation families:

1. **General Editorial / Preview atmosphere** — no required real person or exact pitch geometry.
2. **Result Statement** — exact score and club identities deterministic; losing side remains neutral and respected.
3. **Transfer / Verified Subject** — verified subject asset path; no fabricated signing state.
4. **Tactical Intelligence** — exact deterministic football geometry, positions and arrows; generative pixels cannot own tactical truth.
5. **Data / Record Visual** — exact numbers deterministic; generated imagery cannot invent statistics or records.
6. **Event / Match Context** — geometry only when editorial semantics require it; composition remains story-first.

For every family validate factual integrity, identity integrity, sport geometry, focal hierarchy, protected text/brand zones, platform crop strength, semantic QA, provenance and publication blocking.

## External/owner gates intentionally left open

These are not missing engineering features and must not be faked by code:

- owner acceptance of real multi-family visual quality;
- final owner-approved PUL7SAR publication brand master;
- approved brand and editorial typography assets;
- publication-safe verified real-subject assets/rights evidence;
- final target-runtime semantic-inspector evidence on real candidates;
- explicit final publication approval.

Until those gates close, `publication_ready` remains false and the Phase 18 draft branch must not be merged into production merely because engineering tests are green.
