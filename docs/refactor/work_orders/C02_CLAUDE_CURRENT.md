# C02 — Claude A | Agentra FAST-3 | ORDER A-20261031-08 | EIGHT NEW VERIFIED BODY MOVEs

## CURRENT SINGLE-FILE EXECUTION CONTRACT (2026-10-31 08h)

Canonical input HEAD `feba2f3a032860135c181f76d034464334cafaa5`; A owner remote HEAD `8256523b1222de59ac4c4978d3937b9cd3a092aa`; OLD_ORDER_BLOB `b251450dfc5fbbb21b9143793bd47208750f7eba`. The prior 07h order was **REMOTE_DONE 8/8** based on #11 07h delta and remote owner HEAD; do not reissue its moved BODY or repeat same-SHA tests. Pin CANONICAL_HEAD, ORDER_FILE_BLOB_SHA, OWNER_REMOTE_SHA, SOURCE_BLOB at start. New document publication during actor execution does not invalidate pinned start order.

**Owner and safety:** RF-035; Claude A owns only the specified libs/reporting code/test paths. Each new TARGET file was checked **404 on both integration and actor owner branch** before issuance. All SOURCE functions were inspected at owner remote HEAD and are currently un-moved. Do not touch other Actor code, docs, RF, queue, STATUS, D00, C03/C04/C05, HANDOFF, CI workflows, frozen tests or live runtime. No Broker/Guard/Step5C/UEF/RunLab effect, production DB/State, real orders, network or force push. Only fake/temp targeted normal unittest/smoke.

**All eight items are mandatory and independent:** Move actual SOURCE computation BODY into the single new TARGET Owner; keep thin public SOURCE wrapper, exact caller behavior and call-time monkeypatch parity. Execute each targeted normal test exit0 and py_compile; do not require blanket -O/full peer/hosted CI. Commit own code/test and push normally, then re-fetch remote HEAD and changed blobs. Git auth failure blocks push only, pytest missing can use stdlib unittest; continue every other safe item even after one PASS, blocker or local commit. Do not claim local-only G1, C03 docs as development, or RF DONE. C04 integration and C05 G1/G2/G3 are separate.

## EIGHT CURRENT VERIFIED SOURCE BODY MOVEs

