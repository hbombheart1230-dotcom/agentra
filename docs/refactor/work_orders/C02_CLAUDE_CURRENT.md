# C02 — Claude A | A-20261101-01 | FAST-3 NEW 8 VERIFIED SOURCE BODY MOVEs + one regression guard repair

**INPUT_SHA:** integration bda559f8931c8184f5693b7f8196d60b96701569 | A remote 0add890cd2484edcfe730cc177311a7f3f8fbf5e | B remote 32ed205327a36f2041ebd9a3257c02cba1cd41cd | OLD_C02_BLOB ce3fca564cbb33ea4e7de33e17ea3f6a93501446 | C01_BLOB fb882c992842fc133138c5726b525f4c521d3f6e | SOURCE_BLOB a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501 (identical A/integration verified earlier this run).
**NEW DELTA:** #11 comment 6545319970: A-20261101-00 8/8 actual BODY MOVE pushed 0add890cd2484edcfe730cc177311a7f3f8fbf5e, targeted unittest 8/8 exit0; previous C02 is REMOTE_DONE and must NOT be replayed. A reported one new structural guard failure in `tests/test_closeout_payload_projection.py` because `build_quant_shadow_candidate_evaluation` body moved to its new owner. #12 comment 6545189506: B3 `_evaluate` local fake test 3/3 but duplicate legacy body, NOT_DELIVERED; B remote unchanged 32ed205327a36f2041ebd9a3257c02cba1cd41cd and B3-B8 remain six remote-available safe items; C01 retained. #32 latest 6520075820 runtime Exited(255), RUN_SOURCE_SHA UNKNOWN, operational HOLD.
**RF OWNER:** RF-035 / CLAUDE_A exclusive `libs/reporting` per current RF-035 source coverage and source ownership; this is report-bundle pure projection extraction, NOT actual trading. SOURCE `libs/reporting/live_execution_bundle_runner.py` at current blob `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`; no Actor B source/target overlap. All 8 new TARGETs and 6 reserve TARGETs absent in integration and A directory inventory; test path absent on both.
**ONE FILE:** Read ONLY C02 and code/test paths below. No D00/RF/queue/C03/HANDOFF. Pin start canonical HEAD, C02 blob, A remote HEAD and ORDER_ID. Execute ALL eight A1-A8 independently, mark exact per-item IMPLEMENTED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED; blocked item => continue remaining safe items. Do not self-select work. Do not redo completed A-00 or claim KEEP/test-only as BODY MOVE.
**SAFETY:** Only pure scalar, path-string, timestamp and report metadata calculations; no `main`, subprocess, PID inspection, lock/queue writes, background job lifecycle, real broker/order, Guard, Step5C, UEF, RunLab, real report/State/DB, live network, frozen oracle, CI policy, deployment or force-push. The SOURCE file also contains effectful code; NEVER execute it or change its behavior except thin wrappers for exactly listed pure functions. Use patched fakes and TemporaryDirectory; if any item proves effectful, SAFETY_BLOCKED and continue.
**MOVE:** Capture ORIGINAL golden behavior before editing. Move exact BODY below into one new TARGET Owner (same function name), replace SOURCE body with a same-signature thin delegation only; no duplicated computation or imports back from Owner to SOURCE. Owner accepts keyword-only `facade`, passed by SOURCE as `sys.modules[__name__]`; SOURCE already imports sys. For names referenced in original body (os, time, re, _to_epoch, ROOT, Path), resolve through facade at call time, preserve monkeypatch, errors, output and ordering. Each Owner uses `from __future__ import annotations` and necessary local typing imports. Keep original callers/public API and all existing tests intact except the ONE authorized guard test row below.
**NORMAL G2:** Create ONLY `tests/test_p15_rf035_20261101_01h_live_bundle_pure_owners.py` with `test_a1_env_bool` … `test_a8_wmi_epoch`, golden(original) vs wrapper vs direct Owner, negative cases and call-time monkeypatch. `python -m py_compile libs/reporting/live_execution_bundle_runner.py` plus all eight target files; `python -m unittest tests/test_p15_rf035_20261101_01h_live_bundle_pure_owners.py -v` normal exit0. No mandatory -O/full peer/hosted CI. Commit only listed A source/targets/new test and exact guard test repair; normal non-force push A branch, refetch remote A HEAD and SOURCE/TARGET/test blob; report measured START/END, actual LOC and individual results #11. C04 integrates and C05 decides G1/G2/G3/DONE; document publication itself is not code progress.
**ADDITIONAL G2 REGRESSION REPAIR (NOT a BODY MOVE; explicitly authorized):** `tests/test_closeout_payload_projection.py::test_converted_consumers_read_only_the_projected_keys`: in the single `@pytest.mark.parametrize` row for `build_quant_shadow_candidate_evaluation`, replace SOURCE path `libs/reporting/quant_shadow_candidate_evaluation.py` with `libs/reporting/quant_shadow_evaluation_builder_projection.py`, keep `{"build_quant_shadow_candidate_evaluation"}` and other rows untouched. New Owner is A remote at 0add890cd2484edcfe730cc177311a7f3f8fbf5e; source wrapper has no payload key reads. Run `python -m pytest tests/test_closeout_payload_projection.py -q -k converted_consumers_read_only_the_projected_keys` expected 3 passed normal exit0; if pytest missing, report TEST_BLOCKED but continue eight BODY MOVEs. Do NOT modify test AST scanning logic, frozen oracle or any unrelated test. This repair is G2 test-location correction only, not a ninth MOVE.

