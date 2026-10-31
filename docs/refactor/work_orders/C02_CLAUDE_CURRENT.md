# C02 — Claude A | A-20261031-18 | FAST-3 eight NEW verified SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_ISSUANCE:** `86bf6e034a8dbfaaca19cb744f74ad136e4b677a` · **OLD_ORDER_BLOB:** `3f53b86981d0db59fa7e5f22afece54997354cc0` · **A_REMOTE_HEAD_AT_DESIGN:** `ea6c23bb2f31aa3daa75a74f4291c32d876f3721` · **SOURCE_BLOB:** `de0194163fc2602881feaebd8cd125fb6f204b13`.
#11 `6541098810` and remote A HEAD confirm A-20261031-17 A1–A8 REMOTE_DONE, normal 8/8 exit0, remote source/Owner/test SHA. Prior completed items never reused. RF-035 exclusively owns `libs/reporting/profitability_recovery_day1.py` (RF-035 Owner table checked). A1–A6 promote earlier reserves after exact fresh BODY comparison; A7–A8 are separately inspected read-only diagnostic calculations. All eight new TARGET modules verified absent 404 on A and integration before issuance.

**Single-document contract:** Read only this C02, pin CANONICAL_HEAD/ORDER_BLOB/A_REMOTE_HEAD. Do not read D00/RF/queue/C03/handoff or self-select. Move entire exact computation BODY into named new A Owner, SOURCE thin signature-preserving wrapper; TARGET must not import SOURCE. Use call-time facade for globals, preserve caller/monkeypatch seams, return identity, errors, output ordering. No duplicate BODY/KEEP-only or same-SHA rechecks counted as MOVE. Execute A1–A8 independently; blocked item never cancels other safe items, and a new order does not retroactively invalidate a started order.

**Safety:** diagnostic read-only fake/temp/in-memory only. Do not invoke real report roots or `main()`, network, broker/order/Guard/Step5C/UEF, RunLab, operational DB/state, deployments, frozen oracle/CI workflow, or modify protected effect. A source/test branch only, no docs/RF/STATUS/C04/C05 or force push. Normal scoped unittest/pytest exit0 is G2, no blanket -O/full peer/hosted CI. HTTPS auth failure is PUSH_BLOCKED only; continue other safe work, use only approved normal/exact-tree expected-head delivery. Re-fetch remote SHA and source/Owner/test blobs. C04 G3 integration and C05 RF DONE separate.

**Allowed code/test:** `libs/reporting/profitability_recovery_day1.py`, the eight exact A TARGET paths below, and `tests/test_p15_rf035_18h_reporting_projection_owners.py` only.

