"""P1.5 BATCH03-A: quant shadow candidate evaluation projection parity.

The frozen BASE ``quant_shadow_candidate_evaluation.py`` (``e92950d4``) is exec'd as a separate module and compared
with the current facade on identical synthetic payloads: full evaluation dict (JSON with key order), rendered lines,
exception type/message, late monkeypatch of facade helpers/constants and streaming loader use. ``attach_forward_outcomes``
is replaced by a deterministic copy on both modules so no ``data/state.json`` is read.
"""
from __future__ import annotations

import ast
import json
import random
import subprocess
import tracemalloc
import types
from pathlib import Path

import pytest

import libs.reporting.quant_shadow_candidate_evaluation as cur
import libs.reporting.quant_shadow_candidate_projection as proj

ROOT = Path(__file__).resolve().parents[1]
BASE = "e92950d41aa8dd08c643377b3527fa0b77f51106"
PATH = "libs/reporting/quant_shadow_candidate_evaluation.py"
MOVED = ("_mean", "_checkpoint_value", "_forward_outcome_summary", "_top_forward_groups", "_entry_lane_forward_outcomes",
         "_scorecard_return_signal", "_scorecard_rows", "_named_forward_rows", "_no_trade_scorecard")
POLICY = ("_promotion_candidate", "_shadow_readiness")  # env-policy coupled: kept in the facade with BASE bodies


def _base_module():
    src = subprocess.check_output(["git", "show", f"{BASE}:{PATH}"], cwd=ROOT).decode("utf-8-sig")
    mod = types.ModuleType("qsce_base_e92950d4")
    exec(compile(src, f"<base:{PATH}>", "exec"), mod.__dict__)
    return mod


@pytest.fixture()
def mods(monkeypatch):
    base = _base_module()
    for m in (base, cur):
        monkeypatch.setattr(m, "attach_forward_outcomes", lambda rows, **_k: [dict(r) for r in rows], raising=True)
    return base, cur


LANES = [("pullback_quality", "failed_pullback"), ("vwap_reclaim", "reclaim_in_progress_with_improving_volume"),
         ("opening_momentum", "gap_and_go"), ("breakout", "range_break")]


def _checkpoints(rng, *, future=False):
    cps = {}
    for h in ("+3m", "+5m", "+15m", "+30m", "+60m", "EOD"):
        roll = rng.random()
        if future and h in ("+60m", "EOD"):
            cps[h] = {"status": "pending"}
        elif roll < 0.15:
            continue  # missing checkpoint
        elif roll < 0.2:
            cps[h] = {"status": "observed", "return_pct": rng.choice(["abc", "", None])}  # invalid value
        else:
            cps[h] = {"status": "observed", "return_pct": round(rng.uniform(-1.6, 1.4), 3),
                      "mfe_pct": round(rng.uniform(0, 1.2), 3), "mae_pct": round(rng.uniform(-1.6, 0), 3)}
    return cps


def _rows(seed=7, n=320, *, would_enter=False, days=("2026-10-14", "2026-10-15", "2026-10-16")):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        lane, subtype = LANES[i % len(LANES)]
        day = days[i % len(days)]
        row = {
            "symbol": f"{5930 + i % 23:06d}", "day": day, "candidate_day": day, "baseline_epoch": 1_760_000_000 + i,
            "entry_lane_subtype": subtype, "primary_lane": lane, "subtype": subtype, "time_bucket": ("open", "mid")[i % 2],
            "market_regime_rail": ("risk_on", "risk_off")[i % 3 == 0], "shadow_role": ("primary", "runner_up")[i % 2],
            "reason": ("비용 바닥 미달", "cost_edge_fail", "entry_guard", "runner_up_fallback")[i % 4],
            "primary_failure_axis": ("cost", "guard", "")[i % 3], "evaluated": i % 5 != 0, "guard_blocked": i % 4 == 2,
            "would_enter": would_enter and i % 17 == 0, "blockers": ["cost_edge_fail"] if i % 3 == 0 else [],
            "shadow_forward_outcome": {"available": i % 6 != 0, "checkpoints": _checkpoints(rng, future=(i % 9 == 0))},
        }
        out.append(row)
        if i % 11 == 0:
            out.append(dict(row))  # exact duplicate (dedupe key)
    return out


