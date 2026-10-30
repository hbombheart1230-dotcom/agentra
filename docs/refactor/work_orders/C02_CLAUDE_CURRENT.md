# C02 — Claude A | Agentra FAST-3 | ORDER A-20261031-07 | EIGHT VERIFIED NEW BODY MOVEs

## CURRENT SINGLE-FILE EXECUTION CONTRACT (2026-10-31 07h)

Canonical `integration/p1.5` input HEAD `e84a1aeb1abd1f75f84261ec62de27152c0673fa`; A own remote HEAD `8bca83003ddb9bb753535f059d9a99b85f054297`; OLD_ORDER_BLOB `3cc2763655f94f5a1b272599b5576dfd9d798914`. On start pin CANONICAL_HEAD, ORDER_FILE_BLOB_SHA, OWNER_REMOTE_SHA and SOURCE blobs; if remote HEAD changes, verify before acting. Old A-06 is **REMOTE_DONE** (#11 6533638180: 8/8 moved, 26 normal PASS), no old MOVE or same-SHA test reissued. A-07 consists of the eight **new** numbered items below, all independently mandatory. New publication during a run does not invalidate pinned start order.

**Owner/safety:** RF-035 Claude A exclusively owns libs/reporting files; other Actor is read-only. Every SOURCE BODY below was inspected at the owner HEAD, and each new TARGET path independently returned **404 on both owner branch and integration**. Preserve public wrapper, monkeypatch seam, caller/exception/output parity; use fake/tmp only. No operational or real-trade effect, Broker/Guard/Step5C/UEF/RunLab, live network, subprocess, scheduler or production files. No D00/RF/queue/design re-reading, autonomous selection, Markdown/RF/STATUS/C04/C05/HANDOFF writes, other Actor branch edits or force push. Only own code and code tests. G1 remote code, G2 targeted normal exit0 and C04/C05 G3 are separate; this document is not development evidence.

**Execution and delivery:** Move each exact computation BODY to new single Owner and leave thin SOURCE wrapper. Build named `unittest` test with original/Owner/wrapper parity, negative and call-time monkeypatch. Run `python -m py_compile` and `python -m unittest tests/test_...py -v` normal exit0 for each; stdlib unittest avoids pytest installation dependence. Commit code/test only, normal approved push and re-fetch own HEAD + SOURCE/TARGET/TEST blobs. If Git HTTPS auth blocks push, report PUSH_BLOCKED (local commit is not G1), continue all other safe items; approved exact-tree ref update requires exact parent lease/refetch. First PASS, first commit, time spent, or one failure never ends remaining work. No -O/full peer/hosted CI as blanket requirements.

## EIGHT CURRENT VERIFIED SOURCE BODY MOVEs

### A1 | RF-035 | `libs/reporting/intraday_trade_reports.py::_read_lock_payload` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L118 (10 lines) → `libs/reporting/intraday_report_queue_read_projection.py::_read_lock_payload`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _read_lock_payload(path: Path) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {}
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_queue_read_projection._read_lock_payload` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.json.loads. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_a1_read_lock_payload_owner.py` with fake/temp fixture and expected result: missing temp lock -> {}; dict JSON -> dict; malformed/list -> {}; patched json.loads raises -> {}. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_queue_read_projection.py`; `python -m unittest tests/test_p15_rf035_07h_a1_read_lock_payload_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### A2 | RF-035 | `libs/reporting/intraday_trade_reports.py::_load_bundle_queue` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L551 (12 lines) → `libs/reporting/intraday_report_queue_read_projection.py::_load_bundle_queue`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _load_bundle_queue(path: Path) -> List[Dict[str, Any]]:
    try:
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            return []
        return [dict(row) for row in payload if isinstance(row, dict)]
    except Exception:
        return []
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_queue_read_projection._load_bundle_queue` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.json.loads. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_a2_load_bundle_queue_owner.py` with fake/temp fixture and expected result: JSON list [{'id':1},3,{'id':2}] -> [{'id':1},{'id':2}]; malformed/missing/nonlist -> []. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_queue_read_projection.py`; `python -m unittest tests/test_p15_rf035_07h_a2_load_bundle_queue_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### A3 | RF-035 | `libs/reporting/intraday_trade_reports.py::_build_bundle_argv` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L844 (34 lines) → `libs/reporting/intraday_report_command_projection.py::_build_bundle_argv`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _build_bundle_argv(root: Path, state: Dict[str, Any] | None = None) -> List[str]:
    runtime_state = state if isinstance(state, dict) else {}
    execution = runtime_state.get("execution") if isinstance(runtime_state.get("execution"), dict) else {}
    order = execution.get("order") if isinstance(execution.get("order"), dict) else {}
    run_id = str(runtime_state.get("run_id") or "").strip()
    symbol = _normalize_symbol(order.get("symbol") or execution.get("symbol") or runtime_state.get("symbol") or "")
    argv = [
        "--env-path",
        str(Path(os.getenv("ENV_PATH", str(root / ".env")))),
        "--event-log-path",
        str(Path(os.getenv("EVENT_LOG_PATH", str(root / "data" / "logs" / "events.jsonl")))),
        "--evidence-log-path",
        str(Path(os.getenv("EVIDENCE_LOG_PATH", str(root / "data" / "evidence_ledger" / "events.jsonl")))),
        "--report-dir",
        str(root / "reports" / "dev" / "analysis" / "live_execution_bundles"),
        "--reports-root",
        str(root / "reports"),
        "--intents-path",
        str(Path(os.getenv("INTENTS_PATH", str(root / "data" / "logs" / "intents.jsonl")))),
        "--role",
        _bundle_role(),
        "--trade-report-ai",
        "--json",
    ]
    if run_id:
        argv.extend(["--target-run-id", run_id])
    if symbol:
        argv.extend(["--target-symbol", symbol])
    day = _runtime_trade_day(runtime_state)
    if day:
        argv.extend(["--day", day])
    return argv
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_command_projection._build_bundle_argv` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.Path, facade.os.getenv, facade._normalize_symbol, facade._bundle_role, facade._runtime_trade_day. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_a3_build_bundle_argv_owner.py` with fake/temp fixture and expected result: tmp root, fake run_id=r symbol=005930, patched day -> argv includes --target-run-id r --target-symbol 005930 --day fake; preserve all flags. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_command_projection.py`; `python -m unittest tests/test_p15_rf035_07h_a3_build_bundle_argv_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### A4 | RF-035 | `libs/reporting/intraday_trade_reports.py::_stale_process_after_sec` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L755 (7 lines) → `libs/reporting/intraday_report_timeout_projection.py::_stale_process_after_sec`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _stale_process_after_sec() -> float:
    try:
        return max(30.0, float(os.getenv("INTRADAY_TRADE_REPORT_STALE_PROCESS_SEC", "180") or 180.0))
    except Exception:
        return 180.0
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_timeout_projection._stale_process_after_sec` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.os.getenv. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_a4_stale_process_after_sec_owner.py` with fake/temp fixture and expected result: fake getenv '12' -> 30.0, '60' -> 60.0, 'bad' -> 180.0. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_timeout_projection.py`; `python -m unittest tests/test_p15_rf035_07h_a4_stale_process_after_sec_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### A5 | RF-035 | `libs/reporting/trade_bundle_assembly.py::attach_strategy_anchor` SOURCE blob `f5c61ac32748c05e5070004e68fac96e2034119b` L178 (22 lines) → `libs/reporting/trade_bundle_strategy_anchor_projection.py::attach_strategy_anchor`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def attach_strategy_anchor(
    payload: Mapping[str, Any] | None,
    *,
    strategy_anchor_run_id: str,
    strategist_input_path: Path,
    strategist_compact_input_path: Path,
    strategist_llm_response_path: Path,
) -> Dict[str, Any]:
    out = dict(payload or {})
    out["entry_strategist_run_id"] = str(strategy_anchor_run_id or "")
    out["strategy_anchor_run_id"] = str(strategy_anchor_run_id or "")
    out["strategy_anchor"] = {
        "run_id": str(strategy_anchor_run_id or ""),
        "artifacts": {
            "strategist_input_json": str(strategist_input_path),
            "strategist_compact_input_json": str(strategist_compact_input_path),
            "strategist_llm_response_json": str(strategist_llm_response_path),
        },
    }
    return out
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.trade_bundle_strategy_anchor_projection.attach_strategy_anchor` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure dict computation. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_a5_attach_strategy_anchor_owner.py` with fake/temp fixture and expected result: {'x':1}, anchor r, tmp paths -> copied dict x preserved, nested anchor r, original input unchanged. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/trade_bundle_assembly.py libs/reporting/trade_bundle_strategy_anchor_projection.py`; `python -m unittest tests/test_p15_rf035_07h_a5_attach_strategy_anchor_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### A6 | RF-035 | `libs/reporting/trade_bundle_assembly.py::apply_strategy_anchor_metadata` SOURCE blob `f5c61ac32748c05e5070004e68fac96e2034119b` L200 (50 lines) → `libs/reporting/trade_bundle_strategy_anchor_projection.py::apply_strategy_anchor_metadata`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def apply_strategy_anchor_metadata(
    *,
    lifecycle: Dict[str, Any],
    lifecycle_bundle: Dict[str, Any],
    strategy_anchor_run_id: str,
    strategist_input_path: Path,
    strategist_compact_input_path: Path,
    strategist_llm_response_path: Path,
) -> Dict[str, Any]:
    lifecycle["entry_strategist_run_id"] = strategy_anchor_run_id
    lifecycle["strategy_anchor_run_id"] = strategy_anchor_run_id
    lifecycle["strategy_anchor"] = {
        "run_id": strategy_anchor_run_id,
        "source": "strategist_input_artifact" if strategy_anchor_run_id else "missing",
        "artifacts": {
            "strategist_input_json": str(strategist_input_path),
            "strategist_compact_input_json": str(strategist_compact_input_path),
            "strategist_llm_response_json": str(strategist_llm_response_path),
        },
    }
    lifecycle_bundle["entry_strategist_run_id"] = strategy_anchor_run_id
    lifecycle_bundle["strategy_anchor_run_id"] = strategy_anchor_run_id
    lifecycle_bundle["market_context_human"] = attach_strategy_anchor(
        lifecycle_bundle.get("market_context_human") if isinstance(lifecycle_bundle.get("market_context_human"), dict) else {},
        strategy_anchor_run_id=strategy_anchor_run_id,
        strategist_input_path=strategist_input_path,
        strategist_compact_input_path=strategist_compact_input_path,
        strategist_llm_response_path=strategist_llm_response_path,
    )
    lifecycle_bundle["scanner_reason_human"] = attach_strategy_anchor(
        lifecycle_bundle.get("scanner_reason_human") if isinstance(lifecycle_bundle.get("scanner_reason_human"), dict) else {},
        strategy_anchor_run_id=strategy_anchor_run_id,
        strategist_input_path=strategist_input_path,
        strategist_compact_input_path=strategist_compact_input_path,
        strategist_llm_response_path=strategist_llm_response_path,
    )
    lifecycle_bundle["monitor_reason_human"] = attach_strategy_anchor(
        lifecycle_bundle.get("monitor_reason_human") if isinstance(lifecycle_bundle.get("monitor_reason_human"), dict) else {},
        strategy_anchor_run_id=strategy_anchor_run_id,
        strategist_input_path=strategist_input_path,
        strategist_compact_input_path=strategist_compact_input_path,
        strategist_llm_response_path=strategist_llm_response_path,
    )
    return {
        "lifecycle": lifecycle,
        "lifecycle_bundle": lifecycle_bundle,
        "strategy_anchor_run_id": strategy_anchor_run_id,
    }
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.trade_bundle_strategy_anchor_projection.apply_strategy_anchor_metadata` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.attach_strategy_anchor; mutate only provided fake dicts. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_a6_apply_strategy_anchor_metadata_owner.py` with fake/temp fixture and expected result: empty lifecycle and bundle, anchor r, tmp paths -> same dict identities, nested anchors r; facade.attach_strategy_anchor spy called three times. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/trade_bundle_assembly.py libs/reporting/trade_bundle_strategy_anchor_projection.py`; `python -m unittest tests/test_p15_rf035_07h_a6_apply_strategy_anchor_metadata_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### A7 | RF-035 | `libs/reporting/intraday_trade_reports.py::_execution_action` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L814 (6 lines) → `libs/reporting/intraday_report_execution_projection.py::_execution_action`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _execution_action(state: Dict[str, Any]) -> str:
    execution = state.get("execution") if isinstance(state.get("execution"), dict) else {}
    order = execution.get("order") if isinstance(execution.get("order"), dict) else {}
    return str(order.get("action") or execution.get("action") or "").strip().upper()
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_execution_projection._execution_action` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure, order action precedence. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_a7_execution_action_owner.py` with fake/temp fixture and expected result: execution.order.action=' buy ' -> BUY; execution.action SELL fallback; {} -> ''. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_execution_projection.py`; `python -m unittest tests/test_p15_rf035_07h_a7_execution_action_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

