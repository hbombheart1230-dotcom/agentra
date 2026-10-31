# C02 — Claude A | A-20261101-00 | FAST-3 NEW 8 VERIFIED SOURCE BODY MOVEs

**INPUT:** canonical integration at design `c2fff478f77d9cd25e6101cd1c5f2d040953f61b`; A remote `b95c04e3ca5d3dbcdac082af9de6b18fbc0ef0f2`; prior C02 blob `11716af4e3c8a6be0a456a03adc3096282e12e5c`; RF-035 CLAUDE_A exclusive `libs/reporting`; SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py` blob `0857857f4f056c95a750fe4476f1ec3b23d265eb` (A/integration exact match; 877 source LOC). #11 comment 6544589564 A-23 all eight actual BODY MOVEs normal unittest 8/8 exit0, remote pushed b95c04e3; A-23 is REMOTE_DONE, do NOT redo. #12 comment 6544449972 B-21 B2 now REMOTE_DONE at 32ed2053, B3–B8 remain six; C01 separately corrected. #32 latest 6520075820 RunLab exited255, RUN_SOURCE_SHA UNKNOWN, operational HOLD. No operational regression attribution.

**ONE-FILE CONTRACT:** Read only this C02 and exact code/test paths. Do not read D00/RF/queue/C03/HANDOFF, self-select work, reuse old PASS/KEEP, or edit docs. Pin current CANONICAL_HEAD, ORDER_BLOB, A_REMOTE_HEAD, ORDER_ID at start; complete ALL eight independent items or mark each BLOCKED with exact evidence and continue next safe item. A owns ONLY `work/p15-a-reporter-pure-20261021` code/tests; never B, integration, RF, STATUS, C04/C05, RunLab. This document authorizes no code execution by C03.

**SAFETY:** RF-035 offline shadow reporting and diagnostic projections only. Fake dictionaries, fake functions, TemporaryDirectory only; never real dataset/report, network, state/DB, live pipeline, actual broker/order, Guard policy/enforcement, Step5C, UEF, RunLab, CI/frozen oracle, force-push. The guard-named A5 and promotion-named A7 are OBSERVATION/RECOMMENDATION ONLY; their existing calculation and existing pure helper calls must be preserved without altering protected behavior. If the helper has effects under actual code inspection, mark that item SAFETY_BLOCKED and continue other seven.

**MOVE CONTRACT:** For each exact existing SOURCE body below, move its actual calculation to one NEW single-owner target. Leave same-signature thin SOURCE wrapper; preserve output, exceptions, identity, mutability, generator laziness, iteration order, caller imports and monkeypatch-at-call-time seams. New Owner must never import SOURCE. Pass keyword-only `facade=sys.modules[__name__]` (SOURCE imports sys already); resolve SOURCE module globals through facade at call time, including builtins replaced by monkeypatch, and add necessary local typing imports with `from __future__ import annotations`. Do not copy BODY into both files or treat a one-line delegation as MOVE. Before editing capture ORIGINAL function golden with fake fixtures, then compare original vs SOURCE wrapper vs direct Owner, negative/error and post-import monkeypatch. AST verify original SOURCE computation removed. Keep all older tests unchanged.

**TEST/PUSH:** Create only `tests/test_p15_rf035_20261101_00h_quant_shadow_owners.py` (404 verified A/integration), eight tests `test_a1_q9_windows` through `test_a8_evaluation_builder`, fixture and expected results below; `python -m py_compile` SOURCE and eight exact new targets, `python -m unittest tests/test_p15_rf035_20261101_00h_quant_shadow_owners.py -v` exit0. Normal targeted once, no full peer, mandatory -O or hosted CI. Commit only SOURCE + eight targets + new test on A branch, normal non-force push, refetch A remote HEAD and SOURCE/TARGET/test blob SHA; report original/after LOC, 8 individual outcomes, test command/exit and START/END measured in #11. Git auth failure blocks PUSH only; continue other safe items. C04 integration and C05 G1/G2/G3 DONE are separate.

**Allowed target files:** `libs/reporting/quant_shadow_q9_windows_projection.py`, `libs/reporting/quant_shadow_q9_augment_projection.py`, `libs/reporting/quant_shadow_trust_gate_projection.py`, `libs/reporting/quant_shadow_render_lines_projection.py`, `libs/reporting/quant_shadow_guard_observation_projection.py`, `libs/reporting/quant_shadow_payload_iterator_projection.py`, `libs/reporting/quant_shadow_promotion_projection.py`, `libs/reporting/quant_shadow_evaluation_builder_projection.py`; SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py`; TEST `tests/test_p15_rf035_20261101_00h_quant_shadow_owners.py`. All eight target paths returned 404 on both integration and A at design. Each item independently executable; on blocker continue next item.

