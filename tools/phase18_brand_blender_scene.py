from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacementResolver, BrandZone
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


def main():
    p=argparse.ArgumentParser(); p.add_argument('--family',required=True); p.add_argument('--input',required=True); p.add_argument('--output',required=True); p.add_argument('--accent',required=True); a=p.parse_args()
    family=EditorialSceneFamily(a.family); profile=PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
    occupied=(BrandZone.UPPER_LEFT,)
    placement=AdaptiveBrandPlacementResolver().resolve(family=family,profile=profile,occupied_zones=occupied)
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    AdaptiveBrandOverlayRenderer().render_on_file(base_path=a.input,output_path=a.output,adaptive=placement,profile=profile,accent_hex=a.accent)

if __name__=='__main__': main()
