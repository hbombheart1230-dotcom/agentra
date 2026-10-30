# C02 — Agentra FAST-3 A-20261031-02 | NEW 8 RF-035 actual BODY MOVEs

PRIOR REMOTE_DONE: #11 6527585681 confirms A previous 8/8 with normal scoped tests; A HEAD 6251e20ce7bded96f760febb6ab721d2e77739d5. Old C02 blob 318bbc0cdcd1192fbf8aae0c248927b7c62166fd. Old SOURCE markdown.py now thin wrappers (blob 0ed16b2f3d77ed675de1acdbfa5507e4bf53edad). Do not repeat previous MOVE/PASS. New SOURCE trade_explain.py blob 86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3 identical on A/integration. All five new target modules checked 404 on A remote. RF-035 exclusive Claude A Owner; no B overlap.

Read THIS C02 only, then named SOURCE/TARGET/test. Do not read D00, RF, queues or select own work. Pin canonical HEAD, order blob, A remote HEAD and SOURCE blobs before editing. Execute ALL A1-A8; if one BLOCKED continue next independent item. Work only on work/p15-a-reporter-pure-20261021 code/test. MOVE displayed full calculation BODY to TARGET and REMOVE from SOURCE, leaving exact-signature thin compatibility wrapper, preserving annotations/docstrings/caller, return/exception, order, monkeypatch. TARGET must not import SOURCE. For trade_explain use facade=_r3_sys.modules[__name__] for module-global seams; for markdown facade=sys.modules[__name__]. Preserve call-time resolution of helper/global symbols (do not bind at import time). Before move capture baseline golden output on fake fixture; after move compare Owner and wrapper normal/negative/monkeypatch parity. Run py_compile and new targeted normal pytest exit0 (or reproducible stdlib normal smoke if pytest absent). Commit only source/target/new scoped test; normal A push, re-fetch remote ref and SOURCE/TARGET/TEST blobs. If credentials fail mark LOCAL_ONLY/PUSH_BLOCKED, continue other safe items. No force push, operational reports, production file writes, real network/order, Broker/Guard/Step5C/UEF, RunLab, state/DB. -O/full peer/hosted CI not mandatory; C04 integrates and C05 judges G1/G2/G3/DONE.

## A1 RF-035 SOURCE libs/reporting/daily_report_runtime/markdown.py::render_daily_markdown blob 0ed16b2f3d77ed675de1acdbfa5507e4bf53edad -> TARGET libs/reporting/daily_report_runtime/markdown_daily_full_projection.py::render_daily_markdown (new target 404)

Exact BODY to MOVE, not duplicate:

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

Wrapper: preserve exact signature, old caller and monkeypatch. SOURCE thin delegates to new Owner; module globals resolved through facade at call time. Pass all render_* and render_data_freshness_markdown via facade; preserve residual callback and Counter order. Multiple items sharing a TARGET must append functions, not overwrite.

New targeted test tests/test_p15_rf035_02h_a1_render_daily_markdown_owner.py: fake day 2026-10-30, summary data_freshness {}, events 2, actions Counter approve 1, stage_counter Counter monitor 2; monkeypatch all facade render_* helpers to [] and expect exact header/events/counts/trailing newline; missing data_freshness KeyError. Compare original baseline, wrapper and Owner exact values/errors and patch behavior using fake/temp only. Run python -m py_compile libs/reporting/daily_report_runtime/markdown.py libs/reporting/daily_report_runtime/markdown_daily_full_projection.py; python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_02h_a1_render_daily_markdown_owner.py normal exit0 (or exact stdlib smoke). Commit code/test, normal push A, re-fetch A HEAD and SOURCE/TARGET/TEST blobs. If blocked record exact SHA/error and continue A2.

## A2 RF-035 SOURCE libs/reporting/trade_explain.py::_safe_int blob 86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3 -> TARGET libs/reporting/trade_explain_scalar_projection.py::_safe_int (new target 404)

Exact BODY to MOVE, not duplicate:

```python
def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except Exception:
        return int(default)
```

Wrapper: preserve exact signature, old caller and monkeypatch. SOURCE thin delegates to new Owner; module globals resolved through facade at call time. Preserve any global helper/constant via facade and existing exception semantics. Multiple items sharing a TARGET must append functions, not overwrite.

New targeted test tests/test_p15_rf035_02h_a2_safe_int_owner.py: '2.9' returns 2, bad returns 0, bad with default 7 returns 7; invalid default exception parity. Compare original baseline, wrapper and Owner exact values/errors and patch behavior using fake/temp only. Run python -m py_compile libs/reporting/trade_explain.py libs/reporting/trade_explain_scalar_projection.py; python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_02h_a2_safe_int_owner.py normal exit0 (or exact stdlib smoke). Commit code/test, normal push A, re-fetch A HEAD and SOURCE/TARGET/TEST blobs. If blocked record exact SHA/error and continue A3.

