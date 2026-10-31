# C01 — Codex B | B-20261101-04-DELIVERY | FAST-3 7 REMOTE-PENDING BODY MOVEs (B2–B8)

**ONE-FILE START.** Pin integration HEAD, C01 blob, B remote HEAD and ORDER_ID. Read ONLY this C01 and named code/tests. No D00/RF/queue/C03/HANDOFF or self-selection. All seven B2–B8 are still REMOTE-PENDING; **DO NOT REIMPLEMENT ALREADY COMPLETED LOCAL BODY MOVEs** if the recorded local commit and working tree are intact. New order does not retroactively cancel a prior in-flight order.

**C03 NEW DELTA:** #12 `6547301271` confirms B2–B8 original calculation bodies already moved into seven unique Owners **LOCAL_ONLY** at local commit `4ca5ee9674faf524c763f171c4391da84a80abba`, targeted normal `python -m unittest tests/test_p15_rf063_20261101_03h_diagnostics_remaining_owners.py -v` **7 PASS, exit0**, py_compile exit0. But `git push origin work/p15-b-operator-structure-20261022` failed `fatal: could not read Username for 'https://github.com': No such device or address`. **B remote remains `da1ec19b27aedefea64381ca88ba9c1d2c3fec20`; remote SOURCE `scripts/diagnostics/run_m26_scorecard.py` blob `320abe9f61f75e4de06b46ee451aa878bbb79b62` still contains original B2–B8 BODY and all seven TARGET paths absent. LOCAL_ONLY is NOT REMOTE_DONE. B1 `_to_epoch` was already remote-moved; do not repeat B1. B1 separate normal G2 exit0 remains NOT_VERIFIED, do not infer from test presence.

**FIRST ACTION = DELIVERY, NOT REDUNDANT CODING.** In B's authorized development environment, inspect exact local commit `4ca5ee96`, verify it changes ONLY `scripts/diagnostics/run_m26_scorecard.py`, seven `scripts/diagnostics/m26_scorecard_{day,jsonl,int,float,close,parser,validate}_projection.py`, and new `tests/test_p15_rf063_20261101_03h_diagnostics_remaining_owners.py`; no markdown/HANDOFF/RF/STATUS/other-owner code. Confirm each source thin wrapper and Owner calculation, direct caller seam, and 7/7 normal test evidence at that commit. If intact, deliver **that same verified code/test tree** via normal non-force push after GitHub authentication recovery, or an approved B-actor GitHub exact-tree/create-commit/update-ref path with expected-head lease equal to `da1ec19b...` (never force/rewrite or overwrite intervening changes). Re-fetch remote B HEAD, SOURCE/TARGET/test Git blobs and verify exact parity with local commit. Only after REMOTE_PUSH_VERIFIED report B2–B8 REMOTE_DONE to #12. If B remote HEAD advanced, compare exact file/function diffs and safely reconcile, never blindly replace.

**IF DELIVERY STILL BLOCKED:** mark PUSH_BLOCKED with exact error, owner/credential unlock and resume SHA; do not claim remote completion or re-run identical SHA tests as new work. Independently fix only a demonstrated missing body/target/test defect, then continue remaining safe B2–B8 tasks below. A/B actor code changes belong ONLY on B `work/p15-b-operator-structure-20261022`; C03 never writes B code. C04 selective integration/G3 and C05 RF DONE/STATUS remain exclusive. RunLab #32 latest `6520075820`: Exited(255), RUN_SOURCE_SHA UNKNOWN; no runtime restart/real order/Guard/Step5C/UEF/State/Broker effects.

**SCOPE:** RF-063 CODEX_B. Fake in-memory dicts and TemporaryDirectory/patch env/clock only; no real dataset, network, live CLI/main, broker, order, operational state, frozen oracle or force push. The seven sections below preserve the complete original SOURCE BODY, exact target, thin wrapper, monkeypatch seam, and targeted expected results. Keep B1 existing test intact; do not overwrite any previous test. Existing B2–B8 normal test exit0 is evidence for local commit only, not permission to omit remote delivery. On actual code change, run scoped normal stdlib unittest exit0 once. No mandatory -O/full peer/per-RF hosted CI.

**REPORT:** to #12: `ORDER_ID | CANONICAL_HEAD | ORDER_BLOB | B_REMOTE_BEFORE→AFTER | LOCAL_SHA | B2..B8 LOCAL_DONE/REMOTE_DONE | NORMAL_EXIT | PUSH_ERROR/REMOTE_BLOBS | FIRST_BLOCKER | NEXT | measured START/END`. If all seven are delivered, report all seven as REMOTE_DONE, then wait for C03 next verified order; no redundant same-SHA work. Six future reserve items below are DESIGN ONLY and are NOT part of this order.

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
