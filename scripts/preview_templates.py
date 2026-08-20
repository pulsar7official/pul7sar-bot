from pathlib import Path

from PIL import Image, ImageDraw

from engine.bootstrap import create_engine


def _sample_image() -> Image.Image:
    width, height = 1600, 1000
    image = Image.new("RGB", (width, height), (16, 33, 52))
    draw = ImageDraw.Draw(image)

    for y in range(height):
        t = y / max(1, height - 1)
        draw.line(
            (0, y, width, y),
            fill=(int(15 + 10 * t), int(28 + 60 * t), int(55 + 20 * t)),
        )

    draw.rectangle((0, 620, width, height), fill=(24, 78, 55))
    return image


def _request(template: str, source: Image.Image) -> dict:
    return {
        "template": template,
        "platform": "telegram",
        "content": {
            "headline": "ريال مدريد يحسم صفقة جديدة في الساعات الأخيرة",
            "summary": "",
            "image": source,
        },
        "entity": {
            "key": "real_madrid",
            "kind": "club",
            "display_name": "Real Madrid",
        },
    }


def main() -> None:
    engine = create_engine()
    source = _sample_image()

    outputs = []
    for template_name in ("news", "breaking"):
        result = engine.execute(_request(template_name, source))
        path = Path(__file__).with_name(f"preview_{template_name}.jpg")
        path.write_bytes(result)
        outputs.append(path)

    for path in outputs:
        with Image.open(path) as image:
            print(
                f"{path.name}: {image.format} {image.size} {image.mode} "
                f"{path.stat().st_size} bytes"
            )

    if outputs[0].read_bytes() == outputs[1].read_bytes():
        raise RuntimeError("News and Breaking previews must differ")


if __name__ == "__main__":
    main()
