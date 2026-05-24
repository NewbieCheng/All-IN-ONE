import runpy
import sys


def test_python_m_aione_runs_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["aione", "--help"])

    try:
        runpy.run_module("aione", run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 0

    assert "usage: aione" in capsys.readouterr().out


def test_root_main_py_runs_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["main.py", "--help"])

    try:
        runpy.run_path("main.py", run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 0

    assert "usage: aione" in capsys.readouterr().out

