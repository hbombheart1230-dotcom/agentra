"""Pinned-source differential proof for the two BATCH04 read-only node projections."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
import importlib
import inspect
import json
from pathlib import Path
import subprocess
import sys
import types

import pytest

BASE = "8fd49ddf958574f0f505249c3370314ffc06aeac"
ROOT = Path(__file__).resolve().parents[1]
CONTEXT = "graphs.nodes.build_decision_context"
SKILL = "graphs.nodes.hydrate_skill_results_node"


@lru_cache(None)
def _source(name):
    return subprocess.check_output(["git", "show", BASE + ":" + name.replace(".", "/") + ".py"], cwd=ROOT).decode("utf-8")


def _baseline(name, monkeypatch):
    mod = types.ModuleType(name + "_frozen_batch04")
    mod.__file__ = str(ROOT / (name.replace(".", "/") + ".py"))
    monkeypatch.setitem(sys.modules, mod.__name__, mod)
    exec(compile(_source(name), mod.__file__, "exec"), mod.__dict__)
    return mod


def _bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _view(state):
    return {k: v for k, v in state.items() if k not in {"skill_runner", "event_logger", "skill_runner_factory"}}


def _aliases(value):
    """Ordered container identity graph; compare aliases without comparing addresses."""
    seen = {}
    def visit(v):
        if isinstance(v, (dict, list)):
            if id(v) in seen:
                return ("ref", seen[id(v)])
            tag = len(seen)
            seen[id(v)] = tag
            return (type(v).__name__, tag, [(k, visit(x)) for k, x in v.items()] if isinstance(v, dict) else [visit(x) for x in v])
        return v
    return visit(value)


def _context_run(mod, scenario, monkeypatch):
    state = {"symbol": "aaa", "market_snapshot": {"price": 102},
             "policy": {"use_global_sentiment": True, "use_news_analysis": True, "decision_context_refresh_sec": 300},
             "news_items": {"OTHER": [{"title": "old"}]}}
    now = 1000
    cached = {"refreshed_epoch": 900, "global_sentiment_score": .2, "news_sentiment_score": .3,
              "news_items": [{"title": "cached"}]}
    if scenario in {"cache", "partial", "future", "edge", "expired", "empty_signal", "bad_items", "cache_error"}:
        if scenario == "future": cached["refreshed_epoch"] = 1100
        if scenario == "edge": cached["refreshed_epoch"] = 700
        if scenario == "expired": cached["refreshed_epoch"] = 699
        if scenario == "partial": cached["global_sentiment_signal"] = {"score": .9, "status": "stale"}
        if scenario == "empty_signal": cached["news_sentiment_signal"] = {}
        if scenario == "bad_items": cached["news_items"] = None
        state["_decision_context_cache"] = {"AAA": cached, "OTHER": {"keep": True}}
    if scenario == "bad_cache": state["_decision_context_cache"] = []
    if scenario == "missing_symbol": state.pop("symbol"); state["market_snapshot"] = {}
    if scenario == "selected_symbol": state.pop("symbol"); state["selected_symbol"] = "aaa"
    if scenario == "disabled": state["policy"].update(use_news_analysis=False, use_global_sentiment=False)
    if scenario == "env": state.pop("policy")
    if scenario == "bad_state": state["news_sentiment"] = []; state["news_sentiment_signal"] = "bad"
    if scenario == "rows": state["ohlcv_by_symbol"] = {"AAA": [{"ts": 1000, "close": 101, "open": 99}]}
    events = []
    def event(name, *args): events.append((name, args, copy.deepcopy(state)))
    def getenv(k, default=None): event("env", k, default); return default
    def clock(): event("clock"); return now
    def seed(symbol, policy): event("seed", symbol); return []
    def features(rows): event("features", copy.deepcopy(rows)); return {"AAA": {"regime": "trend", "signal_score": .4}}
    def global_signal(**kw):
        event("global")
        if scenario == "global_error": raise RuntimeError("offline global")
        return {"score": .5, "status": "ok", "source": "offline", "reason": "synthetic"}
    def collect(symbols, **kw):
        event("collect", symbols)
        if scenario == "news_error": raise ValueError("offline news")
        return {"AAA": [{"title": "\uac80\uc99d", "id": 1}]}
    def score(items, **kw):
        event("score", copy.deepcopy(items))
        if scenario == "score_error": raise TypeError("offline score")
        if scenario == "missing_news": return {}
        return {"AAA": {"score": -.25, "status": "ok", "source": "offline-news"}}
    with monkeypatch.context() as m:
        m.setattr(mod, "time", types.SimpleNamespace(time=clock))
        m.setattr(mod, "os", types.SimpleNamespace(getenv=getenv))
        for name, fn in {"_fetch_yfinance_seed": seed, "build_feature_map": features,
                         "compute_global_sentiment_signal": global_signal, "collect_news_items": collect,
                         "score_news_sentiment_signal": score}.items(): m.setattr(mod, name, fn)
        # Exercise facade lookups after import, including nested projection calls.
        if scenario in {"late_patch", "cache_error"}:
            original = mod._to_float
            def conversion(v, default=0.):
                event("float", v, default)
                if scenario == "cache_error" and v == .2: raise ValueError("cache conversion")
                return original(v, default)
            m.setattr(mod, "_to_float", conversion)
        error = None
        try:
            result = mod.build_decision_context(state)
            assert result is state
        except ValueError as exc:
            if scenario != "cache_error": raise
            error = (type(exc).__name__, str(exc))
    return _bytes(state), _aliases(state), _bytes(events), error


CONTEXT_CASES = ["fresh", "cache", "partial", "future", "edge", "expired", "empty_signal", "bad_items",
                 "bad_cache", "missing_symbol", "selected_symbol", "disabled", "env", "bad_state", "rows",
                 "global_error", "news_error", "score_error", "missing_news", "late_patch", "cache_error"]


@pytest.mark.parametrize("scenario", CONTEXT_CASES)
def test_context_pinned_state_bytes_aliases_and_effect_order(scenario, monkeypatch):
    before = _context_run(_baseline(CONTEXT, monkeypatch), scenario, monkeypatch)
    after = _context_run(importlib.import_module(CONTEXT), scenario, monkeypatch)
    assert after == before


@dataclass
class _Ready:
    action: str = "ready"
    data: object = None


def _skill_run(mod, scenario, monkeypatch):
    state = {"run_id": "offline-batch04", "policy": {"candidate_k": 2},
             "candidates": [{"symbol": "AAA"}, {"symbol": "AAA"}, {"symbol": "BBB"}],
             "selected": {"symbol": "CCC"},
             "portfolio_snapshot": {"positions": [{"symbol": "HELD", "qty": 2}, {"symbol": "AAA", "qty": 3}, {"symbol": "ZERO", "qty": 0}]},
             "order_ref": {"ord_no": "old-order", "symbol": "AAA", "ord_dt": "20000101"},
             "skill_results": {"preserved": {"x": 1}, "order.status": {"old": True}}}
    if scenario == "missing_ref": state.pop("order_ref")
    if scenario == "partial_ref": state["order_ref"].pop("ord_dt")
    if scenario == "no_symbols": state.update(candidates=[], selected={}, portfolio_snapshot={})
    if scenario == "bad_limit": state["policy"]["candidate_k"] = "invalid"
    events = []
    def event(name, *args): events.append((name, args, copy.deepcopy(_view(state))))
    class Clock:
        @staticmethod
        def now(tz): event("clock"); return datetime(2026, 10, 20, 1, 2, 3, 999, tzinfo=timezone.utc)
    class Runner:
        def run(self, *, run_id, skill, args):
            if skill not in {"market.quote", "account.orders", "order.status"}: raise AssertionError("write skill forbidden")
            event("run", run_id, skill, dict(args))
            if scenario == "raise_runner" and skill == "account.orders": raise RuntimeError("offline runner")
            if scenario == "error": return {"result": {"action": "error", "meta": {"error_type": "TimeoutError"}}}
            if scenario == "ask": return {"action": "ask", "question": "missing account"}
            if scenario == "unsupported": return None
            if scenario == "empty": return {}
            if scenario == "missing_data": return {"result": {"action": "ready"}}
            data = {"symbol": args.get("symbol", "AAA"), "qty": 1}
            if scenario == "late_patch": return _Ready(data=data)
            if scenario == "dataclass": return _Ready(data={"rows": [_Ready(data=data)]})
            return {"result": {"action": "ready", "data": data}}
    class Logger:
        def log(self, **kw):
            event("log", copy.deepcopy(kw))
            if scenario == "logger_error": raise RuntimeError("offline logger")
            return kw
    runner = Runner()
    state["event_logger"] = Logger()
    if scenario == "no_runner": pass
    elif scenario == "factory": state["skill_runner_factory"] = lambda: runner
    elif scenario == "factory_error":
        def factory(*args): event("factory"); raise ValueError("offline factory")
        state["skill_runner_factory"] = factory
    elif scenario == "auto": state["auto_skill_runner"] = True
    else: state["skill_runner"] = runner
    with monkeypatch.context() as m:
        m.setattr(mod, "datetime", Clock)
        m.setattr(mod, "os", types.SimpleNamespace(getenv=lambda k, default=None: default))
        m.setattr(mod, "_build_composite_skill_runner", lambda state: runner)
        if scenario == "late_patch":
            original = mod._norm_symbol
            def norm(v): event("normalize", v); return original(v)
            m.setattr(mod, "_norm_symbol", norm)
            original_plain = mod._to_plain
            def plain(v): event("plain", copy.deepcopy(v)); return original_plain(v)
            m.setattr(mod, "_to_plain", plain)
        error = None
        try:
            result = mod.hydrate_skill_results_node(state)
            assert result is state
        except RuntimeError as exc:
            error = (type(exc).__name__, str(exc))
    return _bytes(_view(state)), _aliases(_view(state)), _bytes(events), error


SKILL_CASES = ["ready", "missing_ref", "partial_ref", "no_symbols", "bad_limit", "error", "ask", "unsupported",
               "empty", "missing_data", "dataclass", "raise_runner", "no_runner", "factory", "factory_error", "auto", "late_patch", "logger_error"]


@pytest.mark.parametrize("scenario", SKILL_CASES)
def test_skill_pinned_records_aliases_clock_runner_and_log_order(scenario, monkeypatch):
    before = _skill_run(_baseline(SKILL, monkeypatch), scenario, monkeypatch)
    after = _skill_run(importlib.import_module(SKILL), scenario, monkeypatch)
    assert after == before


@pytest.mark.parametrize("name", [CONTEXT, SKILL])
def test_original_signatures_and_import_paths(name, monkeypatch):
    base = _baseline(name, monkeypatch)
    actual = importlib.import_module(name)
    for key, value in vars(base).items():
        if inspect.isfunction(value) and value.__module__ == base.__name__:
            assert inspect.signature(getattr(actual, key)) == inspect.signature(value)


@pytest.mark.parametrize("kind", ["cache", "status", "metadata_order", "skill_status", "quote_order", "counts", "extra_effect"])
def test_nonvacuous_runtime_mutants_are_detected(kind, monkeypatch):
    context = importlib.import_module(CONTEXT)
    skill = importlib.import_module(SKILL)
    scenario = "cache" if kind in {"cache", "status", "metadata_order"} else "ready"
    name = CONTEXT if scenario == "cache" else SKILL
    mod = context if scenario == "cache" else skill
    run = _context_run if scenario == "cache" else _skill_run
    reference = run(_baseline(name, monkeypatch), scenario, monkeypatch)
    assert run(mod, scenario, monkeypatch) == reference  # Real green baseline FIRST.
    if scenario == "cache":
        owner = context._context_projection
        original = owner.apply_cached
        def corrupt(*args, **kw):
            state = original(*args, **kw)
            if kind == "cache": state["_decision_context_cache"]["AAA"]["refreshed_epoch"] += 1
            if kind == "status": state["global_sentiment_signal"]["status"] = "approved"
            if kind == "metadata_order": state["decision_context_meta"] = dict(reversed(list(state["decision_context_meta"].items())))
            return state
        monkeypatch.setattr(owner, "apply_cached", corrupt)
    elif kind == "skill_status":
        original = skill._skill_projection._skill_output_to_record
        def corrupt(*args, **kw):
            rec = original(*args, **kw); rec["result"]["action"] = "approved"; return rec
        monkeypatch.setattr(skill._skill_projection, "_skill_output_to_record", corrupt)
    elif kind == "quote_order":
        original = skill._skill_projection._quote_hydration_symbols
        monkeypatch.setattr(skill._skill_projection, "_quote_hydration_symbols", lambda *a, **k: list(reversed(original(*a, **k))))
    elif kind == "counts":
        original = skill._skill_projection.fetch_counts
        def corrupt(*a, **k):
            out = original(*a, **k); out["ready"]["market.quote"] += 1; return out
        monkeypatch.setattr(skill._skill_projection, "fetch_counts", corrupt)
    else:
        original = skill._skill_projection._quote_hydration_symbols
        def corrupt(state, **kw):
            state["skill_runner"].run(run_id="extra", skill="market.quote", args={"symbol": "EXTRA"})
            return original(state, **kw)
        monkeypatch.setattr(skill._skill_projection, "_quote_hydration_symbols", corrupt)
    assert run(mod, scenario, monkeypatch) != reference


@pytest.mark.parametrize("value", [None, {}, {"action": "ask", "question": "why"},
    {"result": {"action": "ready", "data": {"nested": []}}}, _Ready(data={"nested": [1]})])
def test_projection_can_be_called_independently_with_alias_equivalence(value, monkeypatch):
    base = _baseline(SKILL, monkeypatch)
    facade = importlib.import_module(SKILL)
    owner = importlib.import_module("graphs.nodes.skill_result_projection")
    before = base._skill_output_to_record(copy.deepcopy(value))
    after = owner._skill_output_to_record(copy.deepcopy(value), facade=facade)
    assert _bytes(after) == _bytes(before)
    assert _aliases(after) == _aliases(before)
    assert owner._error_reason(after, facade=facade) == base._error_reason(before)


def test_quote_projection_keeps_late_helper_lookups(monkeypatch):
    facade = importlib.import_module(SKILL)
    calls = []
    monkeypatch.setattr(facade, "_unique_symbols", lambda rows, *, limit: calls.append((rows, limit)) or ["PATCHED"])
    monkeypatch.setattr(facade, "position_by_symbol", lambda state: {"HELD": {"qty": 1}})
    state = {"candidates": ["AAA"], "selected": {"symbol": "BBB"}}
    assert facade._quote_hydration_symbols(state, candidate_limit=3) == ["PATCHED", "BBB", "HELD"]
    assert calls == [(["AAA"], 3)]
