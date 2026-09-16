"""CPU-only repository integrity gate for the first Golden GPU execution.

This gate is deliberately placed before CUDA qualification/model downloads. It
proves that the currently active Phase 18 study-brand transport is the compact,
member-pinned reference master and that the legacy truncated ZIP transport is
not authoritative. It grants no generation or publication authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from engine.intelligence.brand_embedded_master import EmbeddedBrandMasterLoader
from engine.intelligence.brand_reference_master import APPROVED_BRAND_REFERENCE_MASTER


EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"
EXPECTED_COMPACT_DATA_DIR = Path("assets/brand/compact_v1")
LEGACY_TRUNCATED_TRANSPORT = Path("assets/brand/pul7sar_reference_master_v1.zip.b64")


@dataclass(frozen=True)
class PreGpuRepositoryIntegrityReceipt:
    schema: str
    branch: str
    ready: bool
    blockers: tuple[str, ...]
    cost_mode: str
    compact_brand_contract: str
    compact_brand_bundle_sha256: str
    compact_brand_source_reference_sha256: str
    compact_brand_member_integrity_pinned: bool
    compact_brand_self_contained: bool
    compact_brand_study_only: bool
    legacy_transport_path: str
    legacy_transport_exists: bool
    legacy_transport_authoritative: bool
    network_required: bool
    gpu_required: bool
    generation_authorized: bool
    queue_mutated: bool
    png_created: bool
    publication_ready: bool

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["blockers"] = list(self.blockers)
        return payload


class PreGpuRepositoryIntegrityGate:
    """Verify CPU-side repository evidence before any expensive GPU operation."""

    SCHEMA = "pul7sar-phase18-pre-gpu-repository-integrity-v1"

    def inspect(self, *, repository_root: str | Path, branch: str) -> PreGpuRepositoryIntegrityReceipt:
        root = Path(repository_root).resolve()
        blockers: list[str] = []

        if branch != EXPECTED_BRANCH:
            blockers.append("unexpected_branch")

        if EmbeddedBrandMasterLoader.DATA_DIR != EXPECTED_COMPACT_DATA_DIR:
            blockers.append("active_brand_transport_not_compact_v1")

        try:
            master = EmbeddedBrandMasterLoader().load(root)
            receipt = master.receipt
        except Exception as exc:
            blockers.append(f"compact_brand_integrity_failed:{type(exc).__name__}:{exc}")
            return PreGpuRepositoryIntegrityReceipt(
                schema=self.SCHEMA,
                branch=branch,
                ready=False,
                blockers=tuple(blockers),
                cost_mode=EXPECTED_COST_MODE,
                compact_brand_contract="unavailable",
                compact_brand_bundle_sha256="",
                compact_brand_source_reference_sha256="",
                compact_brand_member_integrity_pinned=False,
                compact_brand_self_contained=False,
                compact_brand_study_only=True,
                legacy_transport_path=str(LEGACY_TRUNCATED_TRANSPORT),
                legacy_transport_exists=(root / LEGACY_TRUNCATED_TRANSPORT).is_file(),
                legacy_transport_authoritative=False,
                network_required=False,
                gpu_required=False,
                generation_authorized=False,
                queue_mutated=False,
                png_created=False,
                publication_ready=False,
            )

        if receipt.source_reference_sha256 != APPROVED_BRAND_REFERENCE_MASTER.source_sha256:
            blockers.append("compact_brand_source_reference_sha_drift")
        if receipt.member_integrity_pinned is not True:
            blockers.append("compact_brand_member_integrity_not_pinned")
        if receipt.container_sha_authoritative is not False:
            blockers.append("legacy_container_authority_reintroduced")
        if receipt.self_contained is not True or receipt.network_required is not False:
            blockers.append("compact_brand_not_self_contained_zero_network")
        if receipt.font_required is not False or receipt.generator_required is not False:
            blockers.append("compact_brand_requires_recreation")
        if receipt.reference_derived is not True or receipt.study_only is not True:
            blockers.append("compact_brand_study_contract_drift")
        if receipt.publication_ready is not False:
            blockers.append("compact_brand_publication_authority_drift")

        return PreGpuRepositoryIntegrityReceipt(
            schema=self.SCHEMA,
            branch=branch,
            ready=not blockers,
            blockers=tuple(blockers),
            cost_mode=EXPECTED_COST_MODE,
            compact_brand_contract=receipt.contract,
            compact_brand_bundle_sha256=receipt.bundle_sha256,
            compact_brand_source_reference_sha256=receipt.source_reference_sha256,
            compact_brand_member_integrity_pinned=receipt.member_integrity_pinned,
            compact_brand_self_contained=receipt.self_contained,
            compact_brand_study_only=receipt.study_only,
            legacy_transport_path=str(LEGACY_TRUNCATED_TRANSPORT),
            legacy_transport_exists=(root / LEGACY_TRUNCATED_TRANSPORT).is_file(),
            legacy_transport_authoritative=False,
            network_required=False,
            gpu_required=False,
            generation_authorized=False,
            queue_mutated=False,
            png_created=False,
            publication_ready=False,
        )
