"""P1.5.2 renderer smoke goldens, pinned from pre-split source (not production data)."""
import ast
import hashlib
import inspect
from pathlib import Path
import pytest
from libs.reporting.trade_report.markdown_summary import render_trade_summary_markdown
from libs.reporting.trade_report.summary_render_parts.overview import append_summary_overview
from libs.reporting.trade_report.summary_render_parts.market_news import append_summary_market_news
from libs.reporting.trade_report.summary_render_parts.decision_lifecycle import append_summary_decision_lifecycle
from libs.reporting.trade_report.summary_render_parts.closing import append_summary_closing

def _as_dict(x):return x if isinstance(x,dict) else {}
def _list(x):return x if isinstance(x,list) else ([] if x in (None,"") else [x])
def _num(x):
    try:return float(x) if x not in (None,"") else None
    except (TypeError,ValueError):return None
def _clip(x,n=200,max_len=None):return str(x if x is not None else "")[:max_len or n]
def _one(*args,**kwargs):return ""
def _empty(*args,**kwargs):return {}
def _none(*args,**kwargs):return []
def _str(x):return str(x if x is not None else "")
def _pct(x):
    n=_num(x)
    return f"{n*100:.2f}%" if n is not None else "-"

def deps():
    s=Path(inspect.getsourcefile(render_trade_summary_markdown)).read_text(encoding="utf-8")
    fn=next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name=="render_trade_summary_markdown")
    keys=[x.value.slice.value for x in fn.body if isinstance(x,ast.Assign)
          and isinstance(x.value,ast.Subscript) and isinstance(x.value.value,ast.Name)
          and x.value.value.id=="deps" and isinstance(x.value.slice,ast.Constant)]
    d={x:_one for x in keys}
    d.update(dict(
        RECOVERED_PARTIAL_ENTRY_NOTE="recovered partial entry not captured",
        RECOVERED_PARTIAL_EXIT_NOTE="recovered partial exit",
        as_dict=_as_dict, clip=_clip, listify=_list, num_opt=_num, fmt_pct=_pct,
        operator_pnl_pct=lambda p,sh:(p.get("pnl_pct",sh.get("pnl_pct")),False),
        get_truth_surface=lambda r:r.get("truth_surface",{}),
        resolve_market_context=lambda r:r.get("market_context_at_entry",{}),
        resolve_trade_symbol_metadata=lambda r,s:r.get("symbol_metadata",{}),
        resolve_entry_signal_snapshot=lambda r:r.get("entry_signal_snapshot",{}),
        enrich_exit_signal_snapshot_from_monitor=lambda snap,mon:snap,
        extract_exit_signal_snapshot=lambda lines:{},
        build_trade_cost_analysis=lambda r:r.get("cost_analysis",{}),
        selection_fallback_context=lambda selection,symbol:selection.get("selection_fallback",{}),
        carryover_context=lambda r:r.get("carryover_context",{}),
        is_recovered_partial_exit_report=lambda r:r.get("recovered_partial",False),
        is_not_captured=lambda x:x in (None,"","not_captured","-"),
        is_post_entry_gate_text=lambda t:False,
        entry_confidence_for_operator_summary=_one,
        normalize_entry_confidence_for_operator_summary=_one,
        entry_watch_summary_lines=_none, entry_signal_metric_summary_lines=_none,
        entry_reason_line=lambda lines:next((str(x) for x in lines if x),""),
        sample_news_titles=_none, sample_news_titles_for_symbol=_none,
        render_quant_tactic_report_lines_impl=_none,
        render_controlled_lane_report_lines=_none,
        build_strategy_horizon_lines=_none,
        build_post_exit_shadow_summary_lines=_none,
        build_summary_exit_trigger_lines=_none,
        trade_cost_analysis_lines=_none, korea_index_lines=_none,
        same_day_current_result=_empty,
        same_day_summary_from_texts=lambda *a,**kw:"Day summary",
        authoritative_holding_duration_label=lambda r:r.get("hold_duration",""),
        authoritative_final_operator_summary=lambda r,**kw:r.get("final_operator_conclusion",{}).get("summary",""),
        strip_trailing_blanks=lambda rows:rows,
        dedupe=lambda values:list(dict.fromkeys(values)),
        translate_text=_str,translated_metadata=_str,metadata_value=_str,
        theme_label=_str,playbook_label=_str,risk_mode_label=_str,
        status_label=_str,story_type_label=_str,execution_mode_label=_str,
        action_label=_str,normalize_exit_trigger_label=lambda a,b:a or b,
        memory_layers_text=_str,applied_label=_str,ensure_sentence=_str,
        pnl_basis_label=lambda p,sh:"broker truth",
    ))
    return d

