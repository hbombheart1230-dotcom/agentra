import pytest
from scripts.diagnostics.check_trade_report_runtime_regression import _parse_case
def test_cases(): assert _parse_case('2026-10-30:T:R')['target_run_id']=='R';
