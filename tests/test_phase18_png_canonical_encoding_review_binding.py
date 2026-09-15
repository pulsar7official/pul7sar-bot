from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.phase18_bind_png_canonical_encoding_to_review_bundle import bind, verify


class CanonicalEncodingReviewBindingTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, Path]:
        bundle = root / "bundle"
        (bundle / "evidence").mkdir(parents=True)
        source_sha = "a" * 40
        png_sha = "b" * 64
        manifest = {
            "schema": "pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1",
            "branch": "phase18/story-intelligence", "candidate": 1,
            "cost_mode": "$0-local", "offline_only": True,
            "exact_evidence_only": True, "eligible_for_human_visual_review": True,
            "source_commit_sha": source_sha, "png_sha256": png_sha,
            "entries": {"candidate_png": {"path": "candidate.png", "sha256": png_sha, "bytes": 1}},
            "authoritative_gate": False, "network_download_authorized": False,
            "generation_authorized": False, "human_visual_review_approved": False,
            "golden_quality_approved": False, "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        (bundle / "review-bundle-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        evidence = {
            "schema": "pul7sar-phase18-first-genuine-golden-png-canonical-encoding-v1",
            "status": "FIRST_GENUINE_GOLDEN_PNG_CANONICAL_ENCODING_VERIFIED",
            "branch": "phase18/story-intelligence", "candidate": 1,
            "cost_mode": "$0-local", "offline_only": True,
            "source_commit_sha": source_sha, "png_sha256": png_sha, "png_bytes": 123,
            "canonical_color_mode": "RGB8", "bit_depth": 8, "color_type": 2,
            "channels": 3, "bits_per_pixel": 24, "interlace_method": 0,
            "canonical_platform_encoding_verified": True,
            "eligible_for_human_visual_review": True,
            "authoritative_gate": False, "network_download_authorized": False,
            "generation_authorized": False, "human_visual_review_approved": False,
            "golden_quality_approved": False, "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        evidence_path = root / "canonical.json"
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        return bundle, evidence_path

    def test_bind_and_replay(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            bundle, evidence = self._fixture(Path(temp))
            result = bind(bundle_dir=bundle, evidence_path=evidence)
            self.assertTrue(result["png_canonical_encoding_verified"])
            replay = verify(bundle_dir=bundle)
            self.assertEqual(replay["status"], "FIRST_GENUINE_GOLDEN_PNG_CANONICAL_ENCODING_EVIDENCE_BOUND_AND_VERIFIED")

    def test_rejects_non_rgb8_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            bundle, evidence = self._fixture(Path(temp))
            payload = json.loads(evidence.read_text())
            payload["color_type"] = 6
            evidence.write_text(json.dumps(payload))
            with self.assertRaisesRegex(RuntimeError, "ENCODING_DRIFT:color_type"):
                bind(bundle_dir=bundle, evidence_path=evidence)

    def test_rejects_authority_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            bundle, evidence = self._fixture(Path(temp))
            payload = json.loads(evidence.read_text())
            payload["publication_ready"] = True
            evidence.write_text(json.dumps(payload))
            with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT:canonical:publication_ready"):
                bind(bundle_dir=bundle, evidence_path=evidence)

    def test_replay_rejects_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            bundle, evidence = self._fixture(Path(temp))
            bind(bundle_dir=bundle, evidence_path=evidence)
            bound = bundle / "evidence/png_canonical_encoding.json"
            bound.write_text(bound.read_text() + "\n")
            with self.assertRaisesRegex(RuntimeError, "EVIDENCE_DRIFT"):
                verify(bundle_dir=bundle)


if __name__ == "__main__":
    unittest.main()
