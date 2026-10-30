"""P15 RF-035 (00h): llm_daily_summary._build_messages moved to llm_daily_summary_message_projection; parity with the pre-move body."""
from __future__ import annotations

import copy
import json

import pytest

from libs.reporting import llm_daily_summary as m
from libs.reporting import llm_daily_summary_message_projection as owner


STATE = {"eod_day": "2026-10-30", "daily_report": {"approvals": 2, "denials": 1, "runs": 3}}


def _both(state, policy):
    return m._build_messages(state, policy), owner._build_messages(state, policy)


def test_messages_exact():
    snap = copy.deepcopy(STATE)
    a, b = _both(STATE, {"day": "wrong"})
    assert a == b and STATE == snap
    assert [x["role"] for x in a] == ["system", "user"] and list(a[0]) == ["role", "content"]
    assert "Day: 2026-10-30\n" in a[1]["content"] and "approvals: 2\n" in a[1]["content"] and "denials: 1\n" in a[1]["content"] and "runs: 3\n\n" in a[1]["content"]
    assert a[0]["content"] == "You are a trading system reporter. Summarize the day's automated decisions succinctly in Korean. No financial advice. Use bullet points."
    assert a[1]["content"].endswith("Write a short summary (max 6 bullets) and a one-line takeaway.")


def test_missing_state_uses_policy_day_and_none():
    a, b = _both({}, {"day": "P"})
    assert a == b and a[1]["content"].startswith("Day: P\napprovals: None\ndenials: None\nruns: None\n\n")
    a, b = _both({}, {})
    assert a == b and a[1]["content"].startswith("Day: \napprovals: None")


def test_non_dict_daily_report_exception_parity():
    for fn in (m._build_messages, owner._build_messages):
        with pytest.raises((TypeError, ValueError)):
            fn({"daily_report": 5}, {})
