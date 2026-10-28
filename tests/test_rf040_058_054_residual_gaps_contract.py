"""RF-040 / RF-058 / RF-054 residual coverage gaps (measured with coverage.py): small, offline, tmp_path only.

intent_parser L68 (``price <n>`` form), strategist L59 (themes limit), commander branch 109->115
(non-dict executor result), state_store L125-126 (tmp unlink failure ignored), playbook_stats L38-39
(truth-surface return), performance_aggregator L39 (missing json path). Explicit raises keep the
checks live under ``python -O``.
"""
from __future__ import annotations

import json
import pathlib

from libs.agent.commander import Commander
from libs.agent.intent_parser import parse_nl
from libs.agent.strategist import Plan, Strategist, _normalize_symbols, _normalize_text_list
from libs.performance import performance_aggregator as pa
from libs.performance import playbook_stats as ps
from libs.storage.state_store import StateStore


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def test_intent_parser_price_keyword_forms_and_precedence():
    _eq(parse_nl("buy 005930 price 70000").price, 70000)          # English keyword form (lower-cased text)
    _eq(parse_nl("매수 005930 가격 72000").price, 72000)
    _eq(parse_nl("매수 005930 가격72000").price, 72000)            # no space
    _eq(parse_nl("매수 005930 71000원 가격 72000").price, 71000)     # the "원" form wins over the keyword form
    _eq(parse_nl("buy 005930 price 99").price, None)              # needs at least 3 digits
    _eq(parse_nl("buy 005930 qty 4 price 70000").qty, 4)


def test_strategist_normalizers_stop_at_their_limits_and_dedupe():
    _eq(_normalize_text_list(["a", "b", "a", "", None, "c"], limit=2), ["a", "b"])
    _eq(_normalize_symbols(["x", "X", " y ", "z"], limit=2), ["X", "Y"])
    _eq(_normalize_text_list("notalist", limit=3), [])
    plan = Strategist().plan(context={"themes": [f"t{i}" for i in range(9)], "candidates": [f"c{i}" for i in range(9)], "top_n_candidates": 3})
    _eq((plan.themes, plan.candidates), (["t0", "t1", "t2", "t3", "t4"], ["C0", "C1", "C2"]))   # themes cap 5, candidates cap top_n


class _Strat:
    def plan(self, *, context):
        return Plan(thesis="t", constraints={})


class _Scan:
    def scan(self, *, plan, context):
        return [{"side": "buy"}]


class _Rep:
    def build(self, **kw):
        return {"n_decisions": len(kw["decisions"]), "n_exec": len(kw["executions"])}


class _Mon:
    def __init__(self):
        self.seen = None

    def update(self, *, intents, decisions, executions, context):
        self.seen = (intents, decisions, executions)


def test_commander_ignores_non_dict_or_decisionless_executor_results():
    class Ex:
        def __init__(self, result):
            self.result = result

        def submit(self, **kw):
            return self.result

    for result, n_dec in (("rejected-as-text", 0), ({"no_decision_key": 1}, 0), ({"decision": "text"}, 0), ({"decision": {"status": "ok"}}, 1)):
        mon = _Mon()
        res = Commander(strategist=_Strat(), scanner=_Scan(), monitor=mon, reporter=_Rep(), executor=Ex(result)).run()
        _eq(res.report["n_decisions"], n_dec)
        _eq(res.execution, result)                       # the raw executor result is passed through untouched
        _eq(len(mon.seen[1]), n_dec)
        _eq(len(mon.seen[2]), 1)


def test_state_store_ignores_failure_to_remove_its_tmp_file(tmp_path, monkeypatch):
    p = tmp_path / "s.json"
    orig = pathlib.Path.unlink

    def bad_unlink(self, *a, **k):
        if ".tmp." in self.name:
            raise OSError("cannot remove")
        return orig(self, *a, **k)

    # save() replaces the tmp file first, so the tmp no longer exists and unlink is never needed ...
    monkeypatch.setattr(pathlib.Path, "unlink", bad_unlink)
    StateStore(p).save({"v": 1})
    _eq(json.loads(p.read_text(encoding="utf-8")), {"v": 1})
    # ... but when the replace fails the tmp file stays and the failed cleanup must not mask the original error
    import libs.storage.state_store as ss
    monkeypatch.setattr(ss.os, "replace", lambda a, b: (_ for _ in ()).throw(OSError("replace failed")))
    try:
        StateStore(p).save({"v": 2})
    except OSError as exc:
        _eq(str(exc), "replace failed")
    else:
        raise AssertionError("OSError from replace must propagate")
    leftovers = [x.name for x in tmp_path.iterdir() if ".tmp." in x.name]
    _eq(len(leftovers), 1)          # the tmp file is left behind because its removal failed (documented current behaviour)
    _eq(json.loads(p.read_text(encoding="utf-8")), {"v": 1})


def test_playbook_stats_prefers_truth_surface_return(tmp_path):
    d = tmp_path / "t1"
    (d / "reports").mkdir(parents=True)
    (d / "reports" / "ai_trade_summary_input.json").write_text(json.dumps({"truth_surface": {"pnl": 4.0, "pnl_pct": 2.5}}), encoding="utf-8")
    bundle = {"_bundle_path": str(d / "lifecycle_bundle.json"), "trade_outcome": {"return_pct": 9.0}}
    _eq(ps._extract_return(bundle), 2.5)                                           # truth return beats the lifecycle value
    (d / "reports" / "ai_trade_summary_input.json").write_text(json.dumps({"truth_surface": {"pnl_pct": 1.0}}), encoding="utf-8")
    _eq(ps._extract_return(bundle), None)                                          # pnl missing -> return stays None (observation only)


def test_aggregator_read_json_dict_missing_corrupt_and_non_dict(tmp_path):
    _eq(pa._read_json_dict(tmp_path / "missing.json"), {})
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    _eq(pa._read_json_dict(bad), {})
    lst = tmp_path / "list.json"
    lst.write_text("[1]", encoding="utf-8")
    _eq(pa._read_json_dict(lst), {})
    # Note: the `if not path: return {"available": False}` branch of extract_truth_outcome_from_bundle is unreachable
    # (``Path()`` is truthy), see the truth_surface_path quirk pinned in test_rf054_libs_performance_contract.py.
    _eq(bool(pathlib.Path()), True)
