# C02 — Agentra FAST-3 Claude A | ORDER A-20261031-05 | 8 NEW verified actual SOURCE BODY MOVEs

**Authoritative preflight at publication:** integration HEAD `115425b347e3288b7b07d1df0cadbf7af824eae3`; A remote HEAD `09a816f516d055e1e6b4b0952b74363bfa9648f7`; B remote HEAD `97c1c22cb70fbb022dce4391362f589e00d171ac`. Previous C02 blob `1043ef52a165f9450308b50454d3d53891ad4a41` ORDER A-04 is **8/8 REMOTE_DONE**, A #11 comment 6531488218 normal targeted **44 PASS exit0**, SOURCE `symbol_trade_report.py` after blob `28f8a159f4da31bfb7726681516bddf966706ede`; C04 integrated A-04 at `852480b2b8372fa1c8cf2b5dba4103fcf4185afa` and C05 accepted scoped G1/G2/G3. **Do not repeat A-04 or older PASS.** Current eight A1–A8 are separate unmoved functions, verified on latest A remote; R1–R6 prior reserve bodies were re-compared byte-for-byte against current SOURCE and targets 404, plus new A7/A8 SOURCE/TARGET checked. RF-035 is A-exclusive reporting scope; B RF-063/RF-065 paths disjoint.

**Single-file complete execution:** At start pin CANONICAL_HEAD, ORDER_FILE_BLOB_SHA, A_REMOTE_SHA and each SOURCE blob. Read **only this C02**, not D00/RF/queue/detail designs, and do not self-select tasks. Execute **all A1–A8**, continue past each isolated blocker; if a newer remote SHA already moved one item, mark REMOTE_DONE and skip duplicate. Real BODY must leave SOURCE, TARGET becomes sole computation owner, SOURCE thin wrapper preserves caller/monkeypatch and exact signature, annotations, lazy timing, output/errors. Symbol_trade_report has UTF-8 BOM: preserve it. Owner TARGET never imports SOURCE; append without overwriting. Normal targeted fake/tmp test exit0 once per changed scope, `py_compile`, A code/test-only commit and normal push, re-fetch A remote HEAD and SOURCE/TARGET/TEST blob. Git auth failure=PUSH_BLOCKED not G2; pytest absence=test-only blocker and use stdlib smoke where possible; continue other safe work. Report each item and exact SHA/exit to #11. No forced -O/full peer/per-RF hosted CI; C04/C05 own G3/DONE. Never touch B branch, RF/STATUS/C04/C05/docs, production data/State/DB, live network, real account/order, Broker/Guard/Step5C/UEF/RunLab/operational apply. No force push.

## A1 — RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_extract_trade_artifact_snapshot` blob `28f8a159f4da31bfb7726681516bddf966706ede` → TARGET `libs/reporting/symbol_trade_artifact_projection.py::_extract_trade_artifact_snapshot` (404 A/integration; newly owned by A)

**Exact original computation BODY to MOVE once:**

```python
def _extract_trade_artifact_snapshot(
    *,
    report_path: Path,
    operator_brief_path: Path,
    lifecycle_bundle_path: Path,
) -> Dict[str, Any]:
    report = _read_json(report_path)
    brief = _read_json(operator_brief_path)
    bundle = _read_json(lifecycle_bundle_path)
    report_executive = report.get("executive_summary") if isinstance(report.get("executive_summary"), dict) else {}
    report_market = report.get("market_context_at_entry") if isinstance(report.get("market_context_at_entry"), dict) else {}
    report_entry = report.get("entry_decision") if isinstance(report.get("entry_decision"), dict) else {}
    report_final = report.get("final_operator_conclusion") if isinstance(report.get("final_operator_conclusion"), dict) else {}
    feedback = (
        bundle.get("strategist_feedback_input")
        if isinstance(bundle.get("strategist_feedback_input"), dict)
        else report.get("strategist_feedback_input")
        if isinstance(report.get("strategist_feedback_input"), dict)
        else {}
    )
    shared_facts = (
        bundle.get("shared_facts")
        if isinstance(bundle.get("shared_facts"), dict)
        else report.get("shared_facts")
        if isinstance(report.get("shared_facts"), dict)
        else {}
    )
    trade_outcome = bundle.get("trade_outcome") if isinstance(bundle.get("trade_outcome"), dict) else {}
    report_shared_facts = report.get("shared_facts") if isinstance(report.get("shared_facts"), dict) else {}
    artifact_result_pct = _pick_result_pct(
        trade_outcome.get("return_pct"),
        shared_facts.get("return_pct"),
        shared_facts.get("pnl_pct"),
        report_shared_facts.get("return_pct"),
        report_shared_facts.get("pnl_pct"),
    )
    entry_reason_text = str(report_entry.get("summary") or "").strip()
    actual_entry_reason_text = _actual_entry_reason_from_artifacts(
        report_path=Path(report_path),
        report_entry_summary=entry_reason_text,
        bundle=bundle,
        feedback=feedback,
    )
    exit_reason_text = str(shared_facts.get("exit_reason") or "").strip()
    if not exit_reason_text:
        exit_reason_text = str(report_final.get("summary") or "").strip()
    entry_pattern_type = str(feedback.get("entry_pattern_type") or "").strip() or _classify_entry_pattern(actual_entry_reason_text or entry_reason_text)
    exit_pattern_type = str(feedback.get("exit_pattern_type") or "").strip() or _classify_exit_pattern(exit_reason_text)
    clean_entry_reason = _clean_symbol_reason(actual_entry_reason_text or entry_reason_text, axis="entry")
    clean_exit_reason = _clean_symbol_reason(exit_reason_text, axis="exit")
    return {
        "report_headline": _clean_symbol_free_text(report_executive.get("headline") or report.get("headline"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "report_executive_summary": _clean_symbol_free_text(report_executive.get("summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "report_market_summary": str(report_market.get("summary") or "").strip(),
        "report_entry_summary": clean_entry_reason,
        "actual_entry_reason": clean_entry_reason,
        "report_final_conclusion": _clean_symbol_free_text(report_final.get("summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_headline": _clean_symbol_free_text(brief.get("headline"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_executive_summary": _clean_symbol_free_text(brief.get("executive_summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_risk_summary": _clean_symbol_free_text(brief.get("risk_summary"), entry_reason=clean_entry_reason, exit_reason=clean_exit_reason),
        "brief_next_checkpoints": _list_text(brief.get("next_checkpoints"), limit=3),
        "entry_pattern_type": _clean_symbol_pattern(entry_pattern_type, axis="entry", fallback_reason=clean_entry_reason),
        "exit_pattern_type": _clean_symbol_pattern(exit_pattern_type, axis="exit", fallback_reason=clean_exit_reason),
        "thesis_invalidation_code": _clean_symbol_code(feedback.get("thesis_invalidation_code")),
        "improvement_tags": _list_text(feedback.get("improvement_tags"), limit=6),
        "review_flags": _list_text(feedback.get("review_flags"), limit=6),
        "artifact_result_pct": artifact_result_pct,
    }
```

