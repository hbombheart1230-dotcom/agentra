# C01 — Codex B | B-20261031-16 | FAST-3 eight NEW verified SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_ISSUANCE:** `7a1bf9d0d1eda1615803645afd6a5481a242994b` · **OLD_ORDER_BLOB:** `d8d15bcf3249c7d960e8dc15624e569428323828` · **B_REMOTE_HEAD_AT_DESIGN:** `56073f0d0b3852d5a093d8eb3263fd91adb35462` · **SOURCE_BLOB:** `1a9d7fb0e803b0df0ca4bac00a679a9da31f3557`. #12 comment 6539961171 and B remote HEAD prove B-20261031-14 B1–B8 REMOTE_DONE (normal unittest 6/6, eight owner targets present). Do NOT reuse any completed BODY, same-SHA PASS or KEEP. This order replaces all eight, no work is pre-completed. RF-063 B owns `scripts/diagnostics/run_m31_weekly_health_summary.py` and `check_alert_policy_v1.py` (RF-063 physical owner file list verified). New TARGET modules listed below were checked 404 on both B remote and integration; only these actor-owned files may change.

## SINGLE DOCUMENT CONTRACT — COMPLETE ALL B1–B8

Read only this C01, pin ORDER_BLOB/CANONICAL_HEAD/B_REMOTE_HEAD and source blobs at start. Do not read D00/RF/queue/C03/handoff or self-select tasks. **For each B item move the entire exact function computation BODY** from SOURCE to TARGET; SOURCE retains original signature, defaults, annotations and public import as a thin wrapper. TARGET must never import SOURCE. For dynamic SOURCE globals use TARGET keyword-only `facade` and `facade.NAME` at invocation; SOURCE passes `_migration_sys.modules[__name__]`, retaining post-import monkeypatch and exception behavior. Pure helpers may omit facade. Preserve generator/exception/output/order and import-time semantics. After each item continue the next even if prior item PASS/blocked; do not stop after first commit. For pre-existing remote move mark REMOTE_DONE, not new work.

**Safety:** all tests fake/in-memory/TemporaryDirectory; only read fake JSON. Do not execute `main`, operating reports, live account, real order, Broker, Guard, Step5C, UEF, RunLab, network, deployment, frozen oracle, CI workflow, force-push or policy. Change only `scripts/diagnostics/run_m31_weekly_health_summary.py`, the explicitly named new B Owner modules and `tests/test_p15_rf063_16h_weekly_health_owners.py`. Do not touch A branch or any docs/RF/STATUS/queue/C04/C05. Normal targeted unittest/pytest exit0 once is G2; blanket -O/full peer/full CI is not required. Commit/push B-only code/tests by normal non-force push or approved exact-tree expected-head lease; re-fetch remote B HEAD and source/target/test blobs. Terminal HTTPS failure alone is PUSH_BLOCKED, not test failure; continue other safe items. C04 integration and C05 G1/G2/G3/DONE are separate.

## B1 | RF-063 | SOURCE `scripts/diagnostics/run_m31_weekly_health_summary.py::_to_epoch` @ L19 | SOURCE_BLOB=`1a9d7fb0e803b0df0ca4bac00a679a9da31f3557`

**TARGET:** `scripts/diagnostics/m31_weekly_time_projection.py::_to_epoch` (NEW B-exclusive Owner; absent on B/integration). **Actual SOURCE computation BODY to MOVE unchanged:**

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

**Wrapper/callers/monkeypatch:** datetime/timezone call-time facade; preserve UTC parsing, naive UTC and invalid None. SOURCE retains exact original signature and thin delegation; no second computation in SOURCE, no TARGET→SOURCE import. Compare original pre-move output and new wrapper/Owner on normal, negative, exception and patched-global cases; AST/source check ensures BODY truly removed. **Test method:** `test_b1_to_epoch` in `tests/test_p15_rf063_16h_weekly_health_owners.py`. **Input→expected:** '2026-10-31T00:00:00Z' → 1793404800; '' → None; 0 → 0; patch datetime post-import. Isolation: in-memory/fake temp only. **Normal command:** `python -m py_compile scripts/diagnostics/run_m31_weekly_health_summary.py scripts/diagnostics/m31_weekly_time_projection.py`; then `python -m unittest tests/test_p15_rf063_16h_weekly_health_owners.py -v` (once all B1–B8 exist; equivalent exact-scope pytest acceptable). Record actual exit/PASS, never invent. Commit/push B source+Owner+test and re-fetch remote SHA/blob; if blocked, report precise reason and continue B2.