### A1 | RF-035 | `libs/reporting/intraday_trade_reports.py::_is_trueish` SOURCE blob `31cc169edeafa33db93d58ea103b2ac9ad77af56` L64 (4 lines) → `libs/reporting/intraday_report_scalar_projection.py::_is_trueish`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _is_trueish(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_scalar_projection._is_trueish` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_08h_a1_is_trueish_owner.py` with fake/temp fixture and expected result: ' YES ' -> True; 0 and None -> False. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_scalar_projection.py`; `python -m unittest tests/test_p15_rf035_08h_a1_is_trueish_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### A2 | RF-035 | `libs/reporting/intraday_trade_reports.py::_normalize_symbol` SOURCE blob `31cc169edeafa33db93d58ea103b2ac9ad77af56` L68 (4 lines) → `libs/reporting/intraday_report_scalar_projection.py::_normalize_symbol`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_scalar_projection._normalize_symbol` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_08h_a2_normalize_symbol_owner.py` with fake/temp fixture and expected result: ' 005930 ' -> '005930'; ab -> AB; None -> ''. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_scalar_projection.py`; `python -m unittest tests/test_p15_rf035_08h_a2_normalize_symbol_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### A3 | RF-035 | `libs/reporting/intraday_trade_reports.py::_stable_json_text` SOURCE blob `31cc169edeafa33db93d58ea103b2ac9ad77af56` L132 (4 lines) → `libs/reporting/intraday_report_scalar_projection.py::_stable_json_text`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _stable_json_text(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_scalar_projection._stable_json_text` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.json.dumps. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_08h_a3_stable_json_text_owner.py` with fake/temp fixture and expected result: {'b':2,'a':1} -> compact sorted JSON; unicode not escaped. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_scalar_projection.py`; `python -m unittest tests/test_p15_rf035_08h_a3_stable_json_text_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### A4 | RF-035 | `libs/reporting/intraday_trade_reports.py::_payload_fingerprint` SOURCE blob `31cc169edeafa33db93d58ea103b2ac9ad77af56` L136 (4 lines) → `libs/reporting/intraday_report_scalar_projection.py::_payload_fingerprint`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _payload_fingerprint(payload: Any) -> str:
    return hashlib.sha256(_stable_json_text(payload).encode("utf-8")).hexdigest()
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_scalar_projection._payload_fingerprint` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade._stable_json_text/facade.hashlib.sha256. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_08h_a4_payload_fingerprint_owner.py` with fake/temp fixture and expected result: {'a':1} -> sha256 stable JSON; patch facade._stable_json_text changes hash. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_scalar_projection.py`; `python -m unittest tests/test_p15_rf035_08h_a4_payload_fingerprint_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### A5 | RF-035 | `libs/reporting/intraday_trade_reports.py::_brief_cache_dir` SOURCE blob `31cc169edeafa33db93d58ea103b2ac9ad77af56` L104 (6 lines) → `libs/reporting/intraday_report_path_projection.py::_brief_cache_dir`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _brief_cache_dir(root: Path) -> Path:
    return Path(
        os.getenv("OPERATOR_UI_CACHE_PATH", str(root / "data" / "operator_ui" / "brief_cache"))
    )
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_path_projection._brief_cache_dir` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: facade.os.getenv/facade.Path; no mkdir. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_08h_a5_brief_cache_dir_owner.py` with fake/temp fixture and expected result: tmp root and fake env -> tmp/cache; default -> root/data/operator_ui/brief_cache. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_path_projection.py`; `python -m unittest tests/test_p15_rf035_08h_a5_brief_cache_dir_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### A6 | RF-035 | `libs/reporting/intraday_trade_reports.py::_script_path` SOURCE blob `31cc169edeafa33db93d58ea103b2ac9ad77af56` L96 (4 lines) → `libs/reporting/intraday_report_path_projection.py::_script_path`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _script_path(root: Path) -> Path:
    return root / "scripts" / "run_live_execution_bundle_report.py"
```

**Thin compatibility wrapper/caller/patch seam:** Preserve exact SOURCE signature, defaults, annotations, docstring, output ordering, identity, exceptions and lazy behavior. Replace body with one delegation to `libs.reporting.intraday_report_path_projection._script_path` passing `facade=_r3_sys.modules[__name__]` when global references require it. TARGET must not import SOURCE. Use facade.NAME at call time for module globals; locals/builtins unchanged. Specific: pure path join, no execute. When TARGET has earlier functions, append rather than overwrite. Caller imports unchanged; no duplicate BODY in SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_08h_a6_script_path_owner.py` with fake/temp fixture and expected result: tmp root -> root/scripts/run_live_execution_bundle_report.py. Assert original baseline vs new Owner vs thin wrapper equality (including negative exception type/message and monkeypatch after import). `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_path_projection.py`; `python -m unittest tests/test_p15_rf035_08h_a6_script_path_owner.py -v` **normal exit0**, record actual command/exit; no mandatory -O/full peer/hosted CI. No production paths, network, subprocess, broker, Guard, Step5C, UEF, real state, RunLab, scheduler or live calls. MANDATORY NOW: move actual BODY, normal test, commit code/test and push; if blocked record exact reason and continue next item.

### A7 | RF-035 | `libs/reporting/intraday_trade_reports.py::_bundle_job_lock_path` SOURCE blob `31cc169edeafa33db93d58ea103b2ac9ad77af56` L114 → `libs/reporting/intraday_report_queue_path_projection.py::_bundle_job_lock_path`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _bundle_job_lock_path(root: Path) -> Path:
    return root / "reports" / "runtime" / "intraday_trade_report_bundle.lock"
