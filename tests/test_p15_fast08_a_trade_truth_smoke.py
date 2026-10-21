"""FAST08 A8.6 characterization tests for trade_truth_resolver.

The module is already a single pure function with no I/O, so it was not restructured
(see the A8.6 patch note). These cases pin the canonical/fill provenance semantics
that report_truth_surface depends on, so a later refactor cannot silently turn a
fallback mark into realized PnL.
"""

from __future__ import annotations

import pytest

from libs.reporting.trade_truth_resolver import resolve_trade_truth


def test_non_mapping_and_empty_facts_are_unavailable_not_zero() -> None:
    for facts in (None, {}, "x", []):
        result = resolve_trade_truth(facts)  # type: ignore[arg-type]
        assert result["authority"] == "fallback_mark_only" and result["authoritative_pct"] is None
        assert result["authoritative_pnl_krw"] is None and result["confidence"] == "low"
        assert result["pnl_pct_display_role"] == "fallback_mark_only"
        assert result["warnings"] == ["realized_pnl_pct_unavailable_fallback_mark_only"]


def test_broker_day_authoritative_pnl_is_high_confidence_truth() -> None:
    result = resolve_trade_truth({"pnl": 1200, "pnl_pct": 0.012, "broker_day_authoritative": True, "pnl_truth_source": "kiwoom.order_pair"})
    assert result["authority"] == "broker_day" and result["confidence"] == "high"
    assert result["authoritative_pnl_krw"] == 1200 and result["authoritative_pct"] == 0.012
    assert result["pct_basis"] == "truth" and result["fallback_pct"] is None and result["fallback_role"] == ""
    assert result["broker_pnl_present"] is True and result["pnl_pct_is_unconfirmed"] is False


def test_local_realized_pnl_without_broker_day_is_medium_and_sourced() -> None:
    result = resolve_trade_truth({"pnl": "-300", "pnl_pct": -0.003, "pnl_truth_source": "local_ledger"})
    assert result["authority"] == "local_ledger" and result["confidence"] == "medium"
    assert result["pnl_value_present"] is True and result["authoritative_pct"] == -0.003
    assert result["warnings"] == []
    # A realized value with no named source reports the default source label, not a broker authority.
    assert resolve_trade_truth({"pnl": 5, "pnl_pct": 0.01})["authority"] == "unavailable"


def test_pct_only_observation_never_becomes_truth_without_pnl_value() -> None:
    result = resolve_trade_truth({"pnl_pct": 0.02, "pnl_truth_source": "estimate"})
    assert result["authoritative_pct"] is None and result["pnl_pct_display"] == 0.02
    assert result["pnl_pct_display_role"] == "fallback_mark_only" and result["authority"] == "fallback_mark_only"
    assert set(result["warnings"]) == {"realized_pnl_pct_unavailable_fallback_mark_only", "broker_day_pct_observation_only"}
    assert result["fallback_pct"] == 0.02 and result["fallback_role"] == "fallback_mark_only"


@pytest.mark.parametrize("pnl_value", [None, "", "-", "None", "null", "unavailable", "not_available", "  "])
def test_placeholder_pnl_values_are_not_present(pnl_value: object) -> None:
    result = resolve_trade_truth({"pnl": pnl_value, "pnl_pct": 0.01})
    assert result["pnl_value_present"] is False and result["authoritative_pnl_krw"] is None


def test_zero_pnl_is_a_real_value_when_stringified() -> None:
    # 0 is not in the placeholder set once stringified; only None/"" are treated as absent.
    result = resolve_trade_truth({"pnl": 0, "pnl_pct": 0.0, "pnl_truth_source": "local"})
    assert result["pnl_value_present"] is True and result["authoritative_pnl_krw"] == 0


