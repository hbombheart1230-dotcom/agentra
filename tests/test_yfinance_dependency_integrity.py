"""Regression tests for the 2026-10-06 yfinance incident.

A missing yfinance install used to be swallowed (``except Exception: return []``),
so Q10/Q12/macro collectors reported empty-but-healthy results. These tests pin:

* a missing dependency is an explicit DataSourceDependencyError / explicit status,
  never an empty healthy result;
* a Q10 snapshot whose observations are ALL unavailable is not reported CAPTURED;
* strategy/scoring semantics are untouched (only status/reason fields change).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

import pytest

from libs.market import yfinance_support
from libs.market.yfinance_support import (
    DEPENDENCY_MISSING_REASON,
    DataSourceDependencyError,
    require_yfinance,
    try_yfinance,
    yfinance_dependency_status,
)

KST = timezone(timedelta(hours=9))


@pytest.fixture()
def no_yfinance(monkeypatch: pytest.MonkeyPatch):
    """Make `import yfinance` fail exactly like a missing install."""
    monkeypatch.setitem(sys.modules, "yfinance", None)
    yfinance_support._REPORTED.clear()
    yield
    yfinance_support._REPORTED.clear()


# ---------------------------------------------------------------- helper module


def test_require_yfinance_raises_explicit_error_when_missing(no_yfinance) -> None:
    with pytest.raises(DataSourceDependencyError) as info:
        require_yfinance()
    assert info.value.reason == DEPENDENCY_MISSING_REASON == "dependency_missing:yfinance"
    assert "requirements.txt" in str(info.value)
    assert isinstance(info.value, RuntimeError)


def test_dependency_status_probe_does_not_raise(no_yfinance) -> None:
    status = yfinance_dependency_status()
    assert status["available"] is False
    assert status["reason"] == DEPENDENCY_MISSING_REASON


def test_try_yfinance_logs_explicit_error_once_per_component(no_yfinance, caplog) -> None:
    with caplog.at_level(logging.ERROR, logger="libs.market.yfinance_support"):
        assert try_yfinance("component_a") is None
        assert try_yfinance("component_a") is None
        assert try_yfinance("component_b") is None
    messages = [r.getMessage() for r in caplog.records]
    assert sum("component=component_a" in m for m in messages) == 1
    assert sum("component=component_b" in m for m in messages) == 1
    assert all("DATA_SOURCE_DEPENDENCY_MISSING" in m and "dependency_missing:yfinance" in m for m in messages)


def test_yfinance_is_a_declared_requirement() -> None:
    requirements = (Path(__file__).resolve().parents[1] / "requirements.txt").read_text(encoding="utf-8")
    declared = [line.strip().lower() for line in requirements.splitlines() if line.strip() and not line.startswith("#")]
    assert any(line.startswith("yfinance") for line in declared)


# --------------------------------------------------------------------- Q12 / BTC


def test_q12_yf_rows_raises_instead_of_returning_empty(no_yfinance) -> None:
    from libs.reporting.baseline_btc_woori_tech.data_provider import _yf_rows

    with pytest.raises(DataSourceDependencyError):
        _yf_rows("BTC-USD", day="2026-10-06")


def test_q12_signal_rows_carry_explicit_dependency_error_without_crashing(no_yfinance, caplog) -> None:
    from libs.reporting.baseline_btc_woori_tech.data_provider import load_btc_signal_rows

    with caplog.at_level(logging.ERROR):
        payload = load_btc_signal_rows(day="2026-10-06")
    assert payload["available"] is False
    assert payload["fallback_reason"] == DEPENDENCY_MISSING_REASON
    assert payload["data_source_error"] == DEPENDENCY_MISSING_REASON
    assert any("DATA_SOURCE_DEPENDENCY_MISSING" in r.getMessage() for r in caplog.records)


def test_q12_0855_capture_reports_dependency_missing_not_generic_missing(no_yfinance, tmp_path: Path) -> None:
    from libs.reporting.baseline_btc_woori_tech.point_in_time_capture import (
        capture_paths,
        capture_q12_btc_0855_snapshot,
    )

    result = capture_q12_btc_0855_snapshot(
        day="2026-10-06", root=tmp_path, now=datetime(2026, 10, 6, 8, 55, 5, tzinfo=KST)
    )
    assert result["capture_status"] == "DEPENDENCY_MISSING"
    assert result["reason"] == DEPENDENCY_MISSING_REASON
    assert result["snapshot_submitted"] is False
    ledger = json.loads(capture_paths("2026-10-06", root=tmp_path)["ledger"].read_text(encoding="utf-8"))
    assert ledger["latest_status"] == "DEPENDENCY_MISSING"


def test_q12_0855_dependency_missing_is_not_terminal_and_can_still_capture(no_yfinance, monkeypatch, tmp_path: Path) -> None:
    from libs.reporting.baseline_btc_woori_tech.point_in_time_capture import capture_q12_btc_0855_snapshot

    now = datetime(2026, 10, 6, 8, 55, 5, tzinfo=KST)
    first = capture_q12_btc_0855_snapshot(day="2026-10-06", root=tmp_path, now=now)
    assert first["capture_status"] == "DEPENDENCY_MISSING"

    target = int(datetime(2026, 10, 6, 8, 54, tzinfo=KST).timestamp())
    second = capture_q12_btc_0855_snapshot(
        day="2026-10-06",
        root=tmp_path,
        now=now + timedelta(seconds=30),
        signal_loader=lambda *, day: {"sources": {"btc_usd": [{"ts": target, "price": 1.0}]}},
    )
    assert second["capture_status"] == "CAPTURED"


def test_q12_capture_script_exit_codes(monkeypatch, tmp_path: Path, capsys) -> None:
    from scripts import capture_q12_btc_0855_snapshot as script

    monkeypatch.setattr(sys, "argv", ["x", "--day", "2026-10-06", "--root", str(tmp_path), "--attempts", "3", "--retry-sec", "0"])
    calls = {"n": 0}

    def fake_capture(*, day: str, root: Path) -> dict[str, Any]:
        calls["n"] += 1
        return {"capture_status": "DEPENDENCY_MISSING", "reason": DEPENDENCY_MISSING_REASON, "error": "boom"}

    monkeypatch.setattr(script, "capture_q12_btc_0855_snapshot", fake_capture)
    monkeypatch.setattr(script, "load_env_file", lambda _path: None)
    assert script.main() == script.EXIT_DEPENDENCY_MISSING == 3
    assert calls["n"] == 1  # no pointless retries for a missing dependency
    assert "Q12 capture failed" in capsys.readouterr().err

    monkeypatch.setattr(
        script, "capture_q12_btc_0855_snapshot", lambda **_k: {"capture_status": "MISSING", "reason": "x"}
    )
    monkeypatch.setattr(sys, "argv", ["x", "--day", "2026-10-06", "--root", str(tmp_path), "--attempts", "1"])
    assert script.main() == 2


# --------------------------------------------------------------------------- Q10


class _Provider:
    def __init__(self, observations: Mapping[str, Mapping[str, Any]]) -> None:
        self._observations = observations

    def capture(self, *, as_of: datetime) -> Mapping[str, Any]:
        return self._observations


_UNAVAILABLE = {
    "sox": {"status": "UNAVAILABLE", "reason": "daily_history_missing"},
    "nvidia": {"status": "UNAVAILABLE", "reason": "daily_history_missing"},
    "usdkrw_0850": {"status": "UNAVAILABLE", "reason": "point_in_time_quote_missing"},
}


def _capture(tmp_path: Path, provider: Any, day: str = "2026-10-06") -> dict[str, Any]:
    from libs.reporting.baseline_samsung_hynix.forward_validation import capture_q10_preopen_snapshot

    return capture_q10_preopen_snapshot(
        day=day,
        reports_root=tmp_path / "reports",
        state_path=tmp_path / "state.json",
        now=datetime(2026, 10, 6, 8, 50, 5, tzinfo=KST),
        lead_market_provider=provider,
    )


def test_q10_all_unavailable_is_not_reported_captured(tmp_path: Path) -> None:
    result = _capture(tmp_path, _Provider(_UNAVAILABLE))
    assert result["q10_preopen_capture_status"] == "DATA_UNAVAILABLE"
    assert result["reason"] == "all_lead_market_observations_unavailable"
    snapshot = json.loads(Path(result["path"]).read_text(encoding="utf-8"))
    assert snapshot["capture_status"] == "DATA_UNAVAILABLE"
    assert snapshot["observation_summary"] == {"total": 3, "available": 0}
    # evidence is preserved and still immutable (no backfill / no recapture)
    assert set(snapshot["observations"]) == set(_UNAVAILABLE)
    again = _capture(tmp_path, _Provider({"sox": {"status": "AVAILABLE", "return_pct": 1.0}}))
    assert again["q10_preopen_capture_status"] == "DATA_UNAVAILABLE"


def test_q10_partial_data_is_still_captured(tmp_path: Path) -> None:
    observations = dict(_UNAVAILABLE)
    observations["sox"] = {"status": "AVAILABLE", "return_pct": 1.5, "current": 10.0, "previous": 9.0}
    result = _capture(tmp_path, _Provider(observations))
    assert result["q10_preopen_capture_status"] == "CAPTURED"
    assert result["reason"] == ""
    snapshot = json.loads(Path(result["path"]).read_text(encoding="utf-8"))
    assert snapshot["observation_summary"] == {"total": 3, "available": 1}
    assert snapshot["signals"]  # scoring still runs exactly as before


def test_q10_data_unavailable_snapshot_yields_no_controlled_lane_candidate(tmp_path: Path) -> None:
    """DATA_UNAVAILABLE gates the Q10 semiconductor lane off exactly like any non-CAPTURED snapshot."""
    import inspect

    from libs.runtime.controlled_mock_lanes import signals

    parameters = list(inspect.signature(signals.build_q10_semiconductor_candidate).parameters)
    assert "preopen" in parameters
    result = _capture(tmp_path, _Provider(_UNAVAILABLE))
    snapshot = json.loads(Path(result["path"]).read_text(encoding="utf-8"))
    assert snapshot["capture_status"] != "CAPTURED"


def test_q10_provider_raises_when_dependency_missing(no_yfinance) -> None:
    from libs.reporting.baseline_samsung_hynix.forward_validation.market_inputs import YFinanceLeadMarketProvider

    with pytest.raises(DataSourceDependencyError):
        YFinanceLeadMarketProvider().capture(as_of=datetime(2026, 10, 6, 8, 50, tzinfo=KST))


def test_q10_capture_does_not_persist_a_snapshot_when_dependency_missing(no_yfinance, tmp_path: Path) -> None:
    with pytest.raises(DataSourceDependencyError):
        _capture(tmp_path, None)
    assert not list((tmp_path / "reports").rglob("q10_preopen_signal_snapshot.json"))


def test_q10_capture_script_exit_codes(monkeypatch, tmp_path: Path, capsys) -> None:
    from scripts import capture_q10_preopen_snapshot as script

    monkeypatch.setattr(sys, "argv", ["x", "--day", "2026-10-06", "--reports-root", str(tmp_path)])
    monkeypatch.setattr(script, "load_env_file", lambda _path: None)

    def raise_missing(**_kwargs: Any) -> dict[str, Any]:
        raise DataSourceDependencyError("yfinance")

    monkeypatch.setattr(script, "capture_q10_preopen_snapshot", raise_missing)
    assert script.main() == script.EXIT_DEPENDENCY_MISSING == 3
    captured = capsys.readouterr()
    assert "DEPENDENCY_MISSING" in captured.out and "Q10 capture failed" in captured.err

    monkeypatch.setattr(
        script, "capture_q10_preopen_snapshot", lambda **_k: {"q10_preopen_capture_status": "DATA_UNAVAILABLE"}
    )
    assert script.main() == 2
    monkeypatch.setattr(script, "capture_q10_preopen_snapshot", lambda **_k: {"q10_preopen_capture_status": "CAPTURED"})
    assert script.main() == 0


# ------------------------------------------------------- macro / sentiment / news


def test_macro_snapshot_fails_loudly_when_dependency_missing(no_yfinance, tmp_path: Path) -> None:
    from libs.market.preopen_macro_snapshot import capture_preopen_macro_snapshot

    with pytest.raises(DataSourceDependencyError):
        capture_preopen_macro_snapshot(env_path=tmp_path / ".env", state_path=tmp_path / "state.json")


def test_macro_snapshot_with_injected_compute_does_not_need_yfinance(no_yfinance, tmp_path: Path) -> None:
    from libs.market.preopen_macro_snapshot import capture_preopen_macro_snapshot

    result = capture_preopen_macro_snapshot(
        env_path=tmp_path / ".env",
        state_path=tmp_path / "state.json",
        compute=lambda **_k: {"status": "ok", "source": "fixture", "ts": 1},
    )
    assert result["status"] == "ok"


def test_opening_macro_slot_records_explicit_dependency_failure(no_yfinance, tmp_path: Path) -> None:
    from libs.market.opening_macro_snapshot_collector import capture_slot

    day = "2026-10-06"
    scheduled = datetime(2026, 10, 6, 8, 50, tzinfo=KST)
    row = capture_slot(
        day=day,
        scheduled_at=scheduled,
        manifest_path=tmp_path / "manifest.json",
        macro_root=tmp_path / "macro",
        env_path=tmp_path / ".env",
        state_path=tmp_path / "state.json",
        now_fn=lambda: scheduled + timedelta(seconds=1),
    )
    assert row["status"] == "CAPTURE_FAILED"
    assert "dependency_missing:yfinance" in row["error"]


def test_global_sentiment_fetch_degrades_but_logs_explicit_error(no_yfinance, caplog) -> None:
    from libs.market.global_sentiment import _fetch_last2_closes_yfinance

    with caplog.at_level(logging.ERROR):
        assert _fetch_last2_closes_yfinance("^GSPC") is None
    assert any("component=global_sentiment" in r.getMessage() for r in caplog.records)


def test_news_fallback_degrades_but_logs_explicit_error(no_yfinance, caplog) -> None:
    from libs.news.news_pipeline import _fetch_yfinance_news_items

    with caplog.at_level(logging.ERROR):
        assert _fetch_yfinance_news_items("005930", {}) == []
    assert any("component=news_pipeline" in r.getMessage() for r in caplog.records)


def test_scanner_hydration_reports_dependency_reason_not_generic(no_yfinance, caplog) -> None:
    from libs.runtime.scanner_feature_hydration import _fetch_seed_rows

    with caplog.at_level(logging.ERROR):
        rows, reason = _fetch_seed_rows(
            "005930", policy={"scanner_feature_seed_with_yf": True}, state={"now_epoch": 1_790_000_000}
        )
    assert rows == []
    assert reason == DEPENDENCY_MISSING_REASON
    assert any("component=scanner_feature_hydration" in r.getMessage() for r in caplog.records)


# ------------------------------------------------ source-unavailable != dependency-missing


class _FakeYF:
    """Stand-in `yfinance` module: the library is installed, but the data source misbehaves."""

    def __init__(self, behaviour: str) -> None:
        self.behaviour = behaviour
        self.__version__ = "fake"

    def Ticker(self, _ticker: str):  # noqa: N802 (mirrors yfinance API)
        behaviour = self.behaviour

        class _T:
            def history(self, **_kwargs: Any):
                if behaviour == "raises":
                    raise RuntimeError("network down")
                import pandas as pd

                return pd.DataFrame()

            @property
            def news(self):
                return []

            @property
            def fast_info(self):
                raise RuntimeError("quote unavailable")

        return _T()


@pytest.mark.parametrize("behaviour", ["raises", "empty"])
def test_source_unavailable_is_not_a_dependency_error_q12(monkeypatch, behaviour: str) -> None:
    from libs.reporting.baseline_btc_woori_tech.data_provider import _yf_rows, load_btc_signal_rows

    monkeypatch.setitem(sys.modules, "yfinance", _FakeYF(behaviour))
    assert _yf_rows("BTC-USD", day="2026-10-06") == []  # normal empty result, no exception
    payload = load_btc_signal_rows(day="2026-10-06", include_research_context=False)
    assert payload["available"] is False
    assert payload["fallback_reason"] == "btc_and_crypto_proxy_unavailable"  # NOT dependency_missing
    assert payload["data_source_error"] == ""


@pytest.mark.parametrize("behaviour", ["raises", "empty"])
def test_source_unavailable_is_not_a_dependency_error_q10(monkeypatch, tmp_path: Path, behaviour: str) -> None:
    from libs.reporting.baseline_samsung_hynix.forward_validation.market_inputs import YFinanceLeadMarketProvider

    monkeypatch.setitem(sys.modules, "yfinance", _FakeYF(behaviour))
    observations = YFinanceLeadMarketProvider().capture(as_of=datetime(2026, 10, 6, 8, 50, 5, tzinfo=KST))
    assert observations  # no DataSourceDependencyError
    assert {row["status"] for row in observations.values()} == {"UNAVAILABLE"}
    assert {observations["sox"]["reason"]} == {"daily_history_missing"}  # source reason, not dependency
    result = _capture(tmp_path, YFinanceLeadMarketProvider())
    assert result["q10_preopen_capture_status"] == "DATA_UNAVAILABLE"  # data gap, distinct from DEPENDENCY_MISSING


def test_source_unavailable_is_not_a_dependency_error_loop_paths(monkeypatch, caplog) -> None:
    from libs.market.global_sentiment import _fetch_last2_closes_yfinance
    from libs.news.news_pipeline import _fetch_yfinance_news_items
    from libs.runtime.scanner_feature_hydration import _fetch_seed_rows

    monkeypatch.setitem(sys.modules, "yfinance", _FakeYF("empty"))
    yfinance_support._REPORTED.clear()
    with caplog.at_level(logging.ERROR):
        assert _fetch_last2_closes_yfinance("^GSPC") is None
        assert _fetch_yfinance_news_items("005930", {}) == []
        rows, reason = _fetch_seed_rows("005930", policy={"scanner_feature_seed_with_yf": True}, state={"now_epoch": 1_790_000_000})
    assert rows == [] and reason != DEPENDENCY_MISSING_REASON
    assert not any("DATA_SOURCE_DEPENDENCY_MISSING" in r.getMessage() for r in caplog.records)


def test_q12_capture_with_installed_but_empty_source_is_missing_not_dependency(monkeypatch, tmp_path: Path) -> None:
    from libs.reporting.baseline_btc_woori_tech.point_in_time_capture import capture_q12_btc_0855_snapshot

    monkeypatch.setitem(sys.modules, "yfinance", _FakeYF("empty"))
    result = capture_q12_btc_0855_snapshot(
        day="2026-10-06", root=tmp_path, now=datetime(2026, 10, 6, 8, 55, 5, tzinfo=KST)
    )
    assert result["capture_status"] == "MISSING"
    assert result["reason"] == "btc_usd_point_in_time_source_missing"
