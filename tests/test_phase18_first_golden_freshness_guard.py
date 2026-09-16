import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "phase18_first_golden_freshness_guard.py"
spec = importlib.util.spec_from_file_location("freshness_guard", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

PNG = b"\x89PNG\r\n\x1a\n" + b"candidate-1"


class FreshnessGuardTests(unittest.TestCase):
    def _layout(self, root: Path):
        return {
            "generation_summary": Path("output/latest.json"),
            "semantic_receipt": Path("output/semantic.json"),
            "staging_receipt": Path("output/staging.json"),
            "resource_lock": Path("output/resource.json"),
        }

    def _write_post(self, root: Path, mutable):
        png = root / "output/candidate.png"
        png.parent.mkdir(parents=True, exist_ok=True)
        png.write_bytes(PNG)
        sha = mod._sha256(png)
        for label, rel in mutable.items():
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            payload = {"fresh": label}
            if label in {"staging_receipt", "resource_lock"}:
                payload.update({"png": str(png), "png_sha256": sha})
            target.write_text(json.dumps(payload), encoding="utf-8")
        return png, sha

    def test_new_post_attempt_evidence_passes_and_authority_stays_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mutable = self._layout(root)
            with patch.object(mod, "ROOT", root), patch.object(mod, "MUTABLE", mutable), patch.object(mod, "STAGING", mutable["staging_receipt"]), patch.object(mod, "RESOURCE_LOCK", mutable["resource_lock"]):
                baseline = mod.capture()
                png, sha = self._write_post(root, mutable)
                result = mod.verify(baseline)
            self.assertTrue(result["fresh_attempt_evidence"])
            self.assertEqual(result["blockers"], [])
            self.assertEqual(result["png"], str(png.resolve()))
            self.assertEqual(result["png_sha256"], sha)
            for field in ("generation_authorized", "network_download_authorized", "publication_ready", "seeds_2_to_4_authorized"):
                self.assertIs(result[field], False)

    def test_unchanged_existing_receipts_fail_stale(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mutable = self._layout(root)
            with patch.object(mod, "ROOT", root), patch.object(mod, "MUTABLE", mutable), patch.object(mod, "STAGING", mutable["staging_receipt"]), patch.object(mod, "RESOURCE_LOCK", mutable["resource_lock"]):
                self._write_post(root, mutable)
                baseline = mod.capture()
                result = mod.verify(baseline)
            self.assertFalse(result["fresh_attempt_evidence"])
            self.assertIn("FRESHNESS_POST_ARTIFACT_STALE_GENERATION_SUMMARY", result["blockers"])
            self.assertIn("FRESHNESS_POST_ARTIFACT_STALE_SEMANTIC_RECEIPT", result["blockers"])
            self.assertIn("FRESHNESS_POST_ARTIFACT_STALE_STAGING_RECEIPT", result["blockers"])
            self.assertIn("FRESHNESS_POST_ARTIFACT_STALE_RESOURCE_LOCK", result["blockers"])

    def test_png_path_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mutable = self._layout(root)
            with patch.object(mod, "ROOT", root), patch.object(mod, "MUTABLE", mutable), patch.object(mod, "STAGING", mutable["staging_receipt"]), patch.object(mod, "RESOURCE_LOCK", mutable["resource_lock"]):
                baseline = mod.capture()
                self._write_post(root, mutable)
                resource = root / mutable["resource_lock"]
                payload = json.loads(resource.read_text(encoding="utf-8"))
                payload["png"] = str(root / "output/other.png")
                resource.write_text(json.dumps(payload), encoding="utf-8")
                result = mod.verify(baseline)
            self.assertFalse(result["fresh_attempt_evidence"])
            self.assertIn("FRESHNESS_PNG_PATH_DRIFT", result["blockers"])

    def test_baseline_authority_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            mutable = self._layout(root)
            with patch.object(mod, "ROOT", root), patch.object(mod, "MUTABLE", mutable), patch.object(mod, "STAGING", mutable["staging_receipt"]), patch.object(mod, "RESOURCE_LOCK", mutable["resource_lock"]):
                baseline = mod.capture()
                baseline["generation_authorized"] = True
                self._write_post(root, mutable)
                result = mod.verify(baseline)
            self.assertFalse(result["fresh_attempt_evidence"])
            self.assertIn("FRESHNESS_BASELINE_AUTHORITY_DRIFT_GENERATION_AUTHORIZED", result["blockers"])


if __name__ == "__main__":
    unittest.main()