```

**Thin compatibility wrapper/caller/monkeypatch:** Preserve exact signature, defaults, annotations, return/exception and caller import. Keep SOURCE as a one-call wrapper to the new Owner function; TARGET must not import SOURCE. Pure Path joining; preserve original path and no filesystem writes. Resolve module globals via `facade` at call time where needed, preserving post-import monkeypatch. No duplicate calculation remains in SOURCE; do not alter CLI/operational effects.

**New normal targeted test:** `tests/test_p15_rf035_08h_a7_bundle_job_lock_path_owner.py`. For temp root expect root/reports/runtime/intraday_trade_report_bundle.lock; path not created. Compare pre-move baseline, Owner and wrapper outputs and exception parity; mock module globals after import. `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_queue_path_projection.py`; `python -m unittest tests/test_p15_rf035_08h_a7_bundle_job_lock_path_owner.py -v` normal exit0. Use fake/tmp only; no live network, production state, real order, Broker/Guard/Step5C/UEF/RunLab, scheduler or subprocess. Commit only own code/test, normal push, re-fetch exact owner HEAD and SOURCE/TARGET/test blob. If blocked, record FIRST_BLOCKER and continue next mandatory item.

### A8 | RF-035 | `libs/reporting/intraday_trade_reports.py::_bundle_job_queue_path` SOURCE blob `31cc169edeafa33db93d58ea103b2ac9ad77af56` L118 → `libs/reporting/intraday_report_queue_path_projection.py::_bundle_job_queue_path`

**EXACT SOURCE COMPUTATION BODY — MOVE, do not duplicate:**
```python
def _bundle_job_queue_path(root: Path) -> Path:
    return root / "reports" / "runtime" / "intraday_trade_report_bundle.queue.json"
```

**Thin compatibility wrapper/caller/monkeypatch:** Preserve exact signature, defaults, annotations, return/exception and caller import. Keep SOURCE as a one-call wrapper to the new Owner function; TARGET must not import SOURCE. Pure Path joining; preserve original path and no filesystem writes. Resolve module globals via `facade` at call time where needed, preserving post-import monkeypatch. No duplicate calculation remains in SOURCE; do not alter CLI/operational effects.

**New normal targeted test:** `tests/test_p15_rf035_08h_a8_bundle_job_queue_path_owner.py`. For temp root expect root/reports/runtime/intraday_trade_report_bundle.queue.json; path not created. Compare pre-move baseline, Owner and wrapper outputs and exception parity; mock module globals after import. `python -m py_compile libs/reporting/intraday_trade_reports.py libs/reporting/intraday_report_queue_path_projection.py`; `python -m unittest tests/test_p15_rf035_08h_a8_bundle_job_queue_path_owner.py -v` normal exit0. Use fake/tmp only; no live network, production state, real order, Broker/Guard/Step5C/UEF/RunLab, scheduler or subprocess. Commit only own code/test, normal push, re-fetch exact owner HEAD and SOURCE/TARGET/test blob. If blocked, record FIRST_BLOCKER and continue next mandatory item.

## SIX FUTURE RESERVES — RESERVE_NOT_VERIFIED (0/6)

The six prior 07h reserves A-R1..R6 are consumed as A1..A6 in this order. **Do not** count them as reserves or implement any unassigned candidate. Next C03 must inspect six fresh actual SOURCE bodies, exclusive TARGET nonexistence, RF ownership, effects and targeted test before marking VERIFIED. Candidate scanning may begin with remaining pure reporter path/time/format helpers, but no unverified name is an executable order.

## REPORT AND CONTINUATION

Post #11: `ORDER_ID=A-20261031-08 | CANONICAL_HEAD | OLD_ORDER_BLOB=b251450dfc5fbbb21b9143793bd47208750f7eba | ORDER_FILE_BLOB_SHA | OWNER_REMOTE_SHA_BEFORE→AFTER | A1..A8 per-item IMPLEMENTED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED | SOURCE_BEFORE_AFTER_BLOBS | TARGET_BLOBS | NORMAL_TEST_COMMAND/EXIT | PUSH_REMOTE_SHA | FIRST_BLOCKER | NEXT`. START/END/ELAPSED only measured; reserves not executable.