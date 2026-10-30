# C02 — FAST-3 Claude A | ORDER A-20261031-03 | NEW 8 verified RF-035 BODY MOVEs

**Canonical preflight:** C03 observed integration HEAD ae4c73b35678885158f547c69d6e411bd9ef6e68; A remote HEAD 42240ee55417386f9553ba91f66e5630a88ff682. #11 6528880739 reports previous A-20261031-02 A1–A8 all remote moved and 32 scoped normal PASS. C03 checked new SOURCE blob `bfa1137b3219500c7934eff75bb010a9722e4d12` and reserve SOURCE blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` on A remote; active 3 and reserve 4 TARGET paths return 404 on A and integration. **Previous eight are REMOTE_DONE, never repeat.** RF-035 exclusive A Owner; B's RF-063/RF-065 paths disjoint. This C02 is the entire actor instruction; do NOT open D00, RF, queues, triage or choose tasks.

**Execution contract:** Pin canonical HEAD, this order blob, A remote HEAD, each SOURCE blob before changes. Execute **ALL A1–A8**, each independently; one blocker means record exact reason and continue next safe item. Move actual displayed computation BODY out of SOURCE into indicated new TARGET single Owner. SOURCE retains exact original public/private name, signature, annotations, docstring, exception/return and a thin delegate to target; no duplicate computation. Add `import sys` and module owner imports only if absent. TARGET may accept keyword-only `facade`, must never import SOURCE; resolve source module helpers/globals at **call time** through `facade=sys.modules[__name__]`, including monkeypatch seams. Shared target modules must be appended to, not overwritten. Capture pre-move fake golden outputs/errors, compare original vs wrapper vs target, including negative and monkeypatch behavior. Tests only with fake dictionaries, tmp_path, controlled datetime; no live network/LLM/order/Broker/Guard/Step5C/UEF/RunLab/production report paths/state/DB. Run `python -m py_compile` on each SOURCE/TARGET and the **new targeted normal test** exit0; if pytest absent, reproducible stdlib normal smoke with exact assertions/exit. Commit only code/test on `work/p15-a-reporter-pure-20261021`; normal push, refetch remote HEAD and SOURCE/TARGET/TEST blob, compare to local tree. If push fails, LOCAL_ONLY/PUSH_BLOCKED, continue other safe items; no force push. Report per item to #11. No -O/full peer/hosted CI requirement; C04/C05 own G3 and DONE. This document commit is NOT code G1/G2/G3.

## A1 — RF-035 | SOURCE `libs/reporting/report_source_helpers.py::read_json` (blob `bfa1137b3219500c7934eff75bb010a9722e4d12`, line 20) → TARGET `libs/reporting/report_source_read_projection.py::read_json` (new 404)

**Exact SOURCE computation BODY to MOVE (remove from SOURCE; retain only thin wrapper):**

```python
def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}
```

**Wrapper/caller/monkeypatch:** preserve original signature and all imports/callers; SOURCE delegates to `report_source_read_projection.read_json(..., facade=sys.modules[__name__])` using original positional/keyword semantics. facade.json.loads resolved at call time; read-only tmp_path; preserve broad except and dict-only result. Target contains calculation once, no import of SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_03h_a1_read_json_owner.py`. Golden input/expected: missing tmp path → {}; {'ok':1} JSON→same dict; [] JSON→{}; patch facade.json.loads raise→{}. Assert original/Owner/wrapper output and exception parity, facade monkeypatch at invocation, no real effects. `python -m py_compile libs/reporting/report_source_helpers.py libs/reporting/report_source_read_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_03h_a1_read_json_owner.py` exit0 (or exact stdlib smoke). Commit only code/new test, push A normally, re-fetch remote HEAD and three blobs; if blocked record exact blocker and **continue A2**.

## A2 — RF-035 | SOURCE `libs/reporting/report_source_helpers.py::to_epoch` (blob `bfa1137b3219500c7934eff75bb010a9722e4d12`, line 30) → TARGET `libs/reporting/report_source_clock_projection.py::to_epoch` (new 404)

**Exact SOURCE computation BODY to MOVE (remove from SOURCE; retain only thin wrapper):**

```python
def to_epoch(ts: Any) -> int:
    if ts is None:
        return 0
    if isinstance(ts, (int, float)):
        return int(ts)
    s = str(ts).strip()
    if not s:
        return 0
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
        return 0
