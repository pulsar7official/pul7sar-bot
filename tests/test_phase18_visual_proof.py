import base64
import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.local_generation_provenance import LocalGenerationProvenance
from engine.intelligence.visual_proof import VisualProofArtifactWriter


# Valid 1x1 PNG used only to test artifact registration, never as a generated visual.
_ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Z1JkAAAAASUVORK5CYII="
)


class VisualProofArtifactTests(unittest.TestCase):
    def provenance(self, width=1, height=1):
        return LocalGenerationProvenance(
            provider_id="local-test",
            model_id="model-test",
            backend="diffusers",
            seed=712345,
            request_id="proof-001",
            width=width,
            height=height,
        )

    def test_real_png_is_registered_with_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "real.png"
            source.write_bytes(_ONE_PIXEL_PNG)
            out = Path(temp) / "proof"
            artifact = VisualProofArtifactWriter(str(out)).register(
                png_path=str(source),
                provenance=self.provenance(),
            )
            self.assertTrue(Path(artifact.png_path).exists())
            data = json.loads(Path(artifact.metadata_path).read_text(encoding="utf-8"))
            self.assertEqual(data["seed"], 712345)
            self.assertEqual(data["cost_mode"], "$0-local")
            self.assertTrue(data["visual_proof"])

    def test_missing_png_is_never_fabricated(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                VisualProofArtifactWriter(str(Path(temp) / "proof")).register(
                    png_path=str(Path(temp) / "missing.png"),
                    provenance=self.provenance(),
                )
            self.assertFalse((Path(temp) / "proof").exists())

    def test_dimension_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "real.png"
            source.write_bytes(_ONE_PIXEL_PNG)
            with self.assertRaisesRegex(ValueError, "dimensions"):
                VisualProofArtifactWriter(str(Path(temp) / "proof")).register(
                    png_path=str(source),
                    provenance=self.provenance(width=1080, height=1350),
                )


if __name__ == "__main__":
    unittest.main()
