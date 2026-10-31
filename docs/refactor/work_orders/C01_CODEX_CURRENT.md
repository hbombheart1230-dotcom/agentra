# C01 — Codex B | B-20261031-17 | FAST-3 eight NEW verified SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_ISSUANCE:** `420b885efbff732bad9730202fa23f3afab926a2` · **OLD_ORDER_BLOB:** `24489087735d0affa3e87b2e7997ded2c51fcd57` · **B_REMOTE_HEAD_AT_DESIGN:** `c8efd3b1332d68d5de12dc95ca80477b066ac5b0` · **SOURCE_BLOBS:** `1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d`, `2c493ba7ba5b252033316202142d35fc94b4ff97`. #12 `6540466623` and remote B HEAD confirm prior B-20261031-16 B1–B8 REMOTE_DONE, normal 5/5 exit0 and new owner/test blobs. Prior completed items never reused. RF-063 owns `scripts/diagnostics/check_alert_policy_v1.py` and `scripts/diagnostics/check_metrics_schema_v1.py` exclusively; integration source blobs identical. B1–B6 promote previous verified reserves after recheck; B7/B8 separately inspected pure computations. All five new TARGET modules checked ABSENT 404 on B and integration.

**Single-document execution contract:** Read this C01/C02 only, pin order blob, canonical HEAD and actor HEAD; do not read D00/RF/queue/C03/handoff or self-select. Move the entire exact SOURCE computation BODY to the named new actor-only TARGET; SOURCE keeps original signature/defaults/annotations as thin delegation wrapper, TARGET never imports SOURCE. For dynamic globals (including imports, constants and monkeypatchable helpers), TARGET accepts keyword-only `facade` and uses `facade.NAME` at call time; SOURCE passes `sys.modules[__name__]` or equivalent. Preserve byte output, identity, ordering, exceptions and caller patch seams; use golden original vs wrapper/Owner, thin-wrapper AST and post-import patch tests. Pure helpers may omit facade. Never count KEEP, same-SHA PASS, or pre-moved code as new BODY MOVE. Complete every safe item even if one is blocked; an already-started order is not retroactively cancelled.

**Safety:** fake/in-memory/TemporaryDirectory and patched environment only. No actual reports/main(), real account/order/Broker/Guard/Step5C/UEF/RunLab, network, operational state, deployment, frozen oracle, CI workflow, force push, other actor branch or docs/RF/STATUS/C04/C05. One normal targeted unittest/pytest exit0 on changed scope is G2; no blanket -O/full peer/hosted CI. Actor commits/pushes code/test on own branch only (normal push or approved exact-tree expected-head lease), re-fetches remote HEAD/source/target/test blobs. HTTPS auth failure is PUSH_BLOCKED only; continue other safe items. C04 integration and C05 G1/G2/G3/DONE separate.

**Allowed code/test:** `scripts/diagnostics/check_alert_policy_v1.py`, `scripts/diagnostics/check_metrics_schema_v1.py`, explicitly named new B target modules and `tests/test_p15_rf063_17h_diagnostic_owners.py` only.

