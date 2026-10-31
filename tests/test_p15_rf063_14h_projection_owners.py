import contextlib
import io
import unittest
from pathlib import Path

from scripts.diagnostics import query_commander_resilience_events as query
from scripts.diagnostics import reconstruct_incident_timeline as timeline
from scripts.diagnostics.commander_resilience_summary_projection import _summary
from scripts.diagnostics.incident_timeline_trigger_projection import _incident_trigger


class ProjectionOwnerTests(unittest.TestCase):
    def test_b1_summary_owner_and_wrapper(self):
        rows = [{"event": "error", "run_id": "R", "payload": {"status": "failed"}}, {"event": "transition", "payload": {"transition": "cooldown"}}]
        self.assertEqual(query._summary(rows, total_matched=3), _summary(rows, total_matched=3))
        self.assertEqual(query._summary(rows, total_matched=3)["error_total"], 1)
        self.assertEqual(query._summary([], total_matched=0)["event_total"], {})

    def test_b2_stdout_and_facade_patch(self):
        rows = [{"ts": "T", "run_id": "R", "event": "error", "payload": {"error_type": "E", "error": "bad"}}]
        summary = query._summary(rows, total_matched=1); out = io.StringIO()
        with contextlib.redirect_stdout(out): query._print_human(Path("fake.jsonl"), rows, summary)
        text = out.getvalue(); self.assertIn("=== Commander Resilience Events ===\n", text); self.assertIn("event=error error_type=E error=bad\n", text)
        captured = []; query.print = captured.append
        try: query._print_human(Path("x"), [], {"total_matched": 0, "shown": 0})
        finally: del query.print
        self.assertEqual(captured[0], "=== Commander Resilience Events ===")

    def test_b3_b4_b5(self):
        err = {"stage": "commander_router", "event": "error", "payload": {"error_type": "E"}}
        self.assertEqual(timeline._incident_trigger(err), (True, "commander_router:error:E")); self.assertEqual(timeline._incident_trigger({"event":"route"}), (False, "")); self.assertEqual(_incident_trigger(err), timeline._incident_trigger(err))
        self.assertEqual(timeline._is_recovery({"stage": "commander_router", "event": "intervention"}), (True, "commander_router:intervention"))
        self.assertEqual(timeline._event_reason({"payload": {"error": "x", "status": "ok"}}), "x"); self.assertEqual(timeline._event_reason({}), "")

    def test_b6_markdown_parity_content(self):
        text = timeline._build_markdown({"day":"2026-10-31", "ok": True, "events": 0, "runs": 0, "incident_total": 0, "trigger_total":{"b":2,"a":1}})
        self.assertTrue(text.startswith("# Incident Timeline Reconstruction (2026-10-31)")); self.assertIn("- a: 1\n- b: 2", text); self.assertIn("## Failures\n\n- (none)\n", text)

    def test_b7_to_epoch_and_invalid(self):
        self.assertEqual(timeline._to_epoch("2026-10-31T00:00:00Z"), 1793404800); self.assertIsNone(timeline._to_epoch("")); self.assertEqual(timeline._to_epoch(0), 0)

    def test_b8_parser_wrapper(self):
        self.assertEqual(timeline._build_parser().parse_args(["--json", "--window-before-sec", "30"]).window_before_sec, 30)
        self.assertEqual(timeline._build_parser().parse_args([]).window_after_sec, 900)


if __name__ == "__main__": unittest.main()
