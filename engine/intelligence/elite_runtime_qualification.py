"""Measured GPU qualification receipts for Elite local image models.

A qualification receipt does not claim a universal minimum VRAM. It proves that
one exact model/backend/dtype/canvas successfully executed on one observed GPU
class. Normal Elite execution can then require the same GPU identity and at least
the qualified canvas envelope without weakening publication or semantic gates.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

from engine.intelligence.local_runtime import RuntimeHardwareSnapshot, RuntimeKind


@dataclass(frozen=True)
class EliteRuntimeQualificationReceipt:
    provider_id: str
    model_id: str
    backend: str
    dtype: str
    gpu_name: str
    gpu_vram_gb: float
    compute_capability: str
    bf16_supported: bool
    qualified_width: int
    qualified_height: int
    backend_version: str
    png_sha256: str
    cuda_peak_allocated_gb: float | None
    cuda_peak_reserved_gb: float | None
    qualified_at_utc: str
    engineering_only: bool = True
    publication_ready: bool = False
    contract: str = "pul7sar-elite-runtime-qualification-v1"

    def __post_init__(self) -> None:
        for name in ("provider_id","model_id","backend","dtype","gpu_name","compute_capability","backend_version","png_sha256","qualified_at_utc"):
            value=getattr(self,name)
            if not isinstance(value,str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if self.dtype != "bfloat16":
            raise ValueError("Elite qualification is locked to bfloat16")
        if not self.bf16_supported:
            raise ValueError("Elite qualification requires proven BF16 support")
        if self.gpu_vram_gb <= 0 or self.qualified_width <= 0 or self.qualified_height <= 0:
            raise ValueError("qualification hardware/canvas values must be positive")
        if len(self.png_sha256)!=64 or any(ch not in "0123456789abcdef" for ch in self.png_sha256.lower()):
            raise ValueError("png_sha256 must be hexadecimal SHA-256")
        try:
            parsed=datetime.fromisoformat(self.qualified_at_utc.replace("Z","+00:00"))
        except ValueError as exc:
            raise ValueError("qualified_at_utc must be ISO-8601") from exc
        if parsed.tzinfo is None:
            raise ValueError("qualified_at_utc must be timezone-aware")
        if not self.engineering_only or self.publication_ready:
            raise ValueError("runtime qualification may never authorize publication")

    @property
    def qualified_megapixels(self) -> float:
        return (self.qualified_width*self.qualified_height)/1_000_000

    def to_dict(self) -> dict[str,object]:
        return {name:getattr(self,name) for name in self.__dataclass_fields__}

    def write(self,path:str) -> str:
        target=Path(path); target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(self.to_dict(),ensure_ascii=False,indent=2,sort_keys=True),encoding="utf-8")
        return str(target)

    @classmethod
    def read(cls,path:str) -> "EliteRuntimeQualificationReceipt":
        return cls(**json.loads(Path(path).read_text(encoding="utf-8")))


class EliteRuntimeQualificationGate:
    """Require current execution to match measured qualification evidence."""

    def evaluate(
        self,
        receipt: EliteRuntimeQualificationReceipt,
        *,
        runtime: RuntimeHardwareSnapshot,
        provider_id: str,
        model_id: str,
        backend: str,
        width: int,
        height: int,
    ) -> tuple[str,...]:
        if not isinstance(receipt,EliteRuntimeQualificationReceipt):
            raise TypeError("receipt must be EliteRuntimeQualificationReceipt")
        if not isinstance(runtime,RuntimeHardwareSnapshot):
            raise TypeError("runtime must be RuntimeHardwareSnapshot")
        failures=[]
        if (receipt.provider_id,receipt.model_id,receipt.backend)!=(provider_id,model_id,backend):
            failures.append("qualification model/backend identity mismatch")
        if runtime.kind is not RuntimeKind.LOCAL_CUDA or not runtime.cuda_available:
            failures.append("qualified Elite execution requires CUDA")
        if runtime.gpu_name != receipt.gpu_name:
            failures.append("current GPU name does not match qualification receipt")
        if runtime.gpu_vram_gb is None or runtime.gpu_vram_gb + 0.05 < receipt.gpu_vram_gb:
            failures.append("current GPU VRAM is below qualified GPU observation")
        if str(runtime.metadata.get("compute_capability") or "") != receipt.compute_capability:
            failures.append("current compute capability does not match qualification receipt")
        if runtime.metadata.get("bf16_supported") is not True:
            failures.append("current GPU does not prove BF16 support")
        if width*height > receipt.qualified_width*receipt.qualified_height:
            failures.append("requested canvas exceeds measured qualification envelope")
        return tuple(failures)

    def assert_allowed(self,*args,**kwargs) -> None:
        failures=self.evaluate(*args,**kwargs)
        if failures:
            raise ValueError("ELITE_RUNTIME_NOT_QUALIFIED: "+"; ".join(failures))
