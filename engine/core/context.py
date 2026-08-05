"""Immutable rendering request state.

Defined by 04_RENDERING_SPECIFICATION.md, Section 6 (RenderContext).

RenderContext is created exactly once, by the Pipeline. Every rendering
subsystem receives the same instance. No subsystem may modify it.
RenderContext contains data only; it never contains rendering logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.config.configuration import ResolvedConfiguration
    from engine.core.canvas_info import CanvasInfo
    from engine.core.locale_info import LocaleInfo
    from engine.core.payload import ValidatedPayload
    from engine.core.render_metadata import RenderMetadata
    from engine.resources.assets import ResolvedAssets
    from engine.resources.fonts import ResolvedFonts


@dataclass(frozen=True, slots=True)
class RenderContext:
    """One immutable rendering request.

    Every field is resolved before RenderContext is created; no field
    is computed or mutated afterward.

    Attributes:
        render_id: Unique identifier for this render.
        payload: The validated rendering request payload.
        configuration: The resolved configuration for this render.
        assets: The resolved assets (images, badges, overlays, etc.)
            required for this render.
        fonts: The resolved fonts required for this render.
        metadata: Render metadata (e.g. timestamps, source info).
        platform_targets: The platforms this render is destined for.
        canvas_info: Information describing the target canvas.
        locale_info: Locale information for this render.
    """

    render_id: str
    payload: "ValidatedPayload"
    configuration: "ResolvedConfiguration"
    assets: "ResolvedAssets"
    fonts: "ResolvedFonts"
    metadata: "RenderMetadata"
    platform_targets: tuple[str, ...]
    canvas_info: "CanvasInfo"
    locale_info: "LocaleInfo"
