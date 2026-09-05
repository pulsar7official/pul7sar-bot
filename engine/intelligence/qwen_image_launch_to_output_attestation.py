"""CS293: bind the verified GPU launch manifest to the genuine canonical output."""
from __future__ import annotations

import hashlib, json, os
from pathlib import Path
from typing import Any, Mapping

from .qwen_image_gpu_host_launch_manifest import verify_gpu_host_launch_manifest
from .qwen_image_local_inference_provenance import verify_local_inference_provenance
from .qwen_image_one_shot_canonical_inference import verify_one_shot_canonical_inference
from .qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-2512-launch-to-output-attestation-v1"
STATUS = "QWEN_IMAGE_2512_LAUNCH_TO_OUTPUT_ATTESTED"
DOWNSTREAM_FALSE = ("semantic_approved","human_visual_review_approved","golden_quality_approved","genuine_golden_png_created","publication_ready")


def _sha(v: Any) -> bool:
    return isinstance(v, str) and len(v) == 64 and all(c in "0123456789abcdef" for c in v.lower())


def _file(path: Path, root: Path, code: str) -> tuple[Path, str]:
    p = (path if path.is_absolute() else root / path)
    if p.is_symlink():
        raise ValueError(code)
    p = p.resolve()
    try:
        rel = p.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not p.is_file():
        raise ValueError(code)
    return p, rel


def _binding(path: Path, root: Path, code: str) -> dict[str, Any]:
    p, rel = _file(path, root, code)
    raw = p.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"repository_relative_path": rel, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _assert_join(launch: Mapping[str, Any], prov: Mapping[str, Any], canonical: Mapping[str, Any]) -> None:
    for field in ("story_snapshot_sha256","model_id","model_revision","cost_mode"):
        if prov.get(field) != launch.get(field) or canonical.get(field) != launch.get(field):
            raise ValueError(f"QWEN_LAUNCH_OUTPUT_JOIN_DRIFT:{field}")
    ls, ps = launch.get("snapshot"), prov.get("snapshot")
    if not isinstance(ls, Mapping) or not isinstance(ps, Mapping):
        raise ValueError("QWEN_LAUNCH_OUTPUT_SNAPSHOT_INVALID")
    for field in ("resolved_path","revision","revision_verified"):
        if ps.get(field) != ls.get(field):
            raise ValueError(f"QWEN_LAUNCH_OUTPUT_SNAPSHOT_DRIFT:{field}")
    settings = launch.get("inference_settings")
    if not isinstance(settings, Mapping):
        raise ValueError("QWEN_LAUNCH_OUTPUT_SETTINGS_INVALID")
    for field in ("width","height","seed","num_inference_steps","guidance_scale"):
        if canonical.get(field) != settings.get(field):
            raise ValueError(f"QWEN_LAUNCH_OUTPUT_SETTINGS_DRIFT:{field}")
    if launch.get("network_allowed") is not False or prov.get("network_allowed") is not False:
        raise ValueError("QWEN_LAUNCH_OUTPUT_NETWORK_DRIFT")
    if launch.get("local_files_only") is not True or prov.get("local_files_only") is not True:
        raise ValueError("QWEN_LAUNCH_OUTPUT_LOCAL_ONLY_DRIFT")
    if prov.get("genuine_canonical_inference_executed") is not True:
        raise ValueError("QWEN_LAUNCH_OUTPUT_GENUINE_INFERENCE_MISSING")
    for field in DOWNSTREAM_FALSE:
        if prov.get(field) is not False or canonical.get(field) is not False:
            raise ValueError(f"QWEN_LAUNCH_OUTPUT_PREMATURE_AUTHORITY:{field}")


