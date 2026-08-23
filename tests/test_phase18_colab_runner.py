import tempfile
import unittest
from pathlib import Path

from tools.phase18_colab_runner import _candidate, _proof_from_result


class Phase18ColabRunnerTests(unittest.TestCase):
    def test_candidate_selection_uses_manifest_candidate_number(self):
        manifest = {
            "candidates": [
                {"candidate": 1, "seed": 7007001},
                {"candidate": 2, "seed": 7007002},
            ]
        }
        self.assertEqual(_candidate(manifest, 2)["seed"], 7007002)
        with self.assertRaisesRegex(ValueError, "not present"):
            _candidate(manifest, 3)

    def test_candidate_number_must_be_positive(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            _candidate({"candidates": []}, 0)

    def test_proof_result_requires_real_existing_png(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            png = root / "proof.png"
            png.write_bytes(b"\x89PNG\r\n\x1a\nproof")
            result = {"status": "REAL_VISUAL_PROOF_GENERATED", "png": "proof.png"}
            self.assertEqual(_proof_from_result(result, root), png.resolve())

    def test_proof_result_rejects_non_success_status(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(RuntimeError, "REAL_VISUAL_PROOF_GENERATED"):
                _proof_from_result({"status": "FAILED", "png": "proof.png"}, Path(temp))


if __name__ == "__main__":
    unittest.main()
