import tempfile,unittest
from pathlib import Path
from scripts.diagnostics import check_reporter_upgrade_regression as s
class T(unittest.TestCase):
 def test_sorted_and_missing(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); base=root/"trades"/"x";base.mkdir(parents=True);(base/"b").mkdir();(base/"a").mkdir();self.assertEqual([x.name for x in s._trade_dirs_for_day(root,"x")],["a","b"]);self.assertEqual(s._trade_dirs_for_day(root,"none"),[])
