# C01 — Codex B | B-20261031-18 continuation | FAST-3 six REMAINING verified SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_ISSUANCE:** `86bf6e034a8dbfaaca19cb744f74ad136e4b677a` · **OLD_ORDER_BLOB:** `b3e3860d0508133e30f9c462921ecd58a2c6850f` · **B_REMOTE_HEAD_AT_DESIGN:** `f5e41ab686a3ea97a99d5d2362b49ca228808513` · **SOURCE_BLOBS: ** `68349976f3e988989cc3133f597297d6ca3bd887`, `4d5bb75ee8a22ad506ceff962e69e53a15d88563` (B7/B8 wrapper-only source change).
#12 `6542067869` and remote B HEAD `bc2bf16fafc2c27cc081b864f42b97f90671ecf9` confirm B-18 B7/B8 REMOTE_DONE 2/8 (normal unittest 2/2 exit0, C04 integrated `d7f5684207fabb307e8e00d4c8211351b1f7e8a0`); B1–B6 remain unimplemented and must all be completed. Earlier B-17 is also REMOTE_DONE; never repeat it. Do not reuse any of those eight. RF-063 exclusively owns both SOURCE files under scripts/diagnostics (RF-063 original Owner table checked). B1–B6 are previously verified reserve items **revalidated against current B SOURCE BODY**; B7–B8 were already completed remotely and are excluded from this executable order. B1–B6 TARGET paths rechecked 404 on B and integration after partial B7/B8 push. B7/B8 removed from executable queue; their existing code/tests are NOT new work.

**2026-10-31 20h C03 delta:** B18 B7/B8 actual SOURCE BODY MOVE and normal test remotely verified, integrated by C04 and accepted scoped by C05; B1–B6 remain READY=6/6. All six current SOURCE functions unchanged at `68349976...`; all six TARGETs 404 on both B/integration. Future reserve R1–R6 bodies unchanged after B source `run_m26_scorecard.py` moved from `da20247c` to `4d5bb75e`, all six targets 404 on B/integration, DESIGN ONLY. New document does not cancel a B run that pinned previous C01.

**Single-document contract:** Read only this C01; pin CANONICAL_HEAD/ORDER_BLOB/B_REMOTE_HEAD. No D00/RF/queue/C03/handoff lookup or self-selection. Move the exact BODY to the named new B Owner, preserve SOURCE public signature as thin wrapper, caller/monkeypatch/use-time global parity, outputs and exceptions. For global references use `facade` passed at invocation; no Owner→SOURCE import or duplicate calculation. Each of B1–B6 is mandatory; blocked item does not stop remaining safe items. A newer C01 does not retroactively cancel a started order.

**Safety:** read-only diagnostic projection and offline scorecard math; mock/fake/TemporaryDirectory only. Never invoke actual `main()`, PowerShell/process inspection, runtime health probes, real reports, broker/order/Guard/Step5C/UEF, RunLab, live network, operational DB/state, CI/frozen oracle or deployment. B code/test branch only; no docs/RF/STATUS/C04/C05 or force push. One normal targeted unittest/pytest exit0 is G2; no blanket -O/full peer/hosted CI. Terminal HTTPS auth failure is PUSH_BLOCKED only; approved exact-tree expected-head lease is permitted, not force. After B commit/push, re-fetch remote HEAD/source/Owner/test blob. C04 G3 integration and C05 DONE separate.

**Allowed code/test:** `scripts/diagnostics/check_q9_q12_readiness.py`, `scripts/diagnostics/run_m26_scorecard.py`, the six exact new B TARGET paths B1–B6 below, and `tests/test_p15_rf063_18h_readiness_projection_owners.py` only.

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
**Normal targeted test:** `test_b1_read_json` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: missing temp path → {}; BOM JSON object → dict. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all six pending items run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B2**.

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
**Normal targeted test:** `test_b2_parse_dt` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: 2026-10-31T00:00:00Z → 2026-10-31 09:00+09:00; invalid → None. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all six pending items run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B3**.

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
**Normal targeted test:** `test_b3_artifact` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: missing temp path → exists=False,size_bytes=0. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all six pending items run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B4**.

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
**Normal targeted test:** `test_b4_q9_checks` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: empty temp root/day → window_count=0 and no timestamps. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all six pending items run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B5**.

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
**Normal targeted test:** `test_b5_baseline_artifacts` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: empty temp root/day → q10/q11/q12 groups with missing artifacts. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all six pending items run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B6**.

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
**Normal targeted test:** `test_b6_evaluate` in `tests/test_p15_rf063_18h_readiness_projection_owners.py`. Fixture input→expected: phase=preopen, live.running=False, processes={} → blocker live_session_not_running. Compare original golden against facade wrapper and Owner, include negative/exception and monkeypatch seam parity, AST thin-wrapper check. Use temp paths/in-memory only. After all six pending items run `python -m py_compile scripts/diagnostics/check_q9_q12_readiness.py scripts/diagnostics/run_m26_scorecard.py scripts/diagnostics/*readiness*projection.py scripts/diagnostics/m26_scorecard_*_projection.py` and `python -m unittest tests/test_p15_rf063_18h_readiness_projection_owners.py -v` (equivalent scoped pytest allowed); record actual exit/PASS. Commit/push own B source/Owner/test and re-fetch HEAD/blob. If blocked record reason and **continue B7**.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY

