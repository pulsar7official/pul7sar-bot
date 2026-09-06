"""Final composed-output contract and fail-closed export authorization."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from engine.intelligence.assets import AssetBundle
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.post_composition import PostCompositionPlan, PostCompositionQualityGate
from engine.intelligence.typography import TextLayout, TextStyle, DeterministicTypographyEngine


@dataclass(frozen=True)
class FinalComposedOutput:
    platform: str
    canvas: str
    base_scene_reference: str
    composed_asset_reference: str
    text_layouts: tuple[TextLayout, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("platform", "canvas", "base_scene_reference", "composed_asset_reference"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        object.__setattr__(self, "text_layouts", tuple(self.text_layouts))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class ExportAuthorization:
    allowed: bool
    failures: tuple[str, ...] = ()
    token: str | None = None

    def __post_init__(self) -> None:
        if self.allowed and (not isinstance(self.token, str) or not self.token.strip()):
            raise ValueError("allowed export requires a non-empty token")
        if not self.allowed and self.token is not None:
            raise ValueError("denied export may not carry a token")
        object.__setattr__(self, "failures", tuple(self.failures))


class FinalExportGate:
    """Last Phase 18 gate before a platform file may be exported/published."""

    def __init__(
        self,
        *,
        composition_gate: PostCompositionQualityGate | None = None,
        typography_engine: DeterministicTypographyEngine | None = None,
    ) -> None:
        self._composition_gate = composition_gate or PostCompositionQualityGate()
        self._typography_engine = typography_engine or DeterministicTypographyEngine()

    def authorize(
        self,
        package: GenerationPackage,
        assets: AssetBundle,
        plan: PostCompositionPlan,
        output: FinalComposedOutput,
        *,
        approved_styles: Mapping[str, TextStyle],
    ) -> ExportAuthorization:
        failures: list[str] = []
        composition = self._composition_gate.evaluate(package, assets, plan)
        failures.extend(composition.failures)

        if output.platform != package.platform:
            failures.append("final output platform mismatch")
        if output.canvas != package.canvas:
            failures.append("final output canvas mismatch")
        if not output.base_scene_reference.strip():
            failures.append("missing base scene reference")
        if not output.composed_asset_reference.strip():
            failures.append("missing composed asset reference")

        seen_roles: set[str] = set()
        for layout in output.text_layouts:
            role = layout.role.value
            if role in seen_roles:
                failures.append(f"duplicate text layout role: {role}")
                continue
            seen_roles.add(role)
            style = approved_styles.get(role)
            if style is None:
                failures.append(f"missing approved text style: {role}")
                continue
            decision = self._typography_engine.validate(layout, style)
            failures.extend(f"{role}: {failure}" for failure in decision.failures)

            expected_box = package.layout_boxes.get(role)
            if expected_box is None:
                failures.append(f"text layout has no approved package box: {role}")
            else:
                actual = layout.box
                if (
                    actual.x != expected_box["x"]
                    or actual.y != expected_box["y"]
                    or actual.width != expected_box["width"]
                    or actual.height != expected_box["height"]
                ):
                    failures.append(f"text geometry mismatch: {role}")

        planned_text_roles = {
            element.role.value
            for element in plan.elements
            if element.text is not None
        }
        if planned_text_roles != seen_roles:
            missing = sorted(planned_text_roles - seen_roles)
            unexpected = sorted(seen_roles - planned_text_roles)
            if missing:
                failures.append("missing rendered text roles: " + ", ".join(missing))
            if unexpected:
                failures.append("unexpected rendered text roles: " + ", ".join(unexpected))

        if failures:
            return ExportAuthorization(False, tuple(dict.fromkeys(failures)))

        token = f"export:{package.platform}:{package.canvas}:{output.composed_asset_reference}"
        return ExportAuthorization(True, (), token)

    @staticmethod
    def assert_authorized(authorization: ExportAuthorization) -> None:
        if not isinstance(authorization, ExportAuthorization):
            raise TypeError("authorization must be ExportAuthorization")
        if not authorization.allowed or not authorization.token:
            raise ValueError("final export is not authorized")
