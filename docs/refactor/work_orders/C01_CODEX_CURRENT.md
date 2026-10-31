# C01 — Codex B | B-20261031-18 | FAST-3 eight NEW verified SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_ISSUANCE:** `86bf6e034a8dbfaaca19cb744f74ad136e4b677a` · **OLD_ORDER_BLOB:** `b3e3860d0508133e30f9c462921ecd58a2c6850f` · **B_REMOTE_HEAD_AT_DESIGN:** `f5e41ab686a3ea97a99d5d2362b49ca228808513` · **SOURCE_BLOBS:** `68349976f3e988989cc3133f597297d6ca3bd887`, `da20247c7177389f4f020c99474a0734218461a7`.
#12 `6540982789` and remote B HEAD confirm B-20261031-17 B1–B8 REMOTE_DONE, normal 4/4 exit0, remote test/source/Owner SHA. Do not reuse any of those eight. RF-063 exclusively owns both SOURCE files under scripts/diagnostics (RF-063 original Owner table checked). B1–B6 are previously verified reserve items **revalidated against current B SOURCE BODY**; B7–B8 are newly inspected pure scorecard calculations. All eight TARGET files verified 404 on B and integration before issuance.

**Single-document contract:** Read only this C01; pin CANONICAL_HEAD/ORDER_BLOB/B_REMOTE_HEAD. No D00/RF/queue/C03/handoff lookup or self-selection. Move the exact BODY to the named new B Owner, preserve SOURCE public signature as thin wrapper, caller/monkeypatch/use-time global parity, outputs and exceptions. For global references use `facade` passed at invocation; no Owner→SOURCE import or duplicate calculation. Each of B1–B8 is mandatory; blocked item does not stop remaining safe items. A newer C01 does not retroactively cancel a started order.

**Safety:** read-only diagnostic projection and offline scorecard math; mock/fake/TemporaryDirectory only. Never invoke actual `main()`, PowerShell/process inspection, runtime health probes, real reports, broker/order/Guard/Step5C/UEF, RunLab, live network, operational DB/state, CI/frozen oracle or deployment. B code/test branch only; no docs/RF/STATUS/C04/C05 or force push. One normal targeted unittest/pytest exit0 is G2; no blanket -O/full peer/hosted CI. Terminal HTTPS auth failure is PUSH_BLOCKED only; approved exact-tree expected-head lease is permitted, not force. After B commit/push, re-fetch remote HEAD/source/Owner/test blob. C04 G3 integration and C05 DONE separate.

**Allowed code/test:** `scripts/diagnostics/check_q9_q12_readiness.py`, `scripts/diagnostics/run_m26_scorecard.py`, the eight exact new B TARGET paths below, and `tests/test_p15_rf063_18h_readiness_projection_owners.py` only.

## B1 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_read_json` @ L31 | SOURCE_BLOB=`68349976f3e988989cc3133f597297d6ca3bd887`
**TARGET:** `scripts/diagnostics/q9_readiness_json_projection.py::_read_json` (NEW, verified absent on B and integration; B-exclusive).
**Exact computation BODY to MOVE (not a test-only/KEEP task):**
```python
def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}
```
**Wrapper/monkeypatch/callers:** Leave original function signature, defaults and exception semantics in SOURCE as thin delegation to TARGET. TARGET must not import SOURCE. json/Path via facade; UTF-8-SIG and exception fallback unchanged. If the function calls SOURCE globals, pass keyword-only `facade=sys.modules[__name__]` and resolve via facade at call time. Do not duplicate BODY; preserve callers, CLI behavior, output order/identity, patch seams and exceptions.
**Normal targeted test:** `test_b1_read_json` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: missing temp path → {}; BOM JSON object → dict. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all eight run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B2**.

## B2 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_parse_dt` @ L39 | SOURCE_BLOB=`68349976f3e988989cc3133f597297d6ca3bd887`
**TARGET:** `scripts/diagnostics/q9_readiness_time_projection.py::_parse_dt` (NEW, verified absent on B and integration; B-exclusive).
**Exact computation BODY to MOVE (not a test-only/KEEP task):**
```python
def _parse_dt(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(KST)
```
**Wrapper/monkeypatch/callers:** Leave original function signature, defaults and exception semantics in SOURCE as thin delegation to TARGET. TARGET must not import SOURCE. datetime/timezone/KST via facade; preserve naive UTC assumption. If the function calls SOURCE globals, pass keyword-only `facade=sys.modules[__name__]` and resolve via facade at call time. Do not duplicate BODY; preserve callers, CLI behavior, output order/identity, patch seams and exceptions.
**Normal targeted test:** `test_b2_parse_dt` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: 2026-10-31T00:00:00Z → 2026-10-31 09:00+09:00; invalid → None. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all eight run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B3**.

