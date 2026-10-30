from scripts.diagnostics.check_trade_report_runtime_regression import _has_substantive_exit_evidence
def test_cases(): assert not _has_substantive_exit_evidence({}) and _has_substantive_exit_evidence({'reason_human':'stop'})