```

**Wrapper/caller/monkeypatch:** preserve original signature and all imports/callers; SOURCE delegates to `report_source_clock_projection.to_epoch(..., facade=sys.modules[__name__])` using original positional/keyword semantics. facade.datetime.fromisoformat and facade.timezone.utc at call time; preserve int(float), invalid→0. Target contains calculation once, no import of SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_03h_a2_to_epoch_owner.py`. Golden input/expected: None→0, '1970-01-02T00:00:00Z'→86400, 'bad'→0, naive ISO UTC; patched facade.datetime/timezone observed. Assert original/Owner/wrapper output and exception parity, facade monkeypatch at invocation, no real effects. `python -m py_compile libs/reporting/report_source_helpers.py libs/reporting/report_source_clock_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_03h_a2_to_epoch_owner.py` exit0 (or exact stdlib smoke). Commit only code/new test, push A normally, re-fetch remote HEAD and three blobs; if blocked record exact blocker and **continue A3**.

## A3 — RF-035 | SOURCE `libs/reporting/report_source_helpers.py::utc_day` (blob `bfa1137b3219500c7934eff75bb010a9722e4d12`, line 53) → TARGET `libs/reporting/report_source_clock_projection.py::utc_day` (new 404)

**Exact SOURCE computation BODY to MOVE (remove from SOURCE; retain only thin wrapper):**

```python
def utc_day(ts: Any) -> str:
    epoch = to_epoch(ts)
    if epoch <= 0:
        return ""
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d")
```

**Wrapper/caller/monkeypatch:** preserve original signature and all imports/callers; SOURCE delegates to `report_source_clock_projection.utc_day(..., facade=sys.modules[__name__])` using original positional/keyword semantics. facade.to_epoch, facade.datetime.fromtimestamp and facade.timezone.utc at call time. Target contains calculation once, no import of SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_03h_a3_utc_day_owner.py`. Golden input/expected: facade.to_epoch patched 86400→'1970-01-02', 0→''; exception parity. Assert original/Owner/wrapper output and exception parity, facade monkeypatch at invocation, no real effects. `python -m py_compile libs/reporting/report_source_helpers.py libs/reporting/report_source_clock_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_03h_a3_utc_day_owner.py` exit0 (or exact stdlib smoke). Commit only code/new test, push A normally, re-fetch remote HEAD and three blobs; if blocked record exact blocker and **continue A4**.

## A4 — RF-035 | SOURCE `libs/reporting/report_source_helpers.py::utc_now_iso` (blob `bfa1137b3219500c7934eff75bb010a9722e4d12`, line 60) → TARGET `libs/reporting/report_source_clock_projection.py::utc_now_iso` (new 404)

**Exact SOURCE computation BODY to MOVE (remove from SOURCE; retain only thin wrapper):**

```python
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
```

**Wrapper/caller/monkeypatch:** preserve original signature and all imports/callers; SOURCE delegates to `report_source_clock_projection.utc_now_iso(..., facade=sys.modules[__name__])` using original positional/keyword semantics. facade.datetime.now and facade.timezone.utc at call time; no actual clock dependency in tests. Target contains calculation once, no import of SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_03h_a4_utc_now_iso_owner.py`. Golden input/expected: patch facade.datetime.now to 2026-10-31 03:00:00+00:00 → '2026-10-31T03:00:00+00:00'; seconds only. Assert original/Owner/wrapper output and exception parity, facade monkeypatch at invocation, no real effects. `python -m py_compile libs/reporting/report_source_helpers.py libs/reporting/report_source_clock_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_03h_a4_utc_now_iso_owner.py` exit0 (or exact stdlib smoke). Commit only code/new test, push A normally, re-fetch remote HEAD and three blobs; if blocked record exact blocker and **continue A5**.

## A5 — RF-035 | SOURCE `libs/reporting/report_source_helpers.py::epoch_to_iso` (blob `bfa1137b3219500c7934eff75bb010a9722e4d12`, line 64) → TARGET `libs/reporting/report_source_clock_projection.py::epoch_to_iso` (new 404)

**Exact SOURCE computation BODY to MOVE (remove from SOURCE; retain only thin wrapper):**

```python
def epoch_to_iso(epoch: Any) -> str:
    try:
        n = int(float(epoch))
    except Exception:
        return ""
    if n <= 0:
        return ""
    return datetime.fromtimestamp(n, tz=timezone.utc).isoformat(timespec="seconds")
```

