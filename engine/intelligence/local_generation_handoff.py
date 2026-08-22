"""Portable JSON handoff for PUL7SAR local GPU generation requests.

A compiled request can be produced by the headless core on one machine and
executed on another compatible $0-local GPU runtime without changing semantics.
The handoff is versioned and SHA-256 protected so prompt/seed/canvas/provider
metadata cannot be edited in transit without being detected before generation.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from engine.intelligence.local_backend_execution import LocalBackendGenerationRequest


class LocalGenerationHandoff:
    VERSION = "pul7sar-local-generation-v2"

    @classmethod
    def _payload_dict(cls, request: LocalBackendGenerationRequest) -> dict[str, object]:
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

    @staticmethod
    def _canonical_bytes(payload: dict[str, object]) -> bytes:
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    @classmethod
    def payload_sha256(cls, payload: dict[str, object]) -> str:
        return sha256(cls._canonical_bytes(payload)).hexdigest()

    @classmethod
    def to_dict(cls, request: LocalBackendGenerationRequest) -> dict[str, object]:
        payload = cls._payload_dict(request)
        payload["payload_sha256"] = cls.payload_sha256(payload)
        return payload

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
        supplied_hash = data.get("payload_sha256")
        if not isinstance(supplied_hash, str) or len(supplied_hash) != 64:
            raise ValueError("generation handoff is missing a valid payload_sha256")
        payload = dict(data)
        payload.pop("payload_sha256", None)
        expected_hash = cls.payload_sha256(payload)
        if supplied_hash != expected_hash:
            raise ValueError("generation handoff integrity check failed")

        required = (
            "provider_id", "model_id", "backend", "prompt", "width", "height",
            "seed", "request_id",
        )
        missing = [name for name in required if name not in payload]
        if missing:
            raise ValueError("missing generation handoff fields: " + ", ".join(missing))
        metadata = dict(payload.get("metadata") or {})
        if metadata.get("cost_mode") != "$0-local":
            raise ValueError("generation handoff must remain locked to $0-local mode")
        return LocalBackendGenerationRequest(
            provider_id=payload["provider_id"],
            model_id=payload["model_id"],
            backend=payload["backend"],
            prompt=payload["prompt"],
            native_negative_constraints=tuple(payload.get("native_negative_constraints") or ()),
            width=int(payload["width"]),
            height=int(payload["height"]),
            seed=int(payload["seed"]),
            request_id=payload["request_id"],
            reference_asset_ids=tuple(payload.get("reference_asset_ids") or ()),
            metadata=metadata,
        )
