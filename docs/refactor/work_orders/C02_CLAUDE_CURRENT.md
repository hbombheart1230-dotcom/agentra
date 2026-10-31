# C02 — Claude A | A-20261031-23 | FAST-3 NEW 8 verified SOURCE BODY MOVEs

**CANONICAL_HEAD_AT_DESIGN:** `4cf9e0893c2f2a1993d96f89601a37f3a9618404` | **OLD_ORDER_BLOB:** `829d37c6ae8a35342a76e6dbeecd21e6b00d5908` | **A_REMOTE_HEAD:** `a71a29dec11665954b4df9bef263198217a16ad0` | **SOURCE_BLOB:** `92a77e5552ebcd0777db52c842bd500e80b5ae00` | **OWNER:** RF-035 CLAUDE_A, exclusive `libs/reporting` source/target only.

**C03 verified delta:** #11 comment 6543895966 reports A-22 A1–A8 REMOTE_DONE, normal unittest 8/8 exit0 and normal non-force push `a71a29de`; source `quant_shadow_candidate_evaluation.py` changed `c014b371→92a77e55`, 1207→1015 LOC. Re-fetched A and integration same source blob `92a77e5552ebcd0777db52c842bd500e80b5ae00`; old A-22 eight targets exist and are NOT new work. #12 6543760151 B-21 B1 REMOTE_DONE at `444cd862`, B2–B8 remain 7 safe pending, C01 retained with B1 completion correction. #32 no new comment since 6520075820; runtime Exited(255), RUN_SOURCE_SHA=UNKNOWN, operation HOLD.

**One-file execution contract:** Read THIS C02 only and exact code/test paths below; no D00/RF/queue/C03/HANDOFF/self-selection. Pin CANONICAL_HEAD, ORDER_BLOB, A_REMOTE_SHA, ORDER_ID on start; do all A1–A8 or individually BLOCKED and continue safe next item. Do not redo A-22 or previous PASS/KEEP. Only A branch `work/p15-a-reporter-pure-20261021` code/test; no docs/RF/STATUS/C04/C05/B branch. Source BODY must leave original function as thin same-signature facade wrapper, move actual computation to one exclusive new Owner; Owner MUST NOT import SOURCE. Preserve import/caller signatures, original exception/order, generator/identity semantics, call-time monkeypatch via `facade=sys.modules[__name__]` where needed. Capture original-preimage golden before mutation; compare original vs wrapper vs direct Owner for each fixture including negative/error, post-import monkeypatch, and AST body removal. No duplicate BODY, rename-only, KEEP-only, or test-only work.

**Safety:** RF-035 offline reporting/diagnostics only, fake dict/TemporaryDirectory. No real pipeline execution, actual report/state/db writes, network, broker/order/Guard/Step5C/UEF/RunLab effects, operational environment, CI/frozen oracle, force push. Even guard-named functions below only compute read-only diagnostic values; never change enforcement or policy. No full peer/-O/hosted CI requirement. A-23 tests MUST be new `tests/test_p15_rf035_23h_quant_shadow_owners.py` (verified absent A/integration); preserve all earlier suites.

**Targeted normal G2:** `python -m py_compile libs/reporting/quant_shadow_candidate_evaluation.py libs/reporting/quant_shadow_*_projection.py` (expand only actual eight new targets) and `python -m unittest tests/test_p15_rf035_23h_quant_shadow_owners.py -v` exit0 with eight named tests. If glob pulls unrelated files, use explicit paths instead. Commit only source + eight targets + that one test to A branch, non-force; re-fetch remote HEAD and all source/target/test blob SHAs, report per-item `IMPLEMENTED/TEST_BLOCKED/PUSH_BLOCKED/SAFETY_BLOCKED/NOT_RUN`, original/after LOC, golden parity, normal exit and exact remote SHA in #11. Git auth blocks push only; continue other safe items. C04 G3 integration and C05 RF DONE are separate, NOT part of this C03 document supply.

**Allowed paths:** `libs/reporting/quant_shadow_candidate_evaluation.py`; `libs/reporting/quant_shadow_text_projection.py`; `libs/reporting/quant_shadow_json_projection.py`; `libs/reporting/quant_shadow_day_paths_projection.py`; `libs/reporting/quant_shadow_drop_q9_projection.py`; `libs/reporting/quant_shadow_format_scorecard_projection.py`; `libs/reporting/quant_shadow_readiness_projection.py`; `libs/reporting/quant_shadow_root_projection.py`; `libs/reporting/quant_shadow_no_trade_scorecard_projection.py`; `tests/test_p15_rf035_23h_quant_shadow_owners.py`. No other code/test paths.

