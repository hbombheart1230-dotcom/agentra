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


def _tasks(tmp_path, create_prefix, delete_prefix, create='%TASK_PREFIX%-Q12-Preopen', delete='%TASK_PREFIX%-Q12-Preopen'):
    scripts = tmp_path / 'scripts'
    scripts.mkdir()
    for name, prefix, action, task in (
        ('register_mock_exam_tasks_example.bat', create_prefix, 'Create', create),
        ('unregister_mock_exam_tasks_example.bat', delete_prefix, 'Delete', delete),
    ):
        (scripts / name).write_text(prefix + f'\nschtasks /{action} /TN "{task}"\nexit /b 0\n')
    return MOD.audit(tmp_path)


def test_literal_prefix_resolves_and_matching_delete_has_no_mismatch(tmp_path):
    result = _tasks(tmp_path, 'set "TASK_PREFIX=Literal"', 'set "TASK_PREFIX=Literal"')
    assert result['tasks'][0]['task'] == '%TASK_PREFIX%-Q12-Preopen'
    assert result['tasks'][0]['resolved_task'] == 'Literal-Q12-Preopen'
    assert result['tasks'][0]['resolution'] == 'PREFIX_RESOLVED'
    assert result['unmatched_task_creates_resolved'] == []
    assert result['unmatched_task_deletes_resolved'] == []


def test_literal_task_names_match(tmp_path):
    result = _tasks(tmp_path, '', '', 'Literal-Task', 'Literal-Task')
    assert all(t['resolution'] == 'LITERAL' for t in result['tasks'])
    assert result['unmatched_task_creates_resolved'] == []


def test_undefined_dynamic_and_reassigned_prefixes_fail_closed(tmp_path):
    for index, assignment in enumerate(('', 'set "TASK_PREFIX=%HOST_PREFIX%"',
            'set "TASK_PREFIX=Literal"\nset "TASK_PREFIX=%HOST_PREFIX%"')):
        root = tmp_path / str(index)
        root.mkdir()
        result = _tasks(root, assignment, assignment)
        assert len(result['unresolved_tasks']) == 2
        assert result['unmatched_task_creates_resolved'] == []
        assert result['mockexam_task_contract']['status'] == 'UNPROVEN'
        MOD.assert_mockexam_known_contract(result)
        assert not result['ok']


def test_per_file_prefixes_not_unified(tmp_path):
    result = _tasks(tmp_path, 'set "TASK_PREFIX=First"', 'set "TASK_PREFIX=Second"')
    assert result['unmatched_task_creates_resolved'] == ['First-Q12-Preopen']
    assert result['unmatched_task_deletes_resolved'] == ['Second-Q12-Preopen']


def test_prefix_after_use_does_not_resolve_earlier_task(tmp_path):
    result = _tasks(tmp_path, '', 'set "TASK_PREFIX=Late"')
    path = tmp_path / 'scripts/register_mock_exam_tasks_example.bat'
    path.write_text(path.read_text() + 'set "TASK_PREFIX=Late"\n')
    result = MOD.audit(tmp_path)
    assert result['tasks'][0]['resolution'] == 'UNRESOLVED'


def test_static_tasks_never_execute_and_missing_contract_fails(tmp_path, monkeypatch):
    import subprocess
    def forbidden(*args, **kwargs):
        raise AssertionError('shell execution forbidden')
    monkeypatch.setattr(subprocess, 'run', forbidden)
    result = _tasks(tmp_path, 'set "TASK_PREFIX=Literal"', 'set "TASK_PREFIX=Literal"')
    assert result['ok']  # exit /b 0 is source text only
    MOD.assert_mockexam_known_contract(result)
    assert not result['ok']  # changed names are not the frozen baseline
    (tmp_path / 'scripts/unregister_mock_exam_tasks_example.bat').unlink()
    result = MOD.audit(tmp_path)
    MOD.assert_mockexam_known_contract(result)
    assert not result['ok']


def test_frozen_mockexam_baseline_and_added_task_rejected(tmp_path):
    scripts = tmp_path / 'scripts'
    scripts.mkdir()
    for filename, action, names in (
        ('register_mock_exam_tasks_example.bat', 'Create', MOD._FROZEN_REGISTERED),
        ('unregister_mock_exam_tasks_example.bat', 'Delete', MOD._FROZEN_UNREGISTERED),
    ):
        (scripts / filename).write_text('\n'.join(f'schtasks /{action} /TN "{name}"' for name in sorted(names)))
    result = MOD.audit(tmp_path)
    MOD.assert_mockexam_known_contract(result)
    assert result['ok']
    assert len(result['mockexam_task_contract']['unmatched']) == 2
    path = scripts / 'register_mock_exam_tasks_example.bat'
    path.write_text(path.read_text() + '\nschtasks /Create /TN "Unexpected"\n')
    result = MOD.audit(tmp_path)
    MOD.assert_mockexam_known_contract(result)
    assert not result['ok']
