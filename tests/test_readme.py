from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_root_main_and_readme_exist():
    assert (ROOT / "main.py").exists()
    assert (ROOT / "README.md").exists()


def test_readme_documents_cli_auth_upstreams_and_real_tests():
    content = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "aione" in content
    assert "python main.py" in content
    assert "upstreams/" in content
    assert "AIONE_XHS_COOKIES" in content
    assert "真实接口测试" in content
    assert "cookie" in content.lower()