## A1 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::iter_trade_dirs` @ L33 | SOURCE_BLOB=`de0194163fc2602881feaebd8cd125fb6f204b13`
**TARGET:** `libs/reporting/profitability_recovery_trade_dirs_projection.py::iter_trade_dirs` (NEW A-exclusive, verified absent on A and integration).
**Exact computation BODY to MOVE (not test-only/KEEP):**
```python
def iter_trade_dirs(reports_root: Path, day: str) -> List[Path]:
    day_root = Path(reports_root) / "trades" / str(day)
    if not day_root.exists():
        return []
    return sorted(_iter_trade_dirs(day_root))
```
**Wrapper/monkeypatch/callers:** Leave original signature/defaults/annotations in SOURCE as thin delegation. TARGET never imports SOURCE. _iter_trade_dirs and Path via facade; sorted deterministic order. For SOURCE global lookups, TARGET accepts keyword-only `facade` and accesses `facade.NAME` at invocation, SOURCE passes `sys.modules[__name__]`. No duplicate BODY, preserve return identity, exceptions, byte output, call-time patch seams.
**Normal targeted test:** `test_a1_iter_trade_dirs` in `tests/test_p15_rf035_18h_reporting_projection_owners.py`. Input→expected: empty temp root/day → [] ; with two mock trade folders → deterministic sorted paths. Compare original golden vs facade wrapper and Owner, include negative/exception parity, post-import monkeypatch and AST thin-wrapper. Temp/memory only; no real reports. After all eight run `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_*_projection.py` and `python -m unittest tests/test_p15_rf035_18h_reporting_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A code/test, re-fetch remote HEAD/source/Owner/test blob. If blocked record and **continue A2**.

## A2 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_read_hold_payload` @ L68 | SOURCE_BLOB=`de0194163fc2602881feaebd8cd125fb6f204b13`
**TARGET:** `libs/reporting/profitability_recovery_hold_projection.py::_read_hold_payload` (NEW A-exclusive, verified absent on A and integration).
**Exact computation BODY to MOVE (not test-only/KEEP):**
```python
def _read_hold_payload(trade_dir: Path) -> Dict[str, Any]:
    return _read_json(trade_dir / "hold.json")
```
**Wrapper/monkeypatch/callers:** Leave original signature/defaults/annotations in SOURCE as thin delegation. TARGET never imports SOURCE. _read_json via facade; preserve direct helper patch seam. For SOURCE global lookups, TARGET accepts keyword-only `facade` and accesses `facade.NAME` at invocation, SOURCE passes `sys.modules[__name__]`. No duplicate BODY, preserve return identity, exceptions, byte output, call-time patch seams.
**Normal targeted test:** `test_a2_read_hold_payload` in `tests/test_p15_rf035_18h_reporting_projection_owners.py`. Input→expected: temp trade_dir without hold.json → {}; temp hold.json object → exact dict. Compare original golden vs facade wrapper and Owner, include negative/exception parity, post-import monkeypatch and AST thin-wrapper. Temp/memory only; no real reports. After all eight run `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_*_projection.py` and `python -m unittest tests/test_p15_rf035_18h_reporting_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A code/test, re-fetch remote HEAD/source/Owner/test blob. If blocked record and **continue A3**.

## A3 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_resolve_same_day_linkage` @ L72 | SOURCE_BLOB=`de0194163fc2602881feaebd8cd125fb6f204b13`
**TARGET:** `libs/reporting/profitability_recovery_linkage_projection.py::_resolve_same_day_linkage` (NEW A-exclusive, verified absent on A and integration).
**Exact computation BODY to MOVE (not test-only/KEEP):**
```python
def _resolve_same_day_linkage(lifecycle_bundle: Dict[str, Any], trade_dir: Path) -> Dict[str, Any]:
    linkage = lifecycle_bundle.get("same_day_reporter_linkage")
    if isinstance(linkage, dict) and _linkage_surface_present(linkage):
        return dict(linkage)

    artifacts = _bundle_artifacts(lifecycle_bundle)
    section_provenance = _section_provenance(lifecycle_bundle)
    candidate_paths = [
        artifacts.get("reporter_analysis_json"),
        artifacts.get("reporter_analysis_md"),
        ((section_provenance.get("reporter_status_human") or {}) if isinstance(section_provenance.get("reporter_status_human"), dict) else {}).get("artifact_path"),
    ]
    for raw in candidate_paths:
        if not raw:
            continue
        candidate = Path(str(raw))
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        if candidate.exists():
            return {
                "status": "linked_day_fallback",
                "linkage_reason": "same_day_reporter_artifact_present",
                "artifact_path": str(candidate),
            }
    return linkage if isinstance(linkage, dict) else {}
```
**Wrapper/monkeypatch/callers:** Leave original signature/defaults/annotations in SOURCE as thin delegation. TARGET never imports SOURCE. _linkage_surface_present/_bundle_artifacts/_section_provenance/Path via facade; absolute temp-only artifact probes. For SOURCE global lookups, TARGET accepts keyword-only `facade` and accesses `facade.NAME` at invocation, SOURCE passes `sys.modules[__name__]`. No duplicate BODY, preserve return identity, exceptions, byte output, call-time patch seams.
**Normal targeted test:** `test_a3_resolve_same_day_linkage` in `tests/test_p15_rf035_18h_reporting_projection_owners.py`. Input→expected: lifecycle with same_day_reporter_linkage.status='linked' and a visible linkage key → original dict; missing artifacts → {}. Compare original golden vs facade wrapper and Owner, include negative/exception parity, post-import monkeypatch and AST thin-wrapper. Temp/memory only; no real reports. After all eight run `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_*_projection.py` and `python -m unittest tests/test_p15_rf035_18h_reporting_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A code/test, re-fetch remote HEAD/source/Owner/test blob. If blocked record and **continue A4**.

## A4 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::iter_trade_diagnostic_rows` @ L330 | SOURCE_BLOB=`de0194163fc2602881feaebd8cd125fb6f204b13`
**TARGET:** `libs/reporting/profitability_recovery_row_iteration_projection.py::iter_trade_diagnostic_rows` (NEW A-exclusive, verified absent on A and integration).
**Exact computation BODY to MOVE (not test-only/KEEP):**
```python
def iter_trade_diagnostic_rows(reports_root: Path, day: str) -> List[Dict[str, Any]]:
    return [read_trade_diagnostic_row(trade_dir) for trade_dir in iter_trade_dirs(reports_root, day)]
```
**Wrapper/monkeypatch/callers:** Leave original signature/defaults/annotations in SOURCE as thin delegation. TARGET never imports SOURCE. read_trade_diagnostic_row/iter_trade_dirs via facade, preserve call-time monkeypatch. For SOURCE global lookups, TARGET accepts keyword-only `facade` and accesses `facade.NAME` at invocation, SOURCE passes `sys.modules[__name__]`. No duplicate BODY, preserve return identity, exceptions, byte output, call-time patch seams.
**Normal targeted test:** `test_a4_iter_trade_diagnostic_rows` in `tests/test_p15_rf035_18h_reporting_projection_owners.py`. Input→expected: empty temp trade day → [] ; one mock trade folder → one diagnostic row. Compare original golden vs facade wrapper and Owner, include negative/exception parity, post-import monkeypatch and AST thin-wrapper. Temp/memory only; no real reports. After all eight run `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_*_projection.py` and `python -m unittest tests/test_p15_rf035_18h_reporting_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A code/test, re-fetch remote HEAD/source/Owner/test blob. If blocked record and **continue A5**.

## A5 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::audit_profitability_recovery_day` @ L338 | SOURCE_BLOB=`de0194163fc2602881feaebd8cd125fb6f204b13`
**TARGET:** `libs/reporting/profitability_recovery_audit_projection.py::audit_profitability_recovery_day` (NEW A-exclusive, verified absent on A and integration).
**Exact computation BODY to MOVE (not test-only/KEEP):**
```python
def audit_profitability_recovery_day(reports_root: Path, day: str) -> Dict[str, Any]:
    rows = iter_trade_diagnostic_rows(reports_root, day)
    return {
        "schema_version": "profitability_recovery_day1_audit.v1",
        "day": str(day),
        "trade_count": len(rows),
        "closed_trade_count": sum(1 for row in rows if bool(row.get("closed_trade"))),
        "closed_trade_report_generation_regression_count": sum(
            1 for row in rows if bool(row.get("closed_trade_report_generation_regression"))
        ),
        "closed_trade_decision_only_misclassification_count": sum(
            1 for row in rows if bool(row.get("closed_trade_decision_only_misclassification"))
        ),
        "holding_evidence_thin_count": sum(1 for row in rows if bool(row.get("holding_evidence_thin"))),
        "same_day_linkage_missing_count": sum(1 for row in rows if bool(row.get("same_day_linkage_missing"))),
        "execution_fields_missing_count": sum(
            int(row.get("execution_missing_fields_count") or 0) for row in rows
        ),
        "top_recurring_diagnostic_weakness": _top_recurring_weakness(rows),
        "rows": rows,
    }
```
**Wrapper/monkeypatch/callers:** Leave original signature/defaults/annotations in SOURCE as thin delegation. TARGET never imports SOURCE. iter_trade_diagnostic_rows/_top_recurring_weakness via facade, dict keys and sum semantics exact. For SOURCE global lookups, TARGET accepts keyword-only `facade` and accesses `facade.NAME` at invocation, SOURCE passes `sys.modules[__name__]`. No duplicate BODY, preserve return identity, exceptions, byte output, call-time patch seams.
**Normal targeted test:** `test_a5_audit_profitability_recovery_day` in `tests/test_p15_rf035_18h_reporting_projection_owners.py`. Input→expected: empty temp root/day → trade_count=0, top_recurring_diagnostic_weakness='none'. Compare original golden vs facade wrapper and Owner, include negative/exception parity, post-import monkeypatch and AST thin-wrapper. Temp/memory only; no real reports. After all eight run `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_*_projection.py` and `python -m unittest tests/test_p15_rf035_18h_reporting_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A code/test, re-fetch remote HEAD/source/Owner/test blob. If blocked record and **continue A6**.

## A6 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::build_daily_profitability_scorecard` @ L361 | SOURCE_BLOB=`de0194163fc2602881feaebd8cd125fb6f204b13`
**TARGET:** `libs/reporting/profitability_recovery_scorecard_projection.py::build_daily_profitability_scorecard` (NEW A-exclusive, verified absent on A and integration).
**Exact computation BODY to MOVE (not test-only/KEEP):**
```python
def build_daily_profitability_scorecard(reports_root: Path, day: str) -> Dict[str, Any]:
    audit = audit_profitability_recovery_day(reports_root, day)
    rows = list(audit.get("rows") or [])
    return {
        "schema_version": "daily_profitability_scorecard.v1",
        "day": str(day),
        "total_trades": int(audit.get("trade_count") or 0),
        "closed_trades": int(audit.get("closed_trade_count") or 0),
        "loss_trades": sum(1 for row in rows if bool(row.get("loss_trade"))),
        "lifecycle_linkage_missing_count": int(audit.get("same_day_linkage_missing_count") or 0),
        "holding_evidence_thin_count": int(audit.get("holding_evidence_thin_count") or 0),
        "execution_fields_missing_count": int(audit.get("execution_fields_missing_count") or 0),
        "closed_trade_report_generation_regression_count": int(
            audit.get("closed_trade_report_generation_regression_count") or 0
        ),
        "closed_trade_decision_only_misclassification_count": int(
            audit.get("closed_trade_decision_only_misclassification_count") or 0
        ),
        "top_recurring_diagnostic_weakness": str(
            audit.get("top_recurring_diagnostic_weakness") or "none"
        ),
        "rows": rows,
    }
```
**Wrapper/monkeypatch/callers:** Leave original signature/defaults/annotations in SOURCE as thin delegation. TARGET never imports SOURCE. audit_profitability_recovery_day via facade, preserve row identity and schema keys. For SOURCE global lookups, TARGET accepts keyword-only `facade` and accesses `facade.NAME` at invocation, SOURCE passes `sys.modules[__name__]`. No duplicate BODY, preserve return identity, exceptions, byte output, call-time patch seams.
**Normal targeted test:** `test_a6_build_daily_profitability_scorecard` in `tests/test_p15_rf035_18h_reporting_projection_owners.py`. Input→expected: empty temp root/day → total_trades=0, closed_trades=0, loss_trades=0. Compare original golden vs facade wrapper and Owner, include negative/exception parity, post-import monkeypatch and AST thin-wrapper. Temp/memory only; no real reports. After all eight run `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_*_projection.py` and `python -m unittest tests/test_p15_rf035_18h_reporting_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A code/test, re-fetch remote HEAD/source/Owner/test blob. If blocked record and **continue A7**.

## A7 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_resolve_execution_details` @ L171 | SOURCE_BLOB=`de0194163fc2602881feaebd8cd125fb6f204b13`
**TARGET:** `libs/reporting/profitability_recovery_execution_projection.py::_resolve_execution_details` (NEW A-exclusive, verified absent on A and integration).
**Exact computation BODY to MOVE (not test-only/KEEP):**
```python
def _resolve_execution_details(lifecycle_bundle: Dict[str, Any], trade_dir: Path) -> Dict[str, Any]:
    explicit = lifecycle_bundle.get("execution_details")
    if isinstance(explicit, dict) and explicit:
        return dict(explicit)

    execution = lifecycle_bundle.get("execution")
    execution = execution if isinstance(execution, dict) else {}
    story_contract = lifecycle_bundle.get("story_contract")
    story_contract = story_contract if isinstance(story_contract, dict) else {}
    entry = _read_json(trade_dir / "entry.json")
    exit_payload = _read_json(trade_dir / "exit.json")

    order_id = (
        execution.get("ord_no")
        or ((entry.get("execution_details") or {}) if isinstance(entry.get("execution_details"), dict) else {}).get("order_id")
        or ((exit_payload.get("execution_details") or {}) if isinstance(exit_payload.get("execution_details"), dict) else {}).get("order_id")
        or None
    )

    if order_id in (None, ""):
        for ctx in (lifecycle_bundle.get("exit_execution_details", {}), lifecycle_bundle.get("entry_execution_details", {})):
            if ctx.get("order_id") not in (None, ""):
                order_id = ctx.get("order_id")
                break

    execution_mode_label = str(story_contract.get("execution_mode_label") or "").strip().lower()
    execution_mode = None
    broker_env = None
    if "simulation" in execution_mode_label or "mock" in execution_mode_label:
        execution_mode = "simulation"
        broker_env = "mock"
    elif execution_mode_label:
        execution_mode = execution_mode_label

    filled_qty = execution.get("qty")
    avg_price = (
        execution.get("avg_price")
        or execution.get("price")
        or entry.get("price")
        or exit_payload.get("price")
        or None
    )
    if avg_price in (None, ""):
        for ctx in (lifecycle_bundle.get("exit_execution_details", {}), lifecycle_bundle.get("entry_execution_details", {})):
            if ctx.get("avg_price") not in (None, ""):
                avg_price = ctx.get("avg_price")
                break
    if avg_price in (None, ""):
        avg_price = (
            _safe_float(lifecycle_bundle.get("exit", {}).get("price")) or
            _safe_float(lifecycle_bundle.get("entry", {}).get("price")) or
            _safe_float(lifecycle_bundle.get("monitor_snapshot", {}).get("average_price"))
        )

    order_status = execution.get("status")
    if order_status in (None, "") and str(execution.get("action") or "").strip():
        order_status = "filled"

    return {
        "order_status": order_status if order_status not in ("", []) else None,
        "order_id": order_id if order_id not in ("", []) else None,
        "execution_mode": execution_mode,
        "broker_env": broker_env,
        "filled_qty": filled_qty if filled_qty not in ("", []) else None,
        "avg_price": avg_price if avg_price not in ("", []) else None,
    }
```
**Wrapper/monkeypatch/callers:** Leave original signature/defaults/annotations in SOURCE as thin delegation. TARGET never imports SOURCE. _read_json/_safe_float via facade, only temp fixture paths; preserve fallback precedence and exception semantics. For SOURCE global lookups, TARGET accepts keyword-only `facade` and accesses `facade.NAME` at invocation, SOURCE passes `sys.modules[__name__]`. No duplicate BODY, preserve return identity, exceptions, byte output, call-time patch seams.
**Normal targeted test:** `test_a7_resolve_execution_details` in `tests/test_p15_rf035_18h_reporting_projection_owners.py`. Input→expected: {'execution_details':{'order_id':'X'}} with temp dir → {'order_id':'X'}; empty lifecycle/temp → same original six-key missing/None structure. Compare original golden vs facade wrapper and Owner, include negative/exception parity, post-import monkeypatch and AST thin-wrapper. Temp/memory only; no real reports. After all eight run `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_*_projection.py` and `python -m unittest tests/test_p15_rf035_18h_reporting_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A code/test, re-fetch remote HEAD/source/Owner/test blob. If blocked record and **continue A8**.

## A8 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::read_trade_diagnostic_row` @ L253 | SOURCE_BLOB=`de0194163fc2602881feaebd8cd125fb6f204b13`
**TARGET:** `libs/reporting/profitability_recovery_diagnostic_row_projection.py::read_trade_diagnostic_row` (NEW A-exclusive, verified absent on A and integration).
**Exact computation BODY to MOVE (not test-only/KEEP):**
```python
def read_trade_diagnostic_row(trade_dir: Path) -> Dict[str, Any]:
    lifecycle_path = _artifact_path(
        trade_dir,
        "lifecycle_bundle.json",
        "lifecycle/trade_lifecycle.json",
        "trade_lifecycle.json",
    )
    generation_state_path = trade_dir / "reports" / "report_generation_state.json"
    ai_trade_report_llm_path = _artifact_path(
        trade_dir,
        "reports/ai_trade_report_llm_response.json",
        "ai_trade_report/ai_trade_report_llm_response.json",
    )
    lifecycle_bundle = _read_json(lifecycle_path)
    generation_state = _read_json(generation_state_path)
    components = generation_state.get("components") if isinstance(generation_state.get("components"), dict) else {}
    ai_component = components.get("ai_trade_report") if isinstance(components.get("ai_trade_report"), dict) else {}
    ai_trade_report_llm_exists = ai_trade_report_llm_path.exists()
    same_day_linkage = _resolve_same_day_linkage(lifecycle_bundle, trade_dir)
    holding_evidence = _resolve_holding_evidence(lifecycle_bundle, trade_dir)
    holding_phase_summary = str(holding_evidence.get("holding_phase_summary") or "").strip()
    hold_events_count = int(holding_evidence.get("hold_events_count") or 0)
    monitor_context_snapshots = [
        dict(row)
        for row in list(holding_evidence.get("monitor_context_snapshots") or [])
        if isinstance(row, dict)
    ]
    execution_details = _resolve_execution_details(lifecycle_bundle, trade_dir)
    closed_trade = _is_closed_trade(lifecycle_bundle)
    story_type = str(
        lifecycle_bundle.get("story_type")
        or ((lifecycle_bundle.get("story_contract") or {}) if isinstance(lifecycle_bundle.get("story_contract"), dict) else {}).get("story_type")
        or ""
    ).strip().lower()
    ai_status = _resolve_ai_trade_report_status(lifecycle_bundle, ai_component, ai_trade_report_llm_exists)
    return_pct = _safe_float(((lifecycle_bundle.get("trade_outcome") or {}) if isinstance(lifecycle_bundle.get("trade_outcome"), dict) else {}).get("return_pct"))
    same_day_linkage_missing = not _linkage_surface_present(same_day_linkage)
    holding_evidence_thin = bool(
        lifecycle_bundle.get("hold_evidence_thin")
        or hold_events_count <= 0
        or (not monitor_context_snapshots and not holding_phase_summary)
    )
    execution_missing_fields = _execution_missing_fields(execution_details)
    row = {
        "trade_id": str(lifecycle_bundle.get("trade_id") or trade_dir.name),
        "day": str(lifecycle_bundle.get("day") or trade_dir.parent.name),
        "symbol": str(lifecycle_bundle.get("symbol") or ""),
        "story_type": story_type,
        "lifecycle_status": str(lifecycle_bundle.get("trade_lifecycle_status") or lifecycle_bundle.get("status") or ""),
        "closed_trade": closed_trade,
        "loss_trade": bool(return_pct is not None and return_pct < 0),
        "return_pct": return_pct,
        "hold_duration": str(holding_evidence.get("hold_duration") or ""),
        "hold_duration_sec": holding_evidence.get("hold_duration_sec"),
        "holding_evidence_thin": holding_evidence_thin,
        "holding_phase_summary": holding_phase_summary,
        "hold_events_count": hold_events_count,
        "monitor_context_snapshots_count": len(monitor_context_snapshots),
        "same_day_linkage_status": str(same_day_linkage.get("status") or ""),
        "same_day_linkage_reason": str(same_day_linkage.get("linkage_reason") or ""),
        "same_day_linkage_missing": same_day_linkage_missing,
        "execution_fields_missing": execution_missing_fields,
        "execution_missing_fields_count": len(execution_missing_fields),
        "ai_trade_report_llm_response_exists": ai_trade_report_llm_exists,
        "ai_trade_report_status": ai_status,
        "closed_trade_report_generation_regression": _is_closed_trade_report_generation_regression(
            closed_trade=closed_trade,
            ai_trade_report_llm_exists=ai_trade_report_llm_exists,
            ai_status=ai_status,
        ),
        "closed_trade_decision_only_misclassification": bool(closed_trade and story_type == "decision_only"),
        "report_generation_state_path": str(generation_state_path),
        "lifecycle_bundle_path": str(lifecycle_path),
    }
    return row
```
**Wrapper/monkeypatch/callers:** Leave original signature/defaults/annotations in SOURCE as thin delegation. TARGET never imports SOURCE. _artifact_path/_read_json/_resolve_same_day_linkage/_resolve_holding_evidence/_resolve_execution_details/_is_closed_trade/_safe_float/_execution_missing_fields/_resolve_ai_trade_report_status/_linkage_surface_present/_is_closed_trade_report_generation_regression via facade; do not fix unrelated behavior or access real reports. For SOURCE global lookups, TARGET accepts keyword-only `facade` and accesses `facade.NAME` at invocation, SOURCE passes `sys.modules[__name__]`. No duplicate BODY, preserve return identity, exceptions, byte output, call-time patch seams.
**Normal targeted test:** `test_a8_read_trade_diagnostic_row` in `tests/test_p15_rf035_18h_reporting_projection_owners.py`. Input→expected: empty temp trade dir named 'T123' → trade_id='T123', closed_trade=False, missing fields count matches golden. Compare original golden vs facade wrapper and Owner, include negative/exception parity, post-import monkeypatch and AST thin-wrapper. Temp/memory only; no real reports. After all eight run `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_*_projection.py` and `python -m unittest tests/test_p15_rf035_18h_reporting_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A code/test, re-fetch remote HEAD/source/Owner/test blob. If blocked record and **continue Ahandoff**.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY

Six RF-035 pure shadow-diagnostic SOURCE bodies inspected at A/integration blob `c46916f178b600cef3729d65e197e7e971d851cd`; exact six new TARGET paths returned 404 on both A and integration. Distinct from current eight profitability-recovery moves. Do not execute without a new C03 order and fresh blob/target recheck.

### R1 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_bool` @ L32 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd` → TARGET `libs/reporting/quant_shadow_scalar_projection.py::_bool` (404 A/integration, A-exclusive)
```python
def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}
```
**Safety/patch:** pure truth normalization, no side effects; pure fake/in-memory shadow diagnostic only. SOURCE thin wrapper, no duplicate BODY, call-time monkeypatch parity. **Future normal test input→expected:** True→True; 'YES'→True; 'off'→False; original golden/wrapper/Owner and negative/exception parity. **RESERVE_VERIFIED DESIGN ONLY**, C03 fresh HEAD/blob/target recheck before promotion.

### R2 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_iter_days` @ L51 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd` → TARGET `libs/reporting/quant_shadow_day_projection.py::_iter_days` (404 A/integration, A-exclusive)
```python
def _iter_days(start: str, end: str) -> Iterable[str]:
    start_date = date.fromisoformat(str(start)[:10])
    end_date = date.fromisoformat(str(end)[:10])
    current = start_date
    while current <= end_date:
        yield current.isoformat()
        current += timedelta(days=1)
