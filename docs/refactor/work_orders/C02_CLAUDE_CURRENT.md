# C02 — Claude A | A-20261101-04 | FAST-3 8 NEW VERIFIED SOURCE BODY MOVEs

**ONE-FILE EXECUTION CONTRACT.** At start pin integration HEAD, this C02 Git blob, A actor remote HEAD, and ORDER_ID. Read only this C02 and the named code/test files. Never read D00, RF details, queue, C03, CURRENT, HANDOFF, or self-select tasks. Execute ALL eight items A1–A8; if one is blocked, log exact blocker and continue remaining safe items. A previous in-flight order is not retroactively cancelled.

**C03 verified input:** #11 latest 6547339921 A-20261101-03 eight BODY MOVEs, targeted normal 8/8 exit0, actor HEAD `6cd49fcd2e2da882a7a76772243caf92cb92ba3f`; C04 integration `411f2ea7bd42a55d474ef12a1bc3fac16df12a87`, C05 `9348bdb20f6d17db19ba0ed02112b04fb794372d`. All previous A1–A8 are REMOTE_DONE, DO NOT REPEAT. A/integration current SOURCE `libs/reporting/quant_tactic_report.py` Git blob `29366e9ba8847cc7ad36392b726a02b6f4be2444` identical. Eight NEW TARGET files below were checked absent on both A and integration. B remote `da1ec19b27aedefea64381ca88ba9c1d2c3fec20`, B2–B8 seven code MOVEs LOCAL_ONLY due HTTPS push auth (#12 6547301271); B work is not A work. #32 latest 6520075820 Exited(255)/RUN_SOURCE_SHA UNKNOWN; RunLab HOLD. Emergency `069dadd5` unchanged.

**OWNER:** RF-035, CLAUDE_A, reporting-only transformations. A changes ONLY named SOURCE, eight NEW Owner Python files and NEW targeted test in its own `work/p15-a-reporter-pure-20261021` branch. C03 does not implement actor code/tests. C04 integrates and C05 decides G1/G2/G3 and RF status. Do not touch B branch, D00, RF/queue/STATUS, C04/C05, CI/frozen oracle, runtime or live broker/order/Guard/Step5C/UEF/RunLab effects. No force push.

**MANDATORY MOVE RULE:** Copy the COMPLETE executable original function calculation below into its unique Owner (not a second copy), preserving exact value, ordering, copy/identity, exception and Unicode output. In SOURCE retain the original signature/annotations and only a thin `return` delegation to Owner. SOURCE has `import sys` already; import Owner under unique alias, preferably module-level. Owner MUST NOT import SOURCE. Where a function calls SOURCE helper(s), Owner accepts keyword-only `facade` and resolves them through `facade.<name>` at call time, preserving post-import monkeypatch. Do not accidentally create circular imports or remove source public names. No policy changes.

**G2 & PUSH:** Write NEW `tests/test_p15_rf035_20261101_04h_quant_tactic_owners.py` with eight named tests `test_a1_playbook` ... `test_a8_exit_tactic_drifts`. Capture golden ORIGINAL source before edits (preimage from pinned source blob), then compare original vs wrapper vs direct Owner for positive, negative, exception, identity and patched facade seam. AST confirm SOURCE body removed and no duplicate calculation. Run `python -m py_compile libs/reporting/quant_tactic_report.py` plus each new Owner, then `python -m unittest tests/test_p15_rf035_20261101_04h_quant_tactic_owners.py -v` normal exit0 and directly affected existing `tests/test_quant_tactic_report.py` if present. Fake in-memory dict/list only, no actual runtime/main, no subprocess, network, real paths or state. Commit ONLY code/new test to A branch, normal push, re-fetch actor HEAD and all SOURCE/Owner/test blobs. If push fails, report PUSH_BLOCKED but continue safe tasks; local commit is not remote G1. Report per-item results, exact normal exit, SHA, and actually measured START/END to #11. -O/full peer/hosted CI NOT mandatory.

