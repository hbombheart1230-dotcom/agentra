"""Owner-extraction regression tests for pure commander shadow projections."""

import copy
import json
import unittest

from libs.contracts import agent_outputs
from libs.contracts.agent_output_parts import commander_shadow_runtime


class CommanderShadowRuntimeOwnerTests(unittest.TestCase):
    def test_actual_runtime_cached_and_noop_projection(self):
        state = {
            "commander_shadow_runtime": {"strategist_executed": False},
            "monitor_action_decision": {"decision": "NOOP"},
            "decision_packet": {"intent": {"action": "BUY"}},
            "execution": {"reason": "mock_reason"},
        }
        before = copy.deepcopy(state)
        result = agent_outputs._commander_shadow_actual_runtime(state, path="cached_strategist")
        self.assertEqual(state, before)
        self.assertEqual(result["strategist_called"], False)
        self.assertEqual(result["llm_called_by_strategist"], False)
        self.assertTrue(result["used_cached_strategist"])
        self.assertEqual(result["runtime_path"], "cached_strategist")
        self.assertEqual(result["monitor_decision"], "WAIT")
        self.assertEqual(result["executor_action"], "BUY")
        self.assertEqual(result["executor_status"], "mock_reason")

    def test_observations_projection_uses_facade_seams(self):
        state = {
            "runtime_fast_path": {"reason": "post_scanner_selected_symbol_refresh", "selected_symbol": "005930", "strategist_refresh_reason": "fixture"},
            "selected": {"score_total": None, "score": 0.7},
            "strategist_llm": {"attempts": 3},
            "portfolio_snapshot": {"positions": [{}, "bad"]},
            "monitor": {"order_lifecycle": {"stage": "filled", "terminal": True}},
        }
        before = copy.deepcopy(state)
        original_clip = agent_outputs._clip
        clip_calls = []
        def spy(value, *, max_len):
            clip_calls.append((value, max_len))
            return original_clip(value, max_len=max_len)
        agent_outputs._clip = spy
        try:
            wrapped = agent_outputs._commander_shadow_observations(state, path="shadow")
            direct = commander_shadow_runtime.build_observations(state, path="shadow", facade=agent_outputs)
        finally:
            agent_outputs._clip = original_clip
        self.assertEqual(state, before)
        self.assertEqual(wrapped, direct)
        self.assertTrue(clip_calls)
        self.assertTrue(wrapped["post_scanner_refresh_requested"])
        self.assertEqual(wrapped["post_scanner_refresh_selected_symbol"], "005930")
        self.assertEqual(wrapped["signal_strength"], 0.7)
        self.assertEqual(wrapped["retry_count_estimate"], 2)
        self.assertEqual(wrapped["position_state"], "open_position")
        self.assertFalse(wrapped["has_open_order"])
        json.dumps(wrapped, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
