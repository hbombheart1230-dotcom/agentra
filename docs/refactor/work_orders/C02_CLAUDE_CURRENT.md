# C02 — Claude A | A-20261031-19 | FAST-3 eight NEW verified SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_ISSUANCE:** `58ae1829a470d45120c5777405f2787f1fea255e` · **OLD_ORDER_BLOB:** `aa76914f70432192da088d32978a28424898ecb9` · **A_REMOTE_HEAD_AT_DESIGN:** `3041b41ea51b455971e1fcf609095b60a48daf40` · **SOURCE_BLOB:** `c46916f178b600cef3729d65e197e7e971d851cd`.

#11 6541615114 and remote A source/Owner/test evidence: A-20261031-18 A1–A8 **REMOTE_DONE 8/8**, normal unittest 8/8 exit0, integrated via C04 5d7ef926 and C05 accepted. DO NOT repeat prior profitability-recovery tasks or prior tests. #12 6541579406: B-18 0/8, B remote f5e41ab6 unchanged, B C01 remains valid and MUST NOT be replaced by A. #32 no new comment after 6520075820; RunLab runtime exit255, RUN_SOURCE_SHA=UNKNOWN, operational SAFETY_HOLD.

**Single-document execution:** Read only THIS C02. Pin CANONICAL_HEAD, ORDER_BLOB, A_REMOTE_HEAD, ORDER_ID. Implement all A1–A8 independently in this order, continuing after any individual blocker. Do not read D00/RF/queue/C03/handoff or self-select reserve. The new C02 does not cancel an already-started older A order retroactively. A only edits its own branch code/tests. No docs/RF/STATUS/C04/C05 or other Actor files, force push, frozen oracle, workflow or live effects.

**Verified scope:** RF-035, Claude A exclusive reporting SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py`; A and integration exact SOURCE blob `c46916f178b600cef3729d65e197e7e971d851cd` matched. Eight distinct TARGET paths below and the new test file returned **404 on both A and integration**. No B overlap. All eight are existing read-only shadow candidate *report/evaluation* helpers, not the live quant-enforcement implementation. Move each exact existing SOURCE function BODY (not a copy or a rename-only change) to the specified new single Owner; SOURCE retains original public/private signature, annotations and a thin delegation wrapper. Preserve output bytes/order, dict/list identity where relevant, exception types, call-time monkeypatch, generator laziness. TARGET never imports SOURCE; use keyword-only `facade` for names looked up from SOURCE globals and SOURCE passes `sys.modules[__name__]` (import sys under collision-free alias if needed). For pure functions without module globals, do not add unnecessary facade. Import annotations in Owner under `from __future__ import annotations`, avoid evaluating `facade.*` in annotations. Do not change any callers unless a verified thin-wrapper/monkeypatch compatibility defect requires a narrowly scoped test-only fix.

**Safety:** fake in-memory inputs and TemporaryDirectory only; never invoke actual shadow pipeline, entry enforcement, real reports, broker/order/Guard/Step5C/UEF/RunLab, live network, operational State/DB, runtime/deploy or real CLI. No trading policy change. Use scoped normal `python -m unittest tests/test_p15_rf035_19h_quant_shadow_owners.py -v` (or scoped pytest) **exit0** after all items, with 8 per-item golden preimage→wrapper→Owner parity checks, negative/exception checks, AST actual BODY removal/thin-wrapper check and post-import facade monkeypatch seams. `python -m py_compile` on SOURCE and all eight TARGET modules before normal test. Each item below names the exact test case and input→expected; make actual test implementations in the one new test file, not placeholder assertions. Preserve baseline golden results from original source blob. Report any existing unrelated failures separately, never invent PASS. Git commit/push only A code+test on `work/p15-a-reporter-pure-20261021`, non-force, re-fetch A remote HEAD and SOURCE/8 Owners/test blobs; Git authentication failure is PUSH_BLOCKED only (continue remaining safe items). C04 integration and C05 G1/G2/G3/DONE are separate, not A/C03 duties.

**Allowed changed files:** `libs/reporting/quant_shadow_candidate_evaluation.py`, exactly the eight new `libs/reporting/quant_shadow_*_projection.py` TARGET paths below, and `tests/test_p15_rf035_19h_quant_shadow_owners.py`. Do not touch the six FUTURE RESERVE targets.

## A1 | RF-035 | Owner=CLAUDE_A | SOURCE=libs/reporting/quant_shadow_candidate_evaluation.py | SOURCE_BLOB=c46916f178b600cef3729d65e197e7e971d851cd | SOURCE::_bool @ L32
**TARGET:** `libs/reporting/quant_shadow_scalar_projection.py::_bool` (NEW, A-exclusive; 404 A/integration). **MOVE actual BODY exactly:**
```python
def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}
```
**Wrapper / callers / monkeypatch:** pure builtin conversion, no facade required; retain bool-before-number precedence. Keep SOURCE original signature as thin wrapper delegating to `libs/reporting/quant_shadow_scalar_projection.py::_bool`; no duplicate computation, no TARGET→SOURCE import, preserve preexisting call sites and error behavior.
**Normal targeted test:** `test_a1_bool` in `tests/test_p15_rf035_19h_quant_shadow_owners.py`. Input→expected: True→True; 'YES'→True; 'off'→False; 0→False. Compare original-preimage golden with SOURCE wrapper and TARGET; negative/error and call-time patch where applicable, AST thin wrapper; fake/temp only. **Blocked:** record exact reason/status, then continue A2.

## A2 | RF-035 | Owner=CLAUDE_A | SOURCE=libs/reporting/quant_shadow_candidate_evaluation.py | SOURCE_BLOB=c46916f178b600cef3729d65e197e7e971d851cd | SOURCE::_iter_days @ L51
**TARGET:** `libs/reporting/quant_shadow_day_projection.py::_iter_days` (NEW, A-exclusive; 404 A/integration). **MOVE actual BODY exactly:**
```python
def _iter_days(start: str, end: str) -> Iterable[str]:
    start_date = date.fromisoformat(str(start)[:10])
    end_date = date.fromisoformat(str(end)[:10])
    current = start_date
    while current <= end_date:
        yield current.isoformat()
        current += timedelta(days=1)