```
**Safety/patch:** date/timedelta via facade, preserve generator laziness and ValueError; pure fake/in-memory shadow diagnostic only. SOURCE thin wrapper, no duplicate BODY, call-time monkeypatch parity. **Future normal test input→expected:** start='2026-10-30',end='2026-10-31'→two ISO days; reversed→empty iterator; original golden/wrapper/Owner and negative/exception parity. **RESERVE_VERIFIED DESIGN ONLY**, C03 fresh HEAD/blob/target recheck before promotion.

### R3 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_top_counter` @ L261 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd` → TARGET `libs/reporting/quant_shadow_counter_projection.py::_top_counter` (404 A/integration, A-exclusive)
```python
def _top_counter(counter: Counter[str], *, limit: int = 8) -> List[Dict[str, Any]]:
    return [
        {"name": name, "count": count}
        for name, count in counter.most_common(limit)
        if name
    ]
```
**Safety/patch:** Counter input, preserve most_common tie order; pure fake/in-memory shadow diagnostic only. SOURCE thin wrapper, no duplicate BODY, call-time monkeypatch parity. **Future normal test input→expected:** Counter({'a':2,'b':1}),limit=1→[{'name':'a','count':2}]; original golden/wrapper/Owner and negative/exception parity. **RESERVE_VERIFIED DESIGN ONLY**, C03 fresh HEAD/blob/target recheck before promotion.

### R4 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_row_blockers` @ L269 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd` → TARGET `libs/reporting/quant_shadow_blocker_projection.py::_row_blockers` (404 A/integration, A-exclusive)
```python
def _row_blockers(row: Mapping[str, Any]) -> List[str]:
    blockers: List[str] = []
    for value in (row.get("blockers"),):
        if isinstance(value, list):
            blockers.extend(_text(item) for item in value if _text(item))
    decision = row.get("entry_quant_decision")
    if isinstance(decision, Mapping):
        value = decision.get("blockers")
        if isinstance(value, list):
            blockers.extend(_text(item) for item in value if _text(item))
    return blockers