### A8 | RF-035 | `libs/reporting/intraday_trade_reports.py::_execution_ok` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L820 (5 lines) → `libs/reporting/intraday_report_execution_projection.py::_execution_ok`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _execution_ok(state: Dict[str, Any]) -> bool:
    execution = state.get("execution") if isinstance(state.get("execution"), dict) else {}
    return bool(execution.get("ok")) and bool(execution.get("allowed", True))
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_execution_projection._execution_ok` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure, allowed default True. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_a8_execution_ok_owner.py` with fake/temp fixture and expected result: execution ok=True, allowed omitted -> True; allowed False -> False; {} -> False. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_execution_projection.py`; `python -m unittest tests/test_p15_rf035_07h_a8_execution_ok_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. Implement and test this mandatory item; commit code/test only on own branch, normal push and re-fetch exact HEAD/source/target/test blob. If blocked, record FIRST_BLOCKER and continue next item.

## SIX VERIFIED FUTURE RESERVES (6/6) — NOT EXECUTABLE NOW

Each reserve source function body was inspected at same owner HEAD, target independently 404 on owner and integration, safe fake/temp test designed; no implementation/test executed. Must re-fetch and revalidate after current order; changed/moved means RESERVE_NOT_VERIFIED, never reuse REMOTE_DONE.