**Implementation / wrapper / monkeypatch:** facade._read_json, _pick_result_pct, _actual_entry_reason_from_artifacts, _classify_entry_pattern/_classify_exit_pattern and clean helpers; read-only fake JSON paths. Preserve exact-signature thin SOURCE wrapper and output/error parity. Move the complete BODY (not a duplicate) to the new TARGET function; preserve SOURCE's original public signature/annotations/docstring and replace its BODY with a thin delegation wrapper. TARGET must not import SOURCE. Resolve referenced SOURCE helpers/globals through `facade=sys.modules[__name__]` (for symbol_trade_report use its existing `_r3_sys.modules[__name__]`) at call time; keep lazy iterator helper lookup at iteration time. Maintain exact output, exception order and original callers. No changes to any operational/real account files.

**Mandatory new normal targeted test:** `tests/test_p15_rf035_05h_a1_trade_artifact_snapshot_owner.py`. Input/expected: fake tmp report/brief/bundle JSON: trade_outcome.return_pct=1.25 and entry summary/feedback => artifact_result_pct=1.25 and clean entry/exit fields; missing paths => empty/defaults; patched facade._read_json and _pick_result_pct must affect wrapper and Owner identically. Capture original behavior before MOVE and assert original-vs-Owner-vs-wrapper output/error parity and monkeypatch seams. Only fake/temp/controlled clock; do not invoke real data, health or network. `python -m py_compile libs/reporting/symbol_trade_report.py libs/reporting/symbol_trade_artifact_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_05h_a1_trade_artifact_snapshot_owner.py` normal exit0, or exact reproducible stdlib normal smoke if pytest missing. Commit only code+test on A branch, normal push and refetch A remote HEAD/SOURCE/TARGET/TEST blobs; report G1/G2 evidence. If blocked record exact error/SHA and **continue A2**; do not end whole order.

## A2 — RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::_build_history_index` blob `28f8a159f4da31bfb7726681516bddf966706ede` → TARGET `libs/reporting/symbol_trade_history_projection.py::_build_history_index` (404 A/integration; newly owned by A)

**Exact original computation BODY to MOVE once:**

```python
def _build_history_index(reports_root: Path, symbol: str) -> List[Dict[str, Any]]:
    history: List[Dict[str, Any]] = []
    normalized_symbol = str(symbol or "").strip().upper()
    for path, obj in _iter_trade_lifecycles(reports_root):
        if str(obj.get("symbol") or "").strip().upper() != normalized_symbol:
            continue
        summary = obj.get("summary") if isinstance(obj.get("summary"), dict) else {}
        entry = obj.get("entry") if isinstance(obj.get("entry"), dict) else {}
        exit_row = obj.get("exit") if isinstance(obj.get("exit"), dict) else {}
        artifacts = obj.get("artifacts") if isinstance(obj.get("artifacts"), dict) else {}
        trade_id = str(obj.get("trade_id") or "")
        trade_day = str(obj.get("day") or "")
        trade_root = (
            path.parent
            if path.name == "lifecycle_bundle.json"
            else path.parent.parent
        )
        expected_report_path = trade_root / "reports" / "ai_trade_report.json"
        expected_operator_brief_path = trade_root / "reports" / "operator_brief.json"
        lifecycle_bundle_path = trade_root / "lifecycle_bundle.json"
        artifact_snapshot = _extract_trade_artifact_snapshot(
            report_path=Path(str(artifacts.get("ai_trade_report_json") or expected_report_path)),
            operator_brief_path=Path(str(artifacts.get("operator_brief_json") or expected_operator_brief_path)),
            lifecycle_bundle_path=Path(str(artifacts.get("lifecycle_bundle_json") or lifecycle_bundle_path)),
        )
        trade_status = str(obj.get("status") or "").strip()
        if exit_row:
            last_action = "SELL"
        elif trade_status.lower() == "open":
            last_action = "HOLD"
        elif entry:
            last_action = "BUY"
        else:
            last_action = ""
        run_id = (
            str(entry.get("run_id") or "").strip()
            or str(exit_row.get("run_id") or "").strip()
            or str(obj.get("entry_strategist_run_id") or "").strip()
        )
        result_pct = _result_pct_from_lifecycle(obj)
        if result_pct is None:
            result_pct = _safe_float(artifact_snapshot.get("artifact_result_pct"))
        raw_entry_reason = str(summary.get("entry_reason_human") or "")
        artifact_entry_reason = str(artifact_snapshot.get("actual_entry_reason") or "")
        entry_reason_raw = (
            artifact_entry_reason
            if _should_prefer_artifact_entry_reason(raw_entry_reason, artifact_entry_reason)
            else raw_entry_reason
        )
        entry_reason = _clean_symbol_reason(entry_reason_raw, axis="entry")
        exit_reason = _clean_symbol_reason(summary.get("exit_reason_human"), axis="exit")
        entry_pattern_type = _clean_symbol_pattern(
            artifact_snapshot.get("entry_pattern_type"),
            axis="entry",
            fallback_reason=entry_reason,
        )
        exit_pattern_type = _clean_symbol_pattern(
            artifact_snapshot.get("exit_pattern_type"),
            axis="exit",
            fallback_reason=exit_reason,
        )
        history.append(
            {
                "trade_id": trade_id,
                "date": trade_day,
                "run_id": run_id,
                "status": trade_status,
                "last_status": trade_status,
                "last_action": last_action,
                "entry_reason": entry_reason,
                "exit_reason": exit_reason,
                "lifecycle_summary": _clean_lifecycle_summary(
                    trade_id=trade_id,
                    status=trade_status,
                    entry_reason=entry_reason,
                    exit_reason=exit_reason,
                ),
                "operator_conclusion": str(summary.get("operator_conclusion_human") or ""),
                "playbook": str((((entry.get("strategist_context") or {}) if isinstance(entry.get("strategist_context"), dict) else {}).get("playbook")) or ""),
                "hold_seconds": _hold_seconds_from_lifecycle(obj),
                "result_pct": result_pct,
                "trade_origin": str(obj.get("trade_origin") or ""),
                "lifecycle_completeness": str(obj.get("lifecycle_completeness") or ""),
                "evidence_recovery_used": bool(obj.get("evidence_recovery_used")),
                "report_path": str(artifacts.get("ai_trade_report_json") or expected_report_path),
                "operator_brief_path": str(artifacts.get("operator_brief_json") or expected_operator_brief_path),
                "lifecycle_bundle_path": str(artifacts.get("lifecycle_bundle_json") or lifecycle_bundle_path),
                "trade_root_path": str(trade_root),
                "report_headline": str(artifact_snapshot.get("report_headline") or ""),
                "report_executive_summary": str(artifact_snapshot.get("report_executive_summary") or ""),
                "report_market_summary": str(artifact_snapshot.get("report_market_summary") or ""),
                "report_entry_summary": str(artifact_snapshot.get("report_entry_summary") or entry_reason or ""),
                "report_final_conclusion": str(artifact_snapshot.get("report_final_conclusion") or ""),
                "brief_headline": str(artifact_snapshot.get("brief_headline") or ""),
                "brief_executive_summary": str(artifact_snapshot.get("brief_executive_summary") or ""),
                "brief_risk_summary": str(artifact_snapshot.get("brief_risk_summary") or ""),
                "brief_next_checkpoints": list(artifact_snapshot.get("brief_next_checkpoints") or []),
                "entry_pattern_type": entry_pattern_type,
                "exit_pattern_type": exit_pattern_type,
                "thesis_invalidation_code": _clean_symbol_code(artifact_snapshot.get("thesis_invalidation_code")),
                "improvement_tags": list(artifact_snapshot.get("improvement_tags") or []),
                "review_flags": list(artifact_snapshot.get("review_flags") or []),
            }
        )
    history.sort(key=lambda row: (str(row.get("date") or ""), str(row.get("trade_id") or "")))
    return history
```

