# Agentra P1.5 FAST-3 — C01 B-20261030-21 B0 carryover + NEW 9 verified BODY MOVEs

**C03 supply 2026-10-30 21h KST.** Prior C01 blob `18938c819b18d6eb9161ee92da3fc84b0cd549a5` had B0 RF-065 PENDING and B1–B9 RF-063. B1–B9 have only LOCAL commit `6aa9a0a0` (#12 `6521349981`) with py_compile exit0/isolated normal smoke exit0, **terminal HTTPS PUSH_BLOCKED**; they are NOT remote G1, do not claim REMOTE_DONE, and DO NOT recreate their local tree or overwrite them. Remote B ref still `8fe73f486c4b8ac43f75558b19c403bbe29f6b50` and remote old audit source blob `1df9947a268f31d73639542db4a09eaac6e172b6` contains bodies, target 404. B0 remains PENDING and is copied in full below. New B1–B9 here are DIFFERENT verified RF-063 source functions from `scripts/diagnostics/check_trade_report_runtime_regression.py` blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` and `scripts/diagnostics/query_strategist_llm_events.py` blob `c45516931dcb365c8283c596345233458c10a41f`; 6 new target modules are 404 on B/integration preflight. They do not touch the old local-only audit source/targets. RF-063/B owner exclusive, A read-only.

**Required delivery recovery before/alongside tasks:** preserve existing local `6aa9a0a0` commit and its exact reviewed tree; attempt approved GitHub blob→tree→commit→lease-protected B ref update ONLY if all original changed blobs/tree and parent are verifiably identical. Re-fetch remote ref/tree after update and report exact SHA equivalence. If that reviewed local tree is unavailable or cannot be proven, mark `PUSH_BLOCKED`, record remote `8fe73f486c4b8ac43f75558b19c403bbe29f6b50`, local `6aa9a0a0`, exact terminal error `fatal: could not read Username for 'https://github.com': No such device or address`, and continue B0 and B1–B9 in a separate safe checkout/branch state without overwriting the preserved local commit. Never claim local-only delivery, never force push or write another branch. No probe commits.

**Execution contract:** Actor Codex B, only `work/p15-b-operator-structure-20261022`, canonical `integration/p1.5`. Before each item `git fetch origin`, record canonical HEAD, C01 blob, remote B HEAD, local HEAD. Use prepared `.venv/bin/python`/pytest when present. Preserve exact SOURCE calculation BODY by MOVING to single TARGET; old SOURCE exact-signature thin wrapper with call-time facade monkeypatch, no reverse import/duplicate body. Each item normal targeted exit0 (or stdlib normal smoke when pytest missing); -O/full peer/hosted CI NOT required by FAST-3. Commit code/test only and verify remote ref/blob/tree after every push. If push credential failure, preserve local commit and continue next disjoint safe task. Do not touch D00/C01/C02/RF/queue/STATUS/HANDOFF/C04/C05, A branch, main, live data/logs/orders/Broker/Guard/Step5C/UEF/RunLab; command builders are **argv construction only, NEVER EXECUTE**. All tasks mandatory, no self-selection. Report each B0–B9, remote/local status, exact normal exit, FIRST_BLOCKER/NEXT in Issue #12. C04 integrates; C05 alone judges G1/G2/G3 and RF DONE.

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


### B1 — RF-063 | `scripts/diagnostics/check_trade_report_runtime_regression.py::_read_json` SOURCE blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` → `scripts/diagnostics/trade_artifact_validation_read_projection.py::_read_json`

**Exact SOURCE BODY to MOVE (not duplicate):**
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

**Wrapper/monkeypatch:** SOURCE keeps exact signature/annotations/defaults and becomes a thin delegate. TARGET takes keyword-only `facade` only if needed, does NOT import SOURCE, does not copy body into SOURCE. facade.json.loads at call time; preserve path.exists guard and broad Exception; read temp only. For multi-function targets add without overwriting earlier functions. Preserve caller exception/format/order/identity.

**Normal targeted fixture:** `tests/test_p15_rf063_21h_read_json_owner.py`: tmp_path missing→{}; valid dict→same; JSON list/invalid→{}; monkeypatch facade.json.loads to raise→{}. Golden baseline before MOVE vs wrapper vs target, negative/monkeypatch, isolated fake/tmp only. `.venv/bin/python -m py_compile scripts/diagnostics/check_trade_report_runtime_regression.py scripts/diagnostics/trade_artifact_validation_read_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_21h_read_json_owner.py` normal exit0 required, or reproducible stdlib smoke when pytest absent, record actual exit. Commit only code/test; normal push B branch; refetch remote ref and exact SOURCE/TARGET/TEST blobs/tree after push. On failure preserve local SHA/error and continue next safe disjoint item.

### B2 — RF-063 | `scripts/diagnostics/check_trade_report_runtime_regression.py::_resolve_trade_context` SOURCE blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` → `scripts/diagnostics/trade_artifact_context_projection.py::_resolve_trade_context`

**Exact SOURCE BODY to MOVE (not duplicate):**
```python
def _resolve_trade_context(reports_root: Path, day: str, trade_id: str) -> Dict[str, Any]:
    trade_paths = trade_artifact_paths(reports_root, day, trade_id)
    entry_payload = _read_json(trade_paths["entry_json"])
    exit_payload = _read_json(trade_paths["exit_json"])
    hold_payload = _read_json(trade_paths["hold_json"])
    lifecycle_bundle = _read_json(trade_paths["lifecycle_bundle_json"])
    story_input = _read_json(trade_paths["ai_trade_report_input_json"])
    report = _read_json(trade_paths["ai_trade_report_json"])
    provenance = _read_json(trade_paths["trade_provenance_json"])
    health = _read_json(trade_paths["trade_health_json"])
    entry_run_id = str(
        entry_payload.get("run_id")
        or ((lifecycle_bundle.get("lifecycle") or {}).get("entry") or {}).get("run_id")
        or ""
    ).strip()
    exit_run_id = str(
        exit_payload.get("run_id")
        or ((lifecycle_bundle.get("lifecycle") or {}).get("exit") or {}).get("run_id")
        or lifecycle_bundle.get("run_id")
        or ""
    ).strip()
    target_run_id = exit_run_id or entry_run_id
    return {
        "trade_paths": trade_paths,
        "entry_payload": entry_payload,
        "exit_payload": exit_payload,
        "hold_payload": hold_payload,
        "lifecycle_bundle": lifecycle_bundle,
        "story_input": story_input,
        "report": report,
        "provenance": provenance,
        "health": health,
        "entry_run_id": entry_run_id,
        "exit_run_id": exit_run_id,
        "target_run_id": target_run_id,
    }
```

**Wrapper/monkeypatch:** SOURCE keeps exact signature/annotations/defaults and becomes a thin delegate. TARGET takes keyword-only `facade` only if needed, does NOT import SOURCE, does not copy body into SOURCE. facade.trade_artifact_paths and facade._read_json at call time; preserve ordered keys and run_id fallbacks; never actual broker/production report read. For multi-function targets add without overwriting earlier functions. Preserve caller exception/format/order/identity.

**Normal targeted fixture:** `tests/test_p15_rf063_21h_resolve_trade_context_owner.py`: patch facade.trade_artifact_paths with temp paths and facade._read_json fake; empty payloads→target_run_id ''; exit run_id preferred to entry; compare dict/keys. Golden baseline before MOVE vs wrapper vs target, negative/monkeypatch, isolated fake/tmp only. `.venv/bin/python -m py_compile scripts/diagnostics/check_trade_report_runtime_regression.py scripts/diagnostics/trade_artifact_context_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_21h_resolve_trade_context_owner.py` normal exit0 required, or reproducible stdlib smoke when pytest absent, record actual exit. Commit only code/test; normal push B branch; refetch remote ref and exact SOURCE/TARGET/TEST blobs/tree after push. On failure preserve local SHA/error and continue next safe disjoint item.

### B3 — RF-063 | `scripts/diagnostics/check_trade_report_runtime_regression.py::_build_bundle_repair_command` SOURCE blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` → `scripts/diagnostics/trade_artifact_command_projection.py::_build_bundle_repair_command`

**Exact SOURCE BODY to MOVE (not duplicate):**
```python
def _build_bundle_repair_command(
    *,
    day: str,
    target_run_id: str,
    role: str,
    max_runs: int,
    event_log_path: str,
    evidence_log_path: str,
    report_dir: str,
    reports_root: str,
) -> List[str]:
    return [
        sys.executable,
        str(ROOT / "scripts" / "run_live_execution_bundle_report.py"),
        "--day",
        str(day),
        "--target-run-id",
        str(target_run_id),
        "--max-runs",
        str(max_runs),
        "--event-log-path",
        str(event_log_path),
        "--evidence-log-path",
        str(evidence_log_path),
        "--report-dir",
        str(report_dir),
        "--reports-root",
        str(reports_root),
        "--no-trade-report-ai",
        "--role",
        str(role),
        "--json",
    ]
```

**Wrapper/monkeypatch:** SOURCE keeps exact signature/annotations/defaults and becomes a thin delegate. TARGET takes keyword-only `facade` only if needed, does NOT import SOURCE, does not copy body into SOURCE. facade.sys.executable and facade.ROOT at call time; construct argv ONLY; NEVER execute subprocess or generated command. For multi-function targets add without overwriting earlier functions. Preserve caller exception/format/order/identity.

**Normal targeted fixture:** `tests/test_p15_rf063_21h_build_bundle_repair_command_owner.py`: day='2026-10-30', target_run_id='r', role='manual', max_runs=2, fake paths→argv includes '--no-trade-report-ai','--json' in exact order; patch facade.ROOT. Golden baseline before MOVE vs wrapper vs target, negative/monkeypatch, isolated fake/tmp only. `.venv/bin/python -m py_compile scripts/diagnostics/check_trade_report_runtime_regression.py scripts/diagnostics/trade_artifact_command_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_21h_build_bundle_repair_command_owner.py` normal exit0 required, or reproducible stdlib smoke when pytest absent, record actual exit. Commit only code/test; normal push B branch; refetch remote ref and exact SOURCE/TARGET/TEST blobs/tree after push. On failure preserve local SHA/error and continue next safe disjoint item.

### B4 — RF-063 | `scripts/diagnostics/check_trade_report_runtime_regression.py::_build_report_regen_command` SOURCE blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` → `scripts/diagnostics/trade_artifact_command_projection.py::_build_report_regen_command`

**Exact SOURCE BODY to MOVE (not duplicate):**
```python
def _build_report_regen_command(
    *,
    day: str,
    trade_id: str,
    reports_root: str,
    local_debug: bool,
    hard_timeout_sec: Optional[float],
    with_llm: bool = False,
) -> List[str]:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "run_ai_trade_report_batch.py"),
        "--day",
        str(day),
        "--trade-id",
        str(trade_id),
        "--reports-root",
        str(reports_root),
        "--retry-max",
        "0",
        "--json",
    ]
    if hard_timeout_sec is not None:
        command.extend(["--hard-timeout-sec", str(hard_timeout_sec)])
    if local_debug:
        command.append("--local-debug")
    elif with_llm:
        command.append("--with-llm")
    return command
```

**Wrapper/monkeypatch:** SOURCE keeps exact signature/annotations/defaults and becomes a thin delegate. TARGET takes keyword-only `facade` only if needed, does NOT import SOURCE, does not copy body into SOURCE. facade.sys.executable and facade.ROOT at call time; preserve local_debug over with_llm priority, hard timeout, argv order; NEVER execute. For multi-function targets add without overwriting earlier functions. Preserve caller exception/format/order/identity.

**Normal targeted fixture:** `tests/test_p15_rf063_21h_build_report_regen_command_owner.py`: local_debug=False,with_llm=False→no '--with-llm'; local_debug=True→'--local-debug'; timeout=1→'--hard-timeout-sec','1'; no subprocess. Golden baseline before MOVE vs wrapper vs target, negative/monkeypatch, isolated fake/tmp only. `.venv/bin/python -m py_compile scripts/diagnostics/check_trade_report_runtime_regression.py scripts/diagnostics/trade_artifact_command_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_21h_build_report_regen_command_owner.py` normal exit0 required, or reproducible stdlib smoke when pytest absent, record actual exit. Commit only code/test; normal push B branch; refetch remote ref and exact SOURCE/TARGET/TEST blobs/tree after push. On failure preserve local SHA/error and continue next safe disjoint item.

### B5 — RF-063 | `scripts/diagnostics/check_trade_report_runtime_regression.py::validate_trade_artifact_chain` SOURCE blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` → `scripts/diagnostics/trade_artifact_validation_evidence_projection.py::validate_trade_artifact_chain`

**Exact SOURCE BODY to MOVE (not duplicate):**
```python
def validate_trade_artifact_chain(reports_root: Path, day: str, trade_id: str) -> Dict[str, Any]:
    ctx = _resolve_trade_context(reports_root, day, trade_id)
    trade_paths = ctx["trade_paths"]
    entry_payload = ctx["entry_payload"]
    exit_payload = ctx["exit_payload"]
    hold_payload = ctx["hold_payload"]
    lifecycle_bundle = ctx["lifecycle_bundle"]
    story_input = ctx["story_input"]
    report = ctx["report"]
    provenance = ctx["provenance"]
    health = ctx["health"]

    failures: List[str] = []
    warnings: List[str] = []
    artifact_exists = {
        "entry_json": trade_paths["entry_json"].exists(),
        "hold_json": trade_paths["hold_json"].exists(),
        "exit_json": trade_paths["exit_json"].exists(),
        "lifecycle_bundle_json": trade_paths["lifecycle_bundle_json"].exists(),
        "ai_trade_report_input_json": trade_paths["ai_trade_report_input_json"].exists(),
        "ai_trade_report_json": trade_paths["ai_trade_report_json"].exists(),
        "ai_trade_report_md": trade_paths["ai_trade_report_md"].exists(),
    }
    for key, exists in artifact_exists.items():
        if not exists:
            failures.append(f"missing_artifact:{key}")

    authoritative_status = str(
        provenance.get("lifecycle_status")
        or health.get("lifecycle_status")
        or lifecycle_bundle.get("trade_lifecycle_status")
        or lifecycle_bundle.get("status")
        or ""
    ).strip().lower()
    closed_trade = _is_closed_trade(
        {
            **lifecycle_bundle,
            "trade_lifecycle_status": authoritative_status or lifecycle_bundle.get("trade_lifecycle_status"),
        },
        exit_payload,
    )
    entry_evidence = _has_substantive_entry_evidence(entry_payload)
    exit_evidence = _has_substantive_exit_evidence(exit_payload)
    linked_run_ids = [
        str(value or "").strip()
        for value in list(lifecycle_bundle.get("linked_run_ids") or [])
        if str(value or "").strip()
    ]
    selected_rank = _safe_int(
        story_input.get("selected_rank"),
        _safe_int(((story_input.get("scanner_selection_trace") or {}) if isinstance(story_input.get("scanner_selection_trace"), dict) else {}).get("selected_rank")),
    )
    candidate_count = _safe_int(
        story_input.get("candidate_count"),
        _safe_int(((story_input.get("scanner_selection_trace") or {}) if isinstance(story_input.get("scanner_selection_trace"), dict) else {}).get("candidate_count")),
    )
    selected_symbol = str(
        story_input.get("selected_symbol")
        or ((story_input.get("scanner_selection_trace") or {}) if isinstance(story_input.get("scanner_selection_trace"), dict) else {}).get("selected_symbol")
        or story_input.get("symbol")
        or ""
    ).strip()
    hold_duration = str(hold_payload.get("hold_duration") or lifecycle_bundle.get("hold_duration") or story_input.get("hold_duration") or "").strip()
    hold_duration_sec = hold_payload.get("hold_duration_sec")
    if hold_duration_sec in (None, ""):
        hold_duration_sec = lifecycle_bundle.get("hold_duration_sec")
    if hold_duration_sec in (None, ""):
        hold_duration_sec = story_input.get("hold_duration_sec")
    hold_duration_sec_int = _safe_int(hold_duration_sec, default=-1)
    story_status = str(story_input.get("status") or "").strip().lower()
    story_action = str(story_input.get("action") or "").strip().upper()

    if closed_trade and not str(exit_payload.get("run_id") or "").strip():
        failures.append("closed_trade_missing_exit_run_id")
    if closed_trade and not linked_run_ids:
        failures.append("closed_trade_missing_linked_run_ids")
    if closed_trade and entry_evidence and not str(entry_payload.get("run_id") or "").strip():
        failures.append("closed_trade_missing_entry_run_id")
    if closed_trade and entry_evidence and not str(entry_payload.get("ts") or "").strip():
        failures.append("closed_trade_missing_entry_ts")
    if closed_trade and not str(exit_payload.get("ts") or "").strip():
        failures.append("closed_trade_missing_exit_ts")
    if closed_trade and entry_evidence:
        if hold_duration in {"", "00:00:00", "0초", "0.0m", "0m"}:
            failures.append("closed_trade_fake_or_missing_hold_duration")
        if hold_duration_sec_int == 0:
            failures.append("closed_trade_zero_hold_duration_sec")
    if closed_trade and selected_rank <= 0:
        failures.append("closed_trade_selected_rank_zero")
    if closed_trade and candidate_count <= 0:
        failures.append("closed_trade_candidate_count_zero")
    if authoritative_status and story_status and story_status != authoritative_status:
        failures.append("story_input_status_conflicts_with_authoritative_status")
    if authoritative_status == "open" and not exit_evidence and story_action == "SELL":
        failures.append("story_input_action_conflicts_with_open_trade")
    if selected_symbol and selected_symbol != str(story_input.get("symbol") or "").strip():
        failures.append("selected_symbol_mismatch_story_symbol")
    generation = report.get("generation") if isinstance(report.get("generation"), dict) else {}
    generation_status = str(generation.get("status") or "").strip().lower()
    if report and generation_status not in {"ok", "partial", "salvaged", "repaired"}:
        failures.append("ai_trade_report_generation_status_bad")
    if report and _section_provenance_all_fallback(report):
        failures.append("ai_trade_report_all_section_provenance_fallback")

    linkage = lifecycle_bundle.get("same_day_reporter_linkage") if isinstance(lifecycle_bundle.get("same_day_reporter_linkage"), dict) else {}
    if linkage:
        linkage_status = str(linkage.get("status") or "").strip().lower()
        json_path = str(linkage.get("reporter_analysis_json_path") or "").strip()
        md_path = str(linkage.get("reporter_analysis_md_path") or "").strip()
        if linkage_status == "missing" and (json_path or md_path):
            failures.append("reporter_linkage_missing_but_artifact_path_populated")

    trade_origin = str(provenance.get("trade_origin") or lifecycle_bundle.get("trade_origin") or "").strip()
    completeness = str(provenance.get("lifecycle_completeness") or lifecycle_bundle.get("lifecycle_completeness") or "").strip()
    if closed_trade and entry_evidence and trade_origin == "recovered_partial":
        warnings.append("trade_origin_is_recovered_partial_even_with_entry_evidence")
    if closed_trade and not entry_evidence and completeness != "partial":
        failures.append("thin_entry_evidence_not_marked_partial")

    return {
        "day": day,
        "trade_id": trade_id,
        "closed_trade": closed_trade,
        "authoritative_status": authoritative_status,
        "entry_run_id": str(entry_payload.get("run_id") or "").strip(),
        "exit_run_id": str(exit_payload.get("run_id") or "").strip(),
        "linked_run_ids": linked_run_ids,
        "selected_symbol": selected_symbol,
        "selected_rank": selected_rank,
        "candidate_count": candidate_count,
        "hold_duration": hold_duration,
        "hold_duration_sec": None if hold_duration_sec in (None, "") else hold_duration_sec_int,
        "trade_origin": trade_origin,
        "lifecycle_completeness": completeness,
        "artifact_exists": artifact_exists,
        "failures": failures,
        "warnings": warnings,
        "ok": len(failures) == 0,
    }
```

**Wrapper/monkeypatch:** SOURCE keeps exact signature/annotations/defaults and becomes a thin delegate. TARGET takes keyword-only `facade` only if needed, does NOT import SOURCE, does not copy body into SOURCE. facade._resolve_trade_context, _is_closed_trade, _has_substantive_entry_evidence, _has_substantive_exit_evidence, _safe_int, _section_provenance_all_fallback at call time; preserve failure order, output fields, no write/subprocess. For multi-function targets add without overwriting earlier functions. Preserve caller exception/format/order/identity.

**Normal targeted fixture:** `tests/test_p15_rf063_21h_validate_trade_artifact_chain_owner.py`: fake tmp context with all artifact paths missing→ordered missing_artifact failures; fully fake empty context yields ok=False; spy helper call; compare before/after entire dict. Golden baseline before MOVE vs wrapper vs target, negative/monkeypatch, isolated fake/tmp only. `.venv/bin/python -m py_compile scripts/diagnostics/check_trade_report_runtime_regression.py scripts/diagnostics/trade_artifact_validation_evidence_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_21h_validate_trade_artifact_chain_owner.py` normal exit0 required, or reproducible stdlib smoke when pytest absent, record actual exit. Commit only code/test; normal push B branch; refetch remote ref and exact SOURCE/TARGET/TEST blobs/tree after push. On failure preserve local SHA/error and continue next safe disjoint item.

### B6 — RF-063 | `scripts/diagnostics/check_trade_report_runtime_regression.py::_build_parser` SOURCE blob `3176dab6c01dda0e7edc24f5fed5ea65e83d8d0c` → `scripts/diagnostics/trade_artifact_validation_cli.py::_build_parser`

**Exact SOURCE BODY to MOVE (not duplicate):**
```python
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay and validate trade report runtime regression cases.")
    parser.add_argument("--reports-root", default="reports")
    parser.add_argument("--event-log-path", default="data/logs/events.jsonl")
    parser.add_argument("--evidence-log-path", default="data/evidence_ledger/events.jsonl")
    parser.add_argument("--report-dir", default="reports/dev/analysis/live_execution_bundles")
    parser.add_argument("--case", action="append", default=[], help="DAY:TRADE_ID[:RUN_ID]. Defaults to the golden trade matrix.")
    parser.add_argument("--role", default="manual_repair_bundle")
    parser.add_argument("--max-runs", type=int, default=200)
    parser.add_argument("--skip-repair", action="store_true")
    parser.add_argument("--skip-local-debug", action="store_true")
    parser.add_argument("--llm-acceptance", action="store_true")
    parser.add_argument("--llm-hard-timeout-sec", type=float, default=900.0)
    parser.add_argument("--json", action="store_true")
    return parser
```

**Wrapper/monkeypatch:** SOURCE keeps exact signature/annotations/defaults and becomes a thin delegate. TARGET takes keyword-only `facade` only if needed, does NOT import SOURCE, does not copy body into SOURCE. facade.argparse.ArgumentParser at call time if patched; preserve flags/defaults, never invoke main or repair. For multi-function targets add without overwriting earlier functions. Preserve caller exception/format/order/identity.

**Normal targeted fixture:** `tests/test_p15_rf063_21h_build_parser_owner.py`: parse_args([])→reports_root 'reports', max_runs 200, skip_repair False; ['--skip-repair','--json']→True; unknown→SystemExit(2). Golden baseline before MOVE vs wrapper vs target, negative/monkeypatch, isolated fake/tmp only. `.venv/bin/python -m py_compile scripts/diagnostics/check_trade_report_runtime_regression.py scripts/diagnostics/trade_artifact_validation_cli.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_21h_build_parser_owner.py` normal exit0 required, or reproducible stdlib smoke when pytest absent, record actual exit. Commit only code/test; normal push B branch; refetch remote ref and exact SOURCE/TARGET/TEST blobs/tree after push. On failure preserve local SHA/error and continue next safe disjoint item.

### B7 — RF-063 | `scripts/diagnostics/query_strategist_llm_events.py::_to_float` SOURCE blob `c45516931dcb365c8283c596345233458c10a41f` → `scripts/diagnostics/strategist_event_query_projection.py::_to_float`

**Exact SOURCE BODY to MOVE (not duplicate):**
```python
def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)
```

**Wrapper/monkeypatch:** SOURCE keeps exact signature/annotations/defaults and becomes a thin delegate. TARGET takes keyword-only `facade` only if needed, does NOT import SOURCE, does not copy body into SOURCE. pure; no facade; preserve broad Exception fallback float(default) and nan/inf handling. For multi-function targets add without overwriting earlier functions. Preserve caller exception/format/order/identity.

**Normal targeted fixture:** `tests/test_p15_rf063_21h_to_float_owner.py`: '2.5'→2.5; None default=3→3.0; invalid default='bad' raises ValueError; no external calls. Golden baseline before MOVE vs wrapper vs target, negative/monkeypatch, isolated fake/tmp only. `.venv/bin/python -m py_compile scripts/diagnostics/query_strategist_llm_events.py scripts/diagnostics/strategist_event_query_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_21h_to_float_owner.py` normal exit0 required, or reproducible stdlib smoke when pytest absent, record actual exit. Commit only code/test; normal push B branch; refetch remote ref and exact SOURCE/TARGET/TEST blobs/tree after push. On failure preserve local SHA/error and continue next safe disjoint item.

### B8 — RF-063 | `scripts/diagnostics/query_strategist_llm_events.py::_infer_call_kind` SOURCE blob `c45516931dcb365c8283c596345233458c10a41f` → `scripts/diagnostics/strategist_event_query_projection.py::_infer_call_kind`

**Exact SOURCE BODY to MOVE (not duplicate):**
```python
def _infer_call_kind(payload: Dict[str, Any]) -> str:
    explicit = str(payload.get("call_kind") or "").strip()
    if explicit:
        return explicit
    schema_version = str(payload.get("schema_version") or "").strip().lower()
    prompt_version = str(payload.get("prompt_version") or "").strip().lower()
    intent_action = str(payload.get("intent_action") or "").strip().upper()
    error_type = str(payload.get("error_type") or "").strip()
    if schema_version == "strategist_output.v1" or prompt_version.startswith("m31-strategic-frame"):
        return "strategic_frame"
    if schema_version == "intent.v1" or intent_action in {"BUY", "SELL", "NOOP"}:
        return "legacy_trade_intent"
    if error_type == "StrategistBlocked":
        return "blocked_legacy_runtime"
    return "unknown"
```

**Wrapper/monkeypatch:** SOURCE keeps exact signature/annotations/defaults and becomes a thin delegate. TARGET takes keyword-only `facade` only if needed, does NOT import SOURCE, does not copy body into SOURCE. pure; preserve explicit call_kind precedence, schema/prompt/intent/error priority, string conversions. For multi-function targets add without overwriting earlier functions. Preserve caller exception/format/order/identity.

**Normal targeted fixture:** `tests/test_p15_rf063_21h_infer_call_kind_owner.py`: {'call_kind':'custom'}→custom; {'schema_version':'strategist_output.v1'}→strategic_frame; {'intent_action':'BUY'}→legacy_trade_intent; {}→unknown. Golden baseline before MOVE vs wrapper vs target, negative/monkeypatch, isolated fake/tmp only. `.venv/bin/python -m py_compile scripts/diagnostics/query_strategist_llm_events.py scripts/diagnostics/strategist_event_query_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_21h_infer_call_kind_owner.py` normal exit0 required, or reproducible stdlib smoke when pytest absent, record actual exit. Commit only code/test; normal push B branch; refetch remote ref and exact SOURCE/TARGET/TEST blobs/tree after push. On failure preserve local SHA/error and continue next safe disjoint item.

### B9 — RF-063 | `scripts/diagnostics/query_strategist_llm_events.py::_filtered_events` SOURCE blob `c45516931dcb365c8283c596345233458c10a41f` → `scripts/diagnostics/strategist_event_query_projection.py::_filtered_events`

**Exact SOURCE BODY to MOVE (not duplicate):**
```python
def _filtered_events(
    rows: List[Dict[str, Any]],
    *,
    run_id: str = "",
    day: str = "",
    only_failures: bool = False,
    only_nonzero_news: bool = False,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for rec in rows:
        if rec.get("stage") != "strategist_llm" or rec.get("event") != "result":
            continue
        if day and not str(rec.get("ts_kst") or rec.get("ts") or "").startswith(day):
            continue
        if run_id and str(rec.get("run_id") or "") != run_id:
            continue
        p = rec.get("payload") if isinstance(rec.get("payload"), dict) else {}
        if only_failures and bool(p.get("ok")):
            continue
        if only_nonzero_news and abs(_to_float(p.get("context_symbol_sentiment_score"), 0.0)) <= 1e-12:
            continue
        out.append(rec)
    return out
```

**Wrapper/monkeypatch:** SOURCE keeps exact signature/annotations/defaults and becomes a thin delegate. TARGET takes keyword-only `facade` only if needed, does NOT import SOURCE, does not copy body into SOURCE. facade._to_float at call time; preserve row identity, filter order and only_nonzero_news epsilon 1e-12. For multi-function targets add without overwriting earlier functions. Preserve caller exception/format/order/identity.

**Normal targeted fixture:** `tests/test_p15_rf063_21h_filtered_events_owner.py`: rows with strategist_llm result and other stages→only result; day/run_id exact filter; only_failures removes ok; only_nonzero_news filters zero; monkeypatch facade._to_float spy. Golden baseline before MOVE vs wrapper vs target, negative/monkeypatch, isolated fake/tmp only. `.venv/bin/python -m py_compile scripts/diagnostics/query_strategist_llm_events.py scripts/diagnostics/strategist_event_query_projection.py`; `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_p15_rf063_21h_filtered_events_owner.py` normal exit0 required, or reproducible stdlib smoke when pytest absent, record actual exit. Commit only code/test; normal push B branch; refetch remote ref and exact SOURCE/TARGET/TEST blobs/tree after push. On failure preserve local SHA/error and continue next safe disjoint item.

## VERIFIED future reserve — 6/6, not executable by Actor

At B `8fe73f486c4b8ac43f75558b19c403bbe29f6b50`, `scripts/diagnostics/check_reports_trades_health.py` source blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` has six inspected non-wrapper bodies; three proposed target paths 404 on B/integration. Tests are design hypotheses NOT_RUN; revalidate before next C03 issue.

- R1 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_read_json` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_read_projection.py::_read_json`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: missing tmp→{}; valid dict→dict; malformed→{}; facade.json.loads. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**
- R2 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_iter_trade_dirs` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_read_projection.py::_iter_trade_dirs`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: tmp reports/trades/day nested dirs→sorted; facade._iter_trade_dirs_under_day; no production root. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**
- R3 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_artifact_path` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_read_projection.py::_artifact_path`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: tmp path first exists→first; none→first candidate; no write. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**
- R4 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_issue` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_issue_projection.py::_issue`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: fake severity/trade/path→exact seven-key dict; pure. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**
- R5 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_ai_trade_report_is_complete` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_read_projection.py::_ai_trade_report_is_complete`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: fake tmp report with required dict sections→True; missing→False; facade._artifact_path/_read_json. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**
- R6 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_build_parser` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_cli.py::_build_parser`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: parse_args([]) defaults; '--day' filter; unknown→SystemExit(2); no main. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**

## Final B report

Report real START_KST/END_KST/ELAPSED (no estimate), canonical/order/B remote and local SHAs, old audit local-only recovery, B0 and NEW B1–B9 separately, normal test exits, remote SOURCE/TARGET/TEST blobs and exact ref/tree after push, FIRST_BLOCKER/NEXT. C03 supply is not code G1/G2/G3 or RF DONE.