## B2 | RF-063 | SOURCE `scripts/diagnostics/run_m31_weekly_health_summary.py::_utc_day` @ L44 | SOURCE_BLOB=`1a9d7fb0e803b0df0ca4bac00a679a9da31f3557`

**TARGET:** `scripts/diagnostics/m31_weekly_time_projection.py::_utc_day` (NEW B-exclusive Owner; absent on B/integration). **Actual SOURCE computation BODY to MOVE unchanged:**

```python
def _utc_day(ts: Any) -> Optional[str]:
    e = _to_epoch(ts)
    if e is None:
        return None
    return datetime.fromtimestamp(e, tz=timezone.utc).strftime("%Y-%m-%d")
```

**Wrapper/callers/monkeypatch:** _to_epoch/datetime/timezone call-time facade; keep None and UTC day. SOURCE retains exact original signature and thin delegation; no second computation in SOURCE, no TARGET→SOURCE import. Compare original pre-move output and new wrapper/Owner on normal, negative, exception and patched-global cases; AST/source check ensures BODY truly removed. **Test method:** `test_b2_utc_day` in `tests/test_p15_rf063_16h_weekly_health_owners.py`. **Input→expected:** '2026-10-31T23:00:00Z' → '2026-10-31'; invalid → None; patched _to_epoch observed. Isolation: in-memory/fake temp only. **Normal command:** `python -m py_compile scripts/diagnostics/run_m31_weekly_health_summary.py scripts/diagnostics/m31_weekly_time_projection.py`; then `python -m unittest tests/test_p15_rf063_16h_weekly_health_owners.py -v` (once all B1–B8 exist; equivalent exact-scope pytest acceptable). Record actual exit/PASS, never invent. Commit/push B source+Owner+test and re-fetch remote SHA/blob; if blocked, report precise reason and continue B3.

## B3 | RF-063 | SOURCE `scripts/diagnostics/run_m31_weekly_health_summary.py::_read_json` @ L55 | SOURCE_BLOB=`1a9d7fb0e803b0df0ca4bac00a679a9da31f3557`

**TARGET:** `scripts/diagnostics/m31_weekly_read_projection.py::_read_json` (NEW B-exclusive Owner; absent on B/integration). **Actual SOURCE computation BODY to MOVE unchanged:**

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

**Wrapper/callers/monkeypatch:** Path/json via call-time facade; only read TemporaryDirectory fixture, never operating reports. SOURCE retains exact original signature and thin delegation; no second computation in SOURCE, no TARGET→SOURCE import. Compare original pre-move output and new wrapper/Owner on normal, negative, exception and patched-global cases; AST/source check ensures BODY truly removed. **Test method:** `test_b3_read_json` in `tests/test_p15_rf063_16h_weekly_health_owners.py`. **Input→expected:** temp JSON {'x':1} → {'x':1}; malformed/non-dict/missing → {}; patched json.loads observed. Isolation: in-memory/fake temp only. **Normal command:** `python -m py_compile scripts/diagnostics/run_m31_weekly_health_summary.py scripts/diagnostics/m31_weekly_read_projection.py`; then `python -m unittest tests/test_p15_rf063_16h_weekly_health_owners.py -v` (once all B1–B8 exist; equivalent exact-scope pytest acceptable). Record actual exit/PASS, never invent. Commit/push B source+Owner+test and re-fetch remote SHA/blob; if blocked, report precise reason and continue B4.

## B4 | RF-063 | SOURCE `scripts/diagnostics/run_m31_weekly_health_summary.py::_parse_day` @ L65 | SOURCE_BLOB=`1a9d7fb0e803b0df0ca4bac00a679a9da31f3557`

**TARGET:** `scripts/diagnostics/m31_weekly_time_projection.py::_parse_day` (NEW B-exclusive Owner; absent on B/integration). **Actual SOURCE computation BODY to MOVE unchanged:**

```python
def _parse_day(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
```