**Implementation / wrapper / monkeypatch:** facade._iter_trade_lifecycles, _extract_trade_artifact_snapshot and all clean/pct helpers at call time; read-only; preserve sorted (date,trade_id). Preserve exact-signature thin SOURCE wrapper and output/error parity. Move the complete BODY (not a duplicate) to the new TARGET function; preserve SOURCE's original public signature/annotations/docstring and replace its BODY with a thin delegation wrapper. TARGET must not import SOURCE. Resolve referenced SOURCE helpers/globals through `facade=sys.modules[__name__]` (for symbol_trade_report use its existing `_r3_sys.modules[__name__]`) at call time; keep lazy iterator helper lookup at iteration time. Maintain exact output, exception order and original callers. No changes to any operational/real account files.

**Mandatory new normal targeted test:** `tests/test_p15_rf035_05h_a2_history_index_owner.py`. Input/expected: two fake lifecycle rows out of order for same symbol => history sorted by (date,trade_id) with preserved action; different symbol filtered; facade._iter_trade_lifecycles and snapshot helper patched after import; no real disk writes. Capture original behavior before MOVE and assert original-vs-Owner-vs-wrapper output/error parity and monkeypatch seams. Only fake/temp/controlled clock; do not invoke real data, health or network. `python -m py_compile libs/reporting/symbol_trade_report.py libs/reporting/symbol_trade_history_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_05h_a2_history_index_owner.py` normal exit0, or exact reproducible stdlib normal smoke if pytest missing. Commit only code+test on A branch, normal push and refetch A remote HEAD/SOURCE/TARGET/TEST blobs; report G1/G2 evidence. If blocked record exact error/SHA and **continue A3**; do not end whole order.

## A3 — RF-035 | SOURCE `libs/reporting/symbol_trade_report.py::collect_symbols_for_day` blob `28f8a159f4da31bfb7726681516bddf966706ede` → TARGET `libs/reporting/symbol_trade_symbol_projection.py::collect_symbols_for_day` (404 A/integration; newly owned by A)

**Exact original computation BODY to MOVE once:**

```python
def collect_symbols_for_day(
    events_path: Path,
    reports_root: Path,
    day: str,
    trade_index: Optional[List[Dict[str, Any]]] = None,
) -> List[str]:
    target_day = str(day or "").strip()
    symbols: List[str] = []
    seen: set[str] = set()

    index_rows = trade_index if trade_index is not None else build_daily_trade_index(reports_root, target_day)
    for row in index_rows:
        symbol = str(row.get("symbol") or "").strip().upper()
        if symbol and symbol not in seen:
            seen.add(symbol)
            symbols.append(symbol)

    for row in iter_jsonl_events(events_path, day=target_day):
        ts_day = datetime.fromtimestamp(_to_epoch(row.get("ts") or (row.get("payload") or {}).get("ts")), tz=timezone.utc).strftime("%Y-%m-%d") if _to_epoch(row.get("ts") or (row.get("payload") or {}).get("ts")) > 0 else ""
        if ts_day != target_day:
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        detail = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
        order = payload.get("order") if isinstance(payload.get("order"), dict) else {}
        for candidate in (
            detail.get("symbol"),
            payload.get("symbol"),
            order.get("symbol"),
            order.get("stk_cd"),
        ):
            symbol = str(candidate or "").strip().upper()
            if symbol and symbol not in seen:
                seen.add(symbol)
                symbols.append(symbol)
    return symbols
```

