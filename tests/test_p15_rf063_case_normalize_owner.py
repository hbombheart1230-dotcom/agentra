from scripts.diagnostics.check_trade_report_runtime_regression import _normalize_cases
def test_cases(): assert _normalize_cases(['2026-10-30:T:R1','2026-10-30:T:R2'])==[{'day':'2026-10-30','trade_id':'T','target_run_id':'R1'}]
