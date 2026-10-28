"""RF-031 trade_report_ai_compact_input: how read-model seeds shape the compact LLM payload (in-memory hint, no disk/AI/network)."""
from __future__ import annotations

import copy

from libs.reporting import trade_report_ai as tra

_PLACEHOLDER = "Same-day reporter analysis was not generated yet."


def _eq(a, b):
    if a != b:
        raise AssertionError(f"{a!r} != {b!r}")


def _compact(monkeypatch, story, seeds):
    hint = {"context": {"report_section_seeds": copy.deepcopy(seeds)}} if seeds else {}
    monkeypatch.setattr(tra, "_load_trade_read_model_hint", lambda s: hint)
    return tra._compact_story_input_for_llm(copy.deepcopy(story))


def test_placeholder_reporter_status_is_replaced_by_the_seed_summary_bullets_status_grade(monkeypatch):
    seeds = {"reporter_evaluation": {"summary": "SEED reporter", "bullets": ["sb1", "sb2"], "status": "seeded", "grade": "A"}}
    out = _compact(monkeypatch, {"reporter_status_human": {"summary": _PLACEHOLDER, "status": "missing", "bullets": ["old"], "grade": "Z"}}, seeds)
    _eq(out["reporter_status_human"], {"summary": "SEED reporter", "status": "seeded", "grade": "A", "bullets": ["sb1", "sb2"]})


def test_real_reporter_status_is_kept_even_when_a_seed_exists(monkeypatch):
    seeds = {"reporter_evaluation": {"summary": "SEED reporter", "bullets": ["sb1"], "status": "seeded", "grade": "A"}}
    story = {"reporter_status_human": {"summary": "Genuine same-run evaluation.", "status": "ok", "bullets": ["real"], "grade": "B"}}
    out = _compact(monkeypatch, story, seeds)
    _eq(out["reporter_status_human"], {"summary": "Genuine same-run evaluation.", "status": "ok", "grade": "B", "bullets": ["real"]})


def test_partial_seed_only_overrides_the_fields_it_has(monkeypatch):
    out = _compact(monkeypatch, {"reporter_status_human": {"summary": _PLACEHOLDER, "status": "missing", "bullets": ["old"], "grade": "Z"}},
                   {"reporter_evaluation": {"summary": "only summary"}})
    _eq((out["reporter_status_human"]["summary"], out["reporter_status_human"]["status"], out["reporter_status_human"]["grade"], out["reporter_status_human"]["bullets"]),
        ("only summary", "missing", "Z", ["old"]))


def test_no_seed_leaves_a_placeholder_summary_untouched_and_is_deterministic(monkeypatch):
    story = {"reporter_status_human": {"summary": _PLACEHOLDER, "status": "missing"}}
    first = _compact(monkeypatch, story, None)
    _eq(first["reporter_status_human"]["summary"], _PLACEHOLDER)
    _eq(first, _compact(monkeypatch, story, None))
    seeded = _compact(monkeypatch, {}, {"reporter_evaluation": {"summary": "S"}})
    _eq(set(seeded["report_section_seeds"]) >= {"reporter_evaluation", "strategist_summary", "execution_quality", "final_operator_conclusion"}, True)