```
**Safety/patch:** _text via facade, preserve nested blocker order and duplicates; pure fake/in-memory shadow diagnostic only. SOURCE thin wrapper, no duplicate BODY, call-time monkeypatch parity. **Future normal test input→expected:** {'blockers':['a','']}→['a']; nested entry_quant_decision.blockers preserved; original golden/wrapper/Owner and negative/exception parity. **RESERVE_VERIFIED DESIGN ONLY**, C03 fresh HEAD/blob/target recheck before promotion.

### R5 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_count_reason` @ L393 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd` → TARGET `libs/reporting/quant_shadow_reason_projection.py::_count_reason` (404 A/integration, A-exclusive)
```python
def _count_reason(candidates: Sequence[Mapping[str, Any]], names: set[str]) -> int:
    total = 0
    for row in candidates:
        reason = _text(row.get("reason"))
        primary = _text(row.get("primary_failure_axis"))
        cost_floor = _cost_floor_state(row)
        if reason in names or primary in names or cost_floor in names:
            total += 1
            continue
        blockers = _row_blockers(row)
        if any(blocker in names for blocker in blockers):
            total += 1
    return total
```
**Safety/patch:** _text/_cost_floor_state/_row_blockers via facade, preserve short circuit; pure fake/in-memory shadow diagnostic only. SOURCE thin wrapper, no duplicate BODY, call-time monkeypatch parity. **Future normal test input→expected:** [{'reason':'bad'}],{'bad'}→1; []→0; original golden/wrapper/Owner and negative/exception parity. **RESERVE_VERIFIED DESIGN ONLY**, C03 fresh HEAD/blob/target recheck before promotion.

### R6 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_runner_up_risk_count` @ L408 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd` → TARGET `libs/reporting/quant_shadow_runnerup_projection.py::_runner_up_risk_count` (404 A/integration, A-exclusive)
```python
def _runner_up_risk_count(candidates: Sequence[Mapping[str, Any]]) -> int:
    total = 0
    for row in candidates:
        if _text(row.get("shadow_role")) != "runner_up_evaluated":
            continue
        if _bool(row.get("would_enter")):
            total += 1
            continue
        if _bool(row.get("runner_up_quality_blocked")) or _bool(row.get("weak_fallback_blocked")):
            total += 1
            continue
        reason = _text(row.get("reason"))
        if reason in {"runner_up_quality_gate_failed", "weak_fallback_pullback"}:
            total += 1
    return total
```
**Safety/patch:** _text/_bool via facade, preserve precedence and count; pure fake/in-memory shadow diagnostic only. SOURCE thin wrapper, no duplicate BODY, call-time monkeypatch parity. **Future normal test input→expected:** [{'shadow_role':'runner_up_evaluated','would_enter':True}]→1; other role→0; original golden/wrapper/Owner and negative/exception parity. **RESERVE_VERIFIED DESIGN ONLY**, C03 fresh HEAD/blob/target recheck before promotion.

## REPORT / PUSH
#11: `ORDER_ID=A-20261031-18 | CANONICAL_HEAD | ORDER_BLOB | A_REMOTE_BEFORE→AFTER | A1..A8 ITEM_STATUS | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | MOVED_FUNCTIONS | SOURCE_LOC_BEFORE_AFTER | FIRST_BLOCKER | NEXT_SAFE_ITEM | PUSH_REMOTE_SHA/PUSH_BLOCKED | START_KST/END_KST/ELAPSED_MIN`. Times measured only. C03 document push is not code G1/G2/G3 or RF_DONE. RunLab SOURCE_UNKNOWN/exit255 remains SAFETY_HOLD.
