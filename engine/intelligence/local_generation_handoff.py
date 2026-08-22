"""Portable JSON handoff for PUL7SAR local GPU generation requests.

A compiled request can be produced by the headless core on one machine and
executed on another compatible $0-local GPU runtime without changing semantics.
"""

from __future__ import annotations

import json
from pathlib import Path

from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest


class LocalGenerationHandoff:
    VERSION = "pul7sar-local-generation-v1"

    @classmethod
    def to_dict(cls, request: LocalBackendGenerationRequest) -> dict[str, object]:
        return {
            "handoff_version": cls.VERSION,
            "provider_id": request.provider_id,
            "model_id": request.model_id,
            "backend": request.backend,
            "prompt": request.prompt,
            "native_negative_constraints": list(request.native_negative_constraints),
            "width": request.width,
            "height": request.height,
            "seed": request.seed,
            "request_id": request.request_id,
            "reference_asset_ids": list(request.reference_asset_ids),
            "metadata": dict(request.metadata),
        }

    @classmethod
    def write(cls, request: LocalBackendGenerationRequest, path: str) -> str:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(cls.to_dict(request), ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return str(target)

    @classmethod
    def read(cls, path: str) -> LocalBackendGenerationRequest:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("handoff_version") != cls.VERSION:
            raise ValueError("unsupported or missing PUL7SAR generation handoff version")
        required = (
            "provider_id", "model_id", "backend", "prompt", "width", "height",
            "seed", "request_id",
        )
        missing = [name for name in required if name not in data]
        if missing:
            raise ValueError("missing generation handoff fields: " + ", ".join(missing))
        metadata = dict(data.get("metadata") or {})
        if metadata.get("cost_mode") != "$0-local":
            raise ValueError("generation handoff must remain locked to $0-local mode")
        return LocalBackendGenerationRequest(
            provider_id=data["provider_id"],
            model_id=data["model_id"],
            backend=data["backend"],
            prompt=data["prompt"],
            native_negative_constraints=tuple(data.get("native_negative_constraints") or ()),
            width=int(data["width"]),
            height=int(data["height"]),
            seed=int(data["seed"]),
            request_id=data["request_id"],
            reference_asset_ids=tuple(data.get("reference_asset_ids") or ()),
            metadata=metadata,
        )
