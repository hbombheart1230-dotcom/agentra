"""RF-031 reporter_analysis: optional decision-story / run-card writers and fail-soft evidence recorders (tmp only).

Same isolation as test_rf031_reporter_analysis_writers: day cache, strategy memory, evidence ledger, event log,
reports root and cwd all live under tmp_path; the AI review is disabled. Explicit raises keep the checks live
under ``python -O``.
"""
from __future__ import annotations

import json

import pytest

from libs.reporting import reporter_analysis as ra

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


def _run(tmp_path, ev, **kw):
    return ra.generate_reporter_analysis_report(ev, tmp_path / "reports" / "dev" / "analysis", day=DAY,
                                                reports_root=tmp_path / "reports", ai_review_enabled=False, **kw)


def _files(root):
    return {str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file()}


def test_story_and_run_card_writers_are_opt_in_and_stay_under_the_reports_root(env):
    tmp_path, ev = env
    _run(tmp_path, ev)
    base = _files(tmp_path)
    if any("/manual/" in f for f in base):
        raise AssertionError(sorted(f for f in base if "/manual/" in f))
    _run(tmp_path, ev, generate_decision_story=True, generate_run_cards=True)
    added = {f for f in _files(tmp_path) - base}
    if not added or not all(f.startswith("reports/dev/manual/") for f in added):
        raise AssertionError(sorted(added))
    if not any("decision_story" in f for f in added) or not any("run_cards" in f for f in added):
        raise AssertionError(sorted(added))


def test_evidence_recorders_are_fail_soft(env, monkeypatch):
    tmp_path, ev = env
    calls = []

    def boom(**kw):
        calls.append(kw.get("stage"))
        raise RuntimeError("recorder down")

    monkeypatch.setattr(ra, "record_raw_input", boom)
    monkeypatch.setattr(ra, "record_decision_bridge", boom)
    md, js, out = _run(tmp_path, ev)
    _eq(sorted(set(calls)), ["post_run_analysis"])
    _eq(len(calls), 2)                                                    # both recorders were attempted and swallowed
    if not md.exists() or not js.exists():
        raise AssertionError("reports must still be written")
    _eq(out["ai_review"]["status"], "disabled")
