# C02 — Claude A | A-20261031-20 | FAST-3 eight NEW verified SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_ISSUANCE:** `c38cc05709700486c59704710b26f9db6db45575` · **OLD_ORDER_BLOB:** `b005ac47c17274054ed1d73f45e38b492504ee24` · **A_REMOTE_HEAD_AT_DESIGN:** `d55f50fe3830e768fbdf01d595739095b317862d` · **SOURCE_BLOB:** `1758abc17594e8c1ecf99810a47a207f340a2c39`.

**C03 new delta (20h):** #11 `6542146568`: A-20261031-19 A1–A8 actual BODY MOVEs REMOTE_DONE 8/8, actor push `d55f50fe3830e768fbdf01d595739095b317862d`, normal `python -m unittest tests/test_p15_rf035_19h_quant_shadow_owners.py` exit0 8/8. C04 exact integration `d7f5684207fabb307e8e00d4c8211351b1f7e8a0` and C05 scoped acceptance; RF-035 already DONE, RF_DONE_DELTA=0. No repeat of A19 or same-SHA tests. #12 `6542067869`: B18 B7/B8 REMOTE_DONE 2/8, B1–B6 still safe READY; C01 separately trimmed by C03, no A/B cross-work. #32 unchanged since `6520075820`, RunLab exit255/RUN_SOURCE_SHA UNKNOWN; do not operate runtime. Emergency branch no new observed HEAD.

**One-file execution contract:** Claude A reads THIS C02 only, pins CANONICAL_HEAD/ORDER_BLOB/A_REMOTE_HEAD/ORDER_ID, executes **all A1–A8** independently; a blocked item does not block the others. No D00, RF details, queue, C03 or handoff reading; no self-selection of FUTURE RESERVE. A newer C02 does not retroactively cancel an already-started order. A edits/pushes only A branch code and targeted test, not docs, RF, STATUS, C04/C05, B branch or operational files.

**Verified scope:** RF-035 exclusively CLAUDE_A; actual SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py` at blob `1758abc17594e8c1ecf99810a47a207f340a2c39` matched A and integration after A19. The 8 TARGET files below plus `tests/test_p15_rf035_20h_quant_shadow_owners.py` were **404 on both A and integration**. The six future-reserve TARGETs were also 404 both refs. All 8 SOURCE function bodies were inspected at A remote HEAD and are still original calculation bodies, not prior thin wrappers; disjoint from A19 and B. These are **read-only shadow reporting/evaluation** helpers, never live entry enforcement.

**Implementation:** Move each exact Python BODY below into named NEW A-exclusive Owner module; leave original signature/annotations in SOURCE as a thin delegating wrapper (no duplicated computation). Owner must NOT import SOURCE. For call-time globals use `def fn(..., *, facade):` in Owner and SOURCE delegates with `facade=_p15_sys.modules[__name__]` (`import sys as _p15_sys` only if needed). Resolve specified names via `facade.name` at invocation, not captured imports; preserve monkeypatch seams, call order, dict copy/identity, exceptions, output bytes. Use `from __future__ import annotations` in new Owner modules; keep original public SOURCE signatures unchanged. Do not modify callers unless a narrow verified seam defect requires test-only correction.

**Safety:** fake in-memory mappings and TemporaryDirectory only; never invoke full shadow pipeline, live entry/order, broker, Guard/Step5C/UEF, RunLab, operational State/DB, network, deploy, real CLI, protected policies or frozen oracle. No strategy behavior changes. First obtain original-preimage golden for each item, then assert original vs SOURCE wrapper vs Owner parity, negative/exception behavior, post-import facade monkeypatch, and AST proof that SOURCE computation BODY was removed (one-line originals require Owner-body verification, not AST alone). Create **actual tests** `tests/test_p15_rf035_20h_quant_shadow_owners.py` with named `test_a1_...` through `test_a8_...`. Run `python -m py_compile` on SOURCE and all 8 TARGET files, then normal `python -m unittest tests/test_p15_rf035_20h_quant_shadow_owners.py -v` (or scoped pytest) **exit0**. No blanket -O/full-peer/full-suite/hosted-CI requirement. Record actual exit, pass count, SOURCE before/after LOC, Owner/test blobs. Commit/push only A code+test to `work/p15-a-reporter-pure-20261021`, non-force, re-fetch A HEAD and every SOURCE/Owner/test blob; if HTTPS auth fails mark PUSH_BLOCKED and continue safe items, use only previously approved exact-tree expected-head lease if available. C04 G3/C05 DONE are separate.

**Allowed changed files:** `libs/reporting/quant_shadow_candidate_evaluation.py`, exactly the eight A1–A8 TARGETs below, and `tests/test_p15_rf035_20h_quant_shadow_owners.py`. Do not implement reserve R1–R6 in this order.

## A1 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_cost_floor_state` @ L269 | SOURCE_BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_cost_floor_projection.py::_cost_floor_state` (NEW, 404 A/integration, A-exclusive).
**Exact SOURCE computation BODY to MOVE (not copy/KEEP/test-only):**
```python
def _cost_floor_state(row: Mapping[str, Any]) -> str:
    direct = _text(row.get("entry_quant_cost_floor_state"))
    if direct:
        return direct
    decision = row.get("entry_quant_decision")
    if isinstance(decision, Mapping):
        cost_edge = decision.get("cost_edge")
        if isinstance(cost_edge, Mapping):
            state = _text(cost_edge.get("cost_floor_state"))
            if state:
                return state
    snapshot = row.get("quant_factor_snapshot")
    if isinstance(snapshot, Mapping):
        factors = snapshot.get("factors")
        if isinstance(factors, Mapping):
            return _text(factors.get("cost_floor_state"))
    return ""