def _payloads(rows, chunk=50):
    return [{"generated_at": f"2026-10-16T0{k % 9}:00:00", "candidates": rows[k:k + chunk]} for k in range(0, len(rows), chunk)]


SCENARIOS = {
    "no_trade_mixed": dict(rows=_rows()),
    "would_enter": dict(rows=_rows(seed=3, would_enter=True)),
    "single_day_small": dict(rows=_rows(seed=5, n=24, days=("2026-10-16",))),
    "empty": dict(rows=[]),
    "large_trusted": dict(rows=_rows(seed=11, n=900)),
}


def _run(mod, rows, symbol=""):
    payloads = _payloads(rows) + ["not-a-mapping", {"candidates": ["junk", 3]}]
    out = mod.build_quant_shadow_candidate_evaluation(iter(payloads), symbol=symbol)
    return json.dumps(out, ensure_ascii=False), mod.render_quant_shadow_candidate_evaluation_lines(out)


@pytest.mark.parametrize("scenario", sorted(SCENARIOS))
@pytest.mark.parametrize("symbol", ["", "005935"])
def test_evaluation_and_render_bytes_match_base(scenario, symbol, mods):
    base, current = mods
    assert _run(current, SCENARIOS[scenario]["rows"], symbol) == _run(base, SCENARIOS[scenario]["rows"], symbol)


def test_fixtures_exercise_non_trivial_branches(mods):
    _base, current = mods
    statuses = {json.loads(_run(current, s["rows"])[0])["no_trade_scorecard"]["status"] for s in SCENARIOS.values()}
    assert {"no_shadow_data", "trade_candidates_available"} <= statuses and len(statuses) >= 3
    big = json.loads(_run(current, SCENARIOS["large_trusted"]["rows"])[0])
    assert big["entry_lane_forward_outcomes"]["by_primary_lane"] and big["promotion_candidate"]["candidate"] != "hold"
    assert big["duplicate_candidate_count"] > 0 and big["shadow_readiness"]["status"]


@pytest.mark.parametrize("name", MOVED)
def test_each_moved_function_matches_base_on_direct_inputs(name, mods):
    base, current = mods
    rows = current.attach_forward_outcomes(_rows(seed=13, n=200))
    lanes = current._entry_lane_forward_outcomes(rows)
    cases = {
        "_mean": [([1.0, None, 2.5],), ([],)],
        "_checkpoint_value": [(r, "+5m", "return_pct") for r in rows[:30]] + [({}, "+5m", "x"), ({"shadow_forward_outcome": 1}, "EOD", "mae_pct")],
        "_forward_outcome_summary": [(rows,), ([],), (rows[:7],)],
        "_top_forward_groups": [({"a": rows[:40], "b": rows[40:90], "c": []},)],
        "_entry_lane_forward_outcomes": [(rows,), ([],)],
        "_scorecard_return_signal": [({"avg_return_15m_pct": "x", "avg_return_5m_pct": "0.3"},), ({},)],
        "_scorecard_rows": [(lanes["by_lane_subtype"],), (lanes["by_primary_lane"],)],
        "_named_forward_rows": [(lanes["by_lane_subtype"], {"pullback_quality:failed_pullback", "missing"})],
        "_no_trade_scorecard": [()],
        "_promotion_candidate": [(rows,), ([],), (rows[:3],)],
        "_shadow_readiness": [(rows, current._promotion_candidate(rows)), ([], {})],
    }
    kwargs = {"_scorecard_rows": [{"mode": "missed"}, {"mode": "blocked", "limit": 2}],
              "_no_trade_scorecard": [dict(candidates=rows, entry_lane_forward_outcomes=lanes, would_enter_count=0,
                                           opening_probe_would_enter=0, largecap_probe_would_enter=0),
                                      dict(candidates=rows, entry_lane_forward_outcomes="bad", would_enter_count=1,
                                           opening_probe_would_enter=0, largecap_probe_would_enter=0)]}
    for args in cases[name]:
        for kw in kwargs.get(name, [{}]):
            got, want = _outcome(getattr(current, name), *args, **kw), _outcome(getattr(base, name), *args, **kw)
            assert got == want, (name, kw)


