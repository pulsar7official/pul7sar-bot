import unittest
from pathlib import Path

from PIL import ImageFont

from engine.visual.text_utils import (
    fit_headline,
    measure_rtl_text,
    render_rtl_line,
    wrap_logical_text,
)


FONT = Path("/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf")


@unittest.skipUnless(FONT.exists(), "NotoSansArabic-Bold.ttf unavailable")
class TestArabicTextUtils(unittest.TestCase):
    def test_arabic_numbers_and_score(self):
        font = ImageFont.truetype(str(FONT), 44)
        text = "برشلونة يفوز 3-1 ويتصدر جدول الترتيب"
        lines = wrap_logical_text(text, font, 900)
        self.assertTrue(lines)
        for line in lines:
            w, h = measure_rtl_text(line, font)
            self.assertGreater(w, 0)
            self.assertGreater(h, 0)
            rendered = render_rtl_line(line, font)
            self.assertEqual(rendered.mode, "RGBA")

    def test_long_headline_max_three_lines(self):
        text = (
            "ريال مدريد يحسم المواجهة بثلاثية ويواصل صدارة الدوري "
            "بعد مباراة قوية شهدت العديد من الفرص والأحداث المثيرة "
            "وسط حضور جماهيري كبير في المدرجات"
        )
        fitted = fit_headline(
            text,
            str(FONT),
            max_width=1152,
            max_height=230,
            max_lines=3,
        )
        self.assertLessEqual(len(fitted.logical_lines), 3)


if __name__ == "__main__":
    unittest.main()
