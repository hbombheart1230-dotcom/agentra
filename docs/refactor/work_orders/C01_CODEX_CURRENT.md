# C01 — Codex B | B-20261101-02 | FAST-3 8 verified real SOURCE BODY MOVEs

**START ORDER — ONE FILE ONLY.** Read THIS document, then only the named code/test files. Do not read D00/RF/queue/C03/HANDOFF or select tasks yourself. Pin canonical HEAD `9e47ed5230d68814688ff6b48ae2764a8a25222f` (pre-issue), ORDER_BLOB, actor branch HEAD, and ORDER_ID at start; newer documents do not retroactively cancel a started order. Run ALL eight items; if blocked, record precise reason and proceed to the next independent safe item. Never redo completed old order. 

**EVIDENCE:** C03 compared actor/integration exact source blobs, SOURCE original executable bodies, unique target path absence on both refs, RF ownership, and recent #11/#12/#32. Actor A old order A-20261101-01 8/8 REMOTE_DONE at 0cc2d549; B old order B-21 B1–B3 REMOTE_DONE at 30295cc1, B4–B8 remain unfinished and are carried as B1–B5 here, with B6–B8 new. Current C01 old blob `b9f6a1dfcc6e0ca746c738f80e599a12fe54ae49`, C02 old blob `606eb2ce8baaa1abf36b366675f9208878b0745c`. RunLab Exited(255), RUN_SOURCE_SHA=UNKNOWN, operational HOLD. No C03 code/test work or RF DONE is claimed.

**RF/OWNER:** RF-063; CODEX_B exclusively owns all named source and target files. Actor writes only its `work/p15-b-operator-structure-20261022` code/test paths; no D00, RF, queue, STATUS, C04/C05, other actor branch, CI/frozen oracle, Git force-push. All eight target paths confirmed absent on actor and integration before issue. C04 performs selective integration/G3; C05 alone accepts RF DONE.

**SAFETY:** isolated fake in-memory mappings, monkeypatch and TemporaryDirectory only. No real trading, broker, order, guard, Step5C, UEF, RunLab operations, live network, runtime process/queue/lock mutation, operational State/DB/report paths, subprocess, actual CLI main, deploy/restart, or security policy change. Paths/env in these helpers must be fake/patched. Preserve exact public signatures, return type, exceptions, ordering, CLI callers, and SOURCE call-time monkeypatch seams. Source function must become a single-return thin delegation; new Owner must hold the ORIGINAL computation body, never import SOURCE (pass `facade=sys.modules[__name__]` when source globals are referenced). Use import inside SOURCE wrapper or safe top-level alias, no cycles. Capture original preimage golden before edits; compare golden vs SOURCE wrapper vs Owner with positive, negative, exception, and post-import monkeypatch cases; AST prove retired SOURCE calculation body absent, no duplicate/orphan statements.

**TEST/PUSH:** Create NEW `tests/test_p15_rf063_20261101_02h_diagnostics_owners.py` (do not overwrite old B21/A01 tests). Each test must pin exact input→expected below, original golden parity, Owner direct parity, thin-wrapper AST and patch seams. Run `python -m py_compile` on modified source and all new Owner modules; run `python -m unittest tests/test_p15_rf063_20261101_02h_diagnostics_owners.py -v` normal exit0; use safe isolated tests only. Commit ONLY actor code/test; normal non-force push actor branch; re-fetch actor HEAD and source/target/test blob SHAs. If pytest unavailable, stdlib unittest remains valid. If push authentication fails, mark PUSH_BLOCKED but continue other safe items. Report each item IMPLEMENTED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN with measured START/END, normal command exit and exact remote SHA to #12; do not claim G1 for local-only. No mandatory -O/full peer/per-RF hosted CI.

## B1 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_to_epoch` @ L26 | CURRENT_BLOB `4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**NEW TARGET (404 on actor and integration):** `scripts/diagnostics/m26_scorecard_epoch_projection.py::_to_epoch`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
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
**Exact SOURCE thin-wrapper executable statement:** `return _epoch_owner._to_epoch(ts, facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `scripts.diagnostics.m26_scorecard_epoch_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade.datetime/timezone; no real clock needed for fixed timestamps. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_b1_to_epoch`:** None→None; '0'→0; '1970-01-01T00:00:00Z'→0; invalid→None. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue B2.

## B2 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_utc_day` @ L49 | CURRENT_BLOB `4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**NEW TARGET (404 on actor and integration):** `scripts/diagnostics/m26_scorecard_day_projection.py::_utc_day`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
```python
def _utc_day(ts: Any) -> str:
    ep = _to_epoch(ts)
    if ep is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return datetime.fromtimestamp(ep, tz=timezone.utc).strftime("%Y-%m-%d")
