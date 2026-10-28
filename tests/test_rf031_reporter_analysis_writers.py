"""RF-031 libs/reporting reporter_analysis: real writer chain, tmp-isolated.

Runs the real ``generate_reporter_analysis_report`` (not stubbed) with the
day-cache, strategy memory, evidence ledger, event log, reports root and cwd all
redirected to ``tmp_path``; the AI review is disabled so no LLM is called.
Pins (a) the set of files the chain writes, (b) which writer failures propagate
as OSError and which are fail-soft today, (c) nothing is written outside tmp.
Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from libs.reporting.reporter_analysis import generate_reporter_analysis_report

DAY = "2026-10-28"


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
    return tmp_path, ev


def _run(tmp_path, ev):
    return generate_reporter_analysis_report(ev, tmp_path / "reports" / "dev" / "analysis", day=DAY,
                                             reports_root=tmp_path / "reports", ai_review_enabled=False)


def _files(root):
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())


def test_normal_run_writes_expected_files_only_under_tmp(env):
    tmp_path, ev = env
    md, js, out = _run(tmp_path, ev)
    files = _files(tmp_path)
    cache = [f for f in files if f.startswith("cache/")]
    _eq(sorted(c.split(".")[-1] for c in cache), ["json", "jsonl"])  # events_<day>_<hash>.{jsonl,meta.json}
    rest = [f for f in files if not f.startswith("cache/")]
    _eq(rest, [
        "data/events.jsonl",
        "ledger/ev.jsonl",
        "mem/daily/2026-10-28.json",
        "mem/sm.jsonl",
        "reports/dev/analysis/reporter_analysis_2026-10-28.json",
        "reports/dev/analysis/reporter_analysis_2026-10-28.md",
        "reports/dev/analysis/trade_explain/trade_explain_2026-10-28.json",
        "reports/dev/analysis/trade_explain/trade_explain_2026-10-28.md",
        "reports/metrics/metrics_2026-10-28.json",
        "reports/metrics/metrics_2026-10-28.md",
        "reports/operator_summary/daily/2026-10-28/operator_summary.json",
        "reports/operator_summary/daily/2026-10-28/operator_summary.md",
    ])
    _eq((md, js), (tmp_path / "reports/dev/analysis/reporter_analysis_2026-10-28.md",
                   tmp_path / "reports/dev/analysis/reporter_analysis_2026-10-28.json"))
    _eq(json.loads(js.read_text(encoding="utf-8"))["strategy_memory_record"]["strategy_memory_path"], str(tmp_path / "mem" / "sm.jsonl"))
    _eq(out["ai_review"]["status"], "disabled")
    _eq(pathlib.Path.cwd(), tmp_path)


def _fail_on(monkeypatch, suffix):
    orig = pathlib.Path.write_text
    hits = []

    def wt(self, *a, **kw):
        if not hits and str(self).replace("\\", "/").endswith(suffix):
            hits.append(str(self))
            raise OSError("synthetic write failure")
        return orig(self, *a, **kw)

    monkeypatch.setattr(pathlib.Path, "write_text", wt)
    return hits


@pytest.mark.parametrize("suffix", [
    ".meta.json",
    "trade_explain/trade_explain_2026-10-28.json",
    "trade_explain/trade_explain_2026-10-28.md",
    "operator_summary/daily/2026-10-28/operator_summary.json",
    "operator_summary/daily/2026-10-28/operator_summary.md",
    "analysis/reporter_analysis_2026-10-28.json",
    "analysis/reporter_analysis_2026-10-28.md",
])
def test_these_writer_failures_propagate_as_oserror(env, monkeypatch, suffix):
    tmp_path, ev = env
    hits = _fail_on(monkeypatch, suffix)
    with pytest.raises(OSError):
        _run(tmp_path, ev)
    _eq(len(hits), 1)
    if suffix.endswith("reporter_analysis_2026-10-28.md"):
        # the final JSON was already written before the final .md write failed (partial output)
        if not (tmp_path / "reports/dev/analysis/reporter_analysis_2026-10-28.json").exists():
            raise AssertionError("expected partial JSON before the .md failure")
    if suffix.endswith("reporter_analysis_2026-10-28.json"):
        if (tmp_path / "reports/dev/analysis/reporter_analysis_2026-10-28.md").exists():
            raise AssertionError("md must not exist when the json write failed first")


@pytest.mark.parametrize("suffix", [
    "metrics/metrics_2026-10-28.md",
    "metrics/metrics_2026-10-28.json",
    "mem/daily/2026-10-28.json",
])
def test_these_writer_failures_are_fail_soft_today(env, monkeypatch, suffix):
    tmp_path, ev = env
    hits = _fail_on(monkeypatch, suffix)
    md, js, out = _run(tmp_path, ev)
    _eq(len(hits), 1)
    if not (md.exists() and js.exists()):
        raise AssertionError("final reporter_analysis outputs must still be written")
    if suffix.startswith("mem/"):
        if "daily_summary_path" not in out["strategy_memory_record"] and "error" not in out["strategy_memory_record"]:
            raise AssertionError(out["strategy_memory_record"])
