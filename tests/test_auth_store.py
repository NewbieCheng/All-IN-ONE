import json
from pathlib import Path

from all_in_one.cli.auth import CookieStore, redact_cookie, resolve_cookie


def test_resolve_cookie_prefers_cli_over_env_and_saved(tmp_path, monkeypatch):
    store = CookieStore(tmp_path)
    store.save_cookie("xhs", "saved-cookie", profile="pc", source="test")
    monkeypatch.setenv("AIONE_XHS_PC_COOKIES", "env-cookie")

    resolved = resolve_cookie("xhs", profile="pc", cli_cookie="cli-cookie", store=store)

    assert resolved.value == "cli-cookie"
    assert resolved.source == "cli"
    assert resolved.profile == "pc"


def test_resolve_cookie_prefers_env_over_saved(tmp_path, monkeypatch):
    store = CookieStore(tmp_path)
    store.save_cookie("weibo", "saved-cookie", profile="web", source="test")
    monkeypatch.setenv("AIONE_WEIBO_WEB_COOKIES", "env-cookie")

    resolved = resolve_cookie("weibo", profile="web", store=store)

    assert resolved.value == "env-cookie"
    assert resolved.source == "env"
    assert resolved.profile == "web"


def test_saved_cookie_has_metadata_and_can_be_cleared(tmp_path):
    store = CookieStore(tmp_path)

    store.save_cookie("douyin", "sid=abc; uid=123", profile="live", source="cli")
    cookie_file = Path(tmp_path) / "douyin" / "live.json"

    payload = json.loads(cookie_file.read_text(encoding="utf-8"))
    assert payload["platform"] == "douyin"
    assert payload["profile"] == "live"
    assert payload["cookie"] == "sid=abc; uid=123"
    assert payload["source"] == "cli"
    assert payload["created_at"]
    assert payload["updated_at"]

    loaded = store.load_cookie("douyin", profile="live")
    assert loaded.value == "sid=abc; uid=123"
    assert loaded.source == "saved"
    assert loaded.profile == "live"

    assert store.clear_cookie("douyin", profile="live") is True
    assert store.load_cookie("douyin", profile="live") is None
    assert store.clear_cookie("douyin", profile="live") is False


def test_profile_specific_env_does_not_fall_back_to_generic_for_special_profiles(tmp_path, monkeypatch):
    store = CookieStore(tmp_path)
    store.save_cookie("xhs", "creator-saved", profile="creator", source="test")
    monkeypatch.setenv("AIONE_XHS_COOKIES", "generic-cookie")

    resolved = resolve_cookie("xhs", profile="creator", store=store)

    assert resolved.value == "creator-saved"
    assert resolved.source == "saved"


def test_redact_cookie_masks_cookie_like_values():
    text = "request cookie sid=abc123456789; uid=42 with xsec_token=secret-token-value"

    redacted = redact_cookie(text)

    assert "abc123456789" not in redacted
    assert "secret-token-value" not in redacted
    assert "sid=<redacted>" in redacted
    assert "xsec_token=<redacted>" in redacted

