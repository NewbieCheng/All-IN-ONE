from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from all_in_one.cli.auth import redact_cookie


class ErrorCategory(str, Enum):
    AUTH_MISSING = "AUTH_MISSING"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    AUTH_INVALID = "AUTH_INVALID"
    UPSTREAM_ERROR = "UPSTREAM_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    OUTPUT_ERROR = "OUTPUT_ERROR"


@dataclass
class CLIError(Exception):
    category: ErrorCategory
    message: str
    platform: Optional[str] = None
    auth_profile: Optional[str] = None
    cookie_source: Optional[str] = None
    exit_code: int = 1

    def __str__(self) -> str:
        return self.message


def error_payload(error: CLIError) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "error": {
            "category": error.category.value,
            "message": redact_cookie(error.message),
        }
    }
    if error.platform:
        payload["error"]["platform"] = error.platform
    if error.auth_profile:
        payload["error"]["auth_profile"] = error.auth_profile
    if error.cookie_source:
        payload["error"]["cookie_source"] = error.cookie_source
    if error.category in {ErrorCategory.AUTH_EXPIRED, ErrorCategory.AUTH_INVALID} and error.platform:
        payload["error"][
            "cleanup_command"
        ] = f"aione auth {error.platform} clear-cookie"
    return payload