## A1 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_text` @ L60 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_text_projection.py::_text` — NEW, 404 A/integration, exclusive single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE, not copy/KEEP):**
```python
def _text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() in {"", "-", "none", "null", "unknown", "not_captured"} else text
```
**Thin wrapper / caller / monkeypatch:** Preserve exact original signature (including keyword-only and return type) and delegate to new Owner; use call-time `facade=sys.modules[__name__]` where relevant. Required seam: facade-free pure calculation. Owner must not import SOURCE. Preserve output, exception, identity and original call-site monkeypatch parity. **Safety:** pure scalar; preserve str(value or '') conversion and empty-token set; no effect.
**Normal targeted test:** `test_a1_text` in `tests/test_p15_rf035_23h_quant_shadow_owners.py`. Input→expected: ' unknown ' → ''; ' x ' → 'x'. Verify original-preimage golden vs wrapper vs Owner, negative/error, AST actual body removal. If BLOCKED report exact reason and **continue A2**.

## A2 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_read_json` @ L69 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_json_projection.py::_read_json` — NEW, 404 A/integration, exclusive single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE, not copy/KEEP):**
```python
def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
```
**Thin wrapper / caller / monkeypatch:** Preserve exact original signature (including keyword-only and return type) and delegate to new Owner; use call-time `facade=sys.modules[__name__]` where relevant. Required seam: facade.json. Owner must not import SOURCE. Preserve output, exception, identity and original call-site monkeypatch parity. **Safety:** read-only UTF-8 JSON from temporary path; facade.json bound at call time; no real report file.
**Normal targeted test:** `test_a2_read_json` in `tests/test_p15_rf035_23h_quant_shadow_owners.py`. Input→expected: TemporaryDirectory valid JSON {'x':1} → {'x':1}; missing file → None. Verify original-preimage golden vs wrapper vs Owner, negative/error, AST actual body removal. If BLOCKED report exact reason and **continue A3**.

## A3 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_json_paths_for_day` @ L84 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_day_paths_projection.py::_json_paths_for_day` — NEW, 404 A/integration, exclusive single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE, not copy/KEEP):**
```python
def _json_paths_for_day(root: Path, day: str) -> List[Path]:
    day_dir = root / str(day)[:10]
    if not day_dir.exists():
        return []
    return sorted(path for path in day_dir.glob("*.json") if path.name != "latest.json")
```
**Thin wrapper / caller / monkeypatch:** Preserve exact original signature (including keyword-only and return type) and delegate to new Owner; use call-time `facade=sys.modules[__name__]` where relevant. Required seam: facade.Path where used. Owner must not import SOURCE. Preserve output, exception, identity and original call-site monkeypatch parity. **Safety:** read-only temporary glob; preserve sort and latest.json exclusion; no real data.
**Normal targeted test:** `test_a3_json_paths_for_day` in `tests/test_p15_rf035_23h_quant_shadow_owners.py`. Input→expected: temp root/2026-10-31/a.json and latest.json → [a.json]; missing day → []. Verify original-preimage golden vs wrapper vs Owner, negative/error, AST actual body removal. If BLOCKED report exact reason and **continue A4**.

## A4 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_drop_q9_row_keys` @ L184 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_drop_q9_projection.py::_drop_q9_row_keys` — NEW, 404 A/integration, exclusive single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE, not copy/KEEP):**
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
**Thin wrapper / caller / monkeypatch:** Preserve exact original signature (including keyword-only and return type) and delegate to new Owner; use call-time `facade=sys.modules[__name__]` where relevant. Required seam: no globals. Owner must not import SOURCE. Preserve output, exception, identity and original call-site monkeypatch parity. **Safety:** mutate ONLY supplied in-memory fixture; preserve object identity and nested row mutation; never operational State.
**Normal targeted test:** `test_a4_drop_q9_row_keys` in `tests/test_p15_rf035_23h_quant_shadow_owners.py`. Input→expected: payload={'q9_decision_candidates':[{'x':1,'y':2}]} drop=['x'] → identical payload object, row={'y':2}; drop=None → unchanged. Verify original-preimage golden vs wrapper vs Owner, negative/error, AST actual body removal. If BLOCKED report exact reason and **continue A5**.

## A5 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_format_scorecard_rows` @ L800 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_format_scorecard_projection.py::_format_scorecard_rows` — NEW, 404 A/integration, exclusive single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE, not copy/KEEP):**
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
**Thin wrapper / caller / monkeypatch:** Preserve exact original signature (including keyword-only and return type) and delegate to new Owner; use call-time `facade=sys.modules[__name__]` where relevant. Required seam: facade._text. Owner must not import SOURCE. Preserve output, exception, identity and original call-site monkeypatch parity. **Safety:** format-only; facade._text resolved at call time; no real output writes.
**Normal targeted test:** `test_a5_format_scorecard_rows` in `tests/test_p15_rf035_23h_quant_shadow_owners.py`. Input→expected: [] → 'none'; [{'name':'x','observed_count':2,'candidate_count':3,'avg_return_5m_pct':1.0}] → 'x (2/3, +5m 1.0000%)'; malformed numeric preserves exception. Verify original-preimage golden vs wrapper vs Owner, negative/error, AST actual body removal. If BLOCKED report exact reason and **continue A6**.

