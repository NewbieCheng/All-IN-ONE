from pathlib import Path

import pytest

from all_in_one.cli.auth import CookieResolution
from all_in_one.cli.errors import CLIError, ErrorCategory
from all_in_one.platforms.discovery import Endpoint
from all_in_one.platforms.invoke import invoke_endpoint


def test_invoke_class_method_injects_cookie_proxy_and_coerces_types(tmp_path):
    source = tmp_path / "fake_api.py"
    source.write_text(
        "\n".join(
            [
                "class FakeApi:",
                "    def search(self, query: str, limit: int, cookies_str, proxies=None):",
                "        return {",
                "            'query': query,",
                "            'limit': limit,",
                "            'limit_type': type(limit).__name__,",
                "            'cookie': cookies_str,",
                "            'proxies': proxies,",
                "        }",
            ]
        ),
        encoding="utf-8",
    )
    endpoint = Endpoint(
        platform="xhs",
        source_file=source,
        module_name="fake_api",
        class_name="FakeApi",
        function_name="search",
        target_id="fake_api.py:FakeApi.search",
        resource="note",
        action="search",
        parameters=("query", "limit", "cookies_str", "proxies"),
        auth_profile="pc",
    )

    result = invoke_endpoint(
        endpoint,
        arguments={"query": "coffee", "limit": "2"},
        cookie=CookieResolution("xhs", "sid=abc", "cli"),
        proxy="http://127.0.0.1:8080",
    )

    assert result["query"] == "coffee"
    assert result["limit"] == 2
    assert result["limit_type"] == "int"
    assert result["cookie"] == "sid=abc"
    assert result["proxies"] == {
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080",
    }


def test_invoke_module_function(tmp_path):
    source = tmp_path / "fake_api.py"
    source.write_text("def ping(name: str):\n    return {'hello': name}\n", encoding="utf-8")
    endpoint = Endpoint(
        platform="weibo",
        source_file=source,
        module_name="fake_api",
        class_name=None,
        function_name="ping",
        target_id="fake_api.py:ping",
        resource="api",
        action="ping",
        parameters=("name",),
        auth_profile="web",
    )

    assert invoke_endpoint(endpoint, arguments={"name": "world"}) == {"hello": "world"}


def test_invoke_auth_required_without_cookie_raises_auth_missing(tmp_path):
    source = tmp_path / "fake_api.py"
    source.write_text(
        "def needs_auth(auth, url):\n    return {'url': url}\n",
        encoding="utf-8",
    )
    endpoint = Endpoint(
        platform="douyin",
        source_file=source,
        module_name="fake_api",
        class_name=None,
        function_name="needs_auth",
        target_id="fake_api.py:needs_auth",
        resource="work",
        action="info",
        parameters=("auth", "url"),
        auth_profile="web",
    )

    with pytest.raises(CLIError) as exc_info:
        invoke_endpoint(endpoint, arguments={"url": "https://example.test"})

    assert exc_info.value.category == ErrorCategory.AUTH_MISSING
    assert exc_info.value.platform == "douyin"


def test_douyin_auth_parameter_receives_auth_object(tmp_path):
    source = tmp_path / "fake_douyin.py"
    source.write_text(
        "\n".join(
            [
                "def needs_auth(auth, url):",
                "    return {",
                "        'url': url,",
                "        'cookie_str': auth.cookie_str,",
                "        'msToken': auth.msToken,",
                "        'cookie': auth.cookie,",
                "    }",
            ]
        ),
        encoding="utf-8",
    )
    endpoint = Endpoint(
        platform="douyin",
        source_file=source,
        module_name="fake_douyin",
        class_name=None,
        function_name="needs_auth",
        target_id="fake_douyin.py:needs_auth",
        resource="work",
        action="info",
        parameters=("auth", "url"),
        auth_profile="web",
    )

    result = invoke_endpoint(
        endpoint,
        arguments={"url": "https://example.test"},
        cookie=CookieResolution("douyin", "sid=abc; msToken=tok", "cli", "web"),
    )

    assert result["cookie_str"]
    assert result["msToken"] == "tok"
    assert result["cookie"]["sid"] == "abc"
