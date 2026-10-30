# C02 — Agentra P1.5 FAST-3 Claude A | ORDER A-20261031-06 | 8 NEW RF-035 SOURCE BODY MOVEs

**C03 remote preflight (06:xx KST):** integration HEAD `e2a5b4d9595a4a690a69fde3d0374b0484dfb478`; A remote HEAD `6df60c7d8ca1d954a66bb5c207d386a6671f8104`; previous C02 blob `f031d0dfb45bfff445c04379150ec40e216bf64f` ORDER A-05 **8/8 REMOTE_DONE** from #11 comment 6532635190; normal targeted exit0 reported and remote diff confirmed. All eight old A1–A8 have actual Owner modules on A remote, so **DO NOT REPEAT**. New SOURCE `libs/reporting/intraday_trade_reports.py` remote blob `819ce8b895d8fb5adc8b60cf3ba42988d35803cb`, 1,577 LOC, eight non-delegating function bodies confirmed at this SHA. RF-035 exclusive Claude A reporting scope per RF-035 implementation ownership list; B RF-063/RF-065 source paths disjoint. Five new target modules were independently checked 404 on both A and integration before publication. These are new A1–A8, not historical KEEP/test-only.

**Single-file complete order:** At start pin CANONICAL_HEAD, ORDER_FILE_BLOB_SHA, A_REMOTE_SHA, SOURCE_BLOB. Execute **all eight** in order; if a single item is blocked, record reason and proceed to next independent safe item. Read only C02 and the code/test paths named below, NOT D00/RF/queue/C03/old handoffs. Each item moves **the entire exact calculation body** out of SOURCE into the designated new TARGET single owner; retain exact SOURCE signature, annotations, docstring, return/error semantics as thin wrapper. TARGET must never import SOURCE. Use `facade=_r3_sys.modules[__name__]` at wrapper call time; TARGET resolves any SOURCE helper/global through `facade.NAME` (including `json`, `_read_json`, `_execution_truth_surface`, `_utc_now_iso`) and preserves lazy evaluation, call order, monkeypatch behavior and exception parity. Append multiple functions to shared target without overwriting. Do not re-move anything already present on a newer A remote; mark REMOTE_DONE if genuinely moved.

**Safety/G1/G2:** Code/tests ONLY on `work/p15-a-reporter-pure-20261021`; no A/B cross-ownership, docs, RF, STATUS, C04/C05, frozen or operational policy edits. Fake/temp fixtures only. Never invoke report generation entrypoint, runtime scheduler, real broker, live account/order, Guard, Step5C, UEF, RunLab, operational apply, network or production State/DB. Read-only file tests must use tmp_path. `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_*_projection.py` and normal `python -m pytest -q -p no:cacheprovider <each listed test>` exit0 (or reproducible stdlib smoke if pytest missing). Compare pre-move original with new Owner and thin wrapper for positive/negative/monkeypatch parity. G1 = actual A remote code blob; G2 = normal scoped exit0; C04/C05 own G3 and DONE. No blanket -O/full peer/hosted CI. Commit only changed code/test, normal push or approved exact-tree lease-protected delivery; re-fetch A remote HEAD plus SOURCE/TARGET/TEST blobs and verify. Git auth failure=PUSH_BLOCKED not fake G1; preserve local-only and continue all safe items. Never force push.

## A1 — RF-035 | SOURCE `libs/reporting/intraday_trade_reports.py::_read_json` blob `819ce8b895d8fb5adc8b60cf3ba42988d35803cb` lines 123–132 → TARGET `libs/reporting/intraday_report_read_projection.py::_read_json` (new, 404)

**Exact SOURCE computation BODY to MOVE (not copy):**

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

**Thin wrapper / call-time patch:** Retain the original SOURCE signature and annotations. Replace only function BODY with delegation to `libs.reporting.intraday_report_read_projection._read_json` using `facade=_r3_sys.modules[__name__]` where referenced helpers/globals require it; pass all existing parameters unchanged. TARGET imports only standard library and type dependencies, never SOURCE. Original globals and nested helpers retain their resolution semantics. No writing or live effects. If a target already exists at new A HEAD, compare actual body; mark REMOTE_DONE if already moved and do not overwrite.

**Normal targeted G2:** new `tests/test_p15_rf035_06h_a1_intraday_read_json_owner.py`: tmp_path missing file -> {}; valid dict JSON {'x':1} -> {'x':1}; JSON array and malformed JSON -> {}; facade.json.loads patched to raise -> {} (same exception handling); verify wrapper/Owner original parity and no writes. Run `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_06h_a1_intraday_read_json_owner.py` normal exit0 or exact stdlib smoke; `py_compile`; compare baseline original/Owner/wrapper and exceptions, then A code/test-only commit + push + remote SOURCE/TARGET/TEST blob refetch. If isolated failure, record FIRST_BLOCKER and continue A2.

