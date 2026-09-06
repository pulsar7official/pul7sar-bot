from __future__ import annotations

import json
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


def _make_snapshot(tmp_path: Path, *, revision: str | None = None, missing_component: str | None = None) -> Path:
    snapshot = tmp_path / "snapshots" / (revision or readiness.QWEN_IMAGE_2512_REVISION)
    snapshot.mkdir(parents=True)
    model_index = {
        "_class_name": "QwenImagePipeline",
        "scheduler": ["diffusers", "FlowMatchEulerDiscreteScheduler"],
        "transformer": ["diffusers", "QwenImageTransformer2DModel"],
        "vae": ["diffusers", "AutoencoderKLQwenImage"],
    }
    (snapshot / "model_index.json").write_text(json.dumps(model_index), encoding="utf-8")
    for component in ("scheduler", "transformer", "vae"):
        directory = snapshot / component
        directory.mkdir()
        if component != missing_component:
            (directory / "config.json").write_text("{}", encoding="utf-8")
    return snapshot


def test_cpu_runtime_fails_closed(monkeypatch):
    fake_torch = SimpleNamespace(
        __version__="2.10.0+cpu",
        version=SimpleNamespace(cuda=None),
        cuda=_FakeCuda(available=False),
    )
    monkeypatch.setattr(readiness, "import_module", lambda name: fake_torch if name == "torch" else SimpleNamespace(QwenImagePipeline=_FakePipeline))
    monkeypatch.setattr(readiness, "_nvidia_smi_available", lambda: False)

    result = readiness.inspect_qwen_image_gpu_readiness()

    assert result.static_preflight_passed is False
    assert result.ready_for_model_load_attempt is False
    assert result.genuine_inference_executed is False
    assert result.ready_for_genuine_inference_claim is False
    assert result.zero_cost_local_only is True
    assert result.network_required is False
    assert result.snapshot_structure_verified is False
    assert result.snapshot_component_count == 0
    assert "cuda_unavailable" in result.blockers
    assert "native_bf16_unavailable" in result.blockers
    assert "approved_model_snapshot_not_supplied" in result.blockers


def test_compatible_local_runtime_passes_static_preflight_without_claiming_inference(monkeypatch, tmp_path: Path):
    snapshot = _make_snapshot(tmp_path)
    fake_torch = SimpleNamespace(
        __version__="2.10.0+cu128",
        version=SimpleNamespace(cuda="12.8"),
        cuda=_FakeCuda(available=True, bf16=True, memory_gib=24.0),
    )
    monkeypatch.setattr(readiness, "import_module", lambda name: fake_torch if name == "torch" else SimpleNamespace(QwenImagePipeline=_FakePipeline))
    monkeypatch.setattr(readiness, "_nvidia_smi_available", lambda: True)

    result = readiness.inspect_qwen_image_gpu_readiness(snapshot_path=snapshot)

    assert result.static_preflight_passed is True
    assert result.ready_for_model_load_attempt is True
    assert result.genuine_inference_executed is False
    assert result.ready_for_genuine_inference_claim is False
    assert result.blockers == ()
    assert result.snapshot_revision_verified is True
    assert result.snapshot_structure_verified is True
    assert result.snapshot_component_count == 3
    assert result.gpu_memory_gib_observed == 24.0


def test_gpu_memory_is_observed_not_used_as_an_invented_threshold(monkeypatch, tmp_path: Path):
    snapshot = _make_snapshot(tmp_path)
    fake_torch = SimpleNamespace(
        __version__="2.10.0+cu128",
        version=SimpleNamespace(cuda="12.8"),
        cuda=_FakeCuda(available=True, bf16=True, memory_gib=16.0),
    )
    monkeypatch.setattr(readiness, "import_module", lambda name: fake_torch if name == "torch" else SimpleNamespace(QwenImagePipeline=_FakePipeline))
    monkeypatch.setattr(readiness, "_nvidia_smi_available", lambda: True)

    result = readiness.inspect_qwen_image_gpu_readiness(snapshot_path=snapshot)

    assert result.static_preflight_passed is True
    assert result.ready_for_model_load_attempt is True
    assert result.ready_for_genuine_inference_claim is False
    assert result.gpu_memory_gib_observed == 16.0


