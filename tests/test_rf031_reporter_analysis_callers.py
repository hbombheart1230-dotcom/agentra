"""RF-031 reporter_analysis caller side: Reporter agent + CLI, real writer chain, tmp-isolated.

Same isolation as test_rf031_reporter_analysis_writers.py (day-cache, strategy
memory, ledger, event log, reports root and cwd in tmp_path; AI review off).
Pins how callers surface the chain: ReporterOutput state, the CLI text/JSON
line and exit code, and OSError propagation to the caller.
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

from libs.agent.reporter import Reporter
from libs.agent.reporter_outputs import ReporterOutput

DAY = "2026-10-28"
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


@pytest.fixture()
def env(tmp_path, monkeypatch):
    for k, v in (("EVENT_LOG_DAY_CACHE_DIR", tmp_path / "cache"),
                 ("STRATEGY_MEMORY_PATH", tmp_path / "mem" / "sm.jsonl"),
                 ("STRATEGY_MEMORY_DAILY_DIR", tmp_path / "mem" / "daily"),
                 ("EVIDENCE_LEDGER_PATH", tmp_path / "ledger" / "ev.jsonl")):
        monkeypatch.setenv(k, str(v))
    monkeypatch.chdir(tmp_path)
    ev = tmp_path / "data" / "events.jsonl"
    ev.parent.mkdir()
    ev.write_text(json.dumps({"ts": DAY + "T01:00:00+00:00", "event": "x", "run_id": "r1", "payload": {}}) + "\n", encoding="utf-8")
    (tmp_path / "empty.env").write_text("", encoding="utf-8")
    return tmp_path, ev


def _cli():
    spec = importlib.util.spec_from_file_location("rf031_run_reporter_analysis_report", ROOT / "scripts" / "run_reporter_analysis_report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _kwargs(tmp_path, ev):
    return dict(event_log_path=ev, report_dir=tmp_path / "reports" / "dev" / "analysis", reports_root=tmp_path / "reports",
                day=DAY, ai_review_enabled=False)


def test_reporter_run_reporter_analysis_wraps_real_chain_into_output(env):
    tmp_path, ev = env
    out = Reporter().run(mode="reporter_analysis", **_kwargs(tmp_path, ev))
    if not isinstance(out, ReporterOutput):
        raise AssertionError(type(out))
    js = tmp_path / "reports/dev/analysis/reporter_analysis_2026-10-28.json"
    md = tmp_path / "reports/dev/analysis/reporter_analysis_2026-10-28.md"
    _eq(out.output_paths, {"md": str(md), "json": str(js)})
    _eq(out.report_type, "reporter_analysis")
    _eq(out.payload["day"], DAY)
    # reports_root is inferred as the nearest ancestor directory named "reports"
    _eq(out.summary_metadata["reporter_input"]["reports_root"], str(tmp_path / "reports"))
    _eq(sorted(out.payload["strategy_memory_record"]), sorted(json.loads(js.read_text(encoding="utf-8"))["strategy_memory_record"]))
    _eq(out.success, out.warnings == [])


def test_reporter_oserror_from_writer_propagates_to_caller(env, monkeypatch):
    tmp_path, ev = env
    orig = pathlib.Path.write_text

    def wt(self, *a, **kw):
        if self.name == "operator_summary.json":
            raise OSError("synthetic")
        return orig(self, *a, **kw)

    monkeypatch.setattr(pathlib.Path, "write_text", wt)
    with pytest.raises(OSError):
        Reporter().run(mode="reporter_analysis", **_kwargs(tmp_path, ev))
    if (tmp_path / "reports/dev/analysis/reporter_analysis_2026-10-28.json").exists():
        raise AssertionError("final json must not exist after an earlier writer failed")


def _argv(tmp_path, ev, *extra):
    return ["--event-log-path", str(ev), "--intents-path", str(tmp_path / "none.jsonl"), "--report-dir", str(tmp_path / "reports/dev/analysis"),
            "--reports-root", str(tmp_path / "reports"), "--env-path", str(tmp_path / "empty.env"), "--day", DAY, "--no-ai-review", *extra]


def test_cli_text_line_and_exit_code(env, capsys):
    tmp_path, ev = env
    rc = _cli().main(_argv(tmp_path, ev))
    _eq(rc, 0)
    line = capsys.readouterr().out.strip()
    for token in (f"day={DAY}", "intents_created=0", "intents_blocked=0", "incidents=0", "ai_review_status=disabled",
                  "reporter_analysis_2026-10-28.json", "reporter_analysis_2026-10-28.md"):
        if token not in line:
            raise AssertionError((token, line))


def test_cli_json_mode_prints_one_json_document_and_oserror_escapes(env, capsys, monkeypatch):
    tmp_path, ev = env
    _eq(_cli().main(_argv(tmp_path, ev, "--json")), 0)
    doc = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    _eq(doc["day"], DAY)
    orig = pathlib.Path.write_text

    def wt(self, *a, **kw):
        if self.name == "reporter_analysis_2026-10-28.md":
            raise OSError("synthetic")
        return orig(self, *a, **kw)

    monkeypatch.setattr(pathlib.Path, "write_text", wt)
    with pytest.raises(OSError):  # no try/except in main(): a writer failure is an uncaught exception, not an exit code
        _cli().main(_argv(tmp_path, ev))
