from scripts.diagnostics.check_trade_report_runtime_regression import _safe_int
def test_cases(): assert (_safe_int('12.9'),_safe_int('bad',7),_safe_int(None,4),_safe_int(-2.7))==(12,7,4,-2)
