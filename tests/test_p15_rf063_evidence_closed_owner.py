from scripts.diagnostics.check_trade_report_runtime_regression import _is_closed_trade
def test_cases(): assert not _is_closed_trade({'status':'open'},{'run_id':'R'}) and _is_closed_trade({'status':'closed'},{})
