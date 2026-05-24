"""Command-to-upstream traceability for Weibo."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from all_in_one.platforms.discovery import discover_endpoints


def build_mapping(
    upstream_root: Path = Path("upstreams"),
) -> Dict[Tuple[str, str], dict]:
    mapping: Dict[Tuple[str, str], dict] = {}
    for ep in discover_endpoints("weibo", upstream_root):
        mapping[(ep.resource, ep.action)] = {
            "module": ep.module_name,
            "class": ep.class_name,
            "function": ep.function_name,
            "source": str(ep.source_file),
            "auth_profile": ep.auth_profile,
        }
    return mapping
