import json
import os

import pytest

from all_in_one.cli.auth import CookieStore
from all_in_one.cli.main import main

SKIP_XHS = not os.environ.get("AIONE_XHS_COOKIES")
SKIP_WEIBO = not os.environ.get("AIONE_WEIBO_COOKIES")
SKIP_DOUYIN = not os.environ.get("AIONE_DOUYIN_COOKIES")


@pytest.mark.integration
@pytest.mark.skipif(SKIP_XHS, reason="AIONE_XHS_COOKIES not set")
def test_xhs_user_self_info_smoke(capsys):
    assert main(["xhs", "user", "self-info", "--output", "json"]) == 0
    output = capsys.readouterr().out
    data = json.loads(output)
    assert data is not None


@pytest.mark.integration
@pytest.mark.skipif(SKIP_WEIBO, reason="AIONE_WEIBO_COOKIES not set")
def test_weibo_self_info_smoke(capsys):
    assert main(["weibo", "info", "self", "--output", "json"]) == 0
    output = capsys.readouterr().out
    data = json.loads(output)
    assert data is not None


@pytest.mark.integration
@pytest.mark.skipif(SKIP_DOUYIN, reason="AIONE_DOUYIN_COOKIES not set")
def test_douyin_device_id_smoke(capsys):
    assert main(["douyin", "device", "id", "--output", "json"]) == 0
    output = capsys.readouterr().out
    data = json.loads(output)
    assert data is not None
