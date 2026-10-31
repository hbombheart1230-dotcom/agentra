# C02 — Claude A | A-20261031-22 | FAST-3 8 NEW actual SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_DESIGN:** `246b0a35e5b961762157859d34c492d7a06d17ff` | **OLD_ORDER_BLOB:** `6c8d49bdadd86d09ccaa0b23455908f63ad6e66e` | **A_REMOTE_HEAD:** `a7aaf71128922f1ac6db5e54e2c1683a7e7e3854` | **SOURCE_BLOB:** `c014b371593ced1c668f97f1372449cf1863ce3f`.

**C03 NEW DELTA:** #11 6543303217 confirms A-21 A1–A8 actual REMOTE_DONE, actor remote `a7aaf71128922f1ac6db5e54e2c1683a7e7e3854`, targeted normal unittest 8/8 exit0. C04 #36 6543477218 integrated exact 10/10 code/test blobs `f3aa21c1927d053d76f6055b3d1eb562fee825b6`; C05 #36 6543513407 accepted scoped G1/G2/G3, RF-035 existing DONE, RF_DONE_DELTA=0. C02 A-21 old items must NOT be rerun. #12 6543204864 B21 NO_MUTATION, remote `68f3f0797951cb35219752956a10a609b8363500`; C01 B21 8 pending remains valid. #32 no new since 6520075820; RunLab exit255/RUN_SOURCE_SHA UNKNOWN operational SAFETY_HOLD. Emergency `069dadd5` unchanged.

**One-file complete execution contract:** Read only THIS C02 and code/test paths named here, not D00/RF/queue/C03/CURRENT/HANDOFF; no self-selection. Pin `CANONICAL_HEAD`, this `ORDER_FILE_BLOB_SHA`, `OWNER_REMOTE_SHA`, `ORDER_ID` at start. Execute all A1–A8 independently, blocked item → next safe item, do not stop at first PASS/commit. An already-started prior order remains valid. Only A-owned code/test branch; no B, D00, RF, STATUS, C04/C05, other documents, CI workflow or schedules.

