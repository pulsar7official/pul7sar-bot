#!/usr/bin/env python3
"""Semi-automatic Colab runner for the Phase 18 Golden Visual GPU loop.

GitHub is the source of truth. The runner fast-forwards the Phase 18 branch,
runs CPU-safe regressions, rebuilds and verifies the current Golden batch,
proves GPU readiness, executes one candidate, persists a durable result and
shows the PNG under IPython. It refuses stale Golden contracts before GPU use.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_MANIFEST_VERSION = "pul7sar-golden-batch-v4"
EXPECTED_COMPOSITION = "single_continuous_scene"
EXPECTED_SPORT_GEOMETRY = "association_football_regulation_pitch"
EXPECTED_BRAND_POLICY = "exact_assets_only_after_generation"
DEFAULT_BATCH_DIR = "output/phase18_handoffs/golden-batch"
DEFAULT_GENERATION_DIR = "output/phase18_generated"
DEFAULT_PROOF_DIR = "output/phase18_visual_proof"
DEFAULT_SUMMARY = "output/phase18_colab/latest.json"
TARGETED_TEST_MODULES = (
    "tests.test_phase18_unified_scene_policy",
    "tests.test_phase18_golden_batch",
    "tests.test_phase18_golden_smoke",
    "tests.test_phase18_verify_golden_batch",
    "tests.test_phase18_flux2_execute_command",
    "tests.test_phase18_colab_runner",
    "tests.test_phase18_story_visual_editorial",
    "tests.test_phase18_story_to_visual_orchestrator",
)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.phase18_build_golden_batch import build_batch
from tools.phase18_verify_golden_batch import verify_batch


def _subprocess_env(cwd: Path) -> dict[str, str]:
    env = os.environ.copy()
    root = str(cwd.resolve())
    existing = env.get("PYTHONPATH", "")
    parts = [item for item in existing.split(os.pathsep) if item]
    if root not in parts:
        parts.insert(0, root)
    env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


def _run(command: list[str], *, cwd: Path, capture: bool = True, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=capture,
        check=check,
        env=_subprocess_env(cwd),
    )


def _current_branch(root: Path) -> str:
    completed = _run(["git", "branch", "--show-current"], cwd=root, capture=True)
    if completed.returncode != 0:
        raise RuntimeError("unable to read current git branch: " + completed.stderr.strip())
    return completed.stdout.strip()


def _assert_phase18_branch(root: Path) -> str:
    branch = _current_branch(root)
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(
            f"COLAB_BRANCH_BLOCKED: expected {EXPECTED_BRANCH!r}, found {branch!r}; refusing to touch another branch"
        )
    return branch


def _fast_forward_phase18(root: Path) -> str:
    _assert_phase18_branch(root)
    completed = _run(["git", "pull", "--ff-only", "origin", EXPECTED_BRANCH], cwd=root, capture=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "COLAB_UPDATE_FAILED: fast-forward pull failed; no merge/rebase fallback is attempted\n"
            + completed.stdout[-2000:] + completed.stderr[-2000:]
        )
    _assert_phase18_branch(root)
    head = _run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture=True)
    if head.returncode != 0:
        raise RuntimeError("unable to resolve updated HEAD")
    return head.stdout.strip()


def _run_targeted_tests(root: Path) -> dict[str, Any]:
    command = [sys.executable, "-m", "unittest", "-q", *TARGETED_TEST_MODULES]
    completed = _run(command, cwd=root, capture=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "COLAB_CPU_PREFLIGHT_FAILED: refusing to spend GPU time on a branch that fails the Golden targeted tests\n"
            + completed.stdout[-3000:] + completed.stderr[-3000:]
        )
    return {"status": "COLAB_CPU_PREFLIGHT_PASSED", "test_modules": list(TARGETED_TEST_MODULES)}


def _assert_current_golden_contract(manifest: dict[str, Any]) -> None:
    """Prevent stale Colab prompts/results from masquerading as the current benchmark."""
    failures: list[str] = []
    if manifest.get("manifest_version") != EXPECTED_MANIFEST_VERSION:
        failures.append(f"manifest_version={manifest.get('manifest_version')!r}")
    if manifest.get("composition_grammar") != EXPECTED_COMPOSITION:
        failures.append(f"composition_grammar={manifest.get('composition_grammar')!r}")
    if manifest.get("sport_geometry") != EXPECTED_SPORT_GEOMETRY:
        failures.append(f"sport_geometry={manifest.get('sport_geometry')!r}")
    if manifest.get("generated_branding_allowed") is not False:
        failures.append(f"generated_branding_allowed={manifest.get('generated_branding_allowed')!r}")
    if manifest.get("brand_composition_policy") != EXPECTED_BRAND_POLICY:
        failures.append(f"brand_composition_policy={manifest.get('brand_composition_policy')!r}")
    if failures:
        raise RuntimeError("COLAB_STALE_GOLDEN_CONTRACT: " + "; ".join(failures))


def _json_command(command: list[str], *, root: Path, label: str) -> dict[str, Any]:
    completed = _run(command, cwd=root, capture=True)
    if completed.returncode != 0:
        raise RuntimeError(f"{label} failed\nstdout:\n{completed.stdout[-3000:]}\nstderr:\n{completed.stderr[-3000:]}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} did not emit JSON\nstdout:\n{completed.stdout[-3000:]}\nstderr:\n{completed.stderr[-3000:]}") from exc


def _golden_readiness(root: Path) -> dict[str, Any]:
    payload = _json_command([sys.executable, str(root / "tools" / "phase18_local_readiness.py")], root=root, label="Golden readiness")
    if payload.get("golden_generation_ready") is not True:
        raise RuntimeError("COLAB_GOLDEN_GPU_NOT_READY\n" + json.dumps(payload, ensure_ascii=False, indent=2))
    return payload


def _candidate(manifest: dict[str, Any], candidate_number: int) -> dict[str, Any]:
    if candidate_number <= 0:
        raise ValueError("candidate must be positive")
    for item in manifest.get("candidates", []):
        if int(item.get("candidate", -1)) == candidate_number:
            return dict(item)
    raise ValueError(f"candidate {candidate_number} is not present in the Golden manifest")


def _result_matches_candidate(result: dict[str, Any], selected: dict[str, Any]) -> bool:
    return (
        result.get("status") == "REAL_VISUAL_PROOF_GENERATED"
        and result.get("request_id") == selected.get("request_id")
        and result.get("seed") == selected.get("seed")
        and result.get("model_id") == selected.get("model_id")
        and result.get("payload_sha256") == selected.get("payload_sha256")
        and result.get("cost_mode") == "$0-local"
    )


def _proof_from_result(result: dict[str, Any], root: Path) -> Path:
    if result.get("status") != "REAL_VISUAL_PROOF_GENERATED":
        raise RuntimeError("executor result did not report REAL_VISUAL_PROOF_GENERATED")
    value = result.get("png")
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("executor result does not contain a PNG path")
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    if not path.is_file() or path.suffix.lower() != ".png":
        raise RuntimeError("executor reported a PNG path that does not exist")
    return path.resolve()


def _maybe_display(path: Path) -> bool:
    try:
        from IPython import get_ipython
        shell = get_ipython()
        if shell is None:
            return False
        from IPython.display import Image, display
        display(Image(filename=str(path)))
        return True
    except Exception:
        return False


def _write_summary(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Semi-automatic PUL7SAR Phase 18 Colab Golden Visual runner")
    parser.add_argument("--repository-root", default=str(ROOT))
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-targeted-tests", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--batch-dir", default=DEFAULT_BATCH_DIR)
    parser.add_argument("--generation-dir", default=DEFAULT_GENERATION_DIR)
    parser.add_argument("--proof-dir", default=DEFAULT_PROOF_DIR)
    parser.add_argument("--summary", default=DEFAULT_SUMMARY)
    parser.add_argument("--dtype", choices=("auto", "bfloat16"), default="auto")
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    if not (root / "engine" / "intelligence").is_dir():
        raise RuntimeError("repository-root is not a Phase 18 checkout")

    branch = _assert_phase18_branch(root)
    head = _fast_forward_phase18(root) if args.update else _run(["git", "rev-parse", "--short", "HEAD"], cwd=root).stdout.strip()

    test_preflight = {"status": "COLAB_CPU_PREFLIGHT_SKIPPED", "test_modules": []} if args.skip_targeted_tests else _run_targeted_tests(root)

    batch_dir = root / args.batch_dir
    manifest = build_batch(str(batch_dir))
    _assert_current_golden_contract(manifest)
    integrity = verify_batch(str(batch_dir / "manifest.json"))
    selected = _candidate(manifest, args.candidate)
    readiness = _golden_readiness(root)

    base_summary: dict[str, Any] = {
        "branch": branch,
        "head": head,
        "benchmark": manifest.get("benchmark"),
        "manifest_version": manifest.get("manifest_version"),
        "composition_grammar": manifest.get("composition_grammar"),
        "sport_geometry": manifest.get("sport_geometry"),
        "generated_branding_allowed": manifest.get("generated_branding_allowed"),
        "brand_composition_policy": manifest.get("brand_composition_policy"),
        "candidate": args.candidate,
        "seed": selected.get("seed"),
        "request_id": selected.get("request_id"),
        "payload_sha256": selected.get("payload_sha256"),
        "model_id": selected.get("model_id"),
        "native_canvas": selected.get("native_canvas"),
        "target_canvas": selected.get("target_canvas"),
        "integrity_status": integrity.get("status"),
        "cpu_preflight_status": test_preflight.get("status"),
        "cpu_preflight_modules": test_preflight.get("test_modules"),
        "golden_generation_ready": readiness.get("golden_generation_ready"),
        "recommended_dtype": readiness.get("recommended_dtype"),
        "publication_ready": False,
    }

    summary_path = root / args.summary
    if args.prepare_only:
        payload = {"status": "COLAB_GOLDEN_PREPARED", **base_summary}
        _write_summary(summary_path, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    proof_dir = root / args.proof_dir
    proof_dir.mkdir(parents=True, exist_ok=True)
    result_path = proof_dir / f"colab-candidate-{args.candidate:02d}-result.json"

    if result_path.is_file() and not args.force:
        try:
            existing = json.loads(result_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
        if _result_matches_candidate(existing, selected):
            png = _proof_from_result(existing, root)
            payload = {"status": "COLAB_GOLDEN_ALREADY_EXISTS", **base_summary, "png": str(png), "displayed_inline": _maybe_display(png)}
            _write_summary(summary_path, payload)
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
            return 0

    handoff = batch_dir / str(selected["handoff"])
    command = [
        sys.executable, str(root / "tools" / "phase18_flux2_execute.py"),
        "--request", str(handoff),
        "--generation-dir", str(root / args.generation_dir),
        "--proof-dir", str(proof_dir),
        "--dtype", args.dtype,
        "--result", str(result_path),
    ]

    print("=== PUL7SAR COLAB GPU EXECUTION ===")
    print(f"branch={branch} head={head} candidate={args.candidate} seed={selected.get('seed')}")
    print(
        f"benchmark={manifest.get('benchmark')} manifest={manifest.get('manifest_version')} "
        f"composition={manifest.get('composition_grammar')} geometry={manifest.get('sport_geometry')} "
        f"generated_branding_allowed={manifest.get('generated_branding_allowed')} "
        f"brand_policy={manifest.get('brand_composition_policy')}"
    )
    print("Streaming the locked FLUX executor below; generation may take several minutes on a T4.")
    completed = _run(command, cwd=root, capture=False)
    if completed.returncode != 0:
        raise RuntimeError(f"COLAB_EXECUTOR_FAILED with exit code {completed.returncode}; inspect the traceback above")
    if not result_path.is_file():
        raise RuntimeError("executor succeeded without writing the durable result JSON")

    result = json.loads(result_path.read_text(encoding="utf-8"))
    if not _result_matches_candidate(result, selected):
        raise RuntimeError("executor result identity/SHA/cost contract does not match the selected manifest candidate")
    png = _proof_from_result(result, root)

    payload = {
        "status": "COLAB_REAL_VISUAL_PROOF_GENERATED", **base_summary,
        "png": str(png), "executor_result": str(result_path.resolve()),
        "execution_seconds": result.get("execution_seconds"), "gpu_name": result.get("gpu_name"),
        "gpu_vram_gb": result.get("gpu_vram_gb"), "resolved_dtype": result.get("resolved_dtype"),
        "cuda_peak_allocated_gb": result.get("cuda_peak_allocated_gb"),
        "cuda_peak_reserved_gb": result.get("cuda_peak_reserved_gb"),
        "displayed_inline": _maybe_display(png),
        "publication_note": "Real generation is still subject to semantic verification and strict Golden visual review.",
    }
    _write_summary(summary_path, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
