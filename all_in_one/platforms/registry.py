from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from all_in_one.platforms.discovery import Endpoint, discover_endpoints


@dataclass(frozen=True)
class Registry:
    endpoints: Tuple[Endpoint, ...]
    by_command: Dict[Tuple[str, str, str], Endpoint]


def build_registry(upstream_root: Path = Path("upstreams")) -> Registry:
    endpoints: List[Endpoint] = []
    for platform in ("xhs", "weibo", "douyin"):
        endpoints.extend(discover_endpoints(platform, upstream_root))

    by_command: Dict[Tuple[str, str, str], Endpoint] = {}
    normalized: List[Endpoint] = []
    for endpoint in endpoints:
        key = (endpoint.platform, endpoint.resource, endpoint.action)
        if key in by_command:
            endpoint = _with_unique_action(endpoint)
            key = (endpoint.platform, endpoint.resource, endpoint.action)
            suffix = 2
            while key in by_command:
                endpoint = _replace_action(endpoint, f"{endpoint.action}-{suffix}")
                key = (endpoint.platform, endpoint.resource, endpoint.action)
                suffix += 1
        by_command[key] = endpoint
        normalized.append(endpoint)

    return Registry(endpoints=tuple(normalized), by_command=by_command)


def _with_unique_action(endpoint: Endpoint) -> Endpoint:
    return _replace_action(endpoint, f"{endpoint.action}-{endpoint.function_name.replace('_', '-')}")


def _replace_action(endpoint: Endpoint, action: str) -> Endpoint:
    return Endpoint(
        platform=endpoint.platform,
        source_file=endpoint.source_file,
        module_name=endpoint.module_name,
        class_name=endpoint.class_name,
        function_name=endpoint.function_name,
        target_id=endpoint.target_id,
        resource=endpoint.resource,
        action=action,
        parameters=endpoint.parameters,
        auth_profile=endpoint.auth_profile,
    )
