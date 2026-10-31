# C02 — Claude A | A-20261031-21 | FAST-3 8 NEW actual SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_DESIGN:** `2c9453195ea619bfefbecf24ed711c9de161939d` | **OLD_ORDER_BLOB:** `c311d09dc8cbc25f183fdab7805406821041e1f3` | **A_REMOTE_HEAD:** `aca6396a75fddf2ced1a96025719cb4257b193ae` | **SOURCE_BLOB:** `7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`.

**C03 NEW DELTA:** #11 comment 6542696699: A-20 A1–A8 REMOTE_DONE, normal unittest 8/8 exit0, actor SHA `aca6396a75fddf2ced1a96025719cb4257b193ae`; C04 integrated A20 and C05 scoped accepted, RF-035 already DONE, RF_DONE_DELTA=0. #12 comment 6542649748: B18 B1–B3 additional REMOTE_DONE, B4–B6 pending; B handled separately in C01. #32 no newer delta since 6520075820; RunLab exit255/RUN_SOURCE_SHA UNKNOWN, operational HOLD. Emergency branch unchanged at 069dadd5. A20 old functions/identical SHA tests MUST NOT be repeated.

**One-file complete contract:** Read only this C02 and specified SOURCE/Owner/test code; do NOT read D00, RF details, queue, C03, HANDOFF, or choose own work. Pin canonical HEAD, this ORDER_BLOB, A remote SHA, ORDER_ID. All A1–A8 mandatory independently; individual blocker does not stop remaining safe items. New issuance never retroactively cancels an already-started prior order. Edit/push ONLY A code+test branch, not B, D00, RF, STATUS, C04/C05 or other documents.

**Verified ownership/safety:** RF-035 exclusively CLAUDE_A, current A SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py` blob `7050e36800db8521d2fdf6a3fb0aaa37b7942fcb` matched integration. All eight new TARGETs and tests/test_p15_rf035_21h_quant_shadow_owners.py 404 on both A and integration; six future-reserve targets 404 too. Each SOURCE function still contains actual calculation BODY, not a previous wrapper. Read-only reporting/evaluation calculations, not live strategy enforcement. Do not execute live entry/order, Broker/Guard/Step5C/UEF, RunLab, operational State/DB, network, deploy, frozen oracle or real pipeline. Only in-memory/fake/temp fixtures. Existing import of runtime observation classifiers may be patched with pure fake functions; no operational calls.

**Implementation/test/push:** Move exact bodies below into new exclusive Owner modules; original SOURCE signatures remain thin wrappers, no duplicate body; Owner never imports SOURCE. For dynamic globals use `facade=sys.modules[__name__]` at call time; preserve post-import monkeypatch, ordering, copy identity, exceptions and byte output. Use `from __future__ import annotations` in Owners. Capture original-preimage golden first. Create `tests/test_p15_rf035_21h_quant_shadow_owners.py` with eight named tests, negative/error + patch seam + thin-wrapper/Owner-body checks. Run `python -m py_compile libs/reporting/quant_shadow_candidate_evaluation.py libs/reporting/quant_shadow_*_projection.py` then `python -m unittest tests/test_p15_rf035_21h_quant_shadow_owners.py -v` normal exit0 (scoped pytest alternative). No blanket -O/full peer/CI. Report SOURCE LOC before/after, owner/test blobs, actual normal exit, START/END if measured. Commit/push ONLY libs/reporting/quant_shadow_candidate_evaluation.py, the eight exact A targets and tests/test_p15_rf035_21h_quant_shadow_owners.py to `work/p15-a-reporter-pure-20261021`, non-force; re-fetch remote HEAD and blobs. HTTPS auth failure is PUSH_BLOCKED, continue other safe work; use approved exact-tree expected-head lease only when available. C04 integration and C05 G1/G2/G3 closeout separate.

**Allowed paths:** libs/reporting/quant_shadow_candidate_evaluation.py; libs/reporting/quant_shadow_opening_probe_projection.py; libs/reporting/quant_shadow_opening_probe_enter_projection.py; libs/reporting/quant_shadow_largecap_probe_projection.py; libs/reporting/quant_shadow_largecap_enter_projection.py; libs/reporting/quant_shadow_entry_shape_payload_projection.py; libs/reporting/quant_shadow_vwap_observation_payload_projection.py; libs/reporting/quant_shadow_forward_summary_projection.py; libs/reporting/quant_shadow_top_forward_groups_projection.py; tests/test_p15_rf035_21h_quant_shadow_owners.py. Future reserves R1–R6 are NOT executable.

## A1 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_opening_probe` @ L313 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_opening_probe_projection.py::_opening_probe` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _opening_probe(row: Mapping[str, Any]) -> Dict[str, Any]:
    probe = row.get("opening_momentum_probe_shadow")
    return dict(probe) if isinstance(probe, Mapping) else {}
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: Mapping lookup and copy; facade.Mapping. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_a1_opening_probe` in `tests/test_p15_rf035_21h_quant_shadow_owners.py`. Fixture input→expected: {'opening_momentum_probe_shadow':{'would_probe':1}} → {'would_probe':1}, distinct dict identity; {} → {}. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue A2**.

