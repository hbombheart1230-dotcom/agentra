import tempfile,unittest
from pathlib import Path
from scripts.diagnostics import check_q9_q12_readiness as q
class T(unittest.TestCase):
 def test_b1_read_json(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x';self.assertEqual(q._read_json(p),{});p.write_text('{"schema_version":"x"}',encoding='utf-8');self.assertEqual(q._read_json(p)['schema_version'],'x')
 def test_b2_parse_dt(self):self.assertEqual(q._parse_dt('2026-10-31T00:00:00Z').hour,9);self.assertIsNone(q._parse_dt('bad'))
 def test_b3_artifact(self):
  with tempfile.TemporaryDirectory() as d:self.assertFalse(q._artifact(Path(d)/'x')['exists'])
if __name__=='__main__':unittest.main()