def _outcome(fn, *a, **k):
    try:
        return ("ok", json.dumps(fn(*a, **k), ensure_ascii=False, default=repr))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


@pytest.mark.parametrize("bad", [
    [{"candidates": [{"shadow_forward_outcome": {"available": True, "checkpoints": {"+5m": {"status": "observed"}}},
                      "observed_count": "x"}]}],
    [{"candidates": [{"symbol": None, "candidate_day": 5, "shadow_forward_outcome": "nope"}]}],
])
def test_invalid_inputs_raise_or_return_like_base(bad, mods):
    base, current = mods
    assert _outcome(current.build_quant_shadow_candidate_evaluation, bad) == _outcome(base.build_quant_shadow_candidate_evaluation, bad)


def test_named_rows_bad_observed_count_raises_same_exception(mods):
    base, current = mods
    bad = [{"name": "pullback_quality:failed_pullback", "observed_count": "many"}]
    got = _outcome(current._named_forward_rows, bad, {"pullback_quality:failed_pullback"})
    assert got[0] == "exc" and got == _outcome(base._named_forward_rows, bad, {"pullback_quality:failed_pullback"})


def test_late_monkeypatch_of_facade_helpers_and_constants_is_honoured(mods, monkeypatch):
    base, current = mods
    results = []
    for m in (base, current):
        calls = []
        real = m._forward_outcome
        monkeypatch.setattr(m, "_forward_outcome", lambda row, _c=calls, _r=real: (_c.append(1), _r(row))[1])
        monkeypatch.setattr(m, "TRUSTED_FORWARD_MIN_COUNT", 5)
        monkeypatch.setattr(m, "PROMOTION_CANDIDATE_MIN_OBSERVED", 3)
        monkeypatch.setattr(m, "build_entry_quant_enforcement", lambda d: {"blocked": True, "behavior_effect": "patched"})
        out = _run(m, SCENARIOS["no_trade_mixed"]["rows"])
        results.append((len(calls), out))
    assert results[0] == results[1]
    doc = json.loads(results[1][1][0])
    assert doc["promotion_candidate"].get("behavior_effect") in ("patched", "recommendation_only")
    assert doc["shadow_readiness"]["sample_floor"] == 5 and doc["shadow_readiness"]["evaluated_floor"] == 3


def test_inner_sibling_calls_dispatch_through_the_facade(mods, monkeypatch):
    _base, current = mods
    monkeypatch.setattr(current, "_forward_outcome_summary", lambda rows: {"observed_count": len(rows), "avg_return_5m_pct": 1})
    groups = current._top_forward_groups({"x": [{}], "y": [{}, {}]})
    assert [g["name"] for g in groups] == ["y", "x"]