## A6 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_shadow_readiness` @ L610 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_readiness_projection.py::_shadow_readiness` — NEW, 404 A/integration, exclusive single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE, not copy/KEEP):**
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
**Thin wrapper / caller / monkeypatch:** Preserve exact original signature (including keyword-only and return type) and delegate to new Owner; use call-time `facade=sys.modules[__name__]` where relevant. Required seam: facade._bool/_text and three constants. Owner must not import SOURCE. Preserve output, exception, identity and original call-site monkeypatch parity. **Safety:** read-only diagnostic summary only; facade._bool/_text/TRUSTED_FORWARD_MIN_COUNT/PROMOTION_CANDIDATE_MIN_OBSERVED/TRUSTED_FORWARD_MIN_COVERAGE resolved at call time; no Guard or trading changes.
**Normal targeted test:** `test_a6_shadow_readiness` in `tests/test_p15_rf035_23h_quant_shadow_owners.py`. Input→expected: ([], {}) → status='hold_no_shadow_candidates', action='hold', evaluated_ratio=0.0; no live gating. Verify original-preimage golden vs wrapper vs Owner, negative/error, AST actual body removal. If BLOCKED report exact reason and **continue A7**.

## A7 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::shadow_candidate_root_for_reports` @ L76 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_root_projection.py::shadow_candidate_root_for_reports` — NEW, 404 A/integration, exclusive single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE, not copy/KEEP):**
```python
def shadow_candidate_root_for_reports(reports_root: Path) -> Path:
    return Path(reports_root).parent / "data" / "logs" / "quant_shadow_candidates"
```
**Thin wrapper / caller / monkeypatch:** Preserve exact original signature (including keyword-only and return type) and delegate to new Owner; use call-time `facade=sys.modules[__name__]` where relevant. Required seam: facade.Path. Owner must not import SOURCE. Preserve output, exception, identity and original call-site monkeypatch parity. **Safety:** pure path projection, no mkdir/read/write; facade.Path resolved at call time.
**Normal targeted test:** `test_a7_shadow_candidate_root_for_reports` in `tests/test_p15_rf035_23h_quant_shadow_owners.py`. Input→expected: reports_root=Path('/tmp/fake/reports') → Path('/tmp/fake/data/logs/quant_shadow_candidates') (platform-safe parent comparison). Verify original-preimage golden vs wrapper vs Owner, negative/error, AST actual body removal. If BLOCKED report exact reason and **continue A8**.

## A8 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_no_trade_scorecard` @ L421 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_no_trade_scorecard_projection.py::_no_trade_scorecard` — NEW, 404 A/integration, exclusive single Owner.
**Exact calculation BODY to MOVE (remove from SOURCE, not copy/KEEP):**
```python
def _no_trade_scorecard(
    *,
    candidates: Sequence[Mapping[str, Any]],
    entry_lane_forward_outcomes: Mapping[str, Any],
    would_enter_count: int,
    opening_probe_would_enter: int,
    largecap_probe_would_enter: int,
) -> Dict[str, Any]:
    candidate_count = len(candidates)
    outcome_count = sum(1 for row in candidates if _bool(_forward_outcome(row).get("available")))
    coverage = float(outcome_count) / float(candidate_count) if candidate_count else 0.0
    lane_rows = (
        list(entry_lane_forward_outcomes.get("by_primary_lane") or [])
        if isinstance(entry_lane_forward_outcomes, Mapping)
        else []
    )
    lane_subtype_rows = (
        list(entry_lane_forward_outcomes.get("by_lane_subtype") or [])
        if isinstance(entry_lane_forward_outcomes, Mapping)
        else []
    )
    combined_rows = [row for row in lane_rows + lane_subtype_rows if isinstance(row, Mapping)]
    missed = _scorecard_rows(combined_rows, mode="missed", limit=6)
    blocked = _scorecard_rows(combined_rows, mode="blocked", limit=6)
    watchlist = _named_forward_rows(
        lane_subtype_rows,
        {
            "pullback_quality:failed_pullback",
            "vwap_reclaim:reclaim_in_progress_with_improving_volume",
        },
    )
    promotion_ready_watchlist = [
        row for row in watchlist if _text(row.get("review_state")) == "promotion_watch"
    ]
    if candidate_count <= 0:
        status = "no_shadow_data"
        verdict = "no shadow candidates were collected"
    elif would_enter_count > 0 or opening_probe_would_enter > 0 or largecap_probe_would_enter > 0:
        status = "trade_candidates_available"
        verdict = "shadow candidates had would-enter paths; compare against actual execution"
    elif missed and blocked:
        status = "mixed_no_trade_day"
        verdict = "major weak groups were blocked, but selected subtypes show missed-opportunity signals"
    elif missed:
        status = "possible_over_blocking"
        verdict = "no would-enter candidates, but forward outcomes show positive missed-opportunity groups"
    elif blocked:
        status = "correctly_blocked"
        verdict = "no would-enter candidates and blocked groups underperformed in forward outcomes"
    else:
        status = "inconclusive_no_trade_day"
        verdict = "no would-enter candidates; forward evidence is not decisive"
    evidence_quality = (
        "high"
        if outcome_count >= TRUSTED_FORWARD_MIN_COUNT and coverage >= TRUSTED_FORWARD_MIN_COVERAGE
        else "medium"
        if outcome_count >= 30
        else "low"
    )
    return {
        "behavior_effect": "evaluation_only",
        "status": status,
        "verdict": verdict,
        "candidate_count": candidate_count,
        "would_enter_count": int(would_enter_count),
        "opening_momentum_probe_would_enter_count": int(opening_probe_would_enter),
        "opening_largecap_surge_would_enter_count": int(largecap_probe_would_enter),
        "forward_outcome_available_count": int(outcome_count),
        "forward_outcome_coverage": coverage,
        "evidence_quality": evidence_quality,
        "correctly_blocked_signals": blocked,
        "missed_opportunity_candidates": missed,
        "promotion_watchlist": watchlist,
        "next_review_action": (
            "review_promotion_watchlist_for_probe_candidate"
            if promotion_ready_watchlist
            else "collect_repeatability_before_promotion_review"
            if missed or watchlist
            else "retain_current_guards_and_continue_observation"
        ),
    }
```
**Thin wrapper / caller / monkeypatch:** Preserve exact original signature (including keyword-only and return type) and delegate to new Owner; use call-time `facade=sys.modules[__name__]` where relevant. Required seam: facade._bool/_forward_outcome/_scorecard_rows/_named_forward_rows/_text/constants. Owner must not import SOURCE. Preserve output, exception, identity and original call-site monkeypatch parity. **Safety:** report-only evaluation; facade._bool/_forward_outcome/_scorecard_rows/_named_forward_rows/_text and TRUSTED_FORWARD_MIN_COUNT/TRUSTED_FORWARD_MIN_COVERAGE at call time; no actual Guard or order effect.
**Normal targeted test:** `test_a8_no_trade_scorecard` in `tests/test_p15_rf035_23h_quant_shadow_owners.py`. Input→expected: candidates=[],entry_lane_forward_outcomes={},would_enter_count=0,opening_probe_would_enter=0,largecap_probe_would_enter=0 → status='no_shadow_data',candidate_count=0,behavior_effect='evaluation_only',forward_outcome_coverage=0.0. Verify original-preimage golden vs wrapper vs Owner, negative/error, AST actual body removal. If BLOCKED report exact reason and **continue remaining safe test/push**.

