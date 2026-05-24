import importlib
from pathlib import Path

from all_in_one.platforms.discovery import discover_endpoints

ROOT = Path(__file__).resolve().parents[1]
UPSTREAMS = ROOT / "upstreams"


def test_mapping_covers_all_discovered_endpoints():
    for platform in ("xhs", "weibo", "douyin"):
        mapping_module = importlib.import_module(
            f"all_in_one.platforms.{platform}.mapping"
        )
        mapping = mapping_module.build_mapping(UPSTREAMS)
        endpoints = discover_endpoints(platform, UPSTREAMS)

        assert len(mapping) == len(endpoints), (
            f"{platform}: mapping has {len(mapping)} entries "
            f"but discovery found {len(endpoints)} endpoints"
        )


def test_mapping_entries_contain_required_fields():
    for platform in ("xhs", "weibo", "douyin"):
        mapping_module = importlib.import_module(
            f"all_in_one.platforms.{platform}.mapping"
        )
        mapping = mapping_module.build_mapping(UPSTREAMS)

        for key, info in mapping.items():
            assert len(key) == 2, f"key should be (resource, action): {key}"
            assert "module" in info
            assert "function" in info
            assert "auth_profile" in info
            assert "source" in info