## A1 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_playbook` | CURRENT_BLOB `29366e9ba8847cc7ad36392b726a02b6f4be2444`
**NEW TARGET (404 A/integration):** `libs/reporting/quant_tactic_playbook_projection.py::_playbook`.
**ORIGINAL EXECUTABLE BODY TO MOVE EXACTLY:**
```python
def _playbook(report: Mapping[str, Any], *, fallback: str = "") -> str:
    for item in (
        _mapping(report.get("strategist_summary")),
        _mapping(report.get("market_context_at_entry")),
        _mapping(report.get("market_context")),
    ):
        value = str(item.get("playbook") or item.get("selected_playbook") or "").strip()
        if value:
            return value
    return str(fallback or "").strip()
```
**SOURCE THIN WRAPPER:** keep exact signature; `from libs.reporting import quant_tactic_playbook_projection as _a1_owner`; sole executable calculation becomes `return _a1_owner._playbook(report, fallback=fallback, facade=sys.modules[__name__])`. Owner adds keyword-only facade and replaces runtime SOURCE helper lookup(s) `_mapping` with `facade.<name>`; no SOURCE import. Keep call-time monkeypatch and original error/identity semantics.
**NORMAL TARGETED TEST `test_a1_playbook`:** report={'market_context':{'selected_playbook':'PB'}} -> 'PB'; report={},fallback='F' -> 'F'. Compare original-golden/wrapper/direct Owner, patched SOURCE helper seam if any, and SOURCE AST thin delegation. **BLOCKED:** report exact failure and proceed A2.

## A2 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_entry_visibility` | CURRENT_BLOB `29366e9ba8847cc7ad36392b726a02b6f4be2444`
**NEW TARGET (404 A/integration):** `libs/reporting/quant_tactic_entry_visibility_projection.py::_entry_visibility`.
**ORIGINAL EXECUTABLE BODY TO MOVE EXACTLY:**
```python
def _entry_visibility(report: Mapping[str, Any]) -> Dict[str, Any]:
    return _mapping(report.get("entry_execution_visibility"))
```
**SOURCE THIN WRAPPER:** keep exact signature; `from libs.reporting import quant_tactic_entry_visibility_projection as _a2_owner`; sole executable calculation becomes `return _a2_owner._entry_visibility(report, facade=sys.modules[__name__])`. Owner adds keyword-only facade and replaces runtime SOURCE helper lookup(s) `_mapping` with `facade.<name>`; no SOURCE import. Keep call-time monkeypatch and original error/identity semantics.
**NORMAL TARGETED TEST `test_a2_entry_visibility`:** {'entry_execution_visibility':{'x':1}} -> {'x':1}; {} -> {}. Compare original-golden/wrapper/direct Owner, patched SOURCE helper seam if any, and SOURCE AST thin delegation. **BLOCKED:** report exact failure and proceed A3.