## FUTURE RESERVE — VERIFIED 6/6, DESIGN ONLY, NOT EXECUTABLE IN A-23
Each RF-035 CLAUDE_A SOURCE body below was inspected at current A/integration blob `92a77e5552ebcd0777db52c842bd500e80b5ae00`; distinct target filenames returned 404 on both A and integration. These are not executable instructions, and require fresh source/target recheck plus a future C03 order. They are not counted as A-23 new work. Only fake/temp/read-only; no operational guard/promotion effects.

### R1 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_q9_windows_by_id` @ L91 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_q9_windows_projection.py::_q9_windows_by_id` (404 A/integration, verified absent, design only).
**Actual existing BODY, NOT EXECUTABLE until newly issued:**
```python
def _q9_windows_by_id(reports_root: Path, day: str) -> Dict[str, Dict[str, Any]]:
    # `_augment_missing_q9_commander_candidate` reads only `commander_final` from a window, so
    # the ~120 MB windows file is streamed and reduced to that field (id -> {"commander_final"}).
    path = (
        Path(reports_root)
        / "operator_summary"
        / "daily"
        / str(day)[:10]
        / "q9_decision_windows.json"
    )
    out: Dict[str, Dict[str, Any]] = {}
    try:
        for row in iter_json_array(path, "windows", strict=True):
            if isinstance(row, Mapping) and str(row.get("decision_id") or ""):
                out[str(row.get("decision_id") or "")] = {"commander_final": row.get("commander_final")}
    except (OSError, ValueError):
        return {}
    return out
```
**Future targeted fixture:** fake iter_json_array yields {'decision_id':'d1','commander_final':{'decision':'hold'}} → {'d1':{'commander_final':{'decision':'hold'}}}; malformed fake OSError → {}. **Safety/wrapper/monkeypatch:** read-only fake stream; facade.iter_json_array/Mapping/Path; no actual 120MB file; preserve original same-signature thin wrapper, original golden and exceptions. Recheck SHA/target before issuance.

