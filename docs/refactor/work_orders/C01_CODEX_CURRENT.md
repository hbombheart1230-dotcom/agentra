# C01 — Codex B | B-20261031-21 | FAST-3 8 actual pending/new SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_DESIGN:** `2c9453195ea619bfefbecf24ed711c9de161939d` | **OLD_ORDER_BLOB:** `fed5961b653a805aeb7cb8d3a0e59f2aefcb0bab` | **B_REMOTE_HEAD:** `68f3f0797951cb35219752956a10a609b8363500` | **SOURCE_BLOBS:** Q9 `77750437392a1d53f83e5123320a2a3f6b1c40e7`, M26 `4d5bb75ee8a22ad506ceff962e69e53a15d88563`.

**C03 NEW DELTA:** #12 6542649748 B18 B1–B3 REMOTE_DONE on `68f3f0797951cb35219752956a10a609b8363500`, normal unittest 3/3 exit0; earlier B18 B7–B8 also REMOTE_DONE on bc2bf16f. Thus old C01 has only B4–B6=3/6 safe pending, BELOW supply threshold. B-21 carries these 3 still-unimplemented Q9 BODY MOVEs as B1–B3, and adds 5 freshly verified M26 BODY MOVEs as B4–B8. Do not redo old B18 B1–B3/B7–B8, tests, or KEEP. C04 #36 6542892505 and C05 #36 6542991480: B1–B3 integrated scoped; B test at `tests/test_p15_rf063_18h_readiness_projection_owners.py` on B branch accidentally overwrote earlier B7/B8 suite. C04 preserved both by relocating B1–B3 exact tested content to `tests/test_p15_rf063_20h_readiness_projection_owners.py` on integration. **Do not overwrite either existing suite**; create ONLY tests/test_p15_rf063_21h_projection_owners.py for new eight items. RF-063 remains DEV/PARTIAL. #11 A20 all 8 REMOTE_DONE handled in C02; #32 RunLab no delta, exit255/UNKNOWN source operational HOLD.

**One-file complete contract:** Read only THIS C01 and exact code/test paths; no D00/RF/queue/C03/HANDOFF exploration, no self-selected tasks. Pin CANONICAL_HEAD, ORDER_BLOB, B remote SHA, ORDER_ID; execute ALL B1–B8, independently. B18 previous-start order is not retroactively canceled. Only B branch code/tests, never docs/RF/STATUS/C04/C05/A branch. Blocked item → continue next safe item.

**Verified ownership/safety:** RF-063 exclusively CODEX_B; Q9 SOURCE `scripts/diagnostics/check_q9_q12_readiness.py` blob `77750437392a1d53f83e5123320a2a3f6b1c40e7`, M26 SOURCE `scripts/diagnostics/run_m26_scorecard.py` blob `4d5bb75ee8a22ad506ceff962e69e53a15d88563` match integration. B1–B3 Q9 still actual calculation bodies; B4–B8 M26 still actual calculation bodies. Eight target paths + tests/test_p15_rf063_21h_projection_owners.py absent on B/integration; reserve six targets absent. No source/target collision with A. Pure offline readiness projection and scorecard scalar/JSONL calculations. Never call actual `main()`, PowerShell/process status, live health, real reports, broker/order/Guard/Step5C/UEF, RunLab, operational State/DB, network, deploy, frozen tests or CI workflows. Fake/temp only. Q9 _evaluate uses synthetic phase/live/processes and never queries runtime.

