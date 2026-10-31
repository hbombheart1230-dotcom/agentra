import tempfile,unittest
from pathlib import Path
from scripts.diagnostics import check_q9_q12_readiness as q
class T(unittest.TestCase):
 def test_b1_q9_checks(self):
  with tempfile.TemporaryDirectory() as d:
   o=q._q9_checks(Path(d),'2026-08-30');self.assertEqual(o['window_count'],0);self.assertEqual(o['first_window_kst'],'')
if __name__=='__main__':unittest.main()
