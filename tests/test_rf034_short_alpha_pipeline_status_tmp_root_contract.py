"""RF-034 C3: short_alpha_discriminator.pipeline source-loading, status ladder and output-set contract (tmp root only).

Complements the existing happy-path test: pins the fail-soft source errors, the INVALID/JOIN_GAPS/OPTIONAL_GAP/PASS ladder,
latest-cumulative scorecard selection and that the writer emits exactly its 10 files into ``output_dir`` and nothing else.
"""
from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest

from libs.reporting.short_alpha_discriminator import pipeline as pl


@pytest.fixture(autouse=True)
def _deny_network(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("network attempt")

    monkeypatch.setattr(socket.socket, "connect", _boom)
    monkeypatch.setattr(socket, "create_connection", _boom)


OPENING = ("evaluation", "opening_rank1_shadow", "opening_rank1_shadow_cumulative.json")
FEATURE = ("evaluation", "feature_mart", "opening_rank1", "feature_mart.json")


def _put(root: Path, parts, payload) -> Path:
    p = root.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")
    return p


def _ep(decision_id, day="2026-08-24", symbol="005930"):
    return {
        "episode_id": f"episode:{decision_id}", "decision_id": decision_id, "decision_epoch": 1, "day": day, "symbol": symbol,
        "opening_observability": {"decision_from_open_sec": 30, "asset_observation": {"asset_class": "common_stock"}},
        "checkpoints": {h: {"live_net_return_pct": 1.0, "mfe_pct": 2.0} for h in ("+5m", "+15m", "+30m", "+60m", "EOD")},
    }


def _feat(decision_id, day="2026-08-24", symbol="005930"):
    return {
        "identity": {"decision_id": decision_id, "decision_epoch": 1, "day": day, "symbol": symbol},
        "scanner": {"risk_band": "HIGH", "candidate_setup": "DIRECTIONAL_BREADTH", "sources": [], "score_total": 1.0},
        "strategy": {"entry_horizon": "scalp", "tactic_id": "t", "canonical_evidence_status": "OBSERVED"},
        "strategy_choice_observation": {"playbook_choice": {}, "tactic_choice": {}, "generation": {"mode": "m"}},
        "outcomes": {"checkpoints": {h: {"status": "OBSERVED", "net_return_pct": 1.0} for h in ("+5m", "+15m", "+30m", "+60m", "EOD")}},
    }


# ---------- _load_json ----------

def test_load_json_error_taxonomy(tmp_path):
    payload, src = pl._load_json(tmp_path / "none.json")
    assert payload == {} and src == {"path": str(tmp_path / "none.json"), "available": False, "error": "MISSING_ARTIFACT"}
    bad = _put(tmp_path, ("bad.json",), "{nope")
    payload, src = pl._load_json(bad)
    assert payload == {} and src["available"] is True and src["error"] == "INVALID_ARTIFACT:JSONDecodeError"
    arr = _put(tmp_path, ("arr.json",), "[1]")
    payload, src = pl._load_json(arr)
    assert payload == {} and src["error"] == "SCHEMA_MISMATCH:ROOT_NOT_OBJECT"
    ok = _put(tmp_path, ("ok.json",), {"schema_version": "v9", "k": 1})
    payload, src = pl._load_json(ok)
    assert payload == {"schema_version": "v9", "k": 1} and src["error"] is None and src["schema_version"] == "v9"


def test_load_json_invalid_utf8_is_reported_not_raised(tmp_path):
    p = tmp_path / "b.json"
    p.write_bytes(b"\xff\xfe\x00bad")
    payload, src = pl._load_json(p)
    assert payload == {} and src["error"].startswith("INVALID_ARTIFACT:")


def test_latest_scorecard_picks_lexicographically_last_cumulative_dir(tmp_path):
    base = ("evaluation", "agent_effectiveness")
    _put(tmp_path, (*base, "cumulative_20260801_20260820", "agent_effectiveness_scorecard.json"), {"schema_version": "old"})
    _put(tmp_path, (*base, "cumulative_20260801_20260824", "agent_effectiveness_scorecard.json"), {"schema_version": "new"})
    _put(tmp_path, (*base, "daily_20260901", "agent_effectiveness_scorecard.json"), {"schema_version": "ignored"})
    payload, src = pl._latest_cumulative_agent_scorecard(tmp_path)
    assert payload["schema_version"] == "new" and "cumulative_20260801_20260824" in src["path"]
    payload, src = pl._latest_cumulative_agent_scorecard(tmp_path / "empty")
    assert payload == {} and src["available"] is False and src["error"] == "MISSING_ARTIFACT"


# ---------- status ladder ----------

def test_status_invalid_required_source_when_opening_or_feature_missing(tmp_path):
    out = pl.build_short_alpha_discriminator(reports_root=tmp_path, through_day="2026-08-25T09:00")
    assert out["integrity"]["status"] == "INVALID_REQUIRED_SOURCE"
    assert out["integrity"]["source_errors"] == ["MISSING_ARTIFACT"] * 3
    assert out["through_day"] == "2026-08-25" and out["behavior_change_authorized"] is False
    assert set(out["sources"]) == {"opening_rank1", "feature_mart", "agent_effectiveness"}
    _put(tmp_path, OPENING, {"episodes": []})
    out = pl.build_short_alpha_discriminator(reports_root=tmp_path, through_day="2026-08-25")
    assert out["integrity"]["status"] == "INVALID_REQUIRED_SOURCE"                    # feature mart still missing
    assert out["integrity"]["source_errors"] == ["MISSING_ARTIFACT", "MISSING_ARTIFACT"]


def test_status_pass_with_join_gaps_then_optional_gap_then_pass(tmp_path):
    _put(tmp_path, OPENING, {"episodes": [_ep("d1"), _ep("d2"), "not-a-mapping"]})
    _put(tmp_path, FEATURE, {"episodes": [_feat("d1")]})
    out = pl.build_short_alpha_discriminator(reports_root=tmp_path, through_day="2026-08-25")
    assert out["integrity"]["status"] == "PASS_WITH_JOIN_GAPS" and out["integrity"]["join"]["missing_join_count"] == 1
    # all joined, scorecard still missing -> optional source gap
    _put(tmp_path, OPENING, {"episodes": [_ep("d1")]})
    out = pl.build_short_alpha_discriminator(reports_root=tmp_path, through_day="2026-08-25")
    assert out["integrity"]["status"] == "PASS_WITH_OPTIONAL_SOURCE_GAP" and out["integrity"]["source_errors"] == ["MISSING_ARTIFACT"]
    _put(tmp_path, ("evaluation", "agent_effectiveness", "cumulative_1", "agent_effectiveness_scorecard.json"), {"schema_version": "s"})
    out = pl.build_short_alpha_discriminator(reports_root=tmp_path, through_day="2026-08-25")
    assert out["integrity"]["status"] == "PASS" and out["integrity"]["source_errors"] == []


def test_corrupt_required_source_is_invalid_not_raised(tmp_path):
    _put(tmp_path, OPENING, "{corrupt")
    _put(tmp_path, FEATURE, {"episodes": []})
    out = pl.build_short_alpha_discriminator(reports_root=tmp_path, through_day="2026-08-25")
    assert out["integrity"]["status"] == "INVALID_REQUIRED_SOURCE"
    assert out["sources"]["opening_rank1"]["error"] == "INVALID_ARTIFACT:JSONDecodeError"


# ---------- writer ----------

_EXPECTED = {
    "short_alpha_discriminator.json", "short_alpha_discriminator.md", "short_alpha_cohorts.json", "profit_fade_shadow.json",
    "strategist_stage2_roi.json", "scanner_diagnostics.json", "opening_overshoot_casebook.json", "opening_overshoot_casebook.md",
    "opening_policy_matrix.json", "opening_policy_matrix.md",
}


def test_writer_with_all_sources_missing_still_writes_exact_file_set_and_never_touches_reports(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    out_dir = tmp_path / "nested" / "out"
    res = pl.write_short_alpha_discriminator(reports_root=reports, through_day="2026-08-25", output_dir=out_dir)
    assert {p.name for p in out_dir.iterdir()} == _EXPECTED
    assert list(reports.iterdir()) == []                                              # reports root is read-only
    assert res["integrity_status"] == "INVALID_REQUIRED_SOURCE" and res["behavior_change_authorized"] is False
    assert {Path(v).name for k, v in res.items() if k.endswith("_path")} == _EXPECTED
    summary = json.loads((out_dir / "short_alpha_discriminator.json").read_text(encoding="utf-8"))
    assert summary["integrity"]["status"] == "INVALID_REQUIRED_SOURCE"
    for name in _EXPECTED:
        text = (out_dir / name).read_text(encoding="utf-8")
        assert text.endswith("\n") if name.endswith(".json") else text != ""


def test_writer_artifacts_are_the_matching_sections_of_the_summary(tmp_path):
    reports = tmp_path / "reports"
    _put(reports, OPENING, {"episodes": [_ep("d1")]})
    _put(reports, FEATURE, {"episodes": [_feat("d1")]})
    out_dir = tmp_path / "out"
    pl.write_short_alpha_discriminator(reports_root=reports, through_day="2026-08-25", output_dir=out_dir)
    load = lambda n: json.loads((out_dir / n).read_text(encoding="utf-8"))  # noqa: E731
    s = load("short_alpha_discriminator.json")
    assert load("short_alpha_cohorts.json") == s["cohort_review"]
    assert load("profit_fade_shadow.json") == s["profit_fade_review"]
    assert load("strategist_stage2_roi.json") == s["strategist_stage2_review"]
    assert load("scanner_diagnostics.json") == s["scanner_diagnostics"]
    assert load("opening_overshoot_casebook.json") == s["opening_overshoot_casebook"]
    assert load("opening_policy_matrix.json") == s["opening_policy_matrix"]


def test_writer_overwrites_previous_outputs_and_fails_when_output_dir_is_a_file(tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "short_alpha_discriminator.json").write_text("OLD", encoding="utf-8")
    pl.write_short_alpha_discriminator(reports_root=reports, through_day="2026-08-25", output_dir=out_dir)
    assert (out_dir / "short_alpha_discriminator.json").read_text(encoding="utf-8") != "OLD"
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    with pytest.raises(OSError):
        pl.write_short_alpha_discriminator(reports_root=reports, through_day="2026-08-25", output_dir=blocker / "sub")
    assert blocker.read_text(encoding="utf-8") == "x"