```
**Thin wrapper/callers/monkeypatch:** facade._text and facade.Mapping at invocation; preserve direct→decision.cost_edge→snapshot precedence and early return. SOURCE original signature remains; delegate to Owner at call time; preserve original output/exception semantics, no Owner→SOURCE import or duplicate BODY.
**Normal targeted test:** `test_a1_cost_floor_state` in `tests/test_p15_rf035_20h_quant_shadow_owners.py`; input→expected: {'entry_quant_cost_floor_state':'safe'}→'safe'; {'entry_quant_decision':{'cost_edge':{'cost_floor_state':'hold'}}}→'hold'; {}→''. Compare preimage golden, wrapper, Owner; negative and call-time patch seams; AST BODY removal. If BLOCKED record exact first reason and continue **A2**.

## A2 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_entry_quant_decision` @ L288 | SOURCE_BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_entry_decision_projection.py::_entry_quant_decision` (NEW, 404 A/integration, A-exclusive).
**Exact SOURCE computation BODY to MOVE (not copy/KEEP/test-only):**
```python
def _entry_quant_decision(row: Mapping[str, Any]) -> str:
    decision = row.get("entry_quant_decision")
    if isinstance(decision, Mapping):
        return _text(decision.get("decision"))
    return ""
```
**Thin wrapper/callers/monkeypatch:** facade._text and facade.Mapping at invocation; preserve absent/non-Mapping return empty string. SOURCE original signature remains; delegate to Owner at call time; preserve original output/exception semantics, no Owner→SOURCE import or duplicate BODY.
**Normal targeted test:** `test_a2_entry_quant_decision` in `tests/test_p15_rf035_20h_quant_shadow_owners.py`; input→expected: {'entry_quant_decision':{'decision':'entry_ready'}}→'entry_ready'; {}→''. Compare preimage golden, wrapper, Owner; negative and call-time patch seams; AST BODY removal. If BLOCKED record exact first reason and continue **A3**.

## A3 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_tactic_id` @ L295 | SOURCE_BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_tactic_projection.py::_tactic_id` (NEW, 404 A/integration, A-exclusive).
**Exact SOURCE computation BODY to MOVE (not copy/KEEP/test-only):**
```python
def _tactic_id(row: Mapping[str, Any]) -> str:
    direct = _text(row.get("quant_tactic_id") or row.get("tactic_id"))
    if direct:
        return direct
    decision = row.get("entry_quant_decision")
    if isinstance(decision, Mapping):
        tactic = _text(decision.get("tactic_id"))
        if tactic:
            return tactic
    snapshot = row.get("quant_factor_snapshot")
    if isinstance(snapshot, Mapping):
        return _text(snapshot.get("tactic_id"))
    return ""
