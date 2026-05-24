import json

from all_in_one.cli.auth import CookieStore
from all_in_one.cli.main import main


def test_auth_set_status_and_clear_cookie(tmp_path, capsys):
    store = CookieStore(tmp_path)

    assert main(["auth", "xhs", "set-cookie", "--profile", "creator", "--cookie", "sid=abc123"], store=store) == 0
    assert "abc123" not in capsys.readouterr().out

    assert main(["auth", "xhs", "status", "--profile", "creator"], store=store) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["platform"] == "xhs"
    assert status["profile"] == "creator"
    assert status["configured"] is True
    assert status["source"] == "saved"
    assert "cookie" not in status

    assert main(["auth", "xhs", "clear-cookie", "--profile", "creator"], store=store) == 0
    assert json.loads(capsys.readouterr().out)["cleared"] is True


def test_auth_set_cookie_file_missing_returns_validation_error(tmp_path, capsys):
    store = CookieStore(tmp_path)

    assert (
        main(
            [
                "auth",
                "douyin",
                "set-cookie",
                "--profile",
                "web",
                "--cookie-file",
                "missing-cookie.txt",
            ],
            store=store,
        )
        == 1
    )

    payload = json.loads(capsys.readouterr().err)
    assert payload["error"]["category"] == "VALIDATION_ERROR"
    assert "Cookie file not found" in payload["error"]["message"]
    assert "missing-cookie.txt" in payload["error"]["message"]


def test_platform_help_lists_command_groups(capsys):
    assert main(["xhs", "--help"]) == 0

    output = capsys.readouterr().out
    assert "note" in output
    assert "search" in output


def test_endpoint_help_lists_upstream_target_and_options(capsys):
    assert main(["xhs", "note", "search", "--help"]) == 0

    output = capsys.readouterr().out
    assert "search_note" in output
    assert "--query" in output
    assert "--cookies" in output


def test_dry_run_returns_mapped_upstream_target(capsys):
    assert (
        main(
            [
                "douyin",
                "work",
                "info",
                "--dry-run",
                "--url",
                "https://www.douyin.com/video/example",
            ]
        )
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["dry_run"] is True
    assert payload["platform"] == "douyin"
    assert payload["resource"] == "work"
    assert payload["action"] == "info"
    assert payload["auth_profile"] == "web"
    assert payload["target"]["function"] == "get_work_info"
    assert payload["arguments"]["url"] == "https://www.douyin.com/video/example"


def test_xhs_note_search_dry_run_matches_documented_command(capsys):
    assert (
        main(
            [
                "xhs",
                "note",
                "search",
                "--query",
                "coffee",
                "--page",
                "1",
                "--dry-run",
            ]
        )
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["target"]["function"] == "search_note"
    assert payload["arguments"]["query"] == "coffee"
    assert payload["arguments"]["page"] == "1"


def test_weibo_post_search_dry_run_matches_documented_command(capsys):
    assert (
        main(
            [
                "weibo",
                "post",
                "search",
                "--query",
                "AI",
                "--page",
                "1",
                "--dry-run",
            ]
        )
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["target"]["function"] == "searchSome"
    assert payload["arguments"]["query"] == "AI"
    assert payload["arguments"]["page"] == "1"


def test_endpoint_route_invokes_adapter_with_runtime_options(monkeypatch, capsys):
    def fake_invoke(endpoint, arguments, cookie=None, proxy=None, timeout=None):
        return {
            "function": endpoint.function_name,
            "arguments": arguments,
            "cookie": cookie.value,
            "cookie_source": cookie.source,
            "proxy": proxy,
            "timeout": timeout,
        }

    monkeypatch.setattr("all_in_one.cli.main.invoke_endpoint", fake_invoke)

    assert (
        main(
            [
                "douyin",
                "work",
                "info",
                "--url",
                "https://www.douyin.com/video/example",
                "--cookies",
                "sid=abc",
                "--proxy",
                "http://127.0.0.1:8080",
                "--timeout",
                "3",
            ]
        )
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["function"] == "get_work_info"
    assert payload["arguments"]["url"] == "https://www.douyin.com/video/example"
    assert payload["cookie"] == "sid=abc"
    assert payload["cookie_source"] == "cli"
    assert payload["proxy"] == "http://127.0.0.1:8080"
    assert payload["timeout"] == 3.0


def test_endpoint_route_uses_endpoint_auth_profile_for_saved_cookie(monkeypatch, tmp_path, capsys):
    store = CookieStore(tmp_path)
    store.save_cookie("xhs", "creator-cookie", profile="creator", source="test")

    def fake_invoke(endpoint, arguments, cookie=None, proxy=None, timeout=None):
        return {
            "profile": endpoint.auth_profile,
            "cookie": cookie.value,
            "cookie_profile": cookie.profile,
        }

    monkeypatch.setattr("all_in_one.cli.main.invoke_endpoint", fake_invoke)

    assert (
        main(
            [
                "xhs",
                "creator",
                "post-note",
                "--note-info",
                "{}",
            ],
            store=store,
        )
        == 0
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["profile"] == "creator"
    assert payload["cookie"] == "creator-cookie"
    assert payload["cookie_profile"] == "creator"


def test_auth_required_command_fails_before_upstream_invocation(monkeypatch, tmp_path, capsys):
    def should_not_invoke(*args, **kwargs):
        raise AssertionError("upstream adapter should not be called without cookies")

    monkeypatch.setattr("all_in_one.cli.main.invoke_endpoint", should_not_invoke)

    assert (
        main(
            [
                "douyin",
                "work",
                "info",
                "--url",
                "https://www.douyin.com/video/example",
            ],
            store=CookieStore(tmp_path),
        )
        == 1
    )

    payload = json.loads(capsys.readouterr().err)
    assert payload["error"]["category"] == "AUTH_MISSING"
    assert payload["error"]["auth_profile"] == "web"
    assert "set-cookie" in payload["error"]["message"]


def test_verbose_flag_writes_debug_context_to_stderr(monkeypatch, capsys):
    def fake_invoke(endpoint, arguments, cookie=None, proxy=None, timeout=None):
        return {"ok": True}

    monkeypatch.setattr("all_in_one.cli.main.invoke_endpoint", fake_invoke)

    assert (
        main(
            [
                "douyin",
                "work",
                "info",
                "--url",
                "https://www.douyin.com/video/example",
                "--cookies",
                "sid=secret123",
                "--verbose",
            ]
        )
        == 0
    )

    captured = capsys.readouterr()
    assert "[aione]" in captured.err
    assert "douyin_api" in captured.err
    assert "get_work_info" in captured.err
    assert "cookie_source: cli" in captured.err
    assert "secret123" not in captured.err