**Owner/safety:** All A1–A8 are RF-035, exclusive CLAUDE_A, SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py` current exact Git blob `c014b371593ced1c668f97f1372449cf1863ce3f` identical on A actor and integration. Every listed SOURCE still contains a real calculation body (not wrapper); eight TARGET paths and `tests/test_p15_rf035_22h_quant_shadow_owners.py` verified absent on both refs; six design-only reserve targets also absent. This is read-only shadow evaluation/reporting, NOT live entry/strategy/Guard/Step5C/UEF/RunLab. No real accounts/orders, Broker, operational State/DB, network, deploy, frozen oracle, live classifier call. Patch any fallback classifiers with pure fake functions and use in-memory/TemporaryDirectory fixtures only.

**Implementation:** For each item copy the exact SOURCE calculation BODY below to the named NEW single-Owner module and remove it from SOURCE; preserve the SOURCE function's exact signature as a thin wrapper delegating to Owner with `facade=sys.modules[__name__]` (or equivalent call-time resolution). Owner must never import SOURCE. Bind all indicated original globals/helpers from `facade` at invocation time, including `Mapping`, `Counter`, helper functions and constants, so post-import monkeypatch works. Preserve exception types, dict copy/identity, order, generator semantics and public caller compatibility. `from __future__ import annotations` in Owner. Record original-preimage golden before moving and compare original vs wrapper vs Owner, including negative/error and monkeypatch. AST/source check confirms calculation BODY removed, not duplicated.

**Normal G2 + push:** Write NEW `tests/test_p15_rf035_22h_quant_shadow_owners.py` with eight named tests `test_a1`…`test_a8` (exact input→expected below, original golden parity and patch seam); do not overwrite old A19/A20/A21 tests. `python -m py_compile libs/reporting/quant_shadow_candidate_evaluation.py libs/reporting/quant_shadow_*_projection.py` (expand globs to exact files when needed); `python -m unittest tests/test_p15_rf035_22h_quant_shadow_owners.py -v` normal exit0 (scoped pytest alternative). No blanket -O/full peer/hosted CI. Report source before/after LOC, owner/test blobs, normal exit and exact remote SHA. Commit/push ONLY `libs/reporting/quant_shadow_candidate_evaluation.py`, eight NEW targets, `tests/test_p15_rf035_22h_quant_shadow_owners.py` to `work/p15-a-reporter-pure-20261021`, non-force; independently re-fetch remote HEAD and all changed blobs. Git auth failure → PUSH_BLOCKED only; continue safe items and report exact unblock point. C04 G3 and C05 final RF acceptance separate.

**Allowed write paths:** `libs/reporting/quant_shadow_candidate_evaluation.py`; `libs/reporting/quant_shadow_vwap_observation_projection.py`; `libs/reporting/quant_shadow_entry_lane_observation_projection.py`; `libs/reporting/quant_shadow_entry_lane_payload_projection.py`; `libs/reporting/quant_shadow_entry_lane_forward_projection.py`; `libs/reporting/quant_shadow_scorecard_rows_projection.py`; `libs/reporting/quant_shadow_named_forward_rows_projection.py`; `libs/reporting/quant_shadow_format_rows_projection.py`; `libs/reporting/quant_shadow_format_forward_projection.py`; `tests/test_p15_rf035_22h_quant_shadow_owners.py`. Future reserve R1–R6 is DESIGN ONLY, NOT executable in A-22.

## A1 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_below_vwap_reclaim_observation` @ L365 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_vwap_observation_projection.py::_below_vwap_reclaim_observation` — NEW, 404 A/integration, exclusive Owner.
**Exact BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _below_vwap_reclaim_observation(row: Mapping[str, Any]) -> Dict[str, Any]:
    payload = row.get("below_vwap_reclaim_observation")
    if isinstance(payload, Mapping):
        return dict(payload)
    return classify_below_vwap_reclaim_observation(row)
```
**Thin wrapper/caller/monkeypatch:** SOURCE original signature delegates to new Owner at call time with `facade=sys.modules[__name__]`. Bind facade.Mapping and facade.classify_below_vwap_reclaim_observation at call time. No Owner→SOURCE import, no caller/output/exception changes. Compare original-preimage golden, wrapper and Owner, including negative/error/monkeypatch parity and AST actual BODY removal.
**Normal targeted test:** `test_a1_below_vwap_reclaim_observation` in `tests/test_p15_rf035_22h_quant_shadow_owners.py`. Input→expected: row={'below_vwap_reclaim_observation':{'flag':1}} → {'flag':1} (fresh dict); row={} with facade.classify_below_vwap_reclaim_observation=lambda row:{'fallback':True} → {'fallback':True}. Fake in-memory/temp only; never execute real pipeline. On BLOCKED report first blocker and **continue A2**.

## A2 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_entry_lane_observation` @ L376 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_entry_lane_observation_projection.py::_entry_lane_observation` — NEW, 404 A/integration, exclusive Owner.
**Exact BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _entry_lane_observation(row: Mapping[str, Any]) -> Dict[str, Any]:
    payload = row.get("entry_lane_observation")
    if isinstance(payload, Mapping):
        return dict(payload)
    return build_entry_lane_observation(row)
