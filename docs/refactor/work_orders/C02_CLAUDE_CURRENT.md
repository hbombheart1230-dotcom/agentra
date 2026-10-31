# C02 — Claude A | A-20261031-17 | FAST-3 eight NEW verified SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_ISSUANCE:** `420b885efbff732bad9730202fa23f3afab926a2` · **OLD_ORDER_BLOB:** `b0f10269bcf72c7003e292c380cf7aa99a2d35d7` · **A_REMOTE_HEAD_AT_DESIGN:** `358a1531c18a542d6d4df05199ea7d52d1fecf13` · **SOURCE_BLOB:** `4dcdc03719ae59803ab7b63a6bbb37c935983174`. #11 `6540535600` and remote A HEAD confirm prior A-20261031-16 A1–A8 REMOTE_DONE, normal 9/9 exit0 and new owner/test blobs. Prior completed items never reused. RF-035 owns `libs/reporting/profitability_recovery_day1.py` exclusively; integration source blob identical. A1–A6 promote previous verified reserves after recheck; A7/A8 separately inspected. All five new TARGET modules checked ABSENT 404 on A and integration.

**Single-document execution contract:** Read this C01/C02 only, pin order blob, canonical HEAD and actor HEAD; do not read D00/RF/queue/C03/handoff or self-select. Move the entire exact SOURCE computation BODY to the named new actor-only TARGET; SOURCE keeps original signature/defaults/annotations as thin delegation wrapper, TARGET never imports SOURCE. For dynamic globals (including imports, constants and monkeypatchable helpers), TARGET accepts keyword-only `facade` and uses `facade.NAME` at call time; SOURCE passes `sys.modules[__name__]` or equivalent. Preserve byte output, identity, ordering, exceptions and caller patch seams; use golden original vs wrapper/Owner, thin-wrapper AST and post-import patch tests. Pure helpers may omit facade. Never count KEEP, same-SHA PASS, or pre-moved code as new BODY MOVE. Complete every safe item even if one is blocked; an already-started order is not retroactively cancelled.

**Safety:** fake/in-memory/TemporaryDirectory and patched environment only. No actual reports/main(), real account/order/Broker/Guard/Step5C/UEF/RunLab, network, operational state, deployment, frozen oracle, CI workflow, force push, other actor branch or docs/RF/STATUS/C04/C05. One normal targeted unittest/pytest exit0 on changed scope is G2; no blanket -O/full peer/hosted CI. Actor commits/pushes code/test on own branch only (normal push or approved exact-tree expected-head lease), re-fetches remote HEAD/source/target/test blobs. HTTPS auth failure is PUSH_BLOCKED only; continue other safe items. C04 integration and C05 G1/G2/G3/DONE separate.

**Allowed code/test:** `libs/reporting/profitability_recovery_day1.py`, explicitly named new A target modules and `tests/test_p15_rf035_17h_projection_owners.py` only.