```
**Wrapper / callers / monkeypatch:** date/timedelta through call-time facade; SOURCE generator wrapper MUST use `yield from Owner._iter_days(...,facade=sys.modules[__name__])`, never `return Owner...`; retain laziness/ValueError. Keep SOURCE original signature as thin wrapper delegating to `libs/reporting/quant_shadow_day_projection.py::_iter_days`; no duplicate computation, no TARGET→SOURCE import, preserve preexisting call sites and error behavior.
**Normal targeted test:** `test_a2_iter_days` in `tests/test_p15_rf035_19h_quant_shadow_owners.py`. Input→expected: '2026-10-30'..'2026-10-31'→['2026-10-30','2026-10-31']; reversed range→[]; malformed date→ValueError. Compare original-preimage golden with SOURCE wrapper and TARGET; negative/error and call-time patch where applicable, AST thin wrapper; fake/temp only. **Blocked:** record exact reason/status, then continue A3.

## A3 | RF-035 | Owner=CLAUDE_A | SOURCE=libs/reporting/quant_shadow_candidate_evaluation.py | SOURCE_BLOB=c46916f178b600cef3729d65e197e7e971d851cd | SOURCE::_top_counter @ L261
**TARGET:** `libs/reporting/quant_shadow_counter_projection.py::_top_counter` (NEW, A-exclusive; 404 A/integration). **MOVE actual BODY exactly:**
```python
def _top_counter(counter: Counter[str], *, limit: int = 8) -> List[Dict[str, Any]]:
    return [
        {"name": name, "count": count}
        for name, count in counter.most_common(limit)
        if name
    ]
```
**Wrapper / callers / monkeypatch:** pure Counter input; no facade required; preserve most_common tie order and list/dict identity semantics. Keep SOURCE original signature as thin wrapper delegating to `libs/reporting/quant_shadow_counter_projection.py::_top_counter`; no duplicate computation, no TARGET→SOURCE import, preserve preexisting call sites and error behavior.
**Normal targeted test:** `test_a3_top_counter` in `tests/test_p15_rf035_19h_quant_shadow_owners.py`. Input→expected: Counter({'a':2,'b':1}),limit=1→[{'name':'a','count':2}]; empty→[]. Compare original-preimage golden with SOURCE wrapper and TARGET; negative/error and call-time patch where applicable, AST thin wrapper; fake/temp only. **Blocked:** record exact reason/status, then continue A4.

## A4 | RF-035 | Owner=CLAUDE_A | SOURCE=libs/reporting/quant_shadow_candidate_evaluation.py | SOURCE_BLOB=c46916f178b600cef3729d65e197e7e971d851cd | SOURCE::_row_blockers @ L269
**TARGET:** `libs/reporting/quant_shadow_blocker_projection.py::_row_blockers` (NEW, A-exclusive; 404 A/integration). **MOVE actual BODY exactly:**
```python
def _row_blockers(row: Mapping[str, Any]) -> List[str]:
    blockers: List[str] = []
    for value in (row.get("blockers"),):
        if isinstance(value, list):
            blockers.extend(_text(item) for item in value if _text(item))
    decision = row.get("entry_quant_decision")
    if isinstance(decision, Mapping):
        value = decision.get("blockers")
        if isinstance(value, list):
            blockers.extend(_text(item) for item in value if _text(item))
    return blockers