CASES=[
("empty",{}),
("buy",{"trade_id":"TRD_20261009001","symbol":"005930","action":"BUY","shared_facts":{"pnl":100,"broker_buy_price":81000},"truth_surface":{"price":{"broker_buy_price":81000,"broker_fill_price":83000},"pnl":{"value":100,"pnl_pct":0.012}},"market_context_at_entry":{"summary":"Market bullish","playbook":"breakout","vix_level":19.4,"market_sentiment":"bull","market_news_titles":["positive"]},"symbol_metadata":{"symbol_name":"삼성전자","theme":"반도체"},"why_this_symbol_was_chosen":{"basis":"highest rank","selected_rank":1},"entry_decision":{"summary":"Signal good","bullets":["VWAP 확인"]},"exit_decision":{"summary":"exit","bullets":["목표 수익"]},"hold_duration":"2h","full_timeline":[{"event":"entry","run_id":"e1"},{"event":"exit","run_id":"e2"}]}),
("loss",{"symbol":"000660","shared_facts":{"pnl":-200,"broker_fee":7,"broker_tax":3,"exit_reason":"hard_stop"},"truth_surface":{"pnl":{"value":-200,"pnl_pct":-0.02}},"monitor_snapshot":{"entry_evaluated":True},"cost_analysis":{"mock_cost_warning":True,"cost_drag_pct":0.001},"why_this_symbol_was_chosen":{"selected_rank":2,"selection_fallback":{"used":True,"scanner_top_pick_symbol":"005930"}}}),
("carryover",{"symbol":"005930","status":"closed","carryover_context":{"is_carryover_exit":True,"date_basis":"previous","estimated_entry_kst":"2026-10-08T14:35","exit_kst":"2026-10-09T09:15","duration_label":"overnight","exit_date_kst":"2026-10-09","estimated_entry_date_kst":"2026-10-08","weekend_carry":True},"market_context_at_entry":{"summary":"Regime changed"}}),
("partial",{"symbol":"005930","recovered_partial":True,"shared_facts":{"pnl":20},"truth_surface":{"pnl":{"value":20,"pnl_pct":0.01}},"final_operator_conclusion":{"summary":"needs review"}}),
("fallback",{"symbol":"000660","why_this_symbol_was_chosen":{"selection_fallback":{"used":True,"reason":"rank-1 blocked","scanner_top_pick_symbol":"005930"}}}),
]
GOLDEN={
"empty":"ec938fbd6a8599b537fd2c567f37f0b9a02bac438d4618759b3f03a2cdbc4838",
"buy":"69695efaafbad22ea7ab3b8b9d469d8adad875b02e2e94921dcbb55679c4b75a",
"loss":"d10df4062a135180944c29bb00a83a20cd3a4ebcd31485376b8d81fcff6a0478",
"carryover":"c958586fbfbcdc5f906836d5b99626fedef088aa648aaabca086b50963d90937",
"partial":"c8839500becade7cf5a309412ba0fe77e3bbd4315af86d0cbd10b5f9288c86fd",
"fallback":"ce5b1ee0eb426c56eff52956c8756609d875cb201b446f8662604d9daa6edb99",
}
@pytest.mark.parametrize("name,report",CASES)
def test_original_renderer_byte_golden(name,report):
    actual=render_trade_summary_markdown(report,deps=deps())
    assert hashlib.sha256(actual.encode()).hexdigest()==GOLDEN[name]

def test_render_section_owners_are_bounded_and_no_reverse_import():
    for fn in (append_summary_overview,append_summary_market_news,
               append_summary_decision_lifecycle,append_summary_closing):
        code=Path(inspect.getsourcefile(fn)).read_text(encoding="utf-8")
        assert len(code.splitlines())<=350
        for node in ast.walk(ast.parse(code)):
            if isinstance(node,ast.ImportFrom):
                assert all(name not in (node.module or "") for name in
                           ("markdown_summary","trade_report_ai","trade_report_markdown_clean"))