## A1 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_execution_missing_fields` @ L60 | SOURCE_BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174`
**TARGET:** `libs/reporting/profitability_recovery_evidence_projection.py::_execution_missing_fields` (NEW A-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _execution_missing_fields(execution_details: Dict[str, Any]) -> List[str]:
    execution_details = execution_details if isinstance(execution_details, dict) else {}
    missing: List[str] = []
    for key in REQUIRED_EXECUTION_FIELDS:
        if key not in execution_details or execution_details.get(key) in (None, "", []):
            missing.append(str(key))
    return missing
```
**Wrapper/patch:** REQUIRED_EXECUTION_FIELDS resolved through SOURCE facade at call time; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_a1_execution_missing_fields` in `tests/test_p15_rf035_17h_projection_owners.py`. **Input→expected:** {} → list(REQUIRED_EXECUTION_FIELDS); all fields supplied → []. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_evidence_projection.py` and after all eight `python -m unittest tests/test_p15_rf035_17h_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A source/Owner/test, re-fetch SHA/blob; if blocked continue A2.

## A2 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_bundle_artifacts` @ L69 | SOURCE_BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174`
**TARGET:** `libs/reporting/profitability_recovery_evidence_projection.py::_bundle_artifacts` (NEW A-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _bundle_artifacts(lifecycle_bundle: Dict[str, Any]) -> Dict[str, Any]:
    artifacts = lifecycle_bundle.get("artifacts")
    return artifacts if isinstance(artifacts, dict) else {}
```
**Wrapper/patch:** pure, preserve dict identity; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_a2_bundle_artifacts` in `tests/test_p15_rf035_17h_projection_owners.py`. **Input→expected:** {'artifacts':{'x':1}} → same dict object; list → {}. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_evidence_projection.py` and after all eight `python -m unittest tests/test_p15_rf035_17h_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A source/Owner/test, re-fetch SHA/blob; if blocked continue A3.

## A3 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_section_provenance` @ L74 | SOURCE_BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174`
**TARGET:** `libs/reporting/profitability_recovery_evidence_projection.py::_section_provenance` (NEW A-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _section_provenance(lifecycle_bundle: Dict[str, Any]) -> Dict[str, Any]:
    section_provenance = lifecycle_bundle.get("section_provenance")
    return section_provenance if isinstance(section_provenance, dict) else {}
```
**Wrapper/patch:** pure, preserve dict identity; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_a3_section_provenance` in `tests/test_p15_rf035_17h_projection_owners.py`. **Input→expected:** {'section_provenance':{'x':1}} → same dict object; missing → {}. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_evidence_projection.py` and after all eight `python -m unittest tests/test_p15_rf035_17h_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A source/Owner/test, re-fetch SHA/blob; if blocked continue A4.

## A4 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_is_closed_trade_report_generation_regression` @ L270 | SOURCE_BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174`
**TARGET:** `libs/reporting/profitability_recovery_status_projection.py::_is_closed_trade_report_generation_regression` (NEW A-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _is_closed_trade_report_generation_regression(
    *, closed_trade: bool, ai_trade_report_llm_exists: bool, ai_status: str
) -> bool:
    if not closed_trade:
        return False
    if not ai_trade_report_llm_exists:
        return True
    normalized = str(ai_status or "").strip().lower()
    if not normalized:
        return False
    return normalized in {"failed", "error", "skipped"}
```
**Wrapper/patch:** pure, preserve failed/error/skipped and short circuit; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_a4_is_closed_trade_report_generation_regression` in `tests/test_p15_rf035_17h_projection_owners.py`. **Input→expected:** closed_trade=True,llm_exists=False → True; closed_trade=False → False. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_status_projection.py` and after all eight `python -m unittest tests/test_p15_rf035_17h_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A source/Owner/test, re-fetch SHA/blob; if blocked continue A5.

## A5 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_top_recurring_weakness` @ L364 | SOURCE_BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174`
**TARGET:** `libs/reporting/profitability_recovery_weakness_projection.py::_top_recurring_weakness` (NEW A-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _top_recurring_weakness(rows: Iterable[Dict[str, Any]]) -> str:
    counter: Counter[str] = Counter()
    for row in rows:
        if bool(row.get("closed_trade_report_generation_regression")):
            counter["closed_trade_report_generation_regression"] += 1
        if bool(row.get("closed_trade_decision_only_misclassification")):
            counter["closed_trade_decision_only_misclassification"] += 1
        if bool(row.get("holding_evidence_thin")):
            counter["holding_evidence_thin"] += 1
        if bool(row.get("same_day_linkage_missing")):
            counter["same_day_linkage_missing"] += 1
        if int(row.get("execution_missing_fields_count") or 0) > 0:
            counter["execution_fields_missing"] += 1
    if not counter:
        return "none"
    return str(counter.most_common(1)[0][0])
```
**Wrapper/patch:** Counter through SOURCE facade at call time, preserve tie order; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_a5_top_recurring_weakness` in `tests/test_p15_rf035_17h_projection_owners.py`. **Input→expected:** [] → 'none'; [{'same_day_linkage_missing':True}] → 'same_day_linkage_missing'. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_weakness_projection.py` and after all eight `python -m unittest tests/test_p15_rf035_17h_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A source/Owner/test, re-fetch SHA/blob; if blocked continue A6.

## A6 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_resolve_ai_trade_report_status` @ L250 | SOURCE_BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174`
**TARGET:** `libs/reporting/profitability_recovery_status_projection.py::_resolve_ai_trade_report_status` (NEW A-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _resolve_ai_trade_report_status(
    lifecycle_bundle: Dict[str, Any],
    ai_component: Dict[str, Any],
    ai_trade_report_llm_exists: bool,
) -> str:
    diagnostics = lifecycle_bundle.get("ai_report_diagnostics")
    diagnostics = diagnostics if isinstance(diagnostics, dict) else {}
    for candidate in (
        ai_component.get("status"),
        diagnostics.get("ai_trade_report_status"),
        lifecycle_bundle.get("ai_trade_report_status"),
    ):
        value = str(candidate or "").strip().lower()
        if value:
            return value
    if ai_trade_report_llm_exists:
        return "ok"
    return ""
```
**Wrapper/patch:** pure, preserve status precedence; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_a6_resolve_ai_trade_report_status` in `tests/test_p15_rf035_17h_projection_owners.py`. **Input→expected:** {}, {}, True → 'ok'; {'status':'FAILED'}, {}, False → 'failed'. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_status_projection.py` and after all eight `python -m unittest tests/test_p15_rf035_17h_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A source/Owner/test, re-fetch SHA/blob; if blocked continue A7.

## A7 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_read_json` @ L23 | SOURCE_BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174`
**TARGET:** `libs/reporting/profitability_recovery_io_projection.py::_read_json` (NEW A-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}
```
**Wrapper/patch:** json via SOURCE facade at call time; temp read-only; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_a7_read_json` in `tests/test_p15_rf035_17h_projection_owners.py`. **Input→expected:** missing temp file → {}; temp JSON object → dict; malformed → {}. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_io_projection.py` and after all eight `python -m unittest tests/test_p15_rf035_17h_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A source/Owner/test, re-fetch SHA/blob; if blocked continue A8.

## A8 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_artifact_path` @ L40 | SOURCE_BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174`
**TARGET:** `libs/reporting/profitability_recovery_artifact_projection.py::_artifact_path` (NEW A-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _artifact_path(trade_dir: Path, *candidates: str) -> Path:
    for raw in candidates:
        candidate = trade_dir / raw
        if candidate.exists():
            return candidate
    return trade_dir / candidates[0]
```
**Wrapper/patch:** Path.exists read-only, preserve first candidate and IndexError; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_a8_artifact_path` in `tests/test_p15_rf035_17h_projection_owners.py`. **Input→expected:** temp b.json exists, ('a.json','b.json') → b.json; neither exists → a.json. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile libs/reporting/profitability_recovery_day1.py libs/reporting/profitability_recovery_artifact_projection.py` and after all eight `python -m unittest tests/test_p15_rf035_17h_projection_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push A source/Owner/test, re-fetch SHA/blob; if blocked continue Ahandoff.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY

### R1 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::iter_trade_dirs` @ L33 | BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174` → TARGET `libs/reporting/profitability_recovery_trade_dirs_projection.py::iter_trade_dirs` (404 actor/integration)
```python
def iter_trade_dirs(reports_root: Path, day: str) -> List[Path]:
    day_root = Path(reports_root) / "trades" / str(day)
    if not day_root.exists():
        return []
    return sorted(_iter_trade_dirs(day_root))
```
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** empty temp trade day → []. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

### R2 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_read_hold_payload` @ L79 | BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174` → TARGET `libs/reporting/profitability_recovery_hold_projection.py::_read_hold_payload` (404 actor/integration)
```python
def _read_hold_payload(trade_dir: Path) -> Dict[str, Any]:
    return _read_json(trade_dir / "hold.json")
```
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** temp trade dir without hold.json → {}. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

### R3 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::_resolve_same_day_linkage` @ L83 | BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174` → TARGET `libs/reporting/profitability_recovery_linkage_projection.py::_resolve_same_day_linkage` (404 actor/integration)
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
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** linked lifecycle fixture → linked dict. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

### R4 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::iter_trade_diagnostic_rows` @ L360 | BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174` → TARGET `libs/reporting/profitability_recovery_row_iteration_projection.py::iter_trade_diagnostic_rows` (404 actor/integration)
```python
def iter_trade_diagnostic_rows(reports_root: Path, day: str) -> List[Dict[str, Any]]:
    return [read_trade_diagnostic_row(trade_dir) for trade_dir in iter_trade_dirs(reports_root, day)]
```
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** empty temp trade day → []. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

### R5 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::audit_profitability_recovery_day` @ L382 | BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174` → TARGET `libs/reporting/profitability_recovery_audit_projection.py::audit_profitability_recovery_day` (404 actor/integration)
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
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** empty temp trade day → trade_count=0, top weakness='none'. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

### R6 | RF-035 | SOURCE `libs/reporting/profitability_recovery_day1.py::build_daily_profitability_scorecard` @ L405 | BLOB=`4dcdc03719ae59803ab7b63a6bbb37c935983174` → TARGET `libs/reporting/profitability_recovery_scorecard_projection.py::build_daily_profitability_scorecard` (404 actor/integration)
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
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** empty temp trade day → total_trades=0. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

## REPORT / PUSH

#11: `ORDER_ID=A-20261031-17 | CANONICAL_HEAD | ORDER_BLOB | A_REMOTE_BEFORE→AFTER | A1..A8 ITEM_STATUS | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | MOVED_FUNCTIONS | SOURCE_LOC_BEFORE_AFTER | FIRST_BLOCKER | NEXT_SAFE_ITEM | PUSH_REMOTE_SHA/PUSH_BLOCKED | START_KST/END_KST/ELAPSED_MIN`. Times measured only. C03 document commit is not code G1/G2/G3 or RF_DONE. RunLab exit255/RUN_SOURCE_SHA UNKNOWN operating SAFETY_HOLD.