## A2 — RF-035 | SOURCE `libs/reporting/intraday_trade_reports.py::_load_story_input` blob `819ce8b895d8fb5adc8b60cf3ba42988d35803cb` lines 225–235 → TARGET `libs/reporting/intraday_report_read_projection.py::_load_story_input` (new, 404)

**Exact SOURCE computation BODY to MOVE (not copy):**

```python
def _load_story_input(trade_dir: Path) -> tuple[Dict[str, Any], str]:
    canonical = trade_dir / "ai_trade_report_input.json"
    normalized_legacy = trade_dir / "ai_trade_report" / "ai_trade_report_input.json"
    legacy = trade_dir / "trade_story_input.json"
    for path in (canonical, normalized_legacy, legacy):
        payload = _read_json(path)
        if payload:
            return payload, str(path)
    return {}, ""
```

**Thin wrapper / call-time patch:** Retain the original SOURCE signature and annotations. Replace only function BODY with delegation to `libs.reporting.intraday_report_read_projection._load_story_input` using `facade=_r3_sys.modules[__name__]` where referenced helpers/globals require it; pass all existing parameters unchanged. TARGET imports only standard library and type dependencies, never SOURCE. Original globals and nested helpers retain their resolution semantics. No writing or live effects. If a target already exists at new A HEAD, compare actual body; mark REMOTE_DONE if already moved and do not overwrite.

**Normal targeted G2:** new `tests/test_p15_rf035_06h_a2_intraday_story_input_owner.py`: tmp_path with canonical ai_trade_report_input.json {'k':1} and legacy {'k':2} -> ({'k':1},canonical path); remove canonical -> legacy selected; all absent -> ({},''); monkeypatch facade._read_json at call-time, compare wrapper/Owner. Run `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_06h_a2_intraday_story_input_owner.py` normal exit0 or exact stdlib smoke; `py_compile`; compare baseline original/Owner/wrapper and exceptions, then A code/test-only commit + push + remote SOURCE/TARGET/TEST blob refetch. If isolated failure, record FIRST_BLOCKER and continue A3.

## A3 — RF-035 | SOURCE `libs/reporting/intraday_trade_reports.py::build_same_day_reporter_linkage` blob `819ce8b895d8fb5adc8b60cf3ba42988d35803cb` lines 169–224 → TARGET `libs/reporting/intraday_report_linkage_projection.py::build_same_day_reporter_linkage` (new, 404)

**Exact SOURCE computation BODY to MOVE (not copy):**

```python
def build_same_day_reporter_linkage(
    *,
    reporter_obj: Dict[str, Any],
    reporter_js: Path,
    reporter_md: Path,
    entry_run_id: str,
    exit_run_id: str,
    entry_bundle: Dict[str, Any],
    exit_bundle: Dict[str, Any],
) -> Dict[str, Any]:
    reporter_obj = reporter_obj if isinstance(reporter_obj, dict) else {}
    entry_reporter = entry_bundle.get("reporter") if isinstance(entry_bundle.get("reporter"), dict) else {}
    exit_reporter = exit_bundle.get("reporter") if isinstance(exit_bundle.get("reporter"), dict) else {}
    reporter_day_file_found = bool(
        reporter_js.exists()
        or reporter_md.exists()
        or entry_reporter.get("reporter_analysis_day_file_found")
        or exit_reporter.get("reporter_analysis_day_file_found")
    )
    linked_run_ids: List[str] = []
    if bool(entry_reporter.get("reporter_analysis_found")) and entry_run_id:
        linked_run_ids.append(str(entry_run_id))
    if bool(exit_reporter.get("reporter_analysis_found")) and exit_run_id and exit_run_id not in linked_run_ids:
        linked_run_ids.append(str(exit_run_id))
    run_link_found = bool(linked_run_ids)
    if run_link_found:
        status = "linked_run"
        linkage_source = "run_specific"
        linkage_reason = "A same-day reporter analysis linked directly to this lifecycle run."
    elif reporter_day_file_found:
        status = "linked_day_fallback"
        linkage_source = "day_fallback"
        linkage_reason = "A same-day reporter analysis file was attached as fallback context for this lifecycle."
    else:
        status = "missing"
        linkage_source = "missing"
        linkage_reason = "Same-day reporter analysis is not available for this lifecycle yet."
    return {
        "schema_version": "same_day_reporter_linkage.v1",
        "status": status,
        "linkage_source": linkage_source,
        "linkage_reason": linkage_reason,
        "reporter_analysis_day_file_found": reporter_day_file_found,
        "run_link_found": run_link_found,
        "linked_run_ids": linked_run_ids,
        "reporter_analysis_json_path": str(reporter_js) if reporter_js.exists() else "",
        "reporter_analysis_md_path": str(reporter_md) if reporter_md.exists() else "",
        "reporter_analysis_expected_json_path": str(reporter_js),
        "reporter_analysis_expected_md_path": str(reporter_md),
        "reporter_analysis_json_found": bool(reporter_js.exists()),
        "reporter_analysis_md_found": bool(reporter_md.exists()),
        "reporter_analysis_summary": str(reporter_obj.get("ai_summary") or ""),
        "reporter_analysis_grade": str(reporter_obj.get("ai_run_grade") or "N/A"),
    }
```