**Wrapper/callers/monkeypatch:** datetime/timezone call-time facade; invalid date raises same ValueError. SOURCE retains exact original signature and thin delegation; no second computation in SOURCE, no TARGET→SOURCE import. Compare original pre-move output and new wrapper/Owner on normal, negative, exception and patched-global cases; AST/source check ensures BODY truly removed. **Test method:** `test_b4_parse_day` in `tests/test_p15_rf063_16h_weekly_health_owners.py`. **Input→expected:** '2026-10-31' → UTC-aware 2026-10-31 midnight; 'bad' raises ValueError. Isolation: in-memory/fake temp only. **Normal command:** `python -m py_compile scripts/diagnostics/run_m31_weekly_health_summary.py scripts/diagnostics/m31_weekly_time_projection.py`; then `python -m unittest tests/test_p15_rf063_16h_weekly_health_owners.py -v` (once all B1–B8 exist; equivalent exact-scope pytest acceptable). Record actual exit/PASS, never invent. Commit/push B source+Owner+test and re-fetch remote SHA/blob; if blocked, report precise reason and continue B5.

## B5 | RF-063 | SOURCE `scripts/diagnostics/run_m31_weekly_health_summary.py::_window_days` @ L69 | SOURCE_BLOB=`1a9d7fb0e803b0df0ca4bac00a679a9da31f3557`

**TARGET:** `scripts/diagnostics/m31_weekly_time_projection.py::_window_days` (NEW B-exclusive Owner; absent on B/integration). **Actual SOURCE computation BODY to MOVE unchanged:**

```python
def _window_days(*, week_end: str, days: int) -> List[str]:
    end_dt = _parse_day(week_end)
    n = max(1, int(days))
    start_dt = end_dt - timedelta(days=n - 1)
    out: List[str] = []
    cur = start_dt
    while cur <= end_dt:
        out.append(cur.strftime("%Y-%m-%d"))
        cur += timedelta(days=1)
    return out
```

**Wrapper/callers/monkeypatch:** _parse_day/timedelta via call-time facade; preserve day order, min-one behavior. SOURCE retains exact original signature and thin delegation; no second computation in SOURCE, no TARGET→SOURCE import. Compare original pre-move output and new wrapper/Owner on normal, negative, exception and patched-global cases; AST/source check ensures BODY truly removed. **Test method:** `test_b5_window_days` in `tests/test_p15_rf063_16h_weekly_health_owners.py`. **Input→expected:** week_end='2026-10-31', days=3 → ['2026-10-29','2026-10-30','2026-10-31']; days=0 → ['2026-10-31']. Isolation: in-memory/fake temp only. **Normal command:** `python -m py_compile scripts/diagnostics/run_m31_weekly_health_summary.py scripts/diagnostics/m31_weekly_time_projection.py`; then `python -m unittest tests/test_p15_rf063_16h_weekly_health_owners.py -v` (once all B1–B8 exist; equivalent exact-scope pytest acceptable). Record actual exit/PASS, never invent. Commit/push B source+Owner+test and re-fetch remote SHA/blob; if blocked, report precise reason and continue B6.

## B6 | RF-063 | SOURCE `scripts/diagnostics/run_m31_weekly_health_summary.py::_item` @ L81 | SOURCE_BLOB=`1a9d7fb0e803b0df0ca4bac00a679a9da31f3557`

**TARGET:** `scripts/diagnostics/m31_weekly_summary_projection.py::_item` (NEW B-exclusive Owner; absent on B/integration). **Actual SOURCE computation BODY to MOVE unchanged:**

```python
def _item(
    *,
    item_id: str,
    title: str,
    passed: bool,
    evidence: str,
    required: bool = True,
) -> Dict[str, Any]:
    return {
        "id": item_id,
        "title": title,
        "required": bool(required),
        "passed": bool(passed),
        "evidence": str(evidence),
    }
```

