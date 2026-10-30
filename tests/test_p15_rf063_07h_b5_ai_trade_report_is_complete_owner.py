import tempfile, unittest
from pathlib import Path
from scripts.diagnostics import check_reports_trades_health as subject
class TestComplete(unittest.TestCase):
 def test_complete_and_missing(self):
  keys=("executive_summary","market_context_at_entry","why_this_symbol_was_chosen","entry_decision","holding_monitoring_story","exit_decision","execution_quality","scanner_filters","guard_approval_result","reporter_evaluation","errors_weaknesses_improvement_points","final_operator_conclusion")
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); oldp,oldr=subject._artifact_path,subject._read_json; subject._artifact_path=lambda *_:root/"x"; subject._read_json=lambda _:{key:{} for key in keys}
   try: self.assertTrue(subject._ai_trade_report_is_complete(root)); subject._read_json=lambda _:{}; self.assertFalse(subject._ai_trade_report_is_complete(root))
   finally: subject._artifact_path,subject._read_json=oldp,oldr
