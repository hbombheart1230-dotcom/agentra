# C01 — Codex B | Agentra FAST-3 | ORDER B-20261031-08 | EIGHT NEW VERIFIED BODY MOVEs

## CURRENT SINGLE-FILE EXECUTION CONTRACT (2026-10-31 08h)

Canonical input HEAD `feba2f3a032860135c181f76d034464334cafaa5`; B owner remote HEAD `291582e0d83e50390b8abfe64aaefa34815f21e1`; OLD_ORDER_BLOB `130987fe5f755fae641c47afa25f6d3f694a1999`. The prior 07h order was **REMOTE_DONE 8/8** based on #12 07h delta and remote owner HEAD; do not reissue its moved BODY or repeat same-SHA tests. Pin CANONICAL_HEAD, ORDER_FILE_BLOB_SHA, OWNER_REMOTE_SHA, SOURCE_BLOB at start. New document publication during actor execution does not invalidate pinned start order.

**Owner and safety:** RF-063; Codex B owns only the specified scripts/diagnostics code/test paths. Each new TARGET file was checked **404 on both integration and actor owner branch** before issuance. All SOURCE functions were inspected at owner remote HEAD and are currently un-moved. Do not touch other Actor code, docs, RF, queue, STATUS, D00, C03/C04/C05, HANDOFF, CI workflows, frozen tests or live runtime. No Broker/Guard/Step5C/UEF/RunLab effect, production DB/State, real orders, network or force push. Only fake/temp targeted normal unittest/smoke.

**All eight items are mandatory and independent:** Move actual SOURCE computation BODY into the single new TARGET Owner; keep thin public SOURCE wrapper, exact caller behavior and call-time monkeypatch parity. Execute each targeted normal test exit0 and py_compile; do not require blanket -O/full peer/hosted CI. Commit own code/test and push normally, then re-fetch remote HEAD and changed blobs. Git auth failure blocks push only, pytest missing can use stdlib unittest; continue every other safe item even after one PASS, blocker or local commit. Do not claim local-only G1, C03 docs as development, or RF DONE. C04 integration and C05 G1/G2/G3 are separate.

## EIGHT CURRENT VERIFIED SOURCE BODY MOVEs

