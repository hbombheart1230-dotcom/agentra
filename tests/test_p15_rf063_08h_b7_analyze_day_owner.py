import json,tempfile,unittest
from pathlib import Path
from scripts.diagnostics import check_reporter_upgrade_regression as s
class T(unittest.TestCase):
 def test_temp_trades(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); day=root/"trades"/"2026-10-31"; closed=day/"a";open_=day/"b";closed.mkdir(parents=True);open_.mkdir();(closed/"reports").mkdir();(open_/"reports").mkdir();(closed/"lifecycle_bundle.json").write_text(json.dumps({"status":"closed"}));(open_/"lifecycle_bundle.json").write_text("{}");(closed/"reports"/"ai_trade_report.json").write_text("{}");out=s.analyze_day(root,"2026-10-31");self.assertEqual((out["total_trades"],out["closed_trades"]),(2,1))