## A3 RF-035 SOURCE libs/reporting/trade_explain.py::_safe_float blob 86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3 -> TARGET libs/reporting/trade_explain_scalar_projection.py::_safe_float (new target 404)

Exact BODY to MOVE, not duplicate:

```python
def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)
```

Wrapper: preserve exact signature, old caller and monkeypatch. SOURCE thin delegates to new Owner; module globals resolved through facade at call time. Preserve any global helper/constant via facade and existing exception semantics. Multiple items sharing a TARGET must append functions, not overwrite.

New targeted test tests/test_p15_rf035_02h_a3_safe_float_owner.py: '2.5' returns 2.5, bad returns 0.0, bad with default 3.25 returns 3.25. Compare original baseline, wrapper and Owner exact values/errors and patch behavior using fake/temp only. Run python -m py_compile libs/reporting/trade_explain.py libs/reporting/trade_explain_scalar_projection.py; python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_02h_a3_safe_float_owner.py normal exit0 (or exact stdlib smoke). Commit code/test, normal push A, re-fetch A HEAD and SOURCE/TARGET/TEST blobs. If blocked record exact SHA/error and continue A4.

## A4 RF-035 SOURCE libs/reporting/trade_explain.py::_utc_day blob 86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3 -> TARGET libs/reporting/trade_explain_scalar_projection.py::_utc_day (new target 404)

Exact BODY to MOVE, not duplicate:

```python
def _utc_day(ts: Any) -> Optional[str]:
    epoch = _to_epoch(ts)
    if epoch is None:
        return None
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")
```

Wrapper: preserve exact signature, old caller and monkeypatch. SOURCE thin delegates to new Owner; module globals resolved through facade at call time. Preserve any global helper/constant via facade and existing exception semantics. Multiple items sharing a TARGET must append functions, not overwrite.

New targeted test tests/test_p15_rf035_02h_a4_utc_day_owner.py: patch facade._to_epoch to 0 -> 1970-01-01, 86400 -> 1970-01-02, None -> None; patch facade.datetime/timezone and compare. Compare original baseline, wrapper and Owner exact values/errors and patch behavior using fake/temp only. Run python -m py_compile libs/reporting/trade_explain.py libs/reporting/trade_explain_scalar_projection.py; python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_02h_a4_utc_day_owner.py normal exit0 (or exact stdlib smoke). Commit code/test, normal push A, re-fetch A HEAD and SOURCE/TARGET/TEST blobs. If blocked record exact SHA/error and continue A5.

## A5 RF-035 SOURCE libs/reporting/trade_explain.py::official_trade_explain_report_dir blob 86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3 -> TARGET libs/reporting/trade_explain_path_projection.py::official_trade_explain_report_dir (new target 404)

Exact BODY to MOVE, not duplicate:

```python
def official_trade_explain_report_dir(reports_root: Path) -> Path:
    return Path(reports_root) / OFFICIAL_TRADE_EXPLAIN_RELATIVE_DIR
```

Wrapper: preserve exact signature, old caller and monkeypatch. SOURCE thin delegates to new Owner; module globals resolved through facade at call time. Preserve any global helper/constant via facade and existing exception semantics. Multiple items sharing a TARGET must append functions, not overwrite.

New targeted test tests/test_p15_rf035_02h_a5_official_trade_explain_report_dir_owner.py: tmp reports root -> root/dev/analysis/trade_explain; patch facade.OFFICIAL_TRADE_EXPLAIN_RELATIVE_DIR to custom and verify path; no mkdir. Compare original baseline, wrapper and Owner exact values/errors and patch behavior using fake/temp only. Run python -m py_compile libs/reporting/trade_explain.py libs/reporting/trade_explain_path_projection.py; python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_02h_a5_official_trade_explain_report_dir_owner.py normal exit0 (or exact stdlib smoke). Commit code/test, normal push A, re-fetch A HEAD and SOURCE/TARGET/TEST blobs. If blocked record exact SHA/error and continue A6.

## A6 RF-035 SOURCE libs/reporting/trade_explain.py::build_trade_explain_output_path_metadata blob 86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3 -> TARGET libs/reporting/trade_explain_path_projection.py::build_trade_explain_output_path_metadata (new target 404)

Exact BODY to MOVE, not duplicate:

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

Wrapper: preserve exact signature, old caller and monkeypatch. SOURCE thin delegates to new Owner; module globals resolved through facade at call time. Preserve any global helper/constant via facade and existing exception semantics. Multiple items sharing a TARGET must append functions, not overwrite.