## A1 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_q9_windows_by_id` L92 | CURRENT_BLOB `0857857f4f056c95a750fe4476f1ec3b23d265eb`
**TARGET:** `libs/reporting/quant_shadow_q9_windows_projection.py::_q9_windows_by_id` — NEW, verified absent A/integration, single owner.
**EXACT ORIGINAL CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
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
**Thin wrapper/callers/monkeypatch:** Same SOURCE signature; delegate to new Owner with facade at call time, preserve identity, exceptions and ordering. facade.Path, facade.Mapping, facade.iter_json_array; never load actual large Q9 files. Owner must not import SOURCE.
**Targeted normal test:** `test_a1_q9_windows` input→expected: fake facade.iter_json_array yields {'decision_id':'d1','commander_final':{'decision':'hold'}} → {'d1':{'commander_final':{'decision':'hold'}}}; patched OSError → {}. Compare ORIGINAL vs wrapper vs direct Owner and post-import monkeypatch; fake/temp only. If BLOCKED record first exact blocker and continue A2.

## A2 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_augment_missing_q9_commander_candidate` L112 | CURRENT_BLOB `0857857f4f056c95a750fe4476f1ec3b23d265eb`
**TARGET:** `libs/reporting/quant_shadow_q9_augment_projection.py::_augment_missing_q9_commander_candidate` — NEW, verified absent A/integration, single owner.
**EXACT ORIGINAL CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
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
**Thin wrapper/callers/monkeypatch:** Same SOURCE signature; delegate to new Owner with facade at call time, preserve identity, exceptions and ordering. facade.Mapping; preserve original payload in-place mutation, row precedence, identity and exception order. Owner must not import SOURCE.
**Targeted normal test:** `test_a2_q9_augment` input→expected: payload with matching decision_id, strategist-ranked symbol and commander_final selected_symbol adds one C_COMMANDER_FINAL row; existing C_COMMANDER_FINAL row leaves payload identity unchanged. Compare ORIGINAL vs wrapper vs direct Owner and post-import monkeypatch; fake/temp only. If BLOCKED record first exact blocker and continue A3.

## A3 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_evaluation_trust_gate` L428 | CURRENT_BLOB `0857857f4f056c95a750fe4476f1ec3b23d265eb`
**TARGET:** `libs/reporting/quant_shadow_trust_gate_projection.py::_evaluation_trust_gate` — NEW, verified absent A/integration, single owner.
**EXACT ORIGINAL CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
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
**Thin wrapper/callers/monkeypatch:** Same SOURCE signature; delegate to new Owner with facade at call time, preserve identity, exceptions and ordering. facade.Mapping, facade.build_q8_trust_gate, facade._text; read-only evaluation, no policy changes. Owner must not import SOURCE.
**Targeted normal test:** `test_a3_trust_gate` input→expected: fake facade.build_q8_trust_gate returns {'block_reasons':['low_coverage'],'minimums':{}} and empty watchlist → reasons ['low_coverage'], behavior_effect 'evaluation_only'; promotion_watch row retained. Compare ORIGINAL vs wrapper vs direct Owner and post-import monkeypatch; fake/temp only. If BLOCKED record first exact blocker and continue A4.

