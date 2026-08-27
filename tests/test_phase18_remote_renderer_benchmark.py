from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "phase18_remote_renderer_compare.py"
PROMPT = ROOT / "benchmarks" / "phase18" / "savinho_transfer_renderer_benchmark_prompt.txt"


def _load_tool():
    spec = importlib.util.spec_from_file_location("phase18_remote_renderer_compare", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load remote renderer benchmark tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RemoteRendererBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = _load_tool()

    def test_benchmark_prompt_is_identity_neutral_and_platform_name_free(self) -> None:
        prompt = PROMPT.read_text(encoding="utf-8")
        validated = self.tool._validate_prompt(prompt)
        self.assertTrue(validated)
        upper = validated.upper()
        self.assertNotIn("PUL7SAR", upper)
        self.assertNotIn("PULSAR", upper)
        self.assertIn("identity must remain non-recognizable", validated.lower())
        self.assertIn("one continuous physical scene only", validated.lower())

    def test_platform_name_leak_fails_closed(self) -> None:
        safe = PROMPT.read_text(encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "REMOTE_RENDERER_PLATFORM_NAME_LEAK"):
            self.tool._validate_prompt(safe + " Later add PUL7SAR branding.")

    def test_missing_safety_marker_fails_closed(self) -> None:
        safe = PROMPT.read_text(encoding="utf-8")
        self.assertIn("no sponsor mark", safe.lower())
        broken = safe.replace("no sponsor mark", "avoid commercial marks", 1)
        self.assertNotEqual(broken, safe)
        self.assertNotIn("no sponsor mark", broken.lower())
        with self.assertRaisesRegex(ValueError, "REMOTE_RENDERER_SAFETY_MARKER_MISSING"):
            self.tool._validate_prompt(broken)

    def test_png_copy_produces_sha_bound_artifact_evidence(self) -> None:
        png_bytes = b"\x89PNG\r\n\x1a\n" + b"phase18-test-payload"
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.png"
            target = Path(tmp) / "target.png"
            source.write_bytes(png_bytes)
            evidence = self.tool._copy_result(str(source), target)
            self.assertEqual(evidence["output_bytes"], len(png_bytes))
            self.assertEqual(len(evidence["output_sha256"]), 64)
            self.assertEqual(target.read_bytes(), png_bytes)

    def test_non_png_remote_result_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source.bin"
            target = Path(tmp) / "target.png"
            source.write_bytes(b"not-a-png")
            with self.assertRaisesRegex(RuntimeError, "REMOTE_RENDERER_OUTPUT_NOT_PNG"):
                self.tool._copy_result(str(source), target)

    def test_report_can_never_claim_canonical_golden_or_publication_authority(self) -> None:
        report = self.tool._report(
            renderer="test-renderer",
            space="test/space",
            output_evidence={"output": "/tmp/x.png", "output_sha256": "a" * 64, "output_bytes": 8},
            seed=7,
            prompt_sha256="b" * 64,
            elapsed_seconds=1.0,
        )
        self.assertEqual(report["cost_mode"], "$0-remote-zerogpu-study")
        self.assertTrue(report["engineering_benchmark_only"])
        self.assertFalse(report["canonical_golden_eligible"])
        self.assertFalse(report["semantic_approved"])
        self.assertFalse(report["golden_quality_approved"])
        self.assertFalse(report["publication_ready"])

    def test_source_keeps_remote_study_outside_canonical_zero_local_path(self) -> None:
        source = TOOL.read_text(encoding="utf-8")
        self.assertIn("$0-remote-zerogpu-study", source)
        self.assertIn('"canonical_golden_eligible": False', source)
        self.assertIn('"publication_ready": False', source)
        self.assertNotIn('cost_mode = "$0-local"', source)


if __name__ == "__main__":
    unittest.main()