### B1 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_read_json` SOURCE blob `e55b950ad121641186797c891d2129c76615412e` L26 (10 lines) → `scripts/diagnostics/reporter_upgrade_read_projection.py::_read_json`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _read_json(path: Path) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reporter_upgrade_read_projection._read_json` passing `facade=_migration_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.json.loads. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_08h_b1_read_json_owner.py` with fake/temp fixture and expected result: missing/malformed/non-dict tmp -> {}; dict -> dict. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_read_projection.py`; `python -m unittest tests/test_p15_rf063_08h_b1_read_json_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### B2 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_trade_dirs_for_day` SOURCE blob `e55b950ad121641186797c891d2129c76615412e` L36 (9 lines) → `scripts/diagnostics/reporter_upgrade_read_projection.py::_trade_dirs_for_day`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _trade_dirs_for_day(reports_root: Path, day: str) -> List[Path]:
    base = reports_root / "trades" / str(day or "").strip()
    if not base.exists():
        return []
    out = [path for path in base.iterdir() if path.is_dir()]
    out.sort(key=lambda p: p.name)
    return out
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reporter_upgrade_read_projection._trade_dirs_for_day` passing `facade=_migration_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: read-only tmp. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_08h_b2_trade_dirs_for_day_owner.py` with fake/temp fixture and expected result: temp day dir with b,a -> sorted a,b; missing -> []. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_read_projection.py`; `python -m unittest tests/test_p15_rf063_08h_b2_trade_dirs_for_day_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### B3 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_is_closed_trade` SOURCE blob `e55b950ad121641186797c891d2129c76615412e` L45 (17 lines) → `scripts/diagnostics/reporter_upgrade_state_projection.py::_is_closed_trade`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _is_closed_trade(bundle: Dict[str, Any]) -> bool:
    lifecycle = bundle.get("lifecycle") if isinstance(bundle.get("lifecycle"), dict) else {}
    exit_payload = lifecycle.get("exit") if isinstance(lifecycle.get("exit"), dict) else {}
    if exit_payload:
        return True
    status = str(
        bundle.get("trade_lifecycle_status")
        or lifecycle.get("status")
        or bundle.get("status")
        or ""
    ).strip().lower()
    if status in {"closed", "exited", "sell"}:
        return True
    top_exit = bundle.get("exit") if isinstance(bundle.get("exit"), dict) else {}
    return bool(top_exit.get("available"))
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reporter_upgrade_state_projection._is_closed_trade` passing `facade=_migration_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_08h_b3_is_closed_trade_owner.py` with fake/temp fixture and expected result: lifecycle.exit nonempty -> True; status closed -> True; {} -> False. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_state_projection.py`; `python -m unittest tests/test_p15_rf063_08h_b3_is_closed_trade_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### B4 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_reporter_section_fallback` SOURCE blob `e55b950ad121641186797c891d2129c76615412e` L67 (10 lines) → `scripts/diagnostics/reporter_upgrade_state_projection.py::_reporter_section_fallback`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _reporter_section_fallback(report: Dict[str, Any]) -> bool:
    provenance = report.get("section_provenance") if isinstance(report.get("section_provenance"), dict) else {}
    for key in ("reporter_evaluation", "errors_weaknesses_improvement_points"):
        item = provenance.get(key) if isinstance(provenance.get(key), dict) else {}
        source = str(item.get("source") or "").strip().lower()
        if source in {"fallback", "unknown", "missing"}:
            return True
    return False
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reporter_upgrade_state_projection._reporter_section_fallback` passing `facade=_migration_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_08h_b4_reporter_section_fallback_owner.py` with fake/temp fixture and expected result: reporter_evaluation fallback -> True; model or empty -> False. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_state_projection.py`; `python -m unittest tests/test_p15_rf063_08h_b4_reporter_section_fallback_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### B5 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_missing_canonical_paths` SOURCE blob `e55b950ad121641186797c891d2129c76615412e` L77 (6 lines) → `scripts/diagnostics/reporter_upgrade_state_projection.py::_missing_canonical_paths`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _missing_canonical_paths(bundle: Dict[str, Any]) -> bool:
    artifacts = bundle.get("artifacts") if isinstance(bundle.get("artifacts"), dict) else {}
    values = [str(artifacts.get(key) or bundle.get(key) or "").strip() for key in CANONICAL_ARTIFACT_KEYS]
    return any(not value for value in values)
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reporter_upgrade_state_projection._missing_canonical_paths` passing `facade=_migration_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.CANONICAL_ARTIFACT_KEYS. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_08h_b5_missing_canonical_paths_owner.py` with fake/temp fixture and expected result: six canonical artifact paths -> False; missing one -> True. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_state_projection.py`; `python -m unittest tests/test_p15_rf063_08h_b5_missing_canonical_paths_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### B6 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_thin_trace` SOURCE blob `e55b950ad121641186797c891d2129c76615412e` L83 (27 lines) → `scripts/diagnostics/reporter_upgrade_trace_projection.py::_thin_trace`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _thin_trace(bundle: Dict[str, Any]) -> bool:
    scanner_trace = bundle.get("scanner_selection_trace") if isinstance(bundle.get("scanner_selection_trace"), dict) else {}
    if not scanner_trace:
        scanner_reason = bundle.get("scanner_reason_human") if isinstance(bundle.get("scanner_reason_human"), dict) else {}
        scanner_trace = (
            scanner_reason.get("scanner_selection_trace")
            if isinstance(scanner_reason.get("scanner_selection_trace"), dict)
            else {}
        )
    ranked = scanner_trace.get("ranked_candidates") if isinstance(scanner_trace.get("ranked_candidates"), list) else []
    if not ranked:
        scanner_reason = bundle.get("scanner_reason_human") if isinstance(bundle.get("scanner_reason_human"), dict) else {}
        ranked = scanner_reason.get("ranked_candidates") if isinstance(scanner_reason.get("ranked_candidates"), list) else []

    monitor_trace = bundle.get("monitor_stop_policy_trace") if isinstance(bundle.get("monitor_stop_policy_trace"), dict) else {}
    if not monitor_trace:
        monitor_reason = bundle.get("monitor_reason_human") if isinstance(bundle.get("monitor_reason_human"), dict) else {}
        monitor_trace = (
            monitor_reason.get("monitor_stop_policy_trace")
            if isinstance(monitor_reason.get("monitor_stop_policy_trace"), dict)
            else {}
        )
    scanner_thin = len(ranked) == 0
    monitor_thin = len(monitor_trace) == 0
    return scanner_thin or monitor_thin
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reporter_upgrade_trace_projection._thin_trace` passing `facade=_migration_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_08h_b6_thin_trace_owner.py` with fake/temp fixture and expected result: empty vs complete scanner/monitor trace; compare exact original booleans, malformed nested inputs. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_trace_projection.py`; `python -m unittest tests/test_p15_rf063_08h_b6_thin_trace_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### B7 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::analyze_day` SOURCE blob `e55b950ad121641186797c891d2129c76615412e` L110 → `scripts/diagnostics/reporter_upgrade_analysis_projection.py::analyze_day`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def analyze_day(reports_root: Path, day: str) -> Dict[str, Any]:
    trade_dirs = _trade_dirs_for_day(reports_root, day)
    metrics = {
        "day": day,
        "total_trades": 0,
        "closed_trades": 0,
        "closed_trade_ai_report_exists": 0,
        "closed_trade_ai_report_missing": 0,
        "all_fallback_section_count": 0,
        "reporter_fallback_count": 0,
        "missing_canonical_path_count": 0,
        "thin_trace_count": 0,
    }

    for trade_dir in trade_dirs:
        metrics["total_trades"] += 1
        bundle = _read_json(trade_dir / "lifecycle_bundle.json")
        report = _read_json(trade_dir / "reports" / "ai_trade_report.json")

        if _missing_canonical_paths(bundle):
            metrics["missing_canonical_path_count"] += 1
        if _thin_trace(bundle):
            metrics["thin_trace_count"] += 1

        if not _is_closed_trade(bundle):
            continue
        metrics["closed_trades"] += 1

        if report:
            metrics["closed_trade_ai_report_exists"] += 1
            if _section_provenance_all_fallback(report):
                metrics["all_fallback_section_count"] += 1
            if _reporter_section_fallback(report):
                metrics["reporter_fallback_count"] += 1
        else:
            metrics["closed_trade_ai_report_missing"] += 1

    closed = max(1, int(metrics["closed_trades"]))
    metrics["ratios"] = {
        "closed_trade_ai_report_exists_ratio": float(metrics["closed_trade_ai_report_exists"]) / float(closed),
        "all_fallback_section_ratio": float(metrics["all_fallback_section_count"]) / float(closed),
        "reporter_fallback_ratio": float(metrics["reporter_fallback_count"]) / float(closed),
    }
    return metrics
