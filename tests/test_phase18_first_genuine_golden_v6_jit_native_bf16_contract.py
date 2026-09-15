from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase18-first-genuine-golden-v6-jit.yml"


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_jit_workflow_requires_cuda_runtime_device_and_native_bf16() -> None:
    text = _workflow_text()
    assert "torch.cuda.is_available()" in text
    assert "torch.version.cuda is None" in text
    assert "torch.cuda.device_count() < 1" in text
    assert 'getattr(torch.cuda, "is_bf16_supported", None)' in text
    assert "not is_bf16_supported()" in text
    assert "Native CUDA BF16 support is required; refusing FP16/FP32 substitution" in text


def test_jit_workflow_records_runtime_identity_without_relaxing_offline_contract() -> None:
    text = _workflow_text()
    assert 'HF_HUB_OFFLINE: "1"' in text
    assert 'TRANSFORMERS_OFFLINE: "1"' in text
    assert '"device_name": torch.cuda.get_device_name(device_index)' in text
    assert '"compute_capability": torch.cuda.get_device_capability(device_index)' in text
    assert '"native_bf16": True' in text
    assert '"model_cache_mode": "offline-local-only"' in text
    assert "refusing to install or replace PyTorch automatically" in text


def test_jit_workflow_preserves_runner_branch_and_downstream_authority_gates() -> None:
    text = _workflow_text()
    assert "runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]" in text
    assert 'test "$DISPATCH_REF" = "refs/heads/phase18/story-intelligence"' in text
    assert 'git checkout -B phase18/story-intelligence "$DISPATCH_SHA"' in text
    assert 'git fetch --no-tags origin main:refs/remotes/origin/main' in text
    assert 'if git diff --name-only "$base"...HEAD | grep -qx \'main.py\'; then' in text
    assert '("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized")' in text


def test_native_bf16_preflight_occurs_before_candidate_generation() -> None:
    text = _workflow_text()
    bf16_gate = text.index("Native CUDA BF16 support is required; refusing FP16/FP32 substitution")
    generation = text.index("Run JIT-resource replay locked strict Golden Editorial v6 Candidate 1")
    assert bf16_gate < generation
