import tempfile, unittest
from pathlib import Path
from scripts.diagnostics import check_reports_trades_health as subject
class TestIterTradeDirs(unittest.TestCase):
 def test_missing_day_and_call_time_helper(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); self.assertEqual(subject._iter_trade_dirs(root), [])
   day=root/"trades"/"2026-10-30"; day.mkdir(parents=True); old=subject._iter_trade_dirs_under_day; subject._iter_trade_dirs_under_day=lambda p:[p/"spy"]
   try: self.assertEqual(subject._iter_trade_dirs(root, "2026-10-30"), [day/"spy"])
   finally: subject._iter_trade_dirs_under_day=old
