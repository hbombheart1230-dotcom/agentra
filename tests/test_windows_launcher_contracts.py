"""Source-only launcher graph checks: no PowerShell, batch, scheduler or trading execution."""
from __future__ import annotations

import importlib.util
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "scripts/diagnostics/audit_windows_launchers.py"
SPEC = importlib.util.spec_from_file_location("windows_launcher_auditor", TOOL)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_bound_sibling_and_cwd_contracts(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "run_child.py").write_text("raise RuntimeError('never import or execute')\n")
    (scripts / "start.bat").write_text(
        '@echo off\nset "CHILD=%~dp0run_child.py"\npushd "%~dp0.."\ncall "%CHILD%" %*\n'
    )
    result = MOD.audit(tmp_path, expected_count=1)
    assert result["ok"]
    record = result["launchers"][0]
    assert record["cwd_contract"][0]["line"] == 3
    assert any(e["kind"] == "bound_variable_dispatch" and e["target"] == "scripts/run_child.py"
               for e in record["references"])


def test_missing_explicit_target_fails_closed(tmp_path: Path) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/broken.ps1").write_text('& python "scripts/missing.py"\n')
    result = MOD.audit(tmp_path)
    assert not result["ok"]
    assert "missing launcher target scripts/missing.py" in result["issues"][0]


def test_count_and_scheduler_asymmetry_are_explicit(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "register.bat").write_text('schtasks /Create /TN "Mock-Q12" /TR "python -V"\n')
    result = MOD.audit(tmp_path, expected_count=2)
    assert not result["ok"]
    assert "count mismatch" in result["issues"][0]
    assert result["unmatched_task_creates"] == ["Mock-Q12"]


def test_source_only_never_runs_live_launcher(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "live.ps1").write_text("throw 'must never execute'\nStart-Process broker.exe\n")
    result = MOD.audit(tmp_path, expected_count=1)
    assert result["ok"]
    assert result["launchers"][0]["dispatch_commands"]


def test_quoted_batch_python_is_a_direct_dispatch(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "run_session.py").write_text("raise RuntimeError('do not execute')\n")
    (scripts / "run.bat").write_text('"%PY%" "%ROOT%\\scripts\\run_session.py" --mode live %*\n')
    record = MOD.audit(tmp_path, expected_count=1)["launchers"][0]
    assert record["references"][0]["kind"] == "direct_dispatch"
    assert record["dispatch_commands"][0]["line"] == 1
