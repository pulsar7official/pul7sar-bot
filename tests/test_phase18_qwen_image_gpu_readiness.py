from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import engine.intelligence.qwen_image_gpu_readiness as readiness


class _FakeCuda:
    def __init__(self, *, available: bool, bf16: bool = False, memory_gib: float = 0.0):
        self._available = available
        self._bf16 = bf16
        self._memory = int(memory_gib * (1024 ** 3))

    def is_available(self):
        return self._available

    def device_count(self):
        return 1 if self._available else 0

    def is_bf16_supported(self):
        return self._bf16

    def get_device_properties(self, _index):
        return SimpleNamespace(name="Fake GPU", total_memory=self._memory)


class _FakePipeline:
    def enable_sequential_cpu_offload(self):
        return None


def test_cpu_runtime_fails_closed(monkeypatch):
    fake_torch = SimpleNamespace(
        __version__="2.10.0+cpu",
        version=SimpleNamespace(cuda=None),
        cuda=_FakeCuda(available=False),
    )
    monkeypatch.setattr(readiness, "import_module", lambda name: fake_torch if name == "torch" else SimpleNamespace(QwenImagePipeline=_FakePipeline))
    monkeypatch.setattr(readiness, "_nvidia_smi_available", lambda: False)

    result = readiness.inspect_qwen_image_gpu_readiness()

    assert result.ready_for_genuine_inference is False
    assert result.zero_cost_local_only is True
    assert result.network_required is False
    assert "cuda_unavailable" in result.blockers
    assert "native_bf16_unavailable" in result.blockers
    assert "approved_model_snapshot_not_supplied" in result.blockers


def test_compatible_local_runtime_can_be_ready(monkeypatch, tmp_path: Path):
    snapshot = tmp_path / "snapshots" / readiness.QWEN_IMAGE_2512_REVISION
    snapshot.mkdir(parents=True)
    fake_torch = SimpleNamespace(
        __version__="2.10.0+cu128",
        version=SimpleNamespace(cuda="12.8"),
        cuda=_FakeCuda(available=True, bf16=True, memory_gib=24.0),
    )
    monkeypatch.setattr(readiness, "import_module", lambda name: fake_torch if name == "torch" else SimpleNamespace(QwenImagePipeline=_FakePipeline))
    monkeypatch.setattr(readiness, "_nvidia_smi_available", lambda: True)

    result = readiness.inspect_qwen_image_gpu_readiness(snapshot_path=snapshot)

    assert result.ready_for_genuine_inference is True
    assert result.blockers == ()
    assert result.snapshot_revision_verified is True
    assert result.gpu_memory_gib == 24.0


def test_insufficient_gpu_memory_blocks_even_with_cuda(monkeypatch, tmp_path: Path):
    snapshot = tmp_path / "snapshots" / readiness.QWEN_IMAGE_2512_REVISION
    snapshot.mkdir(parents=True)
    fake_torch = SimpleNamespace(
        __version__="2.10.0+cu128",
        version=SimpleNamespace(cuda="12.8"),
        cuda=_FakeCuda(available=True, bf16=True, memory_gib=16.0),
    )
    monkeypatch.setattr(readiness, "import_module", lambda name: fake_torch if name == "torch" else SimpleNamespace(QwenImagePipeline=_FakePipeline))
    monkeypatch.setattr(readiness, "_nvidia_smi_available", lambda: True)

    result = readiness.inspect_qwen_image_gpu_readiness(snapshot_path=snapshot)

    assert result.ready_for_genuine_inference is False
    assert "gpu_memory_below_20gib_or_unknown" in result.blockers


def test_wrong_snapshot_revision_blocks(monkeypatch, tmp_path: Path):
    snapshot = tmp_path / "snapshots" / ("0" * 40)
    snapshot.mkdir(parents=True)
    fake_torch = SimpleNamespace(
        __version__="2.10.0+cu128",
        version=SimpleNamespace(cuda="12.8"),
        cuda=_FakeCuda(available=True, bf16=True, memory_gib=24.0),
    )
    monkeypatch.setattr(readiness, "import_module", lambda name: fake_torch if name == "torch" else SimpleNamespace(QwenImagePipeline=_FakePipeline))
    monkeypatch.setattr(readiness, "_nvidia_smi_available", lambda: True)

    result = readiness.inspect_qwen_image_gpu_readiness(snapshot_path=snapshot)

    assert result.ready_for_genuine_inference is False
    assert "approved_model_snapshot_revision_unverified" in result.blockers