```
**Exact SOURCE thin-wrapper executable statement:** `return _day_owner._utc_day(ts, facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `scripts.diagnostics.m26_scorecard_day_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade._to_epoch/datetime/timezone; preserve patched fallback clock. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_b2_utc_day`:** 0→'1970-01-01'; 86400→'1970-01-02'; invalid with patched datetime. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue B3.

## B3 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_iter_jsonl` @ L56 | CURRENT_BLOB `4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**NEW TARGET (404 on actor and integration):** `scripts/diagnostics/m26_scorecard_jsonl_projection.py::_iter_jsonl`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
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
**Exact SOURCE thin-wrapper executable statement:** `return _jsonl_owner._iter_jsonl(path, facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `scripts.diagnostics.m26_scorecard_jsonl_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade.json; temp only, preserve malformed-skip behavior. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_b3_iter_jsonl`:** missing temp path→[]; temp '{"x":1}\nBAD\n[]\n'→[{'x':1}]. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue B4.

## B4 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_safe_int` @ L74 | CURRENT_BLOB `4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**NEW TARGET (404 on actor and integration):** `scripts/diagnostics/m26_scorecard_int_projection.py::_safe_int`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
```python
def _safe_int(v: Any, default: int = 0) -> int:
    try:
        return int(float(v))
    except Exception:
        return int(default)
```
**Exact SOURCE thin-wrapper executable statement:** `return _int_owner._safe_int(v, default)` (keep original signature, annotations, and any docstring; import `scripts.diagnostics.m26_scorecard_int_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** pure numeric; preserve exceptions. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_b4_safe_int`:** '3.9'→3; ('bad',4)→4; invalid default exception parity. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue B5.

## B5 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_safe_float` @ L81 | CURRENT_BLOB `4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**NEW TARGET (404 on actor and integration):** `scripts/diagnostics/m26_scorecard_float_projection.py::_safe_float`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
```python
def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)
```
**Exact SOURCE thin-wrapper executable statement:** `return _float_owner._safe_float(v, default)` (keep original signature, annotations, and any docstring; import `scripts.diagnostics.m26_scorecard_float_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** pure numeric; preserve exceptions. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_b5_safe_float`:** '1.25'→1.25; ('bad',2.5)→2.5; NaN parity. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue B6.

## B6 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_load_close_price_by_symbol` @ L98 | CURRENT_BLOB `4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**NEW TARGET (404 on actor and integration):** `scripts/diagnostics/m26_scorecard_close_projection.py::_load_close_price_by_symbol`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
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
**Exact SOURCE thin-wrapper executable statement:** `return _close_owner._load_close_price_by_symbol(path, day=day, facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `scripts.diagnostics.m26_scorecard_close_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade.csv/_utc_day/_safe_float; temp CSV only. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_b6_load_close_price_by_symbol`:** temp CSV 'symbol,ts,close\nA,1970-01-01T00:00:00Z,10\n', day='1970-01-01'→{'A':10.0}; missing→{}. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue B7.

## B7 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_build_parser` @ L125 | CURRENT_BLOB `4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**NEW TARGET (404 on actor and integration):** `scripts/diagnostics/m26_scorecard_parser_projection.py::_build_parser`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
```python
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="M26 scorecard scaffold (PnL proxy / risk-adjusted / drawdown).")
    p.add_argument("--dataset-root", default="data/eval/m26_fixed_dataset_v1")
    p.add_argument("--day", default=None)
    p.add_argument("--json", action="store_true")
    return p
```
**Exact SOURCE thin-wrapper executable statement:** `return _parser_owner._build_parser(facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `scripts.diagnostics.m26_scorecard_parser_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade.argparse; parser only, never main. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_b7_build_parser`:** parse_args(['--day','2026-10-31','--json'])→day='2026-10-31', json=True. Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue B8.

## B8 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_validate_required` @ L133 | CURRENT_BLOB `4d5bb75ee8a22ad506ceff962e69e53a15d88563`
**NEW TARGET (404 on actor and integration):** `scripts/diagnostics/m26_scorecard_validate_projection.py::_validate_required`.
**ORIGINAL EXECUTABLE CALCULATION BODY — MOVE, not KEEP or test-only (adapt global lookups through facade where noted):**
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
**Exact SOURCE thin-wrapper executable statement:** `return _validate_owner._validate_required(dataset_root, facade=sys.modules[__name__])` (keep original signature, annotations, and any docstring; import `scripts.diagnostics.m26_scorecard_validate_projection` under the shown `_..._owner` alias or inline in wrapper; remove ALL old calculation statements). **Caller/monkeypatch:** facade.REQUIRED_FILES/json; TemporaryDirectory only, no real dataset. Owner signature adds keyword-only `facade` only when needed; read SOURCE globals through facade at invocation, never import SOURCE. Preserve negative/error parity and side-effect-free fake boundary.
**Normal targeted test `test_b8_validate_required`:** empty temp root→'missing_required_files' in failures; create all facade.REQUIRED_FILES and valid manifest→([],[]). Assert original-golden == wrapper == direct Owner, AST SOURCE thin wrapper and patched SOURCE-global seam. **On blocker:** log exact path/function/error and continue all remaining tests, commit/push and remote re-fetch.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY; NOT PART OF THIS ORDER
All six are distinct, current actor/integration SOURCE bodies and unique absent target paths; not executable until C03 fresh issuance. Never count reserve as G1 or reuse previous completed work.

### R1 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/check_metrics_schema_v1.py::_is_dict` @ L21 | CURRENT_BLOB `586466c6162d818d1ae60644ec7dd0d988beef63`
**TARGET absent actor/integration:** `scripts/diagnostics/metrics_schema_dict_projection.py::_is_dict`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _is_dict(v: Any) -> bool:
    return isinstance(v, dict)
```
**Future isolated normal test:** {}→True; []→False. **Safety/seam:** pure isinstance; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

### R2 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/check_metrics_schema_v1.py::_is_list` @ L25 | CURRENT_BLOB `586466c6162d818d1ae60644ec7dd0d988beef63`
**TARGET absent actor/integration:** `scripts/diagnostics/metrics_schema_list_projection.py::_is_list`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _is_list(v: Any) -> bool:
    return isinstance(v, list)
```
**Future isolated normal test:** []→True; {}→False. **Safety/seam:** pure isinstance; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

### R3 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/check_metrics_schema_v1.py::_build_parser` @ L34 | CURRENT_BLOB `586466c6162d818d1ae60644ec7dd0d988beef63`
**TARGET absent actor/integration:** `scripts/diagnostics/metrics_schema_parser_projection.py::_build_parser`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate frozen metrics schema v1.")
    p.add_argument("--event-log-path", default="data/logs/events.jsonl")
    p.add_argument("--report-dir", default="reports/metrics")
    p.add_argument("--day", default=None)
    p.add_argument("--json", action="store_true")
    return p
```
**Future isolated normal test:** parse_args(['--day','2026-10-31'])→day='2026-10-31'. **Safety/seam:** facade.argparse, no main; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

### R4 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_ab_evaluation.py::_as_float` @ L18 | CURRENT_BLOB `864f845cd2e6644c134372745590ecafeabc70ee`
**TARGET absent actor/integration:** `scripts/diagnostics/m26_ab_float_projection.py::_as_float`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _as_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return float(default)
```
**Future isolated normal test:** '2.5'→2.5; ('bad',3.0)→3.0. **Safety/seam:** pure numeric; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

### R5 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_ab_evaluation.py::_json_path_get` @ L25 | CURRENT_BLOB `864f845cd2e6644c134372745590ecafeabc70ee`
**TARGET absent actor/integration:** `scripts/diagnostics/m26_ab_path_projection.py::_json_path_get`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _json_path_get(obj: Dict[str, Any], path: str, default: float = 0.0) -> float:
    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict):
            return float(default)
        cur = cur.get(part)
    return _as_float(cur, default)
