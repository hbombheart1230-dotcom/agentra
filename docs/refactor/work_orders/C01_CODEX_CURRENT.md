# C01 — Codex B | B-20261031-21 CONTINUATION | FAST-3 6 remaining actual BODY MOVEs

**CANONICAL_HEAD_AT_TRIAGE:** `c2fff478f77d9cd25e6101cd1c5f2d040953f61b` | **OLD_ORDER_BLOB:** `90b763d600d28a340a30a5d4765744e5ded8d9c6` | **B_REMOTE_HEAD:** `32ed205327a36f2041ebd9a3257c02cba1cd41cd` | **Q9_SOURCE_BLOB:** `43db04b1419b39b3716145d7a0d3844abb634835` | **M26_SOURCE_BLOB:** `4d5bb75ee8a22ad506ceff962e69e53a15d88563`.

**C03 latest delta:** #12 comment 6544449972 confirms B-21 B2 `_baseline_artifacts` REMOTE_DONE: Q9 original BODY removed and new `q9_readiness_baseline_projection` owner exists, normal unittest 2/2 exit0, B normal non-force push 32ed2053. Earlier B1 `_q9_checks` REMOTE_DONE on 444cd862. **Never redo B1/B2 or overwrite their two tests.** Current B3 `_evaluate` BODY is still present and matches old order exact code byte-for-byte; Q9 blob advanced `83b0295f→43db04b1` solely due B2, current function L121. B4–B8 M26 BODY source blob unchanged. **Six** independent safe unfinished B3–B8 remain; threshold is strictly fewer than six, so do not cancel this start order or manufacture new B work. A #11 6544589564 A-23 8/8 REMOTE_DONE; new A-20261101-00 supplied separately. RunLab #32 6520075820 Exited(255), RUN_SOURCE_SHA UNKNOWN, operational HOLD.

**ONE-FILE EXECUTION CONTRACT:** Read THIS C01 only and exact source/target/test paths below; no D00/RF/queue/C03/HANDOFF or self-selection. Pin CANONICAL_HEAD, ORDER_BLOB, B remote SHA and ORDER_ID. Execute ALL B3–B8, individually; blocked one → continue other safe ones. Do not invalidate B's earlier start order retroactively. Only B `work/p15-b-operator-structure-20261022` code/test, no docs/RF/STATUS/C04/C05/A branch.

**OWNER/SAFETY:** RF-063 CODEX_B exclusive offline diagnostics: Q9 SOURCE `scripts/diagnostics/check_q9_q12_readiness.py` blob `43db04b1`; M26 SOURCE `scripts/diagnostics/run_m26_scorecard.py` blob `4d5bb75e`; all six TARGETs absent on both B and integration, and six future reserve targets absent on both. No overlap with A. Fake mappings/TemporaryDirectory only. Never run live main, real health/process, broker/order, Guard/Step5C/UEF, RunLab, operational State/DB/network/deploy, CI/frozen oracle or force-push. Q9 B3 receives synthetic phase/live/processes and a patched clock only.

**MOVE:** Move each exact calculation BODY below to new exclusive Owner, SOURCE same-signature thin delegation, no duplicate BODY. Owner never imports SOURCE. Preserve caller/CLI, exception, dict ordering, call-time monkeypatch through `facade=sys.modules[__name__]`; use `from __future__ import annotations` and own typing imports. Capture preimage golden per item; compare original vs wrapper vs direct Owner, negative/error, post-import monkeypatch, AST proof source BODY removed. Existing B1/B2 tests in `tests/test_p15_rf063_21h_projection_owners.py` must be preserved byte-for-byte; append B3–B8 tests safely, or create `tests/test_p15_rf063_20261101_00h_projection_owners.py` if collision. Do not overwrite B18 or prior 21h suite.

**NORMAL G2/PUSH:** `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py` plus six exact new targets; `python -m unittest tests/test_p15_rf063_21h_projection_owners.py -v` (or distinct 00h file for six), normal exit0. Commit only B source/targets/tests, non-force push, refetch remote B HEAD/source/target/test blobs. Report B3–B8 per-item IMPLEMENTED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN, normal exit, SHA, START/END measured to #12. Git authentication failure blocks push only; continue other safe tasks. No mandatory -O/full peer/hosted CI. C04 G3 integration, C05 RF DONE separately.

