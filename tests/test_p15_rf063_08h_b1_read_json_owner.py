import json,tempfile,unittest
from pathlib import Path
from scripts.diagnostics import check_reporter_upgrade_regression as s
class T(unittest.TestCase):
 def test_values_and_patch(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"a";p.write_text(json.dumps({"x":1}));self.assertEqual(s._read_json(p),{"x":1}); old=s.json.loads;s.json.loads=lambda _: {"p":1}
   try:self.assertEqual(s._read_json(p),{"p":1})
   finally:s.json.loads=old
   self.assertEqual(s._read_json(Path(d)/"missing"),{})