```
**Thin wrapper/callers/monkeypatch:** facade._text and facade.Mapping at invocation; preserve quant_tactic_id→tactic_id→decision→snapshot priority. SOURCE original signature remains; delegate to Owner at call time; preserve original output/exception semantics, no Owner→SOURCE import or duplicate BODY.
**Normal targeted test:** `test_a3_tactic_id` in `tests/test_p15_rf035_20h_quant_shadow_owners.py`; input→expected: {'quant_tactic_id':'T1'}→'T1'; {'entry_quant_decision':{'tactic_id':'T2'}}→'T2'; {}→''. Compare preimage golden, wrapper, Owner; negative and call-time patch seams; AST BODY removal. If BLOCKED record exact first reason and continue **A4**.

## A4 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_tactic_suitability_tier` @ L310 | SOURCE_BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_tactic_tier_projection.py::_tactic_suitability_tier` (NEW, 404 A/integration, A-exclusive).
**Exact SOURCE computation BODY to MOVE (not copy/KEEP/test-only):**
```python
def _tactic_suitability_tier(row: Mapping[str, Any]) -> str:
    direct = _text(row.get("tactic_suitability_tier"))
    if direct:
        return direct
    decision = row.get("entry_quant_decision")
    if isinstance(decision, Mapping):
        suitability = decision.get("tactic_suitability")
        if isinstance(suitability, Mapping):
            tier = _text(suitability.get("tier"))
            if tier:
                return tier
    return ""
```
**Thin wrapper/callers/monkeypatch:** facade._text and facade.Mapping at invocation; preserve direct tier priority over nested tier. SOURCE original signature remains; delegate to Owner at call time; preserve original output/exception semantics, no Owner→SOURCE import or duplicate BODY.
**Normal targeted test:** `test_a4_tactic_suitability_tier` in `tests/test_p15_rf035_20h_quant_shadow_owners.py`; input→expected: {'tactic_suitability_tier':'high'}→'high'; {'entry_quant_decision':{'tactic_suitability':{'tier':'low'}}}→'low'; {}→''. Compare preimage golden, wrapper, Owner; negative and call-time patch seams; AST BODY removal. If BLOCKED record exact first reason and continue **A5**.

## A5 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_forward_base` @ L324 | SOURCE_BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_forward_base_projection.py::_forward_base` (NEW, 404 A/integration, A-exclusive).
**Exact SOURCE computation BODY to MOVE (not copy/KEEP/test-only):**
```python
def _forward_base(row: Mapping[str, Any]) -> Dict[str, Any]:
    base = row.get("shadow_forward_base")
    return dict(base) if isinstance(base, Mapping) else {}
```
**Thin wrapper/callers/monkeypatch:** facade.Mapping at invocation; preserve dict copy, not alias, and non-Mapping empty fallback. SOURCE original signature remains; delegate to Owner at call time; preserve original output/exception semantics, no Owner→SOURCE import or duplicate BODY.
**Normal targeted test:** `test_a5_forward_base` in `tests/test_p15_rf035_20h_quant_shadow_owners.py`; input→expected: {'shadow_forward_base':{'a':1}}→{'a':1} (distinct dict identity); {}→{}. Compare preimage golden, wrapper, Owner; negative and call-time patch seams; AST BODY removal. If BLOCKED record exact first reason and continue **A6**.

## A6 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_forward_outcome` @ L329 | SOURCE_BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_forward_outcome_projection.py::_forward_outcome` (NEW, 404 A/integration, A-exclusive).
**Exact SOURCE computation BODY to MOVE (not copy/KEEP/test-only):**
```python
def _forward_outcome(row: Mapping[str, Any]) -> Dict[str, Any]:
    outcome = row.get("shadow_forward_outcome")
    return dict(outcome) if isinstance(outcome, Mapping) else {}
