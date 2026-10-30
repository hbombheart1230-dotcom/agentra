from scripts.diagnostics.check_trade_report_runtime_regression import _is_empty_placeholder
def test_cases(): assert _is_empty_placeholder({'x':[]}) and not _is_empty_placeholder({'x':1})
