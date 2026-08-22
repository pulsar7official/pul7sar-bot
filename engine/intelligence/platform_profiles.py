"""Platform-specific static-image output profiles for PUL7SAR.

These are PUL7SAR production presets, not hard-coded claims about permanent
platform limits. Social platforms change presentation behavior over time, so
profiles are centralized, versioned, and replaceable without touching story
intelligence or concept logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class SocialPlatform(str, Enum):
    INSTAGRAM_FEED = "instagram_feed"
    INSTAGRAM_STORY = "instagram_story"
    FACEBOOK_FEED = "facebook_feed"
    X_FEED = "x_feed"
    THREADS_FEED = "threads_feed"
    TIKTOK_PHOTO = "tiktok_photo"
    TELEGRAM_POST = "telegram_post"


@dataclass(frozen=True)
class SafeArea:
    top: int
    right: int
    bottom: int
    left: int

    def __post_init__(self) -> None:
        for name in ("top", "right", "bottom", "left"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")


@dataclass(frozen=True)
class PlatformImageProfile:
    platform: SocialPlatform
    width: int
    height: int
    safe_area: SafeArea
    crop_strategy: str = "art_directed"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.platform, SocialPlatform):
            raise TypeError("platform must be SocialPlatform")
        for name in ("width", "height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.safe_area, SafeArea):
            raise TypeError("safe_area must be SafeArea")
        if not isinstance(self.crop_strategy, str) or not self.crop_strategy.strip():
            raise ValueError("crop_strategy must be non-empty")
        if self.safe_area.left + self.safe_area.right >= self.width:
            raise ValueError("horizontal safe area consumes the canvas")
        if self.safe_area.top + self.safe_area.bottom >= self.height:
            raise ValueError("vertical safe area consumes the canvas")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def aspect_ratio(self) -> str:
        from math import gcd
        divisor = gcd(self.width, self.height)
        return f"{self.width // divisor}:{self.height // divisor}"


class PlatformProfileRegistry:
    """Versioned PUL7SAR defaults for each publishing surface."""

    VERSION = "2026-08-pul7sar-v1"

    _PROFILES = {
        SocialPlatform.INSTAGRAM_FEED: PlatformImageProfile(
            SocialPlatform.INSTAGRAM_FEED, 1080, 1350,
            SafeArea(90, 72, 120, 72),
            metadata={"surface": "feed", "orientation": "portrait"},
        ),
        SocialPlatform.INSTAGRAM_STORY: PlatformImageProfile(
            SocialPlatform.INSTAGRAM_STORY, 1080, 1920,
            SafeArea(220, 72, 300, 72),
            metadata={"surface": "story_reel", "orientation": "vertical"},
        ),
        SocialPlatform.FACEBOOK_FEED: PlatformImageProfile(
            SocialPlatform.FACEBOOK_FEED, 1200, 1500,
            SafeArea(90, 80, 120, 80),
            metadata={"surface": "feed", "orientation": "portrait"},
        ),
        SocialPlatform.X_FEED: PlatformImageProfile(
            SocialPlatform.X_FEED, 1600, 900,
            SafeArea(60, 80, 70, 80),
            metadata={"surface": "feed", "orientation": "landscape"},
        ),
        SocialPlatform.THREADS_FEED: PlatformImageProfile(
            SocialPlatform.THREADS_FEED, 1080, 1350,
            SafeArea(90, 72, 120, 72),
            metadata={"surface": "feed", "orientation": "portrait"},
        ),
        SocialPlatform.TIKTOK_PHOTO: PlatformImageProfile(
            SocialPlatform.TIKTOK_PHOTO, 1080, 1920,
            SafeArea(180, 90, 340, 90),
            metadata={"surface": "photo_post", "orientation": "vertical"},
        ),
        SocialPlatform.TELEGRAM_POST: PlatformImageProfile(
            SocialPlatform.TELEGRAM_POST, 1280, 720,
            SafeArea(50, 60, 60, 60),
            metadata={"surface": "channel_post", "orientation": "landscape"},
        ),
    }

    def get(self, platform: SocialPlatform) -> PlatformImageProfile:
        if not isinstance(platform, SocialPlatform):
            raise TypeError("platform must be SocialPlatform")
        return self._PROFILES[platform]

    def all(self) -> tuple[PlatformImageProfile, ...]:
        return tuple(self._PROFILES[platform] for platform in SocialPlatform)