These six RF-063 SOURCE bodies were independently inspected at B/integration blob `da20247c7177389f4f020c99474a0734218461a7`, all six new TARGET paths returned 404 on B and integration. The current order B7/B8 changes the same SOURCE file, so C03 must recheck its fresh blob before promotion. No B self-selection.

### R1 | RF-063 | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_to_epoch` @ L26 | BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563` → TARGET `scripts/diagnostics/m26_scorecard_epoch_projection.py::_to_epoch` (404 B/integration, B-exclusive)
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
**Safety/patch:** datetime/timezone via facade; no clock if fixed fixture; pure/read-only, no operational invocation. Preserve SOURCE thin wrapper and call-time monkeypatch. **Future normal test input→expected:** None→None; '2026-10-31T00:00:00Z'→UTC epoch; golden/wrapper/Owner parity and negative/exception. **RESERVE_VERIFIED DESIGN ONLY**, not executable until next C03 fresh HEAD/body/target recheck.

### R2 | RF-063 | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_utc_day` @ L49 | BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563` → TARGET `scripts/diagnostics/m26_scorecard_day_projection.py::_utc_day` (404 B/integration, B-exclusive)
```python
def _utc_day(ts: Any) -> str:
    ep = _to_epoch(ts)
    if ep is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(ep, tz=timezone.utc).strftime("%Y-%m-%d")
```
**Safety/patch:** _to_epoch/datetime/timezone via facade; patched clock for None case; pure/read-only, no operational invocation. Preserve SOURCE thin wrapper and call-time monkeypatch. **Future normal test input→expected:** epoch 0→'1970-01-01'; missing timestamp→patched UTC date; golden/wrapper/Owner parity and negative/exception. **RESERVE_VERIFIED DESIGN ONLY**, not executable until next C03 fresh HEAD/body/target recheck.

### R3 | RF-063 | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_iter_jsonl` @ L56 | BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563` → TARGET `scripts/diagnostics/m26_scorecard_jsonl_projection.py::_iter_jsonl` (404 B/integration, B-exclusive)
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
**Safety/patch:** json/Path via facade, temp only; pure/read-only, no operational invocation. Preserve SOURCE thin wrapper and call-time monkeypatch. **Future normal test input→expected:** missing temp file→[]; temp JSONL with one dict+invalid line→[dict]; golden/wrapper/Owner parity and negative/exception. **RESERVE_VERIFIED DESIGN ONLY**, not executable until next C03 fresh HEAD/body/target recheck.

### R4 | RF-063 | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_safe_int` @ L74 | BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563` → TARGET `scripts/diagnostics/m26_scorecard_int_projection.py::_safe_int` (404 B/integration, B-exclusive)
```python
def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except Exception:
        return int(default)
```
**Safety/patch:** pure numeric exception parity; pure/read-only, no operational invocation. Preserve SOURCE thin wrapper and call-time monkeypatch. **Future normal test input→expected:** '3.9'→3; invalid with default=7→7; golden/wrapper/Owner parity and negative/exception. **RESERVE_VERIFIED DESIGN ONLY**, not executable until next C03 fresh HEAD/body/target recheck.

### R5 | RF-063 | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_safe_float` @ L81 | BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563` → TARGET `scripts/diagnostics/m26_scorecard_float_projection.py::_safe_float` (404 B/integration, B-exclusive)
```python
def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)
```
**Safety/patch:** pure numeric exception parity; pure/read-only, no operational invocation. Preserve SOURCE thin wrapper and call-time monkeypatch. **Future normal test input→expected:** '2.5'→2.5; invalid with default=1.5→1.5; golden/wrapper/Owner parity and negative/exception. **RESERVE_VERIFIED DESIGN ONLY**, not executable until next C03 fresh HEAD/body/target recheck.

### R6 | RF-063 | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_load_close_price_by_symbol` @ L98 | BLOB=`4d5bb75ee8a22ad506ceff962e69e53a15d88563` → TARGET `scripts/diagnostics/m26_scorecard_close_price_projection.py::_load_close_price_by_symbol` (404 B/integration, B-exclusive)
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
**Safety/patch:** csv/_utc_day/_safe_float via facade, temp CSV only; pure/read-only, no operational invocation. Preserve SOURCE thin wrapper and call-time monkeypatch. **Future normal test input→expected:** missing temp CSV→{}; temp CSV with valid symbol/close/day→symbol price; golden/wrapper/Owner parity and negative/exception. **RESERVE_VERIFIED DESIGN ONLY**, not executable until next C03 fresh HEAD/body/target recheck.

## REPORT / PUSH
#12: `ORDER_ID=B-20261031-18 | CANONICAL_HEAD | ORDER_BLOB | B_REMOTE_BEFORE→AFTER | B1..B6 ITEM_STATUS; B7/B8 REMOTE_DONE (do not re-run as new work) | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | MOVED_FUNCTIONS | SOURCE_LOC_BEFORE_AFTER | FIRST_BLOCKER | NEXT_SAFE_ITEM | PUSH_REMOTE_SHA/PUSH_BLOCKED | START_KST/END_KST/ELAPSED_MIN`. Times measured only. C03 document push is not code G1/G2/G3 or RF_DONE. RunLab SOURCE_UNKNOWN/exit255 remains SAFETY_HOLD.
