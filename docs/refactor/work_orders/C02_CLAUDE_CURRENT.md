# C02 — Claude A | A-20261101-03 | FAST-3 8 VERIFIED real SOURCE BODY MOVEs

**START ORDER — ONE FILE ONLY.** Read this C02, then ONLY the code/test paths below. Pin actual remote integration HEAD, this C02 blob, A branch HEAD and ORDER_ID at start. Do not read D00, RF, queue, C03, HANDOFF or choose work. Complete ALL 8 independent items; if one is blocked, log it and proceed through remaining safe items. New order does not retroactively cancel a previously started order.

**C03 evidence at issuance:** previous A-20261101-02 C02 blob `a597df70020925ef58682b57fbe92d54a33c6881` 8/8 REMOTE_DONE by A remote `449fc36ed9b8d7c4244cfc6105db99913b3dd6d4`, #11 comment `6546657974`, normal targeted 8/8 exit0. B latest remote `da1ec19b27aedefea64381ca88ba9c1d2c3fec20` includes one new B1 M26 epoch MOVE; B C01 is separately handled, not this Actor's code. #32 latest `6520075820` still RunLab Exited(255), RUN_SOURCE_SHA UNKNOWN; operational HOLD. Emergency `069dadd5` unchanged. The 8 below are NEW, not the completed A-02 items.

**OWNER:** RF-035 / CLAUDE_A exclusively. SOURCE `libs/reporting/quant_tactic_report.py` original executable BODY verified on A and integration, both blob `95581e3572bd3be06e6c3b93638b22091a968056`. This is reporting-only transformation, not a live decision engine. New target paths verified absent in BOTH A branch and integration directory listings. A modifies ONLY its own branch's named code/new code tests. C03 does NOT write actor code/test. No C04/C05/D00/RF/queue/STATUS/frozen oracle/CI changes. No force-push.

**SAFETY:** in-memory dict/list and monkeypatch fakes only. No real broker, orders, Guard, Step5C, UEF, RunLab, live network, operational IO/State, subprocess, or production entrypoint. No behavioral or formatting change. Preserve original public signature, exception parity, order, identity/copy semantics, and post-import SOURCE monkeypatch seams. Original source becomes a single-return thin compatibility wrapper; new Owner owns the real computation BODY, not a duplicate. New Owner MUST NOT import SOURCE; pass `facade=sys.modules[__name__]` and resolve SOURCE globals through facade at invocation. In each SOURCE wrapper use `import sys` and `from libs.reporting import <target_module> as _owner` locally (or equivalent noncyclic safe import), then one `return` to Owner. New Owner signature may add keyword-only `facade`. Recursion in A6 must invoke facade._nested_dicts, not create duplicate calculation.

**TEST/PUSH:** new `tests/test_p15_rf035_20261101_03h_quant_tactic_owners.py` (do not overwrite prior tests), 8 independent named tests. Capture ORIGINAL preimage golden before edit; compare original vs SOURCE wrapper vs direct Owner for positive/negative/exception and patch seam. AST assert original calculation removed from SOURCE and no duplicate/orphan body. Run `python -m py_compile libs/reporting/quant_tactic_report.py libs/reporting/quant_tactic_*_projection.py` on actually created files and `python -m unittest tests/test_p15_rf035_20261101_03h_quant_tactic_owners.py -v` normal exit0. Run relevant existing targeted consumers if available, without unrelated full-suite or mandatory -O. Commit only A code/new test, normal push `work/p15-a-reporter-pure-20261021`, re-fetch remote A HEAD and SOURCE/TARGET/test blobs, report exact per-item outcome, test exit, SHA and measured START/END to #11. Git auth failure is PUSH_BLOCKED only; continue safe local items. C04 owns G3 integration, C05 owns RF DONE; this C03 order is not code G1/G2/G3 evidence.

## A1 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_mapping` @ L11 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**NEW TARGET (verified absent on A and integration):** `libs/reporting/quant_tactic_mapping_projection.py::_mapping`.
**EXACT ORIGINAL CALCULATION BODY — MOVE ENTIRE BODY to the new Owner, not KEEP/test-only:**
```python
def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value or {}) if isinstance(value, Mapping) else {}
```
**THIN SOURCE wrapper:** retain exact signature/annotations, use `import sys; from libs.reporting import quant_tactic_mapping_projection as _owner` inside function, replace the original calculation with `return _owner._mapping(value, facade=sys.modules[__name__])`. In Owner keep original calculation and adapt globals through `facade` at call-time; no Owner→SOURCE import, no duplicated logic. **Caller/monkeypatch seam:** Mapping.
**Normal targeted `test_a1_mapping`:** {'x':1} -> {'x':1}; [] -> {}; Mapping monkeypatch must be honored. Check preimage golden == wrapper == direct Owner, exception/identity parity and AST thin wrapper. **On blocker:** record exact error and continue A2.

