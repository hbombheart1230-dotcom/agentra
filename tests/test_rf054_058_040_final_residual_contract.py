"""RF-054/058/040 final residual branches: pure parser, tmp reports root, tmp state file. No broker, no operational path."""
from __future__ import annotations

import json
import os
from datetime import date

import pytest

from libs.agent.intent_parser import parse_nl
from libs.performance import strategy_memory as sm
from libs.performance.performance_aggregator import performance_artifact_paths
from libs.storage.state_store import StateStore


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_parse_nl_market_limit_precedence_and_default_order_type():
    mkt = parse_nl("005930 10주 시장가 매수")
    _eq((mkt.action, mkt.order_type, mkt.qty), ("BUY", "market", 10))
    _eq(parse_nl("buy 005930 qty 3 market").order_type, "market")
    both = parse_nl("005930 매도 100주 시장가 지정가 70000원")
    _eq((both.action, both.order_type, both.price), ("SELL", "limit", 70000))     # limit keyword wins over market
    _eq(parse_nl("005930 매수").order_type, "market")                             # default when no keyword
    unknown = parse_nl("지정가 안내")
    _eq((unknown.action, unknown.order_type), ("UNKNOWN", "limit"))               # order_type is kept for UNKNOWN


def test_pattern_stats_skips_blank_names_and_non_dict_payloads():
    out = sm._pattern_stats({"": {"x": 1}, "  ": {}, "a": "junk", "b": {"trade_count": 2}}, limit=5)
    text = json.dumps(out, ensure_ascii=False, default=str)
    for name in ('"a"', '"b"'):
        if name not in text:
            raise AssertionError((name, text))
    if '"  "' in text:
        raise AssertionError(text)


def _memory(root, day, **body):
    path = performance_artifact_paths(root, day)["strategy_memory_json"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body), encoding="utf-8")


def test_resolve_latest_day_helpers_with_missing_root_and_non_date_dirs(tmp_path):
    missing = tmp_path / "nope"
    _eq(sm._resolve_latest_day(missing), "")
    _eq(sm._resolve_latest_usable_day(missing), "")
    perf = tmp_path / "performance"
    (perf / "not-a-day").mkdir(parents=True)
    (perf / "2026-10-2x").mkdir()
    (perf / "file.txt").write_text("x")
    # current contract: only the SHAPE (10 chars, dashes at 4 and 7) is checked, not that it is a real date
    _eq(sm._resolve_latest_day(perf), "2026-10-2x")
    (perf / "2026-10-27").mkdir()
    _eq(sm._resolve_latest_day(perf), "2026-10-2x")                               # sorts after real dates, so it wins


def test_latest_usable_day_skips_days_without_directional_evidence(tmp_path):
    _memory(tmp_path, "2026-10-26", best_playbooks=["pb"])
    _memory(tmp_path, "2026-10-27", best_playbooks=[])
    _memory(tmp_path, "2026-10-28", status="empty")
    perf = tmp_path / "performance"
    _eq(sm._resolve_latest_usable_day(perf), "2026-10-26")
    _eq(sm._resolve_latest_usable_day(perf, at_or_before="2026-10-27"), "2026-10-26")
    _eq(sm._resolve_latest_usable_day(perf, at_or_before="2026-10-25"), "")


def test_hint_fallback_requires_content_and_bad_requested_day_gives_null_age(tmp_path):
    # fallback day exists but holds no summary/playbook/memory files at all -> target day stays
    (tmp_path / "performance" / "2026-10-27").mkdir(parents=True)
    out = sm.load_strategy_memory_hint(reports_root=tmp_path, day="2026-10-28")
    _eq(out["day"], "2026-10-28")
    if "requested_day" in out:
        raise AssertionError(out)
    # usable older day + a malformed requested day -> stale with age_days None
    _memory(tmp_path, "2026-10-20", best_playbooks=["pb"])
    stale = sm.load_strategy_memory_hint(reports_root=tmp_path, day="2026-10-28")
    _eq((stale["resolved_day"], stale["requested_day"], stale["freshness_status"], stale["age_days"]),
        ("2026-10-20", "2026-10-28", "stale", (date(2026, 10, 28) - date(2026, 10, 20)).days))
    real = date.fromisoformat

    class Boom(date):
        @classmethod
        def fromisoformat(cls, s):
            raise ValueError("bad date")

    import datetime as _dt

    orig = _dt.date
    _dt.date = Boom
    try:
        bad = sm.load_strategy_memory_hint(reports_root=tmp_path, day="2026-10-28")
    finally:
        _dt.date = orig
    _eq((bad["freshness_status"], bad["age_days"]), ("stale", None))
    _eq(real("2026-10-28"), date(2026, 10, 28))


def test_state_store_save_replaces_a_non_dict_existing_file(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")                                # valid JSON, wrong shape
    store = StateStore(path)
    store.save({"k": "v"})
    _eq(json.loads(path.read_text(encoding="utf-8")), {"k": "v"})
    _eq([p.name for p in tmp_path.iterdir()], ["state.json"])                     # no temp file left behind
    path.write_text("{broken", encoding="utf-8")
    store.save({"k2": 1})
    _eq(json.loads(path.read_text(encoding="utf-8")), {"k2": 1})


def test_resolve_latest_day_returns_empty_when_no_dir_has_a_date_shape(tmp_path):
    perf = tmp_path / "performance"
    (perf / "not-a-day").mkdir(parents=True)
    (perf / "file.txt").write_text("x")
    _eq(sm._resolve_latest_day(perf), "")