## A4 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::render_quant_shadow_candidate_evaluation_lines` L693 | CURRENT_BLOB `0857857f4f056c95a750fe4476f1ec3b23d265eb`
**TARGET:** `libs/reporting/quant_shadow_render_lines_projection.py::render_quant_shadow_candidate_evaluation_lines` — NEW, verified absent A/integration, single owner.
**EXACT ORIGINAL CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
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
**Thin wrapper/callers/monkeypatch:** Same SOURCE signature; delegate to new Owner with facade at call time, preserve identity, exceptions and ordering. facade.Mapping, facade._format_rows, facade._format_forward_rows, facade._format_scorecard_rows, facade._text; preserve Markdown line ordering. Owner must not import SOURCE.
**Targeted normal test:** `test_a4_render_lines` input→expected: payload={} → []; fake payload with candidate_count=1 and evaluation={} → list containing '## Quant Shadow Candidates'; malformed numeric must retain original exception parity. Compare ORIGINAL vs wrapper vs direct Owner and post-import monkeypatch; fake/temp only. If BLOCKED record first exact blocker and continue A5.

## A5 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_actionable_entry_guard_block` L341 | CURRENT_BLOB `0857857f4f056c95a750fe4476f1ec3b23d265eb`
**TARGET:** `libs/reporting/quant_shadow_guard_observation_projection.py::_actionable_entry_guard_block` — NEW, verified absent A/integration, single owner.
**EXACT ORIGINAL CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
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
**Thin wrapper/callers/monkeypatch:** Same SOURCE signature; delegate to new Owner with facade at call time, preserve identity, exceptions and ordering. OBSERVATION ONLY; facade._bool/_text/_entry_quant_decision/_row_blockers; never touch actual Guard enforcement. Owner must not import SOURCE.
**Targeted normal test:** `test_a5_guard_observation` input→expected: row={'guard_blocked':False} → False; patched facade._bool True, primary_failure_axis='other' → True. Compare ORIGINAL vs wrapper vs direct Owner and post-import monkeypatch; fake/temp only. If BLOCKED record first exact blocker and continue A6.

## A6 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::iter_quant_shadow_candidate_payloads` L207 | CURRENT_BLOB `0857857f4f056c95a750fe4476f1ec3b23d265eb`
**TARGET:** `libs/reporting/quant_shadow_payload_iterator_projection.py::iter_quant_shadow_candidate_payloads` — NEW, verified absent A/integration, single owner.
**EXACT ORIGINAL CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
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
**Thin wrapper/callers/monkeypatch:** Same SOURCE signature; delegate to new Owner with facade at call time, preserve identity, exceptions and ordering. facade.shadow_candidate_root_for_reports/_q9_windows_by_id/_json_paths_for_day/_read_json/_drop_q9_row_keys/_augment_missing_q9_commander_candidate; preserve lazy yield, bounded memory, no real reports. Owner must not import SOURCE.
**Targeted normal test:** `test_a6_payload_iterator` input→expected: TemporaryDirectory one day with one JSON and keys=['candidates'] → one projected dict; patched _q9_windows_by_id must not run; duplicate paths yield once. Compare ORIGINAL vs wrapper vs direct Owner and post-import monkeypatch; fake/temp only. If BLOCKED record first exact blocker and continue A7.