**Implementation / wrapper / monkeypatch:** facade.build_daily_trade_index, iter_jsonl_events, _to_epoch, datetime/timezone at call time; fake tmp log only; preserve index-first dedup and timestamp filtering. Preserve exact-signature thin SOURCE wrapper and output/error parity. Move the complete BODY (not a duplicate) to the new TARGET function; preserve SOURCE's original public signature/annotations/docstring and replace its BODY with a thin delegation wrapper. TARGET must not import SOURCE. Resolve referenced SOURCE helpers/globals through `facade=sys.modules[__name__]` (for symbol_trade_report use its existing `_r3_sys.modules[__name__]`) at call time; keep lazy iterator helper lookup at iteration time. Maintain exact output, exception order and original callers. No changes to any operational/real account files.

**Mandatory new normal targeted test:** `tests/test_p15_rf035_05h_a3_collect_symbols_owner.py`. Input/expected: fake trade index ['005930'], same-day fake JSONL symbols ['000660','005930'] and other-day row => ['005930','000660']; case normalization/dedup and patched _to_epoch parity. Capture original behavior before MOVE and assert original-vs-Owner-vs-wrapper output/error parity and monkeypatch seams. Only fake/temp/controlled clock; do not invoke real data, health or network. `python -m py_compile libs/reporting/symbol_trade_report.py libs/reporting/symbol_trade_symbol_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_05h_a3_collect_symbols_owner.py` normal exit0, or exact reproducible stdlib normal smoke if pytest missing. Commit only code+test on A branch, normal push and refetch A remote HEAD/SOURCE/TARGET/TEST blobs; report G1/G2 evidence. If blocked record exact error/SHA and **continue A4**; do not end whole order.

## A4 — RF-035 | SOURCE `libs/reporting/report_source_helpers.py::build_policy_surface_quality_snapshot` blob `8471837632ec1c7659ba2cbcfe5ee44ec84bf42d` → TARGET `libs/reporting/report_source_policy_projection.py::build_policy_surface_quality_snapshot` (404 A/integration; newly owned by A)

**Exact original computation BODY to MOVE once:**

```python
def build_policy_surface_quality_snapshot(events_path: Path, reports_root: Path, day: str) -> Dict[str, Any]:
    try:
        runtime_health = build_phase_5_2_5_3_runtime_health(
            reports_root=reports_root,
            event_log_path=events_path,
            day=day,
            limit=500,
        )
    except FileNotFoundError:
        summary = build_policy_surface_quality_summary([])
        chart_summary = build_chart_structure_decision_hint_summary([])
        return {
            "summary": summary,
            "executive_summary": build_policy_surface_quality_executive_summary(summary),
            "chart_structure_summary": chart_summary,
            "chart_structure_executive_summary": build_chart_structure_decision_hint_executive_summary(chart_summary),
            "source": {
                "run_count": 0,
                "date": day,
                "source": "daily_monitor_artifacts",
                "notes": ["no_canonical_monitor_runs_found"],
            },
        }
    except Exception:
        summary = build_policy_surface_quality_summary([])
        chart_summary = build_chart_structure_decision_hint_summary([])
        return {
            "summary": summary,
            "executive_summary": build_policy_surface_quality_executive_summary(summary),
            "chart_structure_summary": chart_summary,
            "chart_structure_executive_summary": build_chart_structure_decision_hint_executive_summary(chart_summary),
            "source": {
                "run_count": 0,
                "date": day,
                "source": "daily_monitor_artifacts",
                "notes": ["policy_surface_quality_summary_unavailable"],
            },
        }

    summary = runtime_health.get("policy_surface_quality_summary")
    if not isinstance(summary, dict):
        summary = build_policy_surface_quality_summary([])
    chart_summary = runtime_health.get("chart_structure_decision_hint_summary")
    if not isinstance(chart_summary, dict):
        chart_summary = build_chart_structure_decision_hint_summary([])
    return {
        "summary": dict(summary),
        "executive_summary": build_policy_surface_quality_executive_summary(summary),
        "chart_structure_summary": dict(chart_summary),
        "chart_structure_executive_summary": build_chart_structure_decision_hint_executive_summary(chart_summary),
        "source": {
            "run_count": int(runtime_health.get("run_count") or 0),
            "date": day,
            "source": "daily_monitor_artifacts",
            "health_schema_version": str(runtime_health.get("schema_version") or ""),
        },
    }
```

**Implementation / wrapper / monkeypatch:** facade.build_phase_5_2_5_3_runtime_health and summary/chart helpers at call time; fake-only return values; NEVER invoke live health, Step5C or real paths. Preserve exact-signature thin SOURCE wrapper and output/error parity. Move the complete BODY (not a duplicate) to the new TARGET function; preserve SOURCE's original public signature/annotations/docstring and replace its BODY with a thin delegation wrapper. TARGET must not import SOURCE. Resolve referenced SOURCE helpers/globals through `facade=sys.modules[__name__]` (for symbol_trade_report use its existing `_r3_sys.modules[__name__]`) at call time; keep lazy iterator helper lookup at iteration time. Maintain exact output, exception order and original callers. No changes to any operational/real account files.

**Mandatory new normal targeted test:** `tests/test_p15_rf035_05h_a4_policy_surface_owner.py`. Input/expected: fake runtime_health summary run_count=2 => source.run_count=2; stub raises FileNotFoundError => source.notes=['no_canonical_monitor_runs_found']; generic Exception => ['policy_surface_quality_summary_unavailable']; MUST mock phase5 runtime health before invocation, no Step5C. Capture original behavior before MOVE and assert original-vs-Owner-vs-wrapper output/error parity and monkeypatch seams. Only fake/temp/controlled clock; do not invoke real data, health or network. `python -m py_compile libs/reporting/report_source_helpers.py libs/reporting/report_source_policy_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_05h_a4_policy_surface_owner.py` normal exit0, or exact reproducible stdlib normal smoke if pytest missing. Commit only code+test on A branch, normal push and refetch A remote HEAD/SOURCE/TARGET/TEST blobs; report G1/G2 evidence. If blocked record exact error/SHA and **continue A5**; do not end whole order.

## A5 — RF-035 | SOURCE `libs/reporting/report_source_helpers.py::build_commander_route_summary` blob `8471837632ec1c7659ba2cbcfe5ee44ec84bf42d` → TARGET `libs/reporting/report_source_route_summary_projection.py::build_commander_route_summary` (404 A/integration; newly owned by A)