## B3 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_artifact` @ L117 | SOURCE_BLOB=`68349976f3e988989cc3133f597297d6ca3bd887`
**TARGET:** `scripts/diagnostics/q9_readiness_artifact_projection.py::_artifact` (NEW, verified absent on B and integration; B-exclusive).
**Exact computation BODY to MOVE (not a test-only/KEEP task):**
```python
def _artifact(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    return {
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "schema_version": payload.get("schema_version") or "",
        "capture_status": payload.get("capture_status") or "",
        "evidence_status": payload.get("evidence_status") or "",
    }
```
**Wrapper/monkeypatch/callers:** Leave original function signature, defaults and exception semantics in SOURCE as thin delegation to TARGET. TARGET must not import SOURCE. _read_json via facade; stat/existence and exception parity unchanged. If the function calls SOURCE globals, pass keyword-only `facade=sys.modules[__name__]` and resolve via facade at call time. Do not duplicate BODY; preserve callers, CLI behavior, output order/identity, patch seams and exceptions.
**Normal targeted test:** `test_b3_artifact` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: missing temp path → exists=False,size_bytes=0. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all eight run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B4**.

## B4 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_q9_checks` @ L129 | SOURCE_BLOB=`68349976f3e988989cc3133f597297d6ca3bd887`
**TARGET:** `scripts/diagnostics/q9_readiness_window_projection.py::_q9_checks` (NEW, verified absent on B and integration; B-exclusive).
**Exact computation BODY to MOVE (not a test-only/KEEP task):**
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
**Wrapper/monkeypatch/callers:** Leave original function signature, defaults and exception semantics in SOURCE as thin delegation to TARGET. TARGET must not import SOURCE. _read_json/_parse_dt/_artifact via facade at invocation; preserve list/filter/order. If the function calls SOURCE globals, pass keyword-only `facade=sys.modules[__name__]` and resolve via facade at call time. Do not duplicate BODY; preserve callers, CLI behavior, output order/identity, patch seams and exceptions.
**Normal targeted test:** `test_b4_q9_checks` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: empty temp root/day → window_count=0 and no timestamps. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all eight run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B5**.

## B5 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_baseline_artifacts` @ L151 | SOURCE_BLOB=`68349976f3e988989cc3133f597297d6ca3bd887`
**TARGET:** `scripts/diagnostics/q9_readiness_baseline_projection.py::_baseline_artifacts` (NEW, verified absent on B and integration; B-exclusive).
**Exact computation BODY to MOVE (not a test-only/KEEP task):**
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
**Wrapper/monkeypatch/callers:** Leave original function signature, defaults and exception semantics in SOURCE as thin delegation to TARGET. TARGET must not import SOURCE. _artifact and Q10_LEAD_MARKET_ACTIVATION_DAY via facade; preserve q10/q11/q12 map. If the function calls SOURCE globals, pass keyword-only `facade=sys.modules[__name__]` and resolve via facade at call time. Do not duplicate BODY; preserve callers, CLI behavior, output order/identity, patch seams and exceptions.
**Normal targeted test:** `test_b5_baseline_artifacts` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: empty temp root/day → q10/q11/q12 groups with missing artifacts. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all eight run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B6**.

## B6 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_evaluate` @ L185 | SOURCE_BLOB=`68349976f3e988989cc3133f597297d6ca3bd887`
**TARGET:** `scripts/diagnostics/q9_readiness_evaluation_projection.py::_evaluate` (NEW, verified absent on B and integration; B-exclusive).
**Exact computation BODY to MOVE (not a test-only/KEEP task):**
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
**Wrapper/monkeypatch/callers:** Leave original function signature, defaults and exception semantics in SOURCE as thin delegation to TARGET. TARGET must not import SOURCE. datetime/KST/_parse_dt/to_int/Q10_LEAD_MARKET_ACTIVATION_DAY via facade; fake preopen only; do not query runtime. If the function calls SOURCE globals, pass keyword-only `facade=sys.modules[__name__]` and resolve via facade at call time. Do not duplicate BODY; preserve callers, CLI behavior, output order/identity, patch seams and exceptions.
**Normal targeted test:** `test_b6_evaluate` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: phase=preopen, live.running=False, processes={} → blocker live_session_not_running. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all eight run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B7**.

