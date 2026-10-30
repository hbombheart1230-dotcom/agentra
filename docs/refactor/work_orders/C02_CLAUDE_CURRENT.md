# Agentra P1.5 FAST-3 — C02 A-20261031-01 | NEW 8 RF-035 actual SOURCE BODY MOVEs

**Authoritative preflight:** integration HEAD `ffd3ab0d41ce9037e80e1504fa27b78d9cf8a32d`; A remote HEAD `78662483e7e50a7445b4a18f5979b55c82bd74c9`; OLD_C02_BLOB `f48f7859ee0cd8ee8ceac9110a2426217ec23875`. #11 comment 6526411008 reports previous A1–A8 REMOTE_DONE with 40 normal PASS; A remote exact HEAD confirmed. Prior SOURCE bodies are thin wrappers; **do not reassign/retest them**. This is new order A-20261031-01, not code G1/G2/G3.

**Exclusive Owner:** RF-035, Claude A only. SOURCE `libs/reporting/daily_report_runtime/markdown.py` current A/integration blob `8755975bc5d78e26b48c36179556011498a476d9` (confirmed identical); 8 unique non-wrapper functions below. Seven new target MODULE paths (A/integration 404 verified), with two distinct functions sharing `markdown_operator_projection.py`. Target functions are absent. B owns none of these. Preserve source and target signatures/ordering/exception and call-time monkeypatch behavior.

**Single-file executable contract:** Read only THIS C02 plus named code/test paths; do not read D00, RF, queues, C03, prior orders or choose tasks. Pin fresh canonical HEAD, C02 blob, A remote HEAD and SOURCE blob before editing; if changed, check actual SOURCE/TARGET and avoid overwrite/duplicate. Do ALL A1–A8, independent item by item, even if earlier item blocked. Work only on `work/p15-a-reporter-pure-20261021` code/test. MOVE the exact function calculation BODY to one new Owner, not copy; leave exact original signature, keyword-only args, annotation and docstring as thin source wrapper. Add import alias of target to source and `import sys` only where needed; use `facade=sys.modules[__name__]` passed to target as keyword-only `facade` for listed monkeypatch seams, replacing module globals in moved BODY with `facade.X` at call time. No reverse imports or duplicate body. No actual daily report generation, broker API, live filesystem, real orders, Guard/Step5C/UEF, RunLab or production writes. All tests use fake dict/tmp_path, and compare original baseline behavior to Owner and wrapper (normal/negative/patch).

**Each item G2/G1:** Run `python -m py_compile` on source+target, then its **new targeted normal pytest** (`python -m pytest -q -p no:cacheprovider <testpath>`; use `.venv/bin/python` if available). If pytest unavailable, run reproducible stdlib normal smoke with exact command and exit, NOT py_compile alone. `-O`, full peer, hosted CI not mandatory. Commit ONLY this SOURCE+new TARGET+new scoped test; normal push A; re-fetch A remote ref and exact SOURCE/TARGET/TEST blobs. If push credentials fail, preserve LOCAL_ONLY, mark PUSH_BLOCKED, continue next safe item without force push/unreviewed tree reconstruction. A/B source/target collision, changed blob, effect boundary => item BLOCKED and continue next. C04 handles integration, C05 G1/G2/G3/DONE.

## A1 — RF-035 | SOURCE `libs/reporting/daily_report_runtime/markdown.py::render_operator_summary_snapshot` L14 blob `8755975bc5d78e26b48c36179556011498a476d9` → TARGET `libs/reporting/daily_report_runtime/markdown_snapshot_projection.py::render_operator_summary_snapshot` (new Owner, verified 404)

**Exact SOURCE calculation BODY to MOVE:**
```python
def render_operator_summary_snapshot(
    operator_summary_snapshot: Dict[str, Any],
    *,
    include_system_status: bool,
) -> List[str]:
    executive = (
        operator_summary_snapshot.get("executive_summary")
        if isinstance(operator_summary_snapshot.get("executive_summary"), dict)
        else {}
    )
    if not executive.get("summary_lines"):
        return []

    lines = ["", "## Operator Summary Snapshot", ""]
    if include_system_status and executive.get("system_status"):
        lines.append(f"- system_status: **{executive['system_status']}**")
    for line in executive.get("summary_lines") or []:
        lines.append(f"- {line}")
    return lines
```