```
**Future isolated normal test:** ({'a':{'b':2}},'a.b')→2.0; missing with default=3→3.0. **Safety/seam:** call-time facade._as_float; pure mapping; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

### R6 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_ab_evaluation.py::_build_parser` @ L50 | CURRENT_BLOB `864f845cd2e6644c134372745590ecafeabc70ee`
**TARGET absent actor/integration:** `scripts/diagnostics/m26_ab_parser_projection.py::_build_parser`. **ACTUAL BODY (DESIGN ONLY):**
```python
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="M26 A/B evaluation scaffold over scorecard outputs.")
    p.add_argument("--a-dataset-root", default="data/eval/m26_fixed_dataset_v1")
    p.add_argument("--b-dataset-root", default="data/eval/m26_fixed_dataset_v1")
    p.add_argument("--a-label", default="A")
    p.add_argument("--b-label", default="B")
    p.add_argument("--day", default="")
    p.add_argument("--json", action="store_true")
    return p
```
**Future isolated normal test:** parse_args(['--a-label','X','--json'])→a_label='X',json=True. **Safety/seam:** facade.argparse; no scorecard execution; fake/temp only, no main/effect. Fresh source/target/Owner/consumer recheck required before issue.

**G1/G2/G3:** This C03 document issue is supply only, not code implementation/test/integration or RF DONE. Source/target conflicts, operational effects, missing tests or push failures are individually BLOCKED, never silently PASS. C04/C05 retain their exclusive gates.