**Wrapper/callers/monkeypatch:** pure dict construction; no facade; preserve bool conversion, key order and string conversion. SOURCE retains exact original signature and thin delegation; no second computation in SOURCE, no TARGET→SOURCE import. Compare original pre-move output and new wrapper/Owner on normal, negative, exception and patched-global cases; AST/source check ensures BODY truly removed. **Test method:** `test_b6_item` in `tests/test_p15_rf063_16h_weekly_health_owners.py`. **Input→expected:** item_id='x',title='X',passed=0,evidence='e' → {'id':'x','title':'X','required':True,'passed':False,'evidence':'e'}. Isolation: in-memory/fake temp only. **Normal command:** `python -m py_compile scripts/diagnostics/run_m31_weekly_health_summary.py scripts/diagnostics/m31_weekly_summary_projection.py`; then `python -m unittest tests/test_p15_rf063_16h_weekly_health_owners.py -v` (once all B1–B8 exist; equivalent exact-scope pytest acceptable). Record actual exit/PASS, never invent. Commit/push B source+Owner+test and re-fetch remote SHA/blob; if blocked, report precise reason and continue B7.

## B7 | RF-063 | SOURCE `scripts/diagnostics/run_m31_weekly_health_summary.py::_build_markdown` @ L98 | SOURCE_BLOB=`1a9d7fb0e803b0df0ca4bac00a679a9da31f3557`

**TARGET:** `scripts/diagnostics/m31_weekly_markdown_projection.py::_build_markdown` (NEW B-exclusive Owner; absent on B/integration). **Actual SOURCE computation BODY to MOVE unchanged:**

```python
def _build_markdown(out: Dict[str, Any]) -> str:
    events = out.get("events") if isinstance(out.get("events"), dict) else {}
    policy = out.get("policy") if isinstance(out.get("policy"), dict) else {}
    signoff = out.get("signoff") if isinstance(out.get("signoff"), dict) else {}
    checklist = out.get("checklist") if isinstance(out.get("checklist"), list) else []

    lines = [
        f"# M31 Weekly Health Summary ({out.get('week_start')} ~ {out.get('week_end')})",
        "",
        f"- ok: **{bool(out.get('ok'))}**",
        f"- required_pass_total: **{int(out.get('required_pass_total') or 0)}**",
        f"- required_fail_total: **{int(out.get('required_fail_total') or 0)}**",
        "",
        "## Event Summary",
        "",
        f"- total: **{int(events.get('total') or 0)}**",
        f"- error_total: **{int(events.get('error_total') or 0)}**",
        f"- error_rate: **{float(events.get('error_rate') or 0.0):.2%}**",
        f"- run_total: **{int(events.get('run_total') or 0)}**",
        "",
        "## Post-GoLive Policy Summary",
        "",
        f"- policy_artifact_total: **{int(policy.get('found_total') or 0)}**",
        f"- normal_day_total: **{int(policy.get('normal_day_total') or 0)}**",
        f"- watch_day_total: **{int(policy.get('watch_day_total') or 0)}**",
        f"- incident_day_total: **{int(policy.get('incident_day_total') or 0)}**",
        "",
        "## Final Signoff Summary",
        "",
        f"- signoff_artifact_total: **{int(signoff.get('found_total') or 0)}**",
        f"- approved_day_total: **{int(signoff.get('approved_day_total') or 0)}**",
        f"- hold_day_total: **{int(signoff.get('hold_day_total') or 0)}**",
        "",
        "## Checklist",
        "",
    ]
    for item in checklist:
        mark = "x" if bool(item.get("passed")) else " "
        lines.append(f"- [{mark}] {item.get('title')} | evidence={item.get('evidence')}")

    failures = out.get("failures") if isinstance(out.get("failures"), list) else []
    lines += ["", "## Failures", ""]
    if failures:
        for msg in failures:
            lines.append(f"- {msg}")
    else:
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)
```

**Wrapper/callers/monkeypatch:** pure in-memory formatting; no IO, preserve bytes, list order, trailing newline and exceptions. SOURCE retains exact original signature and thin delegation; no second computation in SOURCE, no TARGET→SOURCE import. Compare original pre-move output and new wrapper/Owner on normal, negative, exception and patched-global cases; AST/source check ensures BODY truly removed. **Test method:** `test_b7_build_markdown` in `tests/test_p15_rf063_16h_weekly_health_owners.py`. **Input→expected:** {'week_start':'2026-10-25','week_end':'2026-10-31','ok':True,'events':{'total':0},'checklist':[]} → header '# M31 Weekly Health Summary (2026-10-25 ~ 2026-10-31)', '## Failures', '- (none)' and final newline. Isolation: in-memory/fake temp only. **Normal command:** `python -m py_compile scripts/diagnostics/run_m31_weekly_health_summary.py scripts/diagnostics/m31_weekly_markdown_projection.py`; then `python -m unittest tests/test_p15_rf063_16h_weekly_health_owners.py -v` (once all B1–B8 exist; equivalent exact-scope pytest acceptable). Record actual exit/PASS, never invent. Commit/push B source+Owner+test and re-fetch remote SHA/blob; if blocked, report precise reason and continue B8.

