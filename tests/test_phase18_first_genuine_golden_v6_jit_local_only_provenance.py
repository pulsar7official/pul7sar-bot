import unittest
from pathlib import Path

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)
from tools.phase18_colab_first_genuine_jit_replay_locked import _validate_local_only_provenance


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase18-first-genuine-golden-v6-jit.yml"


def _inner() -> dict[str, object]:
    return {
        "local_only_model_receipts_bound": True,
        "network_download_authorized": False,
        "local_files_only": True,
        "semantic_model_id": QWEN25_VL_3B_MODEL_ID,
        "semantic_model_revision": QWEN25_VL_3B_REVISION,
        "flux_model_id": FLUX2_KLEIN_4B_MODEL_ID,
        "flux_model_revision": FLUX2_KLEIN_4B_REVISION,
    }


def _receipt() -> dict[str, object]:
    return {
        "schema": "pul7sar-phase18-local-only-model-receipt-verification-v1",
        "status": "PHASE18_LOCAL_ONLY_MODEL_RECEIPTS_VERIFIED",
        "cost_mode": "$0-local",
        "network_download_authorized": False,
        "local_files_only": True,
        "qwen_model_id": QWEN25_VL_3B_MODEL_ID,
        "qwen_model_revision": QWEN25_VL_3B_REVISION,
        "flux_model_id": FLUX2_KLEIN_4B_MODEL_ID,
        "flux_model_revision": FLUX2_KLEIN_4B_REVISION,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


class FirstGenuineGoldenV6JitLocalOnlyProvenanceTests(unittest.TestCase):
    def test_jit_local_only_provenance_accepts_exact_approved_contract(self) -> None:
        _validate_local_only_provenance(_inner(), _receipt())

    def test_jit_local_only_provenance_rejects_any_contract_drift(self) -> None:
        cases = [
            ("inner", "local_only_model_receipts_bound", False),
            ("inner", "network_download_authorized", True),
            ("inner", "local_files_only", False),
            ("inner", "semantic_model_revision", "drifted-qwen-revision"),
            ("inner", "flux_model_revision", "drifted-flux-revision"),
            ("receipt", "network_download_authorized", True),
            ("receipt", "local_files_only", False),
            ("receipt", "qwen_model_id", "drifted/qwen"),
            ("receipt", "flux_model_id", "drifted/flux"),
            ("receipt", "generation_authorized", True),
            ("receipt", "publication_ready", True),
            ("receipt", "seeds_2_to_4_authorized", True),
        ]
        for target, field, value in cases:
            with self.subTest(target=target, field=field, value=value):
                inner = _inner()
                receipt = _receipt()
                if target == "inner":
                    inner[field] = value
                else:
                    receipt[field] = value
                with self.assertRaisesRegex(RuntimeError, "FIRST_GENUINE_GOLDEN_JIT"):
                    _validate_local_only_provenance(inner, receipt)

    def test_jit_workflow_replays_local_only_evidence_before_upload(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('"local_only_model_receipts_verified"', text)
        self.assertIn('"network_download_authorized"', text)
        self.assertIn('"local_files_only"', text)
        self.assertIn('"qwen_model_id"', text)
        self.assertIn('"qwen_model_revision"', text)
        self.assertIn('"flux_model_id"', text)
        self.assertIn('"flux_model_revision"', text)
        self.assertIn('"local_only_model_receipts"', text)
        self.assertIn("PHASE18_LOCAL_ONLY_MODEL_RECEIPTS_VERIFIED", text)
        self.assertIn("generation_authorized", text)
        self.assertIn("publication_ready", text)
        self.assertIn("seeds_2_to_4_authorized", text)

        replay_index = text.index("Replay JIT-bound Candidate 1 evidence before artifact upload")
        upload_index = text.index("Upload JIT-replay locked genuine Golden v6 Candidate 1 evidence")
        local_only_index = text.index("local_only_model_receipts_verified", replay_index)
        self.assertLess(replay_index, local_only_index)
        self.assertLess(local_only_index, upload_index)

    def test_jit_workflow_keeps_main_isolated_and_downstream_authorities_closed(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('test "$(git branch --show-current)" = "phase18/story-intelligence"', text)
        self.assertIn("git fetch --no-tags origin main:refs/remotes/origin/main", text)
        self.assertIn("git diff --name-only", text)
        self.assertIn("main.py", text)
        self.assertIn('HF_HUB_OFFLINE: "1"', text)
        self.assertIn('TRANSFORMERS_OFFLINE: "1"', text)
        for field in (
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            self.assertIn(field, text)


if __name__ == "__main__":
    unittest.main()