```
**Thin wrapper/callers/monkeypatch:** facade.Mapping at invocation; preserve dict copy, not alias, and non-Mapping empty fallback. SOURCE original signature remains; delegate to Owner at call time; preserve original output/exception semantics, no Owner→SOURCE import or duplicate BODY.
**Normal targeted test:** `test_a6_forward_outcome` in `tests/test_p15_rf035_20h_quant_shadow_owners.py`; input→expected: {'shadow_forward_outcome':{'checkpoints':{}}}→{'checkpoints':{}} (distinct dict identity); {}→{}. Compare preimage golden, wrapper, Owner; negative and call-time patch seams; AST BODY removal. If BLOCKED record exact first reason and continue **A7**.

## A7 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_entry_shape` @ L388 | SOURCE_BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_entry_shape_projection.py::_entry_shape` (NEW, 404 A/integration, A-exclusive).
**Exact SOURCE computation BODY to MOVE (not copy/KEEP/test-only):**
```python
def _entry_shape(row: Mapping[str, Any]) -> str:
    reason = _text(row.get("reason"))
    primary = _text(row.get("primary_failure_axis"))
    if reason in {
        "pullback_not_mature",
        "pullback_below_vwap_reclaim_not_ready",
        "pullback_structure_above_vwap_with_volume_confirmation",
    } or primary == "pullback_structure":
        return "pullback"
    if reason in {
        "below_vwap_reclaim_not_ready",
        "pullback_below_vwap_reclaim_not_ready",
    } or primary == "vwap_relationship":
        return "vwap_reclaim"
    if reason in {
        "breakout_above_recent_high_with_vwap_hold_and_volume_confirmation",
        "breakout_above_recent_high_with_vwap_structure_confirmation",
        "breakout_not_ready",
    } or primary == "breakout_readiness":
        return "breakout"
    if reason in {"volume_confirmation_missing", "volume_insufficient"} or primary == "volume_confirmation":
        return "volume_confirmation"
    if reason == "human_chart_sanity_guard_blocked" or primary == "human_chart_sanity":
        return "human_chart_sanity"
    return "other"
```
**Thin wrapper/callers/monkeypatch:** facade._text at invocation; preserve exact ordered reason/primary branch precedence; diagnostic classification only, no live policy. SOURCE original signature remains; delegate to Owner at call time; preserve original output/exception semantics, no Owner→SOURCE import or duplicate BODY.
**Normal targeted test:** `test_a7_entry_shape` in `tests/test_p15_rf035_20h_quant_shadow_owners.py`; input→expected: {'reason':'breakout_not_ready'}→'breakout'; {'primary_failure_axis':'volume_confirmation'}→'volume_confirmation'; {}→'other'. Compare preimage golden, wrapper, Owner; negative and call-time patch seams; AST BODY removal. If BLOCKED record exact first reason and continue **A8**.

## A8 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_checkpoint_value` @ L528 | SOURCE_BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_checkpoint_projection.py::_checkpoint_value` (NEW, 404 A/integration, A-exclusive).
**Exact SOURCE computation BODY to MOVE (not copy/KEEP/test-only):**
```python
def _checkpoint_value(row: Mapping[str, Any], checkpoint: str, metric: str) -> float | None:
    outcome = _forward_outcome(row)
    checkpoints = outcome.get("checkpoints")
    if not isinstance(checkpoints, Mapping):
        return None
    payload = checkpoints.get(checkpoint)
    if not isinstance(payload, Mapping) or _text(payload.get("status")) != "observed":
        return None
    value = payload.get(metric)
    try:
        if value in (None, ""):
            return None
        return float(value)
    except Exception:
        return None
