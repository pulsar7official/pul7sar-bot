"""Dynamic story -> visual concept competition for PUL7SAR Phase 18.

This layer is deterministic and renderer-agnostic. It does not pretend to be an
LLM. It consumes already-extracted/verified story fields, routes the story to an
editorial event, then synthesizes multiple materially different concepts from
story-specific facts. A future reasoning model may propose candidates, but must
still satisfy this contract and its safety/diversity checks.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping, Any

from engine.intelligence.models import StoryBrief
from engine.intelligence.story_analyzer import StoryAnalyzer
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_brain import VisualConceptCandidate, VisualConceptCompetition


_STORY_TYPE_TO_EVENT: dict[str, EditorialEvent] = {
    "result": EditorialEvent.RESULT,
    "match_result": EditorialEvent.RESULT,
    "live": EditorialEvent.LIVE_MOMENT,
    "live_moment": EditorialEvent.LIVE_MOMENT,
    "preview": EditorialEvent.PREVIEW,
    "match_preview": EditorialEvent.PREVIEW,
    "transfer": EditorialEvent.TRANSFER_CONFIRMED,
    "transfer_confirmed": EditorialEvent.TRANSFER_CONFIRMED,
    "transfer_rumour": EditorialEvent.TRANSFER_RUMOUR,
    "transfer_rumor": EditorialEvent.TRANSFER_RUMOUR,
    "contract": EditorialEvent.CONTRACT,
    "renewal": EditorialEvent.CONTRACT,
    "injury": EditorialEvent.INJURY,
    "comeback": EditorialEvent.COMEBACK,
    "suspension": EditorialEvent.SUSPENSION,
    "retirement": EditorialEvent.RETIREMENT,
    "appointment": EditorialEvent.APPOINTMENT,
    "dismissal": EditorialEvent.DISMISSAL,
    "statement": EditorialEvent.STATEMENT,
    "record": EditorialEvent.RECORD,
    "award": EditorialEvent.AWARD,
    "trophy": EditorialEvent.TROPHY,
    "draw": EditorialEvent.DRAW,
    "table": EditorialEvent.TABLE,
    "tactics": EditorialEvent.TACTICS,
    "officiating": EditorialEvent.OFFICIATING,
    "controversy": EditorialEvent.CONTROVERSY,
    "financial": EditorialEvent.FINANCIAL,
    "organization": EditorialEvent.ORGANIZATION,
    "schedule": EditorialEvent.SCHEDULE,
    "qualification": EditorialEvent.QUALIFICATION,
    "elimination": EditorialEvent.ELIMINATION,
    "general": EditorialEvent.GENERAL,
}


@dataclass(frozen=True)
class DynamicVisualBrainPlan:
    story: StoryBrief
    event: EditorialEvent
    concepts: tuple[VisualConceptCandidate, ...]
    story_fingerprint: str
    contract: str = "pul7sar-dynamic-visual-brain-v1"
    publication_ready: bool = False


class DynamicVisualBrain:
    """Create story-specific concept competition from explicit story facts."""

    CONTRACT = "pul7sar-dynamic-visual-brain-v1"

    _COMMON_FORBIDDEN = (
        "readable generated text, pseudo-text, numerals, logos or watermarks",
        "fabricated club crest or competition logo",
        "fabricated real-person identity",
        "specific real venue identity without verified reference",
        "collage, split-screen, grid or image-within-image",
        "generic one-template layout",
    )

    def plan(self, article: Mapping[str, Any]) -> DynamicVisualBrainPlan:
        story = StoryAnalyzer().analyze(article)
        event = self._event(story)
        concepts = self._concepts(story, event)
        VisualConceptCompetition.assert_diverse(concepts)
        fingerprint = sha256(
            (story.headline + "\n" + story.summary + "\n" + event.value + "\n" + (story.primary_entity or "")).encode("utf-8")
        ).hexdigest()
        return DynamicVisualBrainPlan(story, event, concepts, fingerprint)

    @staticmethod
    def _event(story: StoryBrief) -> EditorialEvent:
        raw = (story.story_type or "general").strip().casefold().replace("-", "_").replace(" ", "_")
        return _STORY_TYPE_TO_EVENT.get(raw, EditorialEvent.GENERAL)

    def _concepts(self, story: StoryBrief, event: EditorialEvent) -> tuple[VisualConceptCandidate, ...]:
        subject = story.primary_entity or "the verified story subject"
        secondary = story.secondary_entities[0] if story.secondary_entities else "the relevant counterpart"
        core = story.summary.strip() or story.headline
        if event in {EditorialEvent.TRANSFER_CONFIRMED, EditorialEvent.TRANSFER_RUMOUR, EditorialEvent.CONTRACT}:
            return self._transfer(subject, secondary, core, event)
        if event in {EditorialEvent.RESULT, EditorialEvent.LIVE_MOMENT}:
            return self._result(subject, secondary, core)
        if event in {EditorialEvent.INJURY, EditorialEvent.SUSPENSION, EditorialEvent.STATEMENT, EditorialEvent.CONTROVERSY, EditorialEvent.OFFICIATING, EditorialEvent.DISMISSAL, EditorialEvent.APPOINTMENT, EditorialEvent.RETIREMENT, EditorialEvent.COMEBACK}:
            return self._subject_news(subject, core, event)
        if event is EditorialEvent.TACTICS:
            return self._tactics(subject, core)
        if event in {EditorialEvent.RECORD, EditorialEvent.AWARD, EditorialEvent.TROPHY, EditorialEvent.DRAW, EditorialEvent.TABLE, EditorialEvent.FINANCIAL, EditorialEvent.SCHEDULE, EditorialEvent.QUALIFICATION, EditorialEvent.ELIMINATION}:
            return self._data_or_achievement(subject, core, event)
        return self._event_editorial(subject, core, event)

    def _candidate(self, *, cid: str, title: str, metaphor: str, prompt: str, camera: str, focal: str, negative: str, signature: tuple[str, ...], forbidden: tuple[str, ...], score: float) -> VisualConceptCandidate:
        return VisualConceptCandidate(
            concept_id=cid, title=title, editorial_metaphor=metaphor, scene_prompt=prompt,
            camera_language=camera, focal_strategy=focal, negative_space_strategy=negative,
            signature_elements=signature,
            forbidden_elements=tuple(dict.fromkeys((*self._COMMON_FORBIDDEN, *forbidden))),
            preflight_score=score,
            metadata={"dynamic": True, "provider_agnostic": True, "publication_ready": False},
        )

    def _transfer(self, subject: str, secondary: str, core: str, event: EditorialEvent) -> tuple[VisualConceptCandidate, ...]:
        rumour = event is EditorialEvent.TRANSFER_RUMOUR
        identity_rule = "Do not depict an identifiable person unless a verified identity reference is supplied downstream."
        return (
            self._candidate(cid="dynamic-transfer-threshold", title="New Threshold", metaphor="a career move expressed as crossing into a new chapter", prompt=f"Editorial transfer concept for {subject}; story fact: {core}. Build an original architectural threshold of light and destination-color atmosphere, without literal signing-room clichés. {identity_rule}", camera="ground-level oblique editorial perspective", focal="luminous threshold/destination cue", negative="quiet architectural plane", signature=("threshold", "destination light", "forward motion"), forbidden=("airport stock-photo cliché", "holding scarf cliché", "fabricated contract text", "football pitch"), score=.90),
            self._candidate(cid="dynamic-transfer-two-worlds", title="Between Two Worlds", metaphor="the transfer is tension between origin and destination", prompt=f"Premium sports editorial scene about {subject} and {secondary}; story fact: {core}. Use one continuous scene with two materially distinct environmental light zones connected by a single transition path; no split-screen. {identity_rule}", camera="compressed cinematic environmental perspective", focal="transition between contrasting light environments", negative="soft shadow beside transition", signature=("dual light worlds", "transition path", "destination pull"), forbidden=("split-screen", "versus poster", "fabricated club marks", "football pitch"), score=.88 if rumour else .92),
            self._candidate(cid="dynamic-transfer-object", title="The Empty Place", metaphor="arrival is implied by a prepared place awaiting its new occupant", prompt=f"Story-specific transfer still-life inspired by {subject}; story fact: {core}. Create one premium non-branded destination-space detail prepared for arrival, using material, light and restrained club-color cues only; no readable nameplate or kit text.", camera="intimate 50mm editorial still-life", focal="one prepared destination object/space", negative="dark surrounding material field", signature=("prepared place", "material detail", "arrival anticipation"), forbidden=("jersey name", "contract document text", "generic football on grass", "football pitch"), score=.87),
        )

    def _result(self, subject: str, secondary: str, core: str) -> tuple[VisualConceptCandidate, ...]:
        neutral = "Respect the losing side; no humiliation, collapse caricature, shame or mockery. Exact score and crests are deterministic later layers."
        return (
            self._candidate(cid="dynamic-result-afterglow", title="After the Final Whistle", metaphor="the outcome is felt through the atmosphere left behind", prompt=f"Original post-match atmosphere for {subject} versus {secondary}; verified story fact: {core}. Use crowd light, haze and restrained aftermath energy without readable scoreboard or exact result. {neutral}", camera="cinematic sideline-adjacent environmental view without regulation geometry", focal="one decisive atmospheric light/crowd gesture", negative="calm dark zone for later exact score", signature=("afterglow", "crowd energy", "outcome tension"), forbidden=("scoreboard", "visible score", "humiliated loser", "partial goal geometry"), score=.93),
            self._candidate(cid="dynamic-result-balance", title="Weight of the Result", metaphor="victory has visual weight without degrading the opponent", prompt=f"Premium abstract-photographic result world for {subject}; fact: {core}. Build one physical scene with asymmetric light/material weight suggesting the verified outcome, leaving exact score and identities for deterministic composition. {neutral}", camera="controlled studio-environment hybrid", focal="dominant but respectful material/light mass", negative="counterbalanced quiet field", signature=("visual weight", "balanced opposition", "result tension"), forbidden=("winner crushing loser symbolism", "broken rival crest", "readable text"), score=.90),
            self._candidate(cid="dynamic-result-crowd-pulse", title="The Roar Remains", metaphor="the result lives in collective energy rather than a literal scoreboard", prompt=f"Sports-culture editorial image after {core}. Anonymous crowd texture and directional practical light carry the emotional outcome; no identifiable person, exact score, text or club marks. {neutral}", camera="compressed 70mm crowd-environment view", focal="single wave of crowd/light energy", negative="dark atmospheric falloff", signature=("crowd wave", "directional light", "post-match air"), forbidden=("scoreboard", "celebrity likeness", "mocking supporters", "visible regulation pitch"), score=.88),
        )

    def _subject_news(self, subject: str, core: str, event: EditorialEvent) -> tuple[VisualConceptCandidate, ...]:
        safe = "Do not invent facial expression, injury evidence, body posture or real-person likeness. Verified subject assets, if available, are separate deterministic/reference inputs."
        tone = "serious" if event in {EditorialEvent.INJURY, EditorialEvent.SUSPENSION, EditorialEvent.CONTROVERSY, EditorialEvent.OFFICIATING, EditorialEvent.DISMISSAL} else "restrained"
        return (
            self._candidate(cid="dynamic-subject-presence", title="Presence Without Fabrication", metaphor="the person-led story is represented through verified presence boundaries", prompt=f"{tone.title()} editorial environment for a story about {subject}: {core}. Build identity-neutral environmental storytelling with a clear reserved subject zone for a later verified asset. {safe}", camera="portrait-oriented environmental composition", focal="reserved subject presence zone shaped by light", negative="quiet factual-copy field", signature=("subject zone", "restrained light", "documentary depth"), forbidden=("generated face", "fabricated injury staging", "medical fantasy"), score=.94),
            self._candidate(cid="dynamic-subject-evidence", title="The Detail That Matters", metaphor="one verified consequence/detail carries the story without inventing a face", prompt=f"Editorial evidence-detail concept for {core}. Use one non-identifying, story-authorized symbolic/material detail and controlled depth; avoid sensationalism and avoid implying facts not present in the story. {safe}", camera="close 85mm documentary-detail language", focal="single factual-detail placeholder", negative="soft surrounding falloff", signature=("evidence detail", "controlled depth", "serious restraint"), forbidden=("blood", "fabricated medical equipment", "generated identity"), score=.90),
            self._candidate(cid="dynamic-subject-absence", title="The Absence", metaphor="the subject's absence or change is communicated by space rather than a fabricated portrait", prompt=f"High-end editorial scene responding to {subject}: {core}. Express change/absence through one deliberately empty, non-identifying sports-adjacent space or object, with no readable labels and no person depiction. {safe}", camera="quiet wide-normal editorial framing", focal="one conspicuously empty place", negative="integrated shadow/architecture", signature=("empty place", "absence", "restrained atmosphere"), forbidden=("empty hospital bed cliché", "generic sad silhouette", "football pitch"), score=.86),
        )

    def _tactics(self, subject: str, core: str) -> tuple[VisualConceptCandidate, ...]:
        return (
            self._candidate(cid="dynamic-tactics-spatial", title="Space Is the Story", metaphor="tactical relationships are the visual hero", prompt=f"Tactical editorial base for {subject}: {core}. Keep generated pixels atmospheric and minimal; exact pitch geometry, positions, arrows and labels must be deterministic code-owned layers added later.", camera="orthographic-inspired technical composition without generated field lines", focal="reserved deterministic tactical map zone", negative="clean technical margins", signature=("spatial hierarchy", "technical restraint", "data-ready surface"), forbidden=("generated pitch markings", "invented formation", "decorative player portrait"), score=.96),
            self._candidate(cid="dynamic-tactics-lanes", title="Pressure Lanes", metaphor="movement corridors become the composition", prompt=f"Abstract physical-light study inspired by the tactical idea in: {core}. Use directional light lanes and depth only as a non-factual background metaphor; all actual tactical arrows/positions remain deterministic later.", camera="high oblique abstract-environment view", focal="directional light lanes", negative="clean overlay-ready field", signature=("light lanes", "direction", "spacing"), forbidden=("generated arrows", "generated formation", "generated pitch"), score=.84),
            self._candidate(cid="dynamic-tactics-structure", title="Structure Before Names", metaphor="team structure is shown as order, not invented player identity", prompt=f"Premium technical-editorial base for {subject}; {core}. Use modular depth and disciplined spacing as atmosphere only, leaving every exact football datum to deterministic composition.", camera="clean frontal technical perspective", focal="modular structural rhythm", negative="information-safe margins", signature=("modular rhythm", "structure", "precision"), forbidden=("player likeness", "fake jersey numbers", "generated tactical labels"), score=.85),
        )

    def _data_or_achievement(self, subject: str, core: str, event: EditorialEvent) -> tuple[VisualConceptCandidate, ...]:
        return (
            self._candidate(cid="dynamic-data-monument", title="One Fact, Monumental", metaphor="the verified datum becomes the dominant object", prompt=f"Premium editorial base for {subject}: {core}. Reserve a dominant central/offset zone for one exact deterministic number, record, trophy fact or table datum; generated pixels supply only restrained material depth and light, never digits or text.", camera="monumental studio-editorial perspective", focal="empty deterministic datum anchor", negative="controlled surrounding depth", signature=("monument scale", "datum anchor", "material depth"), forbidden=("generated digits", "dense dashboard", "fake trophy inscription"), score=.95),
            self._candidate(cid="dynamic-data-trace", title="The Trace of the Achievement", metaphor="the fact is suggested through consequence while exact data stays code-owned", prompt=f"Story-specific achievement atmosphere for {core}. Build a restrained physical trace/path/light progression that supports one exact later data statement; no generated numbers, charts or text.", camera="diagonal editorial depth", focal="single progression/trace", negative="quiet data placement zone", signature=("progression trace", "achievement energy", "clean data zone"), forbidden=("generated chart", "generated numerals", "generic trophy room"), score=.87),
            self._candidate(cid="dynamic-data-object", title="The Object Behind the Fact", metaphor="one relevant physical object carries context while data remains exact later", prompt=f"High-end sports still-life context for {subject}: {core}. Use one non-branded, non-identifying physical object materially relevant to the event, with premium light and no readable markings; exact fact is added later.", camera="50mm premium still-life", focal="single contextual object", negative="dark material field", signature=("context object", "premium material", "fact-ready space"), forbidden=("readable engraving", "generated number", "brand imitation"), score=.84),
        )

    def _event_editorial(self, subject: str, core: str, event: EditorialEvent) -> tuple[VisualConceptCandidate, ...]:
        return (
            self._candidate(cid="dynamic-event-threshold", title="The Moment Before", metaphor="the event is expressed through anticipation and threshold", prompt=f"Original premium sports-editorial atmosphere for {subject}: {core}. Build a non-identifying threshold between shadow and event light; avoid literal stadium/pitch clichés and leave factual text for later composition.", camera="ground-level oblique environmental view", focal="event-light threshold", negative="integrated shadow plane", signature=("threshold", "event light", "anticipation"), forbidden=("football pitch", "goal", "scoreboard", "generic tunnel hero"), score=.91),
            self._candidate(cid="dynamic-event-architecture", title="Scale of the Event", metaphor="scale and anticipation replace literal icons", prompt=f"Architectural sports-culture editorial response to: {core}. Use generic non-identifying venue-scale structure, crowd-depth or light infrastructure without showing regulation playing geometry or signage.", camera="low oblique architectural 35mm", focal="one monumental structural/light cue", negative="natural roof/sky shadow", signature=("architecture", "scale", "atmospheric depth"), forbidden=("visible pitch", "goal frame", "readable signage", "generic centered stadium shot"), score=.88),
            self._candidate(cid="dynamic-event-human-trace", title="People Are Coming", metaphor="the event exists through anonymous human movement toward it", prompt=f"Premium event-context image inspired by {core}. Show only distant anonymous supporter-scale movement and practical light in a generic approach/concourse environment; no identifiable people, logos, pitch or readable text.", camera="compressed environmental street-to-venue perspective", focal="flow of anonymous movement into light", negative="quiet side architecture", signature=("human flow", "practical lights", "event pull"), forbidden=("fan portrait", "club scarf text", "visible pitch", "travel-photo blandness"), score=.86),
        )
