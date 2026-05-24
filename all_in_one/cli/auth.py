from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Optional

from platformdirs import user_config_dir


SUPPORTED_PLATFORMS = {"xhs", "weibo", "douyin"}


@dataclass(frozen=True)
class CookieResolution:
    platform: str
    value: str
    source: str
    profile: str = "default"


class CookieStore:
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = Path(
            config_dir or user_config_dir("aione", appauthor=False)
        )

    def cookie_path(self, platform: str, profile: str = "default") -> Path:
        normalized = normalize_platform(platform)
        normalized_profile = normalize_profile(profile)
        return self.config_dir / normalized / f"{normalized_profile}.json"

    def save_cookie(
        self,
        platform: str,
        cookie: str,
        profile: str = "default",
        source: str = "cli",
    ) -> Path:
        normalized = normalize_platform(platform)
        normalized_profile = normalize_profile(profile)
        now = _utc_now()
        path = self.cookie_path(normalized, normalized_profile)
        path.parent.mkdir(parents=True, exist_ok=True)

        created_at = now
        if path.exists():
            try:
                created_at = json.loads(path.read_text(encoding="utf-8")).get(
                    "created_at", now
                )
            except (json.JSONDecodeError, OSError):
                created_at = now

        payload = {
            "platform": normalized,
            "profile": normalized_profile,
            "cookie": cookie,
            "source": source,
            "created_at": created_at,
            "updated_at": now,
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        _chmod_user_only(path)
        return path

    def load_cookie(
        self, platform: str, profile: str = "default"
    ) -> Optional[CookieResolution]:
        normalized = normalize_platform(platform)
        normalized_profile = normalize_profile(profile)
        path = self.cookie_path(normalized, normalized_profile)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        cookie = payload.get("cookie")
        if not cookie:
            return None
        return CookieResolution(
            platform=normalized,
            value=str(cookie),
            source="saved",
            profile=normalized_profile,
        )

    def clear_cookie(self, platform: str, profile: str = "default") -> bool:
        path = self.cookie_path(
            normalize_platform(platform), normalize_profile(profile)
        )
        if not path.exists():
            return False
        path.unlink()
        return True


def resolve_cookie(
    platform: str,
    profile: str = "default",
    cli_cookie: Optional[str] = None,
    store: Optional[CookieStore] = None,
    env: Optional[Mapping[str, str]] = None,
) -> Optional[CookieResolution]:
    normalized = normalize_platform(platform)
    normalized_profile = normalize_profile(profile)
    if cli_cookie:
        return CookieResolution(normalized, cli_cookie, "cli", normalized_profile)

    environment = env or os.environ
    env_name = f"AIONE_{normalized.upper()}_{normalized_profile.upper()}_COOKIES"
    if environment.get(env_name):
        return CookieResolution(
            normalized, environment[env_name], "env", normalized_profile
        )

    if normalized_profile == "default":
        legacy_env_name = f"AIONE_{normalized.upper()}_COOKIES"
        if environment.get(legacy_env_name):
            return CookieResolution(
                normalized, environment[legacy_env_name], "env", normalized_profile
            )

    return (store or CookieStore()).load_cookie(normalized, normalized_profile)


def normalize_platform(platform: str) -> str:
    normalized = platform.strip().lower().replace("-", "_")
    if normalized not in SUPPORTED_PLATFORMS:
        raise ValueError(f"Unsupported platform: {platform}")
    return normalized


def normalize_profile(profile: str) -> str:
    normalized = (profile or "default").strip().lower().replace("-", "_")
    if not re.match(r"^[a-z0-9_]+$", normalized):
        raise ValueError(f"Unsupported auth profile: {profile}")
    return normalized


def redact_cookie(text: str) -> str:
    redacted = str(text)
    patterns = [
        r"(?i)(cookie\s*[:=]\s*)([^;\s]+(?:;[^;\n\r]*)*)",
        r"(?i)\b(sid|uid|xsec_token|webid|sessionid|passport_csrf_token)\s*=\s*([^;\s]+)",
    ]
    redacted = re.sub(patterns[0], lambda match: f"{match.group(1)}<redacted>", redacted)
    redacted = re.sub(patterns[1], lambda match: f"{match.group(1)}=<redacted>", redacted)
    return redacted


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _chmod_user_only(path: Path) -> None:
    try:
        path.chmod(0o600)
    except OSError:
        pass