def build_launch_to_output_attestation(launch_manifest_path: Path, provenance_path: Path, output_path: Path, *, repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    lm, _ = _file(launch_manifest_path, root, "QWEN_LAUNCH_OUTPUT_MANIFEST_INVALID")
    pp, _ = _file(provenance_path, root, "QWEN_LAUNCH_OUTPUT_PROVENANCE_INVALID")
    launch = verify_gpu_host_launch_manifest(lm, repo_root=root)
    prov = verify_local_inference_provenance(pp, repo_root=root)
    cr = prov.get("canonical_inference_receipt")
    if not isinstance(cr, Mapping) or not isinstance(cr.get("repository_relative_path"), str):
        raise ValueError("QWEN_LAUNCH_OUTPUT_CANONICAL_BINDING_INVALID")
    cp, _ = _file(root / cr["repository_relative_path"], root, "QWEN_LAUNCH_OUTPUT_CANONICAL_INVALID")
    canonical = verify_one_shot_canonical_inference(cp, repo_root=root)
    _assert_join(launch, prov, canonical)
    png = prov.get("canonical_candidate_png")
    if not isinstance(png, Mapping) or not isinstance(png.get("repository_relative_path"), str):
        raise ValueError("QWEN_LAUNCH_OUTPUT_PNG_BINDING_INVALID")
    pngp, _ = _file(root / png["repository_relative_path"], root, "QWEN_LAUNCH_OUTPUT_PNG_INVALID")
    payload = {
        "schema": SCHEMA, "status": STATUS,
        "story_snapshot_sha256": canonical.get("story_snapshot_sha256"),
        "model_id": canonical.get("model_id"), "model_revision": canonical.get("model_revision"),
        "cost_mode": "$0-local", "network_allowed": False, "local_files_only": True,
        "launch_manifest": _binding(lm, root, "QWEN_LAUNCH_OUTPUT_MANIFEST_INVALID"),
        "local_inference_provenance": _binding(pp, root, "QWEN_LAUNCH_OUTPUT_PROVENANCE_INVALID"),
        "canonical_inference_receipt": _binding(cp, root, "QWEN_LAUNCH_OUTPUT_CANONICAL_INVALID"),
        "canonical_candidate_png": {**_binding(pngp, root, "QWEN_LAUNCH_OUTPUT_PNG_INVALID"), "width": canonical.get("width"), "height": canonical.get("height")},
        "inference_settings": dict(launch["inference_settings"]),
        "launch_to_output_binding_verified": True, "genuine_canonical_inference_executed": True,
        "semantic_approved": False, "human_visual_review_approved": False, "golden_quality_approved": False,
        "genuine_golden_png_created": False, "publication_ready": False,
    }
    payload["attestation_sha256"] = sha256_json(payload)
    out = output_path if output_path.is_absolute() else root / output_path
    try:
        out.parent.resolve().relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_LAUNCH_OUTPUT_OUTPUT_OUTSIDE_REPOSITORY") from exc
    if out.exists() or out.is_symlink() or not out.parent.is_dir():
        raise ValueError("QWEN_LAUNCH_OUTPUT_OUTPUT_INVALID")
    raw = (json.dumps(payload, ensure_ascii=False, separators=(",",":")) + "\n").encode()
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as h:
        h.write(raw); h.flush(); os.fsync(h.fileno())
    return payload


def verify_launch_to_output_attestation(path: Path, *, repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve()
    rp, _ = _file(path, root, "QWEN_LAUNCH_OUTPUT_RECEIPT_INVALID")
    try:
        payload = json.loads(rp.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_LAUNCH_OUTPUT_RECEIPT_INVALID") from exc
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA or payload.get("status") != STATUS:
        raise ValueError("QWEN_LAUNCH_OUTPUT_SCHEMA_STATUS_DRIFT")
    claimed = payload.get("attestation_sha256"); unsigned = dict(payload); unsigned.pop("attestation_sha256", None)
    if not _sha(claimed) or sha256_json(unsigned) != claimed:
        raise ValueError("QWEN_LAUNCH_OUTPUT_DIGEST_MISMATCH")
    for field in DOWNSTREAM_FALSE:
        if payload.get(field) is not False:
            raise ValueError(f"QWEN_LAUNCH_OUTPUT_DOWNSTREAM_AUTHORITY_DRIFT:{field}")
    if payload.get("launch_to_output_binding_verified") is not True or payload.get("genuine_canonical_inference_executed") is not True:
        raise ValueError("QWEN_LAUNCH_OUTPUT_AUTHORITY_MISSING")
    def bound(name: str) -> Path:
        b = payload.get(name)
        if not isinstance(b, Mapping) or not isinstance(b.get("repository_relative_path"), str):
            raise ValueError(f"QWEN_LAUNCH_OUTPUT_BINDING_INVALID:{name}")
        cur = _binding(root / b["repository_relative_path"], root, f"QWEN_LAUNCH_OUTPUT_FILE_INVALID:{name}")
        if b.get("sha256") != cur["sha256"] or b.get("byte_size") != cur["byte_size"]:
            raise ValueError(f"QWEN_LAUNCH_OUTPUT_BYTE_DRIFT:{name}")
        return root / b["repository_relative_path"]
    lm, pp, cp = bound("launch_manifest"), bound("local_inference_provenance"), bound("canonical_inference_receipt")
    bound("canonical_candidate_png")
    launch = verify_gpu_host_launch_manifest(lm, repo_root=root)
    prov = verify_local_inference_provenance(pp, repo_root=root)
    canonical = verify_one_shot_canonical_inference(cp, repo_root=root)
    _assert_join(launch, prov, canonical)
    if payload.get("inference_settings") != launch.get("inference_settings"):
        raise ValueError("QWEN_LAUNCH_OUTPUT_SETTINGS_RECEIPT_DRIFT")
    return payload