```
**Wrapper / callers / monkeypatch:** resolve `_text` and `Mapping` through call-time facade, preserve nested blocker order/duplicates and repeated `_text` calls. Keep SOURCE original signature as thin wrapper delegating to `libs/reporting/quant_shadow_blocker_projection.py::_row_blockers`; no duplicate computation, no TARGET→SOURCE import, preserve preexisting call sites and error behavior.
**Normal targeted test:** `test_a4_row_blockers` in `tests/test_p15_rf035_19h_quant_shadow_owners.py`. Input→expected: {'blockers':['a','']}→['a']; {'entry_quant_decision':{'blockers':['b','b']}}→['b','b']. Compare original-preimage golden with SOURCE wrapper and TARGET; negative/error and call-time patch where applicable, AST thin wrapper; fake/temp only. **Blocked:** record exact reason/status, then continue A5.

## A5 | RF-035 | Owner=CLAUDE_A | SOURCE=libs/reporting/quant_shadow_candidate_evaluation.py | SOURCE_BLOB=c46916f178b600cef3729d65e197e7e971d851cd | SOURCE::_count_reason @ L393
**TARGET:** `libs/reporting/quant_shadow_reason_projection.py::_count_reason` (NEW, A-exclusive; 404 A/integration). **MOVE actual BODY exactly:**
```python
def _count_reason(candidates: Sequence[Mapping[str, Any]], names: set[str]) -> int:
    total = 0
    for row in candidates:
        reason = _text(row.get("reason"))
        primary = _text(row.get("primary_failure_axis"))
        cost_floor = _cost_floor_state(row)
        if reason in names or primary in names or cost_floor in names:
            total += 1
            continue
        blockers = _row_blockers(row)
        if any(blocker in names for blocker in blockers):
            total += 1
    return total
```
**Wrapper / callers / monkeypatch:** resolve `_text`, `_cost_floor_state`, `_row_blockers` via call-time facade; preserve early-continue and per-row counting once. Keep SOURCE original signature as thin wrapper delegating to `libs/reporting/quant_shadow_reason_projection.py::_count_reason`; no duplicate computation, no TARGET→SOURCE import, preserve preexisting call sites and error behavior.
**Normal targeted test:** `test_a5_count_reason` in `tests/test_p15_rf035_19h_quant_shadow_owners.py`. Input→expected: [{'reason':'bad'}],{'bad'}→1; [],{'bad'}→0; nested blocker matching counts once. Compare original-preimage golden with SOURCE wrapper and TARGET; negative/error and call-time patch where applicable, AST thin wrapper; fake/temp only. **Blocked:** record exact reason/status, then continue A6.

## A6 | RF-035 | Owner=CLAUDE_A | SOURCE=libs/reporting/quant_shadow_candidate_evaluation.py | SOURCE_BLOB=c46916f178b600cef3729d65e197e7e971d851cd | SOURCE::_runner_up_risk_count @ L408
**TARGET:** `libs/reporting/quant_shadow_runnerup_projection.py::_runner_up_risk_count` (NEW, A-exclusive; 404 A/integration). **MOVE actual BODY exactly:**
```python
def _runner_up_risk_count(candidates: Sequence[Mapping[str, Any]]) -> int:
    total = 0
    for row in candidates:
        if _text(row.get("shadow_role")) != "runner_up_evaluated":
            continue
        if _bool(row.get("would_enter")):
            total += 1
            continue
        if _bool(row.get("runner_up_quality_blocked")) or _bool(row.get("weak_fallback_blocked")):
            total += 1
            continue
        reason = _text(row.get("reason"))
        if reason in {"runner_up_quality_gate_failed", "weak_fallback_pullback"}:
            total += 1
    return total
