import unittest
from scripts.diagnostics import check_reports_trades_health as subject
class TestParser(unittest.TestCase):
 def test_default_explicit_and_negative(self):
  self.assertEqual(subject._build_parser().parse_args([]).reports_root,"reports"); self.assertTrue(subject._build_parser().parse_args(["--day","2026-10-30","--json"]).json)
  with self.assertRaises(SystemExit) as exc: subject._build_parser().parse_args(["--unknown"])
  self.assertEqual(exc.exception.code,2)