### R1 | RF-035 | `libs/reporting/intraday_trade_reports.py::_is_trueish` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L64 (4 lines) → `libs/reporting/intraday_report_scalar_projection.py::_is_trueish`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _is_trueish(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_scalar_projection._is_trueish` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_r1_is_trueish_owner.py` with fake/temp fixture and expected result: ' YES ' -> True; 0 and None -> False. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_scalar_projection.py`; `python -m unittest tests/test_p15_rf035_07h_r1_is_trueish_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

### R2 | RF-035 | `libs/reporting/intraday_trade_reports.py::_normalize_symbol` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L68 (4 lines) → `libs/reporting/intraday_report_scalar_projection.py::_normalize_symbol`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_scalar_projection._normalize_symbol` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_r2_normalize_symbol_owner.py` with fake/temp fixture and expected result: ' 005930 ' -> '005930'; ab -> AB; None -> ''. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_scalar_projection.py`; `python -m unittest tests/test_p15_rf035_07h_r2_normalize_symbol_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

### R3 | RF-035 | `libs/reporting/intraday_trade_reports.py::_stable_json_text` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L132 (4 lines) → `libs/reporting/intraday_report_scalar_projection.py::_stable_json_text`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _stable_json_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_scalar_projection._stable_json_text` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.json.dumps. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_r3_stable_json_text_owner.py` with fake/temp fixture and expected result: {'b':2,'a':1} -> compact sorted JSON; unicode not escaped. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_scalar_projection.py`; `python -m unittest tests/test_p15_rf035_07h_r3_stable_json_text_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

