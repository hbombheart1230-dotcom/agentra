from scripts.diagnostics.check_trade_report_runtime_regression import _section_provenance_all_fallback
def test_cases(): assert _section_provenance_all_fallback({'section_provenance':{'a':{'source':'fallback'}}}) and not _section_provenance_all_fallback({})