```
**Wrapper / callers / monkeypatch:** resolve `_text`, `_bool` via call-time facade; preserve ordered early-continues, role gate and duplicate-free per-row count. Keep SOURCE original signature as thin wrapper delegating to `libs/reporting/quant_shadow_runnerup_projection.py::_runner_up_risk_count`; no duplicate computation, no TARGET→SOURCE import, preserve preexisting call sites and error behavior.
**Normal targeted test:** `test_a6_runner_up_risk_count` in `tests/test_p15_rf035_19h_quant_shadow_owners.py`. Input→expected: [{'shadow_role':'runner_up_evaluated','would_enter':True}]→1; [{'shadow_role':'other','would_enter':True}]→0. Compare original-preimage golden with SOURCE wrapper and TARGET; negative/error and call-time patch where applicable, AST thin wrapper; fake/temp only. **Blocked:** record exact reason/status, then continue A7.

## A7 | RF-035 | Owner=CLAUDE_A | SOURCE=libs/reporting/quant_shadow_candidate_evaluation.py | SOURCE_BLOB=c46916f178b600cef3729d65e197e7e971d851cd | SOURCE::_mean @ L561
**TARGET:** `libs/reporting/quant_shadow_mean_projection.py::_mean` (NEW, A-exclusive; 404 A/integration). **MOVE actual BODY exactly:**
```python
def _mean(values: Sequence[float]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    if not clean:
        return None
    return round(sum(clean) / float(len(clean)), 4)
```
**Wrapper / callers / monkeypatch:** pure float/sum/round; no facade; retain None filtering and float conversion exceptions. Keep SOURCE original signature as thin wrapper delegating to `libs/reporting/quant_shadow_mean_projection.py::_mean`; no duplicate computation, no TARGET→SOURCE import, preserve preexisting call sites and error behavior.
**Normal targeted test:** `test_a7_mean` in `tests/test_p15_rf035_19h_quant_shadow_owners.py`. Input→expected: []→None; [1.0,None,3.0]→2.0; ['bad']→ValueError. Compare original-preimage golden with SOURCE wrapper and TARGET; negative/error and call-time patch where applicable, AST thin wrapper; fake/temp only. **Blocked:** record exact reason/status, then continue A8.

## A8 | RF-035 | Owner=CLAUDE_A | SOURCE=libs/reporting/quant_shadow_candidate_evaluation.py | SOURCE_BLOB=c46916f178b600cef3729d65e197e7e971d851cd | SOURCE::_scorecard_return_signal @ L685
**TARGET:** `libs/reporting/quant_shadow_scorecard_signal_projection.py::_scorecard_return_signal` (NEW, A-exclusive; 404 A/integration). **MOVE actual BODY exactly:**
```python
def _scorecard_return_signal(row: Mapping[str, Any]) -> float | None:
    for key in ("avg_return_15m_pct", "avg_return_5m_pct", "avg_return_30m_pct", "avg_return_3m_pct"):
        value = row.get(key)
        if value not in (None, ""):
            try:
                return float(value)
            except Exception:
                continue
    return None
```
**Wrapper / callers / monkeypatch:** pure mapping/float conversion; no facade; retain key priority and fallback after ValueError. Keep SOURCE original signature as thin wrapper delegating to `libs/reporting/quant_shadow_scorecard_signal_projection.py::_scorecard_return_signal`; no duplicate computation, no TARGET→SOURCE import, preserve preexisting call sites and error behavior.
**Normal targeted test:** `test_a8_scorecard_return_signal` in `tests/test_p15_rf035_19h_quant_shadow_owners.py`. Input→expected: {'avg_return_15m_pct':'0.2'}→0.2; {'avg_return_15m_pct':'bad','avg_return_5m_pct':'0.4'}→0.4; {}→None. Compare original-preimage golden with SOURCE wrapper and TARGET; negative/error and call-time patch where applicable, AST thin wrapper; fake/temp only. **Blocked:** record exact reason/status, then continue report/push.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY, NOT EXECUTABLE
Six additional RF-035 Claude A-exclusive SOURCE BODY candidates below were independently inspected on A and integration at blob `c46916f178b600cef3729d65e197e7e971d851cd`; each new TARGET was 404 on both refs. They are disjoint from A1–A8 and B. **Not authorized for implementation without new C03 order**. A1–A8 will alter this same SOURCE blob, so C03 must recheck current actor HEAD/blob and TARGET absence before any promotion.

### R1 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_cost_floor_state` @ L282 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd`
**TARGET:** `libs/reporting/quant_shadow_cost_floor_projection.py::_cost_floor_state` (404 A/integration, A-exclusive). **Verified BODY (design only):**
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
**Safety/patch:** read-only shadow reporting/evaluation, no live effects; _text/Mapping late-bound via facade; thin SOURCE wrapper, no duplicated BODY, preserve call-time monkeypatch. **Future targeted normal test input→expected:** {'entry_quant_cost_floor_state':'safe'}→'safe'; {}→''; preimage golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, recheck HEAD/blob/target before promotion.

### R2 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_entry_quant_decision` @ L301 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd`
**TARGET:** `libs/reporting/quant_shadow_entry_decision_projection.py::_entry_quant_decision` (404 A/integration, A-exclusive). **Verified BODY (design only):**
```python
def _entry_quant_decision(row: Mapping[str, Any]) -> str:
    decision = row.get("entry_quant_decision")
    if isinstance(decision, Mapping):
        return _text(decision.get("decision"))
    return ""
```
**Safety/patch:** read-only shadow reporting/evaluation, no live effects; _text/Mapping late-bound via facade; thin SOURCE wrapper, no duplicated BODY, preserve call-time monkeypatch. **Future targeted normal test input→expected:** {'entry_quant_decision':{'decision':'entry_ready'}}→'entry_ready'; {}→''; preimage golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, recheck HEAD/blob/target before promotion.

### R3 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_tactic_id` @ L308 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd`
**TARGET:** `libs/reporting/quant_shadow_tactic_projection.py::_tactic_id` (404 A/integration, A-exclusive). **Verified BODY (design only):**
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
**Safety/patch:** read-only shadow reporting/evaluation, no live effects; _text/Mapping late-bound via facade; thin SOURCE wrapper, no duplicated BODY, preserve call-time monkeypatch. **Future targeted normal test input→expected:** {'quant_tactic_id':'T1'}→'T1'; {'entry_quant_decision':{'tactic_id':'T2'}}→'T2'; preimage golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, recheck HEAD/blob/target before promotion.

### R4 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_tactic_suitability_tier` @ L323 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd`
**TARGET:** `libs/reporting/quant_shadow_tactic_tier_projection.py::_tactic_suitability_tier` (404 A/integration, A-exclusive). **Verified BODY (design only):**
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
**Safety/patch:** read-only shadow reporting/evaluation, no live effects; _text/Mapping late-bound via facade; thin SOURCE wrapper, no duplicated BODY, preserve call-time monkeypatch. **Future targeted normal test input→expected:** {'tactic_suitability_tier':'high'}→'high'; {}→''; preimage golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, recheck HEAD/blob/target before promotion.

### R5 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_forward_base` @ L337 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd`
**TARGET:** `libs/reporting/quant_shadow_forward_base_projection.py::_forward_base` (404 A/integration, A-exclusive). **Verified BODY (design only):**
```python
def _forward_base(row: Mapping[str, Any]) -> Dict[str, Any]:
    base = row.get("shadow_forward_base")
    return dict(base) if isinstance(base, Mapping) else {}
```
**Safety/patch:** read-only shadow reporting/evaluation, no live effects; Mapping late-bound via facade; preserve dict copy; thin SOURCE wrapper, no duplicated BODY, preserve call-time monkeypatch. **Future targeted normal test input→expected:** {'shadow_forward_base':{'x':1}}→{'x':1}; {}→{}; preimage golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, recheck HEAD/blob/target before promotion.

### R6 | RF-035 | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_forward_outcome` @ L342 | BLOB=`c46916f178b600cef3729d65e197e7e971d851cd`
**TARGET:** `libs/reporting/quant_shadow_forward_outcome_projection.py::_forward_outcome` (404 A/integration, A-exclusive). **Verified BODY (design only):**
```python
def _forward_outcome(row: Mapping[str, Any]) -> Dict[str, Any]:
    outcome = row.get("shadow_forward_outcome")
    return dict(outcome) if isinstance(outcome, Mapping) else {}
```
**Safety/patch:** read-only shadow reporting/evaluation, no live effects; Mapping late-bound via facade; preserve dict copy; thin SOURCE wrapper, no duplicated BODY, preserve call-time monkeypatch. **Future targeted normal test input→expected:** {'shadow_forward_outcome':{'available':True}}→{'available':True}; {}→{}; preimage golden/wrapper/Owner and exception parity. **RESERVE_VERIFIED DESIGN ONLY**, recheck HEAD/blob/target before promotion.

## REPORT / PUSH
#11: `ORDER_ID=A-20261031-19 | CANONICAL_HEAD | ORDER_BLOB | A_REMOTE_BEFORE→AFTER | A1..A8 ITEM_STATUS | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | MOVED_FUNCTIONS | SOURCE_LOC_BEFORE_AFTER | FIRST_BLOCKER | NEXT_SAFE_ITEM | PUSH_REMOTE_SHA/PUSH_BLOCKED | START_KST/END_KST/ELAPSED_MIN`. Measure times, do not infer. Only actual remote code+test G1/G2; C03 documentation update is not G1/G2/G3, C04 G3 and C05 DONE separate. RunLab remains SAFETY_HOLD.
