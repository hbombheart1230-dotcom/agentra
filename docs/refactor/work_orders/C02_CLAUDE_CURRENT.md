# C02 — Claude A | A-20261101-02 | FAST-3 8 verified real SOURCE BODY MOVEs

**START ORDER — ONE FILE ONLY.** Read THIS document, then only the named code/test files. Do not read D00/RF/queue/C03/HANDOFF or select tasks yourself. Pin canonical HEAD `9e47ed5230d68814688ff6b48ae2764a8a25222f` (pre-issue), ORDER_BLOB, actor branch HEAD, and ORDER_ID at start; newer documents do not retroactively cancel a started order. Run ALL eight items; if blocked, record precise reason and proceed to the next independent safe item. Never redo completed old order. 

**EVIDENCE:** C03 compared actor/integration exact source blobs, SOURCE original executable bodies, unique target path absence on both refs, RF ownership, and recent #11/#12/#32. Actor A old order A-20261101-01 8/8 REMOTE_DONE at 0cc2d549; B old order B-21 B1–B3 REMOTE_DONE at 30295cc1, B4–B8 remain unfinished and are carried as B1–B5 here, with B6–B8 new. Current C01 old blob `b9f6a1dfcc6e0ca746c738f80e599a12fe54ae49`, C02 old blob `606eb2ce8baaa1abf36b366675f9208878b0745c`. RunLab Exited(255), RUN_SOURCE_SHA=UNKNOWN, operational HOLD. No C03 code/test work or RF DONE is claimed.

**RF/OWNER:** RF-035; CLAUDE_A exclusively owns all named source and target files. Actor writes only its `work/p15-a-reporter-pure-20261021` code/test paths; no D00, RF, queue, STATUS, C04/C05, other actor branch, CI/frozen oracle, Git force-push. All eight target paths confirmed absent on actor and integration before issue. C04 performs selective integration/G3; C05 alone accepts RF DONE.

**SAFETY:** isolated fake in-memory mappings, monkeypatch and TemporaryDirectory only. No real trading, broker, order, guard, Step5C, UEF, RunLab operations, live network, runtime process/queue/lock mutation, operational State/DB/report paths, subprocess, actual CLI main, deploy/restart, or security policy change. Paths/env in these helpers must be fake/patched. Preserve exact public signatures, return type, exceptions, ordering, CLI callers, and SOURCE call-time monkeypatch seams. Source function must become a single-return thin delegation; new Owner must hold the ORIGINAL computation body, never import SOURCE (pass `facade=sys.modules[__name__]` when source globals are referenced). Use import inside SOURCE wrapper or safe top-level alias, no cycles. Capture original preimage golden before edits; compare golden vs SOURCE wrapper vs Owner with positive, negative, exception, and post-import monkeypatch cases; AST prove retired SOURCE calculation body absent, no duplicate/orphan statements.

**TEST/PUSH:** Create NEW `tests/test_p15_rf035_20261101_02h_reporting_owners.py` (do not overwrite old B21/A01 tests). Each test must pin exact input→expected below, original golden parity, Owner direct parity, thin-wrapper AST and patch seams. Run `python -m py_compile` on modified source and all new Owner modules; run `python -m unittest tests/test_p15_rf035_20261101_02h_reporting_owners.py -v` normal exit0; use safe isolated tests only. Commit ONLY actor code/test; normal non-force push actor branch; re-fetch actor HEAD and source/target/test blob SHAs. If pytest unavailable, stdlib unittest remains valid. If push authentication fails, mark PUSH_BLOCKED but continue other safe items. Report each item IMPLEMENTED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN with measured START/END, normal command exit and exact remote SHA to #11; do not claim G1 for local-only. No mandatory -O/full peer/per-RF hosted CI.

