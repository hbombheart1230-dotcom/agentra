# Agentra P1.5 FAST-3 — C01 B-20261030-20 CARRYOVER B0 + NEW 9 verified BODY MOVEs

**C03 supply 2026-10-30 20h KST.** Prior order blob `af8b3c4ee2608a4fb1ceb46f33166b1c97864432` B1–B6 and B8 were delivered via approved exact-tree path at B HEAD `8fe73f486c4b8ac43f75558b19c403bbe29f6b50` (#12 6520528480); source `scripts/research/run_phase5_validation_bundle.py` blob `aaa29ba0fb9739e3f10eab1a99e97f24360c4fdd` now thin wrappers for those 7. Their tests are NOT all pytest-verified (only recorded stdlib smoke); do not count same-SHA retests as new MOVE. Old B7 remains PENDING, retained as B0 below. **Nine newly assigned independent RF-063 bodies** are from `scripts/diagnostics/check_audit_trail_completeness.py` B/integration blob `1df9947a268f31d73639542db4a09eaac6e172b6`; five new TARGETs 404 on B/integration. B owner exclusive; A read-only. Total executable queue=10 (1 carryover + 9 new), do not drop B0.

**Execution contract (all items, not optional):** Actor=Codex B; authorized branch=`work/p15-b-operator-structure-20261022`; canonical=`integration/p1.5`; source Git blob=`1df9947a268f31d73639542db4a09eaac6e172b6`; this order blob at run start must be fetched from canonical (previous blob `af8b3c4ee2608a4fb1ceb46f33166b1c97864432` is replaced). Before EACH item: `git fetch origin`, record remote canonical SHA, remote actor SHA, local HEAD, and order blob; use prepared `.venv/bin/python` and pytest when available. Work only in own code and new test files; never write D00/C01/C02/RF/queue/STATUS/HANDOFF/C04/C05, another branch, main, or live operational files. Use one isolated fake/tmp fixture, no network/order/Broker/Guard/Step5C/UEF/RunLab effects. Actual original BODY must be removed from SOURCE and moved into the single TARGET owner, leaving the original exact signature/annotations/defaults/docstring as thin delegation wrapper. Preserve call-time module monkeypatch via `facade=sys.modules[__name__]` (import `sys as _p15_sys` or `sys` already present); target never imports SOURCE, never duplicates BODY or mutates global state. Keep caller public signatures/outputs/identity/exception/order/format unchanged. Each item: pre-move golden output and error, post-move source wrapper and target equality, negative and monkeypatch fixture; `.venv/bin/python -m py_compile SOURCE TARGET`; `.venv/bin/python -m pytest -q -p no:cacheprovider EXACT_TEST` normal exit0 (stdlib normal smoke only when pytest absent), record real exit. FAST-3 G2 does not require -O/full peer/hosted CI. Commit code+targeted tests only, push actor branch normally, refetch remote ref and exact SOURCE/TARGET/TEST blob/tree after every push. HTTPS credential error blocks PUSH only: preserve local commit, approved GitHub exact-tree path only if full reviewed tree/ref equivalence proven; else LOCAL_ONLY, continue next safe non-overwriting item. No probe commits, no force push. Each blocked item is item-local; continue all remaining safe tasks. C04 integrates; C05 alone judges G1/G2/G3/RF DONE.

### B0 — **CARRYOVER, NOT NEW** RF-065, former B7 still PENDING

At B HEAD `8fe73f486c4b8ac43f75558b19c403bbe29f6b50`, SOURCE `scripts/research/run_phase5_validation_bundle.py::_render_bundle_markdown` blob `aaa29ba0fb9739e3f10eab1a99e97f24360c4fdd` L60, TARGET `scripts/research/phase5_validation_markdown.py::_render_bundle_markdown` 404. Previous B1–B6+B8 already REMOTE_DONE, do not retest/reimplement. Preserve this **single incomplete B7** while issuing nine new RF-063 items; execute B0 first, then B1–B9, without cancellation of in-flight work. Exact calculation BODY to MOVE, including bytes/order/float formatting and exceptions:
```python
def _render_bundle_markdown(payload: Dict[str, Any], *, repo_root: Path) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
    trade_health = artifacts.get("trade_health") if isinstance(artifacts.get("trade_health"), dict) else {}
    symbol_reports = artifacts.get("symbol_reports") if isinstance(artifacts.get("symbol_reports"), list) else []
    latest_runs = artifacts.get("latest_canonical_runs") if isinstance(artifacts.get("latest_canonical_runs"), list) else []
    policy_surface = (
        artifacts.get("policy_surface_quality")
        if isinstance(artifacts.get("policy_surface_quality"), dict)
        else {}
    )
    policy_surface_summary = (
        policy_surface.get("summary")
        if isinstance(policy_surface.get("summary"), dict)
        else {}
    )
    policy_surface_exec = (
        policy_surface.get("executive_summary")
        if isinstance(policy_surface.get("executive_summary"), dict)
        else {}
    )
    policy_surface_source = (
        policy_surface.get("source")
        if isinstance(policy_surface.get("source"), dict)
        else {}
    )
    chart_structure_guard = (
        artifacts.get("chart_structure_decision_hint")
        if isinstance(artifacts.get("chart_structure_decision_hint"), dict)
        else {}
    )
    chart_structure_guard_summary = (
        chart_structure_guard.get("summary")
        if isinstance(chart_structure_guard.get("summary"), dict)
        else {}
    )
    chart_structure_guard_exec = (
        chart_structure_guard.get("executive_summary")
        if isinstance(chart_structure_guard.get("executive_summary"), dict)
        else {}
    )
    chart_structure_guard_source = (
        chart_structure_guard.get("source")
        if isinstance(chart_structure_guard.get("source"), dict)
        else {}
    )
    chart_structure_guard_examples = (
        chart_structure_guard_summary.get("applied_examples")
        if isinstance(chart_structure_guard_summary.get("applied_examples"), list)
        else []
    )

    lines: List[str] = [
        f"# Phase 5 Validation Bundle ({payload.get('day')})",
        "",
        "## Summary",
        "",
        f"- daily_report_generated: **{bool(summary.get('daily_report_generated'))}**",
        f"- operator_daily_summary_generated: **{bool(summary.get('operator_daily_summary_generated'))}**",
        f"- trade_health_ok: **{bool(summary.get('trade_health_ok'))}**",
        f"- symbol_report_count: **{int(summary.get('symbol_report_count') or 0)}**",
        f"- latest_canonical_run_id: `{summary.get('latest_canonical_run_id') or ''}`",
        "",
        "## Daily Surfaces",
        "",
    ]

    daily = artifacts.get("daily_report") if isinstance(artifacts.get("daily_report"), dict) else {}
    operator = artifacts.get("operator_daily_summary") if isinstance(artifacts.get("operator_daily_summary"), dict) else {}
    lines += [
        f"- daily_report_json: `{daily.get('json_path') or ''}`",
        f"- daily_report_md: `{daily.get('md_path') or ''}`",
        f"- operator_daily_summary_json: `{operator.get('json_path') or ''}`",
        f"- operator_daily_summary_md: `{operator.get('md_path') or ''}`",
        "",
        "## Policy Surface Executive Summary",
        "",
        f"- status: **{str(policy_surface_exec.get('status') or 'unknown').upper()}**",
        f"- headline: {str(policy_surface_exec.get('headline') or 'Policy surface unknown')}",
        "",
        "## Policy Surface Quality",
        "",
        f"- schema_available_rate: **{float(policy_surface_summary.get('schema_available_rate') or 0.0):.4f}**",
        f"- normalized_policy_rate: **{float(policy_surface_summary.get('normalized_policy_rate') or 0.0):.4f}**",
        f"- invalid_spec_rate: **{float(policy_surface_summary.get('invalid_spec_rate') or 0.0):.4f}**",
        f"- total_invalid_specs: **{int(policy_surface_summary.get('total_invalid_specs') or 0)}**",
        f"- run_count: **{int(policy_surface_source.get('run_count') or 0)}**",
        f"- source: `{policy_surface_source.get('source') or ''}`",
        "",
        "## Chart Structure Decision Hint Executive Summary",
        "",
        f"- status: **{str(chart_structure_guard_exec.get('status') or 'unknown').upper()}**",
        f"- headline: {str(chart_structure_guard_exec.get('headline') or 'Chart structure guard unknown')}",
        "",
        "## Chart Structure Decision Hint",
        "",
        f"- available_run_count: **{int(chart_structure_guard_summary.get('available_run_count') or 0)}**",
        f"- applied_count: **{int(chart_structure_guard_summary.get('applied_count') or 0)}**",
        f"- applied_rate: **{float(chart_structure_guard_summary.get('applied_rate') or 0.0):.4f}**",
        f"- top_blocking_features: `{json.dumps(chart_structure_guard_summary.get('top_blocking_features') or [], ensure_ascii=False)}`",
        f"- source: `{chart_structure_guard_source.get('source') or ''}`",
        "",
        "## Trade / Report Health",
        "",
        f"- trade_dir_count: **{int(trade_health.get('trade_dir_count') or 0)}**",
        f"- severity_counts: `{json.dumps(trade_health.get('severity_counts') or {}, ensure_ascii=False)}`",
        f"- issue_counts: `{json.dumps(trade_health.get('issue_counts') or {}, ensure_ascii=False)}`",
        "",
        "## Symbol Reports",
        "",
    ]
    if chart_structure_guard_examples:
        lines += ["## Chart Structure Decision Hint Applied Examples", ""]
        for example in chart_structure_guard_examples[:3]:
            if not isinstance(example, dict):
                continue
            lines.append(
                f"- `{example.get('run_id') or '-'}` "
                f"[{str(example.get('entry_style') or '-').upper()}] "
                f"{example.get('reason_transition') or '-'} "
                f"blockers=`{json.dumps(example.get('blocking_features') or [], ensure_ascii=False)}`"
            )
        lines.append("")
    if symbol_reports:
        for row in symbol_reports:
            lines.append(
                f"- `{row.get('symbol')}`: json=`{row.get('json_path')}` md=`{row.get('md_path')}`"
            )
    else:
        lines.append("- (none)")

    decision_story = artifacts.get("decision_story") if isinstance(artifacts.get("decision_story"), dict) else {}
    run_cards = artifacts.get("run_cards") if isinstance(artifacts.get("run_cards"), dict) else {}
    trade_explain = artifacts.get("trade_explain") if isinstance(artifacts.get("trade_explain"), dict) else {}
    pipeline_trace = artifacts.get("pipeline_trace") if isinstance(artifacts.get("pipeline_trace"), dict) else {}
    lines += [
        "",
        "## Inspection Reports",
        "",
        f"- decision_story_md: `{decision_story.get('md_path') or ''}`",
        f"- run_cards_md: `{run_cards.get('md_path') or ''}`",
        f"- trade_explain_json: `{trade_explain.get('json_path') or ''}`",
        f"- trade_explain_md: `{trade_explain.get('md_path') or ''}`",
        f"- pipeline_trace_json: `{pipeline_trace.get('json_path') or ''}`",
        f"- pipeline_trace_md: `{pipeline_trace.get('md_path') or ''}`",
        "",
        "## Latest Canonical Runs",
        "",
    ]
    if latest_runs:
        for row in latest_runs:
            lines.append(
                f"- `{row.get('run_id')}`: commander=`{row.get('commander_json_path')}` monitor=`{row.get('monitor_json_path')}`"
            )
    else:
        lines.append("- (none)")

    issues = trade_health.get("issues") if isinstance(trade_health.get("issues"), list) else []
    lines += ["", "## Top Issues", ""]
    if issues:
        for issue in issues[:10]:
            lines.append(
                f"- [{issue.get('severity')}] `{issue.get('trade_id')}` `{issue.get('component')}` `{issue.get('code')}` - {issue.get('message')}"
            )
            lines.append(f"  path: `{issue.get('path')}`")
    else:
        lines.append("- (none)")

    lines += [
        "",
        "## Notes",
        "",
        "- This bundle is deterministic/read-only. It does not change runtime behavior.",
        "- It is intended to make report quality, schema linkage, and artifact paths easy to inspect by eye.",
        f"- repo_root: `{_safe_rel(repo_root, repo_root) or '.'}`",
        "",
    ]
    return "\n".join(lines)
```

Keep SOURCE original `def _render_bundle_markdown(payload: Dict[str, Any], *, repo_root: Path) -> str` as thin delegate `return phase5_markdown._render_bundle_markdown(payload, repo_root=repo_root, facade=sys.modules[__name__])`; import `from scripts.research import phase5_validation_markdown as phase5_markdown`; TARGET uses `facade.json.dumps` and `facade._safe_rel` at call time, no reverse import. Test `tests/test_p15_rf065_phase5_markdown_owner.py` fake payload {}→heading '# Phase 5 Validation Bundle (None)' and symbol count 0, {'day':'2026-10-30','summary':{'symbol_report_count':2}}→heading and count 2, full fake nested payload→byte-identical before/after, bad numeric summary count→same ValueError. Run py_compile, normal scoped pytest or stdlib smoke if unavailable, commit/push only code+test, exact remote ref/blob. On blocked record preserved local SHA/error, proceed B1 without overwriting B0 local work.


### B1 — RF-063 | `scripts/diagnostics/check_audit_trail_completeness.py::_to_epoch` (current blob `1df9947a268f31d73639542db4a09eaac6e172b6`, L15) → `scripts/diagnostics/audit_trail_time_projection.py::_to_epoch`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _to_epoch(ts: Any) -> Optional[int]:
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return int(ts)
    s = str(ts).strip()
    if not s:
        return None
    try:
        return int(float(s))
    except Exception:
        pass
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return None
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_to_epoch` to `scripts/diagnostics/audit_trail_time_projection.py`; facade.datetime/timezone at call time; numeric int(ts), ISO Z and naive UTC conversion unchanged. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf063_audit_to_epoch_owner.py`: None/''→None; 0→0; '1970-01-01T00:00:00Z'→0; 'bad'→None. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_audit_to_epoch_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### B2 — RF-063 | `scripts/diagnostics/check_audit_trail_completeness.py::_utc_day` (current blob `1df9947a268f31d73639542db4a09eaac6e172b6`, L38) → `scripts/diagnostics/audit_trail_time_projection.py::_utc_day`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _utc_day(ts: Any) -> str:
    epoch = _to_epoch(ts)
    if epoch is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_utc_day` to `scripts/diagnostics/audit_trail_time_projection.py`; facade._to_epoch/datetime/timezone at call time; fake clock only, never wall-clock assertion. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf063_audit_utc_day_owner.py`: 0→'1970-01-01'; None with patched datetime.now→'2030-01-02'; _to_epoch spy. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_audit_utc_day_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### B3 — RF-063 | `scripts/diagnostics/check_audit_trail_completeness.py::_extract_ts` (current blob `1df9947a268f31d73639542db4a09eaac6e172b6`, L45) → `scripts/diagnostics/audit_trail_decision_projection.py::_extract_ts`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _extract_ts(row: Dict[str, Any]) -> Any:
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    return row.get("ts") or payload.get("ts")
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_extract_ts` to `scripts/diagnostics/audit_trail_decision_projection.py`; dict-only nested payload, truthiness fallback; do not treat numeric 0 as valid primary. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf063_audit_extract_ts_owner.py`: {'ts':0,'payload':{'ts':42}}→42; {'ts':'abc'}→'abc'; missing→None. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_audit_extract_ts_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### B4 — RF-063 | `scripts/diagnostics/check_audit_trail_completeness.py::_extract_decision_action` (current blob `1df9947a268f31d73639542db4a09eaac6e172b6`, L68) → `scripts/diagnostics/audit_trail_decision_projection.py::_extract_decision_action`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _extract_decision_action(row: Dict[str, Any]) -> str:
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    packet = payload.get("decision_packet") if isinstance(payload.get("decision_packet"), dict) else {}
    intent = packet.get("intent") if isinstance(packet.get("intent"), dict) else {}
    action = intent.get("action") or payload.get("action") or payload.get("intent")
    return str(action or "").strip().upper()
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_extract_decision_action` to `scripts/diagnostics/audit_trail_decision_projection.py`; nested decision_packet.intent.action then payload.action/intent; str.strip.upper unchanged. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf063_audit_extract_decision_action_owner.py`: nested BUY→'BUY'; payload.action='sell'→'SELL'; missing→''; invalid payload ignored. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_audit_extract_decision_action_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### B5 — RF-063 | `scripts/diagnostics/check_audit_trail_completeness.py::_extract_allowed` (current blob `1df9947a268f31d73639542db4a09eaac6e172b6`, L76) → `scripts/diagnostics/audit_trail_decision_projection.py::_extract_allowed`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _extract_allowed(row: Dict[str, Any]) -> Optional[bool]:
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    v = payload.get("allowed")
    if isinstance(v, bool):
        return v
    return None
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_extract_allowed` to `scripts/diagnostics/audit_trail_decision_projection.py`; only isinstance(v,bool) returns value, no truthy coercion. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf063_audit_extract_allowed_owner.py`: payload.allowed True→True; False→False; 1/'true'/missing→None. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_audit_extract_allowed_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### B6 — RF-063 | `scripts/diagnostics/check_audit_trail_completeness.py::_latest_day` (current blob `1df9947a268f31d73639542db4a09eaac6e172b6`, L84) → `scripts/diagnostics/audit_trail_time_projection.py::_latest_day`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _latest_day(rows: List[Dict[str, Any]]) -> str:
    days = sorted({str(r.get("_day") or "") for r in rows if str(r.get("_day") or "").strip()})
    if days:
        return str(days[-1])
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_latest_day` to `scripts/diagnostics/audit_trail_time_projection.py`; sort set of nonblank _day, fallback facade.datetime.now(facade.timezone.utc). For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf063_audit_latest_day_owner.py`: unordered days 10-29,10-30→'2026-10-30'; [] fake clock→'2030-01-02'. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_audit_latest_day_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### B7 — RF-063 | `scripts/diagnostics/check_audit_trail_completeness.py::_iter_rows` (current blob `1df9947a268f31d73639542db4a09eaac6e172b6`, L50) → `scripts/diagnostics/audit_trail_read_projection.py::_iter_rows`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _iter_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception:
                continue
            if isinstance(obj, dict):
                out.append(obj)
    return out
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_iter_rows` to `scripts/diagnostics/audit_trail_read_projection.py`; facade.json.loads at invocation, open UTF-8 read-only, blank/malformed/list skip; open exceptions propagate. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf063_audit_iter_rows_owner.py`: missing temp JSONL→[]; dict/blank/invalid/list/dict→two dicts in order; spy loads; no production file. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_audit_iter_rows_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### B8 — RF-063 | `scripts/diagnostics/check_audit_trail_completeness.py::_build_markdown` (current blob `1df9947a268f31d73639542db4a09eaac6e172b6`, L212) → `scripts/diagnostics/audit_trail_markdown.py::_build_markdown`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _build_markdown(*, day: str, out: Dict[str, Any]) -> str:
    anomalies = out.get("anomaly_examples") if isinstance(out.get("anomaly_examples"), dict) else {}
    stage_event_total = out.get("stage_event_total") if isinstance(out.get("stage_event_total"), dict) else {}
    lines = [
        f"# Audit Trail Completeness ({day})",
        "",
        f"- ok: **{bool(out.get('ok'))}**",
        f"- events: **{int(out.get('events') or 0)}**",
        f"- runs: **{int(out.get('run_total') or 0)}**",
        f"- actionable_decision_run_total: **{int(out.get('actionable_decision_run_total') or 0)}**",
        f"- linked_complete_run_total: **{int(out.get('linked_complete_run_total') or 0)}**",
        f"- link_success_rate: **{float(out.get('link_success_rate') or 0.0):.2%}**",
        "",
        "## Anomaly Totals",
        "",
        f"- missing_execution_start_total: {int(out.get('missing_execution_start_total') or 0)}",
        f"- missing_execution_resolution_total: {int(out.get('missing_execution_resolution_total') or 0)}",
        f"- missing_execution_payload_total: {int(out.get('missing_execution_payload_total') or 0)}",
        f"- missing_terminal_event_total: {int(out.get('missing_terminal_event_total') or 0)}",
        f"- orphan_execution_run_total: {int(out.get('orphan_execution_run_total') or 0)}",
        "",
        "## execute_from_packet stage_event_total",
        "",
    ]

    for k in ("start", "verdict", "execution", "degrade_policy_block", "end", "error"):
        lines.append(f"- {k}: {int(stage_event_total.get(k) or 0)}")

    lines += ["", "## Anomaly Examples", ""]
    for key in (
        "missing_execution_start",
        "missing_execution_resolution",
        "missing_execution_payload",
        "missing_terminal_event",
        "orphan_execution",
    ):
        vals = anomalies.get(key) if isinstance(anomalies.get(key), list) else []
        if vals:
            lines.append(f"- {key}: {', '.join(str(x) for x in vals)}")
        else:
            lines.append(f"- {key}: (none)")

    failures = out.get("failures") if isinstance(out.get("failures"), list) else []
    lines += ["", "## Failures", ""]
    if failures:
        for x in failures:
            lines.append(f"- {x}")
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_build_markdown` to `scripts/diagnostics/audit_trail_markdown.py`; exact lines/header/section ordering, .2% formatting, anomaly keys, failures and trailing newline; no IO. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf063_audit_build_markdown_owner.py`: day='2026-10-30', out={'ok':True,'events':0}→starts '# Audit Trail Completeness (2026-10-30)\n'; contains '- ok: **True**'; anomalies none; bad numeric events→same ValueError. Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_audit_build_markdown_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.

### B9 — RF-063 | `scripts/diagnostics/check_audit_trail_completeness.py::_build_parser` (current blob `1df9947a268f31d73639542db4a09eaac6e172b6`, L265) → `scripts/diagnostics/audit_trail_cli_args.py::_build_parser`

**Exact SOURCE calculation BODY to MOVE (not to duplicate):**
```python
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Check intent->decision->execution audit trail completeness.")
    p.add_argument("--event-log-path", default="data/logs/events.jsonl")
    p.add_argument("--report-dir", default="reports/audit")
    p.add_argument("--day", default=None)
    p.add_argument("--require-actionable", action="store_true")
    p.add_argument("--json", action="store_true")
    return p
```

**Wrapper/monkeypatch:** SOURCE retains exact signature and delegates `_build_parser` to `scripts/diagnostics/audit_trail_cli_args.py`; facade.argparse.ArgumentParser at call time; only parser creation, NEVER main/argv effect. For globals/helpers referenced in old body, target uses `facade.NAME` at call time. Preserve any existing caller/exception/identity contract; no target→source import.

**Normal targeted fixture:** `tests/test_p15_rf063_audit_build_parser_owner.py`: parse_args([])→event_log_path 'data/logs/events.jsonl', report_dir 'reports/audit', json False; ['--day','2026-10-30','--json']→day and True; unknown option→SystemExit(2). Baseline vs source wrapper vs target, fake/temp only, no production effect. `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_audit_build_parser_owner.py` (normal exit must be recorded, not assumed); run `py_compile` first. Commit only SOURCE+TARGET+test; push and verify exact remote SHA/blob. On blocked, record first error/sha and proceed to next safe item.


## Verified future reserve — 6/6, not self-selected by Actor

At B `8fe73f48`, `scripts/diagnostics/check_trade_report_runtime_regression.py` blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c`, six distinct un-moved bodies inspected. All proposed targets absent on B and integration. These are read-only context, argument *construction only*, pure evidence, parser; **never execute generated commands/subprocess or real LLM/order/repair**. Tests are hypotheses, NOT_RUN. Recheck owner SHA/targets before future issue:
- R1 RF-063 `scripts/diagnostics/check_trade_report_runtime_regression.py::_read_json` blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` L40 → `scripts/diagnostics/trade_artifact_validation_read_projection.py::_read_json`; exact body 8 lines, missing tmp file→{}; dict→dict; invalid/list→{}; facade.json.loads; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.
- R2 RF-063 `scripts/diagnostics/check_trade_report_runtime_regression.py::_resolve_trade_context` blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` L90 → `scripts/diagnostics/trade_artifact_context_projection.py::_resolve_trade_context`; exact body 36 lines, fake trade_artifact_paths temp files; missing→empty dict payloads/run_id ''; facade.trade_artifact_paths/_read_json; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.
- R3 RF-063 `scripts/diagnostics/check_trade_report_runtime_regression.py::_build_bundle_repair_command` blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` L164 → `scripts/diagnostics/trade_artifact_command_projection.py::_build_bundle_repair_command`; exact body 33 lines, fake day/run/paths yields ordered argv with --no-trade-report-ai and --json; NEVER execute command; facade.sys.executable/ROOT; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.
- R4 RF-063 `scripts/diagnostics/check_trade_report_runtime_regression.py::_build_report_regen_command` blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` L199 → `scripts/diagnostics/trade_artifact_command_projection.py::_build_report_regen_command`; exact body 29 lines, with_llm False and local_debug False→no --with-llm; local_debug True→--local-debug; timeout1→--hard-timeout-sec 1; no execution; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.
- R5 RF-063 `scripts/diagnostics/check_trade_report_runtime_regression.py::validate_trade_artifact_chain` blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` L230 → `scripts/diagnostics/trade_artifact_validation_evidence_projection.py::validate_trade_artifact_chain`; exact body 139 lines, fake temp path dicts missing→ordered missing_artifact failures; no production reads; facade._resolve_trade_context and predicate helpers; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.
- R6 RF-063 `scripts/diagnostics/check_trade_report_runtime_regression.py::_build_parser` blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` L371 → `scripts/diagnostics/trade_artifact_validation_cli.py::_build_parser`; exact body 15 lines, parse_args([]) defaults reports_root reports, max_runs 200; --skip-repair True; no execution; only fake/temp/side-effect-free owner projection, verify current blob and TARGET 404 before future C03 issue.

## Final B report

Issue #12: real START_KST/END_KST/ELAPSED, canonical/order/B before→after SHA, B0 and B1–B9 separately MOVE/REMOTE_DONE/BLOCKED, source/owner/test blobs, normal targeted exit and push ref/blob equivalence, FIRST_BLOCKER/NEXT. Local-only is not delivered. No C03 code G1/G2/G3 or RF DONE claim.