## A3 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_entry_info_from_visibility` | CURRENT_BLOB `29366e9ba8847cc7ad36392b726a02b6f4be2444`
**NEW TARGET (404 A/integration):** `libs/reporting/quant_tactic_entry_info_projection.py::_entry_info_from_visibility`.
**ORIGINAL EXECUTABLE BODY TO MOVE EXACTLY:**
```python
def _entry_info_from_visibility(visibility: Mapping[str, Any], monitor: Mapping[str, Any]) -> Dict[str, Any]:
    focus = _mapping(visibility.get("monitor_focus_context"))
    grouped = _mapping(visibility.get("entry_grouped_logic_trace"))
    cascade = _mapping(visibility.get("monitor_entry_candidate_cascade"))
    out: Dict[str, Any] = {}
    out.update(grouped)
    if focus:
        out.update(
            {
                "triggered": focus.get("entry_triggered"),
                "legacy_entry_decision": focus.get("entry_decision"),
                "guard_reason": focus.get("entry_guard_reason") or focus.get("entry_reason"),
                "reason": focus.get("entry_reason"),
                "primary_failure_axis": focus.get("entry_primary_failure_axis"),
                "cost_adjusted_edge_ok": focus.get("entry_cost_adjusted_edge_ok"),
                "cost_adjusted_edge_pct": focus.get("entry_cost_adjusted_edge_pct"),
                "cost_drag_pct": focus.get("entry_cost_drag_pct"),
                "entry_cost_filter": focus.get("entry_cost_filter"),
            }
        )
    if cascade:
        out.setdefault("reason", cascade.get("reason"))
        out.setdefault("primary_failure_axis", cascade.get("primary_failure_axis"))
    if monitor:
        out.setdefault("triggered", monitor.get("entry_triggered"))
        out.setdefault("legacy_entry_decision", monitor.get("entry_decision"))
    return {key: value for key, value in out.items() if value not in (None, "")}
```
**SOURCE THIN WRAPPER:** keep exact signature; `from libs.reporting import quant_tactic_entry_info_projection as _a3_owner`; sole executable calculation becomes `return _a3_owner._entry_info_from_visibility(visibility, monitor, facade=sys.modules[__name__])`. Owner adds keyword-only facade and replaces runtime SOURCE helper lookup(s) `_mapping` with `facade.<name>`; no SOURCE import. Keep call-time monkeypatch and original error/identity semantics.
**NORMAL TARGETED TEST `test_a3_entry_info_from_visibility`:** visibility={'monitor_focus_context':{'entry_triggered':True,'entry_reason':'ok'}},monitor={} -> triggered=True,reason='ok',guard_reason='ok'; {},{} -> {}. Compare original-golden/wrapper/direct Owner, patched SOURCE helper seam if any, and SOURCE AST thin delegation. **BLOCKED:** report exact failure and proceed A4.

## A4 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_candidate_symbol` | CURRENT_BLOB `29366e9ba8847cc7ad36392b726a02b6f4be2444`
**NEW TARGET (404 A/integration):** `libs/reporting/quant_tactic_candidate_symbol_projection.py::_candidate_symbol`.
**ORIGINAL EXECUTABLE BODY TO MOVE EXACTLY:**
```python
def _candidate_symbol(row: Mapping[str, Any]) -> str:
    return str(row.get("symbol") or row.get("code") or row.get("stk_cd") or row.get("ticker") or "").strip()
```
**SOURCE THIN WRAPPER:** keep exact signature; `from libs.reporting import quant_tactic_candidate_symbol_projection as _a4_owner`; sole executable calculation becomes `return _a4_owner._candidate_symbol(row)`. Owner keeps pure computation and original argument order; no SOURCE import. Keep call-time monkeypatch and original error/identity semantics.
**NORMAL TARGETED TEST `test_a4_candidate_symbol`:** {'ticker':'005930'} -> '005930'; {} -> ''. Compare original-golden/wrapper/direct Owner, patched SOURCE helper seam if any, and SOURCE AST thin delegation. **BLOCKED:** report exact failure and proceed A5.

## A5 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_scanner_chart_fit_from_row` | CURRENT_BLOB `29366e9ba8847cc7ad36392b726a02b6f4be2444`
**NEW TARGET (404 A/integration):** `libs/reporting/quant_tactic_scanner_chart_fit_projection.py::_scanner_chart_fit_from_row`.
**ORIGINAL EXECUTABLE BODY TO MOVE EXACTLY:**
```python
def _scanner_chart_fit_from_row(row: Mapping[str, Any]) -> Dict[str, Any]:
    explicit = _mapping(row.get("scanner_chart_fit"))
    if explicit:
        return explicit
    if row.get("scanner_chart_fit_score") in (None, "") and not _mapping(row.get("scanner_chart_fit_components")):
        return {}
    return {
        "score": row.get("scanner_chart_fit_score"),
        "authority": str(row.get("scanner_chart_fit_authority") or ""),
        "components": _mapping(row.get("scanner_chart_fit_components")),
        "penalty": row.get("scanner_chart_fit_penalty"),
    }
```
**SOURCE THIN WRAPPER:** keep exact signature; `from libs.reporting import quant_tactic_scanner_chart_fit_projection as _a5_owner`; sole executable calculation becomes `return _a5_owner._scanner_chart_fit_from_row(row, facade=sys.modules[__name__])`. Owner adds keyword-only facade and replaces runtime SOURCE helper lookup(s) `_mapping` with `facade.<name>`; no SOURCE import. Keep call-time monkeypatch and original error/identity semantics.
**NORMAL TARGETED TEST `test_a5_scanner_chart_fit_from_row`:** {'scanner_chart_fit_score':2} -> {'score':2,'authority':'','components':{},'penalty':None}; {} -> {}. Compare original-golden/wrapper/direct Owner, patched SOURCE helper seam if any, and SOURCE AST thin delegation. **BLOCKED:** report exact failure and proceed A6.