## B7 | RF-063 | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_max_drawdown_ratio` @ L88 | SOURCE_BLOB=`da20247c7177389f4f020c99474a0734218461a7`
**TARGET:** `scripts/diagnostics/m26_scorecard_drawdown_projection.py::_max_drawdown_ratio` (NEW, verified absent on B and integration; B-exclusive).
**Exact computation BODY to MOVE (not a test-only/KEEP task):**
```python
def _max_drawdown_ratio(equity: List[float]) -> Tuple[float, float]:
    if not equity:
        return 0.0, 0.0
    peak = float(equity[0])
    max_dd = 0.0
    max_dd_ratio = 0.0
    for v in equity:
        x = float(v)
        if x > peak:
            peak = x
        dd = peak - x
        if dd > max_dd:
            max_dd = dd
        denom = abs(peak) if abs(peak) > 1e-12 else 0.0
        ratio = (dd / denom) if denom > 0.0 else 0.0
        if ratio > max_dd_ratio:
            max_dd_ratio = ratio
    return float(max_dd), float(max_dd_ratio)
```
**Wrapper/monkeypatch/callers:** Leave original function signature, defaults and exception semantics in SOURCE as thin delegation to TARGET. TARGET must not import SOURCE. pure; preserve floating point exact arithmetic and empty branch. If the function calls SOURCE globals, pass keyword-only `facade=sys.modules[__name__]` and resolve via facade at call time. Do not duplicate BODY; preserve callers, CLI behavior, output order/identity, patch seams and exceptions.
**Normal targeted test:** `test_b7_max_drawdown_ratio` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: [] → (0.0,0.0); [100.0,80.0] → (20.0,0.2). Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all eight run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B8**.

## B8 | RF-063 | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_risk_adjusted` @ L108 | SOURCE_BLOB=`da20247c7177389f4f020c99474a0734218461a7`
**TARGET:** `scripts/diagnostics/m26_scorecard_risk_projection.py::_risk_adjusted` (NEW, verified absent on B and integration; B-exclusive).
**Exact computation BODY to MOVE (not a test-only/KEEP task):**
```python
def _risk_adjusted(samples: List[float]) -> Dict[str, float]:
    if not samples:
        return {
            "sample_count": 0.0,
            "pnl_mean": 0.0,
            "pnl_std": 0.0,
            "downside_std": 0.0,
            "sharpe_proxy": 0.0,
            "sortino_proxy": 0.0,
        }

    n = float(len(samples))
    mean = float(statistics.fmean(samples))
    std = float(statistics.pstdev(samples)) if len(samples) > 1 else 0.0
    downside = [x for x in samples if x < 0.0]
    downside_std = float(statistics.pstdev(downside)) if len(downside) > 1 else (float(abs(downside[0])) if len(downside) == 1 else 0.0)

    sharpe = (mean / std) * math.sqrt(n) if std > 1e-12 else 0.0
    sortino = (mean / downside_std) * math.sqrt(n) if downside_std > 1e-12 else 0.0
    return {
        "sample_count": n,
        "pnl_mean": mean,
        "pnl_std": std,
        "downside_std": downside_std,
        "sharpe_proxy": float(sharpe),
        "sortino_proxy": float(sortino),
    }
```
**Wrapper/monkeypatch/callers:** Leave original function signature, defaults and exception semantics in SOURCE as thin delegation to TARGET. TARGET must not import SOURCE. statistics/math via facade to preserve patch seams and floating point behavior. If the function calls SOURCE globals, pass keyword-only `facade=sys.modules[__name__]` and resolve via facade at call time. Do not duplicate BODY; preserve callers, CLI behavior, output order/identity, patch seams and exceptions.
**Normal targeted test:** `test_b8_risk_adjusted` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: [] → sample_count=0.0; [1.0,-1.0] → sample_count=2.0,pnl_mean=0.0. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all eight run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue Bhandoff**.

## FUTURE RESERVE — RESERVE_NOT_VERIFIED 0/6
The six earlier verified q9 reserve items have been promoted to B1–B6; **none remains a verified reserve**. Candidate next: RF-063 `run_m26_scorecard.py` remaining `_to_epoch`, `_utc_day`, `_iter_jsonl`, `_safe_int`, `_safe_float`, `_load_close_price_by_symbol`. These are **not executable** and not counted until C03 verifies fresh body/blob, missing new target, side effects, caller/patch parity and normal fixture. Do not self-select.

## REPORT / PUSH
#12: `ORDER_ID=B-20261031-18 | CANONICAL_HEAD | ORDER_BLOB | B_REMOTE_BEFORE→AFTER | B1..B8 ITEM_STATUS | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | MOVED_FUNCTIONS | SOURCE_LOC_BEFORE_AFTER | FIRST_BLOCKER | NEXT_SAFE_ITEM | PUSH_REMOTE_SHA/PUSH_BLOCKED | START_KST/END_KST/ELAPSED_MIN`. Times measured only. C03 document push is not code G1/G2/G3 or RF_DONE. RunLab SOURCE_UNKNOWN/exit255 remains SAFETY_HOLD.
