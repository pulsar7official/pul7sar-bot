"""Publication integrity gate for generator-bypass PUL7SAR PNG renders."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image

from engine.intelligence.direct_visual_execution import DirectVisualExecutionPlan
from engine.intelligence.direct_visual_renderer import DirectRenderReceipt
from engine.intelligence.layout_planner import PlannedLayout


@dataclass(frozen=True)
class DirectRenderQualityDecision:
    allowed: bool
    failures: tuple[str, ...] = ()
    contract: str = "pul7sar-direct-render-quality-v1"


class DirectRenderQualityGate:
    """Bind publication approval to exact direct-render bytes and dimensions."""

    def evaluate(
        self,
        plan: DirectVisualExecutionPlan,
        layout: PlannedLayout,
        receipt: DirectRenderReceipt,
    ) -> DirectRenderQualityDecision:
        failures: list[str] = []
        path = Path(receipt.output_path)
        if not path.is_file():
            failures.append("render output is missing")
            return DirectRenderQualityDecision(False, tuple(failures))

        payload = path.read_bytes()
        actual_sha = sha256(payload).hexdigest()
        if actual_sha != receipt.sha256:
            failures.append("render output checksum does not match receipt")
        if receipt.renderer_contract != "pul7sar-direct-renderer-v1":
            failures.append("unsupported direct renderer contract")
        if receipt.route != plan.route.value:
            failures.append("receipt route does not match execution plan")
        if receipt.base_source != plan.base_source.value:
            failures.append("receipt base source does not match execution plan")
        if plan.metadata.get("generator_bypassed") is not True:
            failures.append("direct plan does not prove generator bypass")
        if plan.metadata.get("provider_selection_performed") is not False:
            failures.append("direct plan indicates provider selection")
        if plan.metadata.get("gpu_job_required") is not False:
            failures.append("direct plan indicates GPU execution")

        expected = (layout.profile.width, layout.profile.height)
        if (receipt.width, receipt.height) != expected:
            failures.append("receipt dimensions do not match platform layout")
        if receipt.format != "PNG":
            failures.append("direct publication artifact must be PNG")

        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                if image.format != "PNG":
                    failures.append("output bytes are not PNG")
                if image.size != expected:
                    failures.append("output pixel dimensions do not match platform layout")
        except Exception:
            failures.append("output is not a readable image")

        asset_receipts = dict(receipt.asset_sha256)
        if len(asset_receipts) != len(receipt.asset_sha256):
            failures.append("duplicate asset checksum receipt")
        required_assets = set(plan.exact_asset_ids) | set(plan.verified_base_asset_ids)
        missing = sorted(required_assets - set(asset_receipts))
        if missing:
            failures.append("missing asset receipts: " + ", ".join(missing))

        return DirectRenderQualityDecision(not failures, tuple(failures))

    def assert_allowed(self, plan: DirectVisualExecutionPlan, layout: PlannedLayout, receipt: DirectRenderReceipt) -> None:
        decision = self.evaluate(plan, layout, receipt)
        if not decision.allowed:
            raise ValueError("direct render quality gate failed: " + "; ".join(decision.failures))