## A1 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_env_bool` L234 | CURRENT_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_env_bool_projection.py::_env_bool` — NEW, verified absent A/integration.
**EXACT CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
```python
def _env_bool(name: str, default: bool = True) -> bool:
    raw = str(os.getenv(name, "1" if default else "0")).strip().lower()
    return raw in {"1", "true", "yes", "on"}
```
**Wrapper/callers/monkeypatch:** facade.os.getenv (call-time), preserve default and truthy tokens; do not touch environment outside patched tests; Owner must not import SOURCE. Preserve original signature, exceptions and outputs; wrapper delegates at call-time via facade.
**Targeted normal test `test_a1_env_bool`:** monkeypatch facade.os.getenv to return 'YES' => True, 'off' => False; missing with default=False => False. Compare golden vs SOURCE wrapper vs direct Owner and post-import monkeypatch. Fake/temp only. If BLOCKED record exact first blocker and continue A2.

## A2 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_bundle_role` L254 | CURRENT_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_bundle_role_projection.py::_bundle_role` — NEW, verified absent A/integration.
**EXACT CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
```python
def _bundle_role(value: Any = "") -> str:
    raw = str(value or "").strip()
    return raw or "intraday_trade_report_bundle"
```
**Wrapper/callers/monkeypatch:** pure str/strip; keep empty-string fallback and original signature; Owner must not import SOURCE. Preserve original signature, exceptions and outputs; wrapper delegates at call-time via facade.
**Targeted normal test `test_a2_bundle_role`:** value=' audit ' => 'audit'; value=' ' => 'intraday_trade_report_bundle'; value=None => default. Compare golden vs SOURCE wrapper vs direct Owner and post-import monkeypatch. Fake/temp only. If BLOCKED record exact first blocker and continue A3.

## A3 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_is_trueish` L259 | CURRENT_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_trueish_projection.py::_is_trueish` — NEW, verified absent A/integration.
**EXACT CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
```python
def _is_trueish(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}
```
**Wrapper/callers/monkeypatch:** pure conversion; exact set of accepted tokens; no operational flag change; Owner must not import SOURCE. Preserve original signature, exceptions and outputs; wrapper delegates at call-time via facade.
**Targeted normal test `test_a3_trueish`:** 'YES' => True, 'y' => True, 'on' => True, 'false' => False, None => False. Compare golden vs SOURCE wrapper vs direct Owner and post-import monkeypatch. Fake/temp only. If BLOCKED record exact first blocker and continue A4.

## A4 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_lock_timestamp_epoch` L611 | CURRENT_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_lock_epoch_projection.py::_lock_timestamp_epoch` — NEW, verified absent A/integration.
**EXACT CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
```python
def _lock_timestamp_epoch(payload: Dict[str, Any], *, stale_after_sec: float) -> float:
    raw = (
        payload.get("touched_at_epoch")
        or payload.get("heartbeat_epoch")
        or payload.get("started_at_epoch")
    )
    try:
        epoch = float(raw or 0.0)
    except Exception:
        epoch = 0.0
    if epoch > 0:
        return epoch
    started_at = str(payload.get("started_at") or "").strip()
    return _to_epoch(started_at) or (time.time() - stale_after_sec - 1.0)
```
**Wrapper/callers/monkeypatch:** facade._to_epoch and facade.time.time dynamically; no actual lock read/write; exact fallback precedence; Owner must not import SOURCE. Preserve original signature, exceptions and outputs; wrapper delegates at call-time via facade.
**Targeted normal test `test_a4_lock_epoch`:** payload={'touched_at_epoch':123.5}, stale_after_sec=30 => 123.5; {'started_at':'fake'} with patched _to_epoch returning 500 => 500; empty payload with patched _to_epoch None and time.time=1000, stale_after_sec=30 => 969.0. Compare golden vs SOURCE wrapper vs direct Owner and post-import monkeypatch. Fake/temp only. If BLOCKED record exact first blocker and continue A5.