def test_fallback_pct_source_is_replaced_by_mark_to_buy_price() -> None:
    facts = {"data_source": {"pnl_pct": "Fallback"}, "pnl_pct": 0.5, "broker_buy_price": 100, "account_mark_price": 102, "monitor_mark_price": 110}
    result = resolve_trade_truth(facts)
    assert result["pnl_pct_is_fallback"] is True and result["pnl_pct_display"] == pytest.approx(0.02)
    assert result["authoritative_pct"] is None and result["pnl_pct_display_role"] == "fallback_mark_only"
    # An unusable account mark falls back to the monitor mark.
    monitor = resolve_trade_truth({**facts, "account_mark_price": 0})
    assert monitor["pnl_pct_display"] == pytest.approx(0.10)
    # No valid buy or mark price leaves the display empty instead of inventing a value.
    none = resolve_trade_truth({"data_source": {"pnl_pct": "fallback"}, "broker_buy_price": 0, "account_mark_price": 5})
    assert none["pnl_pct_display"] is None and none["authoritative_pct"] is None


def test_account_snapshot_estimate_without_valid_fill_price_is_treated_as_fallback() -> None:
    base = {"data_source": {"pnl_pct": "broker_fill_account_snapshot_estimate"}, "pnl_pct": 0.9,
            "broker_buy_price": 200, "account_mark_price": 210}
    assert resolve_trade_truth({**base, "broker_fill_price": 0})["pnl_pct_is_fallback"] is True
    assert resolve_trade_truth(base)["pnl_pct_display"] == pytest.approx(0.05)
    valid = resolve_trade_truth({**base, "broker_fill_price": 205, "broker_day_authoritative": True, "pnl_truth_source": "kiwoom"})
    assert valid["pnl_pct_is_fallback"] is False and valid["authoritative_pct"] == 0.9 and valid["authority"] == "broker_day"


def test_broker_day_flag_without_a_value_or_source_is_not_authority() -> None:
    # v1 field meanings are unchanged (authority/confidence stay low, pct keeps the "truth" basis);
    # A9 only adds a warning that makes the contradiction visible.
    result = resolve_trade_truth({"pnl_pct": 0.03, "broker_day_authoritative": True})
    assert result["authority"] == "unavailable" and result["confidence"] == "low"
    assert result["broker_pnl_present"] is False and result["pnl_value_present"] is False
    assert result["pct_basis"] == "truth" and result["authoritative_pct"] == 0.03
    assert result["warnings"] == ["broker_day_flag_without_pnl_value_or_truth_source"]
    assert result["schema_version"] == "trade_truth_resolution.v1"


def test_a9_warning_is_absent_when_backed_or_not_claimed() -> None:
    code = "broker_day_flag_without_pnl_value_or_truth_source"
    backed_by_value = resolve_trade_truth({"pnl": 10, "pnl_pct": 0.01, "broker_day_authoritative": True})
    backed_by_source = resolve_trade_truth({"pnl_pct": 0.01, "broker_day_authoritative": True, "pnl_truth_source": "kiwoom"})
    not_claimed = resolve_trade_truth({"pnl_pct": 0.01, "pnl_truth_source": "kiwoom"})
    no_pct = resolve_trade_truth({"broker_day_authoritative": True})
    fallback = resolve_trade_truth({"broker_day_authoritative": True, "pnl_pct": 0.5, "data_source": {"pnl_pct": "fallback"},
                                    "broker_buy_price": 100, "account_mark_price": 101})
    for result in (backed_by_value, backed_by_source, not_claimed, no_pct, fallback):
        assert code not in result["warnings"]
    assert backed_by_source["authority"] == "broker_day" and backed_by_value["confidence"] == "high"


def test_a9_only_the_warning_list_differs_from_the_v1_contract() -> None:
    result = resolve_trade_truth({"pnl_pct": 0.03, "broker_day_authoritative": True})
    assert set(result) == {"schema_version", "authoritative_pnl_krw", "authoritative_pct", "pct_basis", "authority",
                           "fallback_pct", "fallback_role", "confidence", "warnings", "broker_pnl_present",
                           "pnl_value_present", "pnl_pct", "pnl_pct_display", "pnl_pct_display_role",
                           "pnl_pct_is_fallback", "pnl_pct_is_unconfirmed"}