## A7 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::_promotion_candidate` L464 | CURRENT_BLOB `0857857f4f056c95a750fe4476f1ec3b23d265eb`
**TARGET:** `libs/reporting/quant_shadow_promotion_projection.py::_promotion_candidate` — NEW, verified absent A/integration, single owner.
**EXACT ORIGINAL CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
```python
def _promotion_candidate(candidates: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    if not candidates:
        return {
            "candidate": "hold",
            "confidence": "none",
            "reason": "no_shadow_candidates",
            "counts": {},
            "promotion_scope": "none",
            "recommended_action": "hold",
        }
    cost_edge = _count_reason(
        candidates,
        {"cost_edge_fail", "cost_filter_failed", "not_met", "cost_floor_not_met", "cost"},
    )
    entry_guard = sum(1 for row in candidates if _actionable_entry_guard_block(row))
    runner_up = _runner_up_risk_count(candidates)
    counts = {
        "cost_edge": cost_edge,
        "runner_up": runner_up,
        "entry_guard": entry_guard,
    }
    candidate, count = max(counts.items(), key=lambda item: item[1])
    if count <= 0:
        return {
            "candidate": "hold",
            "confidence": "low",
            "reason": "no_dominant_shadow_blocker",
            "counts": counts,
            "promotion_scope": "none",
            "recommended_action": "hold",
        }
    total = max(1, len(candidates))
    share = float(count) / float(total)
    confidence = "high" if count >= 5 and share >= 0.35 else "medium" if count >= 3 else "low"
    reason_by_candidate = {
        "cost_edge": "cost_edge_or_cost_floor_is_the_largest_shadow_blocker",
        "runner_up": "runner_up_fallback_quality_is_the_largest_shadow_issue",
        "entry_guard": "entry_guard_blocks_are_the_largest_shadow_issue",
    }
    promotion_scope = "pre_entry_filter" if candidate == "cost_edge" else "candidate_selection"
    recommended_action = "manual_review_before_live_change"
    promotion_state = "candidate_review"
    behavior_effect = "recommendation_only"
    active_guard_reason = ""
    if candidate == "cost_edge" and confidence in {"high", "medium"}:
        enforcement = build_entry_quant_enforcement(
            {"decision": "block_recommended", "blockers": ["cost_edge_fail"]}
        )
        if bool(enforcement.get("blocked")):
            recommended_action = "already_promoted_monitor_hard_gate"
            promotion_state = "active"
            behavior_effect = str(enforcement.get("behavior_effect") or "entry_guard_enforced")
            active_guard_reason = "quant_entry_block:cost_edge_fail"
        else:
            recommended_action = "promote_shadow_validated_guard"
            promotion_state = "recommended"
    return {
        "candidate": candidate,
        "confidence": confidence,
        "reason": reason_by_candidate.get(candidate, "dominant_shadow_blocker"),
        "counts": counts,
        "share": share,
        "behavior_effect": behavior_effect,
        "promotion_scope": promotion_scope,
        "recommended_action": recommended_action,
        "promotion_state": promotion_state,
        "active_guard_reason": active_guard_reason,
    }
```
**Thin wrapper/callers/monkeypatch:** Same SOURCE signature; delegate to new Owner with facade at call time, preserve identity, exceptions and ordering. read-only recommendation projection; facade._count_reason/_actionable_entry_guard_block/_runner_up_risk_count/build_entry_quant_enforcement; no real Guard mutation, order or promotion effect. Owner must not import SOURCE.
**Targeted normal test:** `test_a7_promotion` input→expected: candidates=[] → candidate='hold',reason='no_shadow_candidates'; synthetic 3 cost_edge_fail rows → deterministic counts and confidence; patched facade.build_entry_quant_enforcement returns {'blocked':False} for branch parity. Compare ORIGINAL vs wrapper vs direct Owner and post-import monkeypatch; fake/temp only. If BLOCKED record first exact blocker and continue A8.

