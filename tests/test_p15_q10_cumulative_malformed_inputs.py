"""P15-1 (2026-10-29 C02): build_cumulative isolates non-object JSON / polluted outcomes (read-only, tmp_path only)."""
from __future__ import annotations

import hashlib
import json

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation.contracts import ACTIVATION_DAY
from libs.reporting.baseline_samsung_hynix.forward_validation.cumulative import build_cumulative

FROZEN_VALID_OUTPUT = json.loads(r'''{"day_count": 2, "days": ["2026-09-01", "2026-09-02"], "observed_outcome_count": 6, "prospective_start_day": "2026-08-31", "schema_version": "q10_korea_lead_market_cumulative.v1", "summary": [{"average_eod_return_pct": 0.5, "average_mae_pct": 0.0, "average_mfe_pct": 0.0, "average_return_pct": 0.5, "evaluation_bucket": "SAMSUNG_SPECIFIC_EVENT", "extension_state": "N/A", "max_drawdown_pct": 0.0, "median_return_pct": 0.5, "policy": "ENTRY_0905", "profit_factor": "INF", "target": "kospi", "trade_count": 1, "win_rate": 100.0}, {"average_eod_return_pct": -0.25, "average_mae_pct": -0.625, "average_mfe_pct": 1.0, "average_return_pct": -0.25, "evaluation_bucket": "LEAD_MARKET_SIGNAL", "extension_state": "N/A", "max_drawdown_pct": -3.0, "median_return_pct": 0.0, "policy": "ENTRY_0900", "profit_factor": 0.75, "target": "samsung", "trade_count": 4, "win_rate": 50.0}, {"average_eod_return_pct": 1.0, "average_mae_pct": 0.0, "average_mfe_pct": 0.0, "average_return_pct": 1.0, "evaluation_bucket": "LEAD_MARKET_SIGNAL", "extension_state": "EXTENDED", "max_drawdown_pct": 0.0, "median_return_pct": 1.0, "policy": "ENTRY_0903", "profit_factor": "INF", "target": "sk_hynix", "trade_count": 1, "win_rate": 100.0}]}''')
GOOD = {"target": "samsung", "policy": "ENTRY_0900", "status": "OBSERVED", "net_eod_return_pct": 2.0, "mfe_pct": 3.0, "mae_pct": -0.5}


def put(root, day, payload):
    p = root / day / "q10_forward_validation" / "q10_shadow_entry_comparison.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")
    return p


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}, sorted(str(p.relative_to(root)) for p in root.rglob("*"))


def test_mixed_directory_keeps_only_the_one_valid_observed_row_and_changes_nothing(tmp_path):
    put(tmp_path, "2026-09-01", "[]")                                                      # (a) non-object top level
    put(tmp_path, "2026-09-02", "null")
    put(tmp_path, "2026-09-03", '"text"')
    put(tmp_path, "2026-09-04", {"day": "2026-09-04", "outcomes": "not-a-list"})            # (b) outcomes not a list
    put(tmp_path, "2026-09-05", {"day": "2026-09-05", "outcomes": {"a": GOOD}})             # (b) mapping instead of list
    put(tmp_path, "2026-09-06", {"day": "2026-09-06", "outcomes": [None, 7, {}, "x", [1], GOOD | {"status": "PENDING"}]})   # (c) non-Mapping rows, {} and PENDING
    put(tmp_path, "2026-09-07", "{broken")                                                 # (d) corrupt JSON
    put(tmp_path, "2026-09-08", {"day": "2026-09-08", "outcomes": [GOOD]})                 # (e) the only valid file
    put(tmp_path, "2026-08-30", {"day": "2026-08-30", "outcomes": [GOOD]})                 # before ACTIVATION_DAY
    assert "2026-08-30" < ACTIVATION_DAY
    before = snapshot(tmp_path)
    out = build_cumulative(tmp_path)
    assert snapshot(tmp_path) == before                                                    # inputs and directory listing untouched
    assert out["day_count"] == 1 and out["days"] == ["2026-09-08"] and out["observed_outcome_count"] == 1
    assert len(out["summary"]) == 1 and out["summary"][0]["trade_count"] == 1 and out["summary"][0]["average_return_pct"] == 2.0


