"""CS309 support: fail-closed lineage contract for SemanticPublicationGate evidence.

The SemanticPublicationGate still owns the publication decision.  This module only
prevents its external evidence envelope from being substituted across runs: the
envelope must bind the exact CS283 request, its exact CS282 parent, the exact composed
PNG, and the inherited generation context.  It also reasserts the zero-cost/offline
verifier contract before CS284 may evaluate the evidence.
"""
from __future__ import annotations

from typing import Any, Mapping

EVIDENCE_SCHEMA = "pul7sar-phase18-semantic-publication-evidence-v2"


def _exact_receipt(binding: Mapping[str, Any], receipt_sha256: Any) -> dict[str, Any]:
    return {
        "repository_relative_path": binding.get("repository_relative_path"),
        "sha256": binding.get("sha256"),
        "byte_size": binding.get("byte_size"),
        "receipt_sha256": receipt_sha256,
    }


def assert_lineage_bound_semantic_publication_evidence(
    raw: Mapping[str, Any],
    *,
    cs283: Mapping[str, Any],
    cs283_binding: Mapping[str, Any],
) -> None:
    """Require one evidence envelope to belong to the exact CS283/CS282/PNG lineage."""
    if raw.get("schema") != EVIDENCE_SCHEMA:
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_SCHEMA_DRIFT")

    expected_cs283 = _exact_receipt(cs283_binding, cs283.get("receipt_sha256"))
    if raw.get("source_cs283_semantic_publication_request") != expected_cs283:
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_CS283_LINEAGE_DRIFT")

    source_cs282 = cs283.get("source_cs282_final_semantic_approval")
    if not isinstance(source_cs282, Mapping) or raw.get("source_cs282_final_semantic_approval") != dict(source_cs282):
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_CS282_LINEAGE_DRIFT")

    story_sha = cs283.get("story_snapshot_sha256")
    if raw.get("story_snapshot_sha256") != story_sha:
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_STORY_DRIFT")

    png = cs283.get("composed_candidate_png")
    if not isinstance(png, Mapping) or raw.get("composed_candidate_png") != dict(png):
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_PNG_LINEAGE_DRIFT")

    generation_context = cs283.get("generation_context")
    if not isinstance(generation_context, Mapping) or raw.get("generation_context") != dict(generation_context):
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_GENERATION_CONTEXT_DRIFT")

    package = raw.get("generation_package")
    base = raw.get("base_scene_evidence")
    verifier = raw.get("vision_verifier_profile")
    if not all(isinstance(item, Mapping) for item in (package, base, verifier)):
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_INPUTS_INVALID")

    package_metadata = package.get("metadata")
    if not isinstance(package_metadata, Mapping):
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_PACKAGE_METADATA_INVALID")
    cs282_sha = source_cs282.get("receipt_sha256")
    png_sha = png.get("sha256")
    for field, expected in (
        ("story_snapshot_sha256", story_sha),
        ("composed_candidate_png_sha256", png_sha),
        ("source_cs282_receipt_sha256", cs282_sha),
    ):
        if package_metadata.get(field) != expected:
            raise ValueError(f"QWEN_SEMANTIC_PUBLICATION_EVIDENCE_PACKAGE_LINEAGE_DRIFT:{field}")

    provenance = base.get("provenance")
    if not isinstance(provenance, Mapping):
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_BASE_PROVENANCE_INVALID")
    for field, expected in (
        ("story_snapshot_sha256", story_sha),
        ("composed_candidate_png_sha256", png_sha),
        ("source_cs282_receipt_sha256", cs282_sha),
    ):
        if provenance.get(field) != expected:
            raise ValueError(f"QWEN_SEMANTIC_PUBLICATION_EVIDENCE_BASE_LINEAGE_DRIFT:{field}")
    if base.get("output_ref") != png.get("repository_relative_path"):
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_OUTPUT_REF_DRIFT")

    if verifier.get("local_zero_cost") is not True or verifier.get("requires_network") is not False:
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_ZERO_COST_OFFLINE_REQUIRED")
    verifier_lineage = raw.get("vision_verifier_lineage")
    expected_verifier_lineage = {
        "source_cs282_receipt_sha256": cs282_sha,
        "composed_candidate_png_sha256": png_sha,
        "cost_mode": "$0-local",
        "network_allowed": False,
        "local_files_only": True,
    }
    if verifier_lineage != expected_verifier_lineage:
        raise ValueError("QWEN_SEMANTIC_PUBLICATION_EVIDENCE_VERIFIER_LINEAGE_DRIFT")
