import tempfile
import unittest
from pathlib import Path

from engine.intelligence.data_monument_composition import DataMonumentComposer
from engine.intelligence.data_monument_study_renderer import DataMonumentRow, DataMonumentStudyRenderer
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform


class DataMonumentStudyRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.composition = DataMonumentComposer().plan(self.profile)
        self.font = next((p for p in (
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        ) if p.is_file()), None)
        if self.font is None:
            self.skipTest('DejaVu font unavailable')
        self.rows = (
            DataMonumentRow(1, 'NORTH CITY', '76 PTS', True),
            DataMonumentRow(2, 'ROYAL ATHLETIC', '72 PTS'),
            DataMonumentRow(3, 'UNITED SPORTING', '69 PTS'),
            DataMonumentRow(4, 'OLYMPIA FC', '64 PTS'),
        )

    def _render(self, output: Path):
        return DataMonumentStudyRenderer().render(
            self.composition,
            profile=self.profile,
            output_path=str(output),
            headline='TITLE RACE',
            context='AFTER 30 MATCHES',
            rows=self.rows,
            accent_hex='#C71925',
            font_path=str(self.font),
            seed_key='data-monument-regression',
        )

    def test_renderer_keeps_exact_values_and_avoids_spreadsheet_or_stadium(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = self._render(Path(tmp) / 'data.png')
            self.assertEqual(receipt.contract, 'pul7sar-data-monument-study-renderer-v1-premium')
            self.assertTrue(receipt.exact_values_code_owned)
            self.assertFalse(receipt.spreadsheet_grid_used)
            self.assertFalse(receipt.stadium_used)
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.network_used)
            self.assertTrue(receipt.study_only)
            self.assertFalse(receipt.publication_ready)
            self.assertEqual(receipt.row_count, 4)
            self.assertEqual(receipt.dominant_value, '76 PTS')
            self.assertLess(receipt.brand_width, 870)

    def test_same_input_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / 'a.png'
            b = Path(tmp) / 'b.png'
            first = self._render(a)
            second = self._render(b)
            self.assertEqual(first.output_sha256, second.output_sha256)
            self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_dense_row_count_is_rejected(self):
        rows = tuple(DataMonumentRow(i + 1, f'TEAM {i}', f'{80-i} PTS') for i in range(6))
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, '1..5'):
                DataMonumentStudyRenderer().render(
                    self.composition,
                    profile=self.profile,
                    output_path=str(Path(tmp) / 'data.png'),
                    headline='TITLE RACE',
                    context='AFTER 30 MATCHES',
                    rows=rows,
                    accent_hex='#C71925',
                    font_path=str(self.font),
                )


if __name__ == '__main__':
    unittest.main()
