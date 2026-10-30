# C01 — Agentra FAST-3 Codex B | ORDER B-20261031-04 | 7 remaining verified RF-063 BODY MOVEs + B0 repair

**Remote preflight:** canonical integration HEAD `babe536251f175d41f7eab85fe86d4e47b50b8a6`; B remote HEAD `97c1c22cb70fbb022dce4391362f589e00d171ac`. C03 verified compare B `e28d1a9d→97c1c22c` (two source/Owner commits). **B1 _read_json and B2 _resolve_trade_context are REMOTE_CODE_MOVED; do not reexecute or retest identical SHA.** B1 target `trade_artifact_validation_read_projection.py` blob `c573e644ab9f81377ecba906ad283170807c6ee7`; B2 target `trade_artifact_context_projection.py` blob `433de050fa01885bf7315380a6efa5070d741ccf`. Normal targeted G2 for B1/B2 NOT_VERIFIED (code presence is not RF DONE). B0 RF-065 has a **remote broken wrapper** from prior move; the `phase5_markdown` import is still absent, SOURCE blob `f7ce771eca2286bd6d647641a001f06f0932193c`, TARGET blob `cc37e3ddf7ee1ed5b6eee7e8d28f6bff3d6ca7cb`. **B0 is a defect fix, not a new MOVE.** B3–B6 source blob `00258649f2635e8baf23f3e56442e37b6f2c2b1e`, B7–B9 source blob `c45516931dcb365c8283c596345233458c10a41f`. Four new target paths 404 on B/integration. B3–B9 are **7 independently safe real BODY MOVEs**; threshold ≥6 so do not cancel this active order. No #12 comment newer than 6524800387, but B HEAD has new remote commits: remote source is authoritative.

**Single-file execution:** Pin CANONICAL_HEAD, ORDER_FILE_BLOB_SHA, B_REMOTE_SHA, each SOURCE blob at start. Execute **B0 and ALL B3–B9**, continuing after isolated blocker. Each B3–B9 task below includes exact SOURCE BODY, TARGET, wrapper, monkeypatch seam, normal fake/tmp fixture and push. SOURCE original signature/annotations/exceptions remain thin delegates; move calculation only once to TARGET; TARGET must not import SOURCE. For B3–B9 use `facade=sys.modules[__name__]` for call-time helper/monkeypatch parity, including command and parser global seams. For B0 add only import + new regression test; never re-move old Markdown BODY. Run `python -m py_compile` and each scoped normal targeted test exit0 (pytest or exact stdlib smoke), compare original/Owner/wrapper, negative and fake patch. Commit only code/tests on `work/p15-b-operator-structure-20261022`, normal push or approved exact reviewed tree/lease update, re-fetch remote HEAD + SOURCE/TARGET/TEST blobs; no force push. HTTPS credential failure is PUSH_BLOCKED, not G2 failure; continue other safe items. No D00/RF/queue/C03 reading or self-selection. No docs/RF/STATUS/other branch edits, no live account/orders/Broker/Guard/Step5C/UEF/RunLab/production state, network, frozen oracle or operational apply. No mandatory -O/full peer/hosted CI. C04/C05 own G3/DONE. A RF-035 paths disjoint.

## B0 — RF-065 REMOTE_BROKEN import fix (not new BODY MOVE)

**B0 mandatory minimal fix FIRST:** In SOURCE imports immediately after `from scripts.research import phase5_validation_read_projection as phase5_read`, add **exactly** `from scripts.research import phase5_validation_markdown as phase5_markdown` (module alias; preserve existing facade wrapper). Do not edit TARGET's large markdown BODY unless exact fake parity demonstrates a separate defect. Add NEW `tests/test_p15_rf065_00h_phase5_markdown_import_owner.py` with fake `payload={'day':'2026-10-30','summary':{},'artifacts':{}}`, `repo_root=tmp_path`; assert `bundle._render_bundle_markdown(payload, repo_root=tmp_path)` returns a string with `# Phase 5 Validation Bundle (2026-10-30)` and equals `phase5_markdown._render_bundle_markdown(payload, repo_root=tmp_path, facade=bundle)` byte-for-byte. Negative fake `summary={'symbol_report_count':'invalid'}` must raise the same `ValueError` through wrapper and Owner. Use isolated fake/tmp only, never call `generate_phase5_validation_bundle` or main. `python -m py_compile scripts/research/run_phase5_validation_bundle.py scripts/research/phase5_validation_markdown.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf065_00h_phase5_markdown_import_owner.py` **normal exit0** (or equivalent reproducible stdlib normal smoke if pytest absent). Commit only SOURCE+new test, push B normal/approved exact reviewed tree, re-fetch B HEAD and SOURCE/TARGET/TEST blobs; report exact normal exit and new remote SHA to #12. If push blocked, preserve LOCAL_ONLY and continue safe B1–B9. This is **defect repair**, not a new structural MOVE or RF DONE.