**Wrapper/caller/monkeypatch:** preserve original signature and all imports/callers; SOURCE delegates to `report_source_clock_projection.epoch_to_iso(..., facade=sys.modules[__name__])` using original positional/keyword semantics. facade.datetime.fromtimestamp, facade.timezone.utc at call time; retain invalid→empty. Target contains calculation once, no import of SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_03h_a5_epoch_to_iso_owner.py`. Golden input/expected: 86400→'1970-01-02T00:00:00+00:00'; 'bad'/0/-1→''; fake facade.datetime parity. Assert original/Owner/wrapper output and exception parity, facade monkeypatch at invocation, no real effects. `python -m py_compile libs/reporting/report_source_helpers.py libs/reporting/report_source_clock_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_03h_a5_epoch_to_iso_owner.py` exit0 (or exact stdlib smoke). Commit only code/new test, push A normally, re-fetch remote HEAD and three blobs; if blocked record exact blocker and **continue A6**.

## A6 — RF-035 | SOURCE `libs/reporting/report_source_helpers.py::iter_jsonl` (blob `bfa1137b3219500c7934eff75bb010a9722e4d12`, line 74) → TARGET `libs/reporting/report_source_read_projection.py::iter_jsonl` (new 404)

**Exact SOURCE computation BODY to MOVE (remove from SOURCE; retain only thin wrapper):**

```python
def iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []

    def _gen() -> Iterable[Dict[str, Any]]:
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
                    yield obj

    return _gen()
```

**Wrapper/caller/monkeypatch:** preserve original signature and all imports/callers; SOURCE delegates to `report_source_read_projection.iter_jsonl(..., facade=sys.modules[__name__])` using original positional/keyword semantics. facade.json.loads inside nested generator at iteration time; no eager file open; preserve missing-list distinction. Target contains calculation once, no import of SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_03h_a6_iter_jsonl_owner.py`. Golden input/expected: missing→plain []; tmp file dict, list, malformed, dict→lazy iterator of 2 dicts in file order; patch facade.json.loads after generator creation and before iteration. Assert original/Owner/wrapper output and exception parity, facade monkeypatch at invocation, no real effects. `python -m py_compile libs/reporting/report_source_helpers.py libs/reporting/report_source_read_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_03h_a6_iter_jsonl_owner.py` exit0 (or exact stdlib smoke). Commit only code/new test, push A normally, re-fetch remote HEAD and three blobs; if blocked record exact blocker and **continue A7**.

## A7 — RF-035 | SOURCE `libs/reporting/report_source_helpers.py::_commander_route_from_payload` (blob `bfa1137b3219500c7934eff75bb010a9722e4d12`, line 153) → TARGET `libs/reporting/report_source_route_projection.py::_commander_route_from_payload` (new 404)

**Exact SOURCE computation BODY to MOVE (remove from SOURCE; retain only thin wrapper):**

```python
def _commander_route_from_payload(payload: Dict[str, Any], *, artifact_path: str = "") -> Dict[str, Any]:
    route_obs = payload.get("route_observability") if isinstance(payload.get("route_observability"), dict) else {}
    commander_decision = payload.get("commander_decision") if isinstance(payload.get("commander_decision"), dict) else {}
    route_selected = str(
        payload.get("route_selected")
        or payload.get("selected_route")
        or route_obs.get("route_selected")
        or commander_decision.get("route_selected")
        or ""
    ).strip()
    return {
        "route_selected": route_selected,
        "strategy_generation_mode": str(
            payload.get("strategy_generation_mode")
            or route_obs.get("strategy_generation_mode")
            or commander_decision.get("strategy_generation_mode")
            or ""
        ).strip(),
        "strategist_call_decision": str(
            payload.get("strategist_call_decision")
            or route_obs.get("strategist_call_decision")
            or commander_decision.get("strategist_call_decision")
            or ""
        ).strip(),
        "strategist_fallback_used": bool(
            payload.get("strategist_fallback_used")
            if payload.get("strategist_fallback_used") is not None
            else route_obs.get("fallback_used")
            if route_obs.get("fallback_used") is not None
            else commander_decision.get("strategist_fallback_used")
        ),
        "route_source": "canonical_commander" if artifact_path else "",
        "artifact_path": artifact_path,
    }
```

