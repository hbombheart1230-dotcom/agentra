import unittest
from scripts.diagnostics import check_reporter_upgrade_regression as s
class T(unittest.TestCase):
 def test_cases(self):self.assertTrue(s._reporter_section_fallback({"section_provenance":{"reporter_evaluation":{"source":"fallback"}}}));self.assertFalse(s._reporter_section_fallback({"section_provenance":{"reporter_evaluation":{"source":"model"}}}))