@pytest.mark.parametrize("raw", ["[]", "null", '"text"', "7", "true", "[null, 7, {}]"])
def test_each_non_object_top_level_alone_gives_the_empty_result(tmp_path, raw):
    put(tmp_path, "2026-09-01", raw)
    out = build_cumulative(tmp_path)
    assert out["day_count"] == 0 and out["days"] == [] and out["observed_outcome_count"] == 0 and out["summary"] == []


@pytest.mark.parametrize("outcomes", [None, [], "x", 7, {"k": 1}, [None], [7], [[]], ["OBSERVED"], [{}], [{"status": "PENDING", "net_eod_return_pct": 1.0}]])
def test_polluted_or_empty_outcomes_never_raise_and_add_nothing(tmp_path, outcomes):
    put(tmp_path, "2026-09-01", {"day": "2026-09-01", "outcomes": outcomes})
    out = build_cumulative(tmp_path)
    assert out["observed_outcome_count"] == 0 and out["summary"] == [] and out["days"] == []


def test_dates_are_sorted_and_a_bad_day_between_good_days_does_not_stop_the_scan(tmp_path):
    put(tmp_path, "2026-09-03", {"day": "2026-09-03", "outcomes": [GOOD]})
    put(tmp_path, "2026-09-02", "[]")
    put(tmp_path, "2026-09-01", {"day": "2026-09-01", "outcomes": [GOOD]})
    out = build_cumulative(tmp_path)
    assert out["days"] == ["2026-09-01", "2026-09-03"] and out["day_count"] == 2 and out["observed_outcome_count"] == 2


def test_missing_root_and_activation_day_boundary(tmp_path):
    assert build_cumulative(tmp_path / "none")["summary"] == []
    put(tmp_path, ACTIVATION_DAY, {"day": ACTIVATION_DAY, "outcomes": [GOOD]})
    assert build_cumulative(tmp_path)["days"] == [ACTIVATION_DAY]                          # the activation day itself is included


def test_valid_input_output_is_byte_identical_to_the_pre_change_frozen_json(tmp_path):
    def o(t, pol, r, **k):
        return {"target": t, "policy": pol, "status": "OBSERVED", "net_eod_return_pct": r, **k}

    put(tmp_path, "2026-09-01", {"day": "2026-09-01", "outcomes": [o("samsung", "ENTRY_0900", 2.0, mfe_pct=3.0, mae_pct=-0.5), o("samsung", "ENTRY_0900", -1.0, mfe_pct=1.0, mae_pct=-2.0),
                                                                    o("samsung", "ENTRY_0900", 5.0) | {"status": "PENDING"}, o("sk_hynix", "ENTRY_0903", 1.0, extension_state="EXTENDED"),
                                                                    o("kospi", "ENTRY_0905", 0.5, evaluation_bucket="SAMSUNG_SPECIFIC_EVENT")]})
    put(tmp_path, "2026-09-02", {"day": "2026-09-02", "outcomes": [o("samsung", "ENTRY_0900", 1.0), o("samsung", "ENTRY_0900", -3.0, mfe_pct=None, mae_pct="")]})
    put(tmp_path, "2026-08-30", {"day": "2026-08-30", "outcomes": [o("samsung", "ENTRY_0900", 9.0)]})
    assert json.loads(json.dumps(build_cumulative(tmp_path), sort_keys=True)) == FROZEN_VALID_OUTPUT


def test_schema_keys_and_signature_are_unchanged(tmp_path):
    out = build_cumulative(tmp_path)
    assert set(out) == {"schema_version", "prospective_start_day", "day_count", "days", "observed_outcome_count", "summary"} and out["schema_version"] == "q10_korea_lead_market_cumulative.v1"
    import inspect
    assert list(inspect.signature(build_cumulative).parameters) == ["root"]