def test_streaming_loader_feeds_evaluation_lazily_with_bounded_memory(tmp_path, mods):
    base, current = mods
    reports = tmp_path / "reports"
    root = current.shadow_candidate_root_for_reports(reports)
    rows = _rows(seed=21, n=3000)
    for i, day in enumerate(("2026-10-15", "2026-10-16")):
        d = root / day
        d.mkdir(parents=True)
        for k, payload in enumerate(_payloads(rows[i::2], chunk=300)):
            (d / f"shadow_{k:03d}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    peaks, outs = [], []
    for m in (base, current):
        it = m.iter_quant_shadow_candidate_payloads(reports_root=reports, days=["2026-10-15", "2026-10-16"], keys=["generated_at", "candidates"])
        assert isinstance(it, types.GeneratorType)
        tracemalloc.start()
        out = m.build_quant_shadow_candidate_evaluation(it)
        peaks.append(tracemalloc.get_traced_memory()[1])
        tracemalloc.stop()
        outs.append(json.dumps(out, ensure_ascii=False))
    assert outs[0] == outs[1] and json.loads(outs[1])["payload_count"] == 12
    assert peaks[1] <= peaks[0] * 1.10 + 256 * 1024, peaks  # no extra materialization introduced


def test_facade_keeps_signatures_io_and_only_forwards_moved_bodies():
    base_src = subprocess.check_output(["git", "show", f"{BASE}:{PATH}"], cwd=ROOT).decode("utf-8-sig")
    cur_src = (ROOT / PATH).read_text(encoding="utf-8-sig")
    base_fns = {n.name: n for n in ast.parse(base_src).body if isinstance(n, ast.FunctionDef)}
    cur_fns = {n.name: n for n in ast.parse(cur_src).body if isinstance(n, ast.FunctionDef)}
    assert list(base_fns) == list(cur_fns)
    for name, node in cur_fns.items():
        assert ast.dump(node.args) == ast.dump(base_fns[name].args) and ast.dump(node.returns) == ast.dump(base_fns[name].returns)
        if name in MOVED:
            assert len(node.body) == 1 and f"_qsce_projection.{name}(" in ast.unparse(node.body[0])
        else:
            assert ast.dump(node) == ast.dump(base_fns[name]), name
    assert len(cur_src.splitlines()) < len(base_src.splitlines()) - 250


def test_projection_has_no_io_or_runtime_authority_imports():
    tree = ast.parse((ROOT / "libs/reporting/quant_shadow_candidate_projection.py").read_text(encoding="utf-8"))
    mods_ = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)} | \
        {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert mods_ == {"__future__", "collections", "typing"}
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    assert not names & {"open", "read_text", "write_text", "_read_json", "iter_json_array", "getenv", "environ", "Path",
                        "build_entry_quant_enforcement", *POLICY}
    assert sorted(n.name for n in tree.body if isinstance(n, ast.FunctionDef)) == sorted(MOVED)


def test_projection_is_independently_callable_with_a_stub_facade():
    stub = types.SimpleNamespace(
        _text=lambda v: "" if v is None else str(v).strip(), _bool=bool,
        _forward_outcome=lambda r: dict(r.get("o") or {}), _candidate_day=lambda r: r.get("d", ""),
        _checkpoint_value=lambda r, h, m: (r.get("o") or {}).get(h), _mean=lambda v: proj._mean(v, facade=None))
    stub._forward_outcome_summary = lambda rows: proj._forward_outcome_summary(rows, facade=stub)
    rows = [{"o": {"available": True, "+5m": 1.0}, "d": "D1"}, {"o": {"available": False}, "d": "D2"}]
    summary = proj._forward_outcome_summary(rows, facade=stub)
    assert summary["observed_count"] == 1 and summary["observed_count_by_horizon"]["+5m"] == 1
    assert summary["avg_return_5m_pct"] == 1.0 and summary["coverage"] == 0.5


@pytest.mark.parametrize("mode", ["missed", "blocked"])
def test_scorecard_ties_keep_base_secondary_order(mode, mods):
    base, current = mods
    sig = "0.3" if mode == "missed" else "-0.4"
    rows = [{"name": f"g{i}", "observed_count": n, "avg_return_15m_pct": sig, "avg_mfe_5m_pct": 0.1, "avg_mae_5m_pct": -0.2}
            for i, n in enumerate((12, 40, 25, 12))]
    got = current._scorecard_rows(rows, mode=mode, limit=4)
    assert got == base._scorecard_rows(rows, mode=mode, limit=4)
    assert [r["name"] for r in got] == (["g1", "g2", "g0", "g3"] if mode == "missed" else ["g0", "g3", "g2", "g1"])


@pytest.mark.parametrize("mode", [None, "observe", "enforce"])
@pytest.mark.parametrize("blockers", [None, "cost_edge_fail", "other_blocker"])
def test_env_policy_promotion_path_stays_in_facade_and_reads_env_at_call_time(mode, blockers, mods, monkeypatch):
    base, current = mods
    for name, value in (("QUANT_ENTRY_DECISION_MODE", mode), ("QUANT_ENTRY_ENFORCED_BLOCKERS", blockers)):
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    rows = _rows(seed=31, n=150)
    for name in POLICY:
        assert current.__dict__[name].__code__.co_filename.endswith("quant_shadow_candidate_evaluation.py")
    assert _run(current, rows) == _run(base, rows)
    promo = current._promotion_candidate(current.attach_forward_outcomes(rows))
    assert promo == base._promotion_candidate(base.attach_forward_outcomes(rows))
    assert current._shadow_readiness(rows, promo) == base._shadow_readiness(rows, promo)