### R2 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_augment_missing_q9_commander_candidate` @ L111 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_q9_augment_projection.py::_augment_missing_q9_commander_candidate` (404 A/integration, verified absent, design only).
**Actual existing BODY, NOT EXECUTABLE until newly issued:**
```python
def _augment_missing_q9_commander_candidate(
    payload: Dict[str, Any],
    *,
    windows_by_id: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Any]:
    rows = [
        dict(row)
        for row in payload.get("q9_decision_candidates") or []
        if isinstance(row, Mapping)
    ]
    if any(str(row.get("q9_decision_role") or "") == "C_COMMANDER_FINAL" for row in rows):
        return payload
    decision_id = str(payload.get("q9_decision_id") or "").strip()
    window = windows_by_id.get(decision_id)
    if not isinstance(window, Mapping):
        return payload
    commander = window.get("commander_final")
    commander = commander if isinstance(commander, Mapping) else {}
    symbol = str(
        commander.get("selected_symbol")
        or commander.get("candidate_symbol")
        or ""
    ).strip()
    if not symbol:
        return payload
    source = next(
        (
            row
            for row in rows
            if str(row.get("symbol") or "") == symbol
            and str(row.get("q9_decision_role") or "")
            in {"B_STRATEGIST_RANKED", "A_SCANNER_CONTROL"}
        ),
        None,
    )
    if source is None:
        return payload
    commander_row = dict(source)
    commander_row.update(
        {
            "rank": 1,
            "q9_decision_role": "C_COMMANDER_FINAL",
            "q9_selected": False,
            "q9_commander_decision": str(commander.get("decision") or ""),
            "q9_commander_no_trade": bool(commander.get("no_trade")),
            "q9_backfill_source": "daily_q9_decision_window",
        }
    )
    payload["q9_decision_candidates"] = rows + [commander_row]
    return payload


# The only top-level payload keys the closeout-path consumers read (candidate
# evaluation, Q8 blocker review, strategist LLM evaluation). Everything else in
# a shadow payload -- chiefly `q9_decision_candidates`, ~65% of the bytes -- is
# dead weight for them. Closeout passes this to `keys=` so a full trading day
# is not held in memory (the 10-06 closeout was OOM-killed at the 1 GiB cap).
CANDIDATE_EVALUATION_PAYLOAD_KEYS: Tuple[str, ...] = ("candidates", "generated_at")

# Keys of each `q9_decision_candidates` row that are ~83% of its bytes and that the full-chain
# component review, the scanner-quality review and the cost-basis comparison never read
# (verified statically and with access-trapping values on real days -- see
# tests/test_closeout_memory_bounds.py). Those consumers pass `drop_q9_row_keys=` so a day of
# q9 rows is not held in full. Consumers that DO read them (stage-2 authority, episode scanner
# review, evaluation lens ...) must not use it.
Q9_ROW_KEYS_UNUSED_BY_FULL_CHAIN: Tuple[str, ...] = (
    "entry_lane_observation",
    "score_breakdown",
    "compact_feature_snapshot",
    "below_vwap_reclaim_observation",
)
```
**Future targeted fixture:** payload={} windows_by_id={} → same payload identity; synthetic ranked candidate+window → append one C_COMMANDER_FINAL with q9_selected=False. **Safety/wrapper/monkeypatch:** in-memory copy/append only; no execution or actual Commander; preserve original same-signature thin wrapper, original golden and exceptions. Recheck SHA/target before issuance.

### R3 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_evaluation_trust_gate` @ L504 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_trust_gate_projection.py::_evaluation_trust_gate` (404 A/integration, verified absent, design only).
**Actual existing BODY, NOT EXECUTABLE until newly issued:**
```python
def _evaluation_trust_gate(
    *,
    raw_candidate_count: int,
    deduped_candidate_count: int,
    trusted_forward_count: int,
    trusted_forward_coverage: float,
    no_trade_scorecard: Mapping[str, Any],
) -> Dict[str, Any]:
    watchlist = [
        row for row in list(no_trade_scorecard.get("promotion_watchlist") or []) if isinstance(row, Mapping)
    ]
    gate = build_q8_trust_gate(
        raw_candidate_count=raw_candidate_count,
        deduped_candidate_count=deduped_candidate_count,
        trusted_forward_count=trusted_forward_count,
        trusted_forward_coverage=trusted_forward_coverage,
        candidate_watchlist=watchlist,
    )
    promotion_ready = [
        row for row in watchlist if _text(row.get("review_state")) == "promotion_watch"
    ]
    return {
        "behavior_effect": "evaluation_only",
        **gate,
        "reasons": list(gate.get("block_reasons") or []),
        "raw_candidate_count": int(raw_candidate_count),
        "deduped_candidate_count": int(deduped_candidate_count),
        "promotion_ready_candidates": promotion_ready,
        "minimum_requirements": {
            **dict(gate.get("minimums") or {}),
            "candidate_avg_return_5m_pct": "> 0",
            "candidate_avg_return_15m_pct": "> 0",
        },
    }
```
**Future targeted fixture:** fake facade.build_q8_trust_gate returns {'block_reasons':['x'],'minimums':{}} → reasons=['x'], raw_candidate_count mirrors input. **Safety/wrapper/monkeypatch:** read-only diagnostic evaluation; no changes to trust-gate policy; facade.build_q8_trust_gate/_text/Mapping; preserve original same-signature thin wrapper, original golden and exceptions. Recheck SHA/target before issuance.