## B1 | RF-063 | SOURCE `scripts/diagnostics/check_alert_policy_v1.py::_to_float` @ L20 | SOURCE_BLOB=`1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d`
**TARGET:** `scripts/diagnostics/alert_policy_scalar_projection.py::_to_float` (NEW B-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default
```
**Wrapper/patch:** pure float fallback; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_b1_to_float` in `tests/test_p15_rf063_17h_diagnostic_owners.py`. **Input→expected:** '1.5' → 1.5; 'bad',default=2 → 2. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile scripts/diagnostics/check_alert_policy_v1.py scripts/diagnostics/alert_policy_scalar_projection.py` and after all eight `python -m unittest tests/test_p15_rf063_17h_diagnostic_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push B source/Owner/test, re-fetch SHA/blob; if blocked continue B2.

## B2 | RF-063 | SOURCE `scripts/diagnostics/check_alert_policy_v1.py::_to_int` @ L27 | SOURCE_BLOB=`1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d`
**TARGET:** `scripts/diagnostics/alert_policy_scalar_projection.py::_to_int` (NEW B-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _to_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except Exception:
        return default
```
**Wrapper/patch:** pure int(float) truncation; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_b2_to_int` in `tests/test_p15_rf063_17h_diagnostic_owners.py`. **Input→expected:** '2.9' → 2; 'bad',default=4 → 4. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile scripts/diagnostics/check_alert_policy_v1.py scripts/diagnostics/alert_policy_scalar_projection.py` and after all eight `python -m unittest tests/test_p15_rf063_17h_diagnostic_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push B source/Owner/test, re-fetch SHA/blob; if blocked continue B3.

## B3 | RF-063 | SOURCE `scripts/diagnostics/check_alert_policy_v1.py::_env_float` @ L34 | SOURCE_BLOB=`1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d`
**TARGET:** `scripts/diagnostics/alert_policy_env_projection.py::_env_float` (NEW B-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _env_float(name: str, default: float) -> float:
    raw = str(os.getenv(name, "") or "").strip()
    if not raw:
        return float(default)
    return _to_float(raw, float(default))
```
**Wrapper/patch:** os.getenv and _to_float via SOURCE facade; patched env only; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_b3_env_float` in `tests/test_p15_rf063_17h_diagnostic_owners.py`. **Input→expected:** unset default=0.7 → 0.7; env='0.4' → 0.4. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile scripts/diagnostics/check_alert_policy_v1.py scripts/diagnostics/alert_policy_env_projection.py` and after all eight `python -m unittest tests/test_p15_rf063_17h_diagnostic_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push B source/Owner/test, re-fetch SHA/blob; if blocked continue B4.

## B4 | RF-063 | SOURCE `scripts/diagnostics/check_alert_policy_v1.py::_env_int` @ L41 | SOURCE_BLOB=`1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d`
**TARGET:** `scripts/diagnostics/alert_policy_env_projection.py::_env_int` (NEW B-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _env_int(name: str, default: int) -> int:
    raw = str(os.getenv(name, "") or "").strip()
    if not raw:
        return int(default)
    return _to_int(raw, int(default))
```
**Wrapper/patch:** os.getenv and _to_int via SOURCE facade; patched env only; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_b4_env_int` in `tests/test_p15_rf063_17h_diagnostic_owners.py`. **Input→expected:** unset default=3 → 3; env='7.9' → 7. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile scripts/diagnostics/check_alert_policy_v1.py scripts/diagnostics/alert_policy_env_projection.py` and after all eight `python -m unittest tests/test_p15_rf063_17h_diagnostic_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push B source/Owner/test, re-fetch SHA/blob; if blocked continue B5.

## B5 | RF-063 | SOURCE `scripts/diagnostics/check_alert_policy_v1.py::_env_fail_on` @ L48 | SOURCE_BLOB=`1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d`
**TARGET:** `scripts/diagnostics/alert_policy_env_projection.py::_env_fail_on` (NEW B-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _env_fail_on(default: str = "critical") -> str:
    raw = str(os.getenv("ALERT_POLICY_FAIL_ON", "") or "").strip().lower()
    if raw in ("none", "warning", "critical"):
        return raw
    return str(default)
```
**Wrapper/patch:** os.getenv via SOURCE facade; patched env only; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_b5_env_fail_on` in `tests/test_p15_rf063_17h_diagnostic_owners.py`. **Input→expected:** env='WARNING' → 'warning'; env='other' → 'critical'. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile scripts/diagnostics/check_alert_policy_v1.py scripts/diagnostics/alert_policy_env_projection.py` and after all eight `python -m unittest tests/test_p15_rf063_17h_diagnostic_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push B source/Owner/test, re-fetch SHA/blob; if blocked continue B6.

## B6 | RF-063 | SOURCE `scripts/diagnostics/check_alert_policy_v1.py::_build_parser` @ L55 | SOURCE_BLOB=`1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d`
**TARGET:** `scripts/diagnostics/alert_policy_cli_projection.py::_build_parser` (NEW B-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Check alert policy threshold gates from metrics schema v1.")
    p.add_argument("--event-log-path", default="data/logs/events.jsonl")
    p.add_argument("--report-dir", default="reports/metrics")
    p.add_argument("--day", default=None)
    p.add_argument("--metrics-json-path", default="")

    p.add_argument(
        "--llm-success-rate-min",
        type=float,
        default=_env_float("ALERT_POLICY_LLM_SUCCESS_RATE_MIN", 0.70),
    )
    p.add_argument(
        "--llm-circuit-open-rate-max",
        type=float,
        default=_env_float("ALERT_POLICY_LLM_CIRCUIT_OPEN_RATE_MAX", 0.30),
    )
    p.add_argument(
        "--execution-blocked-rate-max",
        type=float,
        default=_env_float("ALERT_POLICY_EXECUTION_BLOCKED_RATE_MAX", 0.60),
    )
    p.add_argument(
        "--execution-approved-executed-gap-max",
        type=int,
        default=_env_int("ALERT_POLICY_EXECUTION_APPROVED_EXECUTED_GAP_MAX", 0),
    )
    p.add_argument(
        "--api-429-rate-max",
        type=float,
        default=_env_float("ALERT_POLICY_API_429_RATE_MAX", 0.20),
    )
    p.add_argument(
        "--portfolio-guard-blocked-ratio-max",
        type=float,
        default=_env_float("ALERT_POLICY_PORTFOLIO_GUARD_BLOCKED_RATIO_MAX", 0.70),
    )
    p.add_argument(
        "--portfolio-guard-strategy-budget-exceeded-max",
        type=int,
        default=_env_int("ALERT_POLICY_PORTFOLIO_GUARD_STRATEGY_BUDGET_EXCEEDED_MAX", 20),
    )

    p.add_argument("--fail-on", choices=["none", "warning", "critical"], default=_env_fail_on("critical"))
    p.add_argument("--json", action="store_true")
    return p
```
**Wrapper/patch:** argparse/_env_float/_env_int/_env_fail_on via SOURCE facade; fake argv only; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_b6_build_parser` in `tests/test_p15_rf063_17h_diagnostic_owners.py`. **Input→expected:** parse_args(['--json','--fail-on','none']) → json=True, fail_on='none'. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile scripts/diagnostics/check_alert_policy_v1.py scripts/diagnostics/alert_policy_cli_projection.py` and after all eight `python -m unittest tests/test_p15_rf063_17h_diagnostic_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push B source/Owner/test, re-fetch SHA/blob; if blocked continue B7.

## B7 | RF-063 | SOURCE `scripts/diagnostics/check_metrics_schema_v1.py::_is_number` @ L16 | SOURCE_BLOB=`2c493ba7ba5b252033316202142d35fc94b4ff97`
**TARGET:** `scripts/diagnostics/metrics_schema_scalar_projection.py::_is_number` (NEW B-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)
```
**Wrapper/patch:** pure, bool excluded; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_b7_is_number` in `tests/test_p15_rf063_17h_diagnostic_owners.py`. **Input→expected:** 1 → True; 1.5 → True; True → False; '1' → False. Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile scripts/diagnostics/check_metrics_schema_v1.py scripts/diagnostics/metrics_schema_scalar_projection.py` and after all eight `python -m unittest tests/test_p15_rf063_17h_diagnostic_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push B source/Owner/test, re-fetch SHA/blob; if blocked continue B8.

## B8 | RF-063 | SOURCE `scripts/diagnostics/check_metrics_schema_v1.py::_json_path_get` @ L28 | SOURCE_BLOB=`2c493ba7ba5b252033316202142d35fc94b4ff97`
**TARGET:** `scripts/diagnostics/metrics_schema_path_projection.py::_json_path_get` (NEW B-exclusive, 404 on actor/integration). **Exact BODY to MOVE:**
```python
def _json_path_get(obj: Dict[str, Any], path: str) -> Tuple[bool, Any]:
    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur
```
**Wrapper/patch:** pure, preserve missing vs None; preserve signature/callers/monkeypatch, no duplicate BODY. **Targeted normal test:** `test_b8_json_path_get` in `tests/test_p15_rf063_17h_diagnostic_owners.py`. **Input→expected:** ({'a':{'b':0}},'a.b') → (True,0); 'a.c' → (False,None). Include original golden/wrapper/Owner parity, negative/exception, patch seam and thin-wrapper AST. **Normal:** `python -m py_compile scripts/diagnostics/check_metrics_schema_v1.py scripts/diagnostics/metrics_schema_path_projection.py` and after all eight `python -m unittest tests/test_p15_rf063_17h_diagnostic_owners.py -v` (equivalent scoped pytest allowed); report actual exit/PASS. Commit/push B source/Owner/test, re-fetch SHA/blob; if blocked continue Bhandoff.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY

### R1 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_read_json` @ L31 | BLOB=`68349976f3e988989cc3133f597297d6ca3bd887` → TARGET `scripts/diagnostics/q9_readiness_json_projection.py::_read_json` (404 actor/integration)
```python
def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}
```
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** missing temp path → {}; UTF-8-SIG object → dict. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

### R2 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_parse_dt` @ L39 | BLOB=`68349976f3e988989cc3133f597297d6ca3bd887` → TARGET `scripts/diagnostics/q9_readiness_time_projection.py::_parse_dt` (404 actor/integration)
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
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** 2026-10-31T00:00:00Z → 09:00 KST; invalid → None. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

### R3 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_artifact` @ L117 | BLOB=`68349976f3e988989cc3133f597297d6ca3bd887` → TARGET `scripts/diagnostics/q9_readiness_artifact_projection.py::_artifact` (404 actor/integration)
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
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** missing temp path → exists=False,size_bytes=0. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

### R4 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_q9_checks` @ L129 | BLOB=`68349976f3e988989cc3133f597297d6ca3bd887` → TARGET `scripts/diagnostics/q9_readiness_window_projection.py::_q9_checks` (404 actor/integration)
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
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** empty temp root → window_count=0. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

### R5 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_baseline_artifacts` @ L151 | BLOB=`68349976f3e988989cc3133f597297d6ca3bd887` → TARGET `scripts/diagnostics/q9_readiness_baseline_projection.py::_baseline_artifacts` (404 actor/integration)
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
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** empty temp root → q10/q11/q12 keys, absent artifacts. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

### R6 | RF-063 | SOURCE `scripts/diagnostics/check_q9_q12_readiness.py::_evaluate` @ L185 | BLOB=`68349976f3e988989cc3133f597297d6ca3bd887` → TARGET `scripts/diagnostics/q9_readiness_evaluation_projection.py::_evaluate` (404 actor/integration)
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
**Safety/patch:** read-only diagnostic, fake/temp only; dynamic SOURCE globals through facade, no main/operational effect. **Future targeted normal input→expected:** preopen,live.running=False,processes={} → live_session_not_running blocker. Original/wrapper/Owner golden and thin wrapper required. **RESERVE_VERIFIED design only; NOT executable this order.**

## REPORT / PUSH

#12: `ORDER_ID=B-20261031-17 | CANONICAL_HEAD | ORDER_BLOB | B_REMOTE_BEFORE→AFTER | B1..B8 ITEM_STATUS | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | MOVED_FUNCTIONS | SOURCE_LOC_BEFORE_AFTER | FIRST_BLOCKER | NEXT_SAFE_ITEM | PUSH_REMOTE_SHA/PUSH_BLOCKED | START_KST/END_KST/ELAPSED_MIN`. Times measured only. Terminal HTTPS auth may use approved exact-tree expected-head lease, never force. C03 document commit is not code G1/G2/G3 or RF_DONE. RunLab exit255/RUN_SOURCE_SHA UNKNOWN operating SAFETY_HOLD.
