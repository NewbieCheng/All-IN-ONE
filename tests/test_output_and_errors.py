import json

import pytest

from all_in_one.cli.errors import CLIError, ErrorCategory, error_payload
from all_in_one.cli.output import format_output, write_output


def test_json_output_is_default():
    rendered = format_output({"ok": True, "items": [1]}, output="json")

    assert json.loads(rendered) == {"ok": True, "items": [1]}


def test_pretty_output_is_human_readable():
    rendered = format_output({"ok": True, "count": 2}, output="pretty")

    assert "ok: True" in rendered
    assert "count: 2" in rendered


def test_file_output_writes_json(tmp_path):
    target = tmp_path / "result.json"

    rendered = write_output({"ok": True}, output="file", path=target)

    assert rendered == str(target)
    assert json.loads(target.read_text(encoding="utf-8")) == {"ok": True}


def test_structured_error_payload_redacts_cookie_values():
    error = CLIError(
        ErrorCategory.AUTH_EXPIRED,
        "Cookie sid=abc123456789 is expired",
        platform="xhs",
        cookie_source="saved",
    )

    payload = error_payload(error)

    assert payload["error"]["category"] == "AUTH_EXPIRED"
    assert payload["error"]["platform"] == "xhs"
    assert payload["error"]["cookie_source"] == "saved"
    assert payload["error"]["cleanup_command"] == "aione auth xhs clear-cookie"
    assert "abc123456789" not in payload["error"]["message"]


def test_file_output_requires_path():
    with pytest.raises(CLIError) as exc_info:
        write_output({"ok": True}, output="file")

    assert exc_info.value.category == ErrorCategory.OUTPUT_ERROR