**Thin wrapper / call-time patch:** Retain the original SOURCE signature and annotations. Replace only function BODY with delegation to `libs.reporting.intraday_report_linkage_projection.build_same_day_reporter_linkage` using `facade=_r3_sys.modules[__name__]` where referenced helpers/globals require it; pass all existing parameters unchanged. TARGET imports only standard library and type dependencies, never SOURCE. Original globals and nested helpers retain their resolution semantics. No writing or live effects. If a target already exists at new A HEAD, compare actual body; mark REMOTE_DONE if already moved and do not overwrite.

**Normal targeted G2:** new `tests/test_p15_rf035_06h_a3_intraday_linkage_owner.py`: nonexistent reporter_js/md and no reporter flags -> status='missing', linked_run_ids=[]; create fake reporter_js -> status='linked_day_fallback'; entry_bundle={'reporter':{'reporter_analysis_found':True}}, entry_run_id='r1' -> status='linked_run', linked_run_ids=['r1']; no real paths; compare all output fields and negative inputs. Run `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_06h_a3_intraday_linkage_owner.py` normal exit0 or exact stdlib smoke; `py_compile`; compare baseline original/Owner/wrapper and exceptions, then A code/test-only commit + push + remote SOURCE/TARGET/TEST blob refetch. If isolated failure, record FIRST_BLOCKER and continue A4.

## A4 — RF-035 | SOURCE `libs/reporting/intraday_trade_reports.py::_story_input_quality_score` blob `819ce8b895d8fb5adc8b60cf3ba42988d35803cb` lines 236–317 → TARGET `libs/reporting/intraday_report_quality_projection.py::_story_input_quality_score` (new, 404)

**Exact SOURCE computation BODY to MOVE (not copy):**

```python
def _story_input_quality_score(story_input: Dict[str, Any]) -> int:
    if not isinstance(story_input, dict) or not story_input:
        return 0

    def _execution_truth_score(details: Any) -> int:
        details_obj = details if isinstance(details, dict) else {}
        local_score = 0
        if str(details_obj.get("order_id") or "").strip():
            local_score += 1
        if details_obj.get("filled_qty") not in (None, ""):
            local_score += 1
        if details_obj.get("filled_price") not in (None, ""):
            local_score += 2
        if str(details_obj.get("broker_truth_source") or "").strip():
            local_score += 2
        if str(details_obj.get("broker_day_truth_source") or "").strip():
            local_score += 2
        if str(details_obj.get("broker_day_match_mode") or "").strip():
            local_score += 1
        if bool(details_obj.get("broker_day_authoritative")):
            local_score += 1
        if details_obj.get("broker_realized_pnl") not in (None, ""):
            local_score += 2
        if details_obj.get("broker_fee") not in (None, "") or details_obj.get("broker_tax") not in (None, ""):
            local_score += 1
        return local_score

    score = 0
    status_lower = str(story_input.get("status") or "").strip().lower()
    trade_symbol = str(story_input.get("symbol") or "").strip()
    if status_lower in {"open", "closed"}:
        score += 2
    if trade_symbol:
        score += 1
    if str(story_input.get("run_id") or "").strip():
        score += 1
    scanner_reason_human = (
        story_input.get("scanner_reason_human")
        if isinstance(story_input.get("scanner_reason_human"), dict)
        else {}
    )
    scanner_trace = (
        story_input.get("scanner_selection_trace")
        if isinstance(story_input.get("scanner_selection_trace"), dict)
        else {}
    )
    selected_symbol = str(
        story_input.get("selected_symbol")
        or scanner_reason_human.get("selected_symbol")
        or scanner_trace.get("selected_symbol")
        or ""
    ).strip()
    if selected_symbol:
        score += 2
    if status_lower == "closed" and trade_symbol and selected_symbol and trade_symbol != selected_symbol:
        score -= 2
    candidate_count = (
        story_input.get("candidate_count")
        if story_input.get("candidate_count") not in (None, "")
        else scanner_reason_human.get("candidate_count")
    )
    if isinstance(candidate_count, (int, float)) and float(candidate_count) > 0:
        score += 1
    if isinstance(scanner_trace.get("ranked_candidates"), list) and len(scanner_trace.get("ranked_candidates") or []) > 0:
        score += 1
    if isinstance(story_input.get("monitor_stop_policy_trace"), dict) and story_input.get("monitor_stop_policy_trace"):
        score += 1
    canonical_monitor = story_input.get("canonical_monitor") if isinstance(story_input.get("canonical_monitor"), dict) else {}
    if canonical_monitor:
        score += 1
    if canonical_monitor.get("current_price") not in (None, ""):
        score += 1
    if canonical_monitor.get("account_pnl_ratio") not in (None, "") or canonical_monitor.get("effective_pnl_ratio") not in (None, ""):
        score += 1
    if str(story_input.get("entry_summary") or "").strip():
        score += 1
    score += _execution_truth_score(story_input.get("execution_details"))
    score += _execution_truth_score(story_input.get("entry_execution_details"))
    score += _execution_truth_score(story_input.get("exit_execution_details"))
    return score
```

