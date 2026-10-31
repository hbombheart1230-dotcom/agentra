import tempfile,unittest
from pathlib import Path
from scripts.diagnostics import check_q9_q12_readiness as q
class T(unittest.TestCase):
 def test_b1_q9_checks(self):
  with tempfile.TemporaryDirectory() as d:
   o=q._q9_checks(Path(d),'2026-08-30');self.assertEqual(o['window_count'],0);self.assertEqual(o['first_window_kst'],'')
 def test_b2_baseline(self):
  with tempfile.TemporaryDirectory() as d:self.assertFalse(q._baseline_artifacts(Path(d),'2026-08-30')['q10']['decisions']['exists']);self.assertIn('lead_market_preopen',q._baseline_artifacts(Path(d),'2026-08-31')['q10'])
 def test_b3_evaluate(self):self.assertEqual(q._evaluate(phase='preopen',day='2026-08-30',live={'running':False},processes={},q9={},artifacts={})[0],[{'code':'live_session_not_running'}])
if __name__=='__main__':unittest.main()
