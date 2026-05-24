from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "all-in-one"


def test_single_all_in_one_skill_exists_and_is_cli_backed():
    skill = SKILL_ROOT / "SKILL.md"
    references = SKILL_ROOT / "references"

    assert skill.exists()
    content = skill.read_text(encoding="utf-8")
    assert "name: all-in-one" in content
    assert "aione" in content
    assert "references/" in content
    assert "xhs" in content
    assert "weibo" in content
    assert "douyin" in content
    assert references.exists()

    for filename in (
        "auth.md",
        "xhs.md",
        "weibo.md",
        "douyin.md",
        "workflows.md",
    ):
        assert (references / filename).exists()


def test_no_split_platform_skills_remain():
    for platform in ("xhs", "weibo", "douyin"):
        assert not (ROOT / "skills" / platform / "SKILL.md").exists()


def test_unified_skill_references_document_real_cli_usage():
    references = SKILL_ROOT / "references"
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(references.glob("*.md"))
    )

    for platform in ("xhs", "weibo", "douyin"):
        assert f"aione auth {platform}" in combined
        assert f"aione {platform}" in combined
    assert "--output json" in combined
    assert "--dry-run" in combined
    assert "cookie" in combined.lower()