**Exact original computation BODY to MOVE once:**

```python
def build_commander_route_summary(
    *,
    reports_root: Path,
    day: str,
    day_rows: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    canonical_dir = reports_root / "canonical" / day
    canonical_by_run: Dict[str, Dict[str, Any]] = {}
    if canonical_dir.exists():
        for run_dir in sorted(canonical_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            commander = read_json(run_dir / "commander.json")
            if not commander:
                continue
            row = _commander_route_from_payload(commander, artifact_path=str(run_dir / "commander.json"))
            if row.get("route_selected"):
                canonical_by_run[str(run_dir.name)] = row

    event_rows = day_rows or []
    event_by_run = _event_route_rows(event_rows)

    all_run_ids = set(canonical_by_run) | set(event_by_run)

    by_run: Dict[str, Dict[str, Any]] = {}
    route_selected_total: Counter[str] = Counter()
    strategy_generation_mode_total: Counter[str] = Counter()
    strategist_fallback_total = 0
    source_breakdown: Counter[str] = Counter()
    missing_count = 0

    for run_id in sorted(all_run_ids):
        selected = canonical_by_run.get(run_id)
        if not selected:
            selected = event_by_run.get(run_id)
        if not selected or not str(selected.get("route_selected") or "").strip():
            missing_count += 1
            continue
        by_run[run_id] = dict(selected)
        route_selected_total[str(selected.get("route_selected"))] += 1
        mode = str(selected.get("strategy_generation_mode") or "").strip()
        if mode:
            strategy_generation_mode_total[mode] += 1
        if bool(selected.get("strategist_fallback_used")):
            strategist_fallback_total += 1
        source_breakdown[str(selected.get("route_source") or "unknown")] += 1

    return {
        "route_source": "canonical_commander_preferred",
        "route_source_run_count": int(len(by_run)),
        "route_source_missing_count": int(missing_count),
        "route_selected_total": dict(route_selected_total),
        "strategy_generation_mode_total": dict(strategy_generation_mode_total),
        "strategist_fallback_total": int(strategist_fallback_total),
        "route_source_breakdown": dict(source_breakdown),
        "by_run": by_run,
    }
```

**Implementation / wrapper / monkeypatch:** facade.read_json, _commander_route_from_payload, _event_route_rows, Counter at call time; tmp canonical only; canonical preference and counters. Preserve exact-signature thin SOURCE wrapper and output/error parity. Move the complete BODY (not a duplicate) to the new TARGET function; preserve SOURCE's original public signature/annotations/docstring and replace its BODY with a thin delegation wrapper. TARGET must not import SOURCE. Resolve referenced SOURCE helpers/globals through `facade=sys.modules[__name__]` (for symbol_trade_report use its existing `_r3_sys.modules[__name__]`) at call time; keep lazy iterator helper lookup at iteration time. Maintain exact output, exception order and original callers. No changes to any operational/real account files.

**Mandatory new normal targeted test:** `tests/test_p15_rf035_05h_a5_commander_route_summary_owner.py`. Input/expected: tmp canonical/day/r1/commander.json route=direct; fake events r1 fallback and r2 indirect => r1 canonical wins; run_count=2, route totals direct=1,indirect=1; patched facade.read_json/_event_route_rows parity. Capture original behavior before MOVE and assert original-vs-Owner-vs-wrapper output/error parity and monkeypatch seams. Only fake/temp/controlled clock; do not invoke real data, health or network. `python -m py_compile libs/reporting/report_source_helpers.py libs/reporting/report_source_route_summary_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_05h_a5_commander_route_summary_owner.py` normal exit0, or exact reproducible stdlib normal smoke if pytest missing. Commit only code+test on A branch, normal push and refetch A remote HEAD/SOURCE/TARGET/TEST blobs; report G1/G2 evidence. If blocked record exact error/SHA and **continue A6**; do not end whole order.

## A6 — RF-035 | SOURCE `libs/reporting/strategist_llm_summary.py::build_strategist_llm_summary_payload` blob `01e6ea1c6786a5f208d6b6afc6d12f18c8d40319` → TARGET `libs/reporting/strategist_llm_summary_payload_projection.py::build_strategist_llm_summary_payload` (404 A/integration; newly owned by A)

**Exact original computation BODY to MOVE once:**