## B3 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_evaluate` @ L121 | SOURCE_BLOB=`43db04b1419b39b3716145d7a0d3844abb634835`
**TARGET:** `scripts/diagnostics/q9_readiness_evaluation_projection.py::_evaluate` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _evaluate(
    *,
    phase: str,
    day: str,
    live: dict[str, Any],
    processes: dict[str, Any],
    q9: dict[str, Any],
    artifacts: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if phase in {"preopen", "intraday"}:
        if not live.get("running"):
            blockers.append({"code": "live_session_not_running"})
        elif to_int(live.get("heartbeat_age_sec"), 999999) > 180:
            blockers.append({"code": "live_heartbeat_stale", "age_sec": live.get("heartbeat_age_sec")})
        for name, row in processes.items():
            if not row.get("running"):
                blockers.append({"code": f"{name}_loop_not_running"})
            if to_int(row.get("process_count"), 0) > 2:
                warnings.append({"code": f"{name}_duplicate_processes", "pids": row.get("pids")})
    if phase == "intraday":
        now = datetime.now(KST)
        if (now.hour, now.minute) >= (9, 10):
            first = _parse_dt(q9.get("first_window_kst"))
            if not first:
                blockers.append({"code": "q9_first_window_missing_after_0910"})
            elif (first.hour, first.minute) > (9, 5):
                blockers.append({"code": "q9_first_window_late", "first_window_kst": first.isoformat()})
    if phase == "closeout":
        for group, rows in artifacts.items():
            for key, record in rows.items():
                if not record.get("exists"):
                    blockers.append({"code": f"{group}_{key}_missing", "path": record.get("path")})
        if day >= Q10_LEAD_MARKET_ACTIVATION_DAY:
            preopen = (artifacts.get("q10") or {}).get("lead_market_preopen") or {}
            if preopen.get("capture_status") != "CAPTURED":
                blockers.append(
                    {
                        "code": "q10_lead_market_preopen_not_captured",
                        "capture_status": preopen.get("capture_status") or "MISSING",
                        "path": preopen.get("path"),
                    }
                )
        if q9.get("day_validity_status") == "INVALID":
            blockers.append({"code": "q9_day_invalid", "blockers": q9.get("validity_blockers")})
        elif q9.get("day_validity_status") not in {"VALID", ""}:
            warnings.append({"code": "q9_day_not_final_valid", "status": q9.get("day_validity_status")})
    return blockers, warnings
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade.to_int/_parse_dt/datetime/KST/Q10_LEAD_MARKET_ACTIVATION_DAY, fake inputs only; no subprocess. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_b3_evaluate` in `tests/test_p15_rf063_21h_projection_owners.py`. Fixture input→expected: phase='preopen',live={'running':False},processes={},q9={},artifacts={},day='2026-08-30' → blockers=[{'code':'live_session_not_running'}],warnings=[]. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue B4**.

## B4 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_to_epoch` @ L26 | SOURCE_BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**TARGET:** `scripts/diagnostics/m26_scorecard_epoch_projection.py::_to_epoch` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _to_epoch(ts: Any) -> Optional[int]:
    if ts is None:
        return None
    if isinstance(ts, (int, float)):
        return int(ts)
    s = str(ts).strip()
    if not s:
        return None
    try:
        return int(float(s))
    except Exception:
        pass
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return None
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade.datetime/timezone at invocation, preserve numeric conversion and exceptions. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_b4_to_epoch` in `tests/test_p15_rf063_21h_projection_owners.py`. Fixture input→expected: None → None; '0' → 0; '1970-01-01T00:00:00Z' → 0; invalid → None. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue B5**.

## B5 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_utc_day` @ L49 | SOURCE_BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**TARGET:** `scripts/diagnostics/m26_scorecard_day_projection.py::_utc_day` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _utc_day(ts: Any) -> str:
    ep = _to_epoch(ts)
    if ep is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(ep, tz=timezone.utc).strftime("%Y-%m-%d")
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade._to_epoch/datetime/timezone at invocation; preserve fallback clock. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_b5_utc_day` in `tests/test_p15_rf063_21h_projection_owners.py`. Fixture input→expected: 0 → '1970-01-01'; 86400 → '1970-01-02'; invalid timestamp only with deterministic patched datetime. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue B6**.

## B6 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_iter_jsonl` @ L56 | SOURCE_BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**TARGET:** `scripts/diagnostics/m26_scorecard_jsonl_projection.py::_iter_jsonl` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _iter_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    out: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception:
                continue
            if isinstance(obj, dict):
                out.append(obj)
    return out
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade.json; path.open, file order, malformed/blank skip. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_b6_iter_jsonl` in `tests/test_p15_rf063_21h_projection_owners.py`. Fixture input→expected: missing temp path → []; temp JSONL '{"x":1}\ninvalid\n[]\n' → [{'x':1}]. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue B7**.

## B7 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_safe_int` @ L74 | SOURCE_BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**TARGET:** `scripts/diagnostics/m26_scorecard_int_projection.py::_safe_int` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except Exception:
        return int(default)
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: pure numeric coercion; preserve signature/default. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_b7_safe_int` in `tests/test_p15_rf063_21h_projection_owners.py`. Fixture input→expected: '3.9' → 3; 'bad',default=4 → 4; default conversion exception parity. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue B8**.

## B8 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_safe_float` @ L81 | SOURCE_BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**TARGET:** `scripts/diagnostics/m26_scorecard_float_projection.py::_safe_float` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: pure numeric coercion; preserve signature/default. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_b8_safe_float` in `tests/test_p15_rf063_21h_projection_owners.py`. Fixture input→expected: '1.25' → 1.25; 'bad',default=2.5 → 2.5; NaN/exception parity. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue finish targeted test, commit/push, remote re-fetch**.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY (NOT EXECUTABLE)
These are six distinct RF-063 B source bodies re-verified on current M26/metrics blobs, target paths absent B/integration; not part of B-21. New C03 issuance and latest source/target recheck mandatory. Do not treat prior B18 tests as reserve.

### R1 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_load_close_price_by_symbol` @ L98 | SOURCE_BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**TARGET:** `scripts/diagnostics/m26_scorecard_close_projection.py::_load_close_price_by_symbol` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
```python
def _load_close_price_by_symbol(path: Path, *, day: str) -> Dict[str, float]:
    out: Dict[str, Tuple[str, float]] = {}
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = str(row.get("symbol") or "").strip()
            if not symbol:
                continue
            ts = str(row.get("ts") or "").strip()
            d = _utc_day(ts)
            close = _safe_float(row.get("close"), default=0.0)
            if close <= 0.0:
                continue
            prev = out.get(symbol)
            if day:
                if d != day:
                    continue
                if prev is None or d >= prev[0]:
                    out[symbol] = (d, close)
            else:
                if prev is None or d >= prev[0]:
                    out[symbol] = (d, close)
    return {k: v[1] for k, v in out.items()}
```
**Future test input→expected:** missing temp CSV → {}; temp CSV with symbol=A,ts=1970-01-01T00:00:00Z,close=10,day=1970-01-01 → {'A':10.0}. **Safety/call-time seams:** facade.csv/_utc_day/_safe_float; TemporaryDirectory. Requires fresh source blob/target check and new C03 issuance before execution.

### R2 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_build_parser` @ L125 | SOURCE_BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**TARGET:** `scripts/diagnostics/m26_scorecard_parser_projection.py::_build_parser` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
```python
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="M26 scorecard scaffold (PnL proxy / risk-adjusted / drawdown).")
    p.add_argument("--dataset-root", default="data/eval/m26_fixed_dataset_v1")
    p.add_argument("--day", default=None)
    p.add_argument("--json", action="store_true")
    return p
```
**Future test input→expected:** parse_args(['--day','2026-10-31','--json']) → day='2026-10-31',json=True. **Safety/call-time seams:** facade.argparse; parser-only, never main. Requires fresh source blob/target check and new C03 issuance before execution.

### R3 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_validate_required` @ L133 | SOURCE_BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**TARGET:** `scripts/diagnostics/m26_scorecard_validate_projection.py::_validate_required` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
```python
def _validate_required(dataset_root: Path) -> Tuple[List[str], List[str]]:
    failures: List[str] = []
    missing: List[str] = []
    for rel in REQUIRED_FILES:
        if not (dataset_root / rel).exists():
            missing.append(rel)
    if missing:
        failures.append("missing_required_files")

    manifest_path = dataset_root / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as e:
            failures.append(f"invalid_manifest_json ({e})")
            return failures, missing
        if str(manifest.get("schema_version") or "") != "m26.dataset_manifest.v1":
            failures.append("invalid_manifest_schema_version")
    return failures, missing
```
**Future test input→expected:** empty temp dataset root → 'missing_required_files' in failures; all REQUIRED_FILES created → no missing. **Safety/call-time seams:** facade.REQUIRED_FILES/json; TemporaryDirectory, no real dataset. Requires fresh source blob/target check and new C03 issuance before execution.

### R4 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/check_metrics_schema_v1.py::_is_dict` @ L21 | SOURCE_BLOB=`586466c6162d818d1ae60644ec7dd0d988beef63`
**TARGET:** `scripts/diagnostics/metrics_schema_dict_projection.py::_is_dict` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
```python
def _is_dict(v: Any) -> bool:
    return isinstance(v, dict)
```
**Future test input→expected:** {} → True, [] → False. **Safety/call-time seams:** pure isinstance; preserve bool. Requires fresh source blob/target check and new C03 issuance before execution.

### R5 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/check_metrics_schema_v1.py::_is_list` @ L25 | SOURCE_BLOB=`586466c6162d818d1ae60644ec7dd0d988beef63`
**TARGET:** `scripts/diagnostics/metrics_schema_list_projection.py::_is_list` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
```python
def _is_list(v: Any) -> bool:
    return isinstance(v, list)
```
**Future test input→expected:** [] → True, {} → False. **Safety/call-time seams:** pure isinstance; preserve bool. Requires fresh source blob/target check and new C03 issuance before execution.

### R6 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/check_metrics_schema_v1.py::_build_parser` @ L34 | SOURCE_BLOB=`586466c6162d818d1ae60644ec7dd0d988beef63`
**TARGET:** `scripts/diagnostics/metrics_schema_parser_projection.py::_build_parser` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
```python
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate frozen metrics schema v1.")
    p.add_argument("--event-log-path", default="data/logs/events.jsonl")
    p.add_argument("--report-dir", default="reports/metrics")
    p.add_argument("--day", default=None)
    p.add_argument("--json", action="store_true")
    return p
```
**Future test input→expected:** parse_args(['--day','2026-10-31']) → day='2026-10-31'. **Safety/call-time seams:** facade.argparse; parser-only, never main. Requires fresh source blob/target check and new C03 issuance before execution.

**G1/G2/G3 separation:** C01 document issuance is not code G1/G2/G3 or RF DONE. C04/C05 retain integration and final acceptance.