## A6 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_tactic_value` | CURRENT_BLOB `29366e9ba8847cc7ad36392b726a02b6f4be2444`
**NEW TARGET (404 A/integration):** `libs/reporting/quant_tactic_value_projection.py::_tactic_value`.
**ORIGINAL EXECUTABLE BODY TO MOVE EXACTLY:**
```python
def _tactic_value(value: Any) -> str:
    return str(value or "").strip()
```
**SOURCE THIN WRAPPER:** keep exact signature; `from libs.reporting import quant_tactic_value_projection as _a6_owner`; sole executable calculation becomes `return _a6_owner._tactic_value(value)`. Owner keeps pure computation and original argument order; no SOURCE import. Keep call-time monkeypatch and original error/identity semantics.
**NORMAL TARGETED TEST `test_a6_tactic_value`:** '  A ' -> 'A'; None -> ''. Compare original-golden/wrapper/direct Owner, patched SOURCE helper seam if any, and SOURCE AST thin delegation. **BLOCKED:** report exact failure and proceed A7.

## A7 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_tactic_mismatches` | CURRENT_BLOB `29366e9ba8847cc7ad36392b726a02b6f4be2444`
**NEW TARGET (404 A/integration):** `libs/reporting/quant_tactic_mismatches_projection.py::_tactic_mismatches`.
**ORIGINAL EXECUTABLE BODY TO MOVE EXACTLY:**
```python
def _tactic_mismatches(sources: List[tuple[str, str]], tactic_id: str) -> List[Dict[str, str]]:
    return [
        {"source": source, "tactic_id": value}
        for source, value in sources
        if tactic_id and value != tactic_id and source != "exit_quant_decision"
    ]
```
**SOURCE THIN WRAPPER:** keep exact signature; `from libs.reporting import quant_tactic_mismatches_projection as _a7_owner`; sole executable calculation becomes `return _a7_owner._tactic_mismatches(sources, tactic_id)`. Owner keeps pure computation and original argument order; no SOURCE import. Keep call-time monkeypatch and original error/identity semantics.
**NORMAL TARGETED TEST `test_a7_tactic_mismatches`:** sources=[('entry','B'),('exit_quant_decision','C')],tactic_id='A' -> [{'source':'entry','tactic_id':'B'}]; tactic_id='' -> []. Compare original-golden/wrapper/direct Owner, patched SOURCE helper seam if any, and SOURCE AST thin delegation. **BLOCKED:** report exact failure and proceed A8.

## A8 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_exit_tactic_drifts` | CURRENT_BLOB `29366e9ba8847cc7ad36392b726a02b6f4be2444`
**NEW TARGET (404 A/integration):** `libs/reporting/quant_tactic_exit_drifts_projection.py::_exit_tactic_drifts`.
**ORIGINAL EXECUTABLE BODY TO MOVE EXACTLY:**
```python
def _exit_tactic_drifts(sources: List[tuple[str, str]], tactic_id: str) -> List[Dict[str, str]]:
    return [
        {"source": source, "tactic_id": value}
        for source, value in sources
        if tactic_id and value != tactic_id and source == "exit_quant_decision"
    ]
```
**SOURCE THIN WRAPPER:** keep exact signature; `from libs.reporting import quant_tactic_exit_drifts_projection as _a8_owner`; sole executable calculation becomes `return _a8_owner._exit_tactic_drifts(sources, tactic_id)`. Owner keeps pure computation and original argument order; no SOURCE import. Keep call-time monkeypatch and original error/identity semantics.
**NORMAL TARGETED TEST `test_a8_exit_tactic_drifts`:** sources=[('entry','B'),('exit_quant_decision','C')],tactic_id='A' -> [{'source':'exit_quant_decision','tactic_id':'C'}]; tactic_id='' -> []. Compare original-golden/wrapper/direct Owner, patched SOURCE helper seam if any, and SOURCE AST thin delegation. **BLOCKED:** report exact failure and proceed A1–A8 remaining/push.