**Thin wrapper / call-time patch:** Retain the original SOURCE signature and annotations. Replace only function BODY with delegation to `libs.reporting.intraday_report_quality_projection._story_input_quality_score` using `facade=_r3_sys.modules[__name__]` where referenced helpers/globals require it; pass all existing parameters unchanged. TARGET imports only standard library and type dependencies, never SOURCE. Original globals and nested helpers retain their resolution semantics. No writing or live effects. If a target already exists at new A HEAD, compare actual body; mark REMOTE_DONE if already moved and do not overwrite.

**Normal targeted G2:** new `tests/test_p15_rf035_06h_a4_intraday_story_score_owner.py`: {} -> 0; {'status':'open','symbol':'005930','run_id':'r'} -> 4; add {'execution_details':{'order_id':'x','filled_price':10}} -> 7; non-dict -> 0; original/wrapper/Owner parity, no external inputs. Run `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_06h_a4_intraday_story_score_owner.py` normal exit0 or exact stdlib smoke; `py_compile`; compare baseline original/Owner/wrapper and exceptions, then A code/test-only commit + push + remote SOURCE/TARGET/TEST blob refetch. If isolated failure, record FIRST_BLOCKER and continue A5.

## A5 — RF-035 | SOURCE `libs/reporting/intraday_trade_reports.py::_truth_surface_differs` blob `819ce8b895d8fb5adc8b60cf3ba42988d35803cb` lines 322–328 → TARGET `libs/reporting/intraday_report_quality_projection.py::_truth_surface_differs` (new, 404)

**Exact SOURCE computation BODY to MOVE (not copy):**

```python
def _truth_surface_differs(existing_story_input: Dict[str, Any], rebuilt_story_input: Dict[str, Any]) -> bool:
    for key in ("execution_details", "entry_execution_details", "exit_execution_details"):
        if _execution_truth_surface(existing_story_input.get(key)) != _execution_truth_surface(rebuilt_story_input.get(key)):
            return True
    return False
```

**Thin wrapper / call-time patch:** Retain the original SOURCE signature and annotations. Replace only function BODY with delegation to `libs.reporting.intraday_report_quality_projection._truth_surface_differs` using `facade=_r3_sys.modules[__name__]` where referenced helpers/globals require it; pass all existing parameters unchanged. TARGET imports only standard library and type dependencies, never SOURCE. Original globals and nested helpers retain their resolution semantics. No writing or live effects. If a target already exists at new A HEAD, compare actual body; mark REMOTE_DONE if already moved and do not overwrite.

**Normal targeted G2:** new `tests/test_p15_rf035_06h_a5_intraday_truth_diff_owner.py`: empty dicts -> False; differing execution_details order_id -> True when original facade._execution_truth_surface says so; patch facade._execution_truth_surface to deterministic fake and confirm wrapper/Owner both use patched helper at call time; no broker access. Run `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_06h_a5_intraday_truth_diff_owner.py` normal exit0 or exact stdlib smoke; `py_compile`; compare baseline original/Owner/wrapper and exceptions, then A code/test-only commit + push + remote SOURCE/TARGET/TEST blob refetch. If isolated failure, record FIRST_BLOCKER and continue A6.