## B8 | RF-063 | SOURCE `scripts/diagnostics/run_m31_weekly_health_summary.py::_build_parser` @ L149 | SOURCE_BLOB=`1a9d7fb0e803b0df0ca4bac00a679a9da31f3557`

**TARGET:** `scripts/diagnostics/m31_weekly_cli_projection.py::_build_parser` (NEW B-exclusive Owner; absent on B/integration). **Actual SOURCE computation BODY to MOVE unchanged:**

```python
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="M31-3 weekly post-go-live health summary generator.")
    p.add_argument("--event-log-path", default="data/logs/events.jsonl")
    p.add_argument("--policy-report-dir", default="reports/milestones/m30_post_golive")
    p.add_argument("--signoff-report-dir", default="reports/milestones/m30_golive")
    p.add_argument("--report-dir", default="reports/milestones/m31_weekly_health")
    p.add_argument("--week-end", default="2026-02-21")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--max-error-rate", type=float, default=0.20)
    p.add_argument("--max-incident-days", type=int, default=1)
    p.add_argument("--inject-fail", action="store_true")
    p.add_argument("--json", action="store_true")
    return p
```

**Wrapper/callers/monkeypatch:** argparse via call-time facade; parse fake argv only, do not call main or access files. SOURCE retains exact original signature and thin delegation; no second computation in SOURCE, no TARGET→SOURCE import. Compare original pre-move output and new wrapper/Owner on normal, negative, exception and patched-global cases; AST/source check ensures BODY truly removed. **Test method:** `test_b8_build_parser` in `tests/test_p15_rf063_16h_weekly_health_owners.py`. **Input→expected:** parse_args(['--days','3','--json']) → days=3,json=True; empty args → max_error_rate=0.20, days=7. Isolation: in-memory/fake temp only. **Normal command:** `python -m py_compile scripts/diagnostics/run_m31_weekly_health_summary.py scripts/diagnostics/m31_weekly_cli_projection.py`; then `python -m unittest tests/test_p15_rf063_16h_weekly_health_owners.py -v` (once all B1–B8 exist; equivalent exact-scope pytest acceptable). Record actual exit/PASS, never invent. Commit/push B source+Owner+test and re-fetch remote SHA/blob; if blocked, report precise reason and continue Bhandoff.

## FUTURE RESERVE — VERIFIED 6/6, NOT EXECUTABLE IN THIS ORDER

These are **different, not-yet-moved** real SOURCE BODY candidates at B `1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d` in RF-063 exclusive `scripts/diagnostics/check_alert_policy_v1.py`; all three proposed TARGET files are absent on B and integration. The source functions are original calculations (not wrappers/KEEP), inspected at the cited blob. Reserve items require next C03 order before implementation; never self-promote or count as completed.

### R1 | RF-063 | `scripts/diagnostics/check_alert_policy_v1.py::_to_float` L20 | blob `1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d` → `scripts/diagnostics/alert_policy_scalar_projection.py::_to_float` (ABSENT 404)

```python
def _to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default
```

**Safety/patch:** pure float conversion; fake environment via mock.patch.dict, no operating files or main. **Future targeted normal fixture:** 'bad',default=0.4 → 0.4; '1.2' → 1.2; compare original/wrapper/Owner, preserve exception/defaults and no duplicate BODY. `RESERVE_VERIFIED` design only, NOT current B1–B8.

### R2 | RF-063 | `scripts/diagnostics/check_alert_policy_v1.py::_to_int` L27 | blob `1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d` → `scripts/diagnostics/alert_policy_scalar_projection.py::_to_int` (ABSENT 404)

```python
def _to_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except Exception:
        return default
```