## A2 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_pct` @ L23 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**NEW TARGET (verified absent on A and integration):** `libs/reporting/quant_tactic_pct_projection.py::_pct`.
**EXACT ORIGINAL CALCULATION BODY — MOVE ENTIRE BODY to the new Owner, not KEEP/test-only:**
```python
def _pct(value: Any) -> str:
    if value in (None, ""):
        return "-"
    try:
        num = float(value)
    except Exception:
        return str(value)
    return f"{num * 100.0:.2f}%"
```
**THIN SOURCE wrapper:** retain exact signature/annotations, use `import sys; from libs.reporting import quant_tactic_pct_projection as _owner` inside function, replace the original calculation with `return _owner._pct(value, facade=sys.modules[__name__])`. In Owner keep original calculation and adapt globals through `facade` at call-time; no Owner→SOURCE import, no duplicated logic. **Caller/monkeypatch seam:** pure numeric formatting.
**Normal targeted `test_a2_pct`:** 0.125 -> '12.50%'; None -> '-'; 'bad' -> 'bad'. Check preimage golden == wrapper == direct Owner, exception/identity parity and AST thin wrapper. **On blocker:** record exact error and continue A3.

## A3 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_decision_label` @ L33 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**NEW TARGET (verified absent on A and integration):** `libs/reporting/quant_tactic_decision_label_projection.py::_decision_label`.
**EXACT ORIGINAL CALCULATION BODY — MOVE ENTIRE BODY to the new Owner, not KEEP/test-only:**
```python
def _decision_label(value: Any) -> str:
    raw = str(value or "").strip()
    mapping = {
        "entry_ready": "진입 준비",
        "block_recommended": "진입 차단 권고",
        "wait": "대기",
        "hold_watch": "보유 관찰",
        "hard_exit": "즉시 청산 허용",
        "confirm_before_exit_recommended": "청산 전 확인 권고",
        "early_exit_warning": "조기 청산 경고",
        "exit_aligned": "청산 정합",
    }
    return mapping.get(raw, raw or "-")
```
**THIN SOURCE wrapper:** retain exact signature/annotations, use `import sys; from libs.reporting import quant_tactic_decision_label_projection as _owner` inside function, replace the original calculation with `return _owner._decision_label(value, facade=sys.modules[__name__])`. In Owner keep original calculation and adapt globals through `facade` at call-time; no Owner→SOURCE import, no duplicated logic. **Caller/monkeypatch seam:** pure lookup; display text only, not trade policy.
**Normal targeted `test_a3_decision_label`:** 'entry_ready' -> '진입 준비'; 'unknown' -> 'unknown'; '' -> '-'. Check preimage golden == wrapper == direct Owner, exception/identity parity and AST thin wrapper. **On blocker:** record exact error and continue A4.

## A4 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_reason_text` @ L48 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**NEW TARGET (verified absent on A and integration):** `libs/reporting/quant_tactic_reason_text_projection.py::_reason_text`.
**EXACT ORIGINAL CALCULATION BODY — MOVE ENTIRE BODY to the new Owner, not KEEP/test-only:**
```python
def _reason_text(values: Any) -> str:
    rows = _items(values)
    return ", ".join(rows[:5]) if rows else "-"
```
**THIN SOURCE wrapper:** retain exact signature/annotations, use `import sys; from libs.reporting import quant_tactic_reason_text_projection as _owner` inside function, replace the original calculation with `return _owner._reason_text(values, facade=sys.modules[__name__])`. In Owner keep original calculation and adapt globals through `facade` at call-time; no Owner→SOURCE import, no duplicated logic. **Caller/monkeypatch seam:** facade._items at call-time.
**Normal targeted `test_a4_reason_text`:** ['a','b'] -> 'a, b'; [] -> '-'; 6 rows -> first five only. Check preimage golden == wrapper == direct Owner, exception/identity parity and AST thin wrapper. **On blocker:** record exact error and continue A5.

