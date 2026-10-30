import tempfile, unittest
from pathlib import Path
from scripts.diagnostics import check_reports_trades_health as subject
class TestAudit(unittest.TestCase):
 def test_empty_temp_root(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=subject.audit_reports_trades_health(Path(tmp)); self.assertEqual(out["trade_dir_count"],0); self.assertTrue(out["ok"])
