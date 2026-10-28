"""RF-031: Reporter caller -> real passive AI-review boundary, fully offline.

The Reporter and reporter-analysis writer chain use temporary roots.  The only
LLM seam is ``LLMRouter``: it is replaced before the real review function is
called, and the ledger recorders are in-memory no-ops.  This fixes the composed
caller contract without reaching a provider, socket, or operational artifact.
"""
from __future__ import annotations

import json

from libs.agent.reporter import Reporter
from libs.reporting import reporter_ai_review as review


DAY = "2026-10-29"


def _eq(actual, expected):
    if actual != expected:
        raise AssertionError(f"{actual!r} != {expected!r}")


class _Route:
    model = "fake/reporter-review"


class _Router:
    client = object()
    reply = ""
    failure = None
    calls = []

    @classmethod
    def from_env(cls):
        return cls()

    def resolve(self, role, policy=None):
        type(self).calls.append(("resolve", role, dict(policy or {})))
        return _Route()

    def chat(self, role, messages, policy=None):
        type(self).calls.append(("chat", role, dict(policy or {})))
        if type(self).failure is not None:
            raise type(self).failure
        return type(self).reply


def _kwargs(tmp_path):
    events = tmp_path / "input" / "events.jsonl"
    events.parent.mkdir()
    events.write_text(json.dumps({"ts": DAY + "T01:00:00+00:00", "event": "observe", "run_id": "r1", "payload": {}}) + "\n", encoding="utf-8")
    return {
        "event_log_path": events,
        "report_dir": tmp_path / "reports" / "daily" / "analysis",
        "reports_root": tmp_path / "reports",
        "day": DAY,
        "ai_review_enabled": True,
    }


def _install_offline_review(monkeypatch):
    _Router.calls, _Router.failure = [], None
    _Router.reply = json.dumps(
        {
            "ai_summary": "offline review",
            "ai_findings": ["finding"],
            "ai_root_causes": ["cause"],
            "ai_improvement_suggestions": ["improve"],
            "ai_run_grade": "B+",
            "ai_agent_evaluations": {"scanner": "good"},
            "ai_evidence_links": {"findings": [], "root_causes": [], "improvements": []},
        }
    )
    monkeypatch.setattr(review, "LLMRouter", _Router)
    for name in ("record_raw_input", "record_llm_prompt", "record_llm_response"):
        monkeypatch.setattr(review, name, lambda *args, **kwargs: None)


def test_reporter_caller_runs_real_review_with_fake_router_and_tmp_outputs(tmp_path, monkeypatch):
    _install_offline_review(monkeypatch)
    monkeypatch.chdir(tmp_path)
    out = Reporter().run(mode="reporter_analysis", **_kwargs(tmp_path))

    _eq((out.payload["ai_review"]["status"], out.payload["ai_summary"], out.payload["ai_run_grade"]), ("ok", "offline review", "B+"))
    _eq([entry[0:2] for entry in _Router.calls], [("resolve", "reporter_final"), ("chat", "reporter_final")])
    for path in out.output_paths.values():
        if not str(path).startswith(str(tmp_path)):
            raise AssertionError(path)


def test_reporter_caller_keeps_writer_result_when_fake_review_times_out(tmp_path, monkeypatch):
    _install_offline_review(monkeypatch)
    _Router.failure = TimeoutError("fake timeout")
    monkeypatch.chdir(tmp_path)
    out = Reporter().run(mode="reporter_analysis", **_kwargs(tmp_path))

    _eq((out.payload["ai_review"]["status"], out.payload["ai_run_grade"]), ("error", "N/A"))
    # The caller deliberately preserves a deterministic fallback summary when
    # the optional review fails; a timeout must not erase writer output.
    if not out.payload["ai_summary"].startswith("Deterministic evidence is available"):
        raise AssertionError(out.payload["ai_summary"])
    if not str(out.payload["ai_review"]["reason"]).startswith("ai_call_failed:fake timeout"):
        raise AssertionError(out.payload["ai_review"])
    for path in out.output_paths.values():
        if not str(path).startswith(str(tmp_path)):
            raise AssertionError(path)