## A2 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_opening_probe_would_enter` @ L318 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_opening_probe_enter_projection.py::_opening_probe_would_enter` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _opening_probe_would_enter(row: Mapping[str, Any]) -> bool:
    if row.get("opening_momentum_probe_would_enter") not in (None, ""):
        return _bool(row.get("opening_momentum_probe_would_enter"))
    return _bool(_opening_probe(row).get("would_probe"))
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: direct field precedence; facade._bool and facade._opening_probe. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_a2_opening_probe_would_enter` in `tests/test_p15_rf035_21h_quant_shadow_owners.py`. Fixture input→expected: {'opening_momentum_probe_would_enter':'yes'} → True; {'opening_momentum_probe_shadow':{'would_probe':1}} → True; {} → False. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue A3**.

## A3 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_largecap_surge_probe` @ L324 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_largecap_probe_projection.py::_largecap_surge_probe` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _largecap_surge_probe(row: Mapping[str, Any]) -> Dict[str, Any]:
    probe = row.get("opening_largecap_surge_shadow")
    return dict(probe) if isinstance(probe, Mapping) else {}
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade.Mapping and dict copy. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_a3_largecap_surge_probe` in `tests/test_p15_rf035_21h_quant_shadow_owners.py`. Fixture input→expected: {'opening_largecap_surge_shadow':{'would_probe':1}} → {'would_probe':1}, distinct copy; {} → {}. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue A4**.

## A4 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_largecap_surge_would_enter` @ L329 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_largecap_enter_projection.py::_largecap_surge_would_enter` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _largecap_surge_would_enter(row: Mapping[str, Any]) -> bool:
    if row.get("opening_largecap_surge_would_enter") not in (None, ""):
        return _bool(row.get("opening_largecap_surge_would_enter"))
    return _bool(_largecap_surge_probe(row).get("would_probe"))
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade._bool and facade._largecap_surge_probe, direct precedence. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_a4_largecap_surge_would_enter` in `tests/test_p15_rf035_21h_quant_shadow_owners.py`. Fixture input→expected: {'opening_largecap_surge_would_enter':'yes'} → True; {'opening_largecap_surge_shadow':{'would_probe':1}} → True; {} → False. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue A5**.

## A5 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_entry_shape_payload` @ L359 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_entry_shape_payload_projection.py::_entry_shape_payload` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _entry_shape_payload(candidates: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    shapes = Counter(_entry_shape(row) for row in candidates)
    pullback_blocked = sum(
        1
        for row in candidates
        if _entry_shape(row) in {"pullback", "vwap_reclaim"}
        and not _bool(row.get("would_enter"))
    )
    breakout_ready = sum(
        1
        for row in candidates
        if _entry_shape(row) == "breakout"
        and (
            _bool(row.get("would_enter"))
            or _text(row.get("reason"))
            in {
                "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation",
                "breakout_above_recent_high_with_vwap_structure_confirmation",
            }
        )
    )
    breakout_not_ready = sum(
        1
        for row in candidates
        if _entry_shape(row) == "breakout" and not _bool(row.get("would_enter"))
    )
    return {
        "behavior_effect": "diagnostic_only",
        "by_shape": _top_counter(shapes),
        "pullback_or_vwap_blocked_count": pullback_blocked,
        "breakout_ready_like_count": breakout_ready,
        "breakout_not_ready_count": breakout_not_ready,
    }
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade.Counter/_entry_shape/_bool/_text/_top_counter, preserve diagnostic_only and order. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_a5_entry_shape_payload` in `tests/test_p15_rf035_21h_quant_shadow_owners.py`. Fixture input→expected: [] → by_shape=[], pullback_or_vwap_blocked_count=0, breakout_ready_like_count=0, breakout_not_ready_count=0; one {'reason':'breakout_not_ready','would_enter':False} → breakout_not_ready_count=1. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue A6**.