## A5 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_format_duration_human` L1125 | CURRENT_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_duration_human_projection.py::_format_duration_human` — NEW, verified absent A/integration.
**EXACT CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
```python
def _format_duration_human(seconds: int) -> str:
    if seconds <= 0:
        return "0m"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds / 60.0:.1f}m"
    return f"{seconds / 3600.0:.1f}h"
```
**Wrapper/callers/monkeypatch:** pure formatting; preserve numeric comparisons, rounding and exception parity; Owner must not import SOURCE. Preserve original signature, exceptions and outputs; wrapper delegates at call-time via facade.
**Targeted normal test `test_a5_duration_human`:** seconds 0 => '0m', 59 => '59s', 90 => '1.5m', 7200 => '2.0h'. Compare golden vs SOURCE wrapper vs direct Owner and post-import monkeypatch. Fake/temp only. If BLOCKED record exact first blocker and continue A6.

## A6 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_trade_id_sequence` L1141 | CURRENT_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_trade_sequence_projection.py::_trade_id_sequence` — NEW, verified absent A/integration.
**EXACT CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
```python
def _trade_id_sequence(trade_id: str) -> int:
    text = str(trade_id or "").strip()
    if not text:
        return 10**9
    tail = text.rsplit("_", 1)[-1]
    try:
        return int(tail)
    except Exception:
        return 10**9
```
**Wrapper/callers/monkeypatch:** pure suffix parse; preserve sentinel 10**9, int conversion and exception behavior; Owner must not import SOURCE. Preserve original signature, exceptions and outputs; wrapper delegates at call-time via facade.
**Targeted normal test `test_a6_trade_sequence`:** 'TRD_20261101_005930_12' => 12; '' => 1000000000; 'broken' => 1000000000. Compare golden vs SOURCE wrapper vs direct Owner and post-import monkeypatch. Fake/temp only. If BLOCKED record exact first blocker and continue A7.

## A7 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_resolve_existing_day_artifact` L1256 | CURRENT_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_artifact_paths_projection.py::_resolve_existing_day_artifact` — NEW, verified absent A/integration.
**EXACT CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
```python
def _resolve_existing_day_artifact(report_dir: Path, prefix: str, day: str) -> Tuple[Path, Path]:
    return report_dir / f"{prefix}_{day}.md", report_dir / f"{prefix}_{day}.json"
```
**Wrapper/callers/monkeypatch:** pure Path composition; no read/write or real reports; Owner must not import SOURCE. Preserve original signature, exceptions and outputs; wrapper delegates at call-time via facade.
**Targeted normal test `test_a7_artifact_paths`:** report_dir=Path('/tmp/fake'), prefix='daily', day='2026-11-01' => (Path('/tmp/fake/daily_2026-11-01.md'), Path('/tmp/fake/daily_2026-11-01.json')). Compare golden vs SOURCE wrapper vs direct Owner and post-import monkeypatch. Fake/temp only. If BLOCKED record exact first blocker and continue A8.

## A8 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_creation_epoch_from_wmi` L565 | CURRENT_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_wmi_epoch_projection.py::_creation_epoch_from_wmi` — NEW, verified absent A/integration.
**EXACT CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
```python
def _creation_epoch_from_wmi(value: Any) -> float:
    raw = str(value or "").strip()
    if not raw:
        return 0.0
    match = re.search(r"/Date\((\d+)", raw)
    if match:
        try:
            return float(match.group(1)) / 1000.0
        except Exception:
            return 0.0
    return 0.0
```
**Wrapper/callers/monkeypatch:** facade.re.search call-time; string parse only, no WMI process access; Owner must not import SOURCE. Preserve original signature, exceptions and outputs; wrapper delegates at call-time via facade.
**Targeted normal test `test_a8_wmi_epoch`:** '/Date(123000)/' => 123.0; '' => 0.0; 'nonsense' => 0.0. Compare golden vs SOURCE wrapper vs direct Owner and post-import monkeypatch. Fake/temp only. If BLOCKED record exact first blocker and continue Afinish/test/push.

## FUTURE RESERVE — VERIFIED 6/6 (DESIGN ONLY, DO NOT EXECUTE)
These six distinct actual SOURCE bodies and unoccupied TARGETs are verified against RF-035 Owner, SOURCE blob, A/integration directory inventory and pure/temp test feasibility. A must NOT execute reserve items without next C03 reissue and fresh SHA/target check.