New targeted test tests/test_p15_rf035_02h_a6_build_trade_explain_output_path_metadata_owner.py: patch facade._canonical_report_root and facade.official_trade_explain_report_dir; official -> status official and note empty; custom -> custom_nonofficial and exact note. Compare original baseline, wrapper and Owner exact values/errors and patch behavior using fake/temp only. Run python -m py_compile libs/reporting/trade_explain.py libs/reporting/trade_explain_path_projection.py; python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_02h_a6_build_trade_explain_output_path_metadata_owner.py normal exit0 (or exact stdlib smoke). Commit code/test, normal push A, re-fetch A HEAD and SOURCE/TARGET/TEST blobs. If blocked record exact SHA/error and continue A7.

## A7 RF-035 SOURCE libs/reporting/trade_explain.py::_iter_jsonl blob 86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3 -> TARGET libs/reporting/trade_explain_read_projection.py::_iter_jsonl (new target 404)

Exact BODY to MOVE, not duplicate:

```python
def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                out.append(obj)
    return out
```

Wrapper: preserve exact signature, old caller and monkeypatch. SOURCE thin delegates to new Owner; module globals resolved through facade at call time. Use facade.json.loads at call time, read fake tmp only, preserve exception scope and eager list. Multiple items sharing a TARGET must append functions, not overwrite.

New targeted test tests/test_p15_rf035_02h_a7_iter_jsonl_owner.py: tmp missing -> []; tmp lines valid dict/list/bad/dict -> two dicts in order; monkeypatch facade.json.loads to raise -> []. Compare original baseline, wrapper and Owner exact values/errors and patch behavior using fake/temp only. Run python -m py_compile libs/reporting/trade_explain.py libs/reporting/trade_explain_read_projection.py; python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_02h_a7_iter_jsonl_owner.py normal exit0 (or exact stdlib smoke). Commit code/test, normal push A, re-fetch A HEAD and SOURCE/TARGET/TEST blobs. If blocked record exact SHA/error and continue A8.

## A8 RF-035 SOURCE libs/reporting/trade_explain.py::_report_inventory blob 86418b535aa76bb6a8dc88f1beb9a0809a7bc0f3 -> TARGET libs/reporting/trade_explain_inventory_projection.py::_report_inventory (new target 404)

Exact BODY to MOVE, not duplicate:

```python
def _report_inventory(day: str, reports_root: Path) -> List[str]:
    operator_root = operator_summary_artifact_root(reports_root)
    candidates = [
        operator_root / "daily" / day / "operator_summary.md",
        reports_root / "decision_story" / f"decision_story_{day}.md",
        reports_root / "run_cards" / f"run_cards_{day}.md",
        reports_root / "metrics" / f"metrics_{day}.md",
        operator_root / "daily" / day / "daily_report.md",
        operator_root / "daily" / f"daily_{day}.md",
        reports_root / "live_watch" / "live_watch_latest.md",
    ]
    out: List[str] = []
    for p in candidates:
        if p.exists():
            out.append(str(p))
    return out
```

Wrapper: preserve exact signature, old caller and monkeypatch. SOURCE thin delegates to new Owner; module globals resolved through facade at call time. Use facade.operator_summary_artifact_root at call time, preserve seven candidate path order. Multiple items sharing a TARGET must append functions, not overwrite.

New targeted test tests/test_p15_rf035_02h_a8_report_inventory_owner.py: tmp reports root, monkeypatch facade.operator_summary_artifact_root; create fake operator daily and metrics files -> exactly two paths in original order; missing -> []. Compare original baseline, wrapper and Owner exact values/errors and patch behavior using fake/temp only. Run python -m py_compile libs/reporting/trade_explain.py libs/reporting/trade_explain_inventory_projection.py; python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_02h_a8_report_inventory_owner.py normal exit0 (or exact stdlib smoke). Commit code/test, normal push A, re-fetch A HEAD and SOURCE/TARGET/TEST blobs. If blocked record exact SHA/error and continue final report.

## RESERVE_NOT_VERIFIED (A 0/6)
Previous six reserves consumed as A1-A6. Additional candidate functions report_source_helpers.py::read_json,to_epoch,utc_day,epoch_to_iso,iter_jsonl,_commander_route_from_payload are NOT VERIFIED for RF ownership, new target absence, body/fixtures and must NOT be selected by A. C03 next pass must design/verify six reserves before A exhaustion.

Report to #11 ORDER_ID A-20261031-02, canonical/order/A SHA, A1-A8 status, source/target/test blobs, normal exit, push verification, first blocker/next, measured START/END/ELAPSED. C03 document commits are not code G1/G2/G3 or RF DONE.
