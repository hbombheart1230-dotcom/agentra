"""P15 C02-2: Q9 comparison isolates non-object files, non-list candidates and malformed ranks locally."""
from __future__ import annotations

import hashlib
import json

import pytest

from libs.reporting.baseline_samsung_hynix import q9_comparison as q9
from libs.reporting.baseline_samsung_hynix.contracts import HORIZONS

DAY = "2026-10-20"
DRAG = 0.15


def _row(role, ret, rank=None, selected=False, window="w1", **kw):
    row = {"q9_decision_id": window, "q9_decision_role": role, "symbol": "005930", "_ret": ret, "q9_selected": selected, **kw}
    if rank is not None:
        row["rank"] = rank
    return row


def _fake_attach(rows, *, minute_rows_by_symbol=None):
    out = []
    for r in rows:
        r = dict(r)
        r["shadow_forward_outcome"] = {"checkpoints": {h: {"status": "observed", "return_pct": r["_ret"]} for h in HORIZONS}}
        out.append(r)
    return out


@pytest.fixture
def fakes(monkeypatch):
    calls = []

    def fake_candles(rows, **kw):
        calls.append(kw)
        return {}

    monkeypatch.setattr(q9, "load_q9_forward_candles", fake_candles)
    monkeypatch.setattr(q9, "attach_forward_outcomes", _fake_attach)
    return calls


def _write(root, name, text):
    (root / DAY).mkdir(parents=True, exist_ok=True)
    (root / DAY / name).write_text(text, encoding="utf-8")


def _good_payload():
    return {"generated_at": "t", "q9_decision_candidates": [
        _row("P_SCANNER_PRE_STRATEGIST_UNIVERSE", 1.0, rank=1),
        _row("A_SCANNER_CONTROL", 9.0, rank="oops"), _row("A_SCANNER_CONTROL", 2.0, rank=1),
        _row("B_STRATEGIST_RANKED", 5.0, rank=1), _row("B_STRATEGIST_RANKED", 7.0, rank=3, selected=True),
        _row("C_COMMANDER_FINAL", 3.0, rank=1, q9_commander_decision="approve"),
        "junk", None, {"q9_decision_role": "UNKNOWN_ROLE"},
    ]}


def _hashes(root):
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def _run(root, **kw):
    return q9.build_q9_role_comparison(day=DAY, baseline_summary={}, cost_pct=0.1, slippage_pct=0.05, q9_root=root, **kw)


def _role(out, role, horizon=HORIZONS[0]):
    return next(r for r in out["roles"] if r["role"] == role and r["horizon"] == horizon)


def test_malformed_files_and_bad_rank_do_not_abort_valid_window(tmp_path, fakes):
    root = tmp_path / "q9"
    _write(root, "a_null.json", "null")
    _write(root, "b_list.json", "[]")
    _write(root, "c_str.json", '"text"')
    _write(root, "d_obj_candidates.json", json.dumps({"q9_decision_candidates": {"x": 1}}))
    _write(root, "e_broken.json", "{not json")
    _write(root, "f_good.json", json.dumps(_good_payload()))
    before = _hashes(root)
    out = _run(root, state_path=tmp_path / "s.json")
    assert _hashes(root) == before
    assert out["decision_window_count"] == 1 and out["comparable_complete_window_count"] == 1
    assert len(out["roles"]) == 4 * len(HORIZONS)
    for h in HORIZONS:
        a = _role(out, "A_SCANNER_CONTROL", h)                           # rank=1 row beats rank="oops" (sentinel 999)
        assert a["q9_net"]["count"] == 1 and a["q9_net"]["expectancy_pct"] == pytest.approx(2.0 - DRAG)
        b = _role(out, "B_STRATEGIST_RANKED", h)                         # explicit q9_selected wins over best rank
        assert b["q9_net"]["expectancy_pct"] == pytest.approx(7.0 - DRAG)
        c = _role(out, "C_COMMANDER_FINAL", h)
        assert c["active_candidate_count"] == 1 and c["q9_net"]["expectancy_pct"] == pytest.approx(3.0 - DRAG)
        assert _role(out, "P_SCANNER_PRE_STRATEGIST_UNIVERSE", h)["q9_net"]["expectancy_pct"] == pytest.approx(1.0 - DRAG)
    assert len(fakes) == 1


@pytest.mark.parametrize("bad", ["oops", None, float("nan"), float("inf"), [], {}, 0, ""])
def test_bad_rank_values_sort_last_but_never_raise(tmp_path, fakes, bad):
    root = tmp_path / "q9"
    payload = _good_payload()
    payload["q9_decision_candidates"] = [r for r in payload["q9_decision_candidates"] if not (isinstance(r, dict) and r.get("q9_decision_role") == "A_SCANNER_CONTROL")]
    payload["q9_decision_candidates"] += [_row("A_SCANNER_CONTROL", 9.0, rank=bad), _row("A_SCANNER_CONTROL", 2.0, rank=5)]
    _write(root, "good.json", json.dumps(payload, allow_nan=True))
    out = _run(root, state_path=tmp_path / "s.json")
    assert _role(out, "A_SCANNER_CONTROL")["q9_net"]["expectancy_pct"] == pytest.approx(2.0 - DRAG)


def test_all_bad_ranks_keep_original_order_tie_break(tmp_path, fakes):
    root = tmp_path / "q9"
    payload = _good_payload()
    payload["q9_decision_candidates"] = [r for r in payload["q9_decision_candidates"] if not (isinstance(r, dict) and r.get("q9_decision_role") == "A_SCANNER_CONTROL")]
    payload["q9_decision_candidates"] += [_row("A_SCANNER_CONTROL", 4.0, rank="x"), _row("A_SCANNER_CONTROL", 8.0, rank="y")]
    _write(root, "good.json", json.dumps(payload))
    assert _role(_run(root, state_path=tmp_path / "s.json"), "A_SCANNER_CONTROL")["q9_net"]["expectancy_pct"] == pytest.approx(4.0 - DRAG)


def test_valid_rank_ordering_and_string_numeric_rank_unchanged(tmp_path, fakes):
    root = tmp_path / "q9"
    payload = _good_payload()
    payload["q9_decision_candidates"] = [r for r in payload["q9_decision_candidates"] if not (isinstance(r, dict) and r.get("q9_decision_role") == "A_SCANNER_CONTROL")]
    payload["q9_decision_candidates"] += [_row("A_SCANNER_CONTROL", 9.0, rank="3"), _row("A_SCANNER_CONTROL", 6.0, rank="2.0"), _row("A_SCANNER_CONTROL", 1.0, rank=4)]
    _write(root, "good.json", json.dumps(payload))
    assert _role(_run(root, state_path=tmp_path / "s.json"), "A_SCANNER_CONTROL")["q9_net"]["expectancy_pct"] == pytest.approx(6.0 - DRAG)


def test_incomplete_window_stays_excluded_and_missing_day_is_empty(tmp_path, fakes):
    root = tmp_path / "q9"
    _write(root, "partial.json", json.dumps({"q9_decision_candidates": [_row("A_SCANNER_CONTROL", 1.0, rank=1)]}))
    out = _run(root, state_path=tmp_path / "s.json")
    assert out["decision_window_count"] == 1 and out["comparable_complete_window_count"] == 0
    empty = q9.build_q9_role_comparison(day="2099-01-01", baseline_summary={}, cost_pct=0.1, slippage_pct=0.05, q9_root=root, state_path=tmp_path / "s.json")
    assert empty["decision_window_count"] == 0 and len(empty["roles"]) == 4 * len(HORIZONS)