## A6 — RF-035 | SOURCE `libs/reporting/intraday_trade_reports.py::build_live_bundle_backfill_payload` blob `819ce8b895d8fb5adc8b60cf3ba42988d35803cb` lines 438–550 → TARGET `libs/reporting/intraday_report_payload_projection.py::build_live_bundle_backfill_payload` (new, 404)

**Exact SOURCE computation BODY to MOVE (not copy):**

```python
def build_live_bundle_backfill_payload(
    *,
    trade_id: str,
    status: str,
    story_type: str,
    execution_mode_label: str,
    symbol: str,
    entry_run_id: str,
    hold_run_ids: List[str],
    exit_run_id: str,
    linked_run_ids: List[str],
    lifecycle_summary: str,
    lifecycle_bundle_path: Path,
    story_input_path: Path,
    story_compact_input_path: Path,
    trade_report_json_written: str,
    trade_report_md_written: str,
    strategist_llm_response_path: Path,
    ai_trade_report_llm_response_written: str,
    entry_artifact_path: Path,
    hold_artifact_path: Path,
    exit_artifact_path: Path,
    strategist_evidence_path: Path,
    scanner_evidence_path: Path,
    monitor_evidence_path: Path,
    commander_evidence_path: Path,
    trade_provenance_path: Path,
    trade_health_path: Path,
    trade_artifact_links_path: Path,
    trade_root: Path,
    trade_report_summary: str,
    diagnostics: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    diagnostics_obj = dict(diagnostics or {})
    common_row_patch = {
        "trade_id": trade_id,
        "story_id": trade_id,
        "lifecycle_bundle_json_path": str(lifecycle_bundle_path),
        "trade_lifecycle_json_path": "",
        "trade_story_input_path": str(story_input_path),
        "ai_trade_report_input_path": str(story_input_path),
        "ai_trade_report_compact_input_path": str(story_compact_input_path),
        "trade_report_json_path": str(trade_report_json_written or ""),
        "trade_report_md_path": str(trade_report_md_written or ""),
        "ai_trade_report_json_path": str(trade_report_json_written or ""),
        "ai_trade_report_md_path": str(trade_report_md_written or ""),
        "strategist_llm_response_path": str(strategist_llm_response_path),
        "ai_trade_report_llm_response_path": str(ai_trade_report_llm_response_written or ""),
        "entry_json_path": str(entry_artifact_path),
        "hold_json_path": str(hold_artifact_path),
        "exit_json_path": str(exit_artifact_path),
        "strategist_evidence_json_path": str(strategist_evidence_path),
        "scanner_evidence_json_path": str(scanner_evidence_path),
        "monitor_evidence_json_path": str(monitor_evidence_path),
        "monitor_timeline_json_path": str(monitor_evidence_path),
        "commander_evidence_json_path": str(commander_evidence_path),
        "trade_provenance_json_path": str(trade_provenance_path),
        "trade_health_json_path": str(trade_health_path),
        "trade_artifact_links_json_path": str(trade_artifact_links_path),
        "trade_root_path": str(trade_root),
        "trade_report_summary": str(trade_report_summary or ""),
        "report_status": str(diagnostics_obj.get("report_status") or ""),
        "report_reason_code": str(diagnostics_obj.get("report_reason_code") or ""),
        "report_reason_human": str(diagnostics_obj.get("report_reason_human") or ""),
        "report_next_expected_step": str(diagnostics_obj.get("next_expected_step") or ""),
        "report_generation_model": str(diagnostics_obj.get("llm_model_used") or ""),
        "report_generation_attempted": bool(diagnostics_obj.get("generation_attempted")),
        "deterministic_report_status": str(diagnostics_obj.get("deterministic_report_status") or ""),
        "llm_brief_status": str(diagnostics_obj.get("llm_brief_status") or ""),
        "ai_trade_report_status": str(diagnostics_obj.get("ai_trade_report_status") or ""),
    }
    lifecycle_row = {
        "trade_id": trade_id,
        "story_id": trade_id,
        "status": status,
        "story_type": story_type,
        "execution_mode_label": execution_mode_label,
        "symbol": symbol,
        "entry_run_id": entry_run_id,
        "hold_run_ids": list(hold_run_ids or []),
        "exit_run_id": exit_run_id,
        "linked_run_ids": list(linked_run_ids or []),
        "lifecycle_summary": str(lifecycle_summary or ""),
        "report_json_path": str(lifecycle_bundle_path),
        **common_row_patch,
    }
    bundle_artifacts_patch = {
        "lifecycle_bundle_json": str(lifecycle_bundle_path),
        "entry_json": str(entry_artifact_path),
        "hold_json": str(hold_artifact_path),
        "exit_json": str(exit_artifact_path),
        "trade_story_input_json": str(story_input_path),
        "ai_trade_report_input_json": str(story_input_path),
        "ai_trade_report_compact_input_json": str(story_compact_input_path),
        "trade_report_json": str(trade_report_json_written or ""),
        "trade_report_md": str(trade_report_md_written or ""),
        "ai_trade_report_json": str(trade_report_json_written or ""),
        "ai_trade_report_md": str(trade_report_md_written or ""),
        "strategist_llm_response_json": str(strategist_llm_response_path),
        "ai_trade_report_llm_response_json": str(ai_trade_report_llm_response_written or ""),
        "strategist_evidence_json": str(strategist_evidence_path),
        "scanner_evidence_json": str(scanner_evidence_path),
        "monitor_evidence_json": str(monitor_evidence_path),
        "monitor_timeline_json": str(monitor_evidence_path),
        "commander_evidence_json": str(commander_evidence_path),
    }
    return {
        "lifecycle_row": lifecycle_row,
        "run_bundle_row_patch": common_row_patch,
        "bundle_artifacts_patch": bundle_artifacts_patch,
    }
```

