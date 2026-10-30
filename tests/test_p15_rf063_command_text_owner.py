from scripts.diagnostics.check_trade_report_runtime_regression import _command_to_text
def test_cases(): assert _command_to_text(['a',12,None])=='a 12 None'