### R4 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::render_quant_shadow_candidate_evaluation_lines` @ L831 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_render_lines_projection.py::render_quant_shadow_candidate_evaluation_lines` (404 A/integration, verified absent, design only).
**Actual existing BODY, NOT EXECUTABLE until newly issued:**
```python
def render_quant_shadow_candidate_evaluation_lines(payload: Mapping[str, Any] | None) -> List[str]:
    evaluation = dict(payload or {})
    if not evaluation or int(evaluation.get("candidate_count") or 0) <= 0:
        return []
    lines = [
        "",
        "## Quant Shadow Candidates",
        "",
        "- Q8 shadow candidates: "
        f"{evaluation.get('candidate_count') or 0} candidates / "
        f"deduped {evaluation.get('deduped_candidate_count') or evaluation.get('candidate_count') or 0} / "
        f"duplicates {evaluation.get('duplicate_candidate_count') or 0} / "
        f"{evaluation.get('payload_count') or 0} payloads / "
        f"evaluated {evaluation.get('evaluated_count') or 0} / "
        f"would-enter {evaluation.get('would_enter_count') or 0} / "
        f"opening-probe {evaluation.get('opening_momentum_probe_would_enter_count') or 0} / "
        f"largecap-surge {evaluation.get('opening_largecap_surge_would_enter_count') or 0} / "
        f"guard-blocked {evaluation.get('guard_blocked_count') or 0} "
        f"(actionable {evaluation.get('actionable_guard_blocked_count') or 0})",
        f"- Q8 shadow forward base: {evaluation.get('forward_base_available_count') or 0}/"
        f"{evaluation.get('candidate_count') or 0} candidates have baseline minute price "
        f"(coverage {float(evaluation.get('forward_base_coverage') or 0.0):.1%})",
        f"- Q8 shadow forward outcome: {evaluation.get('forward_outcome_available_count') or 0}/"
        f"{evaluation.get('deduped_candidate_count') or evaluation.get('candidate_count') or 0} deduped candidates have "
        "at least one trusted forward checkpoint "
        f"(coverage {float(evaluation.get('forward_outcome_coverage') or 0.0):.1%})",
        f"- Roles: {_format_rows(list(evaluation.get('by_role') or []))}",
        f"- Reasons: {_format_rows(list(evaluation.get('by_reason') or []))}",
        f"- Tactics: {_format_rows(list(evaluation.get('by_tactic_id') or []))}",
        f"- Suitability: {_format_rows(list(evaluation.get('by_tactic_suitability_tier') or []))}",
        f"- Cost floor: {_format_rows(list(evaluation.get('by_cost_floor_state') or []))}",
        f"- Failure axis: {_format_rows(list(evaluation.get('by_primary_failure_axis') or []))}",
    ]
    trust_gate = (
        evaluation.get("evaluation_trust_gate")
        if isinstance(evaluation.get("evaluation_trust_gate"), Mapping)
        else {}
    )
    if trust_gate:
        lines += [
            "",
            "### Q8 Evaluation Trust Gate",
            "",
            "- Trust gate: "
            f"`{trust_gate.get('status') or 'unknown'}` / "
            f"promotion_allowed `{bool(trust_gate.get('promotion_allowed'))}`",
            "- Trust evidence: "
            f"raw {trust_gate.get('raw_candidate_count') or 0}, "
            f"deduped {trust_gate.get('deduped_candidate_count') or 0}, "
            f"duplicates {trust_gate.get('duplicate_count') or 0} "
            f"({float(trust_gate.get('duplicate_rate') or 0.0):.1%}), "
            f"trusted forward {trust_gate.get('trusted_forward_count') or 0} "
            f"({float(trust_gate.get('trusted_forward_coverage') or 0.0):.1%})",
            f"- Trust block reasons: {', '.join(str(x) for x in list(trust_gate.get('reasons') or [])) or 'none'}",
            "- Promotion-ready candidates: "
            f"{_format_scorecard_rows(list(trust_gate.get('promotion_ready_candidates') or []), limit=4)}",
        ]
    readiness = evaluation.get("shadow_readiness") if isinstance(evaluation.get("shadow_readiness"), Mapping) else {}
    if readiness:
        lines.append(
            "- Q8 shadow readiness: "
            f"`{readiness.get('status') or 'not_available'}` / "
            f"action `{readiness.get('action') or 'hold'}` / "
            f"scope `{readiness.get('promotion_scope') or 'none'}` / "
            f"sample {readiness.get('evaluated_count') or 0}/"
            f"{readiness.get('candidate_count') or 0}"
        )
    promotion = evaluation.get("promotion_candidate") if isinstance(evaluation.get("promotion_candidate"), Mapping) else {}
    if promotion:
        lines.append(
            "- Q8 promotion candidate: "
            f"{promotion.get('candidate') or 'hold'} / "
            f"confidence {promotion.get('confidence') or 'none'} / "
            f"{promotion.get('reason') or '-'} / "
            f"action {promotion.get('recommended_action') or 'hold'}"
        )
        if promotion.get("promotion_state"):
            lines.append(
                "- Q8 promotion state: "
                f"{promotion.get('promotion_state') or 'unknown'} / "
                f"effect {promotion.get('behavior_effect') or 'unknown'} / "
                f"guard {promotion.get('active_guard_reason') or '-'}"
            )
        counts = promotion.get("counts") if isinstance(promotion.get("counts"), Mapping) else {}
        if counts:
            lines.append(
                "- Q8 promotion counts: "
                f"cost-edge {counts.get('cost_edge') or 0}, "
                f"runner-up {counts.get('runner_up') or 0}, "
                f"entry-guard {counts.get('entry_guard') or 0}"
            )
    no_trade = evaluation.get("no_trade_scorecard") if isinstance(evaluation.get("no_trade_scorecard"), Mapping) else {}
    if no_trade:
        lines += [
            "",
            "### Q8 No-Trade Scorecard",
            "",
            "- No-trade scorecard: "
            f"`{no_trade.get('status') or 'unknown'}` / "
            f"evidence `{no_trade.get('evidence_quality') or 'unknown'}` / "
            f"forward {no_trade.get('forward_outcome_available_count') or 0}/"
            f"{no_trade.get('candidate_count') or 0} "
            f"({float(no_trade.get('forward_outcome_coverage') or 0.0):.1%})",
            f"- Verdict: {no_trade.get('verdict') or '-'}",
            "- Correctly blocked signals: "
            f"{_format_scorecard_rows(list(no_trade.get('correctly_blocked_signals') or []), limit=4)}",
            "- Missed-opportunity candidates: "
            f"{_format_scorecard_rows(list(no_trade.get('missed_opportunity_candidates') or []), limit=4)}",
            "- Promotion watchlist: "
            f"{_format_scorecard_rows(list(no_trade.get('promotion_watchlist') or []), limit=4)}",
            f"- Next review action: `{no_trade.get('next_review_action') or 'continue_observation'}`",
        ]
    opening_probe = evaluation.get("opening_momentum_probe") if isinstance(evaluation.get("opening_momentum_probe"), Mapping) else {}
    if opening_probe:
        lines += [
            "- Opening momentum probe shadow: "
            f"{opening_probe.get('would_enter_count') or 0}/"
            f"{opening_probe.get('candidate_count') or 0} would-probe "
            f"(observation only)",
            f"- Opening probe reasons: {_format_rows(list(opening_probe.get('by_reason') or []))}",
            f"- Opening probe symbols: {_format_rows(list(opening_probe.get('by_would_enter_symbol') or []))}",
        ]
        if opening_probe.get("zero_would_enter_explanation"):
            lines.append(f"- Opening probe zero-pass note: {opening_probe.get('zero_would_enter_explanation')}")
    largecap_probe = evaluation.get("opening_largecap_surge") if isinstance(evaluation.get("opening_largecap_surge"), Mapping) else {}
    if largecap_probe:
        lines += [
            "- Opening largecap surge shadow: "
            f"{largecap_probe.get('would_enter_count') or 0}/"
            f"{largecap_probe.get('candidate_count') or 0} would-probe "
            f"(observation only)",
            f"- Opening largecap reasons: {_format_rows(list(largecap_probe.get('by_reason') or []))}",
            f"- Opening largecap symbols: {_format_rows(list(largecap_probe.get('by_would_enter_symbol') or []))}",
        ]
        if largecap_probe.get("zero_would_enter_explanation"):
            lines.append(f"- Opening largecap zero-pass note: {largecap_probe.get('zero_would_enter_explanation')}")
    entry_shape = evaluation.get("entry_shape_diagnostics") if isinstance(evaluation.get("entry_shape_diagnostics"), Mapping) else {}
    if entry_shape:
        lines += [
            "- Entry shape diagnostics: "
            f"pullback/vwap blocked {entry_shape.get('pullback_or_vwap_blocked_count') or 0}, "
            f"breakout ready-like {entry_shape.get('breakout_ready_like_count') or 0}, "
            f"breakout not-ready {entry_shape.get('breakout_not_ready_count') or 0}",
            f"- Entry shapes: {_format_rows(list(entry_shape.get('by_shape') or []))}",
        ]
    entry_lane = (
        evaluation.get("entry_lane_observation")
        if isinstance(evaluation.get("entry_lane_observation"), Mapping)
        else {}
    )
    if entry_lane and int(entry_lane.get("candidate_count") or 0) > 0:
        lines += [
            "- Entry lane observation: "
            f"{entry_lane.get('candidate_count') or 0} candidates / "
            f"{_format_rows(list(entry_lane.get('by_primary_lane') or []), limit=8)}",
            f"- Entry lane subtypes: {_format_rows(list(entry_lane.get('by_lane_subtype') or []), limit=8)}",
            f"- Entry lane time buckets: {_format_rows(list(entry_lane.get('by_time_bucket') or []), limit=6)}",
            f"- Entry lane market rails: {_format_rows(list(entry_lane.get('by_market_regime_rail') or []), limit=6)}",
        ]
    lane_forward = (
        evaluation.get("entry_lane_forward_outcomes")
        if isinstance(evaluation.get("entry_lane_forward_outcomes"), Mapping)
        else {}
    )
    if lane_forward:
        lines += [
            "- Entry lane forward outcomes: "
            f"{_format_forward_rows(list(lane_forward.get('by_primary_lane') or []), limit=5)}",
            "- Entry lane subtype forward outcomes: "
            f"{_format_forward_rows(list(lane_forward.get('by_lane_subtype') or []), limit=5)}",
            "- Entry lane market-rail forward outcomes: "
            f"{_format_forward_rows(list(lane_forward.get('by_market_regime_rail') or []), limit=5)}",
        ]
    below_vwap = (
        evaluation.get("below_vwap_reclaim_observation")
        if isinstance(evaluation.get("below_vwap_reclaim_observation"), Mapping)
        else {}
    )
    if below_vwap and int(below_vwap.get("candidate_count") or 0) > 0:
        lines.append(
            "- Below-VWAP reclaim observation: "
            f"{below_vwap.get('candidate_count') or 0} candidates / "
            f"{_format_rows(list(below_vwap.get('by_subtype') or []), limit=8)}"
        )
    return lines
```
**Future targeted fixture:** payload={} → []; payload={'candidate_count':1} → list containing '## Quant Shadow Candidates'. **Safety/wrapper/monkeypatch:** read-only Markdown strings; facade._format_rows/_format_forward_rows/_format_scorecard_rows/Mapping resolved at call time; preserve original same-signature thin wrapper, original golden and exceptions. Recheck SHA/target before issuance.