**Thin wrapper / call-time patch:** Retain the original SOURCE signature and annotations. Replace only function BODY with delegation to `libs.reporting.intraday_report_payload_projection.build_live_bundle_backfill_payload` using `facade=_r3_sys.modules[__name__]` where referenced helpers/globals require it; pass all existing parameters unchanged. TARGET imports only standard library and type dependencies, never SOURCE. Original globals and nested helpers retain their resolution semantics. No writing or live effects. If a target already exists at new A HEAD, compare actual body; mark REMOTE_DONE if already moved and do not overwrite.

**Normal targeted G2:** new `tests/test_p15_rf035_06h_a6_intraday_backfill_payload_owner.py`: supply all signature keyword parameters using tmp_path fake Paths, trade_id='T1', linked_run_ids=['r1'], diagnostics={'report_status':'available','generation_attempted':False}; assert lifecycle_row.trade_id=='T1', run_bundle_row_patch.report_status=='available', bundle_artifacts_patch.lifecycle_bundle_json matches fake path, list copies preserve values; original/Owner/wrapper full dict parity. Run `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_06h_a6_intraday_backfill_payload_owner.py` normal exit0 or exact stdlib smoke; `py_compile`; compare baseline original/Owner/wrapper and exceptions, then A code/test-only commit + push + remote SOURCE/TARGET/TEST blob refetch. If isolated failure, record FIRST_BLOCKER and continue A7.

## A7 — RF-035 | SOURCE `libs/reporting/intraday_trade_reports.py::build_live_execution_summary_payload` blob `819ce8b895d8fb5adc8b60cf3ba42988d35803cb` lines 688–745 → TARGET `libs/reporting/intraday_report_payload_projection.py::build_live_execution_summary_payload` (new, 404)

**Exact SOURCE computation BODY to MOVE (not copy):**

```python
def build_live_execution_summary_payload(
    *,
    day: str,
    role: str,
    event_log_path: Path,
    evidence_log_path: Path,
    lifecycle_rows: List[Dict[str, Any]],
    run_bundle_rows: List[Dict[str, Any]],
    lifecycle_story_type_counts: Mapping[str, Any] | None,
    run_story_type_counts: Mapping[str, Any] | None,
    target_ctx: Mapping[str, Any] | None,
    canonical_trades_root: Path,
    trade_js: Path,
    trade_md: Path,
    reporter_js: Path,
    reporter_md: Path,
    operator_summary_json: Path,
    operator_summary_md: Path,
) -> Dict[str, Any]:
    report_status_counts: Dict[str, int] = {}
    for row in list(lifecycle_rows or []):
        key = str((row or {}).get("report_status") or "").strip().lower() or "unknown"
        report_status_counts[key] = int(report_status_counts.get(key, 0) + 1)

    target_ctx = dict(target_ctx or {})
    return {
        "schema_version": "live_execution_bundles.v3",
        "ok": True,
        "ts": _utc_now_iso(),
        "day": str(day or ""),
        "role": str(role or ""),
        "event_log_path": str(event_log_path),
        "evidence_log_path": str(evidence_log_path),
        "bundle_count": len(list(lifecycle_rows or [])),
        "trade_lifecycle_count": len(list(lifecycle_rows or [])),
        "run_bundle_count": len(list(run_bundle_rows or [])),
        "story_type_counts": dict(lifecycle_story_type_counts or {}),
        "report_status_counts": report_status_counts,
        "run_story_type_counts": dict(run_story_type_counts or {}),
        "targeted_mode": bool(target_ctx.get("targeted_mode")),
        "target_run_id": str(target_ctx.get("target_run_id") or ""),
        "target_symbol": str(target_ctx.get("target_symbol") or ""),
        "targeted_execution_run_count": int(target_ctx.get("execution_run_count") or 0),
        "targeted_lifecycle_context_run_count": int(target_ctx.get("lifecycle_context_run_count") or 0),
        "canonical_trades_root": str(canonical_trades_root),
        "bundles": list(lifecycle_rows or []),
        "run_bundles": list(run_bundle_rows or []),
        "day_artifacts": {
            "trade_explain_json": str(trade_js),
            "trade_explain_md": str(trade_md),
            "reporter_analysis_json": str(reporter_js) if reporter_js.exists() else "",
            "reporter_analysis_md": str(reporter_md) if reporter_md.exists() else "",
            "operator_summary_json": str(operator_summary_json) if operator_summary_json.exists() else "",
            "operator_summary_md": str(operator_summary_md) if operator_summary_md.exists() else "",
        },
    }
```

