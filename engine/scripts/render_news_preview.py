"""Generate a local Phase 14 preview through the real Visual Engine."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from engine.bootstrap import create_engine
from engine.integration.article_adapter import render_article_with_engine


def make_sample_image() -> Image.Image:
    width, height = 1600, 1000
    image = Image.new("RGB", (width, height), (16, 33, 52))
    draw = ImageDraw.Draw(image)

    # Synthetic sports-like pitch/stadium background. No remote assets.
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(15 + 10 * t)
        g = int(28 + 60 * t)
        b = int(55 + 20 * t)
        draw.line((0, y, width, y), fill=(r, g, b))

    draw.rectangle((0, 620, width, height), fill=(24, 78, 55))
    draw.line((0, 810, width, 810), fill=(220, 230, 230), width=5)
    draw.ellipse((600, 650, 1000, 970), outline=(220, 230, 230), width=5)

    # Stadium-light glow blocks.
    for x in (160, 1340):
        draw.ellipse((x - 90, 100, x + 90, 280), fill=(120, 175, 255))
        draw.ellipse((x - 45, 145, x + 45, 235), fill=(235, 245, 255))

    return image


def main() -> None:
    article = {
        "title": "ريال مدريد يحسم المواجهة بثلاثية ويواصل صدارة الدوري",
        "summary": "",
    }

    engine = create_engine()
    output = render_article_with_engine(
        article,
        engine=engine,
        selected_image=make_sample_image(),
    )

    output_path = Path(__file__).with_name("preview_news.jpg")
    output_path.write_bytes(output)

    with Image.open(output_path) as image:
        print("Preview:", output_path)
        print("Format:", image.format)
        print("Size:", image.size)
        print("Mode:", image.mode)
        print("Bytes:", output_path.stat().st_size)


if __name__ == "__main__":
    main()
