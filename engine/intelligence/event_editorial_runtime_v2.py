"""Event Editorial runtime v2: one context-aware light anchor, no duplicate pulse.

The v1 study anchor contained a red pulse-like waveform inside a perspective
portal. In practice this read as an unexplained second PUL7SAR pulse in the middle
of the image. V2 reserves pulse geometry exclusively for the PUL7SAR brand master
and uses a non-semantic light aperture for generic event energy instead.
"""
from __future__ import annotations

from PIL import Image, ImageDraw, ImageFilter

from engine.intelligence.event_editorial_study_renderer import (
    EventAnchorKind,
    EventEditorialStudyReceipt,
    EventEditorialStudyRenderer as _V1,
)


class EventEditorialStudyRenderer(_V1):
    """V2 art direction: cinematic aperture; never a second brand-like pulse."""

    @staticmethod
    def _draw_anchor(
        canvas: Image.Image,
        box: tuple[int, int, int, int],
        *,
        accent: tuple[int, int, int],
        kind: EventAnchorKind,
    ) -> None:
        x0, y0, x1, y1 = box
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0:
            raise ValueError("anchor box must be positive")

        # No literal card/panel. The anchor is made only from light and perspective
        # contours so it can merge into a photographic scene instead of sitting on it.
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer, "RGBA")
        cx = x0 + w // 2
        cy = y0 + h // 2

        # Soft volumetric aperture.
        glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow, "RGBA")
        rx = round(w * 0.33)
        ry = round(h * 0.27)
        gd.ellipse((cx-rx, cy-ry, cx+rx, cy+ry), fill=(*accent, 32))
        inner_rx = round(w * 0.18)
        inner_ry = round(h * 0.13)
        gd.ellipse((cx-inner_rx, cy-inner_ry, cx+inner_rx, cy+inner_ry), fill=(236, 244, 249, 19))
        glow = glow.filter(ImageFilter.GaussianBlur(max(24, round(w * 0.08))))
        canvas.alpha_composite(glow)

        # Two restrained perspective edges. They imply depth but do not form a
        # box, scoreboard, trophy, venue or factual object.
        top_y = y0 + round(h * 0.22)
        bottom_y = y1 - round(h * 0.16)
        top_half = round(w * (0.16 if kind is EventAnchorKind.GOVERNANCE else 0.20))
        bottom_half = round(w * 0.31)
        left_top = (cx-top_half, top_y)
        right_top = (cx+top_half, top_y)
        left_bottom = (cx-bottom_half, bottom_y)
        right_bottom = (cx+bottom_half, bottom_y)
        edge_alpha = 72 if kind is not EventAnchorKind.BROADCAST else 88
        draw.line((left_top, left_bottom), fill=(*accent, edge_alpha), width=max(1, round(w*0.0025)))
        draw.line((right_top, right_bottom), fill=(*accent, edge_alpha), width=max(1, round(w*0.0025)))

        # A neutral horizon shimmer replaces the old red waveform. Pulse topology
        # is intentionally forbidden outside the embedded PUL7SAR brand master.
        horizon_y = cy + round(h * 0.05)
        horizon_w = round(w * 0.29)
        draw.line(
            (cx-horizon_w, horizon_y, cx+horizon_w, horizon_y),
            fill=(226, 238, 246, 42),
            width=max(1, round(w * 0.002)),
        )

        # Event-kind variation is optical only: small light ticks, never iconography.
        tick_count = {
            EventAnchorKind.ANNOUNCEMENT: 3,
            EventAnchorKind.CALENDAR: 4,
            EventAnchorKind.GOVERNANCE: 2,
            EventAnchorKind.BROADCAST: 5,
            EventAnchorKind.GENERIC_EVENT: 3,
        }[kind]
        for i in range(tick_count):
            t = (i + 1) / (tick_count + 1)
            x = round((cx-horizon_w) * (1-t) + (cx+horizon_w) * t)
            tick = max(3, round(h * 0.012))
            draw.line((x, horizon_y-tick, x, horizon_y+tick), fill=(232, 241, 247, 31), width=1)

        layer = layer.filter(ImageFilter.GaussianBlur(0.35))
        canvas.alpha_composite(layer)


__all__ = ["EventAnchorKind", "EventEditorialStudyReceipt", "EventEditorialStudyRenderer"]
