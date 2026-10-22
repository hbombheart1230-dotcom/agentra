"""P1.5 DEV-A Q8 trusted reaggregation: BASE (d7ab8294) vs current parity.

The frozen BASE facade is exec'd from Git beside the live one. Loaders and the shadow evaluation are replaced by the
same deterministic fakes on both (the facade keeps calling them), so payloads, Markdown, written bytes, exceptions and
the loader/evaluation/Path call sequence are compared without touching real reports. Seam tests patch one attribute
identically on both modules; mutation tests break the new owner and must be detected.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import types
from pathlib import Path

import pytest

import libs.reporting.evaluation.q8_trusted_reaggregation_projection_p15 as owner
import libs.reporting.q8_trusted_reaggregation as cur

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
PATH = "libs/reporting/q8_trusted_reaggregation.py"
_BASE: dict = {}


def base():
    if "mod" not in _BASE:
        src = subprocess.check_output(["git", "show", f"{BASE_SHA}:{PATH}"], cwd=ROOT).decode("utf-8")
        mod = types.ModuleType("_p15_q8_trusted_base_d7ab8294")
        mod.__file__ = str(ROOT / PATH)
        sys.modules[mod.__name__] = mod
        exec(compile(src, f"<base:{PATH}>", "exec"), mod.__dict__)
        _BASE["mod"] = mod
    return _BASE["mod"]


def _eval(n, *, allowed, status="promotion_review_ready", reasons=None, watch=(), dup=0.1, cov=0.8, scorecard_status="ok"):
    return {
        "payload_count": 1, "candidate_count": n, "deduped_candidate_count": n - 2, "duplicate_candidate_count": 2,
        "forward_outcome_available_count": n // 2, "forward_outcome_coverage": cov,
        "no_trade_scorecard": {"status": scorecard_status, "promotion_watchlist": list(watch)},
        "evaluation_trust_gate": {"status": status, "promotion_allowed": allowed, "duplicate_rate": dup,
                                  "block_reasons": reasons if reasons is not None else []},
    }


WATCH = [
    {"name": "vwap_reclaim", "observed_count": 1234, "candidate_count": 2000, "observed_day_count": 3,
     "avg_return_5m_pct": 0.5123456, "avg_return_15m_pct": None, "avg_mae_5m_pct": -1.25, "review_state": "watch"},
    "junk", None,
    {"name": "한글|pipe", "observed_count": "x", "candidate_count": None, "avg_return_5m_pct": 0, "review_state": ""},
]
CASES = {
    "gated_and_allowed": {
        "2026-06-01": _eval(50, allowed=False, status="blocked", reasons=["low_coverage", "dup"], watch=WATCH[:1]),
        "2026-06-02": _eval(80, allowed=True, watch=WATCH, dup=0.0, cov=1.0),
    },
    "all_blocked_legacy_reasons_key": {
        "2026-06-01": {**_eval(10, allowed=False, status="blocked"),
                       "evaluation_trust_gate": {"status": "blocked", "promotion_allowed": 0, "reasons": ["r1", 2]}},
        "2026-06-04": _eval(7, allowed=False, status="blocked", cov=0.0, dup=0.9),
    },
    "weird_values": {
        "2026-06-01": {"payload_count": "3", "candidate_count": None, "deduped_candidate_count": "12.0".split(".")[0],
                       "forward_outcome_coverage": "0.5", "no_trade_scorecard": ["not", "a", "mapping"],
                       "evaluation_trust_gate": "not-a-mapping"},
        "2026-06-03": _eval(5, allowed=True, scorecard_status=None, reasons=None, watch=[WATCH[3], {"name": None}]),
    },
    "no_payload_days": {},
    "unmeasurable_number": {"2026-06-01": {**_eval(5, allowed=True), "payload_count": "abc"}},
}
WINDOWS = [("2026-06-01", "2026-06-04"), ("2026-06-04", "2026-06-01"), ("2026-06-02T09:30", "2026-06-02"),
           ("2026-06-01", "2026-06-01"), ("2026-13-01", "2026-06-02"), ("junk", "2026-06-02")]


class Run:
    """Installs identical fakes on a facade and records every call that crosses the facade boundary."""

    def __init__(self, monkeypatch, mod, evals):
        self.calls = []
        self.mod = mod

        def load(*, reports_root, days):
            self.calls.append(("load", str(days), Path(reports_root).name))
            return [{"day": d, "eval": copy.deepcopy(evals[d])} for d in days if d in evals]

        def build(payloads):
            self.calls.append(("build", len(payloads)))
            if len(payloads) == 1:
                return copy.deepcopy(payloads[0]["eval"])
            merged = copy.deepcopy(payloads[-1]["eval"])
            merged["candidate_count"] = sum(p["eval"].get("candidate_count") or 0 for p in payloads if isinstance(p["eval"].get("candidate_count"), int))
            return merged

        monkeypatch.setattr(mod, "load_quant_shadow_candidate_payloads", load)
        monkeypatch.setattr(mod, "build_quant_shadow_candidate_evaluation", build)


def _outcome(fn):
    try:
        return ("ok", json.dumps(fn(), ensure_ascii=False, default=str))
    except Exception as exc:  # noqa: BLE001
        return ("exc", type(exc).__name__, str(exc))


def _both(monkeypatch, evals, fn):
    results = []
    for mod in (base(), cur):
        run = Run(monkeypatch, mod, evals)
        results.append((_outcome(lambda: fn(mod)), run.calls))
        monkeypatch.undo()
    return results


@pytest.mark.parametrize("window", WINDOWS, ids=[f"{a}..{b}" for a, b in WINDOWS])
@pytest.mark.parametrize("case", sorted(CASES))
def test_build_and_render_match_base(monkeypatch, case, window):
    start, end = window
    (b_build, b_calls), (c_build, c_calls) = _both(
        monkeypatch, CASES[case], lambda m: m.build_q8_trusted_reaggregation(reports_root=Path("reports"), start=start, end=end))
    assert c_build == b_build and c_calls == b_calls
    if b_build[0] == "ok":
        payload = json.loads(b_build[1])
        assert base().render_q8_trusted_reaggregation_markdown(payload) == cur.render_q8_trusted_reaggregation_markdown(payload)
        assert list(json.loads(c_build[1])) == list(payload)  # key order of the envelope


def test_gating_observability_is_reported_for_blocked_and_allowed_days(monkeypatch):
    (_, _), (c_build, _) = _both(monkeypatch, CASES["gated_and_allowed"],
                                 lambda m: m.build_q8_trusted_reaggregation(reports_root=Path("reports"), start="2026-06-01", end="2026-06-04"))
    payload = json.loads(c_build[1])
    assert [r["promotion_allowed"] for r in payload["daily"]] == [False, True]
    assert payload["aggregate"]["promotion_allowed_day_count"] == 1
    assert payload["daily"][0]["trust_reasons"] == ["low_coverage", "dup"] and payload["range"]["days_with_payloads"] == 2
    md = cur.render_q8_trusted_reaggregation_markdown(payload)
    assert "`blocked`" in md and "`True`" in md and "PROMOTE is not allowed unless" in md


@pytest.mark.parametrize("case", ["gated_and_allowed", "no_payload_days", "weird_values"])
def test_markdown_on_sparse_payloads_matches_base(case):
    payloads = [{}, {"range": [], "aggregate": "x", "daily": [{}, "row", {"promotion_watchlist": [None]}]},
                {"aggregate": {"promotion_watchlist": WATCH, "cumulative_trust_reasons": [1, None]}, "daily": [
                    {"day": "d", "candidate_count": "1,000", "trust_reasons": None, "promotion_watchlist": WATCH}]}]
    outcomes = []
    for payload in payloads:  # exceptions (e.g. a non-mapping daily row) must match BASE exactly too
        outcomes.append([_outcome(lambda m=mod: m.render_q8_trusted_reaggregation_markdown(payload)) for mod in (base(), cur)])
    assert all(b == c for b, c in outcomes)
    assert any(b[0] == "ok" for b, _ in outcomes) and any(b[0] == "exc" for b, _ in outcomes)


@pytest.mark.parametrize("case", ["gated_and_allowed", "weird_values", "no_payload_days"])
def test_write_bytes_return_value_and_path_order_match_base(tmp_path, monkeypatch, case):
    outcomes = []
    for label, mod in (("base", base()), ("cur", cur)):
        work = tmp_path / label
        Run(monkeypatch, mod, CASES[case])
        ops = []
        orig_mkdir, orig_write = Path.mkdir, Path.write_text
        monkeypatch.setattr(Path, "mkdir", lambda p, *a, **k: (ops.append(("mkdir", "<work>" if p.name == label else p.name, tuple(sorted(k.items())))), orig_mkdir(p, *a, **k))[1])
        monkeypatch.setattr(Path, "write_text", lambda p, data, *a, **k: (ops.append(("write_text", p.name, k.get("encoding"))), orig_write(p, data, *a, **k))[1])
        result = mod.write_q8_trusted_reaggregation(reports_root=work / "reports", start="2026-06-01", end="2026-06-04", output_dir=work / "out")
        monkeypatch.undo()
        files = {p.name: p.read_bytes() for p in sorted((work / "out").iterdir())}
        outcomes.append(({k: str(v.relative_to(work)) for k, v in result.items()}, ops, files))
    assert outcomes[0] == outcomes[1]
    stem = "q8_trusted_reaggregation_2026-06-01_to_2026-06-04"
    assert [(o[0], o[1]) for o in outcomes[1][1]] == [("mkdir", "out"), ("mkdir", "<work>"), ("mkdir", "out"),
                                                       ("write_text", f"{stem}.json"), ("write_text", f"{stem}.md")]
    assert sorted(outcomes[1][2]) == [f"{stem}.json", f"{stem}.md"]


# --- facade monkeypatch seams: the same patch on BASE and current must give the same output, different from unpatched ---


def _run_build_render(mod, evals, monkeypatch):
    Run(monkeypatch, mod, evals)
    payload = mod.build_q8_trusted_reaggregation(reports_root=Path("reports"), start="2026-06-01", end="2026-06-04")
    return json.dumps([payload, mod.render_q8_trusted_reaggregation_markdown(payload)], ensure_ascii=False, default=str)


SEAMS = [
    ("_fmt_pct", lambda mod: lambda value: "PCT"),
    ("_fmt_num", lambda mod: lambda value: "NUM"),
    ("_watchlist_rows", lambda mod: lambda scorecard: [{"name": "patched", "review_state": "p"}]),
    ("TRUSTED_FORWARD_MIN_COUNT", lambda mod: 7),
    ("TRUSTED_FORWARD_MIN_COVERAGE", lambda mod: 0.5),
    ("DUPLICATE_RATE_MAX", lambda mod: 0.25),
    ("PROMOTION_CANDIDATE_MIN_OBSERVED", lambda mod: 99),
    ("PROMOTION_CANDIDATE_MIN_DAYS", lambda mod: 9),
    ("_iter_days", lambda mod: lambda start, end: iter(["2026-06-02"])),
]


@pytest.mark.parametrize("name,factory", SEAMS, ids=[n for n, _ in SEAMS])
def test_facade_monkeypatch_seams_match_base(monkeypatch, name, factory):
    evals = CASES["gated_and_allowed"]
    unpatched = _run_build_render(cur, evals, monkeypatch)
    monkeypatch.undo()
    outputs = []
    for mod in (base(), cur):
        monkeypatch.setattr(mod, name, factory(mod))
        outputs.append(_run_build_render(mod, evals, monkeypatch))
        monkeypatch.undo()
    assert outputs[1] == outputs[0] and outputs[1] != unpatched


def test_patched_render_is_what_write_uses_like_base(tmp_path, monkeypatch):
    texts = []
    for label, mod in (("base", base()), ("cur", cur)):
        Run(monkeypatch, mod, CASES["gated_and_allowed"])
        monkeypatch.setattr(mod, "render_q8_trusted_reaggregation_markdown", lambda payload: "PATCHED-RENDER")
        paths = mod.write_q8_trusted_reaggregation(reports_root=tmp_path / "r", start="2026-06-01", end="2026-06-02", output_dir=tmp_path / label)
        texts.append(paths["markdown"].read_text(encoding="utf-8"))
        monkeypatch.undo()
    assert texts == ["PATCHED-RENDER", "PATCHED-RENDER"]


# --- mutation checks: owner changes must break parity (the comparison is not vacuous) ---------------------------


def _snapshot(mod, monkeypatch):
    return _run_build_render(mod, CASES["gated_and_allowed"], monkeypatch)


def _bind(monkeypatch, name, value):
    monkeypatch.setattr(owner, name, value)
    if hasattr(cur, name):  # names bound into the facade namespace at import
        monkeypatch.setattr(cur, name, value)


@pytest.mark.parametrize(
    "name,mutant",
    [
        ("daily_row_impl", lambda day, evaluation, *, facade: {**owner_daily(day, evaluation, facade), "promotion_allowed": True}),
        ("reaggregation_payload_impl", lambda **kw: {**owner_payload(**kw), "behavior_effect": "trading"}),
        ("render_q8_trusted_reaggregation_markdown_impl", lambda payload, *, facade: "# changed"),
        ("_fmt_pct", lambda value: "-"),
        ("_watchlist_rows", lambda scorecard: []),
    ],
)
def test_owner_mutants_are_detected(monkeypatch, name, mutant):
    expected = _snapshot(base(), monkeypatch)
    monkeypatch.undo()
    assert _snapshot(cur, monkeypatch) == expected  # green baseline first
    monkeypatch.undo()
    _bind(monkeypatch, name, mutant)
    assert _snapshot(cur, monkeypatch) != expected


_ORIG_DAILY, _ORIG_PAYLOAD = owner.daily_row_impl, owner.reaggregation_payload_impl


def owner_daily(day, evaluation, facade):
    return _ORIG_DAILY(day, evaluation, facade=facade)


def owner_payload(**kw):
    return _ORIG_PAYLOAD(**kw)