## FUTURE RESERVE — RF-035 CLAUDE_A | VERIFIED 6/6, DESIGN ONLY, NOT EXECUTABLE
Six separate reporting evaluation calculations were inspected on BOTH actor/integration SOURCE `libs/reporting/quant_tactic_evaluation.py` Git blob `f11bd1e71dedb5494242fa88f3996885d1a3cef2`; all six unique TARGETs verified absent on both. RF-035 owns this reporting path per RF-035 file coverage. This is report-side evaluation only: no broker invocation, live trade readiness decision, real account/Guard/Step5C/UEF/RunLab effect. Future C03 must refresh SHA, caller and target absence before issuing; A must NOT implement these reserves in the present order.

### R1 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_evaluation.py::_closed_or_realized` | BLOB `f11bd1e71dedb5494242fa88f3996885d1a3cef2`
**FUTURE TARGET (404 A/integration):** `libs/reporting/quant_tactic_eval_closed_projection.py::_closed_or_realized`. **BODY VERIFIED, DESIGN ONLY:**
```python
def _closed_or_realized(row: Mapping[str, Any]) -> bool:
    status = str(row.get("status") or row.get("last_status") or "").strip().lower()
    action = str(row.get("last_action") or row.get("action") or "").strip().upper()
    origin = str(row.get("trade_origin") or "").strip().lower()
    partial = status == "partial" or origin == "recovered_partial"
    return bool(
        row.get("is_closed_trade")
        or row.get("is_realized_nonclosed_exit")
        or (status == "closed" and not partial)
        or (action == "SELL" and partial)
    )
```
**Future seam:** pure in-memory calculation; preserve SOURCE monkeypatch at invocation; Owner no SOURCE import. **Fake normal fixture:** {'status':'closed'} -> True; {'status':'partial','action':'SELL'} -> True; {} -> False. No external IO or operational execution.

### R2 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_evaluation.py::_evaluation_rows` | BLOB `f11bd1e71dedb5494242fa88f3996885d1a3cef2`
**FUTURE TARGET (404 A/integration):** `libs/reporting/quant_tactic_eval_rows_projection.py::_evaluation_rows`. **BODY VERIFIED, DESIGN ONLY:**
```python
def _evaluation_rows(rows: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows if isinstance(row, Mapping) and _closed_or_realized(row)]
```
**Future seam:** `facade.Mapping`, `facade._closed_or_realized`; preserve SOURCE monkeypatch at invocation; Owner no SOURCE import. **Fake normal fixture:** [{'status':'closed','trade_id':'T'},{'status':'open'}] -> [{'status':'closed','trade_id':'T'}]. No external IO or operational execution.

### R3 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_evaluation.py::_invalid_sample_reason` | BLOB `f11bd1e71dedb5494242fa88f3996885d1a3cef2`
**FUTURE TARGET (404 A/integration):** `libs/reporting/quant_tactic_eval_invalid_reason_projection.py::_invalid_sample_reason`. **BODY VERIFIED, DESIGN ONLY:**
```python
def _invalid_sample_reason(row: Mapping[str, Any]) -> str:
    status = _text(row.get("broker_alignment_status")).lower()
    if status and status not in {"ok"}:
        return f"broker_alignment_{status}"
    if _int(row.get("broker_alignment_missing_in_local_total")) > 0:
        return "broker_missing_in_local"
    if _int(row.get("broker_alignment_missing_in_broker_total")) > 0:
        return "broker_missing_in_broker"
    snapshot_status = _text(row.get("broker_account_snapshot_status")).lower()
    if snapshot_status and snapshot_status not in {"ok"}:
        return f"account_snapshot_{snapshot_status}"
    if _int(row.get("broker_alignment_account_snapshot_error_count")) > 0:
        return "account_snapshot_partial_errors"
    return ""
```
**Future seam:** `facade._text`, `facade._int`; preserve SOURCE monkeypatch at invocation; Owner no SOURCE import. **Fake normal fixture:** {'broker_alignment_status':'bad'} -> 'broker_alignment_bad'; {} -> ''. No external IO or operational execution.

