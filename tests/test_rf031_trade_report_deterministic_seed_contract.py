"""RF-031 trade_report_ai_deterministic.fallback_report: how trade-read-model section seeds merge into the deterministic report.

``_load_trade_read_model_hint`` (the only disk reader on this path) is replaced by an in-memory fake, so no trade
directory, report tree, AI or network is touched. Explicit raises keep the checks live under ``python -O``.
"""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import trade_report_ai as tra


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _hint(monkeypatch, seeds):
    monkeypatch.setattr(tra, "_load_trade_read_model_hint", lambda story: {"context": {"report_section_seeds": copy.deepcopy(seeds)}} if seeds is not None else {})


def _build(story=None):
    report = tra.build_deterministic_trade_report(copy.deepcopy(story if story is not None else {}))
    report = dict(report)
    report.pop("generated_at", None)
    report.pop("fact_payload", None)          # embeds the raw read-model hint, which differs by construction between cases
    return report


def test_no_seed_report_is_deterministic_and_has_all_sections(monkeypatch):
    _hint(monkeypatch, None)
    first, second = _build(), _build()
    _eq(json.dumps(first, sort_keys=True, ensure_ascii=False, default=str), json.dumps(second, sort_keys=True, ensure_ascii=False, default=str))
    for section in ("reporter_evaluation", "execution_quality", "strategist_summary", "entry_decision", "exit_decision",
                    "holding_monitoring_story", "scanner_filters", "market_context_at_entry", "final_operator_conclusion", "guard_approval_result"):
        if section not in first:
            raise AssertionError(section)
    if "SEED" in json.dumps(first, ensure_ascii=False, default=str):
        raise AssertionError("no seed text expected without seeds")


def test_seed_summaries_replace_placeholder_summaries_and_seed_status_grade_apply(monkeypatch):
    _hint(monkeypatch, {
        "reporter_evaluation": {"summary": "SEED reporter summary", "bullets": ["seed b"], "status": "seeded_status", "grade": "B+"},
        "execution_quality": {"summary": "SEED exec summary", "bullets": ["seed e"]},
        "strategist_summary": {"summary": "SEED strategist", "bullets": ["seed s"]},
    })
    out = _build()
    _eq((out["reporter_evaluation"]["summary"], out["reporter_evaluation"]["status"], out["reporter_evaluation"]["grade"]),
        ("SEED reporter summary", "seeded_status", "B+"))
    _eq(out["execution_quality"]["summary"], "SEED exec summary")
    _eq(out["strategist_summary"]["summary"], "SEED strategist")
    # computed bullets are kept; seed bullets only fill in when no computed bullets exist
    if "seed b" in out["reporter_evaluation"]["bullets"]:
        raise AssertionError("seed bullets must not displace computed bullets")


def test_unseeded_sections_are_unchanged_by_seeding_other_sections(monkeypatch):
    _hint(monkeypatch, None)
    base = _build()
    _hint(monkeypatch, {"reporter_evaluation": {"summary": "SEED only reporter"}})
    seeded = _build()
    _eq(seeded["reporter_evaluation"]["summary"], "SEED only reporter")
    for section in ("execution_quality", "strategist_summary", "entry_decision", "exit_decision", "scanner_filters"):
        _eq(seeded[section], base[section])


def test_non_dict_seed_values_are_ignored(monkeypatch):
    _hint(monkeypatch, None)
    base = _build()
    _hint(monkeypatch, {"reporter_evaluation": "junk", "execution_quality": ["x"], "strategist_summary": None})
    _eq(json.dumps(_build(), sort_keys=True, ensure_ascii=False, default=str), json.dumps(base, sort_keys=True, ensure_ascii=False, default=str))


def test_hint_loader_returns_empty_without_a_trade_artifact_path_and_never_raises(tmp_path):
    _eq(tra._load_trade_read_model_hint({}), {})
    _eq(tra._load_trade_read_model_hint({"artifacts": {"ai_trade_report_input_json": str(tmp_path / "missing" / "ai_trade_report_input.json")}}), {})
    _eq(tra._load_trade_read_model_hint("not-a-dict"), {})


_PLACEHOLDER = "Same-day reporter analysis was not generated yet."
_SEEDS = {"reporter_evaluation": {"summary": "SEED reporter summary", "bullets": ["seed b1"], "status": "seeded_status", "grade": "B+"}}


def test_reporter_status_present_keeps_computed_summary_and_only_fills_missing_status_and_grade(monkeypatch):
    _hint(monkeypatch, _SEEDS)
    missing = _build({"reporter_status_human": {"summary": _PLACEHOLDER, "status": "missing", "grade": ""}})["reporter_evaluation"]
    # a story-provided reporter status disables the seed summary; a "missing" status and empty grade are filled from the seed
    if missing["summary"] == "SEED reporter summary":
        raise AssertionError("seed summary must not replace the computed summary when reporter status exists")
    _eq((missing["status"], missing["grade"]), ("seeded_status", "B+"))
    known = _build({"reporter_status_human": {"summary": _PLACEHOLDER, "status": "ok", "grade": "C"}})["reporter_evaluation"]
    _eq((known["status"], known["grade"]), ("ok", "C"))                      # an explicit status/grade is never overwritten
    none = _build({})["reporter_evaluation"]
    _eq((none["summary"], none["status"], none["grade"]), ("SEED reporter summary", "seeded_status", "B+"))
    _eq(missing["summary"], known["summary"])


def test_seed_does_not_change_bullet_lists_of_a_populated_report(monkeypatch):
    _hint(monkeypatch, None)
    base = _build()
    _hint(monkeypatch, {"reporter_evaluation": {"bullets": ["seed only"]}, "execution_quality": {"bullets": ["seed e"]}, "strategist_summary": {"bullets": ["seed s"]}})
    seeded = _build()
    for section in ("reporter_evaluation", "execution_quality", "strategist_summary"):
        _eq(seeded[section]["bullets"], base[section]["bullets"])


@pytest.mark.parametrize("raw,expected_fragment", [("trailing_stop", "추적 손절로 청산"), ("totally_custom_reason", "totally custom reason")])
def test_normalized_exit_reason_becomes_the_first_exit_bullet(monkeypatch, raw, expected_fragment):
    monkeypatch.setattr(tra, "_load_trade_read_model_hint", lambda story: {"facts": {"exit_reason": raw}})
    first = _build()["exit_decision"]["bullets"][0]
    if not first.startswith("정규화된 청산 사유는 ") or expected_fragment not in first:
        raise AssertionError(first)
    monkeypatch.setattr(tra, "_load_trade_read_model_hint", lambda story: {})
    if _build()["exit_decision"]["bullets"][0] == first:
        raise AssertionError("exit reason bullet must depend on the read-model fact")
