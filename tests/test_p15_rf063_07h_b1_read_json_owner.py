import json, tempfile, unittest
from pathlib import Path
from scripts.diagnostics import check_reports_trades_health as subject
from scripts.diagnostics import reports_trades_health_read_projection as owner
class TestReadJson(unittest.TestCase):
 def test_values_and_call_time_json_seam(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"a.json"; path.write_text(json.dumps({"a":1}))
   self.assertEqual(subject._read_json(path), {"a":1}); self.assertEqual(owner._read_json(path, facade=subject), {"a":1})
   old=subject.json.loads; subject.json.loads=lambda _: {"patched": True}
   try: self.assertEqual(subject._read_json(path), {"patched": True})
   finally: subject.json.loads=old
   self.assertEqual(subject._read_json(Path(tmp)/"missing"), {})
