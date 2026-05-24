import ast
from pathlib import Path

from all_in_one.platforms.discovery import discover_endpoints, scoped_source_files
from all_in_one.platforms.registry import build_registry


ROOT = Path(__file__).resolve().parents[1]
UPSTREAMS = ROOT / "upstreams"


def test_scoped_source_files_match_project_scope():
    xhs_files = {path.name for path in scoped_source_files("xhs", UPSTREAMS)}
    weibo_files = {path.name for path in scoped_source_files("weibo", UPSTREAMS)}
    douyin_files = {path.name for path in scoped_source_files("douyin", UPSTREAMS)}

    assert xhs_files == {
        "xhs_pc_apis.py",
        "xhs_pc_login_apis.py",
        "xhs_creator_apis.py",
        "xhs_creator_login_apis.py",
        "xhs_pugongying_apis.py",
        "xhs_qianfan_apis.py",
    }
    assert weibo_files == {
        "weibo_apis.py",
        "weibo_creator_apis.py",
        "weibo_mobile_apis.py",
    }
    assert douyin_files == {"douyin_api.py"}


def test_discovery_covers_every_public_scoped_endpoint():
    for platform in ("xhs", "weibo", "douyin"):
        expected = _public_targets(platform)
        discovered = {endpoint.target_id for endpoint in discover_endpoints(platform, UPSTREAMS)}

        assert expected
        assert expected <= discovered


def test_registry_assigns_stable_human_commands_for_common_endpoints():
    registry = build_registry(UPSTREAMS)

    assert registry.by_command[("xhs", "note", "search")].function_name == "search_note"
    assert registry.by_command[("weibo", "user", "info")].function_name == "getUserInfo"
    assert registry.by_command[("douyin", "work", "info")].function_name == "get_work_info"


def test_registry_assigns_auth_profiles_from_upstream_domain():
    registry = build_registry(UPSTREAMS)

    assert registry.by_command[("xhs", "note", "search")].auth_profile == "pc"
    assert registry.by_command[("xhs", "creator", "post-note")].auth_profile == "creator"
    assert registry.by_command[("xhs", "pugongying", "user-by-page")].auth_profile == "pugongying"
    assert registry.by_command[("weibo", "post", "search")].auth_profile == "web"
    assert registry.by_command[("weibo", "mobile", "search")].auth_profile == "mobile"
    assert registry.by_command[("douyin", "work", "info")].auth_profile == "web"
    assert registry.by_command[("douyin", "live", "search")].auth_profile == "live"


def test_secondary_domain_commands_have_clean_names():
    registry = build_registry(UPSTREAMS)

    assert registry.by_command[("xhs", "pc-login", "qrcode-login")].function_name == "qrcode_login"
    assert registry.by_command[("xhs", "creator-login", "qrcode-login")].function_name == "qrcode_login"
    assert registry.by_command[("xhs", "qianfan", "all-categories")].function_name == "get_all_categories"
    assert registry.by_command[("xhs", "pugongying", "all-categories")].function_name == "get_all_categories"
    assert registry.by_command[("weibo", "mobile", "work-info")].function_name == "getWorkInfo"


def test_primary_module_commands_unchanged_after_domain_mapping():
    registry = build_registry(UPSTREAMS)

    assert registry.by_command[("xhs", "user", "info")].module_name == "xhs_pc_apis"
    assert registry.by_command[("xhs", "note", "search")].module_name == "xhs_pc_apis"
    assert registry.by_command[("weibo", "work", "info")].module_name == "weibo_apis"
    assert registry.by_command[("douyin", "user", "info")].module_name == "douyin_api"


def test_no_ugly_collision_suffixes_in_registry():
    registry = build_registry(UPSTREAMS)

    for key, endpoint in registry.by_command.items():
        action = key[2]
        func_slug = endpoint.function_name.replace("_", "-").lower()
        assert not action.endswith(f"-{func_slug}") or action == func_slug, (
            f"Collision suffix detected in {key}: action '{action}' "
            f"ends with function name '{func_slug}'"
        )


def test_registry_has_no_command_collisions():
    registry = build_registry(UPSTREAMS)

    assert len(registry.by_command) == len(registry.endpoints)


def _public_targets(platform):
    targets = set()
    for source_file in scoped_source_files(platform, UPSTREAMS):
        tree = ast.parse(source_file.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    targets.add(f"{source_file.name}:{node.name}")
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if child.name != "__init__" and not child.name.startswith("_"):
                            targets.add(f"{source_file.name}:{node.name}.{child.name}")
    return targets