```python
def build_strategist_llm_summary_payload(response_json_path: Path) -> Dict[str, Any]:
    source_path = Path(response_json_path)
    raw = json.loads(source_path.read_text(encoding="utf-8"))
    sidecar_meta = _read_json(source_path.with_name("meta.json"))
    payload = _parse_response_body(raw)
    canonical_path, canonical = _load_canonical_strategist(source_path)
    theme_strategy = _as_dict(payload.get("theme_strategy"))
    refresh_trace = _as_dict(payload.get("strategy_refresh_trace"))
    horizon = _as_dict(payload.get("strategy_horizon_feedback"))
    strategy_detail = _strategy_detail_from_sources(payload, canonical)
    stage_decision = _stage_decision_from_payload(payload, raw, sidecar_meta)
    stage_meta = _stage_meta(payload, raw, sidecar_meta)
    news_usage = _news_usage_from_canonical(canonical)
    market_regime_rail = _market_rail_from_canonical(canonical)
    news_quality = _news_quality_audit(canonical, news_usage)
    risk_off_exception_policy = _as_dict(canonical.get("risk_off_exception_policy")) or build_risk_off_exception_policy(
        market_regime_rail=market_regime_rail,
        news_quality=news_quality,
    )
    output_quality = _strategist_output_quality_audit(
        payload=payload,
        canonical=canonical,
        stage_decision=stage_decision,
        strategy_detail=strategy_detail,
        market_rail=market_regime_rail,
        news_quality=news_quality,
    )

    return {
        "schema_version": "strategist_llm_summary.v1",
        "artifact_type": "strategist_llm_summary",
        "source_response_json": str(source_path),
        "source_canonical_strategist_json": str(canonical_path) if canonical_path else "",
        "generated_at": _utc_now_iso(),
        "llm_meta": {
            "stage": _first_text("", raw.get("stage"), sidecar_meta.get("stage")),
            "stage_index": stage_meta.get("stage_index"),
            "stage_name": _text(stage_meta.get("stage_name"), ""),
            "call_kind": _text(stage_meta.get("call_kind"), ""),
            "stage_component": _text(stage_meta.get("stage_component"), ""),
            "provider": _first_text("", raw.get("provider"), sidecar_meta.get("provider")),
            "model": _first_text("", raw.get("model"), sidecar_meta.get("model")),
            "status": _first_text("", raw.get("status"), raw.get("llm_status"), sidecar_meta.get("status"), sidecar_meta.get("llm_status")),
            "reason": _first_text("", raw.get("reason"), sidecar_meta.get("reason")),
            "run_id": _first_text("", raw.get("run_id"), sidecar_meta.get("run_id")),
            "day": _first_text("", raw.get("day"), sidecar_meta.get("day")),
            "saved_at": _first_text("", raw.get("saved_at"), sidecar_meta.get("saved_at")),
            "repair_used": bool(raw.get("repair_used") or sidecar_meta.get("repair_used")),
            "profile_name": _first_text("", raw.get("llm_execution_profile_name"), sidecar_meta.get("llm_execution_profile_name")),
            "profile_source": _first_text("", raw.get("llm_execution_profile_source"), sidecar_meta.get("llm_execution_profile_source")),
        },
        "operator_readout": _operator_readout_clean(payload, stage_decision),
        "stage_decision": stage_decision,
        "strategy_frame": {
            "playbook": _text(payload.get("playbook")),
            "selected_themes": _as_list(payload.get("selected_themes")),
            "theme_selection_mode": _text(theme_strategy.get("selection_mode")),
            "fallback_reason": _text(theme_strategy.get("fallback_reason"), ""),
            "rationale": _text(payload.get("rationale"), ""),
        },
        "strategy_detail": strategy_detail,
        "policy_changes": {
            "playbook_action": _directive(payload, "playbook_action"),
            "entry_policy_action": _directive(payload, "entry_policy_action"),
            "monitor_focus_action": _directive(payload, "monitor_focus_action"),
            "selected_symbol_bias_action": _directive(payload, "selected_symbol_bias_action"),
            "refresh_action": _directive(payload, "refresh_action"),
        },
        "monitor_entry_policy": _as_dict(payload.get("monitor_entry_policy")),
        "memory_usage": _memory_usage_from_canonical(canonical),
        "news_usage": news_usage,
        "news_event_intelligence": _as_dict(
            payload.get("news_event_intelligence") or canonical.get("news_event_intelligence")
        ),
        "news_event_intelligence_usage": _as_dict(payload.get("news_event_intelligence_usage")),
        "market_regime_rail": market_regime_rail,
        "news_quality_audit": news_quality,
        "risk_off_exception_policy": risk_off_exception_policy,
        "risk_off_exception_conditions": _as_list(payload.get("risk_off_exception_conditions")),
        "strategist_output_quality_audit": output_quality,
        "strategy_refresh_trace": {
            "summary": _text(refresh_trace.get("summary"), ""),
            "bullets": _as_list(refresh_trace.get("bullets")),
            "stages": _as_list(refresh_trace.get("stages")),
        },
        "strategy_horizon_feedback": horizon,
    }
```

**Implementation / wrapper / monkeypatch:** facade.json.loads, _read_json, _parse_response_body, _load_canonical_strategist and all policy/render helpers at call time; fake tmp response; no LLM or network. Preserve exact-signature thin SOURCE wrapper and output/error parity. Move the complete BODY (not a duplicate) to the new TARGET function; preserve SOURCE's original public signature/annotations/docstring and replace its BODY with a thin delegation wrapper. TARGET must not import SOURCE. Resolve referenced SOURCE helpers/globals through `facade=sys.modules[__name__]` (for symbol_trade_report use its existing `_r3_sys.modules[__name__]`) at call time; keep lazy iterator helper lookup at iteration time. Maintain exact output, exception order and original callers. No changes to any operational/real account files.

**Mandatory new normal targeted test:** `tests/test_p15_rf035_05h_a6_strategist_payload_owner.py`. Input/expected: tmp response.json {'stage':'strategist','status':'ok'} and fake canonical/helper outputs => schema_version='strategist_llm_summary.v1', artifact_type='strategist_llm_summary', llm_meta.status='ok'; malformed JSON raises JSONDecodeError identically; no LLM/network. Capture original behavior before MOVE and assert original-vs-Owner-vs-wrapper output/error parity and monkeypatch seams. Only fake/temp/controlled clock; do not invoke real data, health or network. `python -m py_compile libs/reporting/strategist_llm_summary.py libs/reporting/strategist_llm_summary_payload_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_05h_a6_strategist_payload_owner.py` normal exit0, or exact reproducible stdlib normal smoke if pytest missing. Commit only code+test on A branch, normal push and refetch A remote HEAD/SOURCE/TARGET/TEST blobs; report G1/G2 evidence. If blocked record exact error/SHA and **continue A7**; do not end whole order.

## A7 — RF-035 | SOURCE `libs/reporting/market_regime_rail_review.py::classify_market_regime_rail` blob `cd659475acef1bcdf7301317f5c01ebfe29820c0` → TARGET `libs/reporting/market_regime_rail_classification_projection.py::classify_market_regime_rail` (404 A/integration)

**Exact computation BODY to MOVE:**

