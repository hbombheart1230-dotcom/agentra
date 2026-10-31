# C01 — Codex B | B-20261101-03-CONT | FAST-3 7 REMAINING verified real SOURCE BODY MOVEs

**START ORDER — ONE FILE ONLY.** Read this C01 and ONLY named code/test paths. Pin actual integration HEAD, this C01 blob, actor remote HEAD and ORDER_ID at start. Do not read D00/RF/queue/C03/HANDOFF, choose your own work, or redo completed B1. Complete ALL seven remaining independent items B2–B8; if blocked, record exact reason and continue other safe items. This update does not retroactively cancel an order already in progress.

**C03 DELTA EVIDENCE:** previous C01 blob `c478e4901e2b2de1f81f48244c54b2d8d670e7a2`; B remote `30295cc1d492945a9b818bb1e8e1008cfad760a6` → `da1ec19b27aedefea64381ca88ba9c1d2c3fec20` (one commit, 3 files): B1 `run_m26_scorecard.py::_to_epoch` original body removed, `m26_scorecard_epoch_projection.py::_to_epoch` created, test `tests/test_p15_rf063_22h_projection_owners.py` added. B1 is **REMOTE_DONE (code structural only)** and MUST NOT be reassigned. The 7 below are still actual SOURCE BODY on B remote, their TARGETs are absent on B/integration. B source CURRENT_BLOB now `320abe9f61f75e4de06b46ee451aa878bbb79b62` (integration still older `4d5bb75ee8a22ad506ceff962e69e53a15d88563`). B1 new normal test evidence is only source/test presence; normal exit0 for B1 is NOT independently confirmed from #12 yet; do not count B1 as new G2. Previous B-02 order's other seven remain ready. #32 latest `6520075820`: RunLab Exited(255), RUN_SOURCE_SHA=UNKNOWN, operational HOLD.

**OWNER:** RF-063, CODEX_B exclusively. Actor writes ONLY its own `work/p15-b-operator-structure-20261022` code/test; no D00/RF/queue/STATUS/C04/C05, A branch, CI/frozen oracle, force-push. C03 does not write B code/tests. C04 handles selective integration/G3, C05 RF DONE.

**SAFETY:** isolated fake dicts/TemporaryDirectory and patched env/clock only. No real trading/broker/order/Guard/Step5C/UEF/RunLab/live network/runtime process or operational State/DB/report path; no actual CLI main, subprocess or deployment. Preserve public signature/return/exception/ordering and SOURCE post-import monkeypatch seams. Move ORIGINAL calculation to unique Owner, SOURCE becomes single-return thin wrapper, Owner never imports SOURCE (use facade=sys.modules[__name__] when needed). Golden preimage parity, AST source body removal, direct Owner and wrapper parity required.

**TEST/PUSH:** create NEW `tests/test_p15_rf063_20261101_03h_diagnostics_remaining_owners.py` with B2–B8 tests, keeping the B1 `test_p15_rf063_22h_projection_owners.py` unchanged. In the seven item sections below, the older referenced test names are method names; use this NEW 03h test file rather than the obsolete 02h proposed path. Run `python -m py_compile` on changed SOURCE and created Owners, then `python -m unittest tests/test_p15_rf063_20261101_03h_diagnostics_remaining_owners.py -v` normal exit0; optionally run B1's existing test for directly affected caller compatibility, not repeated as new work. Commit ONLY B code/new test, normal push actor branch, re-fetch remote HEAD and SOURCE/TARGET/test blobs. If Git auth fails, mark PUSH_BLOCKED and continue safe work. Report B2–B8 individual outcomes, normal exit, remote SHA and measured START/END to #12. No mandatory -O/full peer/hosted per-RF CI.

## B2 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_utc_day` @ L31 | CURRENT_BLOB `320abe9f61f75e4de06b46ee451aa878bbb79b62`
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

## B3 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_iter_jsonl` @ L38 | CURRENT_BLOB `320abe9f61f75e4de06b46ee451aa878bbb79b62`
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

## B4 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_safe_int` @ L56 | CURRENT_BLOB `320abe9f61f75e4de06b46ee451aa878bbb79b62`
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

## B5 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_safe_float` @ L63 | CURRENT_BLOB `320abe9f61f75e4de06b46ee451aa878bbb79b62`
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

## B6 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_load_close_price_by_symbol` @ L80 | CURRENT_BLOB `320abe9f61f75e4de06b46ee451aa878bbb79b62`
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

## B7 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_build_parser` @ L107 | CURRENT_BLOB `320abe9f61f75e4de06b46ee451aa878bbb79b62`
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

## B8 | RF-063 | CODEX_B | SOURCE `scripts/diagnostics/run_m26_scorecard.py::_validate_required` @ L115 | CURRENT_BLOB `320abe9f61f75e4de06b46ee451aa878bbb79b62`
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