```
**Thin wrapper/callers/monkeypatch:** facade._forward_outcome, facade._text, facade.Mapping at invocation; preserve observed-only status, numeric coercion and exception→None. SOURCE original signature remains; delegate to Owner at call time; preserve original output/exception semantics, no Owner→SOURCE import or duplicate BODY.
**Normal targeted test:** `test_a8_checkpoint_value` in `tests/test_p15_rf035_20h_quant_shadow_owners.py`; input→expected: {'shadow_forward_outcome':{'checkpoints':{'5m':{'status':'observed','ret':'1.25'}}}},'5m','ret'→1.25; {'shadow_forward_outcome':{'checkpoints':{'5m':{'status':'pending','ret':3}}}},'5m','ret'→None. Compare preimage golden, wrapper, Owner; negative and call-time patch seams; AST BODY removal. If BLOCKED record exact first reason and continue **report/push**.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY, NOT EXECUTABLE
All six are additional, distinct RF-035 Claude A SOURCE functions on current A/integration SOURCE blob `1758abc17594e8c1ecf99810a47a207f340a2c39`; all six proposed TARGETs returned 404 on both refs; read-only reporting calculations, no B collision. They are **NOT authorized for implementation** until C03 issues a new C02 and rechecks A HEAD, SOURCE body/blob, TARGET absence, safety and caller seams after A1–A8 change this SOURCE. Tests below are design fixtures only.

### R1 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_opening_probe` @ L346 | BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_opening_probe_projection.py::_opening_probe` (404 A/integration; A-exclusive, future only).
**Verified BODY (DESIGN ONLY):**
```python
def _opening_probe(row: Mapping[str, Any]) -> Dict[str, Any]:
    probe = row.get("opening_momentum_probe_shadow")
    return dict(probe) if isinstance(probe, Mapping) else {}
```
**Safety/patch:** facade.Mapping; dict copy from opening_momentum_probe_shadow. No real pipeline, fake in-memory only; SOURCE thin wrapper and call-time seam when later authorized. **Future normal test input→expected:** {'opening_momentum_probe_shadow':{'would_probe':1}}→{'would_probe':1}; {}→{}; original golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, no implementation now.

### R2 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_opening_probe_would_enter` @ L351 | BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_opening_probe_enter_projection.py::_opening_probe_would_enter` (404 A/integration; A-exclusive, future only).
**Verified BODY (DESIGN ONLY):**
```python
def _opening_probe_would_enter(row: Mapping[str, Any]) -> bool:
    if row.get("opening_momentum_probe_would_enter") not in (None, ""):
        return _bool(row.get("opening_momentum_probe_would_enter"))
    return _bool(_opening_probe(row).get("would_probe"))
```
**Safety/patch:** facade._bool and facade._opening_probe at invocation; direct field overrides nested fallback. No real pipeline, fake in-memory only; SOURCE thin wrapper and call-time seam when later authorized. **Future normal test input→expected:** {'opening_momentum_probe_would_enter':'yes'}→True; {'opening_momentum_probe_shadow':{'would_probe':1}}→True; {}→False; original golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, no implementation now.

### R3 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_largecap_surge_probe` @ L357 | BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_largecap_probe_projection.py::_largecap_surge_probe` (404 A/integration; A-exclusive, future only).
**Verified BODY (DESIGN ONLY):**
```python
def _largecap_surge_probe(row: Mapping[str, Any]) -> Dict[str, Any]:
    probe = row.get("opening_largecap_surge_shadow")
    return dict(probe) if isinstance(probe, Mapping) else {}
