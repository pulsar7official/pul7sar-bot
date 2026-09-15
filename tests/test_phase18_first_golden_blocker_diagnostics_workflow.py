from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase18-first-genuine-golden-v6-fresh.yml"


def test_first_golden_blocker_probe_precedes_cuda_and_generation_and_is_failure_uploaded() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    probe_step = "- name: Record first-Golden execution blocker probe before CUDA preflight"
    cuda_step = "- name: Prove CUDA native BF16 and offline-only execution without replacement"
    generation_step = "- name: Run freshness-bound canonical Candidate 1"
    failure_upload_step = "- name: Upload failed-attempt diagnostics only"
    probe_path = "output/phase18_gpu_smoke/first-genuine-golden-v6-execution-blocker-probe.json"

    for required in (
        "test -f tools/phase18_probe_first_golden_execution_blocker.py",
        probe_step,
        cuda_step,
        generation_step,
        failure_upload_step,
        "if: failure()",
        "path: output/phase18_gpu_smoke/**",
        probe_path,
    ):
        assert required in text

    assert text.index(probe_step) < text.index(cuda_step) < text.index(generation_step)
    assert text.index(generation_step) < text.index(failure_upload_step)


def test_failed_attempt_diagnostics_are_separate_from_success_review_bundle() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    success_upload = "- name: Upload exact Golden v6 Candidate 1 review bundle"
    failure_upload = "- name: Upload failed-attempt diagnostics only"

    success_block = text[text.index(success_upload) : text.index(failure_upload)]
    failure_block = text[text.index(failure_upload) :]

    assert "if: success()" in success_block
    assert "path: output/phase18_golden_review/${{ github.run_id }}-${{ github.run_attempt }}/**" in success_block
    assert "output/phase18_gpu_smoke/**" not in success_block

    assert "if: failure()" in failure_block
    assert "path: output/phase18_gpu_smoke/**" in failure_block
    assert "output/phase18_golden_review/" not in failure_block
