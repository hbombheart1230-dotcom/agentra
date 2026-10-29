"""P15-4 (2026-10-29 C02): build_q10_forward_validation through the REAL collaborators, every path under tmp_path.

Only the provider (fake LeadMarketProvider) and the Kiwoom index collector module (in-memory ABSENT) are replaced; reaction reader,
expected/actual, shadow comparison, cumulative and report renderer are the production functions with their original signatures.
"""
from __future__ import annotations

import hashlib
import json
import socket
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from libs.reporting.baseline_samsung_hynix.forward_validation import pipeline as pl
from libs.reporting.baseline_samsung_hynix.forward_validation.contracts import ACTIVATION_DAY, PROGRAM_ID, SCHEMA_VERSION

KST = timezone(timedelta(hours=9))
DAY = "2026-10-29"
RETURN_KEYS = {"q10_forward_validation_status", "q10_preopen_snapshot", "q10_actual_reactions", "q10_expected_vs_actual", "q10_shadow_comparison", "q10_forward_validation_report", "q10_forward_validation_cumulative"}


@pytest.fixture(autouse=True)
def _isolation(monkeypatch, tmp_path):
    def boom(*a, **k):
        raise AssertionError("network attempt / real provider constructed")

    monkeypatch.setattr(socket.socket, "connect", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(pl, "YFinanceLeadMarketProvider", boom)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)                                                                       # any CWD-relative write would land here and be detected
    mod = types.ModuleType("libs.market.q10_index_observation_collector")
    mod.observation_for_slot = lambda day, slot, root=None: {"availability": "MISSING", "never_attempted": True}
    mod._has_verification_evidence = lambda indices, **kw: True
    monkeypatch.setitem(sys.modules, "libs.market.q10_index_observation_collector", mod)


class FakeProvider:
    def __init__(self):
        self.calls = []

    def capture(self, *, as_of):
        self.calls.append(as_of)
        row = {"status": "AVAILABLE", "return_pct": 6.0, "current": 100.0, "previous": 94.0, "three_day_return_pct": 1.0}
        return {k: dict(row) for k in ("sox", "nvidia", "micron", "samsung", "sk_hynix", "nasdaq", "sp500", "us10y", "vix", "hynix_adr")}


def at(h, m, s=0, day=DAY):
    y, mo, d = map(int, day.split("-"))
    return datetime(y, mo, d, h, m, s, tzinfo=KST)


def run(tmp_path, provider, *, day=DAY, now=None, candle_map=None):
    out_dir = tmp_path / "reports" / "evaluation" / "baseline_samsung_hynix" / day
    return out_dir, pl.build_q10_forward_validation(day=day, output_dir=out_dir, state_path=tmp_path / "state.json", macro_root=tmp_path / "macro", candle_map=candle_map or {},
                                                    cost_pct=0, slippage_pct=0, now=now or at(8, 51), lead_market_provider=provider)


def tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*")) if p.is_file()}


def test_six_returned_paths_exist_inside_tmp_path_with_expected_fields(tmp_path):
    p = FakeProvider()
    out_dir, res = run(tmp_path, p)
    assert set(res) == RETURN_KEYS and res["q10_forward_validation_status"] == "CAPTURED" and len(p.calls) == 1
    paths = {k: Path(v) for k, v in res.items() if k != "q10_forward_validation_status"}
    assert len(paths) == 6
    for k, path in paths.items():
        assert path.is_file(), k
        assert tmp_path.resolve() in path.resolve().parents, k                                  # every artifact is inside tmp_path
    fv = out_dir / "q10_forward_validation"
    assert paths["q10_preopen_snapshot"] == fv / "q10_preopen_signal_snapshot.json" and paths["q10_actual_reactions"] == fv / "q10_actual_market_reactions.json"
    assert paths["q10_expected_vs_actual"] == fv / "q10_expected_vs_actual.json" and paths["q10_shadow_comparison"] == fv / "q10_shadow_entry_comparison.json"
    assert paths["q10_forward_validation_report"] == fv / "q10_forward_validation_report.md" and paths["q10_forward_validation_cumulative"] == out_dir.parent / "q10_forward_validation_cumulative.json"
    snap = json.loads(paths["q10_preopen_snapshot"].read_text(encoding="utf-8"))
    assert snap["schema_version"] == SCHEMA_VERSION and snap["evaluation_program_id"] == PROGRAM_ID and snap["day"] == DAY and snap["capture_status"] == "CAPTURED"
    for key in ("q10_actual_reactions", "q10_expected_vs_actual", "q10_shadow_comparison"):
        body = json.loads(paths[key].read_text(encoding="utf-8"))
        assert body["schema_version"] == SCHEMA_VERSION and body["evaluation_program_id"] == PROGRAM_ID and body["guards"]["prospective_only"] is True
    assert json.loads(paths["q10_expected_vs_actual"].read_text(encoding="utf-8"))["day"] == DAY and json.loads(paths["q10_shadow_comparison"].read_text(encoding="utf-8"))["day"] == DAY
    assert set(json.loads(paths["q10_actual_reactions"].read_text(encoding="utf-8"))["targets"]) == {"samsung", "sk_hynix", "kospi", "kosdaq"}