## A6 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_below_vwap_reclaim_observation_payload` @ L401 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_vwap_observation_payload_projection.py::_below_vwap_reclaim_observation_payload` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _below_vwap_reclaim_observation_payload(candidates: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    subtype_counter: Counter[str] = Counter()
    subtype_v2_counter: Counter[str] = Counter()
    total = 0
    for row in candidates:
        observation = _below_vwap_reclaim_observation(row)
        if not _bool(observation.get("applies")):
            continue
        total += 1
        subtype_counter[_text(observation.get("subtype"))] += 1
        subtype_v2_counter[_text(observation.get("subtype_v2"))] += 1
    return {
        "behavior_effect": "observation_only",
        "candidate_count": int(total),
        "by_subtype": _top_counter(subtype_counter, limit=8),
        "by_subtype_v2": _top_counter(subtype_v2_counter, limit=10),
    }
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade.Counter/_below_vwap_reclaim_observation/_bool/_text/_top_counter, observation_only. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_a6_below_vwap_reclaim_observation_payload` in `tests/test_p15_rf035_21h_quant_shadow_owners.py`. Fixture input→expected: [] → candidate_count=0, by_subtype=[], by_subtype_v2=[]; patched facade._below_vwap_reclaim_observation returns applies=True,subtype='x' → candidate_count=1. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue A7**.

## A7 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_forward_outcome_summary` @ L476 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_forward_summary_projection.py::_forward_outcome_summary` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _forward_outcome_summary(rows: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    observed_rows = [row for row in rows if _bool(_forward_outcome(row).get("available"))]
    observed_days = Counter(_candidate_day(row) for row in observed_rows if _candidate_day(row))
    largest_day_count = observed_days.most_common(1)[0][1] if observed_days else 0
    horizon_counts: Dict[str, int] = {}
    horizon_day_counts: Dict[str, int] = {}
    for horizon in ("+3m", "+5m", "+15m", "+30m", "+60m", "EOD"):
        horizon_rows = [
            row
            for row in rows
            if _checkpoint_value(row, horizon, "return_pct") is not None
        ]
        horizon_counts[horizon] = len(horizon_rows)
        horizon_day_counts[horizon] = len(
            {_candidate_day(row) for row in horizon_rows if _candidate_day(row)}
        )
    return {
        "measurement_contract_version": "forward_horizon_coverage.v2",
        "candidate_count": len(rows),
        "observed_count": len(observed_rows),
        "observed_day_count": len(observed_days),
        "sample_concentration": (
            round(float(largest_day_count) / float(len(observed_rows)), 4)
            if observed_rows
            else 0.0
        ),
        "observed_days": [name for name, _count in observed_days.most_common(5)],
        "observed_count_by_horizon": horizon_counts,
        "observed_day_count_by_horizon": horizon_day_counts,
        **{
            f"observed_count_{horizon[1:-1]}m" if horizon.startswith("+") else "observed_count_eod": count
            for horizon, count in horizon_counts.items()
        },
        **{
            f"observed_day_count_{horizon[1:-1]}m" if horizon.startswith("+") else "observed_day_count_eod": count
            for horizon, count in horizon_day_counts.items()
        },
        "avg_return_3m_pct": _mean([_checkpoint_value(row, "+3m", "return_pct") for row in rows]),
        "avg_return_5m_pct": _mean([_checkpoint_value(row, "+5m", "return_pct") for row in rows]),
        "avg_return_15m_pct": _mean([_checkpoint_value(row, "+15m", "return_pct") for row in rows]),
        "avg_return_30m_pct": _mean([_checkpoint_value(row, "+30m", "return_pct") for row in rows]),
        "avg_return_60m_pct": _mean([_checkpoint_value(row, "+60m", "return_pct") for row in rows]),
        "avg_mfe_5m_pct": _mean([_checkpoint_value(row, "+5m", "mfe_pct") for row in rows]),
        "avg_mae_5m_pct": _mean([_checkpoint_value(row, "+5m", "mae_pct") for row in rows]),
        "coverage": (float(len(observed_rows)) / float(len(rows))) if rows else 0.0,
    }
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade.Counter/_bool/_forward_outcome/_candidate_day/_checkpoint_value/_mean; preserve dict key spellings and exception parity. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_a7_forward_outcome_summary` in `tests/test_p15_rf035_21h_quant_shadow_owners.py`. Fixture input→expected: [] → candidate_count=0,observed_count=0,coverage=0.0; fake observed row → preserve horizon order and original dict keys. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue A8**.

