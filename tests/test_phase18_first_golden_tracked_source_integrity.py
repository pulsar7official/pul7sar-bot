import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/phase18_verify_first_golden_tracked_source_integrity.py"
SPEC = importlib.util.spec_from_file_location("phase18_tracked_source_integrity", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FirstGoldenTrackedSourceIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-b", "phase18/story-intelligence"], cwd=self.root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["git", "config", "user.email", "phase18@example.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Phase18 Test"], cwd=self.root, check=True)
        (self.root / "tracked.txt").write_text("stable\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.txt"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "baseline"], cwd=self.root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        self.baseline = self.root / "output/phase18_gpu_smoke/baseline.json"
        self.verification = self.root / "output/phase18_gpu_smoke/verification.json"
        self.old_env = {key: os.environ.get(key) for key in ("PUL7SAR_PHASE18_COST_MODE", "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")}
        os.environ["PUL7SAR_PHASE18_COST_MODE"] = "$0-local"
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"

    def tearDown(self) -> None:
        for key, value in self.old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.temp.cleanup()

    def _capture(self) -> dict:
        return MODULE.capture(repo_root=self.root, expected_sha=self.sha, output=self.baseline)

    def test_allows_only_runtime_output_and_replays_identical_tracked_source(self) -> None:
        baseline = self._capture()
        runtime = self.root / "output/phase18_gpu_smoke/runtime.json"
        runtime.parent.mkdir(parents=True, exist_ok=True)
        runtime.write_text("{}\n", encoding="utf-8")
        verified = MODULE.verify(repo_root=self.root, expected_sha=self.sha, baseline_path=self.baseline, output=self.verification)
        self.assertTrue(verified["tracked_source_immutable"])
        self.assertTrue(verified["runtime_untracked_paths_restricted_to_output"])
        self.assertEqual(verified["snapshot"]["tracked_index_fingerprint_sha256"], baseline["snapshot"]["tracked_index_fingerprint_sha256"])
        self.assertFalse(verified["publication_ready"])
        self.assertEqual(json.loads(self.verification.read_text(encoding="utf-8"))["phase"], "verified")

    def test_rejects_tracked_worktree_mutation(self) -> None:
        self._capture()
        (self.root / "tracked.txt").write_text("mutated\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "TRACKED_SOURCE_WORKTREE_DIRTY"):
            MODULE.verify(repo_root=self.root, expected_sha=self.sha, baseline_path=self.baseline, output=self.verification)

    def test_rejects_untracked_source_shadow_outside_output(self) -> None:
        self._capture()
        (self.root / "shadow.py").write_text("raise SystemExit\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "TRACKED_SOURCE_UNEXPECTED_UNTRACKED"):
            MODULE.verify(repo_root=self.root, expected_sha=self.sha, baseline_path=self.baseline, output=self.verification)

    def test_rejects_head_drift(self) -> None:
        self._capture()
        (self.root / "second.txt").write_text("new\n", encoding="utf-8")
        subprocess.run(["git", "add", "second.txt"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-m", "drift"], cwd=self.root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with self.assertRaisesRegex(RuntimeError, "TRACKED_SOURCE_HEAD_DRIFT"):
            MODULE.verify(repo_root=self.root, expected_sha=self.sha, baseline_path=self.baseline, output=self.verification)

    def test_rejects_policy_drift(self) -> None:
        os.environ["HF_HUB_OFFLINE"] = "0"
        with self.assertRaisesRegex(RuntimeError, "TRACKED_SOURCE_OFFLINE_POLICY_DRIFT"):
            self._capture()


if __name__ == "__main__":
    unittest.main()