def test_report_states_shadow_only_and_orders_disabled_and_no_stray_files(tmp_path):
    out_dir, res = run(tmp_path, FakeProvider())
    md = Path(res["q10_forward_validation_report"]).read_text(encoding="utf-8")
    assert "prospective_shadow_only" in md and "Historical backfill / threshold optimization / ML / orders: disabled" in md and "Preopen snapshot: `CAPTURED`" in md and md.endswith("\n")
    produced = set(tree(tmp_path))
    assert not [f for f in produced if f.startswith("cwd/")]                                    # nothing written to the operating CWD
    assert not (tmp_path / "state.json").exists() and not (tmp_path / "macro").exists()          # read-only inputs are never created
    assert sorted(f for f in produced if f.endswith(".tmp")) == []                              # atomic writes leave no temp files
    expected = {"reports/evaluation/baseline_samsung_hynix/2026-10-29/q10_forward_validation/" + n for n in ("q10_preopen_signal_snapshot.json", "q10_actual_market_reactions.json", "q10_expected_vs_actual.json",
                                                                                                           "q10_shadow_entry_comparison.json", "q10_forward_validation_report.md")}
    expected.add("reports/evaluation/baseline_samsung_hynix/q10_forward_validation_cumulative.json")
    assert produced == expected


def test_rerun_with_same_inputs_does_not_inflate_cumulative_and_preserves_the_snapshot(tmp_path):
    out_dir, first = run(tmp_path, FakeProvider())
    snap = Path(first["q10_preopen_snapshot"])
    snap_hash = hashlib.sha256(snap.read_bytes()).hexdigest()
    cum1 = json.loads(Path(first["q10_forward_validation_cumulative"]).read_text(encoding="utf-8"))
    second_provider = FakeProvider()
    _, second = run(tmp_path, second_provider, now=at(8, 58))
    assert second_provider.calls == [] and hashlib.sha256(snap.read_bytes()).hexdigest() == snap_hash                       # existing snapshot wins, provider untouched
    cum2 = json.loads(Path(second["q10_forward_validation_cumulative"]).read_text(encoding="utf-8"))
    assert cum2 == cum1 and cum2["day_count"] == cum1["day_count"] and cum2["observed_outcome_count"] == cum1["observed_outcome_count"]
    third = run(tmp_path, FakeProvider(), now=at(9, 30))[1]                                                                 # late rerun still cannot backfill
    assert third["q10_forward_validation_status"] == "CAPTURED" and hashlib.sha256(snap.read_bytes()).hexdigest() == snap_hash


def test_cumulative_counts_adopted_outcomes_once_with_real_shadow_output(tmp_path):
    def stock(price, close):
        rows = [{"ts": int(at(9, 0).timestamp()) + 60 * i, "open": price, "high": price + 1, "low": price - 1, "close": price + 0.1 * i, "volume": 5.0} for i in range(1, 15)]
        rows += [{"ts": int(at(15, 30).timestamp()), "open": close, "high": close, "low": close, "close": close, "volume": 5.0}]
        return rows

    cm = {"005930": stock(100.0, 110.0), "000660": stock(200.0, 210.0)}
    out_dir, res = run(tmp_path, FakeProvider(), candle_map=cm)
    shadow = json.loads(Path(res["q10_shadow_comparison"]).read_text(encoding="utf-8"))
    observed = [o for o in shadow["outcomes"] if o["status"] == "OBSERVED"]
    cum = json.loads(Path(res["q10_forward_validation_cumulative"]).read_text(encoding="utf-8"))
    assert observed and cum["observed_outcome_count"] == len(observed) and cum["days"] == [DAY] and cum["day_count"] == 1
    again = run(tmp_path, FakeProvider(), candle_map=cm)[1]
    assert json.loads(Path(again["q10_forward_validation_cumulative"]).read_text(encoding="utf-8")) == cum


def test_before_activation_day_returns_inactive_status_and_creates_no_file(tmp_path):
    p = FakeProvider()
    out_dir, res = run(tmp_path, p, day="2026-08-30", now=at(8, 55, day="2026-08-30"))
    assert res == {"q10_forward_validation_status": "NOT_ACTIVE_PROSPECTIVE_ONLY"} and p.calls == [] and not out_dir.exists() and not (tmp_path / "reports").exists()
    assert "2026-08-30" < ACTIVATION_DAY


def test_waiting_before_window_still_renders_artifacts_but_snapshot_path_is_blank(tmp_path):
    p = FakeProvider()
    out_dir, res = run(tmp_path, p, now=at(8, 40))
    assert res["q10_forward_validation_status"] == "WAITING" and res["q10_preopen_snapshot"] == "" and p.calls == []
    assert Path(res["q10_forward_validation_report"]).is_file() and not (out_dir / "q10_forward_validation" / "q10_preopen_signal_snapshot.json").exists()


def test_function_signature_and_collaborator_identity_are_the_original_ones():
    import inspect
    sig = inspect.signature(pl.build_q10_forward_validation)
    assert list(sig.parameters) == ["day", "output_dir", "state_path", "macro_root", "candle_map", "cost_pct", "slippage_pct", "now", "lead_market_provider"]
    from libs.reporting.baseline_samsung_hynix.forward_validation import cumulative, expected_actual, reaction_reader, report, shadow_comparison
    assert pl.build_actual_reactions is reaction_reader.build_actual_reactions and pl.build_expected_actual is expected_actual.build_expected_actual
    assert pl.build_shadow_comparison is shadow_comparison.build_shadow_comparison and pl.build_cumulative is cumulative.build_cumulative and pl.render_forward_validation_report is report.render_forward_validation_report
