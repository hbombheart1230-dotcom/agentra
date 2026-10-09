"""P1.5.2 summary-input schema byte goldens (synthetic; not broker report data)."""
import ast
import hashlib
import json
from pathlib import Path
import pytest
from libs.reporting.trade_report.markdown_summary import build_trade_summary_input
from libs.reporting.trade_report.summary_input_parts.broker_alignment import build_broker_alignment
from libs.reporting.trade_report.summary_input_parts.market_and_strategy import build_market_and_strategy
from libs.reporting.trade_report.summary_input_parts.decision_flow import build_decision_flow
from tests.test_p152_markdown_render_section_owners import deps as render_deps, CASES

EXPECTED = {
"empty":"248f379f1602b1e4dbcaeb1bf2e70094ec172b9d2628816d4ae1101ec9a12ad4",
"buy":"f9db3e694b9756e4acbebcd295d6bc8a9508ab0613d9eb3adf890de0a2a2ffc7",
"loss":"067401ebcca74ecf68e0555748ffe9c7705d852de5f1e98057a7764c9c42ba03",
"carryover":"3b2d9208aa6f7d4b0751aab61486edfb50d74ab7d3c473ada379145381f55b02",
"partial":"36ee618353aa77c768475f93232ed9fa99a6f74342efa4442cfd2b3177a4fdf9",
"fallback":"019db8ee2046710af92df185df3e0d0796ab9204bd873234ab186f7fd3e0dcbe",
}
def deps():
    d = render_deps()
    source = Path('libs/reporting/trade_report/markdown_summary.py').read_text(encoding='utf-8')
    f = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'build_trade_summary_input')
    keys = [n.value.slice.value for n in f.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Subscript) and isinstance(n.value.value,ast.Name) and n.value.value.id=='deps' and isinstance(n.value.slice,ast.Constant)]
    for k in keys:
        d.setdefault(k,lambda *a,**kw:'')
    d.update(
        authoritative_hold_duration_seconds=lambda r:None,
        compact_post_exit_shadow=lambda *a:{},
        entry_watch_execution_lines=lambda *a,**kw:[],
        post_exit_shadow_surface=lambda *a:{},
        quant_tactic_surface_impl=lambda *a:{},
        strategy_horizon_report_surface=lambda *a:{},
        resolve_entry_execution_visibility=lambda *a:{},
        truth_source_label=str,
    )
    return d

@pytest.mark.parametrize('name,report',CASES)
def test_summary_input_pre_split_json_golden(name,report):
    result = build_trade_summary_input(report,deps=deps())
    payload = json.dumps(result,ensure_ascii=False,sort_keys=True).encode()
    assert hashlib.sha256(payload).hexdigest()==EXPECTED[name]

def test_canonical_summary_input_parts_are_bounded_and_do_not_import_facades():
    for fn in (build_broker_alignment,build_market_and_strategy,build_decision_flow):
        src=Path(fn.__code__.co_filename).read_text(encoding='utf-8')
        assert len(src.splitlines())<=350
        assert 'from libs.reporting.trade_report_markdown_clean import' not in src
        assert 'from libs.reporting.trade_report_ai import' not in src
        assert 'from libs.reporting.trade_report.markdown_summary import' not in src


def test_input_public_wrapper_uses_call_time_decision_builder(monkeypatch):
    import libs.reporting.trade_report.markdown_summary as api
    monkeypatch.setattr(api, "build_decision_flow", lambda **kwargs: {"patched": True})
    result = api.build_trade_summary_input({}, deps=deps())
    assert result["decision_flow"] == {"patched": True}
