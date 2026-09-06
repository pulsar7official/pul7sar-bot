"""Execute exactly one canonical Qwen Image 2512 inference attempt.

Change Set 262 consumes one exact Change Set 261 story-bound generation
authorization. It revalidates that authorization immediately before execution,
claims it exactly once, byte-binds the prompt/runtime/model/inference settings,
and publishes one candidate PNG plus a receipt only after a real inference
callback returns a structurally valid PNG.

A successful PNG is a canonical candidate, never a Golden Visual by itself.
Semantic/Layer QA, Visual Critic, human review, Golden scoring, exact brand and
typography work, and SemanticPublicationGate remain separate downstream gates.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import struct
from typing import Any, Callable, Mapping

from engine.intelligence.approved_model_revisions import (
    QWEN_IMAGE_2512_MODEL_ID,
    QWEN_IMAGE_2512_REVISION,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_story_bound_generation_authorization import (
    STORY_BOUND_GENERATION_AUTHORIZATION_SCHEMA,
    verify_story_bound_generation_authorization,
)

ONE_SHOT_CANONICAL_INFERENCE_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-one-shot-canonical-inference-v1"
)
ONE_SHOT_CONSUMPTION_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-one-shot-authorization-consumption-v1"
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_PROMPT_UTF8_BYTES = 32_768
MAX_NEGATIVE_PROMPT_UTF8_BYTES = 16_384
MAX_QUALIFIED_WIDTH = 1024
MAX_QUALIFIED_HEIGHT = 1024
MAX_QUALIFIED_PIXELS = 1024 * 1024
MAX_QUALIFIED_STEPS = 8
QUALIFIED_GUIDANCE_SCALE = 1.0
MAX_SEED = 2**63 - 1

_REQUIRED_AUTH_TRUE = (
    "production_semantic_replay_executed",
    "fresh_story_gates_passed",
    "live_observable_host_identity_matched",
    "model_weights_loaded",
    "sequential_cpu_offload_enabled",
    "live_host_recheck_passed",
    "controlled_trial_preflight_valid",
    "canonical_generation_authorized",
)
_REQUIRED_AUTH_FALSE = (
    "inference_executed",
    "genuine_canonical_inference_executed",
    "genuine_golden_png_created",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)
_POST_INFERENCE_REQUIRED_FALSE = (
    "genuine_golden_png_created",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)


@dataclass(frozen=True)
class CanonicalInferenceImage:
    png_bytes: bytes
    width: int
    height: int


@dataclass(frozen=True)
class OneShotCanonicalInferenceRun:
    output_dir: Path
    story_snapshot_sha256: str
    png_path: Path
    receipt_path: Path
    consumption_path: Path


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        ch in "0123456789abcdef" for ch in value.lower()
    )


def _inside_repo(repo_root: Path, path: Path, code: str) -> str:
    if path.is_symlink():
        raise ValueError(code)
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if not resolved.is_file():
        raise ValueError(code)
    return relative


def _file_binding(path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _text_binding(
    value: str, *, maximum: int, code: str, allow_empty: bool
) -> dict[str, Any]:
    if not isinstance(value, str):
        raise ValueError(code)
    encoded = value.encode("utf-8")
    if (not allow_empty and not encoded) or len(encoded) > maximum:
        raise ValueError(code)
    return {"sha256": hashlib.sha256(encoded).hexdigest(), "byte_size": len(encoded)}


def _validate_inference_settings(
    width: int,
    height: int,
    seed: int,
    num_inference_steps: int,
    guidance_scale: float,
) -> None:
    if (
        not isinstance(width, int)
        or isinstance(width, bool)
        or width <= 0
        or width > MAX_QUALIFIED_WIDTH
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_WIDTH_OUTSIDE_MEASURED_ENVELOPE")
    if (
        not isinstance(height, int)
        or isinstance(height, bool)
        or height <= 0
        or height > MAX_QUALIFIED_HEIGHT
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_HEIGHT_OUTSIDE_MEASURED_ENVELOPE")
    if width * height > MAX_QUALIFIED_PIXELS:
        raise ValueError("QWEN_CANONICAL_INFERENCE_PIXEL_BUDGET_OUTSIDE_MEASURED_ENVELOPE")
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0 or seed > MAX_SEED:
        raise ValueError("QWEN_CANONICAL_INFERENCE_SEED_INVALID")
    if (
        not isinstance(num_inference_steps, int)
        or isinstance(num_inference_steps, bool)
        or num_inference_steps <= 0
        or num_inference_steps > MAX_QUALIFIED_STEPS
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_STEPS_OUTSIDE_MEASURED_ENVELOPE")
    if (
        not isinstance(guidance_scale, (int, float))
        or isinstance(guidance_scale, bool)
        or not math.isfinite(float(guidance_scale))
        or float(guidance_scale) != QUALIFIED_GUIDANCE_SCALE
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_GUIDANCE_OUTSIDE_MEASURED_CONTRACT")


def _png_dimensions(raw: bytes) -> tuple[int, int]:
    if not isinstance(raw, bytes) or len(raw) < 24 or raw[:8] != PNG_SIGNATURE:
        raise ValueError("QWEN_CANONICAL_INFERENCE_PNG_INVALID")
    if raw[12:16] != b"IHDR":
        raise ValueError("QWEN_CANONICAL_INFERENCE_PNG_IHDR_MISSING")
    width, height = struct.unpack(">II", raw[16:24])
    if width <= 0 or height <= 0:
        raise ValueError("QWEN_CANONICAL_INFERENCE_PNG_DIMENSIONS_INVALID")
    return width, height


def _verify_authorization(
    authorization_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    receipt = verify_story_bound_generation_authorization(
        authorization_path, repo_root=repo_root
    )
    if receipt.get("schema") != STORY_BOUND_GENERATION_AUTHORIZATION_SCHEMA:
        raise ValueError("QWEN_CANONICAL_INFERENCE_AUTH_SCHEMA_DRIFT")
    if receipt.get("model_id") != QWEN_IMAGE_2512_MODEL_ID:
        raise ValueError("QWEN_CANONICAL_INFERENCE_MODEL_DRIFT")
    if receipt.get("model_revision") != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_CANONICAL_INFERENCE_MODEL_REVISION_DRIFT")
    if receipt.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_CANONICAL_INFERENCE_COST_MODE_DRIFT")
    if receipt.get("authorization_scope") != (
        "single_story_single_model_revision_single_runtime_fingerprint"
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_AUTH_SCOPE_DRIFT")
    for field in _REQUIRED_AUTH_TRUE:
        if receipt.get(field) is not True:
            raise ValueError(f"QWEN_CANONICAL_INFERENCE_REQUIRED_GATE_MISSING:{field}")
    for field in _REQUIRED_AUTH_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_CANONICAL_INFERENCE_PREMATURE_AUTHORITY:{field}")
    if not _is_sha256(receipt.get("story_snapshot_sha256")):
        raise ValueError("QWEN_CANONICAL_INFERENCE_STORY_SHA_INVALID")
    if not _is_sha256(receipt.get("expected_runtime_fingerprint_sha256")):
        raise ValueError("QWEN_CANONICAL_INFERENCE_RUNTIME_FINGERPRINT_INVALID")
    if not _is_sha256(receipt.get("authorization_sha256")):
        raise ValueError("QWEN_CANONICAL_INFERENCE_AUTH_DIGEST_INVALID")
    return receipt


def _claim_path(authorization_path: Path, authorization_sha256: str) -> Path:
    return authorization_path.parent / (
        f".canonical-inference-consumed-{authorization_sha256}.json"
    )


def _claim_once(
    *,
    authorization_path: Path,
    authorization: Mapping[str, Any],
    authorization_binding: Mapping[str, Any],
    prompt_binding: Mapping[str, Any],
    negative_prompt_binding: Mapping[str, Any],
    width: int,
    height: int,
    seed: int,
    num_inference_steps: int,
    guidance_scale: float,
) -> Path:
    claim_path = _claim_path(
        authorization_path, str(authorization["authorization_sha256"])
    )
    if claim_path.is_symlink():
        raise ValueError("QWEN_CANONICAL_INFERENCE_CONSUMPTION_PATH_SYMLINK")
    claim = {
        "schema": ONE_SHOT_CONSUMPTION_SCHEMA,
        "status": "QWEN_IMAGE_2512_CANONICAL_AUTHORIZATION_CONSUMED_BEFORE_INFERENCE",
        "authorization_sha256": authorization["authorization_sha256"],
        "authorization_file_sha256": authorization_binding["sha256"],
        "story_snapshot_sha256": authorization["story_snapshot_sha256"],
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "expected_runtime_fingerprint_sha256": authorization[
            "expected_runtime_fingerprint_sha256"
        ],
        "prompt": dict(prompt_binding),
        "negative_prompt": dict(negative_prompt_binding),
        "width": width,
        "height": height,
        "seed": seed,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": float(guidance_scale),
        "canonical_generation_authorized": True,
        "inference_attempt_claimed": True,
        "inference_executed": False,
        "genuine_canonical_inference_executed": False,
        "genuine_golden_png_created": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    claim["consumption_sha256"] = sha256_json(claim)
    data = (json.dumps(claim, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    try:
        fd = os.open(claim_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError("QWEN_CANONICAL_INFERENCE_AUTHORIZATION_ALREADY_CONSUMED") from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        # Once the exclusive file is created, the authorization remains burned.
        raise
    return claim_path


def _load_and_verify_claim(
    path: Path,
    *,
    authorization: Mapping[str, Any],
    authorization_file_sha256: str,
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("QWEN_CANONICAL_INFERENCE_CONSUMPTION_INVALID")
    try:
        claim = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_CANONICAL_INFERENCE_CONSUMPTION_INVALID") from exc
    if not isinstance(claim, dict):
        raise ValueError("QWEN_CANONICAL_INFERENCE_CONSUMPTION_INVALID")
    if claim.get("schema") != ONE_SHOT_CONSUMPTION_SCHEMA or claim.get("status") != (
        "QWEN_IMAGE_2512_CANONICAL_AUTHORIZATION_CONSUMED_BEFORE_INFERENCE"
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_CONSUMPTION_SCHEMA_OR_STATUS_DRIFT")
    claimed = claim.get("consumption_sha256")
    unsigned = dict(claim)
    unsigned.pop("consumption_sha256", None)
    if not _is_sha256(claimed) or sha256_json(unsigned) != claimed:
        raise ValueError("QWEN_CANONICAL_INFERENCE_CONSUMPTION_DIGEST_MISMATCH")
    expected_pairs = {
        "authorization_sha256": authorization.get("authorization_sha256"),
        "authorization_file_sha256": authorization_file_sha256,
        "story_snapshot_sha256": authorization.get("story_snapshot_sha256"),
        "model_id": QWEN_IMAGE_2512_MODEL_ID,
        "model_revision": QWEN_IMAGE_2512_REVISION,
        "cost_mode": COST_MODE,
        "expected_runtime_fingerprint_sha256": authorization.get(
            "expected_runtime_fingerprint_sha256"
        ),
        "prompt": receipt.get("prompt"),
        "negative_prompt": receipt.get("negative_prompt"),
        "width": receipt.get("width"),
        "height": receipt.get("height"),
        "seed": receipt.get("seed"),
        "num_inference_steps": receipt.get("num_inference_steps"),
        "guidance_scale": receipt.get("guidance_scale"),
    }
    for field, expected in expected_pairs.items():
        if claim.get(field) != expected:
            raise ValueError(f"QWEN_CANONICAL_INFERENCE_CONSUMPTION_BINDING_DRIFT:{field}")
    if claim.get("canonical_generation_authorized") is not True or claim.get(
        "inference_attempt_claimed"
    ) is not True:
        raise ValueError("QWEN_CANONICAL_INFERENCE_CONSUMPTION_AUTHORITY_MISSING")
    for field in (
        "inference_executed",
        "genuine_canonical_inference_executed",
        "genuine_golden_png_created",
        "semantic_approved",
        "human_visual_review_approved",
        "golden_quality_approved",
        "publication_ready",
    ):
        if claim.get(field) is not False:
            raise ValueError(f"QWEN_CANONICAL_INFERENCE_CONSUMPTION_AUTHORITY_DRIFT:{field}")
    return claim


def execute_one_shot_canonical_inference(
    authorization_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    seed: int,
    num_inference_steps: int,
    guidance_scale: float,
    observed_runtime_fingerprint_sha256: str,
    inference_callable: Callable[[], CanonicalInferenceImage],
) -> OneShotCanonicalInferenceRun:
    """Execute one authorized callback exactly once and bind its candidate PNG."""
    if output_dir.exists():
        raise ValueError("QWEN_CANONICAL_INFERENCE_OUTPUT_ALREADY_EXISTS")
    if not output_dir.parent.is_dir():
        raise ValueError("QWEN_CANONICAL_INFERENCE_OUTPUT_PARENT_INVALID")
    if not callable(inference_callable):
        raise ValueError("QWEN_CANONICAL_INFERENCE_CALLABLE_INVALID")

    authorization = _verify_authorization(authorization_path, repo_root=repo_root)
    expected_fingerprint = authorization["expected_runtime_fingerprint_sha256"]
    if (
        not _is_sha256(observed_runtime_fingerprint_sha256)
        or observed_runtime_fingerprint_sha256 != expected_fingerprint
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_LIVE_RUNTIME_FINGERPRINT_DRIFT")
    prompt_binding = _text_binding(
        prompt,
        maximum=MAX_PROMPT_UTF8_BYTES,
        code="QWEN_CANONICAL_INFERENCE_PROMPT_INVALID",
        allow_empty=False,
    )
    negative_prompt_binding = _text_binding(
        negative_prompt,
        maximum=MAX_NEGATIVE_PROMPT_UTF8_BYTES,
        code="QWEN_CANONICAL_INFERENCE_NEGATIVE_PROMPT_INVALID",
        allow_empty=True,
    )
    _validate_inference_settings(
        width, height, seed, num_inference_steps, guidance_scale
    )
    authorization_binding = _file_binding(
        authorization_path, "QWEN_CANONICAL_INFERENCE_AUTH_FILE_INVALID"
    )

    consumption_path = _claim_once(
        authorization_path=authorization_path,
        authorization=authorization,
        authorization_binding=authorization_binding,
        prompt_binding=prompt_binding,
        negative_prompt_binding=negative_prompt_binding,
        width=width,
        height=height,
        seed=seed,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
    )

    output_dir.mkdir(mode=0o700)
    failure_path = output_dir / "canonical_inference_failure.json"
    try:
        result = inference_callable()
        if not isinstance(result, CanonicalInferenceImage):
            raise ValueError("QWEN_CANONICAL_INFERENCE_RESULT_TYPE_INVALID")
        actual_width, actual_height = _png_dimensions(result.png_bytes)
        if result.width != actual_width or result.height != actual_height:
            raise ValueError("QWEN_CANONICAL_INFERENCE_RESULT_DIMENSION_METADATA_DRIFT")
        if actual_width != width or actual_height != height:
            raise ValueError("QWEN_CANONICAL_INFERENCE_OUTPUT_DIMENSION_DRIFT")

        png_path = output_dir / "canonical_candidate.png"
        png_tmp = output_dir / ".canonical_candidate.png.tmp"
        with png_tmp.open("xb") as handle:
            handle.write(result.png_bytes)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(png_tmp, png_path)
        png_binding = _file_binding(
            png_path, "QWEN_CANONICAL_INFERENCE_PUBLISHED_PNG_INVALID"
        )

        receipt = {
            "schema": ONE_SHOT_CANONICAL_INFERENCE_SCHEMA,
            "status": "QWEN_IMAGE_2512_ONE_SHOT_CANONICAL_INFERENCE_EXECUTED",
            "story_snapshot_sha256": authorization["story_snapshot_sha256"],
            "model_id": QWEN_IMAGE_2512_MODEL_ID,
            "model_revision": QWEN_IMAGE_2512_REVISION,
            "cost_mode": COST_MODE,
            "authorization": {
                "repository_relative_path": _inside_repo(
                    repo_root,
                    authorization_path,
                    "QWEN_CANONICAL_INFERENCE_AUTH_OUTSIDE_REPOSITORY",
                ),
                **authorization_binding,
                "authorization_sha256": authorization["authorization_sha256"],
            },
            "consumption": {
                "repository_relative_path": _inside_repo(
                    repo_root,
                    consumption_path,
                    "QWEN_CANONICAL_INFERENCE_CONSUMPTION_OUTSIDE_REPOSITORY",
                ),
                **_file_binding(
                    consumption_path, "QWEN_CANONICAL_INFERENCE_CONSUMPTION_INVALID"
                ),
            },
            "prompt": prompt_binding,
            "negative_prompt": negative_prompt_binding,
            "width": width,
            "height": height,
            "seed": seed,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": float(guidance_scale),
            "expected_runtime_fingerprint_sha256": expected_fingerprint,
            "observed_runtime_fingerprint_sha256": observed_runtime_fingerprint_sha256,
            "png": {
                "filename": png_path.name,
                **png_binding,
                "width": actual_width,
                "height": actual_height,
            },
            "production_semantic_replay_executed": True,
            "fresh_story_gates_passed": True,
            "controlled_trial_preflight_valid": True,
            "canonical_generation_authorized": True,
            "inference_executed": True,
            "genuine_canonical_inference_executed": True,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        for field in _POST_INFERENCE_REQUIRED_FALSE:
            if receipt[field] is not False:
                raise RuntimeError(
                    "QWEN_CANONICAL_INFERENCE_INTERNAL_DOWNSTREAM_AUTHORITY_DRIFT"
                )
        receipt["receipt_sha256"] = sha256_json(receipt)
        receipt_path = output_dir / "canonical_inference_receipt.json"
        receipt_tmp = output_dir / ".canonical_inference_receipt.json.tmp"
        receipt_tmp.write_text(
            json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        os.replace(receipt_tmp, receipt_path)
        return OneShotCanonicalInferenceRun(
            output_dir=output_dir,
            story_snapshot_sha256=authorization["story_snapshot_sha256"],
            png_path=png_path,
            receipt_path=receipt_path,
            consumption_path=consumption_path,
        )
    except Exception as exc:
        failure = {
            "schema": ONE_SHOT_CANONICAL_INFERENCE_SCHEMA,
            "status": "QWEN_IMAGE_2512_ONE_SHOT_CANONICAL_INFERENCE_FAILED",
            "story_snapshot_sha256": authorization["story_snapshot_sha256"],
            "authorization_sha256": authorization["authorization_sha256"],
            "failure_class": type(exc).__name__,
            "authorization_consumed": True,
            "canonical_generation_authorized": True,
            "inference_successfully_completed": False,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        failure["receipt_sha256"] = sha256_json(failure)
        failure_path.write_text(
            json.dumps(failure, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        raise


def verify_one_shot_canonical_inference(
    receipt_path: Path, *, repo_root: Path
) -> dict[str, Any]:
    """Revalidate a successful CS262 receipt and exact candidate/claim bytes."""
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise ValueError("QWEN_CANONICAL_INFERENCE_RECEIPT_INVALID")
    raw = receipt_path.read_bytes()
    if not raw:
        raise ValueError("QWEN_CANONICAL_INFERENCE_RECEIPT_INVALID")
    try:
        receipt = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_CANONICAL_INFERENCE_RECEIPT_INVALID") from exc
    if not isinstance(receipt, dict):
        raise ValueError("QWEN_CANONICAL_INFERENCE_RECEIPT_INVALID")
    if receipt.get("schema") != ONE_SHOT_CANONICAL_INFERENCE_SCHEMA:
        raise ValueError("QWEN_CANONICAL_INFERENCE_RECEIPT_SCHEMA_DRIFT")
    if receipt.get("status") != "QWEN_IMAGE_2512_ONE_SHOT_CANONICAL_INFERENCE_EXECUTED":
        raise ValueError("QWEN_CANONICAL_INFERENCE_RECEIPT_STATUS_DRIFT")
    claimed = receipt.get("receipt_sha256")
    unsigned = dict(receipt)
    unsigned.pop("receipt_sha256", None)
    if not _is_sha256(claimed) or sha256_json(unsigned) != claimed:
        raise ValueError("QWEN_CANONICAL_INFERENCE_RECEIPT_DIGEST_MISMATCH")
    if receipt.get("model_id") != QWEN_IMAGE_2512_MODEL_ID or receipt.get(
        "model_revision"
    ) != QWEN_IMAGE_2512_REVISION:
        raise ValueError("QWEN_CANONICAL_INFERENCE_MODEL_DRIFT")
    if receipt.get("cost_mode") != COST_MODE:
        raise ValueError("QWEN_CANONICAL_INFERENCE_COST_MODE_DRIFT")
    if receipt.get("inference_executed") is not True or receipt.get(
        "genuine_canonical_inference_executed"
    ) is not True:
        raise ValueError("QWEN_CANONICAL_INFERENCE_EXECUTION_AUTHORITY_MISSING")
    for field in _POST_INFERENCE_REQUIRED_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(
                f"QWEN_CANONICAL_INFERENCE_DOWNSTREAM_AUTHORITY_DRIFT:{field}"
            )
    _validate_inference_settings(
        receipt.get("width"),
        receipt.get("height"),
        receipt.get("seed"),
        receipt.get("num_inference_steps"),
        receipt.get("guidance_scale"),
    )

    auth = receipt.get("authorization")
    if not isinstance(auth, Mapping):
        raise ValueError("QWEN_CANONICAL_INFERENCE_AUTH_BINDING_INVALID")
    relative = auth.get("repository_relative_path")
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("QWEN_CANONICAL_INFERENCE_AUTH_PATH_INVALID")
    auth_path = repo_root.resolve() / relative
    canonical = _inside_repo(
        repo_root, auth_path, "QWEN_CANONICAL_INFERENCE_AUTH_OUTSIDE_REPOSITORY"
    )
    if canonical != Path(relative).as_posix():
        raise ValueError("QWEN_CANONICAL_INFERENCE_AUTH_PATH_DRIFT")
    current_auth = _file_binding(
        auth_path, "QWEN_CANONICAL_INFERENCE_AUTH_FILE_INVALID"
    )
    if (
        auth.get("sha256") != current_auth["sha256"]
        or auth.get("byte_size") != current_auth["byte_size"]
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_AUTH_BYTE_DRIFT")
    authorization = _verify_authorization(auth_path, repo_root=repo_root)
    if auth.get("authorization_sha256") != authorization.get("authorization_sha256"):
        raise ValueError("QWEN_CANONICAL_INFERENCE_AUTH_DIGEST_DRIFT")
    if receipt.get("story_snapshot_sha256") != authorization.get(
        "story_snapshot_sha256"
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_CROSS_STORY")
    if receipt.get("expected_runtime_fingerprint_sha256") != authorization.get(
        "expected_runtime_fingerprint_sha256"
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_CROSS_RUNTIME")
    if receipt.get("observed_runtime_fingerprint_sha256") != authorization.get(
        "expected_runtime_fingerprint_sha256"
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_RUNTIME_FINGERPRINT_DRIFT")

    consumption = receipt.get("consumption")
    if not isinstance(consumption, Mapping):
        raise ValueError("QWEN_CANONICAL_INFERENCE_CONSUMPTION_BINDING_INVALID")
    consumption_relative = consumption.get("repository_relative_path")
    if (
        not isinstance(consumption_relative, str)
        or not consumption_relative
        or Path(consumption_relative).is_absolute()
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_CONSUMPTION_PATH_INVALID")
    consumption_path = repo_root.resolve() / consumption_relative
    consumption_canonical = _inside_repo(
        repo_root,
        consumption_path,
        "QWEN_CANONICAL_INFERENCE_CONSUMPTION_OUTSIDE_REPOSITORY",
    )
    if consumption_canonical != Path(consumption_relative).as_posix():
        raise ValueError("QWEN_CANONICAL_INFERENCE_CONSUMPTION_PATH_DRIFT")
    current_consumption = _file_binding(
        consumption_path, "QWEN_CANONICAL_INFERENCE_CONSUMPTION_INVALID"
    )
    if (
        consumption.get("sha256") != current_consumption["sha256"]
        or consumption.get("byte_size") != current_consumption["byte_size"]
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_CONSUMPTION_BYTE_DRIFT")
    _load_and_verify_claim(
        consumption_path,
        authorization=authorization,
        authorization_file_sha256=current_auth["sha256"],
        receipt=receipt,
    )

    png = receipt.get("png")
    if not isinstance(png, Mapping) or png.get("filename") != "canonical_candidate.png":
        raise ValueError("QWEN_CANONICAL_INFERENCE_PNG_BINDING_INVALID")
    png_path = receipt_path.parent / "canonical_candidate.png"
    current_png = _file_binding(
        png_path, "QWEN_CANONICAL_INFERENCE_PUBLISHED_PNG_INVALID"
    )
    if png.get("sha256") != current_png["sha256"] or png.get(
        "byte_size"
    ) != current_png["byte_size"]:
        raise ValueError("QWEN_CANONICAL_INFERENCE_PNG_BYTE_DRIFT")
    actual_width, actual_height = _png_dimensions(png_path.read_bytes())
    if (
        png.get("width") != actual_width
        or png.get("height") != actual_height
        or receipt.get("width") != actual_width
        or receipt.get("height") != actual_height
    ):
        raise ValueError("QWEN_CANONICAL_INFERENCE_PNG_DIMENSION_DRIFT")
    return receipt
