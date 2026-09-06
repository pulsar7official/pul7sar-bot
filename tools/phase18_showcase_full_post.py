#!/usr/bin/env python3
"""Compose a full PUL7SAR study post from a generated base scene.

This is a visual showcase tool for Phase 18. FLUX owns only the base image;
PUL7SAR deterministically owns the final canvas, brand master, typography,
headline hierarchy, metadata strip and social footer. The embedded checksum-
locked reference brand master is used directly, so no external logo upload is
required. The result remains study-only until the owner approves the final font
and publication master.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]

from engine.intelligence.brand_reference_renderer import BrandReferencePlacement, BrandReferenceRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform


def _font(size: int, *, bold: bool = False):
    from PIL import ImageFont
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def _cover(image, size: tuple[int, int]):
    from PIL import Image
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - target_w) // 2)
    top = max(0, (resized.height - target_h) // 2)
    return resized.crop((left, top, left + target_w, top + target_h))


def _draw_gradient(canvas, *, top: int, bottom: int, max_alpha: int):
    from PIL import Image, ImageDraw
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    span = max(1, bottom - top)
    for y in range(top, bottom):
        t = (y - top) / span
        alpha = round(max_alpha * (t ** 1.7))
        draw.line((0, y, canvas.width, y), fill=(3, 6, 13, alpha))
    canvas.alpha_composite(overlay)


def _fit_lines(draw, text: str, box_width: int, *, max_size: int, min_size: int, max_lines: int, bold: bool):
    words = " ".join(text.split()).split()
    for size in range(max_size, min_size - 1, -1):
        font = _font(size, bold=bold)
        lines: list[str] = []
        current = ""
        failed = False
        for word in words:
            candidate = word if not current else current + " " + word
            width = draw.textbbox((0, 0), candidate, font=font)[2]
            if width <= box_width:
                current = candidate
                continue
            if not current:
                failed = True
                break
            lines.append(current)
            current = word
            if len(lines) >= max_lines:
                failed = True
                break
        if not failed and current:
            lines.append(current)
        if not failed and len(lines) <= max_lines:
            return font, lines
    raise ValueError("text does not fit showcase typography box")


def compose(*, base: str, output: str, headline: str, subheadline: str, kicker: str, source: str, accent: str, handle: str) -> dict:
    from PIL import Image, ImageDraw

    profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    target_size = (profile.width, profile.height)
    base_path = Path(base)
    if not base_path.is_file():
        raise FileNotFoundError(base)

    with Image.open(base_path) as raw:
        canvas = _cover(raw.convert("RGB"), target_size).convert("RGBA")

    # Readability layer: preserve image in upper field while creating an editorial
    # information stage at the lower half, not a template rectangle.
    _draw_gradient(canvas, top=570, bottom=1350, max_alpha=238)
    top_shade = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    top_draw = ImageDraw.Draw(top_shade)
    for y in range(0, 300):
        alpha = round(95 * (1 - y / 300))
        top_draw.line((0, y, canvas.width, y), fill=(0, 0, 0, alpha))
    canvas.alpha_composite(top_shade)

    # Save intermediate then let the project-owned reference renderer place the
    # exact embedded PUL7SAR identity. Only the 7/pulse accent is tintable.
    stage = Path(output).with_suffix(".brand-stage.png")
    stage.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(stage, "PNG")
    BrandReferenceRenderer().render_on_file(
        base_path=str(stage),
        output_path=str(stage),
        placement=BrandReferencePlacement(x=72, y=74, width=315),
        accent_hex=accent,
        repository_root=ROOT,
    )

    with Image.open(stage) as branded:
        canvas = branded.convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # Kicker chip.
    kicker_font = _font(24, bold=True)
    kicker_text = "  " + kicker.upper() + "  "
    kb = draw.textbbox((0, 0), kicker_text, font=kicker_font)
    kw, kh = kb[2] - kb[0], kb[3] - kb[1]
    kx, ky = 72, 682
    accent_rgb = tuple(int(accent.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    draw.rounded_rectangle((kx, ky, kx + kw + 18, ky + kh + 18), radius=12, fill=(*accent_rgb, 235))
    draw.text((kx + 9, ky + 6), kicker_text, font=kicker_font, fill=(255, 255, 255, 255))

    # Headline.
    headline_font, headline_lines = _fit_lines(draw, headline.upper(), 900, max_size=76, min_size=48, max_lines=3, bold=True)
    y = 758
    for line in headline_lines:
        draw.text((72, y), line, font=headline_font, fill=(255, 255, 255, 255), stroke_width=1, stroke_fill=(0, 0, 0, 135))
        y += round(headline_font.size * 1.02)

    # Accent rule carries the story/team colour without recolouring the wordmark.
    y += 22
    draw.rounded_rectangle((72, y, 250, y + 8), radius=4, fill=(*accent_rgb, 255))
    y += 34

    sub_font, sub_lines = _fit_lines(draw, subheadline, 900, max_size=35, min_size=25, max_lines=3, bold=False)
    for line in sub_lines:
        draw.text((72, y), line, font=sub_font, fill=(225, 231, 239, 255))
        y += round(sub_font.size * 1.25)

    # Footer separation + source/handle.
    footer_y = 1232
    draw.line((72, footer_y, 1008, footer_y), fill=(255, 255, 255, 70), width=1)
    footer_font = _font(22, bold=True)
    draw.text((72, footer_y + 24), source.upper(), font=footer_font, fill=(184, 193, 207, 255))
    hb = draw.textbbox((0, 0), handle, font=footer_font)
    draw.text((1008 - (hb[2] - hb[0]), footer_y + 24), handle, font=footer_font, fill=(255, 255, 255, 230))

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(target, "PNG", optimize=True)
    stage.unlink(missing_ok=True)
    digest = sha256(target.read_bytes()).hexdigest()
    return {
        "status": "PUL7SAR_FULL_POST_SHOWCASE_GENERATED",
        "output": str(target.resolve()),
        "sha256": digest,
        "canvas": f"{profile.width}x{profile.height}",
        "platform": profile.platform.value,
        "brand_source": "embedded-reference-master",
        "brand_geometry_owned_by_pul7sar": True,
        "text_rendered_outside_image_model": True,
        "team_crest_used": False,
        "publication_ready": False,
        "study_only": True,
    }


def main() -> int:
    import json
    parser = argparse.ArgumentParser(description="Compose a full PUL7SAR study post")
    parser.add_argument("--base", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--headline", required=True)
    parser.add_argument("--subheadline", required=True)
    parser.add_argument("--kicker", default="TRANSFER • OFFICIAL")
    parser.add_argument("--source", default="SOURCE • OFFICIAL CLUB")
    parser.add_argument("--accent", default="#132257")
    parser.add_argument("--handle", default="@PUL7SAR")
    args = parser.parse_args()
    print(json.dumps(compose(
        base=args.base,
        output=args.output,
        headline=args.headline,
        subheadline=args.subheadline,
        kicker=args.kicker,
        source=args.source,
        accent=args.accent,
        handle=args.handle,
    ), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
