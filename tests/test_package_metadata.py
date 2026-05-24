from importlib.metadata import entry_points


def test_aione_console_script_is_registered():
    discovered = entry_points()
    if hasattr(discovered, "select"):
        scripts = discovered.select(group="console_scripts")
    else:
        scripts = discovered.get("console_scripts", [])
    assert any(
        ep.name == "aione" and ep.value == "all_in_one.cli.main:main"
        for ep in scripts
    )