**Thin wrapper / call-time patch:** Retain the original SOURCE signature and annotations. Replace only function BODY with delegation to `libs.reporting.intraday_report_payload_projection.build_live_execution_summary_payload` using `facade=_r3_sys.modules[__name__]` where referenced helpers/globals require it; pass all existing parameters unchanged. TARGET imports only standard library and type dependencies, never SOURCE. Original globals and nested helpers retain their resolution semantics. No writing or live effects. If a target already exists at new A HEAD, compare actual body; mark REMOTE_DONE if already moved and do not overwrite.

**Normal targeted G2:** new `tests/test_p15_rf035_06h_a7_intraday_summary_payload_owner.py`: freeze facade._utc_now_iso=lambda:'2026-10-31T00:00:00+00:00'; fake lifecycle_rows=[{'report_status':'ok'},{'report_status':'FAILED'}], run_bundle_rows=[]; expect report_status_counts={'ok':1,'failed':1}, bundle_count=2, ts frozen, nonexistent fake artifact paths -> empty strings; original/Owner/wrapper equality, no writes. Run `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_06h_a7_intraday_summary_payload_owner.py` normal exit0 or exact stdlib smoke; `py_compile`; compare baseline original/Owner/wrapper and exceptions, then A code/test-only commit + push + remote SOURCE/TARGET/TEST blob refetch. If isolated failure, record FIRST_BLOCKER and continue A8.

## A8 — RF-035 | SOURCE `libs/reporting/intraday_trade_reports.py::_report_diagnostics_from_report` blob `819ce8b895d8fb5adc8b60cf3ba42988d35803cb` lines 746–833 → TARGET `libs/reporting/intraday_report_diagnostics_projection.py::_report_diagnostics_from_report` (new, 404)

**Exact SOURCE computation BODY to MOVE (not copy):**

