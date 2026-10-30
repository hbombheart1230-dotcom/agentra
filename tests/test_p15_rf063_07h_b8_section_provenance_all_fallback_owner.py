import unittest
from scripts.diagnostics import check_reporter_upgrade_regression as subject
class TestProvenance(unittest.TestCase):
 def test_empty_fallback_and_mixed(self):
  self.assertFalse(subject._section_provenance_all_fallback({})); self.assertTrue(subject._section_provenance_all_fallback({"section_provenance":{"a":{"source":"fallback"},"b":{"source":"unknown"}}})); self.assertFalse(subject._section_provenance_all_fallback({"section_provenance":{"a":{"source":"model"}}}))