```
**Thin wrapper/caller/monkeypatch:** SOURCE original signature delegates to new Owner at call time with `facade=sys.modules[__name__]`. Bind facade.Mapping and facade.build_entry_lane_observation at call time. No Owner→SOURCE import, no caller/output/exception changes. Compare original-preimage golden, wrapper and Owner, including negative/error/monkeypatch parity and AST actual BODY removal.
**Normal targeted test:** `test_a2_entry_lane_observation` in `tests/test_p15_rf035_22h_quant_shadow_owners.py`. Input→expected: row={'entry_lane_observation':{'primary_lane':'trend'}} → {'primary_lane':'trend'} (fresh dict); row={} with patched facade.build_entry_lane_observation=lambda row:{'primary_lane':'fallback'} → {'primary_lane':'fallback'}. Fake in-memory/temp only; never execute real pipeline. On BLOCKED report first blocker and **continue A3**.

## A3 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_entry_lane_observation_payload` @ L383 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_entry_lane_payload_projection.py::_entry_lane_observation_payload` — NEW, 404 A/integration, exclusive Owner.
**Exact BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _entry_lane_observation_payload(candidates: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    lane_counter: Counter[str] = Counter()
    subtype_counter: Counter[str] = Counter()
    subtype_v2_counter: Counter[str] = Counter()
    lane_subtype_counter: Counter[str] = Counter()
    lane_subtype_v2_counter: Counter[str] = Counter()
    time_bucket_counter: Counter[str] = Counter()
    market_regime_counter: Counter[str] = Counter()
    market_rail_counter: Counter[str] = Counter()
    total = 0
    for row in candidates:
        observation = _entry_lane_observation(row)
        lane = _text(observation.get("primary_lane")) or "unknown"
        subtype = _text(observation.get("subtype")) or "unknown"
        subtype_v2 = _text(observation.get("subtype_v2")) or subtype
        time_bucket = _text(observation.get("time_bucket")) or "unknown"
        market_regime = _text(observation.get("market_regime")) or "unknown"
        market_rail = _text(observation.get("market_regime_rail")) or "unknown"
        total += 1
        lane_counter[lane] += 1
        subtype_counter[subtype] += 1
        subtype_v2_counter[subtype_v2] += 1
        lane_subtype_counter[f"{lane}:{subtype}"] += 1
        lane_subtype_v2_counter[f"{lane}:{subtype_v2}"] += 1
        time_bucket_counter[time_bucket] += 1
        market_regime_counter[market_regime] += 1
        market_rail_counter[market_rail] += 1
    return {
        "behavior_effect": "observation_only",
        "candidate_count": int(total),
        "by_primary_lane": _top_counter(lane_counter, limit=10),
        "by_subtype": _top_counter(subtype_counter, limit=10),
        "by_subtype_v2": _top_counter(subtype_v2_counter, limit=10),
        "by_lane_subtype": _top_counter(lane_subtype_counter, limit=12),
        "by_lane_subtype_v2": _top_counter(lane_subtype_v2_counter, limit=12),
        "by_time_bucket": _top_counter(time_bucket_counter, limit=8),
        "by_market_regime": _top_counter(market_regime_counter, limit=8),
        "by_market_regime_rail": _top_counter(market_rail_counter, limit=8),
    }
```
**Thin wrapper/caller/monkeypatch:** SOURCE original signature delegates to new Owner at call time with `facade=sys.modules[__name__]`. Bind facade.Counter, facade._entry_lane_observation, facade._text, facade._top_counter at call time. No Owner→SOURCE import, no caller/output/exception changes. Compare original-preimage golden, wrapper and Owner, including negative/error/monkeypatch parity and AST actual BODY removal.
**Normal targeted test:** `test_a3_entry_lane_observation_payload` in `tests/test_p15_rf035_22h_quant_shadow_owners.py`. Input→expected: [] → behavior_effect='observation_only', candidate_count=0 and eight by_* groups empty; fake one row with patched observation {'primary_lane':'trend','subtype':'A'} → candidate_count=1 and by_primary_lane=[{'name':'trend','count':1}] subject to original _top_counter output. Fake in-memory/temp only; never execute real pipeline. On BLOCKED report first blocker and **continue A4**.