def test_wrong_snapshot_revision_blocks(monkeypatch, tmp_path: Path):
    snapshot = _make_snapshot(tmp_path, revision="0" * 40)
    fake_torch = SimpleNamespace(
        __version__="2.10.0+cu128",
        version=SimpleNamespace(cuda="12.8"),
        cuda=_FakeCuda(available=True, bf16=True, memory_gib=24.0),
    )
    monkeypatch.setattr(readiness, "import_module", lambda name: fake_torch if name == "torch" else SimpleNamespace(QwenImagePipeline=_FakePipeline))
    monkeypatch.setattr(readiness, "_nvidia_smi_available", lambda: True)

    result = readiness.inspect_qwen_image_gpu_readiness(snapshot_path=snapshot)

    assert result.static_preflight_passed is False
    assert result.ready_for_model_load_attempt is False
    assert result.ready_for_genuine_inference_claim is False
    assert result.snapshot_structure_verified is True
    assert "approved_model_snapshot_revision_unverified" in result.blockers


def test_correctly_named_but_empty_snapshot_is_not_ready(monkeypatch, tmp_path: Path):
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

    assert result.snapshot_revision_verified is True
    assert result.snapshot_structure_verified is False
    assert result.static_preflight_passed is False
    assert result.ready_for_model_load_attempt is False
    assert "approved_model_snapshot_model_index_missing" in result.blockers


def test_partial_snapshot_component_is_reported_fail_closed(monkeypatch, tmp_path: Path):
    snapshot = _make_snapshot(tmp_path, missing_component="transformer")
    fake_torch = SimpleNamespace(
        __version__="2.10.0+cu128",
        version=SimpleNamespace(cuda="12.8"),
        cuda=_FakeCuda(available=True, bf16=True, memory_gib=24.0),
    )
    monkeypatch.setattr(readiness, "import_module", lambda name: fake_torch if name == "torch" else SimpleNamespace(QwenImagePipeline=_FakePipeline))
    monkeypatch.setattr(readiness, "_nvidia_smi_available", lambda: True)

    result = readiness.inspect_qwen_image_gpu_readiness(snapshot_path=snapshot)

    assert result.snapshot_revision_verified is True
    assert result.snapshot_structure_verified is False
    assert result.snapshot_component_count == 3
    assert result.static_preflight_passed is False
    assert "approved_model_snapshot_component_missing:transformer" in result.blockers


def test_snapshot_pipeline_class_must_match_qwen(monkeypatch, tmp_path: Path):
    snapshot = _make_snapshot(tmp_path)
    payload = json.loads((snapshot / "model_index.json").read_text(encoding="utf-8"))
    payload["_class_name"] = "OtherPipeline"
    (snapshot / "model_index.json").write_text(json.dumps(payload), encoding="utf-8")
    fake_torch = SimpleNamespace(
        __version__="2.10.0+cu128",
        version=SimpleNamespace(cuda="12.8"),
        cuda=_FakeCuda(available=True, bf16=True, memory_gib=24.0),
    )
    monkeypatch.setattr(readiness, "import_module", lambda name: fake_torch if name == "torch" else SimpleNamespace(QwenImagePipeline=_FakePipeline))
    monkeypatch.setattr(readiness, "_nvidia_smi_available", lambda: True)

    result = readiness.inspect_qwen_image_gpu_readiness(snapshot_path=snapshot)

    assert result.snapshot_structure_verified is False
    assert result.static_preflight_passed is False
    assert "approved_model_snapshot_pipeline_class_mismatch" in result.blockers