## A5 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_monitor` @ L53 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**NEW TARGET (verified absent on A and integration):** `libs/reporting/quant_tactic_monitor_projection.py::_monitor`.
**EXACT ORIGINAL CALCULATION BODY — MOVE ENTIRE BODY to the new Owner, not KEEP/test-only:**
```python
def _monitor(report: Mapping[str, Any]) -> Dict[str, Any]:
    monitor = _mapping(report.get("monitor_snapshot"))
    if not monitor:
        monitor = _mapping(report.get("monitor_output"))
    return monitor
```
**THIN SOURCE wrapper:** retain exact signature/annotations, use `import sys; from libs.reporting import quant_tactic_monitor_projection as _owner` inside function, replace the original calculation with `return _owner._monitor(report, facade=sys.modules[__name__])`. In Owner keep original calculation and adapt globals through `facade` at call-time; no Owner→SOURCE import, no duplicated logic. **Caller/monkeypatch seam:** facade._mapping at call-time.
**Normal targeted `test_a5_monitor`:** {'monitor_output':{'x':1}} -> {'x':1}; monitor_snapshot {'y':2} overrides fallback. Check preimage golden == wrapper == direct Owner, exception/identity parity and AST thin wrapper. **On blocker:** record exact error and continue A6.

## A6 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_nested_dicts` @ L60 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**NEW TARGET (verified absent on A and integration):** `libs/reporting/quant_tactic_nested_dicts_projection.py::_nested_dicts`.
**EXACT ORIGINAL CALCULATION BODY — MOVE ENTIRE BODY to the new Owner, not KEEP/test-only:**
```python
def _nested_dicts(value: Any, *, max_depth: int = 9) -> List[Dict[str, Any]]:
    if max_depth < 0:
        return []
    out: List[Dict[str, Any]] = []
    if isinstance(value, Mapping):
        item = dict(value)
        out.append(item)
        for child in item.values():
            out.extend(_nested_dicts(child, max_depth=max_depth - 1))
    elif isinstance(value, (list, tuple)):
        for child in value:
            out.extend(_nested_dicts(child, max_depth=max_depth - 1))
    return out
```
**THIN SOURCE wrapper:** retain exact signature/annotations, use `import sys; from libs.reporting import quant_tactic_nested_dicts_projection as _owner` inside function, replace the original calculation with `return _owner._nested_dicts(value, max_depth=max_depth, facade=sys.modules[__name__])`. In Owner keep original calculation and adapt globals through `facade` at call-time; no Owner→SOURCE import, no duplicated logic. **Caller/monkeypatch seam:** facade.Mapping and facade._nested_dicts recursion at call-time.
**Normal targeted `test_a6_nested_dicts`:** {'a':{'b':1}} with max_depth=1 -> [{'a':{'b':1}},{'b':1}]; -1 -> []; nested list traverses in order. Check preimage golden == wrapper == direct Owner, exception/identity parity and AST thin wrapper. **On blocker:** record exact error and continue A7.

## A7 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_first_nested_mapping` @ L75 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**NEW TARGET (verified absent on A and integration):** `libs/reporting/quant_tactic_first_nested_mapping_projection.py::_first_nested_mapping`.
**EXACT ORIGINAL CALCULATION BODY — MOVE ENTIRE BODY to the new Owner, not KEEP/test-only:**
```python
def _first_nested_mapping(root: Mapping[str, Any], key: str) -> Dict[str, Any]:
    for item in _nested_dicts(root):
        found = _mapping(item.get(key))
        if found:
            return found
    return {}
```
**THIN SOURCE wrapper:** retain exact signature/annotations, use `import sys; from libs.reporting import quant_tactic_first_nested_mapping_projection as _owner` inside function, replace the original calculation with `return _owner._first_nested_mapping(root, key, facade=sys.modules[__name__])`. In Owner keep original calculation and adapt globals through `facade` at call-time; no Owner→SOURCE import, no duplicated logic. **Caller/monkeypatch seam:** facade._nested_dicts and facade._mapping at call-time.
**Normal targeted `test_a7_first_nested_mapping`:** ({'x':{'q':{'a':1}}},'q') -> {'a':1}; missing -> {}. Check preimage golden == wrapper == direct Owner, exception/identity parity and AST thin wrapper. **On blocker:** record exact error and continue A8.

## A8 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_symbol` @ L83 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**NEW TARGET (verified absent on A and integration):** `libs/reporting/quant_tactic_symbol_projection.py::_symbol`.
**EXACT ORIGINAL CALCULATION BODY — MOVE ENTIRE BODY to the new Owner, not KEEP/test-only:**
```python
def _symbol(report: Mapping[str, Any]) -> str:
    fact_trade = _mapping(_mapping(report.get("fact_payload")).get("trade"))
    return str(
        report.get("symbol")
        or fact_trade.get("symbol")
        or _mapping(report.get("shared_facts")).get("symbol")
        or ""
    ).strip()
```
**THIN SOURCE wrapper:** retain exact signature/annotations, use `import sys; from libs.reporting import quant_tactic_symbol_projection as _owner` inside function, replace the original calculation with `return _owner._symbol(report, facade=sys.modules[__name__])`. In Owner keep original calculation and adapt globals through `facade` at call-time; no Owner→SOURCE import, no duplicated logic. **Caller/monkeypatch seam:** facade._mapping at call-time.
**Normal targeted `test_a8_symbol`:** {'symbol':'005930'} -> '005930'; {'fact_payload':{'trade':{'symbol':'A'}}} -> 'A'; {} -> ''. Check preimage golden == wrapper == direct Owner, exception/identity parity and AST thin wrapper. **On blocker:** record exact error and continue all remaining tests/push.

