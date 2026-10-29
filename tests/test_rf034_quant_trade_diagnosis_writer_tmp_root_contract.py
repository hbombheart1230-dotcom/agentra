"""RF-034 C3: quant_trade_diagnosis.writer write/discovery/failure contract on a tmp reports root.

The model builders and payload builder are stubbed in the writer module, so only the writer's own contract is pinned:
paths, discovery, fail-soft report reads, zip truncation, and that nothing outside ``<trade_dir>/reports`` is written.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from libs.reporting.quant_trade_diagnosis import writer as w

DAY = "2026-07-30"


@pytest.fixture
def calls(monkeypatch):
    log = {"model": [], "eval": [], "attr": [], "build": []}

    def model(path):
        log["model"].append(Path(path))
        return {"trade_id": f"T_{Path(path).name}", "symbol": "005930"}

    monkeypatch.setattr(w, "build_q9_trade_read_model", model)
    monkeypatch.setattr(w, "evaluate_trade", lambda m: log["eval"].append(m["trade_id"]) or {"ev": m["trade_id"]})
    monkeypatch.setattr(w, "build_selection_attribution", lambda m: log["attr"].append(m["trade_id"]) or {"at": m["trade_id"]})

    def build(**kw):
        log["build"].append(kw)
        return {"schema_version": "x", "behavior_effect": "diagnostic_only", "trade_id": kw["model"]["trade_id"]}

    monkeypatch.setattr(w, "build_quant_trade_diagnosis", build)
    monkeypatch.setattr(w, "render_quant_trade_diagnosis", lambda p: f"# Quant Trade Diagnosis {p['trade_id']}\n")
    monkeypatch.setattr(w, "resolve_conditional_alpha_context", lambda model, eps: {"n_eps": len(eps)})
    return log


def _bundle(reports: Path, name: str) -> Path:
    d = reports / "trades" / DAY / name
    d.mkdir(parents=True)
    (d / "lifecycle_bundle.json").write_text("{}", encoding="utf-8")
    return d


def _snapshot(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def test_write_single_creates_exactly_two_files_under_trade_reports(tmp_path):
    trade = tmp_path / "trade"
    trade.mkdir()
    out = w.write_quant_trade_diagnosis(trade_dir=trade, payload={"trade_id": "X", "한글": "값"})
    assert out == {"json": str(trade / "reports" / "quant_trade_diagnosis.json"), "markdown": str(trade / "reports" / "quant_trade_diagnosis.md")}
    assert _snapshot(tmp_path) == {"trade/reports/quant_trade_diagnosis.json", "trade/reports/quant_trade_diagnosis.md"}
    raw = (trade / "reports" / "quant_trade_diagnosis.json").read_text(encoding="utf-8")
    assert raw.endswith("\n") and "한글" in raw and json.loads(raw)["trade_id"] == "X"


def test_write_single_overwrites_existing_outputs(tmp_path):
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "quant_trade_diagnosis.json").write_text("OLD", encoding="utf-8")
    w.write_quant_trade_diagnosis(trade_dir=tmp_path, payload={"trade_id": "N"})
    assert json.loads((tmp_path / "reports" / "quant_trade_diagnosis.json").read_text(encoding="utf-8"))["trade_id"] == "N"


def test_day_writer_discovers_trade_dirs_and_reads_inputs_fail_soft(tmp_path, calls):
    reports = tmp_path / "reports"
    first, second = _bundle(reports, "a_trade"), _bundle(reports, "b_trade")
    (reports / "trades" / DAY / "no_bundle").mkdir()
    before = _snapshot(tmp_path)
    out = w.write_quant_trade_diagnoses_for_day(reports_root=reports, day=DAY)
    assert calls["model"] == [first, second]                                     # sorted discovery
    assert out["schema_version"] == "quant_trade_diagnosis_batch.v1" and out["behavior_effect"] == "diagnostic_only"
    assert out["day"] == DAY and out["trade_count"] == 2 and out["written_count"] == 2
    assert [r["trade_id"] for r in out["written"]] == ["T_a_trade", "T_b_trade"] and out["written"][0]["symbol"] == "005930"
    # missing daily reports and episodes file degrade to empty inputs (no raise)
    assert all(k["root_cause_report"] == {} and k["entry_timing_report"] == {} for k in calls["build"])
    assert all(k["conditional_alpha_context"] == {"n_eps": 0} for k in calls["build"])
    after = _snapshot(tmp_path)
    assert after - before == {f"reports/trades/{DAY}/{n}/reports/quant_trade_diagnosis.{e}" for n in ("a_trade", "b_trade") for e in ("json", "md")}
    assert before <= after                                                       # no existing file removed


def test_day_writer_reads_root_cause_entry_timing_and_episode_files(tmp_path, calls, monkeypatch):
    reports = tmp_path / "reports"
    t = _bundle(reports, "t1")
    daily = reports / "evaluation" / "daily" / DAY
    daily.mkdir(parents=True)
    (daily / "scanner_alignment_root_cause_report.json").write_text(json.dumps({"rc": 1}), encoding="utf-8")
    (daily / "entry_timing_attribution_report.json").write_text("[1]", encoding="utf-8")   # non-dict -> {}
    seen = {}
    monkeypatch.setattr(w, "load_conditional_alpha_episodes", lambda p: seen.setdefault("p", p) and [{"e": 1}, {"e": 2}])
    w.write_quant_trade_diagnoses_for_day(reports_root=reports, day=DAY)
    k = calls["build"][0]
    assert k["root_cause_report"] == {"rc": 1} and k["entry_timing_report"] == {}
    assert k["trade_dir"] == t and k["conditional_alpha_context"] == {"n_eps": 2}
    assert seen["p"] == reports / "evaluation/offline_alpha/conditional_alpha_diagnosis/conditional_alpha_episode_contexts.json"
    assert k["all_models"] == [{"trade_id": "T_t1", "symbol": "005930"}]


def test_day_writer_uses_injected_inputs_without_building_models(tmp_path, calls):
    trade = tmp_path / "t"
    trade.mkdir()
    out = w.write_quant_trade_diagnoses_for_day(
        reports_root=tmp_path / "unused", day=DAY, trade_dirs=[trade],
        models=[{"trade_id": "M"}], evaluations=[{"e": 1}], attributions=[{"a": 1}],
        root_cause_report={"rc": 2}, entry_timing_report={"et": 3}, conditional_alpha_episodes=[{"x": 1}])
    assert calls["model"] == [] and calls["eval"] == [] and calls["attr"] == []
    assert out["written"][0]["trade_id"] == "M" and out["trade_count"] == 1
    assert not (tmp_path / "unused").exists()                                   # reports_root untouched when inputs injected
    k = calls["build"][0]
    assert k["root_cause_report"] == {"rc": 2} and k["entry_timing_report"] == {"et": 3} and k["conditional_alpha_context"] == {"n_eps": 1}


def test_day_writer_zero_trades_writes_nothing(tmp_path, calls):
    out = w.write_quant_trade_diagnoses_for_day(reports_root=tmp_path / "reports", day=DAY)
    assert out["trade_count"] == 0 and out["written_count"] == 0 and out["written"] == []
    assert _snapshot(tmp_path) == set()


def test_day_writer_rejects_mismatched_input_lengths_before_any_write(tmp_path, calls):
    """Formerly zip-truncated silently (trade_count 3 / written_count 1); P15 C02-4 fails closed with zero writes."""
    dirs = []
    for n in ("a", "b", "c"):
        d = tmp_path / n
        d.mkdir()
        dirs.append(d)
    with pytest.raises(ValueError, match="length mismatch"):
        w.write_quant_trade_diagnoses_for_day(
            reports_root=tmp_path / "r", day=DAY, trade_dirs=dirs,
            models=[{"trade_id": "A"}, {"trade_id": "B"}, {"trade_id": "C"}], evaluations=[{}], attributions=[{}, {}])
    assert not any((d / "reports").exists() for d in dirs) and calls["build"] == []


def test_day_writer_propagates_builder_failure_after_partial_writes(tmp_path, calls, monkeypatch):
    dirs = []
    for n in ("a", "b"):
        d = tmp_path / n
        d.mkdir()
        dirs.append(d)

    def build(**kw):
        if kw["model"]["trade_id"] == "B":
            raise RuntimeError("boom")
        return {"trade_id": kw["model"]["trade_id"]}

    monkeypatch.setattr(w, "build_quant_trade_diagnosis", build)
    with pytest.raises(RuntimeError, match="boom"):
        w.write_quant_trade_diagnoses_for_day(
            reports_root=tmp_path / "r", day=DAY, trade_dirs=dirs,
            models=[{"trade_id": "A"}, {"trade_id": "B"}], evaluations=[{}, {}], attributions=[{}, {}])
    assert (dirs[0] / "reports" / "quant_trade_diagnosis.json").exists()         # first trade already written (non-atomic batch)
    assert not (dirs[1] / "reports").exists()