**Wrapper/callers/monkeypatch:** none; preserve keyword-only include_system_status. Source function becomes thin delegating wrapper; preserve existing call sites and exact return/exception, bytes and ordering. This is read-only Markdown/projection; any protected effect remains forbidden.

**NEW targeted normal test:** `tests/test_p15_rf035_01h_a1_render_operator_summary_snapshot_owner.py`. Fixture and expected: include_system_status=True with executive_summary.summary_lines=['ok'],system_status='healthy' => header, status and '- ok'; False omits status; no summary_lines => []. Pin golden original before change and compare Owner+wrapper, negative and patch seam, with fake/tmp only.

`python -m py_compile libs/reporting/daily_report_runtime/markdown.py libs/reporting/daily_report_runtime/markdown_snapshot_projection.py` then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_01h_a1_render_operator_summary_snapshot_owner.py` (normal exit0 or exact stdlib smoke); scoped code/test commit + normal A push + remote ref/blob re-fetch. If item BLOCKED record exact SHA/error and **continue A2**.

## A2 — RF-035 | SOURCE `libs/reporting/daily_report_runtime/markdown.py::render_route_and_narrative_sections` L35 blob `8755975bc5d78e26b48c36179556011498a476d9` → TARGET `libs/reporting/daily_report_runtime/markdown_route_projection.py::render_route_and_narrative_sections` (new Owner, verified 404)

**Exact SOURCE calculation BODY to MOVE:**
```python
def render_route_and_narrative_sections(payload: Dict[str, Any]) -> List[str]:
    route_summary = payload.get("route_summary") if isinstance(payload.get("route_summary"), dict) else {}
    narrative_policy = (
        payload.get("narrative_axis_policy")
        if isinstance(payload.get("narrative_axis_policy"), dict)
        else narrative_axis_policy()
    )
    return [
        "",
        "## Route Provenance",
        "",
        f"- route_source: `{route_summary.get('route_source') or '-'}`",
        f"- route_source_run_count: **{int(route_summary.get('route_source_run_count') or 0)}**",
        f"- route_source_missing_count: **{int(route_summary.get('route_source_missing_count') or 0)}**",
        f"- route_source_breakdown: `{json.dumps(route_summary.get('route_source_breakdown') or {}, ensure_ascii=False)}`",
        f"- route_selected_total: `{json.dumps(route_summary.get('route_selected_total') or {}, ensure_ascii=False)}`",
        "",
        "## Narrative Axis Policy",
        "",
        f"- entry_primary_for: `{narrative_policy.get('entry_primary_for') or []}`",
        f"- exit_primary_for: `{narrative_policy.get('exit_primary_for') or []}`",
        f"- mixed_only_for_ambiguous_cases: **{bool(narrative_policy.get('mixed_only_for_ambiguous_cases'))}**",
        f"- runtime_semantics_unchanged: **{bool(narrative_policy.get('runtime_semantics_unchanged'))}**",
    ]
```

**Wrapper/callers/monkeypatch:** facade.json.dumps and facade.narrative_axis_policy resolved at call time. Source function becomes thin delegating wrapper; preserve existing call sites and exact return/exception, bytes and ordering. This is read-only Markdown/projection; any protected effect remains forbidden.

**NEW targeted normal test:** `tests/test_p15_rf035_01h_a2_render_route_and_narrative_sections_owner.py`. Fixture and expected: route_summary={'route_source':'sim','route_source_run_count':1,'route_source_missing_count':0}, narrative_axis_policy={'entry_primary_for':['entry'],'exit_primary_for':[]} => '# Route Provenance', source sim, count 1 and policy lines; missing policy calls patched facade.narrative_axis_policy. Pin golden original before change and compare Owner+wrapper, negative and patch seam, with fake/tmp only.

`python -m py_compile libs/reporting/daily_report_runtime/markdown.py libs/reporting/daily_report_runtime/markdown_route_projection.py` then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_01h_a2_render_route_and_narrative_sections_owner.py` (normal exit0 or exact stdlib smoke); scoped code/test commit + normal A push + remote ref/blob re-fetch. If item BLOCKED record exact SHA/error and **continue A3**.

## A3 — RF-035 | SOURCE `libs/reporting/daily_report_runtime/markdown.py::render_trade_report_integrity` L61 blob `8755975bc5d78e26b48c36179556011498a476d9` → TARGET `libs/reporting/daily_report_runtime/markdown_integrity_projection.py::render_trade_report_integrity` (new Owner, verified 404)

