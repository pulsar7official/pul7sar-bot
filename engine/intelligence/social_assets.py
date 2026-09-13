"""Destination-specific social icon selection for PUL7SAR output packages."""

from __future__ import annotations

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole
from engine.intelligence.platform_profiles import SocialPlatform


_PLATFORM_KEYS = {
    SocialPlatform.INSTAGRAM_FEED: "instagram",
    SocialPlatform.INSTAGRAM_STORY: "instagram",
    SocialPlatform.FACEBOOK_FEED: "facebook",
    SocialPlatform.X_FEED: "x",
    SocialPlatform.THREADS_FEED: "threads",
    SocialPlatform.TIKTOK_PHOTO: "tiktok",
    SocialPlatform.TELEGRAM_POST: "telegram",
}


class DestinationSocialAssetSelector:
    """Select only the destination platform icon; never a dense multi-platform row."""

    def select(self, platform: SocialPlatform, bundle: AssetBundle) -> AssetBundle:
        if not isinstance(platform, SocialPlatform):
            raise TypeError("platform must be SocialPlatform")
        if not isinstance(bundle, AssetBundle):
            raise TypeError("bundle must be AssetBundle")

        target = _PLATFORM_KEYS[platform]
        selected: list[AssetReference] = []
        social_matches: list[AssetReference] = []
        for asset in bundle.assets:
            if asset.role is not AssetRole.SOCIAL_ICON:
                selected.append(asset)
                continue
            key = str(asset.metadata.get("platform", "")).strip().casefold()
            if key == target:
                social_matches.append(asset)

        if len(social_matches) > 1:
            raise ValueError(f"multiple social icons configured for destination: {target}")
        selected.extend(social_matches)
        return AssetBundle(tuple(selected))