## FUTURE RESERVE — VERIFIED 6/6; DESIGN ONLY; NOT EXECUTABLE

### R1 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_playbook` @ L93 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**FUTURE TARGET (absent on A and integration):** `libs/reporting/quant_tactic_playbook_projection.py::_playbook`. **DESIGN ONLY, DO NOT IMPLEMENT until a fresh C03 order.**
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
**Future targeted normal fixture:** {'market_context':{'playbook':'P'}} -> 'P'; fallback='F' -> 'F'. **Safety/seam:** facade._mapping; no runtime execution. Future C03 must recheck current SOURCE/TARGET SHA and Owner before issue.

### R2 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_entry_visibility` @ L105 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**FUTURE TARGET (absent on A and integration):** `libs/reporting/quant_tactic_entry_visibility_projection.py::_entry_visibility`. **DESIGN ONLY, DO NOT IMPLEMENT until a fresh C03 order.**
```python
def _entry_visibility(report: Mapping[str, Any]) -> Dict[str, Any]:
    return _mapping(report.get("entry_execution_visibility"))
```
**Future targeted normal fixture:** {'entry_execution_visibility':{'x':1}} -> {'x':1}. **Safety/seam:** facade._mapping; observation only. Future C03 must recheck current SOURCE/TARGET SHA and Owner before issue.

### R3 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_candidate_symbol` @ L138 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**FUTURE TARGET (absent on A and integration):** `libs/reporting/quant_tactic_candidate_symbol_projection.py::_candidate_symbol`. **DESIGN ONLY, DO NOT IMPLEMENT until a fresh C03 order.**
```python
def _candidate_symbol(row: Mapping[str, Any]) -> str:
    return str(row.get("symbol") or row.get("code") or row.get("stk_cd") or row.get("ticker") or "").strip()
```
**Future targeted normal fixture:** {'ticker':'005930'} -> '005930'; {} -> ''. **Safety/seam:** pure string extraction. Future C03 must recheck current SOURCE/TARGET SHA and Owner before issue.

### R4 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_scanner_chart_fit_from_row` @ L177 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**FUTURE TARGET (absent on A and integration):** `libs/reporting/quant_tactic_scanner_chart_fit_projection.py::_scanner_chart_fit_from_row`. **DESIGN ONLY, DO NOT IMPLEMENT until a fresh C03 order.**
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
**Future targeted normal fixture:** {'scanner_chart_fit_score':2} -> {'score':2,'authority':'','components':{},'penalty':None}; {} -> {}. **Safety/seam:** facade._mapping; no scanner execution. Future C03 must recheck current SOURCE/TARGET SHA and Owner before issue.

### R5 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_tactic_value` @ L191 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**FUTURE TARGET (absent on A and integration):** `libs/reporting/quant_tactic_value_projection.py::_tactic_value`. **DESIGN ONLY, DO NOT IMPLEMENT until a fresh C03 order.**
```python
def _tactic_value(value: Any) -> str:
    return str(value or "").strip()
```
**Future targeted normal fixture:** '  A ' -> 'A'; None -> ''. **Safety/seam:** pure text normalization. Future C03 must recheck current SOURCE/TARGET SHA and Owner before issue.

### R6 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_tactic_mismatches` @ L215 | CURRENT_BLOB `95581e3572bd3be06e6c3b93638b22091a968056`
**FUTURE TARGET (absent on A and integration):** `libs/reporting/quant_tactic_mismatches_projection.py::_tactic_mismatches`. **DESIGN ONLY, DO NOT IMPLEMENT until a fresh C03 order.**
```python
def _tactic_mismatches(sources: List[tuple[str, str]], tactic_id: str) -> List[Dict[str, str]]:
    return [
        {"source": source, "tactic_id": value}
        for source, value in sources
        if tactic_id and value != tactic_id and source != "exit_quant_decision"
    ]
```
**Future targeted normal fixture:** ([('entry','B'),('exit_quant_decision','C')],'A') -> [{'source':'entry','tactic_id':'B'}]; empty tactic_id -> []. **Safety/seam:** pure diagnostic list, no policy effect. Future C03 must recheck current SOURCE/TARGET SHA and Owner before issue.

**NO NEW RF DONE:** C03 only supplies work; G1/G2/G3 remain Actor/C04/C05 evidence. Old PASS is REMOTE_DONE, not reusable as new work.
