from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import phase18_capture_authoritative_pre_generation_evidence as capture_mod


class AuthoritativePreGenerationEvidenceCaptureTests(unittest.TestCase):
    def test_capture_uses_exact_four_authoritative_evidence_names_and_keeps_authority_closed(self) -> None:
        source_sha = "a" * 40
        with tempfile.TemporaryDirectory(dir=capture_mod.ROOT) as tmp:
            output_dir = Path(tmp)
            calls: list[tuple[str, Path]] = []

            def fake_run(tool: str, output: Path) -> None:
                calls.append((tool, output))
                output.write_text("{}\n", encoding="utf-8")

            def fake_bind(**kwargs):
                self.assertEqual(kwargs["source_sha"], source_sha)
                self.assertEqual(kwargs["branch"], "phase18/story-intelligence")
                self.assertEqual(kwargs["network"].name, "first-genuine-golden-v6-zero-cost-network-guard.json")
                self.assertEqual(kwargs["runner"].name, "first-genuine-golden-v6-runner-identity.json")
                self.assertEqual(kwargs["snapshots"].name, "first-genuine-golden-v6-approved-snapshot-inventory.json")
                self.assertEqual(kwargs["blocker"].name, "first-genuine-golden-v6-execution-blocker-probe.json")
                return {"schema": "binding-test", "generation_authorized": False}

            env = {"PUL7SAR_PHASE18_COST_MODE": "$0-local", "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
            with patch.dict(os.environ, env, clear=False), patch.object(capture_mod, "_run", side_effect=fake_run), patch.object(capture_mod, "bind", side_effect=fake_bind):
                payload = capture_mod.capture(source_sha=source_sha, output_dir=output_dir)

            self.assertEqual(len(calls), 4)
            self.assertTrue(payload["ready"])
            for field in ("authoritative_gate", "network_download_authorized", "generation_authorized", "human_review_authorized", "golden_approved", "publication_ready", "seeds_2_to_4_authorized"):
                self.assertFalse(payload[field])
            self.assertTrue((output_dir / "first-genuine-golden-v6-authoritative-pre-generation-binding.json").is_file())

    def test_capture_rejects_non_offline_environment_before_any_probe(self) -> None:
        with tempfile.TemporaryDirectory(dir=capture_mod.ROOT) as tmp:
            env = {"PUL7SAR_PHASE18_COST_MODE": "$0-local", "HF_HUB_OFFLINE": "0", "TRANSFORMERS_OFFLINE": "1"}
            with patch.dict(os.environ, env, clear=False), patch.object(capture_mod, "_run") as run_mock:
                with self.assertRaisesRegex(RuntimeError, "REQUIRES_OFFLINE_MODEL_RESOLUTION"):
                    capture_mod.capture(source_sha="b" * 40, output_dir=Path(tmp))
                run_mock.assert_not_called()

    def test_capture_rejects_malformed_source_sha(self) -> None:
        with tempfile.TemporaryDirectory(dir=capture_mod.ROOT) as tmp:
            with self.assertRaisesRegex(RuntimeError, "SOURCE_SHA_INVALID"):
                capture_mod.capture(source_sha="not-a-sha", output_dir=Path(tmp))


if __name__ == "__main__":
    unittest.main()