**Exact SOURCE calculation BODY to MOVE:**
```python
def render_trade_report_integrity(payload: Dict[str, Any]) -> List[str]:
    integrity = payload.get("trade_report_integrity") if isinstance(payload.get("trade_report_integrity"), dict) else {}
    if not integrity:
        return []
    missing = integrity.get("missing") if isinstance(integrity.get("missing"), list) else []
    broker_closed_report_open = (
        integrity.get("broker_closed_report_open")
        if isinstance(integrity.get("broker_closed_report_open"), list)
        else []
    )
    lines = [
        "",
        "## Trade Report Integrity",
        "",
        f"- status: **{str(integrity.get('status') or 'unknown').upper()}**",
        f"- expected_trade_count: **{int(integrity.get('expected_trade_count') or 0)}**",
        f"- summary_md_count: **{int(integrity.get('summary_md_count') or 0)}**",
        f"- summary_json_count: **{int(integrity.get('summary_json_count') or 0)}**",
        f"- summary_input_count: **{int(integrity.get('summary_input_count') or 0)}**",
        f"- missing_count: **{int(integrity.get('missing_count') or 0)}**",
        f"- broker_closed_report_open_count: **{int(integrity.get('broker_closed_report_open_count') or 0)}**",
    ]
    for row in broker_closed_report_open[:10]:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"- broker closed but report open `{row.get('trade_id') or '-'}` {row.get('symbol') or ''}: "
            f"status=`{row.get('lifecycle_status') or 'unknown'}`"
        )
    for row in missing[:10]:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"- missing `{row.get('trade_id') or '-'}` {row.get('symbol') or ''}: "
            f"`{json.dumps(row.get('missing') or [], ensure_ascii=False)}`"
        )
    return lines
```

**Wrapper/callers/monkeypatch:** facade.json.dumps resolved at call time. Source function becomes thin delegating wrapper; preserve existing call sites and exact return/exception, bytes and ordering. This is read-only Markdown/projection; any protected effect remains forbidden.

**NEW targeted normal test:** `tests/test_p15_rf035_01h_a3_render_trade_report_integrity_owner.py`. Fixture and expected: {} => []; {'trade_report_integrity':{'status':'missing_reports','missing_count':1,'missing':[{'trade_id':'T1','missing':['ai_trade_summary_md']}]}} => status MISSING_REPORTS and missing T1; non-dict rows ignored; malformed count raises same ValueError. Pin golden original before change and compare Owner+wrapper, negative and patch seam, with fake/tmp only.

`python -m py_compile libs/reporting/daily_report_runtime/markdown.py libs/reporting/daily_report_runtime/markdown_integrity_projection.py` then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_01h_a3_render_trade_report_integrity_owner.py` (normal exit0 or exact stdlib smoke); scoped code/test commit + normal A push + remote ref/blob re-fetch. If item BLOCKED record exact SHA/error and **continue A4**.

## A4 — RF-035 | SOURCE `libs/reporting/daily_report_runtime/markdown.py::render_policy_surface_sections` L153 blob `8755975bc5d78e26b48c36179556011498a476d9` → TARGET `libs/reporting/daily_report_runtime/markdown_policy_projection.py::render_policy_surface_sections` (new Owner, verified 404)

**Exact SOURCE calculation BODY to MOVE:**
```python
def render_policy_surface_sections(payload: Dict[str, Any]) -> List[str]:
    policy_surface_summary = (
        payload.get("policy_surface_quality_summary")
        if isinstance(payload.get("policy_surface_quality_summary"), dict)
        else {}
    )
    policy_surface_exec = (
        payload.get("policy_surface_quality_executive_summary")
        if isinstance(payload.get("policy_surface_quality_executive_summary"), dict)
        else {}
    )
    chart_structure_summary = (
        payload.get("chart_structure_decision_hint_summary")
        if isinstance(payload.get("chart_structure_decision_hint_summary"), dict)
        else {}
    )
    chart_structure_exec = (
        payload.get("chart_structure_decision_hint_executive_summary")
        if isinstance(payload.get("chart_structure_decision_hint_executive_summary"), dict)
        else {}
    )
    policy_surface_source = (
        payload.get("policy_surface_quality_source")
        if isinstance(payload.get("policy_surface_quality_source"), dict)
        else {}
    )
    chart_structure_source = (
        payload.get("chart_structure_decision_hint_source")
        if isinstance(payload.get("chart_structure_decision_hint_source"), dict)
        else {}
    )
    chart_structure_examples = (
        chart_structure_summary.get("applied_examples")
        if isinstance(chart_structure_summary.get("applied_examples"), list)
        else []
    )

    lines = [
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
        "",
        "## Chart Structure Decision Hint Executive Summary",
        "",
        f"- status: **{str(chart_structure_exec.get('status') or 'unknown').upper()}**",
        f"- headline: {str(chart_structure_exec.get('headline') or 'Chart structure guard unknown')}",
        "",
        "## Chart Structure Decision Hint",
        "",
        f"- available_run_count: **{int(chart_structure_summary.get('available_run_count') or 0)}**",
        f"- applied_count: **{int(chart_structure_summary.get('applied_count') or 0)}**",
        f"- applied_rate: **{float(chart_structure_summary.get('applied_rate') or 0.0):.4f}**",
        f"- top_blocking_features: `{json.dumps(chart_structure_summary.get('top_blocking_features') or [], ensure_ascii=False)}`",
        f"- run_count: **{int(chart_structure_source.get('run_count') or 0)}**",
    ]
    if chart_structure_examples:
        lines += ["", "## Chart Structure Decision Hint Applied Examples", ""]
        for example in chart_structure_examples[:3]:
            if not isinstance(example, dict):
                continue
            lines.append(
                f"- `{example.get('run_id') or '-'}` "
                f"[{str(example.get('entry_style') or '-').upper()}] "
                f"{example.get('reason_transition') or '-'} "
                f"blockers=`{json.dumps(example.get('blocking_features') or [], ensure_ascii=False)}`"
            )
    return lines