```python
def _report_diagnostics_from_report(report: Dict[str, Any], llm_artifact: Dict[str, Any]) -> Dict[str, Any]:
    generation = report.get("generation") if isinstance(report.get("generation"), dict) else {}
    generation_status = str(generation.get("status") or llm_artifact.get("status") or "").strip().lower()
    generation_mode = str(generation.get("mode") or "").strip().lower()
    declared_ai_status = str(
        report.get("ai_trade_report_status")
        or generation.get("ai_trade_report_status")
        or ""
    ).strip().lower()
    model = str(generation.get("model") or llm_artifact.get("model") or ((llm_artifact.get("model_info") or {}).get("model")) or "")
    deterministic_only = generation_mode in {"deterministic", "local_debug"} or (
        declared_ai_status == "skipped" and generation_status in {"ok", "skipped", ""}
    )
    if deterministic_only:
        ai_trade_report_status = "skipped"
    elif generation_status in {"ok", "repaired"}:
        ai_trade_report_status = "ok"
    elif generation_status in {"partial", "salvaged"}:
        ai_trade_report_status = "partial"
    elif generation_status in {"skipped", "disabled"}:
        ai_trade_report_status = "skipped"
    else:
        ai_trade_report_status = "error"
    diagnostics = {
        "report_status": "failed",
        "report_reason_code": "llm_generation_failed",
        "report_reason_human": "AI trade report generation failed.",
        "report_generation_reason": "AI trade report generation failed.",
        "generation_attempted": True,
        "generation_ts": _utc_now_iso(),
        "story_input_available": True,
        "report_output_available": True,
        "report_artifact_available": True,
        "llm_model_used": model,
        "last_error_message": str(llm_artifact.get("error") or ""),
        "next_expected_step": "Inspect the LLM response artifact and retry generation.",
        "deterministic_report_status": str(
            report.get("deterministic_report_status")
            or generation.get("deterministic_report_status")
            or "ok"
        ),
        "llm_brief_status": str(report.get("llm_brief_status") or generation.get("llm_brief_status") or "skipped"),
        "ai_trade_report_status": ai_trade_report_status,
        "llm_response_status": str(llm_artifact.get("status") or ""),
        "llm_parse_mode": str(llm_artifact.get("parse_mode") or ""),
        "llm_completeness_score": float(llm_artifact.get("completeness_score") or 0.0),
        "llm_required_keys_missing": [
            str(x or "")
            for x in list(llm_artifact.get("required_keys_missing") or [])
            if str(x or "").strip()
        ],
    }
    if deterministic_only:
        diagnostics.update(
            {
                "report_status": "available",
                "report_reason_code": "deterministic_only",
                "report_reason_human": "Deterministic report was generated without AI expansion.",
                "report_generation_reason": "Deterministic report was generated without AI expansion.",
                "generation_attempted": False,
                "next_expected_step": "Review deterministic report sections and evidence linkage.",
                "last_error_message": "",
            }
        )
    elif generation_status in {"ok", "repaired"}:
        diagnostics.update(
            {
                "report_status": "available",
                "report_reason_code": "",
                "report_reason_human": "AI trade report was generated successfully.",
                "report_generation_reason": "AI trade report was generated successfully.",
                "next_expected_step": "Open the full report for detailed lifecycle analysis.",
                "last_error_message": "",
            }
        )
    elif generation_status in {"partial", "salvaged"}:
        diagnostics.update(
            {
                "report_status": "available",
                "report_reason_code": "llm_generation_salvaged",
                "report_reason_human": "AI trade report was generated with partial recovery.",
                "report_generation_reason": "AI trade report was generated with partial recovery.",
                "next_expected_step": "Open the report and review completeness metadata before relying on every section.",
            }
        )
    return diagnostics
```

**Thin wrapper / call-time patch:** Retain the original SOURCE signature and annotations. Replace only function BODY with delegation to `libs.reporting.intraday_report_diagnostics_projection._report_diagnostics_from_report` using `facade=_r3_sys.modules[__name__]` where referenced helpers/globals require it; pass all existing parameters unchanged. TARGET imports only standard library and type dependencies, never SOURCE. Original globals and nested helpers retain their resolution semantics. No writing or live effects. If a target already exists at new A HEAD, compare actual body; mark REMOTE_DONE if already moved and do not overwrite.

**Normal targeted G2:** new `tests/test_p15_rf035_06h_a8_intraday_diagnostics_owner.py`: freeze facade._utc_now_iso; report={'generation':{'status':'ok','model':'fake'}} and llm_artifact={} -> report_status='available', ai_trade_report_status='ok'; generation.mode='deterministic' -> ai_trade_report_status='skipped', generation_attempted=False; completeness_score='invalid' raises same ValueError through wrapper/Owner; no model/network call. Run `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_06h_a8_intraday_diagnostics_owner.py` normal exit0 or exact stdlib smoke; `py_compile`; compare baseline original/Owner/wrapper and exceptions, then A code/test-only commit + push + remote SOURCE/TARGET/TEST blob refetch. If isolated failure, record FIRST_BLOCKER and continue Acompletion report.

## Reserve — RESERVE_NOT_VERIFIED (A 0/6)

Previous six verified reserve items were consumed by A-05 and are REMOTE_DONE. This order has eight separately inspected and verified NEW items, but **no new six reserve candidates were fully validated**. Do not count speculative filenames, already-moved wrappers, KEEP, effectful helpers, or other RF owners as verified reserve. C03 must inspect next A-owned SOURCE bodies/target absence/tests before promoting six future items; A must not self-select from this section.

## Required #11 report

Report `ORDER_ID=A-20261031-06 | ORDER_BLOB | CANONICAL_HEAD | A_START_SHA→A_REMOTE_SHA | A1..A8 IMPLEMENTED/REMOTE_DONE/BLOCKED | SOURCE_BEFORE_AFTER_BLOBS/LOC | TARGET_BLOBS | TEST_NORMAL_COMMAND/EXIT | FIRST_BLOCKER | NEXT`. START/END/ELAPSED only measured values. Each item is independent and mandatory. New C02 issued mid-session does not invalidate a previously pinned start order. C03's order publication is **not** code G1/G2/G3 or RF DONE.