## A8 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_top_forward_groups` @ L524 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_top_forward_groups_projection.py::_top_forward_groups` — NEW, verified absent on actor and integration HEAD, single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE; not duplicate, not KEEP):**
```python
def _top_forward_groups(groups: Mapping[str, List[Mapping[str, Any]]], *, limit: int = 10) -> List[Dict[str, Any]]:
    summaries: List[Dict[str, Any]] = []
    for name, rows in groups.items():
        summary = _forward_outcome_summary(rows)
        if int(summary.get("observed_count") or 0) <= 0:
            continue
        summary["name"] = name
        summaries.append(summary)
    summaries.sort(
        key=lambda item: (
            float(item.get("avg_return_5m_pct") or item.get("avg_return_3m_pct") or -999.0),
            int(item.get("observed_count") or 0),
        ),
        reverse=True,
    )
    return summaries[:limit]
```
**SOURCE thin wrapper / caller / monkeypatch:** Preserve exact SOURCE function signature and return/exception semantics. Import the new Owner via package path at call time or stable alias; pass `facade=sys.modules[__name__]` keyword-only for all SOURCE globals; resolve the following through facade at invocation: facade._forward_outcome_summary; sorting, tie-break, mutation, limit preserved. Owner must never import SOURCE; do not change external callers, CLI behavior or policy. Check original-preimage golden, wrapper, Owner and post-import monkeypatch parity, including negative/error path and AST proof of BODY removal.
**Normal targeted test:** `test_a8_top_forward_groups` in `tests/test_p15_rf035_21h_quant_shadow_owners.py`. Fixture input→expected: {} → []; {'a':[]} with facade._forward_outcome_summary returning observed_count=0 → []; two fake group summaries → descending rank and limit. Only fake mappings/TemporaryDirectory; no real runtime. If BLOCKED record exact first blocker and **continue finish targeted test, commit/push, remote re-fetch**.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY (NOT EXECUTABLE)
These are six additional distinct RF-035 A functions, verified actual SOURCE bodies at `7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`, future target paths absent on A and integration. They are NOT work in A-21. New C03 issuance and latest actor/source/target recheck required before implementation.

### R1 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_below_vwap_reclaim_observation` @ L394 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_vwap_observation_projection.py::_below_vwap_reclaim_observation` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
```python
def _below_vwap_reclaim_observation(row: Mapping[str, Any]) -> Dict[str, Any]:
    payload = row.get("below_vwap_reclaim_observation")
    if isinstance(payload, Mapping):
        return dict(payload)
    return classify_below_vwap_reclaim_observation(row)
```
**Future test input→expected:** {'below_vwap_reclaim_observation':{'applies':True}} → {'applies':True}; fallback classifier mocked. **Safety/call-time seams:** facade.Mapping/classify_below_vwap_reclaim_observation, read-only mock. Requires fresh source blob/target check and new C03 issuance before execution.

### R2 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_entry_lane_observation` @ L420 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_entry_lane_observation_projection.py::_entry_lane_observation` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
```python
def _entry_lane_observation(row: Mapping[str, Any]) -> Dict[str, Any]:
    payload = row.get("entry_lane_observation")
    if isinstance(payload, Mapping):
        return dict(payload)
    return build_entry_lane_observation(row)
```
**Future test input→expected:** {'entry_lane_observation':{'primary_lane':'x'}} → {'primary_lane':'x'}; fallback builder mocked. **Safety/call-time seams:** facade.Mapping/build_entry_lane_observation, read-only mock. Requires fresh source blob/target check and new C03 issuance before execution.

### R3 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_entry_lane_observation_payload` @ L427 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_entry_lane_payload_projection.py::_entry_lane_observation_payload` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
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
**Future test input→expected:** [] → candidate_count=0 and all by_* lists=[]. **Safety/call-time seams:** facade.Counter/_entry_lane_observation/_text/_top_counter; fake rows. Requires fresh source blob/target check and new C03 issuance before execution.

### R4 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_entry_lane_forward_outcomes` @ L542 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_entry_lane_forward_projection.py::_entry_lane_forward_outcomes` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
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
**Future test input→expected:** [] → baseline empty result exactly as golden; fake lane groups → same keys/order. **Safety/call-time seams:** facade._entry_lane_subtype/_forward_outcome_summary/_top_forward_groups; fake rows. Requires fresh source blob/target check and new C03 issuance before execution.

### R5 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_scorecard_rows` @ L580 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_scorecard_rows_projection.py::_scorecard_rows` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
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
**Future test input→expected:** [] with mode='best' → []; fake rows → same score/ordering and limit. **Safety/call-time seams:** facade._scorecard_return_signal and other helpers, fake-only. Requires fresh source blob/target check and new C03 issuance before execution.

### R6 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_named_forward_rows` @ L636 | SOURCE_BLOB=`7050e36800db8521d2fdf6a3fb0aaa37b7942fcb`
**TARGET:** `libs/reporting/quant_shadow_named_forward_rows_projection.py::_named_forward_rows` (404 actor/integration, verified absent). **BODY (DESIGN ONLY, DO NOT EXECUTE):**
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
**Future test input→expected:** [],set() → []; fake rows with matching names → golden order. **Safety/call-time seams:** facade helpers resolved at call time, no operational IO. Requires fresh source blob/target check and new C03 issuance before execution.

**G1/G2/G3 separation:** This C02 issuance is a document-only supply, not code G1/G2/G3, not RF DONE. G1 actor remote code + G2 scoped normal exit0, C04 G3 integration and C05 final acceptance remain separate.