```

**Wrapper/callers/monkeypatch:** facade.json.dumps resolved at call time. Source function becomes thin delegating wrapper; preserve existing call sites and exact return/exception, bytes and ordering. This is read-only Markdown/projection; any protected effect remains forbidden.

**NEW targeted normal test:** `tests/test_p15_rf035_01h_a4_render_policy_surface_sections_owner.py`. Fixture and expected: {} => section headings, rate 0.0000; chart_structure_decision_hint_summary.applied_examples=[{'run_id':'R1','entry_style':'pullback'}] => example R1 line; invalid count raises ValueError. Pin golden original before change and compare Owner+wrapper, negative and patch seam, with fake/tmp only.

`python -m py_compile libs/reporting/daily_report_runtime/markdown.py libs/reporting/daily_report_runtime/markdown_policy_projection.py` then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_01h_a4_render_policy_surface_sections_owner.py` (normal exit0 or exact stdlib smoke); scoped code/test commit + normal A push + remote ref/blob re-fetch. If item BLOCKED record exact SHA/error and **continue A5**.

## A5 — RF-035 | SOURCE `libs/reporting/daily_report_runtime/markdown.py::render_top_issues` L232 blob `8755975bc5d78e26b48c36179556011498a476d9` → TARGET `libs/reporting/daily_report_runtime/markdown_operator_projection.py::render_top_issues` (new Owner, verified 404)

**Exact SOURCE calculation BODY to MOVE:**
```python
def render_top_issues(operator_summary_snapshot: Dict[str, Any]) -> List[str]:
    top_issues = (
        operator_summary_snapshot.get("top_issues")
        if isinstance(operator_summary_snapshot.get("top_issues"), list)
        else []
    )
    if not top_issues:
        return []
    lines = ["", "## Top Issues", ""]
    for issue in top_issues:
        if not isinstance(issue, dict):
            continue
        lines.append(f"- [{issue.get('severity') or '-'}] {issue.get('code') or '-'}: {issue.get('detail') or '-'}")
    return lines
```

**Wrapper/callers/monkeypatch:** none; pure renderer. Source function becomes thin delegating wrapper; preserve existing call sites and exact return/exception, bytes and ordering. This is read-only Markdown/projection; any protected effect remains forbidden.

**NEW targeted normal test:** `tests/test_p15_rf035_01h_a5_render_top_issues_owner.py`. Fixture and expected: {} => []; {'top_issues':[{'severity':'warn','code':'X','detail':'demo'}]} => ['', '## Top Issues', '', '- [warn] X: demo']; non-dict ignored. Pin golden original before change and compare Owner+wrapper, negative and patch seam, with fake/tmp only.