## A4 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_entry_lane_forward_outcomes` @ L440 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_entry_lane_forward_projection.py::_entry_lane_forward_outcomes` — NEW, 404 A/integration, exclusive Owner.
**Exact BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _entry_lane_forward_outcomes(candidates: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    by_lane: Dict[str, List[Mapping[str, Any]]] = {}
    by_subtype: Dict[str, List[Mapping[str, Any]]] = {}
    by_subtype_v2: Dict[str, List[Mapping[str, Any]]] = {}
    by_lane_subtype: Dict[str, List[Mapping[str, Any]]] = {}
    by_lane_subtype_v2: Dict[str, List[Mapping[str, Any]]] = {}
    by_time_bucket: Dict[str, List[Mapping[str, Any]]] = {}
    by_market_rail: Dict[str, List[Mapping[str, Any]]] = {}
    for row in candidates:
        observation = _entry_lane_observation(row)
        lane = _text(observation.get("primary_lane")) or "unknown"
        subtype = _text(observation.get("subtype")) or "unknown"
        subtype_v2 = _text(observation.get("subtype_v2")) or subtype
        time_bucket = _text(observation.get("time_bucket")) or "unknown"
        market_rail = _text(observation.get("market_regime_rail")) or "unknown"
        by_lane.setdefault(lane, []).append(row)
        by_subtype.setdefault(subtype, []).append(row)
        by_subtype_v2.setdefault(subtype_v2, []).append(row)
        by_lane_subtype.setdefault(f"{lane}:{subtype}", []).append(row)
        by_lane_subtype_v2.setdefault(f"{lane}:{subtype_v2}", []).append(row)
        by_time_bucket.setdefault(time_bucket, []).append(row)
        by_market_rail.setdefault(market_rail, []).append(row)
    return {
        "behavior_effect": "evaluation_only",
        "by_primary_lane": _top_forward_groups(by_lane, limit=10),
        "by_subtype": _top_forward_groups(by_subtype, limit=10),
        "by_subtype_v2": _top_forward_groups(by_subtype_v2, limit=10),
        "by_lane_subtype": _top_forward_groups(by_lane_subtype, limit=12),
        "by_lane_subtype_v2": _top_forward_groups(by_lane_subtype_v2, limit=12),
        "by_time_bucket": _top_forward_groups(by_time_bucket, limit=8),
        "by_market_regime_rail": _top_forward_groups(by_market_rail, limit=8),
    }
```
**Thin wrapper/caller/monkeypatch:** SOURCE original signature delegates to new Owner at call time with `facade=sys.modules[__name__]`. Bind facade._entry_lane_observation, facade._text, facade._top_forward_groups at call time. No Owner→SOURCE import, no caller/output/exception changes. Compare original-preimage golden, wrapper and Owner, including negative/error/monkeypatch parity and AST actual BODY removal.
**Normal targeted test:** `test_a4_entry_lane_forward_outcomes` in `tests/test_p15_rf035_22h_quant_shadow_owners.py`. Input→expected: [] → behavior_effect='evaluation_only' and seven by_* groups []; one fake row with patched observation lane='trend' → same group keys/order as original preimage. Fake in-memory/temp only; never execute real pipeline. On BLOCKED report first blocker and **continue A5**.

## A5 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_scorecard_rows` @ L478 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_scorecard_rows_projection.py::_scorecard_rows` — NEW, 404 A/integration, exclusive Owner.
**Exact BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _scorecard_rows(rows: Sequence[Mapping[str, Any]], *, mode: str, limit: int = 5) -> List[Dict[str, Any]]:
    selected: List[Dict[str, Any]] = []
    for row in rows:
        observed = int(row.get("observed_count") or 0)
        if observed < 10:
            continue
        signal = _scorecard_return_signal(row)
        if signal is None:
            continue
        mfe5 = row.get("avg_mfe_5m_pct")
        mae5 = row.get("avg_mae_5m_pct")
        try:
            mfe5_f = float(mfe5) if mfe5 not in (None, "") else None
        except Exception:
            mfe5_f = None
        try:
            mae5_f = float(mae5) if mae5 not in (None, "") else None
        except Exception:
            mae5_f = None

        if mode == "missed":
            if signal < 0.10 and not (mfe5_f is not None and mfe5_f >= 0.45 and (mae5_f is None or mae5_f > -0.80)):
                continue
            if mae5_f is not None and mae5_f <= -1.25:
                continue
        elif mode == "blocked":
            if signal > -0.05 and not (mae5_f is not None and mae5_f <= -0.75 and signal <= 0.05):
                continue
        else:
            continue

        selected.append(
            {
                "name": _text(row.get("name")),
                "candidate_count": int(row.get("candidate_count") or 0),
                "observed_count": observed,
                "observed_day_count": int(row.get("observed_day_count") or 0),
                "sample_concentration": row.get("sample_concentration"),
                "avg_return_5m_pct": row.get("avg_return_5m_pct"),
                "avg_return_15m_pct": row.get("avg_return_15m_pct"),
                "avg_mfe_5m_pct": row.get("avg_mfe_5m_pct"),
                "avg_mae_5m_pct": row.get("avg_mae_5m_pct"),
                "scorecard_signal_pct": round(signal, 4),
            }
        )

    selected.sort(
        key=lambda item: (
            float(item.get("scorecard_signal_pct") or 0.0),
            int(item.get("observed_count") or 0),
        ),
        reverse=(mode == "missed"),
    )
    return selected[:limit]
```
**Thin wrapper/caller/monkeypatch:** SOURCE original signature delegates to new Owner at call time with `facade=sys.modules[__name__]`. Bind facade._scorecard_return_signal and facade._text at call time. No Owner→SOURCE import, no caller/output/exception changes. Compare original-preimage golden, wrapper and Owner, including negative/error/monkeypatch parity and AST actual BODY removal.
**Normal targeted test:** `test_a5_scorecard_rows` in `tests/test_p15_rf035_22h_quant_shadow_owners.py`. Input→expected: [] mode='missed' → []; row observed_count=9 → []; row observed_count=10 with patched scorecard signal=0.5, mode='missed' → one item with scorecard_signal_pct=0.5; mode='unknown' → []. Fake in-memory/temp only; never execute real pipeline. On BLOCKED report first blocker and **continue A6**.

## A6 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_named_forward_rows` @ L534 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_named_forward_rows_projection.py::_named_forward_rows` — NEW, 404 A/integration, exclusive Owner.
**Exact BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _named_forward_rows(rows: Sequence[Mapping[str, Any]], names: set[str]) -> List[Dict[str, Any]]:
    by_name = {str(row.get("name") or ""): row for row in rows}
    selected: List[Dict[str, Any]] = []
    for name in sorted(names):
        row = by_name.get(name)
        if not isinstance(row, Mapping):
            continue
        observed_count = int(row.get("observed_count") or 0)
        ret5 = row.get("avg_return_5m_pct")
        ret15 = row.get("avg_return_15m_pct")
        try:
            ret5_f = float(ret5) if ret5 not in (None, "") else None
        except Exception:
            ret5_f = None
        try:
            ret15_f = float(ret15) if ret15 not in (None, "") else None
        except Exception:
            ret15_f = None
        if observed_count < 20:
            review_state = "sample_insufficient"
        elif int(row.get("observed_day_count") or 0) < 2:
            review_state = "sample_concentrated_single_day"
        elif ret15_f is not None and ret15_f <= 0:
            review_state = "observe_only_negative_15m"
        elif ret5_f is not None and ret5_f <= 0:
            review_state = "observe_only_negative_5m"
        elif observed_count < PROMOTION_CANDIDATE_MIN_OBSERVED:
            review_state = "sample_insufficient"
        else:
            review_state = "promotion_watch"
        selected.append(
            {
                "name": name,
                "candidate_count": int(row.get("candidate_count") or 0),
                "observed_count": observed_count,
                "observed_day_count": int(row.get("observed_day_count") or 0),
                "sample_concentration": row.get("sample_concentration"),
                "avg_return_5m_pct": row.get("avg_return_5m_pct"),
                "avg_return_15m_pct": row.get("avg_return_15m_pct"),
                "avg_mfe_5m_pct": row.get("avg_mfe_5m_pct"),
                "avg_mae_5m_pct": row.get("avg_mae_5m_pct"),
                "review_state": review_state,
            }
        )
    return selected
```
**Thin wrapper/caller/monkeypatch:** SOURCE original signature delegates to new Owner at call time with `facade=sys.modules[__name__]`. Bind facade.Mapping and facade.PROMOTION_CANDIDATE_MIN_OBSERVED at call time. No Owner→SOURCE import, no caller/output/exception changes. Compare original-preimage golden, wrapper and Owner, including negative/error/monkeypatch parity and AST actual BODY removal.
**Normal targeted test:** `test_a6_named_forward_rows` in `tests/test_p15_rf035_22h_quant_shadow_owners.py`. Input→expected: ([],set()) → []; row name='x',observed_count=0, names={'x'} → one review_state='sample_insufficient'; unknown name ignored, output sorted by names. Fake in-memory/temp only; never execute real pipeline. On BLOCKED report first blocker and **continue A7**.

## A7 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_format_rows` @ L952 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_format_rows_projection.py::_format_rows` — NEW, 404 A/integration, exclusive Owner.
**Exact BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _format_rows(rows: Sequence[Mapping[str, Any]], *, limit: int = 4) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = _text(row.get("name"))
        if not name:
            continue
        parts.append(f"{name} ({row.get('count') or 0})")
    return ", ".join(parts) if parts else "none"
```
**Thin wrapper/caller/monkeypatch:** SOURCE original signature delegates to new Owner at call time with `facade=sys.modules[__name__]`. Bind facade._text at call time. No Owner→SOURCE import, no caller/output/exception changes. Compare original-preimage golden, wrapper and Owner, including negative/error/monkeypatch parity and AST actual BODY removal.
**Normal targeted test:** `test_a7_format_rows` in `tests/test_p15_rf035_22h_quant_shadow_owners.py`. Input→expected: [{'name':'x','count':2}] → 'x (2)'; [] → 'none'; limit=0 → 'none'. Fake in-memory/temp only; never execute real pipeline. On BLOCKED report first blocker and **continue A8**.

## A8 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_format_forward_rows` @ L962 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_format_forward_projection.py::_format_forward_rows` — NEW, 404 A/integration, exclusive Owner.
**Exact BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _format_forward_rows(rows: Sequence[Mapping[str, Any]], *, limit: int = 4) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = _text(row.get("name"))
        if not name:
            continue
        observed = int(row.get("observed_count") or 0)
        count = int(row.get("candidate_count") or 0)
        ret5 = row.get("avg_return_5m_pct")
        ret15 = row.get("avg_return_15m_pct")
        mfe5 = row.get("avg_mfe_5m_pct")
        mae5 = row.get("avg_mae_5m_pct")
        parts.append(
            f"{name} ({observed}/{count}, "
            f"+5m {float(ret5):.4f}%"
            if ret5 is not None
            else f"{name} ({observed}/{count}, +5m n/a"
        )
        if parts:
            last = parts[-1]
            if ret15 is not None:
                last += f", +15m {float(ret15):.4f}%"
            if mfe5 is not None:
                last += f", mfe5 {float(mfe5):.4f}%"
            if mae5 is not None:
                last += f", mae5 {float(mae5):.4f}%"
            parts[-1] = last + ")"
    return "; ".join(parts) if parts else "none"
```
**Thin wrapper/caller/monkeypatch:** SOURCE original signature delegates to new Owner at call time with `facade=sys.modules[__name__]`. Bind facade._text at call time. No Owner→SOURCE import, no caller/output/exception changes. Compare original-preimage golden, wrapper and Owner, including negative/error/monkeypatch parity and AST actual BODY removal.
**Normal targeted test:** `test_a8_format_forward_rows` in `tests/test_p15_rf035_22h_quant_shadow_owners.py`. Input→expected: [{'name':'x','observed_count':2,'candidate_count':3,'avg_return_5m_pct':1.25}] → 'x (2/3, +5m 1.2500%)'; [] → 'none'; malformed numeric must match original exception. Fake in-memory/temp only; never execute real pipeline. On BLOCKED report first blocker and **continue remaining safe verification/push**.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY, NOT EXECUTABLE
These six distinct RF-035 CLAUDE_A SOURCE BODYs and exclusive TARGET paths were checked against `c014b371593ced1c668f97f1372449cf1863ce3f` on actor/integration; all six target filenames absent. They are not part of A-22. Latest source/target SHA recheck and a new C03 executable order required before any move.

### R1 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_text` @ L52 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_text_projection.py::_text` (verified absent actor/integration; design-only).
**Exact BODY (NOT EXECUTABLE in A-22):**
```python
def _text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() in {"", "-", "none", "null", "unknown", "not_captured"} else text
```
**Future targeted input→expected:** ' unknown ' → ''; ' x ' → 'x'. **Safety/compatibility:** pure scalar, facade-free; preserve string conversion; retain SOURCE signature/thin wrapper and original golden/monkeypatch semantics. Only fake/temp, no real effects. Recheck latest HEAD and target absence before issuance.

### R2 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_read_json` @ L61 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_json_projection.py::_read_json` (verified absent actor/integration; design-only).
**Exact BODY (NOT EXECUTABLE in A-22):**
```python
def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
```
**Future targeted input→expected:** temp valid JSON {'x':1} → {'x':1}; missing path → None. **Safety/compatibility:** facade.json at call time; temp only; retain SOURCE signature/thin wrapper and original golden/monkeypatch semantics. Only fake/temp, no real effects. Recheck latest HEAD and target absence before issuance.

### R3 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_json_paths_for_day` @ L76 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_day_paths_projection.py::_json_paths_for_day` (verified absent actor/integration; design-only).
**Exact BODY (NOT EXECUTABLE in A-22):**
```python
def _json_paths_for_day(root: Path, day: str) -> List[Path]:
    day_dir = root / str(day)[:10]
    if not day_dir.exists():
        return []
    return sorted(path for path in day_dir.glob("*.json") if path.name != "latest.json")
```
**Future targeted input→expected:** temp day dir with a.json,latest.json → [a.json]. **Safety/compatibility:** facade.Path; temp only; preserve sorted paths; retain SOURCE signature/thin wrapper and original golden/monkeypatch semantics. Only fake/temp, no real effects. Recheck latest HEAD and target absence before issuance.

### R4 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_drop_q9_row_keys` @ L176 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_drop_q9_projection.py::_drop_q9_row_keys` (verified absent actor/integration; design-only).
**Exact BODY (NOT EXECUTABLE in A-22):**
```python
def _drop_q9_row_keys(payload: Dict[str, Any], drop: Optional[Sequence[str]]) -> Dict[str, Any]:
    """Remove `drop` keys from every q9 decision-candidate row of `payload` (no-op when `drop` is empty)."""
    if drop:
        for row in payload.get("q9_decision_candidates") or []:
            if isinstance(row, dict):
                for key in drop:
                    row.pop(key, None)
    return payload
```
**Future targeted input→expected:** payload {'q9_decision_candidates':[{'x':1,'y':2}]} drop=['x'] → same payload identity with row {'y':2}. **Safety/compatibility:** in-place mutation of supplied fake dict only; preserve identity; retain SOURCE signature/thin wrapper and original golden/monkeypatch semantics. Only fake/temp, no real effects. Recheck latest HEAD and target absence before issuance.

### R5 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_format_scorecard_rows` @ L992 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_format_scorecard_projection.py::_format_scorecard_rows` (verified absent actor/integration; design-only).
**Exact BODY (NOT EXECUTABLE in A-22):**
```python
def _format_scorecard_rows(rows: Sequence[Mapping[str, Any]], *, limit: int = 4) -> str:
    parts: List[str] = []
    for row in list(rows)[:limit]:
        name = _text(row.get("name"))
        if not name:
            continue
        observed = int(row.get("observed_count") or 0)
        count = int(row.get("candidate_count") or 0)
        ret5 = row.get("avg_return_5m_pct")
        ret15 = row.get("avg_return_15m_pct")
        mfe5 = row.get("avg_mfe_5m_pct")
        mae5 = row.get("avg_mae_5m_pct")
        state = _text(row.get("review_state"))
        text = (
            f"{name} ({observed}/{count}, "
            f"+5m {float(ret5):.4f}%"
            if ret5 is not None
            else f"{name} ({observed}/{count}, +5m n/a"
        )
        if ret15 is not None:
            text += f", +15m {float(ret15):.4f}%"
        if mfe5 is not None:
            text += f", mfe5 {float(mfe5):.4f}%"
        if mae5 is not None:
            text += f", mae5 {float(mae5):.4f}%"
        if state:
            text += f", state {state}"
        parts.append(text + ")")
    return "; ".join(parts) if parts else "none"
```
**Future targeted input→expected:** [] → 'none'; fake name='x',observed_count=2,candidate_count=3,ret5=1.0 → contains '+5m 1.0000%'. **Safety/compatibility:** facade._text; fake-only; retain SOURCE signature/thin wrapper and original golden/monkeypatch semantics. Only fake/temp, no real effects. Recheck latest HEAD and target absence before issuance.

### R6 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_shadow_readiness` @ L770 | SOURCE_BLOB=`c014b371593ced1c668f97f1372449cf1863ce3f`
**TARGET:** `libs/reporting/quant_shadow_readiness_projection.py::_shadow_readiness` (verified absent actor/integration; design-only).
**Exact BODY (NOT EXECUTABLE in A-22):**
```python
def _shadow_readiness(candidates: Sequence[Mapping[str, Any]], promotion: Mapping[str, Any]) -> Dict[str, Any]:
    candidate_count = len(candidates)
    evaluated_count = sum(1 for row in candidates if _bool(row.get("evaluated")))
    evaluated_ratio = float(evaluated_count) / float(candidate_count) if candidate_count else 0.0
    candidate = _text(promotion.get("candidate"))
    confidence = _text(promotion.get("confidence"))
    action = _text(promotion.get("recommended_action")) or "hold"
    ready = bool(
        candidate_count >= TRUSTED_FORWARD_MIN_COUNT
        and evaluated_count >= PROMOTION_CANDIDATE_MIN_OBSERVED
        and evaluated_ratio >= TRUSTED_FORWARD_MIN_COVERAGE
        and candidate not in {"", "hold"}
        and confidence in {"medium", "high"}
    )
    if not candidate_count:
        status = "hold_no_shadow_candidates"
    elif ready:
        status = "ready"
    elif evaluated_count < PROMOTION_CANDIDATE_MIN_OBSERVED:
        status = "hold_shadow_sample_insufficient"
    elif evaluated_ratio < TRUSTED_FORWARD_MIN_COVERAGE:
        status = "hold_shadow_coverage_insufficient"
    else:
        status = "review_shadow_signal_weak"
    return {
        "status": status,
        "action": action if ready else "hold",
        "candidate_count": candidate_count,
        "evaluated_count": evaluated_count,
        "evaluated_ratio": evaluated_ratio,
        "sample_floor": TRUSTED_FORWARD_MIN_COUNT,
        "evaluated_floor": PROMOTION_CANDIDATE_MIN_OBSERVED,
        "coverage_floor": TRUSTED_FORWARD_MIN_COVERAGE,
        "candidate": candidate or "hold",
        "confidence": confidence or "none",
        "promotion_scope": _text(promotion.get("promotion_scope")) or "none",
    }
```
**Future targeted input→expected:** ([], {}) → status='hold_no_shadow_candidates', action='hold', evaluated_ratio=0.0. **Safety/compatibility:** facade._bool/_text and constants; evaluation-only no real gate invocation; retain SOURCE signature/thin wrapper and original golden/monkeypatch semantics. Only fake/temp, no real effects. Recheck latest HEAD and target absence before issuance.

**G1/G2/G3 separation:** C02 document supply is not code G1/G2/G3, no RF DONE delta. Actor remote code + scoped normal exit0 → C04 exact integration → C05 final acceptance. Never count previous A21 or reserve as new implementation.