### R4 | RF-035 | `libs/reporting/intraday_trade_reports.py::_payload_fingerprint` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L136 (4 lines) → `libs/reporting/intraday_report_scalar_projection.py::_payload_fingerprint`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _payload_fingerprint(payload: Any) -> str:
    return hashlib.sha256(_stable_json_text(payload).encode("utf-8")).hexdigest()
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_scalar_projection._payload_fingerprint` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade._stable_json_text/facade.hashlib.sha256. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_r4_payload_fingerprint_owner.py` with fake/temp fixture and expected result: {'a':1} -> sha256 stable JSON; patch facade._stable_json_text changes hash. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_scalar_projection.py`; `python -m unittest tests/test_p15_rf035_07h_r4_payload_fingerprint_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

### R5 | RF-035 | `libs/reporting/intraday_trade_reports.py::_brief_cache_dir` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L104 (6 lines) → `libs/reporting/intraday_report_path_projection.py::_brief_cache_dir`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _brief_cache_dir(root: Path) -> Path:
    return Path(
        os.getenv("OPERATOR_UI_CACHE_PATH", str(root / "data" / "operator_ui" / "brief_cache"))
    )
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_path_projection._brief_cache_dir` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.os.getenv/facade.Path; no mkdir. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_r5_brief_cache_dir_owner.py` with fake/temp fixture and expected result: tmp root and fake env -> tmp/cache; default -> root/data/operator_ui/brief_cache. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_path_projection.py`; `python -m unittest tests/test_p15_rf035_07h_r5_brief_cache_dir_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

### R6 | RF-035 | `libs/reporting/intraday_trade_reports.py::_script_path` SOURCE blob `2876a2301fa83cb09c6ee0d13e927214e7f07b1f` L96 (4 lines) → `libs/reporting/intraday_report_path_projection.py::_script_path`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _script_path(root: Path) -> Path:
    return root / "scripts" / "run_live_execution_bundle_report.py"
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_path_projection._script_path` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure path join, no execute. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_07h_r6_script_path_owner.py` with fake/temp fixture and expected result: tmp root -> root/scripts/run_live_execution_bundle_report.py. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_path_projection.py`; `python -m unittest tests/test_p15_rf035_07h_r6_script_path_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. VERIFIED DESIGN RESERVE ONLY: NOT assigned; do not implement until C03 next order after new source/target revalidation.

## REPORT AND CONTINUATION

Post to #11: `ORDER_ID=A-20261031-07 | CANONICAL_HEAD | OLD_ORDER_BLOB=3cc2763655f94f5a1b272599b5576dfd9d798914 | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA_BEFORE→AFTER | A1/A2/A3/A4/A5/A6/A7/A8 STATUS | SOURCE_BEFORE_AFTER_BLOBS/LOC | NEW_OWNER_BLOBS | TEST_NORMAL_COMMAND/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER | NEXT`. START/END/ELAPSED only if measured. If one blocked continue next safe item; if all complete, await next C03 supply. Do not count reserve or this documentation as G1/G2/G3/RF DONE.