`python -m py_compile libs/reporting/daily_report_runtime/markdown.py libs/reporting/daily_report_runtime/markdown_operator_projection.py` then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_01h_a5_render_top_issues_owner.py` (normal exit0 or exact stdlib smoke); scoped code/test commit + normal A push + remote ref/blob re-fetch. If item BLOCKED record exact SHA/error and **continue A6**.

## A6 — RF-035 | SOURCE `libs/reporting/daily_report_runtime/markdown.py::render_recommended_operator_actions` L248 blob `8755975bc5d78e26b48c36179556011498a476d9` → TARGET `libs/reporting/daily_report_runtime/markdown_operator_projection.py::render_recommended_operator_actions` (new Owner, verified 404)

**Exact SOURCE calculation BODY to MOVE:**
```python
def render_recommended_operator_actions(operator_summary_snapshot: Dict[str, Any]) -> List[str]:
    recommended_actions = (
        operator_summary_snapshot.get("recommended_operator_actions")
        if isinstance(operator_summary_snapshot.get("recommended_operator_actions"), list)
        else []
    )
    if not recommended_actions:
        return []
    lines = ["", "## Recommended Operator Actions", ""]
    for action in recommended_actions:
        lines.append(f"- {action}")
    return lines
```

**Wrapper/callers/monkeypatch:** none; pure renderer. Source function becomes thin delegating wrapper; preserve existing call sites and exact return/exception, bytes and ordering. This is read-only Markdown/projection; any protected effect remains forbidden.

**NEW targeted normal test:** `tests/test_p15_rf035_01h_a6_render_recommended_operator_actions_owner.py`. Fixture and expected: {} => []; {'recommended_operator_actions':['A','B']} => ['', '## Recommended Operator Actions', '', '- A', '- B']. Pin golden original before change and compare Owner+wrapper, negative and patch seam, with fake/tmp only.

`python -m py_compile libs/reporting/daily_report_runtime/markdown.py libs/reporting/daily_report_runtime/markdown_operator_projection.py` then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_01h_a6_render_recommended_operator_actions_owner.py` (normal exit0 or exact stdlib smoke); scoped code/test commit + normal A push + remote ref/blob re-fetch. If item BLOCKED record exact SHA/error and **continue A7**.

## A7 — RF-035 | SOURCE `libs/reporting/daily_report_runtime/markdown.py::render_broker_alignment` L100 blob `8755975bc5d78e26b48c36179556011498a476d9` → TARGET `libs/reporting/daily_report_runtime/markdown_alignment_projection.py::render_broker_alignment` (new Owner, verified 404)

**Exact SOURCE calculation BODY to MOVE:**
```python
def render_broker_alignment(payload: Dict[str, Any]) -> List[str]:
    alignment = payload.get("broker_alignment") if isinstance(payload.get("broker_alignment"), dict) else {}
    if not alignment:
        return []
    summary = alignment.get("summary") if isinstance(alignment.get("summary"), dict) else {}
    status = str(alignment.get("status") or "unknown")
    lines = [
        "",
        "## Broker Alignment",
        "",
        f"- status: **{status.upper()}**",
        f"- generated_at: `{alignment.get('generated_at') or '-'}`",
        f"- local_total: **{int(summary.get('local_total') or 0)}**",
        f"- broker_total: **{int(summary.get('broker_total') or 0)}**",
        f"- matched_by_ord_no: **{int(summary.get('matched_by_ord_no') or 0)}**",
        f"- missing_in_local: **{int(summary.get('missing_in_local_total') or 0)}**",
        f"- missing_in_broker: **{int(summary.get('missing_in_broker_total') or 0)}**",
    ]
    if alignment.get("error"):
        lines.append(f"- error: `{alignment.get('error')}`")
    if alignment.get("report_json_path"):
        lines.append(f"- report_json: `{alignment.get('report_json_path')}`")
    snapshot = alignment.get("account_snapshot") if isinstance(alignment.get("account_snapshot"), dict) else {}
    if snapshot:
        closed_symbols = snapshot.get("day_trade_closed_symbols") if isinstance(snapshot.get("day_trade_closed_symbols"), list) else []
        lines.append(f"- account_snapshot_status: **{str(snapshot.get('status') or 'unknown').upper()}**")
        if snapshot.get("path"):
            lines.append(f"- account_snapshot_json: `{snapshot.get('path')}`")
        if snapshot.get("api_call_count") not in (None, ""):
            lines.append(
                f"- account_snapshot_calls: **{int(snapshot.get('ok_count') or 0)}"
                f"/{int(snapshot.get('api_call_count') or 0)} ok**"
            )
        lines.append(f"- day_trade_diary_count: **{int(snapshot.get('day_trade_diary_count') or 0)}**")
        if closed_symbols:
            lines.append(f"- day_trade_closed_symbols: `{', '.join(str(x) for x in closed_symbols)}`")
        if snapshot.get("error"):
            lines.append(f"- account_snapshot_error: `{snapshot.get('error')}`")
    for title, key in (("missing broker-only rows", "missing_in_local"), ("missing local-only rows", "missing_in_broker")):
        rows = summary.get(key) if isinstance(summary.get(key), list) else []
        if not rows:
            continue
        lines.append(f"- {title}:")
        for row in rows[:5]:
            if not isinstance(row, dict):
                continue
            lines.append(
                f"  - ord_no={row.get('ord_no') or '-'} symbol={row.get('symbol') or '-'} "
                f"side={row.get('side') or '-'} qty={row.get('filled_qty') or row.get('qty') or row.get('order_qty') or 0}"
            )
    return lines
```