## B3–B9 — RF-063 actual remaining SOURCE BODY MOVEs

### B3 — RF-063 | `scripts/diagnostics/check_trade_report_runtime_regression.py::_build_bundle_repair_command` SOURCE blob `00258649f2635e8baf23f3e56442e37b6f2c2b1e` → `scripts/diagnostics/trade_artifact_command_projection.py::_build_bundle_repair_command`

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

### B4 — RF-063 | `scripts/diagnostics/check_trade_report_runtime_regression.py::_build_report_regen_command` SOURCE blob `00258649f2635e8baf23f3e56442e37b6f2c2b1e` → `scripts/diagnostics/trade_artifact_command_projection.py::_build_report_regen_command`

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

### B5 — RF-063 | `scripts/diagnostics/check_trade_report_runtime_regression.py::validate_trade_artifact_chain` SOURCE blob `00258649f2635e8baf23f3e56442e37b6f2c2b1e` → `scripts/diagnostics/trade_artifact_validation_evidence_projection.py::validate_trade_artifact_chain`

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

### B6 — RF-063 | `scripts/diagnostics/check_trade_report_runtime_regression.py::_build_parser` SOURCE blob `00258649f2635e8baf23f3e56442e37b6f2c2b1e` → `scripts/diagnostics/trade_artifact_validation_cli.py::_build_parser`

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

Reverified at B `97c1c22cb70fbb022dce4391362f589e00d171ac`, `scripts/diagnostics/check_reports_trades_health.py` source blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` has six inspected non-wrapper bodies; three proposed target paths 404 on B/integration. Tests are design hypotheses NOT_RUN; revalidate before next C03 issue.

- R1 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_read_json` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_read_projection.py::_read_json`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: missing tmp→{}; valid dict→dict; malformed→{}; facade.json.loads. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**
- R2 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_iter_trade_dirs` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_read_projection.py::_iter_trade_dirs`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: tmp reports/trades/day nested dirs→sorted; facade._iter_trade_dirs_under_day; no production root. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**
- R3 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_artifact_path` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_read_projection.py::_artifact_path`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: tmp path first exists→first; none→first candidate; no write. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**
- R4 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_issue` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_issue_projection.py::_issue`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: fake severity/trade/path→exact seven-key dict; pure. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**
- R5 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_ai_trade_report_is_complete` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_read_projection.py::_ai_trade_report_is_complete`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: fake tmp report with required dict sections→True; missing→False; facade._artifact_path/_read_json. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**
- R6 RF-063 `scripts/diagnostics/check_reports_trades_health.py::_build_parser` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` → `scripts/diagnostics/reports_trades_health_cli.py::_build_parser`. Original BODY inspected at B HEAD, target 404 B/integration. Fixture hypothesis: parse_args([]) defaults; '--day' filter; unknown→SystemExit(2); no main. Read-only/temp, no real trade/Guard/Broker effect. **NOT assigned/NOT_RUN; recheck source/target before future order.**

## Final #12 report

`ORDER_ID=B-20261031-04 | CANONICAL_HEAD | ORDER_BLOB_SHA | B_START_REMOTE_SHA | B0,B3..B9 status | SOURCE_BEFORE_AFTER_BLOBS | TARGET_BLOBS | NEW_TEST_NORMAL_EXIT | REMOTE_PUSH_SHA | FIRST_BLOCKER | NEXT`. B1/B2 REMOTE_CODE_MOVED but G2 normal evidence NOT_VERIFIED; do not count them as new MOVE or RF DONE. START/END/ELAPSED only if measured, no estimates. Six reserves design-only, not executable.
