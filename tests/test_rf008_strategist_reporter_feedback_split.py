"""RF-008: isolated, no-network regression for extracted reporter-feedback owner."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import copy
import unittest

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "graphs/nodes/strategist_reporter_feedback.py"


def _load_owner():
    spec = importlib.util.spec_from_file_location("_rf008_strategist_reporter_feedback", TARGET)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.load_reporter_feedback_packet


def _facade(packet=None):
    calls = []

    def read_packet(**kwargs):
        calls.append(dict(kwargs))
        return dict(packet or {})

    facade = SimpleNamespace(
        os=SimpleNamespace(getenv=lambda key, default="": default),
        isolate_canonical_path_for_pytest=lambda path, **kw: path,
        _resolve_state_day=lambda state: "2026-10-29",
        build_strategist_feedback_packet=read_packet,
        _round_optional=lambda value, digits: round(float(value), digits),
    )
    return facade, calls


class ReporterFeedbackOwnerTest(unittest.TestCase):
    def setUp(self):
        self.impl = _load_owner()

    def test_disabled_fails_closed_without_io_or_mutation(self):
        facade, calls = _facade()
        state = {"strategist_feedback_packet": {"available": True, "insight_summary": "ignored"}}
        policy = {"reporter_feedback_mode": "enabled"}
        state_before, policy_before = copy.deepcopy(state), copy.deepcopy(policy)
        out = self.impl(state, policy, facade=facade)
        self.assertEqual(out["feedback_gate_reason"], "low_confidence")
        # Policy has no effect when source is present: default mode is auto.
        self.assertEqual(state, state_before)
        self.assertEqual(policy, policy_before)
        self.assertEqual(calls, [])

    def test_explicit_disabled_skips_packet_read(self):
        facade, calls = _facade({"available": True})
        state = {"applied_policy": {"strategist": {"reporter_feedback_mode": "disabled"}}}
        out = self.impl(state, {}, facade=facade)
        self.assertFalse(out["consumed"])
        self.assertEqual(out["feedback_gate_reason"], "mode_disabled")
        self.assertFalse(calls)

    def test_enabled_consumes_available_packet(self):
        facade, calls = _facade()
        state = {"strategist_feedback_packet": {"available": True, "insight_summary": "signal"},
                 "applied_policy": {"strategist": {"reporter_feedback_mode": "enabled"}}}
        before = copy.deepcopy(state)
        out = self.impl(state, {}, facade=facade)
        self.assertTrue(out["consumed"])
        self.assertEqual(out["feedback_gate_reason"], "mode_enabled")
        self.assertEqual(state, before)
        self.assertFalse(calls)

    def test_auto_rejects_stale_packet(self):
        facade, calls = _facade()
        state = {"strategist_feedback_packet": {
            "available": True, "confidence": "high",
            "insight_summary": "signal", "data_freshness": {"stale": True}}}
        out = self.impl(state, {}, facade=facade)
        self.assertFalse(out["consumed"])
        self.assertEqual(out["feedback_gate_reason"], "stale")
        self.assertFalse(calls)

    def test_auto_accepts_fresh_relevant_packet(self):
        facade, _ = _facade()
        state = {"strategist_feedback_packet": {
            "available": True, "confidence": "high", "insight_summary": "signal",
            "data_freshness": {"stale": False}}}
        out = self.impl(state, {}, facade=facade)
        self.assertTrue(out["consumed"])
        self.assertEqual(out["feedback_gate_reason"], "auto_accepted")

    def test_runtime_fake_is_resolved_on_each_call(self):
        facade, _ = _facade()
        state = {"strategist_feedback_packet": {
            "available": True, "confidence": 0.7, "insight_summary": "signal"}}
        out = self.impl(state, {}, facade=facade)
        self.assertTrue(out["consumed"])
        facade._round_optional = lambda value, digits: 0.1
        out2 = self.impl(state, {}, facade=facade)
        self.assertFalse(out2["consumed"])
        self.assertEqual(out2["feedback_gate_reason"], "low_confidence")

    def test_missing_state_uses_injected_reader(self):
        facade, calls = _facade({"available": True, "confidence": "high",
                                  "insight_summary": "from fake"})
        state = {"reports_root": "isolated-tmp", "day": "2026-10-29"}
        original = copy.deepcopy(state)
        out = self.impl(state, {}, facade=facade)
        self.assertTrue(out["consumed"])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["reports_root"], "isolated-tmp")
        self.assertEqual(state, original)


if __name__ == "__main__":
    unittest.main()