### R5 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_actionable_entry_guard_block` @ L345 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_guard_observation_projection.py::_actionable_entry_guard_block` (404 A/integration, verified absent, design only).
**Actual existing BODY, NOT EXECUTABLE until newly issued:**
```python
def _actionable_entry_guard_block(row: Mapping[str, Any]) -> bool:
    if not _bool(row.get("guard_blocked")):
        return False
    primary = _text(row.get("primary_failure_axis"))
    decision = _entry_quant_decision(row)
    blockers = _row_blockers(row)
    guard_reason = _text(row.get("guard_reason"))
    if primary == "confirmed_entry" and decision == "entry_ready" and not blockers and not guard_reason:
        return False
    return True
```
**Future targeted fixture:** row={'guard_blocked':False} → False; patched facade._bool=True and failure_axis='other' → True. **Safety/wrapper/monkeypatch:** OBSERVATION ONLY: read-only classifier, no Guard configuration/order/State changes; facade._bool/_text/_entry_quant_decision/_row_blockers; preserve original same-signature thin wrapper, original golden and exceptions. Recheck SHA/target before issuance.

### R6 | RF-035 | Owner=CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::iter_quant_shadow_candidate_payloads` @ L211 | SOURCE_BLOB=`92a77e5552ebcd0777db52c842bd500e80b5ae00`
**TARGET:** `libs/reporting/quant_shadow_payload_iterator_projection.py::iter_quant_shadow_candidate_payloads` (404 A/integration, verified absent, design only).
**Actual existing BODY, NOT EXECUTABLE until newly issued:**
```python
def iter_quant_shadow_candidate_payloads(
    *,
    reports_root: Path,
    days: Sequence[str],
    keys: Optional[Sequence[str]] = None,
    drop_q9_row_keys: Optional[Sequence[str]] = None,
) -> Iterable[Dict[str, Any]]:
    """Yield one payload dict per shadow file.

    `keys=None` (default) yields the complete payload, unchanged. With `keys`,
    each payload is projected onto those top-level keys as soon as it is parsed
    (the full parse is released immediately) and the q9 commander augmentation
    -- which only ever rewrites `q9_decision_candidates` -- is skipped together
    with its multi-hundred-MiB `q9_decision_windows.json` load, unless the
    caller asked for that key.
    """
    root = shadow_candidate_root_for_reports(reports_root)
    seen: set[str] = set()
    wanted = tuple(keys) if keys is not None else None
    augment = wanted is None or "q9_decision_candidates" in wanted
    for day in days:
        q9_windows = _q9_windows_by_id(reports_root, day) if augment else {}
        for path in _json_paths_for_day(root, day):
            key = str(path)
            if key in seen:
                continue
            seen.add(key)
            payload = _read_json(path)
            if not isinstance(payload, dict):
                continue
            if wanted is not None:
                payload = {name: payload[name] for name in wanted if name in payload}
                if not augment:
                    yield _drop_q9_row_keys(payload, drop_q9_row_keys)
                    continue
            yield _drop_q9_row_keys(
                _augment_missing_q9_commander_candidate(
                    dict(payload),
                    windows_by_id=q9_windows,
                ),
                drop_q9_row_keys,
            )
```
**Future targeted fixture:** temp day folder one valid JSON with keys=['candidates'] → one projected dict, and fake _q9_windows_by_id must not be called; duplicate day path yielded once. **Safety/wrapper/monkeypatch:** read-only temp files and lazy generator; facade.shadow_candidate_root_for_reports/_q9_windows_by_id/_json_paths_for_day/_read_json/_drop_q9_row_keys/_augment_missing_q9_commander_candidate; preserve streaming, no real reports; preserve original same-signature thin wrapper, original golden and exceptions. Recheck SHA/target before issuance.

**Supply accounting:** NEW_READY=A 8; FUTURE_RESERVE_VERIFIED=A 6; A-22 REMOTE_DONE 8. Document commit is not code G1/G2/G3, C04 integration, or RF DONE. No real runtime/RunLab approval.
