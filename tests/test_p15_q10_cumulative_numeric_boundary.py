"""P15-2 (2026-10-29 C02): build_cumulative numeric boundary - OBSERVED rows without a usable return are excluded, never zero-filled."""
from __future__ import annotations

import json
import math

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation.cumulative import build_cumulative


def put(root, day, outcomes, raw=None):
    p = root / day / "q10_forward_validation" / "q10_shadow_entry_comparison.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(raw if raw is not None else json.dumps({"day": day, "outcomes": outcomes}), encoding="utf-8")


def row(ret, **kw):
    return {"target": "samsung", "policy": "ENTRY_0900", "status": "OBSERVED", "net_eod_return_pct": ret, **kw}


def test_two_valid_rows_mixed_with_missing_and_non_numeric_returns(tmp_path):
    put(tmp_path, "2026-09-01", [row(2.0, mfe_pct=3.0, mae_pct=-0.5), row(-1.0, mfe_pct=1.0, mae_pct=-2.0), row(None, mfe_pct=99.0, mae_pct=-99.0), row("bad", mfe_pct=99.0), row("", mfe_pct=99.0),
                                 {k: v for k, v in row(0).items() if k != "net_eod_return_pct"}, row([1], mfe_pct=99.0), row({"x": 1})])
    out = build_cumulative(tmp_path)
    (s,) = out["summary"]
    assert s["trade_count"] == 2 and s["average_return_pct"] == 0.5 and s["median_return_pct"] == 0.5 and s["profit_factor"] == 2.0 and s["win_rate"] == 50.0
    assert s["average_mfe_pct"] == 2.0 and s["average_mae_pct"] == -1.25 and s["average_eod_return_pct"] == 0.5
    assert out["observed_outcome_count"] == 2 and out["day_count"] == 1 and out["days"] == ["2026-09-01"]


def test_a_day_with_only_unusable_returns_is_not_counted_as_a_day(tmp_path):
    put(tmp_path, "2026-09-01", [row(None), row("bad")])
    put(tmp_path, "2026-09-02", [row(1.5)])
    out = build_cumulative(tmp_path)
    assert out["days"] == ["2026-09-02"] and out["day_count"] == 1 and out["observed_outcome_count"] == 1


def test_no_valid_rows_gives_empty_summary_zero_counts_and_no_exception(tmp_path):
    put(tmp_path, "2026-09-01", [row(None), row("bad"), row({})])
    out = build_cumulative(tmp_path)
    assert out["summary"] == [] and out["observed_outcome_count"] == 0 and out["day_count"] == 0 and out["days"] == []


def test_zero_is_a_valid_return_not_a_missing_one(tmp_path):
    put(tmp_path, "2026-09-01", [row(0.0), row(0), row("0"), row("1.5")])
    (s,) = build_cumulative(tmp_path)["summary"]
    assert s["trade_count"] == 4 and s["average_return_pct"] == 0.375 and s["win_rate"] == 25.0           # numeric strings are accepted by float() as before


def test_missing_mfe_mae_keep_their_historical_meaning_of_zero(tmp_path):
    put(tmp_path, "2026-09-01", [row(1.0, mfe_pct=4.0, mae_pct=-2.0), row(1.0), row(1.0, mfe_pct=None, mae_pct=""), row(1.0, mfe_pct=0, mae_pct=0.0)])
    (s,) = build_cumulative(tmp_path)["summary"]
    assert s["average_mfe_pct"] == 1.0 and s["average_mae_pct"] == -0.5


def test_unparseable_mfe_mae_on_an_otherwise_valid_row_is_treated_as_missing_not_fatal(tmp_path):
    put(tmp_path, "2026-09-01", [row(1.0, mfe_pct="bad", mae_pct=[1]), row(3.0, mfe_pct=2.0, mae_pct=-2.0)])
    (s,) = build_cumulative(tmp_path)["summary"]
    assert s["trade_count"] == 2 and s["average_return_pct"] == 2.0 and s["average_mfe_pct"] == 1.0 and s["average_mae_pct"] == -1.0


def test_groups_are_independent_and_sorted_when_one_group_loses_all_rows(tmp_path):
    put(tmp_path, "2026-09-01", [row(1.0), {**row(None), "target": "kospi"}, {**row(2.0), "target": "sk_hynix", "policy": "ENTRY_0903"}])
    out = build_cumulative(tmp_path)
    assert [(g["target"], g["policy"]) for g in out["summary"]] == [("samsung", "ENTRY_0900"), ("sk_hynix", "ENTRY_0903")] and out["observed_outcome_count"] == 2


def test_reported_case_nan_and_infinity_returns_still_flow_through_unchanged(tmp_path):
    """Reported, NOT extended: JSON NaN/Infinity parse to float and are aggregated as-is (average nan/inf) - a numeric-policy decision for C03/C05."""
    put(tmp_path, "2026-09-01", None, raw='{"day":"2026-09-01","outcomes":[{"status":"OBSERVED","target":"a","policy":"p","net_eod_return_pct":NaN},'
                                          '{"status":"OBSERVED","target":"b","policy":"p","net_eod_return_pct":Infinity},{"status":"OBSERVED","target":"c","policy":"p","net_eod_return_pct":1.0}]}')
    out = build_cumulative(tmp_path)
    by = {g["target"]: g for g in out["summary"]}
    assert out["observed_outcome_count"] == 3 and math.isnan(by["a"]["average_return_pct"]) and math.isinf(by["b"]["average_return_pct"]) and by["c"]["average_return_pct"] == 1.0