**Safety/patch:** pure int conversion; fake environment via mock.patch.dict, no operating files or main. **Future targeted normal fixture:** 'bad',default=2 → 2; '3.9' → 3; compare original/wrapper/Owner, preserve exception/defaults and no duplicate BODY. `RESERVE_VERIFIED` design only, NOT current B1–B8.

### R3 | RF-063 | `scripts/diagnostics/check_alert_policy_v1.py::_env_float` L34 | blob `1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d` → `scripts/diagnostics/alert_policy_env_projection.py::_env_float` (ABSENT 404)

```python
def _env_float(name: str, default: float) -> float:
    raw = str(os.getenv(name, "") or "").strip()
    if not raw:
        return float(default)
    return _to_float(raw, float(default))
```

**Safety/patch:** os.getenv/_to_float call-time facade; no operating env mutation; fake environment via mock.patch.dict, no operating files or main. **Future targeted normal fixture:** patched env '0.25'→0.25; unset default 0.7→0.7; compare original/wrapper/Owner, preserve exception/defaults and no duplicate BODY. `RESERVE_VERIFIED` design only, NOT current B1–B8.

### R4 | RF-063 | `scripts/diagnostics/check_alert_policy_v1.py::_env_int` L41 | blob `1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d` → `scripts/diagnostics/alert_policy_env_projection.py::_env_int` (ABSENT 404)

```python
def _env_int(name: str, default: int) -> int:
    raw = str(os.getenv(name, "") or "").strip()
    if not raw:
        return int(default)
    return _to_int(raw, int(default))
```

**Safety/patch:** os.getenv/_to_int call-time facade; fake environment via mock.patch.dict, no operating files or main. **Future targeted normal fixture:** patched env '3'→3; unset default 2→2; compare original/wrapper/Owner, preserve exception/defaults and no duplicate BODY. `RESERVE_VERIFIED` design only, NOT current B1–B8.

### R5 | RF-063 | `scripts/diagnostics/check_alert_policy_v1.py::_env_fail_on` L48 | blob `1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d` → `scripts/diagnostics/alert_policy_env_projection.py::_env_fail_on` (ABSENT 404)

```python
def _env_fail_on(default: str = "critical") -> str:
    raw = str(os.getenv("ALERT_POLICY_FAIL_ON", "") or "").strip().lower()
    if raw in ("none", "warning", "critical"):
        return raw
    return str(default)
```

**Safety/patch:** os.getenv call-time facade; fake environment via mock.patch.dict, no operating files or main. **Future targeted normal fixture:** patched env 'warning'→'warning'; 'other'→'critical'; compare original/wrapper/Owner, preserve exception/defaults and no duplicate BODY. `RESERVE_VERIFIED` design only, NOT current B1–B8.

### R6 | RF-063 | `scripts/diagnostics/check_alert_policy_v1.py::_build_parser` L55 | blob `1dfc6fa273c691e1d0bc66b3d4adaa0d8034e23d` → `scripts/diagnostics/alert_policy_cli_projection.py::_build_parser` (ABSENT 404)

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

**Safety/patch:** argparse and _env_float/_env_int/_env_fail_on call-time facade; fake environment via mock.patch.dict, no operating files or main. **Future targeted normal fixture:** fake argv --json → True; env defaults patched; no main; compare original/wrapper/Owner, preserve exception/defaults and no duplicate BODY. `RESERVE_VERIFIED` design only, NOT current B1–B8.

## REPORT / PUSH / CONTINUITY

Report to #12: `ORDER_ID=B-20261031-16 | CANONICAL_HEAD | ORDER_BLOB_SHA | B_REMOTE_BEFORE→AFTER | B1..B8 ITEM_STATUS | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | MOVED_FUNCTIONS | SOURCE_LOC_BEFORE_AFTER | FIRST_BLOCKER | NEXT_SAFE_ITEM | PUSH_REMOTE_SHA/PUSH_BLOCKED | START_KST/END_KST/ELAPSED_MIN`. Times only if measured. All safe B items must be completed or individually blocked. C03 document supply is not G1/G2/G3 code or RF_DONE. RunLab exit255 and RUN_SOURCE_SHA UNKNOWN remain operating SAFETY_HOLD.