## A1 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_stale_process_after_sec` @ L575 | CURRENT_BLOB `4d49f344036dd15580976b0c6e7222cbcce25e16`
**NEW TARGET (404 on actor and integration):** `libs/reporting/live_bundle_stale_timeout_projection.py::_stale_process_after_sec`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
```python
def _stale_process_after_sec() -> float:
    try:
        return max(30.0, float(os.getenv("INTRADAY_TRADE_REPORT_STALE_PROCESS_SEC", "180") or 180.0))
    except Exception:
        return 180.0
```
**Exact SOURCE thin-wrapper executable statement:** `return _stale_timeout_owner._stale_process_after_sec(facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `libs.reporting.live_bundle_stale_timeout_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade.os.getenv; never query/terminate real processes. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_a1_stale_process_after_sec`:** os.getenv('INTRADAY_TRADE_REPORT_STALE_PROCESS_SEC') patched to '12'→30.0; '45'→45.0; 'bad'→180.0. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue A2.

## A2 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_background_job_lock_path` @ L250 | CURRENT_BLOB `4d49f344036dd15580976b0c6e7222cbcce25e16`
**NEW TARGET (404 on actor and integration):** `libs/reporting/live_bundle_lock_path_projection.py::_background_job_lock_path`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
```python
def _background_job_lock_path() -> Path | None:
    raw = str(os.getenv("INTRADAY_TRADE_REPORT_JOB_LOCK_PATH") or "").strip()
    if raw:
        return Path(raw)
    return ROOT / "reports" / "runtime" / "intraday_trade_report_bundle.lock"
```
**Exact SOURCE thin-wrapper executable statement:** `return _lock_path_owner._background_job_lock_path(facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `libs.reporting.live_bundle_lock_path_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade.os.getenv/Path/ROOT; compute path only; never write lock. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_a2_background_job_lock_path`:** facade.ROOT=Path('/tmp/fake'), getenv empty→Path('/tmp/fake/reports/runtime/intraday_trade_report_bundle.lock'); getenv='/tmp/custom.lock'→Path('/tmp/custom.lock'). Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue A3.

## A3 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_background_job_queue_path` @ L257 | CURRENT_BLOB `4d49f344036dd15580976b0c6e7222cbcce25e16`
**NEW TARGET (404 on actor and integration):** `libs/reporting/live_bundle_queue_path_projection.py::_background_job_queue_path`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
```python
def _background_job_queue_path() -> Path:
    return ROOT / "reports" / "runtime" / "intraday_trade_report_bundle.queue.json"
```
**Exact SOURCE thin-wrapper executable statement:** `return _queue_path_owner._background_job_queue_path(facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `libs.reporting.live_bundle_queue_path_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade.ROOT; never read/write operational queue. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_a3_background_job_queue_path`:** facade.ROOT=Path('/tmp/fake')→Path('/tmp/fake/reports/runtime/intraday_trade_report_bundle.queue.json'). Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue A4.

## A4 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_read_json` @ L769 | CURRENT_BLOB `4d49f344036dd15580976b0c6e7222cbcce25e16`
**NEW TARGET (404 on actor and integration):** `libs/reporting/live_bundle_json_read_projection.py::_read_json`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
```python
def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}
```
**Exact SOURCE thin-wrapper executable statement:** `return _json_read_owner._read_json(path, facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `libs.reporting.live_bundle_json_read_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade.json; temp paths only; no operational State/DB. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_a4_read_json`:** TemporaryDirectory file '{"a":1}'→{'a':1}; malformed→{}; absent→{}. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue A5.

## A5 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_iter_jsonl` @ L751 | CURRENT_BLOB `4d49f344036dd15580976b0c6e7222cbcce25e16`
**NEW TARGET (404 on actor and integration):** `libs/reporting/live_bundle_jsonl_iter_projection.py::_iter_jsonl`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
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
**Exact SOURCE thin-wrapper executable statement:** `return _jsonl_iter_owner._iter_jsonl(path, facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `libs.reporting.live_bundle_jsonl_iter_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade.json; preserve list/iteration order; temp paths only. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_a5_iter_jsonl`:** temp JSONL '{"a":1}\nBAD\n[]\n'→[{'a':1}]; absent→[]. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue A6.

## A6 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_build_trade_id` @ L1114 | CURRENT_BLOB `4d49f344036dd15580976b0c6e7222cbcce25e16`
**NEW TARGET (404 on actor and integration):** `libs/reporting/live_bundle_trade_id_projection.py::_build_trade_id`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
```python
def _build_trade_id(day: str, symbol: str, seq: int) -> str:
    compact_day = str(day or "").replace("-", "")
    clean_symbol = normalize_symbol(symbol or "", allow_test_symbols=True) or "UNKNOWN"
    return f"TRD_{compact_day}_{clean_symbol}_{int(seq):02d}"
```
**Exact SOURCE thin-wrapper executable statement:** `return _trade_id_owner._build_trade_id(day, symbol, seq, facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `libs.reporting.live_bundle_trade_id_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade.normalize_symbol at invocation; pure string only; never create actual trade/order. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_a6_build_trade_id`:** patch facade.normalize_symbol→'005930'; ('2026-11-01','005930',2)→'TRD_20261101_005930_02'. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue A7.

## A7 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_items` @ L13 | CURRENT_BLOB `1e837b5bf9739a6e1a7aaa7775a23591b2bfcc7f`
**NEW TARGET (404 on actor and integration):** `libs/reporting/quant_tactic_items_projection.py::_items`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
```python
def _items(value: Any) -> List[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item or "").strip() for item in value if str(item or "").strip()]
```
**Exact SOURCE thin-wrapper executable statement:** `return _items_owner._items(value)` (keep original signature, annotations, and any docstring; import `libs.reporting.quant_tactic_items_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** pure list/tuple normalization; no runtime classifier. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_a7_items`:** [' A ',None,'B','']→['A','B']; {'x':1}→[]. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue A8.

## A8 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_fmt` @ L19 | CURRENT_BLOB `1e837b5bf9739a6e1a7aaa7775a23591b2bfcc7f`
**NEW TARGET (404 on actor and integration):** `libs/reporting/quant_tactic_fmt_projection.py::_fmt`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
```python
def _fmt(value: Any) -> str:
    if value in (None, ""):
        return "-"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)
```
**Exact SOURCE thin-wrapper executable statement:** `return _fmt_owner._fmt(value)` (keep original signature, annotations, and any docstring; import `libs.reporting.quant_tactic_fmt_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** pure string formatting; preserve float precision. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_a8_fmt`:** None→'-'; 1.2500→'1.25'; 'abc'→'abc'. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue all remaining tests, commit/push and remote re-fetch.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY; NOT PART OF THIS ORDER
All six are distinct, current actor/integration SOURCE bodies and unique absent target paths; not executable until C03 fresh issuance. Never count reserve as G1 or reuse previous completed work.

### R1 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_mapping` @ L9 | CURRENT_BLOB `1e837b5bf9739a6e1a7aaa7775a23591b2bfcc7f`
**TARGET absent actor/integration:** `libs/reporting/quant_tactic_mapping_projection.py::_mapping`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value or {}) if isinstance(value, Mapping) else {}
```
**Future isolated normal test:** {'x':1}→{'x':1}; []→{}. **Safety/seam:** Mapping (facade if patching); no IO; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

### R2 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_pct` @ L27 | CURRENT_BLOB `1e837b5bf9739a6e1a7aaa7775a23591b2bfcc7f`
**TARGET absent actor/integration:** `libs/reporting/quant_tactic_pct_projection.py::_pct`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _pct(value: Any) -> str:
    if value in (None, ""):
        return "-"
    try:
        num = float(value)
    except Exception:
        return str(value)
    return f"{num * 100.0:.2f}%"
```
**Future isolated normal test:** 0.125→'12.50%'; None→'-'; 'bad'→'bad'. **Safety/seam:** pure numeric formatting; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

### R3 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_decision_label` @ L37 | CURRENT_BLOB `1e837b5bf9739a6e1a7aaa7775a23591b2bfcc7f`
**TARGET absent actor/integration:** `libs/reporting/quant_tactic_decision_label_projection.py::_decision_label`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _decision_label(value: Any) -> str:
    raw = str(value or "").strip()
    mapping = {
        "entry_ready": "진입 준비",
        "block_recommended": "진입 차단 권고",
        "wait": "대기",
        "hold_watch": "보유 관찰",
        "hard_exit": "즉시 청산 허용",
        "confirm_before_exit_recommended": "청산 전 확인 권고",
        "early_exit_warning": "조기 청산 경고",
        "exit_aligned": "청산 정합",
    }
    return mapping.get(raw, raw or "-")
```
**Future isolated normal test:** 'entry_ready'→'진입 준비'; 'unknown'→'unknown'. **Safety/seam:** pure lookup, no policy mutation; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

### R4 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_reason_text` @ L52 | CURRENT_BLOB `1e837b5bf9739a6e1a7aaa7775a23591b2bfcc7f`
**TARGET absent actor/integration:** `libs/reporting/quant_tactic_reason_text_projection.py::_reason_text`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _reason_text(values: Any) -> str:
    rows = _items(values)
    return ", ".join(rows[:5]) if rows else "-"
```
**Future isolated normal test:** ['a','b']→'a, b'; []→'-'. **Safety/seam:** call-time facade._items; pure; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

### R5 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_monitor` @ L57 | CURRENT_BLOB `1e837b5bf9739a6e1a7aaa7775a23591b2bfcc7f`
**TARGET absent actor/integration:** `libs/reporting/quant_tactic_monitor_projection.py::_monitor`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _monitor(report: Mapping[str, Any]) -> Dict[str, Any]:
    monitor = _mapping(report.get("monitor_snapshot"))
    if not monitor:
        monitor = _mapping(report.get("monitor_output"))
    return monitor
```
**Future isolated normal test:** {'monitor_output':{'x':1}}→{'x':1}. **Safety/seam:** call-time facade._mapping; no monitor runtime calls; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

### R6 | RF-035 | CLAUDE_A | SOURCE `libs/reporting/quant_tactic_report.py::_nested_dicts` @ L64 | CURRENT_BLOB `1e837b5bf9739a6e1a7aaa7775a23591b2bfcc7f`
**TARGET absent actor/integration:** `libs/reporting/quant_tactic_nested_dicts_projection.py::_nested_dicts`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _nested_dicts(value: Any, *, max_depth: int = 9) -> List[Dict[str, Any]]:
    if max_depth < 0:
        return []
    out: List[Dict[str, Any]] = []
    if isinstance(value, Mapping):
        item = dict(value)
        out.append(item)
        for child in item.values():
            out.extend(_nested_dicts(child, max_depth=max_depth - 1))
    elif isinstance(value, (list, tuple)):
        for child in value:
            out.extend(_nested_dicts(child, max_depth=max_depth - 1))
    return out
```
**Future isolated normal test:** {'a':{'b':1}} max_depth=1→[{'a':{'b':1}},{'b':1}]. **Safety/seam:** call-time facade.Mapping/_nested_dicts recursion; fake data; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

**G1/G2/G3:** This C03 document issue is supply only, not code implementation/test/integration or RF DONE. Source/target conflicts, operational effects, missing tests or push failures are individually BLOCKED, never silently PASS. C04/C05 retain their exclusive gates.