### R1 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_stale_process_after_sec` L578 | SOURCE_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_stale_timeout_projection.py::_stale_process_after_sec` — 404 absent A/integration (verified directory listing).
**ACTUAL BODY (DESIGN ONLY):**
```python
def _stale_process_after_sec() -> float:
    try:
        return max(30.0, float(os.getenv("INTRADAY_TRADE_REPORT_STALE_PROCESS_SEC", "180") or 180.0))
    except Exception:
        return 180.0
```
**Future normal fixture:** patched os.getenv '12' => 30.0, '45' => 45.0, invalid => 180.0. **Safety/seam:** facade.os.getenv, never inspect or kill processes. Do not execute before next C03 issuance.

### R2 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_background_job_lock_path` L243 | SOURCE_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_lock_path_projection.py::_background_job_lock_path` — 404 absent A/integration (verified directory listing).
**ACTUAL BODY (DESIGN ONLY):**
```python
def _background_job_lock_path() -> Path | None:
    raw = str(os.getenv("INTRADAY_TRADE_REPORT_JOB_LOCK_PATH") or "").strip()
    if raw:
        return Path(raw)
    return ROOT / "reports" / "runtime" / "intraday_trade_report_bundle.lock"
```
**Future normal fixture:** patched os.getenv empty, facade.ROOT=Path('/tmp/fake') => Path('/tmp/fake/reports/runtime/intraday_trade_report_bundle.lock'). **Safety/seam:** facade.os.getenv/ROOT/Path; path calculation only. Do not execute before next C03 issuance.

### R3 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_background_job_queue_path` L250 | SOURCE_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_queue_path_projection.py::_background_job_queue_path` — 404 absent A/integration (verified directory listing).
**ACTUAL BODY (DESIGN ONLY):**
```python
def _background_job_queue_path() -> Path:
    return ROOT / "reports" / "runtime" / "intraday_trade_report_bundle.queue.json"
```
**Future normal fixture:** patched facade.ROOT=Path('/tmp/fake') => Path('/tmp/fake/reports/runtime/intraday_trade_report_bundle.queue.json'). **Safety/seam:** facade.ROOT, no queue IO. Do not execute before next C03 issuance.

### R4 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_read_json` L784 | SOURCE_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_json_read_projection.py::_read_json` — 404 absent A/integration (verified directory listing).
**ACTUAL BODY (DESIGN ONLY):**
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
**Future normal fixture:** TemporaryDirectory JSON {'a':1} => {'a':1}; malformed JSON => {}; missing path => {}. **Safety/seam:** read only temp paths; facade.json and Path seam. Do not execute before next C03 issuance.

### R5 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_iter_jsonl` L766 | SOURCE_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_jsonl_iter_projection.py::_iter_jsonl` — 404 absent A/integration (verified directory listing).
**ACTUAL BODY (DESIGN ONLY):**
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
**Future normal fixture:** temp JSONL '{"a":1}\nBAD\n[]\n' => [{'a':1}]; missing path => []. **Safety/seam:** read only temp paths; facade.json; preserve list return. Do not execute before next C03 issuance.

### R6 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/live_execution_bundle_runner.py::_build_trade_id` L1135 | SOURCE_BLOB `a4a6ccbc36b8f65fbf017977f5c4b1281aeb6501`
**TARGET:** `libs/reporting/live_bundle_trade_id_projection.py::_build_trade_id` — 404 absent A/integration (verified directory listing).
**ACTUAL BODY (DESIGN ONLY):**
```python
def _build_trade_id(day: str, symbol: str, seq: int) -> str:
    compact_day = str(day or "").replace("-", "")
    clean_symbol = normalize_symbol(symbol or "", allow_test_symbols=True) or "UNKNOWN"
    return f"TRD_{compact_day}_{clean_symbol}_{int(seq):02d}"
```
**Future normal fixture:** patched facade.normalize_symbol returns '005930'; day='2026-11-01', symbol='005930', seq=2 => 'TRD_20261101_005930_02'. **Safety/seam:** facade.normalize_symbol at call time, no order creation. Do not execute before next C03 issuance.

**SUPPLY ACCOUNTING:** A-00 REMOTE_DONE 8/8; A-01 NEW_READY 8 actual BODY MOVEs; A reserve VERIFIED 6/6; B-21 B3–B8 six remote-pending (B3 requires clean source wrapper), B reserve 6/6 subject to fresh recheck. No C03 code/test implementation, G1/G2/G3, integration or RF DONE claim.