**Wrapper/callers/monkeypatch:** none; pure formatting of supplied dict only, NEVER query broker, reconcile, order or mutate guard. Source function becomes thin delegating wrapper; preserve existing call sites and exact return/exception, bytes and ordering. This is read-only Markdown/projection; any protected effect remains forbidden.

**NEW targeted normal test:** `tests/test_p15_rf035_01h_a7_render_broker_alignment_owner.py`. Fixture and expected: {} => []; {'broker_alignment':{'status':'ok','summary':{'local_total':2,'broker_total':2,'matched_by_ord_no':2}}} => header, OK, local_total 2, broker_total 2, matched 2; fake account_snapshot.api_call_count=2,ok_count=1 => '1/2 ok'; malformed count ValueError parity. Pin golden original before change and compare Owner+wrapper, negative and patch seam, with fake/tmp only.

`python -m py_compile libs/reporting/daily_report_runtime/markdown.py libs/reporting/daily_report_runtime/markdown_alignment_projection.py` then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_01h_a7_render_broker_alignment_owner.py` (normal exit0 or exact stdlib smoke); scoped code/test commit + normal A push + remote ref/blob re-fetch. If item BLOCKED record exact SHA/error and **continue A8**.

## A8 — RF-035 | SOURCE `libs/reporting/daily_report_runtime/markdown.py::render_no_event_daily_markdown` L262 blob `8755975bc5d78e26b48c36179556011498a476d9` → TARGET `libs/reporting/daily_report_runtime/markdown_daily_projection.py::render_no_event_daily_markdown` (new Owner, verified 404)

**Exact SOURCE calculation BODY to MOVE:**
```python
def render_no_event_daily_markdown(
    *,
    day: str,
    payload: Dict[str, Any],
    operator_snapshot_freshness: Dict[str, Any],
    render_residual_positions: ResidualRenderer,
) -> str:
    operator_summary_snapshot = (
        payload.get("operator_summary_snapshot")
        if isinstance(payload.get("operator_summary_snapshot"), dict)
        else {}
    )
    residual_positions = payload.get("residual_positions") if isinstance(payload.get("residual_positions"), dict) else {}
    lines = [
        f"# Daily Report ({day})",
        "",
        "No events found.",
    ]
    lines += [""] + render_data_freshness_markdown(payload["data_freshness"])
    lines += [f"- operator_summary_snapshot_stale: **{operator_snapshot_freshness['stale']}**"]
    lines += render_operator_summary_snapshot(operator_summary_snapshot, include_system_status=False)
    lines += render_residual_positions(residual_positions)
    lines += render_trade_report_integrity(payload)
    lines += render_broker_alignment(payload)
    lines += render_route_and_narrative_sections(payload)
    lines += render_policy_surface_sections(payload)
    return "\n".join(lines) + "\n"
