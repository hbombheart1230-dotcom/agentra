# C02 — Claude A | A-20261031-13 | FAST-3 SINGLE EXECUTION ORDER

**PIN AT START:** CANONICAL_INPUT_HEAD=`4fe7ffc36e8587a1ebad97aa7ea774fee5f76d7a`; ORDER_FILE_BLOB_SHA=fetch this document from `integration/p1.5`; A_REMOTE_HEAD_AT_DESIGN=`d20d9252bd50c1dd284d0563536835a543d6b184`. Previous A-20261031-12 C02 blob=`837b7a680b658e4da246fe42eb070a2cc5e3be7f` is **8/8 REMOTE_DONE** at exact A remote `d20d9252bd50c1dd284d0563536835a543d6b184` (#11 comment 6538289132), confirmed by actual SOURCE wrapper and new TARGET modules, not test-only. No replay of 12h bodies. This C02 is the ONLY execution contract; do not read D00, RF, queue, C03, handoffs or select tasks.

**EIGHT NEW VERIFIED SOURCE BODY MOVES:** RF-035, exclusive Claude A reporting Owner, source `libs/reporting/q8_shadow_blocker_review.py` remote blob `7e482261ae1da4824112d8d2fea0b7c6a3aab9c6`, exact same at integration. These eight top-level functions retain their original calculation BODY on A remote (not previously moved). New Owner targets listed below were individually verified 404 at A remote; all targets are under `libs/reporting/`, no B RF-063 collision. Execute A1–A8 independently or mark item-specific BLOCKED; a partial pass/push failure never stops remaining safe items. At start re-fetch source and target: if already moved, REMOTE_DONE (not new); if changed unexpectedly, STALE/BLOCKED and continue others. Do not retroactively invalidate any Actor start-pinned order.

**Single-Owner mechanics:** Move actual BODY into target exactly once; retain same SOURCE signature/defaults/annotations and only a thin delegate wrapper. Import target as module alias; no target→source import. If body references facade globals, add keyword-only `facade` to Owner and resolve at call time via `facade.NAME`; SOURCE wrapper passes `sys.modules[__name__]` (add `import sys` only if needed), preserving monkeypatch after import. For pure functions, no facade needed. Keep output ordering, exception timing/types, generator semantics, original public import path, caller and test patch seam. Target modules use `from __future__ import annotations` and required typing imports; do not copy a second implementation into SOURCE.

**Safety/Gates:** Evaluation-only, fake in-memory fixtures or tmp_path, no real report/state reads or writes, no live network, trading/order/Broker/Guard/Step5C/UEF/RunLab effects, frozen oracle, CI, deployment or force-push. RF-035 G1 remote owner code + G2 one normal targeted exit0; C04/C05 exclusively handle G3 and RF DONE. No mandatory -O/full peer/full CI. Actor may modify only own code/tests and push own branch; never docs/CSV/RF/STATUS. Every item includes next safe item on BLOCKED.

## A1 | RF-035 | libs/reporting/q8_shadow_blocker_review.py::_text @ L31 | SOURCE_BLOB=7e482261ae1da4824112d8d2fea0b7c6a3aab9c6

**TARGET (new exclusive Owner; absent at A HEAD):** `libs/reporting/q8_shadow_blocker_scalar_projection.py::_text`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (pure string normalization):

```python
def _text(value: Any) -> str:
    return str(value or "").strip()
```

**Thin wrapper / callers / monkeypatch:** Keep SOURCE `_text` signature and public import/patch seam; move above BODY to `q8_shadow_blocker_scalar_projection._text`, never duplicate computation. None; no facade needed. Compare original baseline function, new Owner and SOURCE wrapper for exact result, exception, ordering and patch parity; owner must not import facade/source. No production effect; tests use fake in-memory payloads only.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_13h_a1_text_owner.py`. Explicit input→expected: `None → ''`, `' A ' → 'A'`. Include negative fixture and facade monkeypatch when globals used. Run `python -m py_compile libs/reporting/q8_shadow_blocker_review.py libs/reporting/q8_shadow_blocker_scalar_projection.py`, then `python -m unittest tests/test_p15_rf035_13h_a1_text_owner.py -v` (or equivalent targeted pytest) and record actual exit0. Commit only A-owned code/tests, normal push, re-fetch remote SOURCE/TARGET/test blobs and A HEAD; no local-only G1. If blocked, record exact reason and continue **A2**.

## A2 | RF-035 | libs/reporting/q8_shadow_blocker_review.py::_to_float @ L35 | SOURCE_BLOB=7e482261ae1da4824112d8d2fea0b7c6a3aab9c6

**TARGET (new exclusive Owner; absent at A HEAD):** `libs/reporting/q8_shadow_blocker_scalar_projection.py::_to_float`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (pure numeric normalization):

```python
def _to_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None
```

**Thin wrapper / callers / monkeypatch:** Keep SOURCE `_to_float` signature and public import/patch seam; move above BODY to `q8_shadow_blocker_scalar_projection._to_float`, never duplicate computation. None; preserve float conversion and exception catch. Compare original baseline function, new Owner and SOURCE wrapper for exact result, exception, ordering and patch parity; owner must not import facade/source. No production effect; tests use fake in-memory payloads only.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_13h_a2_to_float_owner.py`. Explicit input→expected: `'2.5' → 2.5`, `None → None`, `'bad' → None`. Include negative fixture and facade monkeypatch when globals used. Run `python -m py_compile libs/reporting/q8_shadow_blocker_review.py libs/reporting/q8_shadow_blocker_scalar_projection.py`, then `python -m unittest tests/test_p15_rf035_13h_a2_to_float_owner.py -v` (or equivalent targeted pytest) and record actual exit0. Commit only A-owned code/tests, normal push, re-fetch remote SOURCE/TARGET/test blobs and A HEAD; no local-only G1. If blocked, record exact reason and continue **A3**.

## A3 | RF-035 | libs/reporting/q8_shadow_blocker_review.py::_bool @ L44 | SOURCE_BLOB=7e482261ae1da4824112d8d2fea0b7c6a3aab9c6

**TARGET (new exclusive Owner; absent at A HEAD):** `libs/reporting/q8_shadow_blocker_scalar_projection.py::_bool`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (pure truth parsing):

```python
def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}
```

**Thin wrapper / callers / monkeypatch:** Keep SOURCE `_bool` signature and public import/patch seam; move above BODY to `q8_shadow_blocker_scalar_projection._bool`, never duplicate computation. None. Compare original baseline function, new Owner and SOURCE wrapper for exact result, exception, ordering and patch parity; owner must not import facade/source. No production effect; tests use fake in-memory payloads only.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_13h_a3_bool_owner.py`. Explicit input→expected: `'yes' → True`, `'off' → False`, `0 → False`. Include negative fixture and facade monkeypatch when globals used. Run `python -m py_compile libs/reporting/q8_shadow_blocker_review.py libs/reporting/q8_shadow_blocker_scalar_projection.py`, then `python -m unittest tests/test_p15_rf035_13h_a3_bool_owner.py -v` (or equivalent targeted pytest) and record actual exit0. Commit only A-owned code/tests, normal push, re-fetch remote SOURCE/TARGET/test blobs and A HEAD; no local-only G1. If blocked, record exact reason and continue **A4**.

## A4 | RF-035 | libs/reporting/q8_shadow_blocker_review.py::_candidate_rows @ L52 | SOURCE_BLOB=7e482261ae1da4824112d8d2fea0b7c6a3aab9c6

**TARGET (new exclusive Owner; absent at A HEAD):** `libs/reporting/q8_shadow_blocker_candidate_projection.py::_candidate_rows`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (read-only candidate row projection):

```python
def _candidate_rows(payloads: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for payload in payloads:
        if not isinstance(payload, Mapping):
            continue
        for raw in list(payload.get("candidates") or []):
            if not isinstance(raw, Mapping):
                continue
            row = dict(raw)
            row.setdefault("_payload_generated_at", payload.get("generated_at"))
            rows.append(row)
    return rows
```

**Thin wrapper / callers / monkeypatch:** Keep SOURCE `_candidate_rows` signature and public import/patch seam; move above BODY to `q8_shadow_blocker_candidate_projection._candidate_rows`, never duplicate computation. `Mapping` resolved through call-time facade; preserve iteration order and input non-mutation. Compare original baseline function, new Owner and SOURCE wrapper for exact result, exception, ordering and patch parity; owner must not import facade/source. No production effect; tests use fake in-memory payloads only.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_13h_a4_candidate_rows_owner.py`. Explicit input→expected: `[{'generated_at':'t','candidates':[{'symbol':'A'}]}] → [{'symbol':'A','_payload_generated_at':'t'}]`; non-mapping payload skipped. Include negative fixture and facade monkeypatch when globals used. Run `python -m py_compile libs/reporting/q8_shadow_blocker_review.py libs/reporting/q8_shadow_blocker_candidate_projection.py`, then `python -m unittest tests/test_p15_rf035_13h_a4_candidate_rows_owner.py -v` (or equivalent targeted pytest) and record actual exit0. Commit only A-owned code/tests, normal push, re-fetch remote SOURCE/TARGET/test blobs and A HEAD; no local-only G1. If blocked, record exact reason and continue **A5**.

## A5 | RF-035 | libs/reporting/q8_shadow_blocker_review.py::_checkpoint_values @ L70 | SOURCE_BLOB=7e482261ae1da4824112d8d2fea0b7c6a3aab9c6

**TARGET (new exclusive Owner; absent at A HEAD):** `libs/reporting/q8_shadow_blocker_checkpoint_projection.py::_checkpoint_values`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (pure checkpoint outcome aggregation):

```python
def _checkpoint_values(outcome: Mapping[str, Any]) -> Dict[str, Any]:
    checkpoints = outcome.get("checkpoints") if isinstance(outcome.get("checkpoints"), Mapping) else {}
    observed: List[Mapping[str, Any]] = [
        checkpoint
        for checkpoint in checkpoints.values()
        if isinstance(checkpoint, Mapping) and str(checkpoint.get("status") or "") == "observed"
    ]
    if not observed:
        return {"available": False}
    returns = [_to_float(row.get("return_pct")) for row in observed]
    mfes = [_to_float(row.get("mfe_pct")) for row in observed]
    maes = [_to_float(row.get("mae_pct")) for row in observed]
    returns = [value for value in returns if value is not None]
    mfes = [value for value in mfes if value is not None]
    maes = [value for value in maes if value is not None]
    latest = returns[-1] if returns else None
    return {
        "available": True,
        "latest_return_pct": latest,
        "max_favorable_pct": max(mfes) if mfes else None,
        "max_adverse_pct": min(maes) if maes else None,
    }
```

**Thin wrapper / callers / monkeypatch:** Keep SOURCE `_checkpoint_values` signature and public import/patch seam; move above BODY to `q8_shadow_blocker_checkpoint_projection._checkpoint_values`, never duplicate computation. `Mapping`, `_to_float` through call-time facade; preserve last observed ordering. Compare original baseline function, new Owner and SOURCE wrapper for exact result, exception, ordering and patch parity; owner must not import facade/source. No production effect; tests use fake in-memory payloads only.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_13h_a5_checkpoint_values_owner.py`. Explicit input→expected: `{'checkpoints':{'5m':{'status':'observed','return_pct':'1.2','mfe_pct':'2.0','mae_pct':'-0.5'}}} → available=True, latest_return_pct=1.2, max_favorable_pct=2.0, max_adverse_pct=-0.5`; no observed → `{'available':False}`. Include negative fixture and facade monkeypatch when globals used. Run `python -m py_compile libs/reporting/q8_shadow_blocker_review.py libs/reporting/q8_shadow_blocker_checkpoint_projection.py`, then `python -m unittest tests/test_p15_rf035_13h_a5_checkpoint_values_owner.py -v` (or equivalent targeted pytest) and record actual exit0. Commit only A-owned code/tests, normal push, re-fetch remote SOURCE/TARGET/test blobs and A HEAD; no local-only G1. If blocked, record exact reason and continue **A6**.

## A6 | RF-035 | libs/reporting/q8_shadow_blocker_review.py::_avg @ L94 | SOURCE_BLOB=7e482261ae1da4824112d8d2fea0b7c6a3aab9c6

**TARGET (new exclusive Owner; absent at A HEAD):** `libs/reporting/q8_shadow_blocker_scalar_projection.py::_avg`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (pure average/rounding):

```python
def _avg(values: Sequence[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0
```

**Thin wrapper / callers / monkeypatch:** Keep SOURCE `_avg` signature and public import/patch seam; move above BODY to `q8_shadow_blocker_scalar_projection._avg`, never duplicate computation. None. Compare original baseline function, new Owner and SOURCE wrapper for exact result, exception, ordering and patch parity; owner must not import facade/source. No production effect; tests use fake in-memory payloads only.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_13h_a6_avg_owner.py`. Explicit input→expected: `[] → 0.0`, `[1.0,2.0] → 1.5`. Include negative fixture and facade monkeypatch when globals used. Run `python -m py_compile libs/reporting/q8_shadow_blocker_review.py libs/reporting/q8_shadow_blocker_scalar_projection.py`, then `python -m unittest tests/test_p15_rf035_13h_a6_avg_owner.py -v` (or equivalent targeted pytest) and record actual exit0. Commit only A-owned code/tests, normal push, re-fetch remote SOURCE/TARGET/test blobs and A HEAD; no local-only G1. If blocked, record exact reason and continue **A7**.

## A7 | RF-035 | libs/reporting/q8_shadow_blocker_review.py::_decision_for_row @ L98 | SOURCE_BLOB=7e482261ae1da4824112d8d2fea0b7c6a3aab9c6

**TARGET (new exclusive Owner; absent at A HEAD):** `libs/reporting/q8_shadow_blocker_decision_projection.py::_decision_for_row`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (read-only diagnostic label):

```python
def _decision_for_row(row: Mapping[str, Any]) -> str:
    reason = _text(row.get("reason"))
    if reason == "volume_confirmation_missing":
        return "retain_under_observation"
    if reason in {"breakout_not_ready", "pullback_not_mature"}:
        return "adjust_and_retest"
    if reason == "human_chart_sanity_guard_blocked":
        return "promotion_review_target"
    return "retain_under_observation"
```

**Thin wrapper / callers / monkeypatch:** Keep SOURCE `_decision_for_row` signature and public import/patch seam; move above BODY to `q8_shadow_blocker_decision_projection._decision_for_row`, never duplicate computation. `_text` via call-time facade; decision remains diagnostic-only, no policy application. Compare original baseline function, new Owner and SOURCE wrapper for exact result, exception, ordering and patch parity; owner must not import facade/source. No production effect; tests use fake in-memory payloads only.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_13h_a7_decision_for_row_owner.py`. Explicit input→expected: `{'reason':'breakout_not_ready'} → 'adjust_and_retest'`, `{'reason':'volume_confirmation_missing'} → 'retain_under_observation'`. Include negative fixture and facade monkeypatch when globals used. Run `python -m py_compile libs/reporting/q8_shadow_blocker_review.py libs/reporting/q8_shadow_blocker_decision_projection.py`, then `python -m unittest tests/test_p15_rf035_13h_a7_decision_for_row_owner.py -v` (or equivalent targeted pytest) and record actual exit0. Commit only A-owned code/tests, normal push, re-fetch remote SOURCE/TARGET/test blobs and A HEAD; no local-only G1. If blocked, record exact reason and continue **A8**.

## A8 | RF-035 | libs/reporting/q8_shadow_blocker_review.py::_summarize_group @ L109 | SOURCE_BLOB=7e482261ae1da4824112d8d2fea0b7c6a3aab9c6

**TARGET (new exclusive Owner; absent at A HEAD):** `libs/reporting/q8_shadow_blocker_group_projection.py::_summarize_group`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (pure report grouping; no trading policy change):

```python
def _summarize_group(
    reason: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    promotion_allowed: bool,
) -> Dict[str, Any]:
    observed_rows: List[Dict[str, Any]] = []
    for row in rows:
        outcome = row.get("shadow_forward_outcome") if isinstance(row.get("shadow_forward_outcome"), Mapping) else {}
        values = _checkpoint_values(outcome)
        if values.get("available"):
            observed_rows.append({**dict(row), "_q8_forward": values})
    latest_returns = [
        float(row["_q8_forward"]["latest_return_pct"])
        for row in observed_rows
        if row["_q8_forward"].get("latest_return_pct") is not None
    ]
    mfes = [
        float(row["_q8_forward"]["max_favorable_pct"])
        for row in observed_rows
        if row["_q8_forward"].get("max_favorable_pct") is not None
    ]
    maes = [
        float(row["_q8_forward"]["max_adverse_pct"])
        for row in observed_rows
        if row["_q8_forward"].get("max_adverse_pct") is not None
    ]
    positive_count = sum(1 for value in latest_returns if value > 0)
    missed_opportunity_count = sum(1 for value in mfes if value >= 1.0)
    adverse_count = sum(1 for value in maes if value <= -0.5)
    examples = sorted(
        observed_rows,
        key=lambda row: float(row["_q8_forward"].get("max_favorable_pct") or 0.0),
        reverse=True,
    )[:5]
    raw_decision = _decision_for_row(rows[0]) if rows else "retain_under_observation"
    decision = raw_decision if promotion_allowed else "retain_under_observation"
    return {
        "reason": reason,
        "candidate_count": len(rows),
        "observed_count": len(observed_rows),
        "coverage": round(float(len(observed_rows)) / float(len(rows)), 4) if rows else 0.0,
        "avg_latest_return_pct": _avg(latest_returns),
        "avg_max_favorable_pct": _avg(mfes),
        "avg_max_adverse_pct": _avg(maes),
        "positive_latest_count": positive_count,
        "positive_latest_rate": round(float(positive_count) / float(len(latest_returns)), 4) if latest_returns else 0.0,
        "missed_opportunity_count": missed_opportunity_count,
        "missed_opportunity_rate": round(float(missed_opportunity_count) / float(len(mfes)), 4) if mfes else 0.0,
        "adverse_count": adverse_count,
        "adverse_rate": round(float(adverse_count) / float(len(maes)), 4) if maes else 0.0,
        "raw_decision": raw_decision,
        "decision": decision,
        "decision_blocked_by_trust_gate": bool(raw_decision != decision),
        "examples": [
            {
                "symbol": _text(row.get("symbol")),
                "role": _text(row.get("shadow_role")),
                "rank": row.get("rank"),
                "tactic_id": _text(row.get("quant_tactic_id")),
                "latest_return_pct": row["_q8_forward"].get("latest_return_pct"),
                "max_favorable_pct": row["_q8_forward"].get("max_favorable_pct"),
                "max_adverse_pct": row["_q8_forward"].get("max_adverse_pct"),
            }
            for row in examples
        ],
    }
```

**Thin wrapper / callers / monkeypatch:** Keep SOURCE `_summarize_group` signature and public import/patch seam; move above BODY to `q8_shadow_blocker_group_projection._summarize_group`, never duplicate computation. `_checkpoint_values`, `_avg`, `_decision_for_row`, `_text` via call-time facade; preserve stable example sort and rate rounding. Compare original baseline function, new Owner and SOURCE wrapper for exact result, exception, ordering and patch parity; owner must not import facade/source. No production effect; tests use fake in-memory payloads only.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_13h_a8_summarize_group_owner.py`. Explicit input→expected: one fake `breakout_not_ready` row with observed 5m return=1.0, mfe=2.0, mae=-0.6 and `promotion_allowed=True` → candidate_count=1, observed_count=1, coverage=1.0, decision='adjust_and_retest'; same row with False → decision='retain_under_observation'; empty rows → candidate_count=0. Include negative fixture and facade monkeypatch when globals used. Run `python -m py_compile libs/reporting/q8_shadow_blocker_review.py libs/reporting/q8_shadow_blocker_group_projection.py`, then `python -m unittest tests/test_p15_rf035_13h_a8_summarize_group_owner.py -v` (or equivalent targeted pytest) and record actual exit0. Commit only A-owned code/tests, normal push, re-fetch remote SOURCE/TARGET/test blobs and A HEAD; no local-only G1. If blocked, record exact reason and continue **report all items**.

## SIX VERIFIED FUTURE RESERVES — DESIGN ONLY, NOT EXECUTABLE THIS ORDER

Revalidated at A remote `d20d9252bd50c1dd284d0563536835a543d6b184` and current integration: SOURCE_BLOB still `362d3ce13c7d5b48eb02b40274115345a2d7dddd`; all five specified controlled_lane_* target modules remain 404. Six reserve items are design-verified only, NOT current executable work. No implementation or test PASS is claimed.

All 6 candidate bodies below were read directly from A remote `work/p15-a-reporter-pure-20261021` at SOURCE_BLOB=`362d3ce13c7d5b48eb02b40274115345a2d7dddd`; each TARGET file was checked absent on A remote (and separate from current A1–A8 and B RF-063). RF-035 source file is A-owned reporting/mock evidence code. These are **design-verified** not implemented, tested, pushed or G1/G2; A must not execute them until C03 issues a new C02 order. A/B source/target overlap 0.

### R1 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/controlled_mock_lane_report.py::_deep_first @ L31 | SOURCE_BLOB=362d3ce13c7d5b48eb02b40274115345a2d7dddd

**TARGET (new exclusive A reporting Owner, absent on A remote):** `libs/reporting/controlled_lane_lookup_projection.py::_deep_first`. **ACTUAL UNMOVED SOURCE BODY (design evidence, NOT executable now):**

```python
def _deep_first(value: Any, *keys: str) -> str:
    if isinstance(value, Mapping):
        for key in keys:
            if _text(value.get(key)):
                return _text(value.get(key))
        for child in value.values():
            found = _deep_first(child, *keys)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _deep_first(child, *keys)
            if found:
                return found
    return ""
```

**Safety/owner/wrapper:** RF-035 A-only report/mock evidence projection. When promoted, SOURCE must retain exact signature as thin wrapper; target owns one BODY, no reverse import; use-time `facade` for source globals and monkeypatch parity. No live Broker/Guard/Step5C/UEF, real State, orders, network, operational RunLab or deploy. `_ledger_row` and report builder may read only fixture files under `tmp_path`; never touch real paths. **Targeted normal G2 hypothesis (NOT RUN):** fake {'outer':[{'order_id':'007'}]} with key order_id -> '007'; no key -> ''. Compare original baseline/owner/wrapper outputs and exceptions, negative case and monkeypatch seam; new targeted unittest normal exit0 and remote push only after promotion. If A source blob changes or target appears, revalidate before assigning.

### R2 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/controlled_mock_lane_report.py::_position_strategy @ L48 | SOURCE_BLOB=362d3ce13c7d5b48eb02b40274115345a2d7dddd

**TARGET (new exclusive A reporting Owner, absent on A remote):** `libs/reporting/controlled_lane_lookup_projection.py::_position_strategy`. **ACTUAL UNMOVED SOURCE BODY (design evidence, NOT executable now):**

```python
def _position_strategy(state: Mapping[str, Any], symbol: str) -> dict[str, Any]:
    persisted = _mapping(state.get("persisted_state"))
    contexts = _mapping(persisted.get("position_strategy_context"))
    row = _mapping(contexts.get(symbol))
    return _mapping(row.get("output"))
```

**Safety/owner/wrapper:** RF-035 A-only report/mock evidence projection. When promoted, SOURCE must retain exact signature as thin wrapper; target owns one BODY, no reverse import; use-time `facade` for source globals and monkeypatch parity. No live Broker/Guard/Step5C/UEF, real State, orders, network, operational RunLab or deploy. `_ledger_row` and report builder may read only fixture files under `tmp_path`; never touch real paths. **Targeted normal G2 hypothesis (NOT RUN):** fake persisted_state.position_strategy_context.A.output={'controlled_mock_lane':True} -> same mapping; missing symbol -> {}. Compare original baseline/owner/wrapper outputs and exceptions, negative case and monkeypatch seam; new targeted unittest normal exit0 and remote push only after promotion. If A source blob changes or target appears, revalidate before assigning.

### R3 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/controlled_mock_lane_report.py::_ledger_row @ L65 | SOURCE_BLOB=362d3ce13c7d5b48eb02b40274115345a2d7dddd

**TARGET (new exclusive A reporting Owner, absent on A remote):** `libs/reporting/controlled_lane_ledger_projection.py::_ledger_row`. **ACTUAL UNMOVED SOURCE BODY (design evidence, NOT executable now):**

```python
def _ledger_row(
    *, root: Path, day: str, symbol: str, order_id: str = "", run_id: str = ""
) -> dict[str, Any]:
    path = root / "data" / "logs" / "controlled_mock_lanes" / day / "lane_submissions.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    rows = payload.get("submissions") if isinstance(payload, Mapping) else []
    symbol_matches = [
        dict(row) for row in list(rows or [])
        if isinstance(row, Mapping) and _text(row.get("symbol")) == symbol
    ]
    if order_id:
        exact = [row for row in symbol_matches if _text(row.get("order_id")).lstrip("0") == order_id.lstrip("0")]
        if exact:
            return exact[-1]
    if run_id:
        exact = [row for row in symbol_matches if _text(row.get("run_id")) == run_id]
        if exact:
            return exact[-1]
    return {}
```

**Safety/owner/wrapper:** RF-035 A-only report/mock evidence projection. When promoted, SOURCE must retain exact signature as thin wrapper; target owns one BODY, no reverse import; use-time `facade` for source globals and monkeypatch parity. No live Broker/Guard/Step5C/UEF, real State, orders, network, operational RunLab or deploy. `_ledger_row` and report builder may read only fixture files under `tmp_path`; never touch real paths. **Targeted normal G2 hypothesis (NOT RUN):** tmp root/data/logs/controlled_mock_lanes/2026-10-31/lane_submissions.json with symbol=A, order_id='0012' -> last exact normalized order row for '12'; malformed JSON -> {}. Compare original baseline/owner/wrapper outputs and exceptions, negative case and monkeypatch seam; new targeted unittest normal exit0 and remote push only after promotion. If A source blob changes or target appears, revalidate before assigning.

### R4 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/controlled_mock_lane_report.py::build_controlled_lane_report_surface @ L89 | SOURCE_BLOB=362d3ce13c7d5b48eb02b40274115345a2d7dddd

**TARGET (new exclusive A reporting Owner, absent on A remote):** `libs/reporting/controlled_lane_surface_build_projection.py::build_controlled_lane_report_surface`. **ACTUAL UNMOVED SOURCE BODY (design evidence, NOT executable now):**

```python
def build_controlled_lane_report_surface(
    state: Mapping[str, Any], *, day: str = "", root: Path | str | None = None,
    prior_entry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Recover controlled-lane entry evidence without same-symbol guessing."""
    execution = _mapping(state.get("execution"))
    order = _mapping(execution.get("order"))
    meta = _mapping(order.get("meta"))
    prior = _mapping(prior_entry)
    lane = _first_mapping(meta.get("controlled_mock_lane"), prior.get("controlled_mock_lane"))
    symbol = _text(order.get("symbol") or execution.get("symbol") or prior.get("symbol") or state.get("symbol"))
    strategy = _first_mapping(meta.get("position_strategy_snapshot"), prior.get("position_strategy_snapshot"))
    if not strategy and symbol:
        strategy = _position_strategy(state, symbol)
    if not lane and day and root is not None and symbol:
        order_id = _deep_first(prior, "order_id", "ord_no")
        entry_run_id = _text(prior.get("run_id"))
        lane = _ledger_row(root=Path(root), day=day, symbol=symbol, order_id=order_id, run_id=entry_run_id)
        if lane and not strategy:
            strategy = _fixed_lane_strategy()
    if not lane or not strategy.get("controlled_mock_lane"):
        return {}
    lane_id = _text(lane.get("lane_id"))
    return {
        "schema_version": "controlled_mock_lane_report.v2",
        "lane_id": lane_id,
        "lane_label": LANE_LABELS.get(lane_id, lane_id),
        "symbol": _text(lane.get("symbol") or symbol),
        "signal_id": _text(lane.get("signal_id")),
        "signal_epoch": lane.get("signal_epoch"),
        "entry_run_id": _text(lane.get("run_id") or prior.get("run_id")),
        "entry_order_id": _text(lane.get("order_id") or _deep_first(prior, "order_id", "ord_no")),
        "score": lane.get("score"),
        "evidence": _mapping(lane.get("evidence")),
        "daily_limit": lane.get("daily_limit"),
        "reservation": _mapping(lane.get("reservation")),
        "strategy_horizon": _text(strategy.get("strategy_horizon")),
        "expected_hold_window": _mapping(strategy.get("expected_hold_window")),
        "llm_used": bool(strategy.get("llm_used")),
        "stage3_horizon_review_allowed": bool(strategy.get("horizon_revision_allowed", True)),
        "selection_authority": "deterministic_independent_lane",
        "scanner_rank_applicable": False,
        "execution_scope": "kiwoom_mock_only",
    }
```

**Safety/owner/wrapper:** RF-035 A-only report/mock evidence projection. When promoted, SOURCE must retain exact signature as thin wrapper; target owns one BODY, no reverse import; use-time `facade` for source globals and monkeypatch parity. No live Broker/Guard/Step5C/UEF, real State, orders, network, operational RunLab or deploy. `_ledger_row` and report builder may read only fixture files under `tmp_path`; never touch real paths. **Targeted normal G2 hypothesis (NOT RUN):** fake state.execution.order.meta.controlled_mock_lane and position_strategy_snapshot with controlled_mock_lane=True -> schema_version='controlled_mock_lane_report.v2', execution_scope='kiwoom_mock_only'; missing lane -> {}. Use only fake root and no broker.. Compare original baseline/owner/wrapper outputs and exceptions, negative case and monkeypatch seam; new targeted unittest normal exit0 and remote push only after promotion. If A source blob changes or target appears, revalidate before assigning.

### R5 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/controlled_mock_lane_report.py::controlled_lane_surface_from_report @ L135 | SOURCE_BLOB=362d3ce13c7d5b48eb02b40274115345a2d7dddd

**TARGET (new exclusive A reporting Owner, absent on A remote):** `libs/reporting/controlled_lane_surface_read_projection.py::controlled_lane_surface_from_report`. **ACTUAL UNMOVED SOURCE BODY (design evidence, NOT executable now):**

```python
def controlled_lane_surface_from_report(report: Mapping[str, Any]) -> dict[str, Any]:
    fact_payload = _mapping(report.get("fact_payload"))
    trade = _mapping(fact_payload.get("trade"))
    lifecycle = _first_mapping(report.get("trade_lifecycle"), report.get("lifecycle"), trade.get("trade_lifecycle"), trade.get("lifecycle"))
    entry = _mapping(lifecycle.get("entry"))
    lifecycle_bundle = _first_mapping(report.get("lifecycle_bundle"), trade.get("lifecycle_bundle"))
    bundle_entry = _mapping(_mapping(lifecycle_bundle.get("lifecycle")).get("entry"))
    return _first_mapping(
        report.get("controlled_mock_lane"), trade.get("controlled_mock_lane"),
        lifecycle_bundle.get("controlled_mock_lane"), entry.get("controlled_mock_lane"),
        bundle_entry.get("controlled_mock_lane"),
    )
```

**Safety/owner/wrapper:** RF-035 A-only report/mock evidence projection. When promoted, SOURCE must retain exact signature as thin wrapper; target owns one BODY, no reverse import; use-time `facade` for source globals and monkeypatch parity. No live Broker/Guard/Step5C/UEF, real State, orders, network, operational RunLab or deploy. `_ledger_row` and report builder may read only fixture files under `tmp_path`; never touch real paths. **Targeted normal G2 hypothesis (NOT RUN):** fake report.fact_payload.trade.controlled_mock_lane={'lane_id':'L'} -> same dict; missing surface -> {}. Compare original baseline/owner/wrapper outputs and exceptions, negative case and monkeypatch seam; new targeted unittest normal exit0 and remote push only after promotion. If A source blob changes or target appears, revalidate before assigning.

### R6 VERIFIED DESIGN ONLY | RF-035 | libs/reporting/controlled_mock_lane_report.py::render_controlled_lane_report_lines @ L238 | SOURCE_BLOB=362d3ce13c7d5b48eb02b40274115345a2d7dddd

**TARGET (new exclusive A reporting Owner, absent on A remote):** `libs/reporting/controlled_lane_markdown_projection.py::render_controlled_lane_report_lines`. **ACTUAL UNMOVED SOURCE BODY (design evidence, NOT executable now):**

```python
def render_controlled_lane_report_lines(report: Mapping[str, Any]) -> list[str]:
    surface = controlled_lane_surface_from_report(report)
    if not surface:
        return []
    evidence = _mapping(surface.get("evidence"))
    window = _mapping(surface.get("expected_hold_window"))
    lines = [
        f"* 실행 레인: **{_text(surface.get('lane_label')) or _text(surface.get('lane_id'))}**",
        f"* 신호 ID: `{_text(surface.get('signal_id')) or '-'}`",
        f"* 선택 권한: {_text(surface.get('selection_authority')) or 'deterministic_independent_lane'}",
        f"* Scanner 순위: {'해당 없음' if surface.get('scanner_rank_applicable') is False else '적용'}",
        f"* LLM 사용: {'예' if surface.get('llm_used') else '아니오'}",
    ]
    if surface.get("score") not in (None, ""):
        lines.append(f"* 신호 점수: {surface.get('score')}")
    if evidence:
        evidence_text = " / ".join(f"{key}={value}" for key, value in evidence.items() if value not in (None, "", [], {}))
        if evidence_text:
            lines.append(f"* 고정 가설 근거: {evidence_text}")
    if window:
        lines.append("* 고정 보유 구간: " f"최소 {window.get('min_sec', '-')}초 / 목표 {window.get('target_sec', '-')}초 / 최대 {window.get('max_sec', '-')}초")
    if surface.get("stage3_horizon_review_allowed"):
        lines.append("* R3 연결: 허용. 3차 전략가의 보유기간 재검토를 적용할 수 있습니다.")
    else:
        lines.append("* R3 연결: 차단. 독립 레인과 고정 horizon 비교를 위해 3차 전략가가 보유기간을 변경하지 않습니다.")
    lines.append("* 주문 범위: 키움 모의투자 검증 전용")
    return lines


__all__ = ["apply_controlled_lane_story_surface", "attach_controlled_lane_report_surface", "build_controlled_lane_report_surface", "controlled_lane_surface_from_report", "render_controlled_lane_report_lines"]
```

**Safety/owner/wrapper:** RF-035 A-only report/mock evidence projection. When promoted, SOURCE must retain exact signature as thin wrapper; target owns one BODY, no reverse import; use-time `facade` for source globals and monkeypatch parity. No live Broker/Guard/Step5C/UEF, real State, orders, network, operational RunLab or deploy. `_ledger_row` and report builder may read only fixture files under `tmp_path`; never touch real paths. **Targeted normal G2 hypothesis (NOT RUN):** fake report.controlled_mock_lane with lane_id='L' and expected_hold_window -> lines include '키움 모의투자 검증 전용' and lane L; absent -> []. Compare original baseline/owner/wrapper outputs and exceptions, negative case and monkeypatch seam; new targeted unittest normal exit0 and remote push only after promotion. If A source blob changes or target appears, revalidate before assigning.


## REPORT / CONTINUITY

Report to #11: `ORDER_ID=A-20261031-13 | CANONICAL_HEAD | ORDER_BLOB | A_REMOTE_HEAD_BEFORE/AFTER | A1..A8 IMPLEMENTED/REMOTE_DONE/BLOCKED | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | NEW_BODY_MOVES | FIRST_BLOCKER | NEXT_SAFE_ITEM | START_KST/END_KST/ELAPSED_MIN`. START/END must be actually measured. Preserve exact remote SHA evidence. If terminal HTTPS push fails, mark PUSH_BLOCKED only and continue remaining safe tasks; local-only is not G1. Reserve R1–R6 are NOT executable without a later C03 order. C04 integrates, C05 decides G1/G2/G3/DONE; no RF/STATUS/queue/doc writes by A.
