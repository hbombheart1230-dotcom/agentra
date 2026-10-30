# C01 — Codex B | Agentra FAST-3 | ORDER B-20261031-07 | EIGHT VERIFIED NEW BODY MOVEs

## CURRENT SINGLE-FILE EXECUTION CONTRACT (2026-10-31 07h)

Canonical `integration/p1.5` input HEAD `e84a1aeb1abd1f75f84261ec62de27152c0673fa`; B own remote HEAD `5773c4a30ffdead13108f62bb8c8182b9c1909af`; OLD_ORDER_BLOB `3d8ff368883979cd6881929bcc3f36cc28167c04`. On start pin CANONICAL_HEAD, ORDER_FILE_BLOB_SHA, OWNER_REMOTE_SHA and SOURCE blobs; if remote HEAD changes, verify before acting. Old B-06 is **REMOTE_DONE** (#12 6533774550: B0 repaired, B5–B9 moved normal unittest 3 PASS; B1–B4 previously remote moved), no old MOVE or same-SHA test reissued. B-07 consists of the eight **new** numbered items below, all independently mandatory. New publication during a run does not invalidate pinned start order.

**Owner/safety:** RF-063 Codex B exclusively owns scripts/diagnostics files; other Actor is read-only. Every SOURCE BODY below was inspected at the owner HEAD, and each new TARGET path independently returned **404 on both owner branch and integration**. Preserve public wrapper, monkeypatch seam, caller/exception/output parity; use fake/tmp only. No operational or real-trade effect, Broker/Guard/Step5C/UEF/RunLab, live network, subprocess, scheduler or production files. No D00/RF/queue/design re-reading, autonomous selection, Markdown/RF/STATUS/C04/C05/HANDOFF writes, other Actor branch edits or force push. Only own code and code tests. G1 remote code, G2 targeted normal exit0 and C04/C05 G3 are separate; this document is not development evidence.

**Execution and delivery:** Move each exact computation BODY to new single Owner and leave thin SOURCE wrapper. Build named `unittest` test with original/Owner/wrapper parity, negative and call-time monkeypatch. Run `python -m py_compile` and `python -m unittest tests/test_...py -v` normal exit0 for each; stdlib unittest avoids pytest installation dependence. Commit code/test only, normal approved push and re-fetch own HEAD + SOURCE/TARGET/TEST blobs. If Git HTTPS auth blocks push, report PUSH_BLOCKED (local commit is not G1), continue all other safe items; approved exact-tree ref update requires exact parent lease/refetch. First PASS, first commit, time spent, or one failure never ends remaining work. No -O/full peer/hosted CI as blanket requirements.

## EIGHT CURRENT VERIFIED SOURCE BODY MOVEs

### B1 | RF-063 | `scripts/diagnostics/check_reports_trades_health.py::_read_json` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` L17 (10 lines) → `scripts/diagnostics/reports_trades_health_read_projection.py::_read_json`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
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

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reports_trades_health_read_projection._read_json` passing `facade=sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.json.loads. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_07h_b1_read_json_owner.py` with fake/temp fixture and expected result: missing/malformed/non-dict tmp JSON -> {}; dict -> dict. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reports_trades_health.py scripts/diagnostics/reports_trades_health_read_projection.py`; `python -m unittest tests/test_p15_rf063_07h_b1_read_json_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### B2 | RF-063 | `scripts/diagnostics/check_reports_trades_health.py::_iter_trade_dirs` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` L27 (18 lines) → `scripts/diagnostics/reports_trades_health_read_projection.py::_iter_trade_dirs`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _iter_trade_dirs(reports_root: Path, day: str = "") -> List[Path]:
    trades_root = reports_root / "trades"
    if not trades_root.exists():
        return []
    if day:
        day_root = trades_root / day
        if not day_root.exists():
            return []
        return _iter_trade_dirs_under_day(day_root)
    out: List[Path] = []
    for path in sorted(trades_root.iterdir()):
        if not path.is_dir():
            continue
        if len(path.name) == 10 and path.name.count("-") == 2:
            out.extend(_iter_trade_dirs_under_day(path))
    return out
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reports_trades_health_read_projection._iter_trade_dirs` passing `facade=sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade._iter_trade_dirs_under_day. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_07h_b2_iter_trade_dirs_owner.py` with fake/temp fixture and expected result: missing reports/trades -> []; fake day root, patched facade._iter_trade_dirs_under_day -> spy result; sorted multiple days. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reports_trades_health.py scripts/diagnostics/reports_trades_health_read_projection.py`; `python -m unittest tests/test_p15_rf063_07h_b2_iter_trade_dirs_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### B3 | RF-063 | `scripts/diagnostics/check_reports_trades_health.py::_artifact_path` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` L45 (8 lines) → `scripts/diagnostics/reports_trades_health_read_projection.py::_artifact_path`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _artifact_path(trade_dir: Path, *candidates: str) -> Path:
    for raw in candidates:
        path = trade_dir / raw
        if path.exists():
            return path
    return trade_dir / candidates[0]
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reports_trades_health_read_projection._artifact_path` passing `facade=sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: Path.exists temp only. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_07h_b3_artifact_path_owner.py` with fake/temp fixture and expected result: first existing candidate -> first; none -> first candidate; no candidates -> IndexError parity. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reports_trades_health.py scripts/diagnostics/reports_trades_health_read_projection.py`; `python -m unittest tests/test_p15_rf063_07h_b3_artifact_path_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### B4 | RF-063 | `scripts/diagnostics/check_reports_trades_health.py::_issue` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` L53 (19 lines) → `scripts/diagnostics/reports_trades_health_issue_projection.py::_issue`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _issue(
    *,
    severity: str,
    trade_id: str,
    component: str,
    code: str,
    message: str,
    path: Path,
) -> Dict[str, Any]:
    return {
        "severity": severity,
        "trade_id": trade_id,
        "component": component,
        "code": code,
        "message": message,
        "path": str(path),
    }
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reports_trades_health_issue_projection._issue` passing `facade=sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure, six keys. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_07h_b4_issue_owner.py` with fake/temp fixture and expected result: warn/t/brief/x/m/tmp -> exact six-key dict including path str. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reports_trades_health.py scripts/diagnostics/reports_trades_health_issue_projection.py`; `python -m unittest tests/test_p15_rf063_07h_b4_issue_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### B5 | RF-063 | `scripts/diagnostics/check_reports_trades_health.py::_ai_trade_report_is_complete` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` L72 (22 lines) → `scripts/diagnostics/reports_trades_health_read_projection.py::_ai_trade_report_is_complete`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _ai_trade_report_is_complete(trade_dir: Path) -> bool:
    report_path = _artifact_path(trade_dir, "ai_trade_report/ai_trade_report.json", "trade_report.json")
    report = _read_json(report_path)
    if not report:
        return False
    required_sections = (
        "executive_summary",
        "market_context_at_entry",
        "why_this_symbol_was_chosen",
        "entry_decision",
        "holding_monitoring_story",
        "exit_decision",
        "execution_quality",
        "scanner_filters",
        "guard_approval_result",
        "reporter_evaluation",
        "errors_weaknesses_improvement_points",
        "final_operator_conclusion",
    )
    return all(isinstance(report.get(key), dict) for key in required_sections)
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reports_trades_health_read_projection._ai_trade_report_is_complete` passing `facade=sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade._artifact_path, facade._read_json. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_07h_b5_ai_trade_report_is_complete_owner.py` with fake/temp fixture and expected result: 12 required sections dict -> True; missing one or file -> False. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reports_trades_health.py scripts/diagnostics/reports_trades_health_read_projection.py`; `python -m unittest tests/test_p15_rf063_07h_b5_ai_trade_report_is_complete_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### B6 | RF-063 | `scripts/diagnostics/check_reports_trades_health.py::audit_reports_trades_health` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` L94 (167 lines) → `scripts/diagnostics/reports_trades_health_audit_projection.py::audit_reports_trades_health`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def audit_reports_trades_health(reports_root: Path, *, day: str = "") -> Dict[str, Any]:
    trade_dirs = _iter_trade_dirs(reports_root, day=day)
    issues: List[Dict[str, Any]] = []
    issue_counts: Counter[str] = Counter()
    llm_status_counts: Counter[str] = Counter()
    lifecycle_status_counts: Counter[str] = Counter()
    duplicate_counts: Counter[str] = Counter()
    sidecar_counts: Counter[str] = Counter()

    for trade_dir in trade_dirs:
        trade_id = trade_dir.name
        lifecycle_path = _artifact_path(trade_dir, "lifecycle_bundle.json", "lifecycle/trade_lifecycle.json", "trade_lifecycle.json")
        ai_trade_report_llm_path = _artifact_path(
            trade_dir,
            "reports/ai_trade_report_llm_response.json",
            "ai_trade_report/ai_trade_report_llm_response.json",
        )
        brief_llm_path = _artifact_path(
            trade_dir,
            "reports/brief_llm_response.json",
        )
        strategist_llm_path = _artifact_path(
            trade_dir,
            "reports/strategist_llm_response.json",
            "strategist/strategist_llm_response.json",
        )

        for sidecar_name in ("_provenance.json", "_health.json", "_artifact_links.json"):
            if (trade_dir / sidecar_name).exists():
                sidecar_counts[f"{sidecar_name}:present"] += 1
            else:
                sidecar_counts[f"{sidecar_name}:missing"] += 1
                issues.append(
                    _issue(
                        severity="warn",
                        trade_id=trade_id,
                        component="trade_root",
                        code="sidecar_missing",
                        message=f"Missing additive sidecar {sidecar_name}.",
                        path=trade_dir / sidecar_name,
                    )
                )
                issue_counts["sidecar_missing"] += 1

        lifecycle = _read_json(lifecycle_path)
        lifecycle_diag = lifecycle.get("ai_report_diagnostics") if isinstance(lifecycle.get("ai_report_diagnostics"), dict) else {}
        lifecycle_status = str(lifecycle_diag.get("report_status") or "").strip().lower()
        if lifecycle_status:
            lifecycle_status_counts[lifecycle_status] += 1

        component_paths = {
            "ai_trade_report": ai_trade_report_llm_path,
            "brief": brief_llm_path,
            "strategist": strategist_llm_path,
        }
        component_rows: Dict[str, Dict[str, Any]] = {}
        for component, path in component_paths.items():
            payload = _read_json(path)
            component_rows[component] = payload
            if not payload:
                continue
            status = str(payload.get("status") or "").strip().lower()
            meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
            if component == "strategist" and bool(meta.get("synthetic_placeholder")):
                llm_status_counts["strategist:synthetic_placeholder"] += 1
                continue
            if (
                component == "strategist"
                and status == "fallback"
                and not str(payload.get("model") or "").strip()
                and not str(payload.get("raw_response_text") or "").strip()
                and not str(payload.get("error") or "").strip()
                and int(payload.get("retry_count") or 0) == 0
            ):
                llm_status_counts["strategist:synthetic_placeholder"] += 1
                continue
            if status:
                llm_status_counts[f"{component}:{status}"] += 1
            if component == "ai_trade_report" and status in {"partial", "salvaged", "repaired"}:
                missing = payload.get("required_keys_missing") if isinstance(payload.get("required_keys_missing"), list) else []
                parse_error = str(meta.get("parse_error") or payload.get("error") or "").strip()
                if _ai_trade_report_is_complete(trade_dir):
                    issues.append(
                        _issue(
                            severity="info",
                            trade_id=trade_id,
                            component=component,
                            code="llm_recovered",
                            message=f"AI trade report LLM output is {status}, but the final report artifact is structurally complete.",
                            path=path,
                        )
                    )
                    issue_counts["llm_recovered"] += 1
                else:
                    issues.append(
                        _issue(
                            severity="warn",
                            trade_id=trade_id,
                            component=component,
                            code="llm_partial",
                            message=f"AI trade report LLM output is {status}; missing_keys={len(missing)} parse_error={parse_error[:120]}",
                            path=path,
                        )
                    )
                    issue_counts["llm_partial"] += 1
            elif component == "brief" and status == "error":
                reason = str(meta.get("reason") or payload.get("error") or "").strip()
                issues.append(
                    _issue(
                        severity="warn",
                        trade_id=trade_id,
                        component=component,
                        code="llm_error",
                        message=reason or "Brief generation failed without a saved reason.",
                        path=path,
                    )
                )
                issue_counts["llm_error"] += 1
            elif component == "strategist" and status == "fallback":
                parse_mode = str(payload.get("parse_mode") or "").strip().lower()
                raw_len = len(str(payload.get("raw_response_text") or ""))
                issues.append(
                    _issue(
                        severity="warn",
                        trade_id=trade_id,
                        component=component,
                        code="llm_fallback",
                        message=f"Strategist LLM fell back; parse_mode={parse_mode or 'none'} raw_response_len={raw_len}.",
                        path=path,
                    )
                )
                issue_counts["llm_fallback"] += 1

        ai_report_payload = component_rows.get("ai_trade_report") or {}
        ai_report_status = str(ai_report_payload.get("status") or "").strip().lower()
        if lifecycle_status == "failed" and ai_report_status in {"partial", "salvaged", "repaired"}:
            issues.append(
                _issue(
                    severity="warn",
                    trade_id=trade_id,
                    component="lifecycle",
                    code="diagnostic_status_mismatch",
                    message=(
                        "Lifecycle diagnostics say failed, but an AI trade report artifact exists in "
                        f"{ai_report_status} state."
                    ),
                    path=lifecycle_path,
                )
            )
            issue_counts["diagnostic_status_mismatch"] += 1

    severity_counts = Counter(str(item.get("severity") or "info").lower() for item in issues)
    return {
        "ok": len([item for item in issues if str(item.get("severity") or "").lower() == "error"]) == 0,
        "reports_root": str(reports_root),
        "day": day,
        "trade_dir_count": len(trade_dirs),
        "llm_status_counts": dict(sorted(llm_status_counts.items())),
        "lifecycle_report_status_counts": dict(sorted(lifecycle_status_counts.items())),
        "issue_counts": dict(sorted(issue_counts.items())),
        "severity_counts": dict(sorted(severity_counts.items())),
        "duplicate_counts": dict(sorted(duplicate_counts.items())),
        "sidecar_counts": dict(sorted(sidecar_counts.items())),
        "issues": issues,
    }
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reports_trades_health_audit_projection.audit_reports_trades_health` passing `facade=sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade._iter_trade_dirs/_artifact_path/_issue/_read_json/_ai_trade_report_is_complete/facade.Counter. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_07h_b6_audit_reports_trades_health_owner.py` with fake/temp fixture and expected result: empty tmp root -> ok=True trade_dir_count=0 issues=[]; fake one trade without sidecars -> sidecar_missing count=3, ok=True. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reports_trades_health.py scripts/diagnostics/reports_trades_health_audit_projection.py`; `python -m unittest tests/test_p15_rf063_07h_b6_audit_reports_trades_health_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### B7 | RF-063 | `scripts/diagnostics/check_reports_trades_health.py::_build_parser` SOURCE blob `90853b7c3ec2a1bf85607a2253363fe376d46e9d` L261 (8 lines) → `scripts/diagnostics/reports_trades_health_cli.py::_build_parser`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only health audit for reports/trades artifacts.")
    parser.add_argument("--reports-root", default="reports")
    parser.add_argument("--day", default="")
    parser.add_argument("--json", action="store_true")
    return parser
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reports_trades_health_cli._build_parser` passing `facade=sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.argparse.ArgumentParser, never main. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_07h_b7_build_parser_owner.py` with fake/temp fixture and expected result: parse_args([]) -> reports_root reports, day '', json False; --day 2026-10-30 --json; unknown -> SystemExit(2). Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reports_trades_health.py scripts/diagnostics/reports_trades_health_cli.py`; `python -m unittest tests/test_p15_rf063_07h_b7_build_parser_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### B8 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_section_provenance_all_fallback` SOURCE blob `ab585cf1618d03df548543162a850900c1d2c008` L62 (11 lines) → `scripts/diagnostics/reporter_upgrade_provenance_projection.py::_section_provenance_all_fallback`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _section_provenance_all_fallback(report: Dict[str, Any]) -> bool:
    provenance = report.get("section_provenance") if isinstance(report.get("section_provenance"), dict) else {}
    if not provenance:
        return False
    entries = [value for value in provenance.values() if isinstance(value, dict)]
    if not entries:
        return False
    fallback_tags = {"fallback", "unknown", "missing"}
    return all(str(entry.get("source") or "").strip().lower() in fallback_tags for entry in entries)
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reporter_upgrade_provenance_projection._section_provenance_all_fallback` passing `facade=_migration_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure provenance predicate. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_07h_b8_section_provenance_all_fallback_owner.py` with fake/temp fixture and expected result: empty -> False; fallback+unknown sources -> True; mixed model -> False. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_provenance_projection.py`; `python -m unittest tests/test_p15_rf063_07h_b8_section_provenance_all_fallback_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

## SIX VERIFIED FUTURE RESERVES (6/6) — NOT EXECUTABLE NOW

Each reserve source function body was inspected at same owner HEAD, target independently 404 on owner and integration, safe fake/temp test designed; no implementation/test executed. Must re-fetch and revalidate after current order; changed/moved means RESERVE_NOT_VERIFIED, never reuse REMOTE_DONE.

### R1 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_read_json` SOURCE blob `ab585cf1618d03df548543162a850900c1d2c008` L26 (10 lines) → `scripts/diagnostics/reporter_upgrade_read_projection.py::_read_json`

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

**New normal targeted test:** `tests/test_p15_rf063_07h_r1_read_json_owner.py` with fake/temp fixture and expected result: missing/malformed/non-dict tmp -> {}; dict -> dict. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_read_projection.py`; `python -m unittest tests/test_p15_rf063_07h_r1_read_json_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

### R2 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_trade_dirs_for_day` SOURCE blob `ab585cf1618d03df548543162a850900c1d2c008` L36 (9 lines) → `scripts/diagnostics/reporter_upgrade_read_projection.py::_trade_dirs_for_day`

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

**New normal targeted test:** `tests/test_p15_rf063_07h_r2_trade_dirs_for_day_owner.py` with fake/temp fixture and expected result: temp day dir with b,a -> sorted a,b; missing -> []. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_read_projection.py`; `python -m unittest tests/test_p15_rf063_07h_r2_trade_dirs_for_day_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

### R3 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_is_closed_trade` SOURCE blob `ab585cf1618d03df548543162a850900c1d2c008` L45 (17 lines) → `scripts/diagnostics/reporter_upgrade_state_projection.py::_is_closed_trade`

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

**New normal targeted test:** `tests/test_p15_rf063_07h_r3_is_closed_trade_owner.py` with fake/temp fixture and expected result: lifecycle.exit nonempty -> True; status closed -> True; {} -> False. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_state_projection.py`; `python -m unittest tests/test_p15_rf063_07h_r3_is_closed_trade_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

### R4 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_reporter_section_fallback` SOURCE blob `ab585cf1618d03df548543162a850900c1d2c008` L73 (10 lines) → `scripts/diagnostics/reporter_upgrade_state_projection.py::_reporter_section_fallback`

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

**New normal targeted test:** `tests/test_p15_rf063_07h_r4_reporter_section_fallback_owner.py` with fake/temp fixture and expected result: reporter_evaluation fallback -> True; model or empty -> False. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_state_projection.py`; `python -m unittest tests/test_p15_rf063_07h_r4_reporter_section_fallback_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

### R5 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_missing_canonical_paths` SOURCE blob `ab585cf1618d03df548543162a850900c1d2c008` L83 (6 lines) → `scripts/diagnostics/reporter_upgrade_state_projection.py::_missing_canonical_paths`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _missing_canonical_paths(bundle: Dict[str, Any]) -> bool:
    artifacts = bundle.get("artifacts") if isinstance(bundle.get("artifacts"), dict) else {}
    values = [str(artifacts.get(key) or bundle.get(key) or "").strip() for key in CANONICAL_ARTIFACT_KEYS]
    return any(not value for value in values)
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `scripts.diagnostics.reporter_upgrade_state_projection._missing_canonical_paths` passing `facade=_migration_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.CANONICAL_ARTIFACT_KEYS. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf063_07h_r5_missing_canonical_paths_owner.py` with fake/temp fixture and expected result: six canonical artifact paths -> False; missing one -> True. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_state_projection.py`; `python -m unittest tests/test_p15_rf063_07h_r5_missing_canonical_paths_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

### R6 | RF-063 | `scripts/diagnostics/check_reporter_upgrade_regression.py::_thin_trace` SOURCE blob `ab585cf1618d03df548543162a850900c1d2c008` L89 (27 lines) → `scripts/diagnostics/reporter_upgrade_trace_projection.py::_thin_trace`

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

**New normal targeted test:** `tests/test_p15_rf063_07h_r6_thin_trace_owner.py` with fake/temp fixture and expected result: empty vs complete scanner/monitor trace; compare exact original booleans, malformed nested inputs. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile scripts/diagnostics/check_reporter_upgrade_regression.py scripts/diagnostics/reporter_upgrade_trace_projection.py`; `python -m unittest tests/test_p15_rf063_07h_r6_thin_trace_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

## REPORT AND CONTINUATION

Post to #12: `ORDER_ID=B-20261031-07 | CANONICAL_HEAD | OLD_ORDER_BLOB=3d8ff368883979cd6881929bcc3f36cc28167c04 | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA_BEFORE→AFTER | B1/B2/B3/B4/B5/B6/B7/B8 STATUS | SOURCE_BEFORE_AFTER_BLOBS/LOC | NEW_OWNER_BLOBS | TEST_NORMAL_COMMAND/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER | NEXT`. START/END/ELAPSED only if measured. If one blocked continue next safe item; if all complete, await next C03 supply. Do not count reserve or this documentation as G1/G2/G3/RF DONE.