```python
def classify_market_regime_rail(snapshot: Mapping[str, Any]) -> Dict[str, Any]:
    if not bool(snapshot.get("available", True)) and not snapshot.get("schema_version"):
        return {
            "schema_version": "market_regime_rail_observation.v1",
            "behavior_effect": "evaluation_only",
            "available": False,
            "rail_id": "not_available",
            "rail_confidence": "none",
            "rationale": "macro snapshot unavailable",
            "market_inputs": {},
            "expected_tactical_behavior": [],
            "q8_review_focus": [],
        }

    korea = snapshot.get("korea_indices") if isinstance(snapshot.get("korea_indices"), Mapping) else {}
    sanity = korea_index_sanity(korea) if korea else {"status": "ok", "warning_count": 0, "warnings": [], "extreme_move_requires_confirmation": False}
    macro_moves = snapshot.get("macro_moves") if isinstance(snapshot.get("macro_moves"), Mapping) else {}
    global_sentiment = snapshot.get("global_sentiment") if isinstance(snapshot.get("global_sentiment"), Mapping) else {}

    inputs = {
        "kospi_pct": _change_pct(snapshot, "kospi"),
        "kosdaq_pct": _change_pct(snapshot, "kosdaq"),
        "kospi200_pct": _change_pct(snapshot, "kospi200"),
        "krx_night_futures_pct": _change_pct(snapshot, "krx_night_futures"),
        "breadth": _to_float(korea.get("breadth"), 0.0),
        "nasdaq_pct": _change_pct(snapshot, "nasdaq"),
        "sp500_pct": _change_pct(snapshot, "sp500"),
        "dxy_pct": _to_float(macro_moves.get("dxy_pct"), _to_float(_indicator(snapshot, "dxy").get("change_pct"), 0.0)),
        "usdkrw_pct": _to_float(_indicator(snapshot, "usdkrw").get("change_pct"), 0.0),
        "vix_level": _to_float(macro_moves.get("vix_level"), 0.0),
        "vix_pct": _to_float(macro_moves.get("vix_pct"), 0.0),
        "us_10y_delta": _to_float(_indicator(snapshot, "us_10y_yield").get("delta"), 0.0),
        "global_sentiment_score": _to_float(global_sentiment.get("score"), 0.0),
    }
    night = snapshot.get("krx_night_futures") if isinstance(snapshot.get("krx_night_futures"), Mapping) else {}
    inputs["krx_night_futures_status"] = str(night.get("status") or _indicator(snapshot, "krx_night_futures").get("status") or "")
    inputs["krx_night_futures_pressure"] = str(
        night.get("direction_pressure") or _indicator(snapshot, "krx_night_futures").get("direction_pressure") or ""
    )

    korea_weak = inputs["kosdaq_pct"] <= -1.0 or inputs["kospi_pct"] <= -0.7 or inputs["breadth"] <= -0.35
    night_gap_down = inputs["krx_night_futures_pct"] <= -1.0
    night_gap_up = inputs["krx_night_futures_pct"] >= 1.0
    us_tech_positive = inputs["nasdaq_pct"] >= 0.2 and inputs["sp500_pct"] >= 0.0
    fx_pressure = inputs["usdkrw_pct"] >= 0.4 or inputs["dxy_pct"] >= 0.2
    vix_pressure = inputs["vix_level"] >= 20.0 or inputs["vix_pct"] >= 8.0

    if night_gap_down:
        rail_id = "krx_night_futures_gap_down"
        confidence = "high" if inputs["krx_night_futures_pct"] <= -2.0 else "medium"
        behavior = [
            "treat pre-open derivatives pressure as broad gap-down risk",
            "require confirmed relative strength before entry",
            "keep cost-edge and volume confirmation strict",
            "compare blocked breakouts and reclaim setups against forward shadow outcomes",
        ]
        focus = ["breakout_not_ready", "below_vwap_reclaim_not_ready", "volume_confirmation_missing"]
        rationale = "KRX KOSPI200 night futures showed sharp negative pressure before or near the regular session."
    elif night_gap_up and not korea_weak:
        rail_id = "krx_night_futures_gap_up"
        confidence = "medium"
        behavior = [
            "watch opening momentum but avoid unconfirmed gap chase",
            "compare opening momentum probes against delayed pullback entries",
            "keep cost-edge active unless promoted policy says otherwise",
        ]
        focus = ["opening_momentum_probe", "breakout_not_ready", "pullback_not_mature"]
        rationale = "KRX KOSPI200 night futures showed positive pre-open derivatives pressure."
    elif us_tech_positive and korea_weak:
        rail_id = "us_tech_risk_on_korea_weak"
        confidence = "high" if inputs["breadth"] <= -0.45 or inputs["kosdaq_pct"] <= -1.5 else "medium"
        behavior = [
            "prefer confirmed relative-strength breakout or reclaim over broad pullback",
            "do not weaken cost-edge or volume confirmation globally",
            "review semiconductor and large-cap tech candidates against shadow breakout outcomes",
        ]
        focus = ["breakout_not_ready", "pullback_not_mature", "human_chart_sanity_guard_blocked"]
        rationale = "US technology risk appetite was positive while Korean breadth and KOSDAQ were weak."
    elif korea_weak and (fx_pressure or vix_pressure or inputs["global_sentiment_score"] < -0.2):
        rail_id = "risk_off_breadth_collapse"
        confidence = "high" if inputs["breadth"] <= -0.45 else "medium"
        behavior = [
            "avoid broad chase",
            "require strong relative strength before entry",
            "keep cost-edge and volume confirmation strict",
        ]
        focus = ["volume_confirmation_missing", "below_vwap_reclaim_not_ready", "breakout_not_ready"]
        rationale = "Korean market breadth was weak with macro pressure signals active."
    elif korea_weak:
        rail_id = "defensive_rotation"
        confidence = "medium"
        behavior = [
            "prefer defensive or isolated relative strength setups",
            "avoid weak-volume pullback chase",
            "measure opportunity cost of blocked breakouts",
        ]
        focus = ["breakout_not_ready", "pullback_not_mature"]
        rationale = "Domestic market was weak without enough global confirmation for full risk-off classification."
    elif us_tech_positive and not korea_weak:
        rail_id = "liquidity_leader_rotation"
        confidence = "medium"
        behavior = [
            "watch leader rotation and high-liquidity breakouts",
            "compare selected candidates against scanner top leaders",
            "keep cost-edge active",
        ]
        focus = ["breakout_not_ready", "below_vwap_reclaim_not_ready"]
        rationale = "US technology risk appetite was positive and domestic weakness was not dominant."
    else:
        rail_id = "macro_pressure_no_trade" if fx_pressure or vix_pressure else "neutral_observation"
        confidence = "low" if rail_id == "neutral_observation" else "medium"
        behavior = [
            "keep current gates unchanged",
            "collect Q8 shadow evidence before policy changes",
        ]
        focus = ["volume_confirmation_missing", "below_vwap_reclaim_not_ready"]
        rationale = "No stronger market rail was identified from the latest macro snapshot."

    return {
        "schema_version": "market_regime_rail_observation.v1",
        "behavior_effect": "evaluation_only",
        "available": True,
        "source": snapshot.get("path") or "macro_snapshot",
        "generated_at": snapshot.get("generated_at"),
        "rail_id": rail_id,
        "rail_confidence": confidence,
        "rationale": rationale,
        "market_inputs": inputs,
        "market_input_sanity": sanity,
        "expected_tactical_behavior": behavior,
        "q8_review_focus": focus,
        "secondary_flags": {
            "korea_weak": korea_weak,
            "night_gap_down": night_gap_down,
            "night_gap_up": night_gap_up,
            "us_tech_positive": us_tech_positive,
            "fx_pressure": fx_pressure,
            "vix_pressure": vix_pressure,
        },
    }
```

