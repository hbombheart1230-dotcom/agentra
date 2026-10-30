import tempfile, unittest
from pathlib import Path
from scripts.diagnostics import check_reports_trades_health as subject
class TestIssue(unittest.TestCase):
 def test_exact_row(self):
  path=Path(tempfile.gettempdir())/"x"; self.assertEqual(subject._issue(severity="warn",trade_id="t",component="brief",code="x",message="m",path=path),{"severity":"warn","trade_id":"t","component":"brief","code":"x","message":"m","path":str(path)})