```

**Thin compatibility wrapper/caller/monkeypatch:** Preserve exact signature, defaults, annotations, return/exception and caller import. Keep SOURCE as a one-call wrapper to the new Owner function; TARGET must not import SOURCE. At call time use facade._trade_dirs_for_day, facade._read_json, facade._missing_canonical_paths, facade._thin_trace, facade._is_closed_trade, facade._section_provenance_all_fallback, facade._reporter_section_fallback; preserve helper patch seams. Resolve module globals via `facade` at call time where needed, preserving post-import monkeypatch. No duplicate calculation remains in SOURCE; do not alter CLI/operational effects.

**New normal targeted test:** `tests/test_p15_rf063_08h_b7_analyze_day_owner.py`. Use temp reports/trades/day with one closed and one open trade, fake lifecycle_bundle.json and reports/ai_trade_report.json. Expect total_trades=2, closed_trades=1, ratios calculated using max(1, closed), no real report directory touched. Compare pre-move baseline, Owner and wrapper outputs and exception parity; mock module globals after import. `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_analysis_projection.py`; `python -m unittest tests/test_p15_rf063_08h_b7_analyze_day_owner.py -v` normal exit0. Use fake/tmp only; no live network, production state, real order, Broker/Guard/Step5C/UEF/RunLab, scheduler or subprocess. Commit only own code/test, normal push, re-fetch exact owner HEAD and SOURCE/TARGET/test blob. If blocked, record FIRST_BLOCKER and continue next mandatory item.

### B8 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::compare_days` SOURCE blob `e55b950ad121641186797c891d2129c76615412e` L156 → `scripts/diagnostics/reporter_upgrade_comparison_projection.py::compare_days`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def compare_days(base: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
    keys = (
        "closed_trades",
        "closed_trade_ai_report_exists",
        "closed_trade_ai_report_missing",
        "all_fallback_section_count",
        "reporter_fallback_count",
        "missing_canonical_path_count",
        "thin_trace_count",
    )
    return {
        "base_day": str(base.get("day") or ""),
        "target_day": str(target.get("day") or ""),
        "deltas": {key: int(target.get(key) or 0) - int(base.get(key) or 0) for key in keys},
    }
```

**Thin compatibility wrapper/caller/monkeypatch:** Preserve exact signature, defaults, annotations, return/exception and caller import. Keep SOURCE as a one-call wrapper to the new Owner function; TARGET must not import SOURCE. Pure metrics delta calculation, no IO or global lookup. Resolve module globals via `facade` at call time where needed, preserving post-import monkeypatch. No duplicate calculation remains in SOURCE; do not alter CLI/operational effects.

**New normal targeted test:** `tests/test_p15_rf063_08h_b8_compare_days_owner.py`. base closed_trades=2, target=5 => deltas.closed_trades=3; absent keys default 0; invalid int raises same ValueError. Compare pre-move baseline, Owner and wrapper outputs and exception parity; mock module globals after import. `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_comparison_projection.py`; `python -m unittest tests/test_p15_rf063_08h_b8_compare_days_owner.py -v` normal exit0. Use fake/tmp only; no live network, production state, real order, Broker/Guard/Step5C/UEF/RunLab, scheduler or subprocess. Commit only own code/test, normal push, re-fetch exact owner HEAD and SOURCE/TARGET/test blob. If blocked, record FIRST_BLOCKER and continue next mandatory item.

## SIX FUTURE RESERVES — RESERVE_NOT_VERIFIED (0/6)

The six prior 07h reserves B-R1..R6 are consumed as B1..B6 in this order. **Do not** count them as reserves or implement any unassigned candidate. Next C03 must inspect six fresh actual SOURCE bodies, exclusive TARGET nonexistence, RF ownership, effects and targeted test before marking VERIFIED. Candidate scanning may begin with the remaining diagnostics-only functions, but no unverified name is an executable order.

## REPORT AND CONTINUATION

Post #12: `ORDER_ID=B-20261031-08 | CANONICAL_HEAD | OLD_ORDER_BLOB=130987fe5f755fae641c47afa25f6d3f694a1999 | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA_BEFORE→AFTER | B1..B8 per-item IMPLEMENTED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED | SOURCE_BEFORE_AFTER_BLOBS | TARGET_BLOBS | NORMAL_TEST_COMMAND/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER | NEXT`. START/END/ELAPSED only measured; reserves not executable.