**Wrapper/callers/monkeypatch:** Preserve `classify_market_regime_rail(snapshot: Mapping[str,Any])->Dict[str,Any]` in SOURCE as thin wrapper; new TARGET owns all threshold/rail selection computation. Call-time `facade` resolves `korea_index_sanity`, `_change_pct`, `_to_float`, `_indicator`, `Mapping` and other globals; TARGET never imports SOURCE. Preserve exact thresholds, ordered branch precedence, confidence and output dictionary, `behavior_effect='evaluation_only'`. No policy/market action, Broker/Guard/Step5C/UEF changes.

**Mandatory normal targeted:** `tests/test_p15_rf035_05h_a7_market_regime_classify_owner.py`. Input `{'available':False}` => rail_id='not_available', available=False, behavior_effect='evaluation_only'; fake krx_night_futures_pct=-2.1 with helper fakes => rail_id='krx_night_futures_gap_down', confidence='high'; fake neutral => rail_id='neutral_observation'. Compare original-vs-Owner-vs-wrapper full dict, patched helper and invalid input exception parity; pure dictionaries only. `python -m py_compile libs/reporting/market_regime_rail_review.py libs/reporting/market_regime_rail_classification_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_05h_a7_market_regime_classify_owner.py` normal exit0 (or exact stdlib smoke). Push A code/test and re-fetch blobs. If blocked **continue A8**.

## A8 — RF-035 | SOURCE `libs/reporting/strategist_llm_summary.py::generate_strategist_llm_summary` blob `01e6ea1c6786a5f208d6b6afc6d12f18c8d40319` → TARGET `libs/reporting/strategist_llm_summary_writer_projection.py::generate_strategist_llm_summary` (404 A/integration)

**Exact existing report-artifact BODY to MOVE (only fake/tmp effect in tests):**

```python
def generate_strategist_llm_summary(response_json_path: Path) -> Tuple[Path, Path, Dict[str, Any]]:
    source_path = Path(response_json_path)
    payload = build_strategist_llm_summary_payload(source_path)
    md_path = source_path.with_name("strategist_summary.md")
    json_path = source_path.with_name("strategist_summary.json")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_strategist_llm_summary_markdown(payload), encoding="utf-8-sig", newline="\n")
    return md_path, json_path, payload
```

**Wrapper/callers/monkeypatch:** Keep original signature and return tuple in SOURCE; thin delegate to new Owner with `facade=sys.modules[__name__]`. In TARGET use `facade.Path`, `facade.build_strategist_llm_summary_payload`, `facade.render_strategist_llm_summary_markdown`, `facade.json.dumps` at call time; do not import SOURCE or duplicate JSON/Markdown writer body. Preserve output basenames, UTF-8 JSON indent=2/ensure_ascii=False, UTF-8-SIG Markdown newline='\\n', exception behavior and return path types. No real report dirs, network, LLM or operational writes; fake tmp_path only. Existing active render wrapper is already moved: DO NOT re-move its shadowed old definition.

**Mandatory normal targeted:** `tests/test_p15_rf035_05h_a8_strategist_writer_owner.py`. Use tmp response.json and monkeypatch facade payload builder to `{'schema_version':'strategist_llm_summary.v1','llm_meta':{'status':'ok'}}`, renderer to '# stub\\n'; expected output paths `strategist_summary.md/json` in tmp dir, JSON payload round-trip equality, Markdown starts UTF-8 BOM and exact newline; wrapper vs Owner return and byte parity; patched builder ValueError propagates and writes nothing. `python -m py_compile libs/reporting/strategist_llm_summary.py libs/reporting/strategist_llm_summary_writer_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_05h_a8_strategist_writer_owner.py` normal exit0 (or exact stdlib smoke). Commit/push A code/test and re-fetch remote HEAD/SOURCE/TARGET/TEST blobs; if blocked report exact blocker and retain local-only, do not invent G1/G2.
## RESERVE_NOT_VERIFIED — A 0/6 after promotion, design backlog (NOT executable)

The six previous VERIFIED reserves R1–R6 are now mandatory A1–A6 and **must not be counted as reserves**. Two further independent functions A7/A8 were verified for this order. No six additional unmoved, exclusive, safe pure/report-only functions have been fully proven on the latest A remote, so **RESERVE_VERIFIED=0/6**; do not fabricate candidates or reissue KEEP, previously moved, shadowed definitions, or already assigned functions. Next C03 must inspect other RF-035 reporting sources, actual active function BODY and target 404, caller/monkeypatch/IO and negative fixture, and publish 6 VERIFIED design-only reserves; effectful `generate_symbol_trade_report`, `generate_daily_report`, `generate_trade_explain_report`, `generate_market_regime_rail_review`, `generate_agent_pipeline_trace_report` remain **NOT_VERIFIED**, not executable reserves until protected write/real-mode impact and target ownership are proven. Do not ask A to choose work from this paragraph.

## Required #11 report and push verification

Report `ORDER_ID=A-20261031-05 | CANONICAL_HEAD | ORDER_BLOB_SHA | A_REMOTE_SHA_BEFORE→AFTER | A1..A8 IMPLEMENTED/REMOTE_DONE/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED | exact normal test command/exit and SOURCE/TARGET/TEST blobs | FIRST_BLOCKER | NEXT`. START/END/ELAPSED only if directly measured, never infer from comments. Commit only code/tests to A branch, normal push and refetch. C03 publication itself is **not** code G1/G2/G3 or RF DONE. If any item fails, continue next safe one; no D00/RF/queue reading or autonomous task selection.