```
**Safety/patch:** facade.Mapping; dict copy from opening_largecap_surge_shadow. No real pipeline, fake in-memory only; SOURCE thin wrapper and call-time seam when later authorized. **Future normal test input→expected:** {'opening_largecap_surge_shadow':{'would_probe':1}}→{'would_probe':1}; {}→{}; original golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, no implementation now.

### R4 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_largecap_surge_would_enter` @ L362 | BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_largecap_probe_enter_projection.py::_largecap_surge_would_enter` (404 A/integration; A-exclusive, future only).
**Verified BODY (DESIGN ONLY):**
```python
def _largecap_surge_would_enter(row: Mapping[str, Any]) -> bool:
    if row.get("opening_largecap_surge_would_enter") not in (None, ""):
        return _bool(row.get("opening_largecap_surge_would_enter"))
    return _bool(_largecap_surge_probe(row).get("would_probe"))
```
**Safety/patch:** facade._bool and facade._largecap_surge_probe at invocation; direct overrides nested. No real pipeline, fake in-memory only; SOURCE thin wrapper and call-time seam when later authorized. **Future normal test input→expected:** {'opening_largecap_surge_would_enter':True}→True; {'opening_largecap_surge_shadow':{'would_probe':1}}→True; {}→False; original golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, no implementation now.

### R5 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_below_vwap_reclaim_observation` @ L450 | BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_below_vwap_projection.py::_below_vwap_reclaim_observation` (404 A/integration; A-exclusive, future only).
**Verified BODY (DESIGN ONLY):**
```python
def _below_vwap_reclaim_observation(row: Mapping[str, Any]) -> Dict[str, Any]:
    payload = row.get("below_vwap_reclaim_observation")
    if isinstance(payload, Mapping):
        return dict(payload)
    return classify_below_vwap_reclaim_observation(row)
```
**Safety/patch:** facade.Mapping and facade.classify_below_vwap_reclaim_observation at invocation; fake payload avoids live pipeline. No real pipeline, fake in-memory only; SOURCE thin wrapper and call-time seam when later authorized. **Future normal test input→expected:** {'below_vwap_reclaim_observation':{'state':'x'}}→{'state':'x'}; fallback only with patched fake classifier; original golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, no implementation now.

### R6 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_entry_lane_observation` @ L476 | BLOB=`1758abc17594e8c1ecf99810a47a207f340a2c39`
**TARGET:** `libs/reporting/quant_shadow_entry_lane_projection.py::_entry_lane_observation` (404 A/integration; A-exclusive, future only).
**Verified BODY (DESIGN ONLY):**
```python
def _entry_lane_observation(row: Mapping[str, Any]) -> Dict[str, Any]:
    payload = row.get("entry_lane_observation")
    if isinstance(payload, Mapping):
        return dict(payload)
    return build_entry_lane_observation(row)
```
**Safety/patch:** facade.Mapping and facade.build_entry_lane_observation at invocation; fake payload avoids live pipeline. No real pipeline, fake in-memory only; SOURCE thin wrapper and call-time seam when later authorized. **Future normal test input→expected:** {'entry_lane_observation':{'lane':'L'}}→{'lane':'L'}; fallback only with patched fake builder; original golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, no implementation now.

## REPORT / PUSH
#11 comment: `ORDER_ID=A-20261031-20 | CANONICAL_HEAD | ORDER_BLOB | A_REMOTE_BEFORE→AFTER | A1..A8 ITEM_STATUS | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | MOVED_FUNCTIONS | SOURCE_LOC_BEFORE_AFTER | FIRST_BLOCKER | NEXT_SAFE_ITEM | PUSH_REMOTE_SHA/PUSH_BLOCKED | START_KST/END_KST/ELAPSED_MIN`. START/END measured only, never inferred from comment time. C03 document supply is NOT code G1/G2/G3 or new RF_DONE. RunLab SOURCE_UNKNOWN/exit255 remains SAFETY_HOLD.