```

**Wrapper/callers/monkeypatch:** facade.render_data_freshness_markdown, render_operator_summary_snapshot, render_trade_report_integrity, render_broker_alignment, render_route_and_narrative_sections, render_policy_surface_sections resolved at call time; render_residual_positions callback stays passed through. Source function becomes thin delegating wrapper; preserve existing call sites and exact return/exception, bytes and ordering. This is read-only Markdown/projection; any protected effect remains forbidden.

**NEW targeted normal test:** `tests/test_p15_rf035_01h_a8_render_no_event_daily_markdown_owner.py`. Fixture and expected: fake day='2026-10-30', payload={'data_freshness':{},'operator_summary_snapshot':{},'residual_positions':{}}, operator_snapshot_freshness={'stale':False}, render_residual_positions=lambda _:[]; patch facade.render_data_freshness_markdown=lambda _:[] => exact '# Daily Report (2026-10-30)\n\nNo events found.' prefix and trailing newline; missing data_freshness => same KeyError; monkeypatch helpers spy. Pin golden original before change and compare Owner+wrapper, negative and patch seam, with fake/tmp only.

`python -m py_compile libs/reporting/daily_report_runtime/markdown.py libs/reporting/daily_report_runtime/markdown_daily_projection.py` then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_01h_a8_render_no_event_daily_markdown_owner.py` (normal exit0 or exact stdlib smoke); scoped code/test commit + normal A push + remote ref/blob re-fetch. If item BLOCKED record exact SHA/error and **continue finish report / preserve blockers**.

## VERIFIED reserve queue — NOT executable in this A order

Six further RF-035 read-only/pure candidate SOURCE bodies inspected against current A branch, all TARGET paths 404 on A/integration. They are future C03 design inventory only, not A9–A14 and not implementation/test results. Recheck source blobs/target functions before future issuance. Never self-select.

### R1 RF-035 | `libs/reporting/daily_report_runtime/markdown.py::render_daily_markdown` L291 blob `8755975bc5d78e26b48c36179556011498a476d9` → `libs/reporting/daily_report_runtime/markdown_daily_full_projection.py::render_daily_markdown` (target 404 on A/integration)

Original inspected BODY (future only):
```python
def render_daily_markdown(
    *,
    day: str,
    summary: Dict[str, Any],
    operator_summary_snapshot_freshness: Dict[str, Any],
    approvals: int,
    blocks: int,
    symbols_for_day: List[str],
    actions: Counter,
    stage_counter: Counter,
    render_residual_positions: ResidualRenderer,
) -> str:
    operator_summary_snapshot = (
        summary.get("operator_summary_snapshot")
        if isinstance(summary.get("operator_summary_snapshot"), dict)
        else {}
    )
    residual_positions = summary.get("residual_positions") if isinstance(summary.get("residual_positions"), dict) else {}
    lines = [
        f"# Daily Report ({day})",
        "",
        *render_data_freshness_markdown(summary["data_freshness"]),
        f"- operator_summary_snapshot_stale: **{operator_summary_snapshot_freshness['stale']}**",
        "",
        f"- events: **{summary['events']}**",
        f"- approvals: **{approvals}** / blocks: **{blocks}**",
        f"- symbols observed: **{len(symbols_for_day)}**",
        "",
        "## Decision actions",
        "",
    ]
    if actions:
        for key, value in actions.most_common():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- (none)")

    lines += ["", "## Stage counts", ""]
    for key, value in stage_counter.most_common():
        lines.append(f"- {key}: {value}")

    lines += render_operator_summary_snapshot(operator_summary_snapshot, include_system_status=True)
    lines += render_residual_positions(residual_positions)
    lines += render_trade_report_integrity(summary)
    lines += render_broker_alignment(summary)
    lines += render_route_and_narrative_sections(summary)
    lines += render_policy_surface_sections(summary)
    lines += render_top_issues(operator_summary_snapshot)
    lines += render_recommended_operator_actions(operator_summary_snapshot)
    return "\n".join(lines) + "\n"
```
Test hypothesis: fake day, summary data_freshness and counters; compare exact Markdown/trailing newline; monkeypatch facade render_data_freshness_markdown and all render_* helpers; no production output. Exact-signature thin wrapper, facade call-time seam where specified, negative parity, fake/tmp only. Future targeted test `tests/test_p15_rf035_reserve_01h_r1_render_daily_markdown_owner.py`; py_compile+normal targeted exit0 and A remote push required AFTER future C03 issuance. No code/test run now.

### R2 RF-035 | `libs/reporting/trade_explain.py::_safe_int` L43 blob `86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3` → `libs/reporting/trade_explain_scalar_projection.py::_safe_int` (target 404 on A/integration)

Original inspected BODY (future only):
```python
def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except Exception:
        return int(default)
```
Test hypothesis: '2.9' => 2, invalid => default 0; pure, no IO. Exact-signature thin wrapper, facade call-time seam where specified, negative parity, fake/tmp only. Future targeted test `tests/test_p15_rf035_reserve_01h_r2__safe_int_owner.py`; py_compile+normal targeted exit0 and A remote push required AFTER future C03 issuance. No code/test run now.