**Wrapper/caller/monkeypatch:** preserve original signature and all imports/callers; SOURCE delegates to `report_source_route_projection._commander_route_from_payload(..., facade=sys.modules[__name__])` using original positional/keyword semantics. pure payload mapping, exact fallback precedence/route_source; preserve input dict immutability. Target contains calculation once, no import of SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_03h_a7_commander_route_from_payload_owner.py`. Golden input/expected: payload {'route_selected':'direct','strategy_generation_mode':'shadow','fallback_used':True} via route_observability, artifact_path='fake.json' → route_source canonical_commander and fallback True; empty→all blank/False. Assert original/Owner/wrapper output and exception parity, facade monkeypatch at invocation, no real effects. `python -m py_compile libs/reporting/report_source_helpers.py libs/reporting/report_source_route_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_03h_a7_commander_route_from_payload_owner.py` exit0 (or exact stdlib smoke). Commit only code/new test, push A normally, re-fetch remote HEAD and three blobs; if blocked record exact blocker and **continue A8**.

## A8 — RF-035 | SOURCE `libs/reporting/report_source_helpers.py::_event_route_rows` (blob `bfa1137b3219500c7934eff75bb010a9722e4d12`, line 189) → TARGET `libs/reporting/report_source_route_projection.py::_event_route_rows` (new 404)

**Exact SOURCE computation BODY to MOVE (remove from SOURCE; retain only thin wrapper):**

```python
def _event_route_rows(day_rows: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    # OOM RCA follow-up (2026-09-23): folds directly off the iterator in
    # file/stream order instead of pre-sorting a materialized day_rows list
    # -- see _build_run_contexts's own comment in operator_visibility.py
    # for why file order is already chronological order in this system,
    # and why per-run same-stage-repeat re-ordering isn't a real concern.
    by_run: Dict[str, Dict[str, Any]] = {}
    for row in day_rows:
        run_id = str(row.get("run_id") or "").strip()
        if not run_id:
            continue
        stage = str(row.get("stage") or "").strip()
        event = str(row.get("event") or "").strip()
        route_event = stage == "commander_router" and event in {"route_selected", "end", "route"}
        policy_event = stage == "strategist" and event == "policy_resolution"
        if not (route_event or policy_event):
            continue
        payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
        current = by_run.setdefault(
            run_id,
            {
                "route_selected": "",
                "strategy_generation_mode": "",
                "strategist_call_decision": "",
                "strategist_fallback_used": False,
                "route_source": "event_fallback",
                "artifact_path": "",
            },
        )
        if route_event:
            merged = _commander_route_from_payload(payload)
            for key in ("route_selected", "strategy_generation_mode", "strategist_call_decision"):
                if merged.get(key):
                    current[key] = merged[key]
            if merged.get("strategist_fallback_used"):
                current["strategist_fallback_used"] = True
        if policy_event:
            mode = str(payload.get("strategy_generation_mode") or "").strip()
            if mode:
                current["strategy_generation_mode"] = mode
            if bool(payload.get("fallback_used")):
                current["strategist_fallback_used"] = True
    return by_run
```

**Wrapper/caller/monkeypatch:** preserve original signature and all imports/callers; SOURCE delegates to `report_source_route_projection._event_route_rows(..., facade=sys.modules[__name__])` using original positional/keyword semantics. facade._commander_route_from_payload at call time; iterator order and setdefault semantics unchanged. Target contains calculation once, no import of SOURCE.

**New normal targeted test:** `tests/test_p15_rf035_03h_a8_event_route_rows_owner.py`. Golden input/expected: rows: r1 commander_router route_selected direct + r1 strategist policy_resolution fallback_used True + empty run_id; expect one r1, selected direct, fallback True, event_fallback; patch facade._commander_route_from_payload and assert seam. Assert original/Owner/wrapper output and exception parity, facade monkeypatch at invocation, no real effects. `python -m py_compile libs/reporting/report_source_helpers.py libs/reporting/report_source_route_projection.py`; `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_03h_a8_event_route_rows_owner.py` exit0 (or exact stdlib smoke). Commit only code/new test, push A normally, re-fetch remote HEAD and three blobs; if blocked record exact blocker and **continue Afinal report**.

## RESERVE_VERIFIED — A 6/6 | design only, NOT part of A1–A8

These six are **not executable in this order**. C03 independently inspected `libs/reporting/symbol_trade_report.py` at A blob `099cdbd04c9fca68115413ce4d4d4b52c4653946`; each is a real unmoved body (not existing R-4 wrapper), RF-035 A Owner, no B overlap, target absent (404) on A/integration, read-only or pure. C03 must recheck remote HEAD and target existence before promoting any reserve in a later C02. Do not count as implemented or tested.

### R1 RF-035 | `libs/reporting/symbol_trade_report.py::_read_json` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` line 79 → `libs/reporting/symbol_trade_read_projection.py::_read_json` (404)

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

Thin original-signature facade wrapper; facade.json.loads; tmp only. Proposed new targeted normal fake/tmp fixture: missing→{}, dict→dict, list→{}, malformed→{}. Capture original vs target vs wrapper, monkeypatch parity, negative path, normal exit0; only when promoted to executable order. If blocked skip to next verified reserve.

### R2 RF-035 | `libs/reporting/symbol_trade_report.py::_iter_jsonl` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` line 89 → `libs/reporting/symbol_trade_read_projection.py::_iter_jsonl` (404)

```python
def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []

    def _gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if isinstance(row, dict):
                    yield row

    return _gen()
```

Thin original-signature facade wrapper; facade.json.loads in generator; no eager open. Proposed new targeted normal fake/tmp fixture: missing→[], fake file dict/list/bad→dict-only lazy sequence. Capture original vs target vs wrapper, monkeypatch parity, negative path, normal exit0; only when promoted to executable order. If blocked skip to next verified reserve.

### R3 RF-035 | `libs/reporting/symbol_trade_report.py::_contains_any` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` line 183 → `libs/reporting/symbol_trade_text_projection.py::_contains_any` (404)

```python
def _contains_any(text: str, needles: List[str]) -> bool:
    lowered = str(text or "").strip().lower()
    return any(needle in lowered for needle in needles)
```

Thin original-signature facade wrapper; pure str; no facade globals. Proposed new targeted normal fake/tmp fixture: ('AbC',['bc'])→True; ('', ['x'])→False; preserve case of needles as original. Capture original vs target vs wrapper, monkeypatch parity, negative path, normal exit0; only when promoted to executable order. If blocked skip to next verified reserve.

### R4 RF-035 | `libs/reporting/symbol_trade_report.py::_clean_symbol_code` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` line 196 → `libs/reporting/symbol_trade_text_projection.py::_clean_symbol_code` (404)

```python
def _clean_symbol_code(value: Any) -> str:
    text = str(value or "").strip()
    if text.lower() in {"", "unknown", "none", "null", "-"}:
        return ""
    return text
```

Thin original-signature facade wrapper; pure str; no global dependencies. Proposed new targeted normal fake/tmp fixture: ' unknown '→'', ' 005930 '→'005930'. Capture original vs target vs wrapper, monkeypatch parity, negative path, normal exit0; only when promoted to executable order. If blocked skip to next verified reserve.

### R5 RF-035 | `libs/reporting/symbol_trade_report.py::_ratio` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` line 437 → `libs/reporting/symbol_trade_scalar_projection.py::_ratio` (404)

```python
def _ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator
```

Thin original-signature facade wrapper; pure arithmetic; no state. Proposed new targeted normal fake/tmp fixture: (4,2)→2.0; (4,0)→0.0; negative denominator→0.0. Capture original vs target vs wrapper, monkeypatch parity, negative path, normal exit0; only when promoted to executable order. If blocked skip to next verified reserve.

### R6 RF-035 | `libs/reporting/symbol_trade_report.py::_summary_input_path_for_report` blob `099cdbd04c9fca68115413ce4d4d4b52c4653946` line 219 → `libs/reporting/symbol_trade_path_projection.py::_summary_input_path_for_report` (404)

```python
def _summary_input_path_for_report(report_path: Path) -> Path:
    return Path(report_path).with_name("ai_trade_summary_input.json")
```

Thin original-signature facade wrapper; facade.Path at call time, fake path only. Proposed new targeted normal fake/tmp fixture: Path('/tmp/a.md')→Path('/tmp/ai_trade_summary_input.json'); no mkdir/write. Capture original vs target vs wrapper, monkeypatch parity, negative path, normal exit0; only when promoted to executable order. If blocked skip to next verified reserve.

## Completion report to Issue #11

`ORDER_ID=A-20261031-03 | CANONICAL_HEAD | ORDER_BLOB_SHA | A_START_REMOTE_SHA | A1..A8 IMPLEMENTED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN | SOURCE_BLOBS_BEFORE_AFTER | TARGET_BLOBS | TEST_NORMAL_EXIT | REMOTE_PUSH_SHA | FIRST_BLOCKER | NEXT`. START_KST/END_KST/ELAPSED_MIN only if measured, no estimates. No docs/RF/STATUS/other actor branches changed. Reserves R1–R6 remain design-only.
