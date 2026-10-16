"""S1-057 bounded offline oracle. The facade is a deterministic TEST DOUBLE.

Generate only from a disposable git-archive of PINNED_BASE, before relocation.
This does not call the real Strategist/LLM, read reports or establish real-report parity.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import io
import json
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from types import SimpleNamespace

PINNED_BASE = "0a3a224c2da8f8305cdf7f9c296cb0e7fea46766"
START_SHA = "d82dd126fd0c818101c5aca1472ed2c8adb6f3c1"
MODULES = {
    "context/theme_strength": "0268ed0e32b337f41606a6897b6a7bbbe23aad24",
    "context/market_key_events": "3b09d58c283cec5e87792ada8214b361805e2668",
    "context/symbol_read_models": "91316b5136d1a14a74eb0dc809e979f0f51c04c6",
    "context/news_compaction": "c4ba0ddfb70b34b681f3043f897d19803dde3b25",
    "output/strategic_answers": "1c84a7ffae545e24747570d798511dc1afd10771",
}


def encode(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


class FakeFacade:
    """Only deterministic, in-memory dependencies. Unknown capabilities fail closed."""
    def __init__(self, modules, env=None, repatch=False):
        self.modules, self.trace, self.repatch = modules, [], repatch
        self.re = re
        self.os = SimpleNamespace(getenv=lambda key, default=None: (env or {}).get(key, default))

    def __getattr__(self, name):
        for module in self.modules.values():
            impl = vars(module).get(name + "_r3_impl")
            if impl is not None:
                return lambda *a, **k: impl(*a, **k, facade=self)
        raise AttributeError("test facade denies " + name)

    @staticmethod
    def _to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    _stage_float = _to_float

    @staticmethod
    def _clamp(value, low=0.0, high=1.0):
        return max(low, min(high, value))

    def _round_optional(self, value, digits):
        if self.repatch:
            self.trace.append("round:rebind")
            self._round_optional = lambda value, digits: 0.125 if value is not None else None
        number = self._to_float(value, None)
        return round(number, digits) if number is not None else None

    def _signal_score(self, signal):
        return self._to_float(signal.get("score"), 0.0)

    @staticmethod
    def _clip_text_for_llm(value, max_len=120):
        return str(value or "").strip()[:max_len]

    def _compact_scalar_mapping_for_llm(self, src, *, allowed_keys, max_text_len):
        self.trace.append("scalar:" + str(max_text_len))
        return {k: self._clip_text_for_llm(v, max_text_len) if isinstance(v, str) else v
                for k in allowed_keys if k in src and isinstance((v := src[k]), (str, bool, int, float))}

    def _compact_pattern_rows_for_llm(self, rows, *, limit):
        self.trace.append("patterns:" + str(limit))
        return copy.deepcopy(rows[:limit]) if isinstance(rows, list) else []

    def _compact_trade_read_model_for_llm(self, row):
        self.trace.append("trade")
        return dict(row) if isinstance(row, dict) else {}

    def _operator_summary_for_llm(self, row):
        self.trace.append("operator_summary")
        return copy.deepcopy(row) if isinstance(row, dict) else {}

    @staticmethod
    def stable_evidence_id(prefix, value):
        return prefix + "-" + hashlib.sha256(encode(value).encode()).hexdigest()[:16]

    @staticmethod
    def _append_unique_text(out, seen, value):
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            out.append(text)

    @staticmethod
    def _theme_news_query_terms(themes, *, limit):
        return ["테마 " + str(t) for t in list(themes or [])[:limit] if t]

    @staticmethod
    def _theme_to_news_queries(theme):
        return [str(theme), str(theme) + " 뉴스"]

    def _build_symbol_refresh_memory_excerpt(self, symbol, facts, reports_root):
        self.trace.append(["memory_stub", symbol, reports_root])
        return {"symbol": symbol, "status": "mock_only", "facts_count": len(facts)}


def specifications():
    rows = []
    def add(module, fn, args=None, kwargs=None, **extra):
        rows.append(dict(module=module, function=fn + "_r3_impl", args=args or [], kwargs=kwargs or {}, **extra))
    theme = "context/theme_strength"
    for scores in ({}, {"반도체": 0.0, "AI": -40}, {"반도체": "bad", "ai": 0.5}, {"반도체": 50, "AI": 50}):
        add(theme, "_theme_strength_map", kwargs=dict(themes=["반도체", "AI", ""], candidates=[{"symbol": "AAA"}, {"symbol": "BBB"}], theme_scores=scores, theme_index={"반도체": ["AAA"], "ai": ["BBB"]}))
    for kwargs in (dict(themes=[], candidates=[], theme_scores={}, theme_index={}),
                   dict(themes=["x"], candidates=["bad"], theme_scores={}, theme_index={}),
                   dict(themes=["x"], candidates=[], theme_scores=None, theme_index={})):
        add(theme, "_theme_strength_map", kwargs=kwargs)
    for sentiment, playbook in (("bearish", "x"), ("neutral", "defensive"), ("bullish", "reversal"), ("", "pullback"), (None, None)):
        add(theme, "_avoid_themes", kwargs=dict(market_sentiment=sentiment, playbook=playbook))
    events = dict(state={}, global_signal={}, news_signal_map={}, market_regime="중립", playbook="pullback", market_context_inputs={}, news_ctx={}, theme_strength={})
    for change in ({}, {"state": {"macro_events": ["한국", "한국", "미국", "유가", "환율", "금리", "금", "끝"]}},
                   {"state": {"macro_events": [], "global_events": ["ignored"]}},
                   {"global_signal": {"score": .3, "components": {"sp500_ret": .01234, "nasdaq_ret": -.02}, "korea_indices": {"indices": {"KOSPI": {"current": 2500.235, "previous_close": 2490, "change_pct": .411}}}}},
                   {"global_signal": {"fear_index": {"level": 30, "level_pressure": .5}}, "theme_strength": {"B": .5, "A": .5}},
                   {"state": None}):
        add("context/market_key_events", "_key_events", kwargs={**events, **change})
    sym = "context/symbol_read_models"
    for value in (None, {}, {"symbol": "AAA", "trade_count": 0, "override_eligible": False, "status": "한글", "ignored": "secret-free", "repeated_failure_pattern": list(range(6)), "data_quality": {"status": "ok"}}, [1]):
        add(sym, "_compact_symbol_read_model_for_llm", [value])
    for value in ({}, None, {"recent_trades": [{"symbol": "AAA", "n": n} for n in range(6)], "symbol_patterns": {str(i): {"symbol": str(i), "trade_count": i} for i in range(8)}, "daily_summary": {"status": "한글"}}, {"recent_trades": 17}):
        add(sym, "_compact_read_model_facts_for_llm", [value])
    candidate = {"symbol": "AAA", "rank": 1, "score": .73456, "confidence": 0, "status": False, "ignored": [1], "score_breakdown": {"a": .123456, "b": "텍스트", "c": None, "d": 1, "e": 2, "f": 3}}
    for value in (None, {}, candidate, {"score_breakdown": "bad"}):
        add(sym, "_compact_candidate_context_for_refresh", [value])
    for value in (None, {}, {"feedback_id": "fixed", "scanner_primary_candidate": candidate, "scanner_runner_ups": [candidate] * 6, "scanner_top_candidates": [candidate] * 7, "selected_symbol_memory": {"symbol": "AAA", "trade_count": 4, "override_eligible": False, "operator_summary": {"x": 1}}}, {"selected_symbol_memory": {"trade_count": "bad"}}):
        add(sym, "_slim_refresh_context_for_llm", [value])
    news = "context/news_compaction"
    for value in (None, {}, {"BBB": {"sample": [{"title": "한글 제목 " * 8}, "둘째", "셋째"], "count": 0}, "AAA": {"sample": [None]}, "C": None}, {"A": {"count": "bad", "sample": []}}):
        add(news, "_compact_news_sample_for_llm", [value], dict(max_symbols=2, max_titles=2, max_title_len=18))
    signal = {"score": .123456, "status": "정상", "source": "mock", "index_moves": {"sp500_pct": 1.23456}, "korea_indices": {"indices": {"KOSPI": {"current": 2500.235, "change_pct": -.123456}}}, "krx_night_futures": {"trading_action_allowed": False}, "macro_indicators": {"usdkrw": {"current": 1300.123456, "role": "관측"}, "ignored": {"current": 7}}}
    for value in (None, {}, signal, {"index_moves": None, "macro_indicators": {"indicators": {"usdkrw": {"current": 1300.123456}, "ignored": {"current": 7}}}}):
        add(news, "_compact_global_signal_for_llm", [value])
    add(news, "_compact_global_signal_for_llm", [signal], repatch=True)
    for score in (-.251, -.25, 0, .2499, .25, "bad", None):
        add(news, "_news_signal_label", [score])
    for title in ({"title": "<b>한글</b> " + "x" * 40}, {"headline": "대체 제목"}, "News(title='한국 성장')", None):
        add(news, "_news_item_title_for_llm", [title], {"max_len": 16})
    for kwargs in (dict(signal_map={}, sample={}, symbols=[], limit=3),
                   dict(signal_map={"B": {"score": -.333333, "status": "ok"}, "A": {}}, sample={"A": {"sample": ["첫 뉴스", "둘째"]}}, symbols=["B", "B", ""], limit=2),
                   dict(signal_map={}, sample={"A": {"count": "bad"}}, symbols=["A"], limit=1)):
        add(news, "_compact_news_signal_summary_for_llm", kwargs=kwargs)
    for value, selected in (([], ""), ([], "AAA"), ([{"symbol": "AAA", "top_evidence": ["한글"]}], "AAA"), (["bad"], "AAA")):
        add(news, "_selected_symbol_news_signal_for_llm", [value, selected])
    for limit in (0, 2, 10, "bad"):
        add(news, "_merge_news_collection_symbols", kwargs=dict(base_symbols=[" aaa ", "BBB", "AAA"], theme_symbols=["CCC", "bbb"], limit=limit))
    for signal, context, hints in (({}, {}, []), ({"score": -.3}, {"macro_risk": .8, "market_breadth": .3}, ["반도체"]), ({"score": .4}, {"index_trend": .2, "market_breadth": .7}, []), ({"fear_index": {"level": 30}}, {"realized_volatility": .04}, ["AI"])):
        add(news, "_build_market_news_query_targets", kwargs=dict(state={"news_query_targets": ["명시", "명시"]}, policy={"strategist_news_query_limit": 8}, global_signal=signal, market_context_inputs=context, theme_hints=hints))
    add(news, "_build_market_news_query_targets", kwargs=dict(state={}, policy={}, global_signal={}, market_context_inputs={}, theme_hints=[]), env={"STRATEGIST_NEWS_QUERY_LIMIT": "3", "NEWS_QUERY_TARGETS": "환경, 환경,뉴스"})
    answers = dict(commander_context={}, market_regime="중립", market_sentiment="neutral", key_events=["한국 이벤트"], themes=["AI"], avoid_themes=[], playbook="pullback", scanner_bias={"kind": {"score": .5}}, scanner_priority=["AAA"], trade_aggressiveness="low", risk_tone="guarded", monitor_guidance={"nested": [1]}, report_focus=["관측"], recent_strategy_feedback={}, strategy_memory={}, read_model_facts={}, reports_root="MOCK_ONLY")
    refresh = {"selected_symbol": "AAA", "selected_rank": 1, "selected_score": .123456, "scanner_primary_candidate": candidate, "scanner_runner_ups": [candidate] * 6, "scanner_top_candidates": [candidate] * 7, "entry_state": {"nested": [1]}, "selected_symbol_was_rank1": False, "prior_monitor_entry_policy_summary": {"nested": [2]}}
    for change in ({}, {"commander_context": {"open_position_refresh_context": refresh, "commander_horizon_policy": {"strategy_horizon": "intraday", "do_not_force_hold": True}}}, {"commander_context": {"strategist_refresh_context": refresh}}, {"commander_context": {"open_position_refresh_context": {"selected_rank": "bad"}}}):
        add("output/strategic_answers", "_build_strategic_answers", kwargs={**answers, **change})
    return rows


def observe(spec, modules):
    args, kwargs = copy.deepcopy([spec["args"], spec["kwargs"]])
    facade = FakeFacade(modules, spec.get("env"), spec.get("repatch", False))
    inputs = {}
    def walk(value, path):
        if isinstance(value, (dict, list)):
            yield id(value), path
            pairs = value.items() if isinstance(value, dict) else enumerate(value)
            for key, child in pairs:
                yield from walk(child, path + "/" + str(key))
    for obj, path in walk([args, kwargs], "input"):
        inputs.setdefault(obj, []).append(path)
    aliases = []
    try:
        value = getattr(modules[spec["module"]], spec["function"])(*args, **kwargs, facade=facade)
        aliases = [[path, source] for obj, path in walk(value, "result") for source in inputs.get(obj, [])]
        result = {"ok": value}
    except Exception as exc:
        result = {"exc": type(exc).__name__, "message": str(exc)}
    serialized = encode(result)
    return dict(result=result, utf8_sha256=hashlib.sha256(serialized.encode()).hexdigest(),
                input_after=[args, kwargs], aliases=aliases, calls=facade.trace)


def load_tree(tree):
    out = {}
    for name, blob in MODULES.items():
        path = tree / ("libs/runtime/strategist/" + name + ".py")
        raw = path.read_bytes()
        if hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest() != blob:
            raise RuntimeError("BASE blob mismatch: " + name)
        parsed = ast.parse(raw)
        if any(not isinstance(n, (ast.FunctionDef, ast.ImportFrom, ast.Expr)) for n in parsed.body):
            raise RuntimeError("unexpected BASE top-level statement")
        spec = importlib.util.spec_from_file_location("_s1_base_" + name.replace("/", "_"), path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        out[name] = mod
    return out


def generate(root, output):
    paths = ["libs/runtime/strategist/" + name + ".py" for name in MODULES]
    data = subprocess.check_output(["git", "-c", "core.autocrlf=false", "archive", PINNED_BASE, *paths], cwd=root)
    with tempfile.TemporaryDirectory(prefix="s1057_base_") as directory:
        tree = Path(directory)
        tarfile.open(fileobj=io.BytesIO(data)).extractall(tree, filter="data")
        modules = load_tree(tree)
        # JSON cannot represent shared input references. Freeze the exact JSON
        # input representation that replay will receive, not generator aliases.
        specs = [json.loads(encode(spec)) for spec in specifications()]
        cases = [{**spec, "expected": observe(spec, modules)} for spec in specs]
    doc = dict(schema="s1057.frozen.v1", producer_sha=PINNED_BASE, start_sha=START_SHA,
               source_blobs=MODULES, python=platform.python_version(),
               oracle="Pinned BASE source plus deterministic test-only facade; no real LLM/report parity.", cases=cases)
    raw = (json.dumps(doc, ensure_ascii=False, indent=1) + "\n").encode()
    if len(raw) >= 256 * 1024:
        raise RuntimeError("bounded fixture exceeds 256 KiB; do not publish")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(raw)
    print("BASE_CASES", len(cases), "BYTES", len(raw), "SHA256", hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    generate(Path.cwd(), args.output)