### R3 RF-035 | `libs/reporting/trade_explain.py::_safe_float` L50 blob `86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3` → `libs/reporting/trade_explain_scalar_projection.py::_safe_float` (target 404 on A/integration)

Original inspected BODY (future only):
```python
def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)
```
Test hypothesis: '2.5' => 2.5, invalid => default 0.0; pure. Exact-signature thin wrapper, facade call-time seam where specified, negative parity, fake/tmp only. Future targeted test `tests/test_p15_rf035_reserve_01h_r3__safe_float_owner.py`; py_compile+normal targeted exit0 and A remote push required AFTER future C03 issuance. No code/test run now.

### R4 RF-035 | `libs/reporting/trade_explain.py::_utc_day` L65 blob `86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3` → `libs/reporting/trade_explain_scalar_projection.py::_utc_day` (target 404 on A/integration)

Original inspected BODY (future only):
```python
def _utc_day(ts: Any) -> Optional[str]:
    epoch = _to_epoch(ts)
    if epoch is None:
        return None
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")
```
Test hypothesis: patched facade._to_epoch fixed UTC epoch -> yyyy-mm-dd, None => None; preserve facade.datetime/timezone at call time. Exact-signature thin wrapper, facade call-time seam where specified, negative parity, fake/tmp only. Future targeted test `tests/test_p15_rf035_reserve_01h_r4__utc_day_owner.py`; py_compile+normal targeted exit0 and A remote push required AFTER future C03 issuance. No code/test run now.

### R5 RF-035 | `libs/reporting/trade_explain.py::official_trade_explain_report_dir` L98 blob `86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3` → `libs/reporting/trade_explain_path_projection.py::official_trade_explain_report_dir` (target 404 on A/integration)

Original inspected BODY (future only):
```python
def official_trade_explain_report_dir(reports_root: Path) -> Path:
    return Path(reports_root) / OFFICIAL_TRADE_EXPLAIN_RELATIVE_DIR
```
Test hypothesis: fake tmp reports root -> root/OFFICIAL_TRADE_EXPLAIN_RELATIVE_DIR, preserve facade constant at call time; no mkdir/write. Exact-signature thin wrapper, facade call-time seam where specified, negative parity, fake/tmp only. Future targeted test `tests/test_p15_rf035_reserve_01h_r5_official_trade_explain_report_dir_owner.py`; py_compile+normal targeted exit0 and A remote push required AFTER future C03 issuance. No code/test run now.

### R6 RF-035 | `libs/reporting/trade_explain.py::build_trade_explain_output_path_metadata` L102 blob `86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3` → `libs/reporting/trade_explain_path_projection.py::build_trade_explain_output_path_metadata` (target 404 on A/integration)

Original inspected BODY (future only):
```python
def build_trade_explain_output_path_metadata(report_dir: Path) -> Dict[str, Any]:
    canonical_reports_root = _canonical_report_root(report_dir)
    requested_dir = Path(report_dir)
    official_dir = official_trade_explain_report_dir(canonical_reports_root)
    is_official = requested_dir == official_dir
    return {
        "official_report_dir": str(official_dir),
        "requested_report_dir": str(requested_dir),
        "path_status": "official" if is_official else "custom_nonofficial",
        "deprecated_note": ""
        if is_official
        else f"Official trade_explain path is `{official_dir}`; custom output path is supported but non-canonical.",
    }
```
Test hypothesis: fake tmp requested official/custom dirs -> path_status official/custom_nonofficial and exact strings; facade._canonical_report_root and official_trade_explain_report_dir patched; no filesystem write. Exact-signature thin wrapper, facade call-time seam where specified, negative parity, fake/tmp only. Future targeted test `tests/test_p15_rf035_reserve_01h_r6_build_trade_explain_output_path_metadata_owner.py`; py_compile+normal targeted exit0 and A remote push required AFTER future C03 issuance. No code/test run now.

## Required #11 report

Report `ORDER_ID=A-20261031-01 | CANONICAL_HEAD | C02_BLOB | A_REMOTE_BEFORE/AFTER | A1..A8 REMOTE_DONE/LOCAL_ONLY/BLOCKED | SOURCE_BLOB_BEFORE/AFTER | TARGET/TEST_BLOBS | NORMAL_CMD/EXIT | PUSH_VERIFIED | FIRST_BLOCKER | NEXT | START_KST/END_KST/ELAPSED_MIN` (measured only). Do not claim RF DONE, G3 or runtime validation.