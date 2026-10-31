import tempfile, unittest
from pathlib import Path
from scripts.diagnostics import run_m31_weekly_health_summary as source

class WeeklyOwners(unittest.TestCase):
 def test_b1_to_epoch(self):
  self.assertEqual(source._to_epoch('2026-10-31T00:00:00Z'),1793404800);self.assertIsNone(source._to_epoch(''));self.assertEqual(source._to_epoch(0),0)
 def test_b2_b4_b5(self):
  self.assertEqual(source._utc_day('2026-10-31T23:00:00Z'),'2026-10-31');self.assertIsNone(source._utc_day('bad'));self.assertEqual(source._parse_day('2026-10-31').tzinfo,source.timezone.utc);self.assertEqual(source._window_days(week_end='2026-10-31',days=3),['2026-10-29','2026-10-30','2026-10-31']);self.assertEqual(source._window_days(week_end='2026-10-31',days=0),['2026-10-31'])
 def test_b3_read_json(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'a.json';p.write_text('{"x":1}');self.assertEqual(source._read_json(p),{'x':1});p.write_text('bad');self.assertEqual(source._read_json(p),{});self.assertEqual(source._read_json(Path(d)/'none'),{})
 def test_b6_b7(self):
  self.assertEqual(source._item(item_id='x',title='X',passed=0,evidence='e'),{'id':'x','title':'X','required':True,'passed':False,'evidence':'e'})
  s=source._build_markdown({'week_start':'2026-10-25','week_end':'2026-10-31','ok':True,'events':{'total':0},'checklist':[]});self.assertTrue(s.startswith('# M31 Weekly Health Summary (2026-10-25 ~ 2026-10-31)'));self.assertIn('## Failures\n\n- (none)\n',s)
 def test_b8_parser(self):
  self.assertTrue(source._build_parser().parse_args(['--days','3','--json']).json);self.assertEqual(source._build_parser().parse_args([]).days,7)
if __name__=='__main__':unittest.main()