## A8 | RF-035 | Owner CLAUDE_A | SOURCE `libs/reporting/quant_shadow_candidate_evaluation.py::build_quant_shadow_candidate_evaluation` L538 | CURRENT_BLOB `0857857f4f056c95a750fe4476f1ec3b23d265eb`
**TARGET:** `libs/reporting/quant_shadow_evaluation_builder_projection.py::build_quant_shadow_candidate_evaluation` — NEW, verified absent A/integration, single owner.
**EXACT ORIGINAL CALCULATION BODY TO MOVE (delete from SOURCE, retain thin wrapper):**
```python
def build_quant_shadow_candidate_evaluation(
    payloads: Iterable[Mapping[str, Any]],
    *,
    symbol: str = "",
) -> Dict[str, Any]:
    symbol_filter = _text(symbol).upper()
    payload_count = 0
    candidates: List[Dict[str, Any]] = []
    for payload in payloads:
        if not isinstance(payload, Mapping):
            continue
        payload_count += 1
        for row in list(payload.get("candidates") or []):
            if not isinstance(row, Mapping):
                continue
            row_symbol = _text(row.get("symbol")).upper()
            if symbol_filter and row_symbol != symbol_filter:
                continue
            enriched = dict(row)
            enriched.setdefault("_payload_generated_at", payload.get("generated_at"))
            candidates.append(enriched)
    candidates = attach_forward_outcomes(candidates)
    deduped_candidates = _dedupe_candidates(candidates)

    roles = Counter(_text(row.get("shadow_role")) for row in candidates)
    reasons = Counter(_text(row.get("reason")) for row in candidates)
    tactics = Counter(_tactic_id(row) for row in candidates)
    suitability = Counter(_tactic_suitability_tier(row) for row in candidates)
    cost_floor = Counter(_cost_floor_state(row) for row in candidates)
    blockers = Counter(_text(row.get("primary_failure_axis")) for row in candidates)
    opening_probe_rows = [row for row in candidates if _opening_probe(row)]
    opening_probe_reasons = Counter(_text(_opening_probe(row).get("reason")) for row in opening_probe_rows)
    opening_probe_symbols = Counter(_text(row.get("symbol")) for row in opening_probe_rows if _opening_probe_would_enter(row))
    largecap_probe_rows = [row for row in candidates if _largecap_surge_probe(row)]
    largecap_probe_reasons = Counter(_text(_largecap_surge_probe(row).get("reason")) for row in largecap_probe_rows)
    largecap_probe_symbols = Counter(
        _text(row.get("symbol")) for row in largecap_probe_rows if _largecap_surge_would_enter(row)
    )
    would_enter = sum(1 for row in candidates if _bool(row.get("would_enter")))
    opening_probe_would_enter = sum(1 for row in candidates if _opening_probe_would_enter(row))
    largecap_probe_would_enter = sum(1 for row in candidates if _largecap_surge_would_enter(row))
    opening_probe_top_reason = ""
    if opening_probe_reasons:
        opening_probe_top_reason = opening_probe_reasons.most_common(1)[0][0]
    largecap_probe_top_reason = ""
    if largecap_probe_reasons:
        largecap_probe_top_reason = largecap_probe_reasons.most_common(1)[0][0]
    guard_blocked = sum(1 for row in candidates if _bool(row.get("guard_blocked")))
    actionable_guard_blocked = sum(1 for row in candidates if _actionable_entry_guard_block(row))
    evaluated = sum(1 for row in candidates if _bool(row.get("evaluated")))
    forward_base_available = sum(1 for row in candidates if _bool(_forward_base(row).get("available")))
    deduped_forward_outcome_available = sum(
        1 for row in deduped_candidates if _bool(_forward_outcome(row).get("available"))
    )
    entry_shape = _entry_shape_payload(candidates)
    below_vwap_reclaim = _below_vwap_reclaim_observation_payload(candidates)
    entry_lane_observation = _entry_lane_observation_payload(candidates)
    entry_lane_forward_outcomes = _entry_lane_forward_outcomes(deduped_candidates)
    promotion = _promotion_candidate(candidates)
    shadow_readiness = _shadow_readiness(candidates, promotion)
    no_trade_scorecard = _no_trade_scorecard(
        candidates=deduped_candidates,
        entry_lane_forward_outcomes=entry_lane_forward_outcomes,
        would_enter_count=would_enter,
        opening_probe_would_enter=opening_probe_would_enter,
        largecap_probe_would_enter=largecap_probe_would_enter,
    )
    forward_outcome_coverage = (
        (float(deduped_forward_outcome_available) / float(len(deduped_candidates)))
        if deduped_candidates
        else 0.0
    )
    trust_gate = _evaluation_trust_gate(
        raw_candidate_count=len(candidates),
        deduped_candidate_count=len(deduped_candidates),
        trusted_forward_count=deduped_forward_outcome_available,
        trusted_forward_coverage=forward_outcome_coverage,
        no_trade_scorecard=no_trade_scorecard,
    )

    return {
        "schema_version": "quant_shadow_candidate_evaluation.v1",
        "behavior_effect": "observation_only",
        "shadow_readiness": shadow_readiness,
        "payload_count": payload_count,
        "candidate_count": len(candidates),
        "deduped_candidate_count": len(deduped_candidates),
        "duplicate_candidate_count": max(0, len(candidates) - len(deduped_candidates)),
        "dedupe_key": list(CANONICAL_DEDUPE_KEY_FIELDS),
        "evaluated_count": evaluated,
        "forward_base_available_count": forward_base_available,
        "forward_base_coverage": (float(forward_base_available) / float(len(candidates))) if candidates else 0.0,
        "forward_outcome_available_count": deduped_forward_outcome_available,
        "forward_outcome_coverage": forward_outcome_coverage,
        "would_enter_count": would_enter,
        "opening_momentum_probe_count": len(opening_probe_rows),
        "opening_momentum_probe_would_enter_count": opening_probe_would_enter,
        "opening_largecap_surge_count": len(largecap_probe_rows),
        "opening_largecap_surge_would_enter_count": largecap_probe_would_enter,
        "guard_blocked_count": guard_blocked,
        "actionable_guard_blocked_count": actionable_guard_blocked,
        "by_role": _top_counter(roles),
        "by_reason": _top_counter(reasons),
        "by_tactic_id": _top_counter(tactics),
        "by_tactic_suitability_tier": _top_counter(suitability),
        "by_cost_floor_state": _top_counter(cost_floor),
        "by_primary_failure_axis": _top_counter(blockers),
        "opening_momentum_probe": {
            "behavior_effect": "observation_only",
            "candidate_count": len(opening_probe_rows),
            "would_enter_count": opening_probe_would_enter,
            "blocked_dominant_reason": opening_probe_top_reason,
            "zero_would_enter_explanation": (
                f"no opening momentum probe passed; dominant blocker={opening_probe_top_reason or 'none'}"
                if opening_probe_would_enter == 0
                else ""
            ),
            "by_reason": _top_counter(opening_probe_reasons),
            "by_would_enter_symbol": _top_counter(opening_probe_symbols),
        },
        "opening_largecap_surge": {
            "behavior_effect": "observation_only",
            "candidate_count": len(largecap_probe_rows),
            "would_enter_count": largecap_probe_would_enter,
            "blocked_dominant_reason": largecap_probe_top_reason,
            "zero_would_enter_explanation": (
                f"no opening largecap surge probe passed; dominant blocker={largecap_probe_top_reason or 'none'}"
                if largecap_probe_would_enter == 0
                else ""
            ),
            "by_reason": _top_counter(largecap_probe_reasons),
            "by_would_enter_symbol": _top_counter(largecap_probe_symbols),
        },
        "entry_shape_diagnostics": entry_shape,
        "below_vwap_reclaim_observation": below_vwap_reclaim,
        "entry_lane_observation": entry_lane_observation,
        "entry_lane_forward_outcomes": entry_lane_forward_outcomes,
        "no_trade_scorecard": no_trade_scorecard,
        "evaluation_trust_gate": trust_gate,
        "promotion_candidate": promotion,
    }
```
**Thin wrapper/callers/monkeypatch:** Same SOURCE signature; delegate to new Owner with facade at call time, preserve identity, exceptions and ordering. facade all original globals incl. Mapping, Counter, _text, attach_forward_outcomes, _dedupe_candidates, _top_counter, _evaluation_trust_gate and other helper functions; no live pipeline or real reports. Owner must not import SOURCE.
**Targeted normal test:** `test_a8_evaluation_builder` input→expected: payloads=[] → schema_version='quant_shadow_candidate_evaluation.v1', candidate_count=0, behavior_effect='observation_only'; one fake payload with candidate symbol A, symbol='B' → candidate_count=0; deterministic fake attach_forward_outcomes. Compare ORIGINAL vs wrapper vs direct Owner and post-import monkeypatch; fake/temp only. If BLOCKED record first exact blocker and continue Afinish/test/push.

## FUTURE RESERVE — RESERVE_NOT_VERIFIED 0/6
The previous six verified reserve functions are now executable A1–A6, therefore NOT future reserve. No other six candidates have been freshly validated against RF Owner, SOURCE BODY/current blob, TARGET absence, test and safety. Do NOT claim 6/6 or let A self-select; next C03 must inspect six new independent RF-035 CLAUDE_A reporting functions and verify target 404 on A/integration before issuance. Potential remaining functions in this source are often already thin wrappers and count as ZERO until actual BODY confirmed. Supply accounting: A-23 REMOTE_DONE=8, A-00 NEW_READY=8, FUTURE_RESERVE_VERIFIED=0/6; this document commit is NOT code G1/G2/G3, C04 integration, or RF DONE.
