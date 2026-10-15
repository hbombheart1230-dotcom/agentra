"""Issue #8 held-entrypoint checks: isolated inputs, no production commands."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]


def test_empty_research_pipeline_writes_only_isolated_outputs(tmp_path):
    from libs.research.opening_rank1_deep_dive.pipeline import run_opening_rank1_deep_dive
    evidence = tmp_path / "evidence.json"
    evidence.write_text('{"episodes": []}', encoding="utf-8")
    outputs = run_opening_rank1_deep_dive(
        evidence_path=evidence, reports_root=tmp_path / "reports",
        macro_logs_root=tmp_path / "macro", metadata_path=tmp_path / "metadata.json",
        minute_cache_root=tmp_path / "minutes", output_root=tmp_path / "out",
    )
    payload = json.loads(Path(outputs["json"]).read_text(encoding="utf-8"))
    assert payload["coverage"]["case_count"] == 0
    assert payload["cases"] == []
    assert payload["analysis"]["outlier_sensitivity"]["contribution"]["top1_return_pct"] is None
    assert set(outputs) == {"json", "csv", "markdown"}
    assert all(Path(p).is_relative_to(tmp_path / "out") and Path(p).is_file() for p in outputs.values())


def test_nonempty_research_contribution_unchanged():
    from libs.research.opening_rank1_deep_dive.analysis import outlier_sensitivity
    result = outlier_sensitivity([{"net_return_30m_pct": 2.0}, {"net_return_30m_pct": -1.0}])
    assert result["contribution"]["top1_return_pct"] == 2.0
    assert result["contribution"]["total_net_return_sum_pct"] == 1.0


def _pytest_runner(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location("issue8_pytest_runner", REPO / "scripts/run_pytest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.__file__ = str(tmp_path / "scripts/run_pytest.py")
    executable = tmp_path / "venv/Scripts/python.exe"
    executable.parent.mkdir(parents=True)
    executable.touch()  # existence contract only; never execute this fixture
    calls = []
    def capture(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return SimpleNamespace(returncode=7)
    monkeypatch.setattr(module.subprocess, "run", capture)
    return module, executable, calls


def test_windows_pytest_runner_forwards_argv_cwd_and_exit(monkeypatch, tmp_path):
    module, executable, calls = _pytest_runner(monkeypatch, tmp_path)
    assert module.main(["tests/test sample.py", "-k", "small or fast"]) == 7
    assert calls == [([str(executable), "-m", "pytest", "tests/test sample.py", "-k", "small or fast"], {"cwd": tmp_path})]


@pytest.mark.parametrize("args", [["--basetemp", "unsafe"], ["--basetemp=unsafe"]])
def test_windows_pytest_runner_rejects_temp_override(monkeypatch, tmp_path, args):
    module, _, calls = _pytest_runner(monkeypatch, tmp_path)
    with pytest.raises(SystemExit, match="Do not pass --basetemp"):
        module.main(args)
    assert calls == []


def test_windows_pytest_runner_missing_venv_fails_closed(monkeypatch, tmp_path):
    module, executable, calls = _pytest_runner(monkeypatch, tmp_path)
    executable.unlink()
    with pytest.raises(FileNotFoundError, match="Python executable not found"):
        module.main([])
    assert calls == []


def test_historical_cli_without_evidence_is_no_write_and_not_authority(tmp_path):
    empty_repo = tmp_path / "empty-repo"
    empty_repo.mkdir()
    command = [sys.executable, str(REPO / "scripts/run_uef5_historical_recompute.py"),
               "--repo-root", str(empty_repo), "--no-write"]
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    # The existing engine calls an empty workload COMPLETE; this is NOT evidence acceptance.
    assert summary["status"] == "COMPLETE"
    for key in ("discovered_source_artifacts", "records_considered", "recomputed"):
        assert summary["totals"][key] == 0
    assert all(family["admissible_units"] == 0 for family in summary["families"])
    assert list(empty_repo.rglob("*")) == []
    assert "outputs:" not in result.stderr
