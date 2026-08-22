# PUL7SAR — Future Social & Video Intelligence Architecture

Status: **Future architecture / not production-wired**

This document captures approved future direction without changing current production behavior.

## Non-negotiable principle

Creative freedom is broad, but no optimization, automation, cost constraint, or publishing shortcut may reduce factual, visual, identity, editorial, or technical quality.

If quality gates fail, PUL7SAR must reject/retry/hold the content rather than publish degraded output.

## 1. Headless Core / PUL7SAR Studio

The intelligence and visual engines should remain headless and callable through an API.

Future clients may include:
- PUL7SAR Web Studio / Control Center
- mobile application
- Telegram publishing adapter
- Facebook / Instagram publishing adapter
- X / Threads adapter
- TikTok / YouTube workflows

A future Studio should support:
`Write/Paste Story -> Analyze -> Generate -> Preview -> Approve -> Publish`

The UI is a client, not the owner of Story Intelligence or Visual Intelligence.

## 2. Credentials and account security

Never store Facebook, Instagram, YouTube, TikTok, or other account passwords in source code, repository files, prompts, logs, or generated artifacts.

Preferred integration:
- official OAuth / platform authorization
- scoped access tokens
- token rotation / expiry handling
- GitHub Secrets or runtime environment secrets where appropriate
- least privilege
- no secret values in committed configuration

PUL7SAR should not require a human password to be embedded in application code.

## 3. Social Intelligence / source discovery

Social sources may complement MAIN sources when they provide faster public developments.

Pipeline concept:
`MAIN Sources + Approved Social Sources -> Normalize -> Story Candidate -> Semantic Dedup -> Fact/Identity Verification -> Story Intelligence`

Social-source ingestion must not bypass existing Fact Lock, Identity Gate, neutrality, or publication quality controls.

## 4. Semantic deduplication and Story Memory

Duplicate detection must operate on story meaning rather than raw text similarity alone.

A Story Fingerprint should model signals such as:
- entities
- sport / competition
- event type
- event status
- clubs / players / organizations
- normalized factual claims
- event time window
- source provenance

Examples of paraphrases that may represent one story:
- club approaches player
- talks advance
- negotiations progress

A material state change must become a `STORY_UPDATE`, not be discarded as a duplicate.

Example:
`approach -> talks advanced -> agreement -> official signing`

Story Memory should preserve the timeline so future weekly/monthly/seasonal content can be assembled without rediscovering every fact.

## 5. Video Intelligence

TikTok and YouTube require native content strategy, not recycled still-image posts.

Future Video Intelligence should build editorial timelines and reusable concepts such as:
- Goals of the Round
- Moments of the Round
- Tactical Turning Points
- Most Impactful Substitutions
- Player / Coach / Team of the Round
- Derby / Major Match Story
- Player / Coach / Team of the Month
- Winter Champion / halfway-stage leader
- Golden Boot / assists race
- title winners / end-of-season awards
- tennis Match Story / Road to the Final / champion story
- equivalent formats for other sports

The Video Director should turn approved facts/events into:
`Hook -> Build-up -> Key Moments -> Payoff -> PUL7SAR Ending`

## 6. Motion identity

PUL7SAR video should have recognizable motion language:
- 7/pulse animation
- restrained premium transitions
- score / stat motion
- lower thirds
- brand lighting
- typography rhythm
- sound design
- platform-specific pacing

The objective is recognizable PUL7SAR identity even before the viewer reads the logo.

## 7. Rights and provenance

Discovery of a third-party video does not grant reuse rights.

Video material must carry rights/provenance state before automated editing or publishing.

Examples of eligible sources may include:
- PUL7SAR-owned footage
- explicitly licensed material
- material with verified reuse permission
- platform/API content whose terms authorize the intended use
- original motion graphics and visualizations produced by PUL7SAR

Unverified third-party broadcast footage must not silently become an editable/publishable asset.

A future Rights & Provenance Gate should block unauthorized material before Video Director / editing stages.

## 8. Zero-cost development rule

Current development should remain zero-cost.

Paid providers/services may be represented architecturally for future extension, but current execution must prefer verified zero-cost/local/free-tier-without-payment-method options.

Zero-cost mode may never lower quality thresholds. If no zero-cost option meets quality requirements, the outcome is hold/retry/no acceptable output — not degraded publication.

## 9. Future architecture

`Source Connectors`
`        |`
`        v`
`Social Listening + MAIN Ingestion`
`        |`
`        v`
`Story Normalization / Semantic Dedup / Story Memory`
`        |`
`        v`
`Fact + Identity + Rights/Provenance Gates`
`        |`
`        v`
`Story Intelligence`
`     /        \\`
`Visual Engine  Video Intelligence`
`     |             |`
`Quality Gates   Video Quality/Rights Gates`
`     \\             /`
`      PUL7SAR Studio / Publishing Adapters`

## 10. Implementation order

Do not interrupt the current Phase 18 visual-quality foundation.

Recommended future order:
1. complete original-scene provider adapter and quality-first candidate flow
2. produce first $0 end-to-end visual
3. stabilize PUL7SAR Studio API contract
4. semantic Story Memory / dedup foundation
5. approved social-source connectors
6. rights/provenance contracts
7. Video Intelligence / Motion Identity
8. publishing adapters and later mobile application
