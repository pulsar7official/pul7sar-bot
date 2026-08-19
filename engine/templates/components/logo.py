from pathlib import Path
from typing import Optional
from PIL import Image
from engine.core.context import RenderContext
from engine.layers.layer import Layer, LayerKind, LayerZone
from engine.templates.components.constants import LOGO_MAX_WIDTH, LOGO_X, LOGO_Y

def _load_master_logo() -> Optional[Image.Image]:
    repo_root = Path(__file__).resolve().parents[3]
    logo_path = repo_root / "logo.png"
    if not logo_path.is_file():
        return None
    try:
        with Image.open(logo_path) as image:
            return image.convert("RGBA").copy()
    except Exception:
        return None

def logo_component(render_context: RenderContext, width: int, height: int) -> Optional[Layer]:
    del render_context, width, height
    logo = _load_master_logo()
    if logo is None:
        return None
    ratio = min(1.0, LOGO_MAX_WIDTH / max(1, logo.width))
    target_w = max(1, int(logo.width * ratio))
    target_h = max(1, int(logo.height * ratio))
    return Layer(
        kind=LayerKind.IMAGE, zone=LayerZone.BRAND, z_index=10,
        properties={
            "image": logo, "x": LOGO_X, "y": LOGO_Y,
            "width": target_w, "height": target_h,
        },
    )
