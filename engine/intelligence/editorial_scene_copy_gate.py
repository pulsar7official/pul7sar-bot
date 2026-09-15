"""Copy-density gate for PUL7SAR sports editorial scenes."""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.sports_editorial_scene import SportsEditorialScenePlan


@dataclass(frozen=True)
class SceneCopyDecision:
    allowed: bool
    headline_words: int
    supporting_words: int
    failures: tuple[str, ...] = ()


class EditorialSceneCopyGate:
    """Prevent premium editorial visuals from collapsing into dense infographics."""

    @staticmethod
    def _count(value: str | None) -> int:
        if not value:
            return 0
        return len(tuple(token for token in value.strip().split() if token))

    def evaluate(
        self,
        scene: SportsEditorialScenePlan,
        *,
        headline: str,
        supporting_copy: str | None = None,
    ) -> SceneCopyDecision:
        if not isinstance(scene, SportsEditorialScenePlan):
            raise TypeError("scene must be SportsEditorialScenePlan")
        headline_words = self._count(headline)
        supporting_words = self._count(supporting_copy)
        failures: list[str] = []
        if headline_words == 0:
            failures.append("headline is empty")
        if headline_words > scene.headline_max_words:
            failures.append("headline exceeds scene word budget")
        if not scene.allow_supporting_copy and supporting_words:
            failures.append("supporting copy is forbidden for this scene family")
        if supporting_words > scene.supporting_copy_max_words:
            failures.append("supporting copy exceeds scene word budget")
        return SceneCopyDecision(not failures, headline_words, supporting_words, tuple(failures))

    def assert_allowed(self, scene: SportsEditorialScenePlan, *, headline: str, supporting_copy: str | None = None) -> None:
        decision = self.evaluate(scene, headline=headline, supporting_copy=supporting_copy)
        if not decision.allowed:
            raise ValueError("PUL7SAR_SCENE_COPY_REJECTED: " + "; ".join(decision.failures))