### R4 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_evaluation.py::_valid_evaluation_rows` | BLOB `f11bd1e71dedb5494242fa88f3996885d1a3cef2`
**FUTURE TARGET (404 A/integration):** `libs/reporting/quant_tactic_eval_valid_rows_projection.py::_valid_evaluation_rows`. **BODY VERIFIED, DESIGN ONLY:**
```python
def _valid_evaluation_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [row for row in rows if not _invalid_sample_reason(row)]
```
**Future seam:** `facade._invalid_sample_reason`; preserve SOURCE monkeypatch at invocation; Owner no SOURCE import. **Fake normal fixture:** [{'broker_alignment_status':'bad'},{}] -> [{}]. No external IO or operational execution.

### R5 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_evaluation.py::_invalid_sample_examples` | BLOB `f11bd1e71dedb5494242fa88f3996885d1a3cef2`
**FUTURE TARGET (404 A/integration):** `libs/reporting/quant_tactic_eval_invalid_examples_projection.py::_invalid_sample_examples`. **BODY VERIFIED, DESIGN ONLY:**
```python
def _invalid_sample_examples(rows: List[Dict[str, Any]], *, limit: int = 5) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row in rows:
        reason = _invalid_sample_reason(row)
        if not reason:
            continue
        out.append(
            {
                "trade_id": _text(row.get("trade_id")),
                "symbol": _text(row.get("symbol")),
                "reason": reason,
            }
        )
        if len(out) >= limit:
            break
    return out
```
**Future seam:** `facade._invalid_sample_reason`, `facade._text`; preserve SOURCE monkeypatch at invocation; Owner no SOURCE import. **Fake normal fixture:** [{'trade_id':'T','symbol':'S','broker_alignment_status':'bad'}] -> [{'trade_id':'T','symbol':'S','reason':'broker_alignment_bad'}]. No external IO or operational execution.

### R6 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_evaluation.py::_field_gap_rows` | BLOB `f11bd1e71dedb5494242fa88f3996885d1a3cef2`
**FUTURE TARGET (404 A/integration):** `libs/reporting/quant_tactic_eval_field_gaps_projection.py::_field_gap_rows`. **BODY VERIFIED, DESIGN ONLY:**
```python
def _field_gap_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    count = len(rows)
    out: List[Dict[str, Any]] = []
    for field in _REQUIRED_FIELDS:
        captured = sum(1 for row in rows if _text(row.get(field)))
        coverage = float(captured) / float(count) if count else 0.0
        out.append(
            {
                "field": field,
                "captured_count": captured,
                "missing_count": max(0, count - captured),
                "coverage": coverage,
                "coverage_ok": coverage >= _FIELD_COVERAGE_FLOOR,
            }
        )
    return out
```
**Future seam:** `facade._REQUIRED_FIELDS`, `facade._text`, `facade._FIELD_COVERAGE_FLOOR`; preserve SOURCE monkeypatch at invocation; Owner no SOURCE import. **Fake normal fixture:** [{'quant_tactic_id':'X'}] -> five field rows, quant_tactic_id coverage=1.0 and remaining coverage=0.0. No external IO or operational execution.

**COUNTS:** A current NEW_READY=8; A future RESERVE_VERIFIED=6; previous A-03 REMOTE_DONE=8; B current remote pending=7 (local-only is not REMOTE_DONE); C03 document-only, code/test implementation=0, RF_DONE_DELTA=0. If a target appears or SOURCE changes before execution, report exact conflict, skip unsafe item and continue others; C03 reissues on next delta.