**Implementation/test/push:** Move each exact BODY below to new exclusive Owner, SOURCE signature as thin delegation, no duplicate BODY; Owner never imports SOURCE. Use call-time `facade=sys.modules[__name__]` for original globals and preserve CLI/caller/monkeypatch, output/exception, dict order. New Owner `from __future__ import annotations`. Capture original-preimage golden and compare original vs wrapper vs Owner, negative/error, post-import monkeypatch; AST prove body removal. Write `tests/test_p15_rf063_21h_projection_owners.py` with 8 named tests; do not modify B18 prior tests. Run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/q9_readiness_*_projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_21h_projection_owners.py -v` normal exit0 (scoped pytest allowed). No blanket -O/full-peer/hosted CI. Report actual normal exit, source before/after LOC, Owner/test blobs. Commit/push ONLY scripts/diagnostics/check_q9_q12_readiness.py, scripts/diagnostics/run_m26_scorecard.py, eight exact B targets and tests/test_p15_rf063_21h_projection_owners.py to `work/p15-b-operator-structure-20261022`, non-force, re-fetch remote HEAD/source/target/test blobs. Terminal auth error → PUSH_BLOCKED only, continue safe work; previously approved exact-tree expected-head lease allowed, no force. C04/C05 G3/DONE separate.

**Allowed paths:** scripts/diagnostics/check_q9_q12_readiness.py; scripts/diagnostics/run_m26_scorecard.py; scripts/diagnostics/q9_readiness_window_projection.py; scripts/diagnostics/q9_readiness_baseline_projection.py; scripts/diagnostics/q9_readiness_evaluation_projection.py; scripts/diagnostics/m26_scorecard_epoch_projection.py; scripts/diagnostics/m26_scorecard_day_projection.py; scripts/diagnostics/m26_scorecard_jsonl_projection.py; scripts/diagnostics/m26_scorecard_int_projection.py; scripts/diagnostics/m26_scorecard_float_projection.py; tests/test_p15_rf063_21h_projection_owners.py. Reserve R1–R6 design only.

## B1 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_q9_checks` @ L111 | SOURCE_BLOB=`77750437392a1d53f83e5123320a2a3f6b1c40e7`
**TARGET:** `scripts/diagnostics/q9_readiness_window_projection.py::_q9_checks` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _q9_checks(reports_root: Path, day: str) -> dict[str, Any]:
    q9_path = reports_root / "operator_summary" / "daily" / day / "q9_decision_windows.json"
    validity_path = reports_root / "evaluation" / "daily" / day / "q9_day_validity.json"
    q9 = _read_json(q9_path)
    validity = _read_json(validity_path)
    windows = [row for row in q9.get("windows") or [] if isinstance(row, dict)]
    times = [parsed for parsed in (_parse_dt(row.get("generated_at")) for row in windows) if parsed is not None]
    first = min(times) if times else None
    last = max(times) if times else None
    return {
        "artifact": _artifact(q9_path),
        "validity_artifact": _artifact(validity_path),
        "window_count": len(windows),
        "first_window_kst": first.isoformat() if first else "",
        "last_window_kst": last.isoformat() if last else "",
        "day_validity_status": validity.get("status") or "",
        "counts_as_formal_day": bool(validity.get("counts_as_formal_day")),
        "validity_blockers": validity.get("blockers") or [],
        "validity_warnings": validity.get("warnings") or [],
    }
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade._read_json/_parse_dt/_artifact, datetime, KST; no actual runtime. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_b1_q9_checks` in `tests/test_p15_rf063_21h_projection_owners.py`. Fixture input→expected: TemporaryDirectory empty reports_root,day='2026-08-30' → window_count=0,first_window_kst='',last_window_kst=''. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue B2**.

## B2 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_baseline_artifacts` @ L133 | SOURCE_BLOB=`77750437392a1d53f83e5123320a2a3f6b1c40e7`
**TARGET:** `scripts/diagnostics/q9_readiness_baseline_projection.py::_baseline_artifacts` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _baseline_artifacts(reports_root: Path, day: str) -> dict[str, Any]:
    artifacts = {
        "q10": {
            "decisions": _artifact(reports_root / "evaluation" / "baseline_samsung_hynix" / day / "baseline_samsung_hynix_decisions.json"),
            "forward": _artifact(reports_root / "evaluation" / "baseline_samsung_hynix" / day / "baseline_samsung_hynix_forward_returns.json"),
            "comparison": _artifact(reports_root / "evaluation" / "baseline_samsung_hynix" / day / "q9_vs_samsung_hynix_daily_comparison.json"),
        },
        "q11": {
            "signals": _artifact(reports_root / "evaluation" / "opportunity_engine_shadow" / day / "opportunity_engine_signals.json"),
            "virtual_trades": _artifact(reports_root / "evaluation" / "opportunity_engine_shadow" / day / "opportunity_engine_virtual_trades.json"),
            "report": _artifact(reports_root / "evaluation" / "opportunity_engine_shadow" / day / "opportunity_engine_daily_report.json"),
        },
        "q12": {
            "decisions": _artifact(reports_root / "evaluation" / "baseline_btc_woori_tech" / day / "baseline_btc_woori_decisions.json"),
            "forward": _artifact(reports_root / "evaluation" / "baseline_btc_woori_tech" / day / "baseline_btc_woori_forward_returns.json"),
            "comparison": _artifact(reports_root / "evaluation" / "baseline_btc_woori_tech" / day / "baseline_btc_woori_comparison.json"),
            "hypothesis_validation": _artifact(reports_root / "evaluation" / "baseline_btc_woori_tech" / day / "q12_btc_woori_hypothesis_validation.json"),
            "hypothesis_cumulative": _artifact(reports_root / "evaluation" / "baseline_btc_woori_tech" / "hypothesis_validation" / "q12_btc_woori_hypothesis_cumulative.json"),
        },
    }
    if day >= Q10_LEAD_MARKET_ACTIVATION_DAY:
        forward_root = reports_root / "evaluation" / "baseline_samsung_hynix" / day / "q10_forward_validation"
        artifacts["q10"].update(
            {
                "lead_market_preopen": _artifact(forward_root / "q10_preopen_signal_snapshot.json"),
                "lead_market_reactions": _artifact(forward_root / "q10_actual_market_reactions.json"),
                "lead_market_expected_actual": _artifact(forward_root / "q10_expected_vs_actual.json"),
                "lead_market_shadow": _artifact(forward_root / "q10_shadow_entry_comparison.json"),
                "lead_market_report": _artifact(forward_root / "q10_forward_validation_report.md"),
            }
        )
    return artifacts
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade._artifact/Q10_LEAD_MARKET_ACTIVATION_DAY, group/key ordering. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_b2_baseline_artifacts` in `tests/test_p15_rf063_21h_projection_owners.py`. Fixture input→expected: TemporaryDirectory empty reports_root,day='2026-08-30' → q10/q11/q12 present, all exists=False; 2026-08-31 threshold adds lead_market_*. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue B3**.

## B3 | RF-063 | Owner=CODEX_B | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_evaluate` @ L167 | SOURCE_BLOB=`77750437392a1d53f83e5123320a2a3f6b1c40e7`
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
These are six distinct RF-063 B source bodies verified on current M26/metrics blobs, target paths absent B/integration; not part of B-21. New C03 issuance and latest source/target recheck mandatory. Do not treat prior B18 tests as reserve.

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
