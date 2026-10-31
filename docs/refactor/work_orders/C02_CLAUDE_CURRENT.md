# C02 — Claude A | A-20261031-12 | FAST-3 SINGLE EXECUTION ORDER

**PIN AT START:** CANONICAL_INPUT_HEAD=`d8fdfb9dd7cf4d7be5b01861d38c8cfb441a61b1`; ORDER_FILE_BLOB_SHA=fetch this C02 from `integration/p1.5`; A_REMOTE_HEAD_AT_DESIGN=`1485132c2c6b4f24c27bba4749b4fe133deaae66`; previous A-20261031-11 C02 blob=`b1784e27c3bd92b7fbcb4cf07be0faa484006a2d` is **8/8 REMOTE_DONE** at A remote `1485132c2c6b4f24c27bba4749b4fe133deaae66` (#11 latest run 46). Do not redo completed 11h work. A's start-pinned order is not retroactively cancelled. This is the only task instruction: do not read D00, RF, queue, C03, handoffs, or select your own items.

**EXECUTE ALL EIGHT NEW SOURCE BODY MOVES (RF-035, exclusive Claude A reporting Owner).** These are 6 previously reserved and now **revalidated against the latest A source blobs** plus 2 newly inspected read-only bodies. Each actual original body matches the code below, target module was absent at A remote HEAD, and no A/B source/target collision was found. On refreshed A HEAD recheck SOURCE blob/target: if body already moved, classify REMOTE_DONE (not new); if source changed and parity is unproven, mark STALE/BLOCKED individually and continue all safe items. Preserve function signature/defaults/annotations, import-visible caller contract, output ordering and exceptions. Move each calculation BODY to a single Owner, SOURCE keeps only a thin delegate; no duplicate computation. If globals are referenced, Owner accepts `facade` and resolves the source module's globals at use time; SOURCE passes `sys.modules[__name__]` (or existing `_r3_sys.modules[__name__]`), preserving monkeypatch seams. Target must never import SOURCE. Preserve generator lazy timing (`yield from` when appropriate). Do not change external side effects. Test fake/temp only, mock time and file reads; NO live trading/order/Broker/Guard/Step5C/UEF/RunLab, production State, live network, CI/frozen oracle, deploy or force push. Normal targeted unittest/pytest/smoke exit0 once for each changed range is sufficient G2; no mandatory -O/full peer/full CI. Actor edits/pushes own code/tests only. C04 integrates, C05 alone decides G1/G2/G3 and RF DONE.

## A1 | RF-035 | libs/reporting/q8_historical_review.py::_aggregate_shadow_summaries @ L242 | SOURCE_BLOB=14c227068e0facd5be52189b3940521e64fb9710

**TARGET (new exclusive Owner, absent at A remote HEAD):** `libs/reporting/q8_historical_shadow_aggregate_projection.py::_aggregate_shadow_summaries`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (preserve semantics; only change global lookup plumbing needed for use-time facade):

```python
def _aggregate_shadow_summaries(reports_root: Path, *, start: str, end: str) -> Dict[str, Any]:
    reason_counter: Counter[str] = Counter()
    role_counter: Counter[str] = Counter()
    tactic_counter: Counter[str] = Counter()
    below_vwap_subtype_counter: Counter[str] = Counter()
    below_vwap_subtype_v2_counter: Counter[str] = Counter()
    vwap_reclaim_subtype_forward: Dict[str, ForwardAccumulator] = defaultdict(ForwardAccumulator)
    vwap_reclaim_subtype_forward_days: set[str] = set()
    group_acc: Dict[str, GroupAccumulator] = defaultdict(GroupAccumulator)
    q_days = 0
    q8_group_days = 0
    for day in _iter_days(start, end):
        path = reports_root / "operator_summary" / "daily" / day / "daily_summary.json"
        if not path.exists():
            continue
        payload = _read_json(path)
        q = payload.get("quant_shadow_candidate_evaluation") if isinstance(payload.get("quant_shadow_candidate_evaluation"), dict) else {}
        if q.get("candidate_count") is not None:
            q_days += 1
        for row in list(q.get("by_reason") or []):
            if isinstance(row, Mapping):
                reason_counter[_text(row.get("name"))] += _int(row.get("count"))
        for row in list(q.get("by_role") or []):
            if isinstance(row, Mapping):
                role_counter[_text(row.get("name"))] += _int(row.get("count"))
        for row in list(q.get("by_tactic_id") or []):
            if isinstance(row, Mapping):
                tactic_counter[_text(row.get("name"))] += _int(row.get("count"))
        below_vwap = (
            q.get("below_vwap_reclaim_observation")
            if isinstance(q.get("below_vwap_reclaim_observation"), Mapping)
            else {}
        )
        for row in list(below_vwap.get("by_subtype") or []):
            if isinstance(row, Mapping):
                below_vwap_subtype_counter[_text(row.get("name"))] += _int(row.get("count"))
        for row in list(below_vwap.get("by_subtype_v2") or []):
            if isinstance(row, Mapping):
                below_vwap_subtype_v2_counter[_text(row.get("name"))] += _int(row.get("count"))
        lane_forward = (
            q.get("entry_lane_forward_outcomes")
            if isinstance(q.get("entry_lane_forward_outcomes"), Mapping)
            else {}
        )
        for row in list(lane_forward.get("by_lane_subtype") or []):
            if not isinstance(row, Mapping):
                continue
            name = _text(row.get("name"))
            if not name.startswith("vwap_reclaim:"):
                continue
            vwap_reclaim_subtype_forward[name].add(row)
            vwap_reclaim_subtype_forward_days.add(day)
        q8 = payload.get("q8_shadow_blocker_review") if isinstance(payload.get("q8_shadow_blocker_review"), dict) else {}
        groups = list(q8.get("groups") or [])
        if groups:
            q8_group_days += 1
        for row in groups:
            if not isinstance(row, Mapping):
                continue
            reason = _text(row.get("reason") or row.get("name"))
            if not reason:
                continue
            group_acc[reason].add(day, row)
    if not below_vwap_subtype_v2_counter:
        for row in _iter_quant_shadow_candidate_rows(reports_root, start=start, end=end):
            observation = classify_below_vwap_reclaim_observation(row)
            if not bool(observation.get("applies")):
                continue
            below_vwap_subtype_v2_counter[_text(observation.get("subtype_v2"))] += 1
    subtype_forward_rows = [
        acc.to_dict(name)
        for name, acc in sorted(
            vwap_reclaim_subtype_forward.items(),
            key=lambda item: (item[1].candidate_count, item[0]),
            reverse=True,
        )
    ]
    for row in subtype_forward_rows:
        row["decision"] = _decision_for_reclaim_subtype(row)
    return {
        "q_shadow_day_count": q_days,
        "q8_group_day_count": q8_group_days,
        "by_reason": [{"name": name, "count": count} for name, count in reason_counter.most_common(20) if name],
        "by_role": [{"name": name, "count": count} for name, count in role_counter.most_common(12) if name],
        "by_tactic_id": [{"name": name, "count": count} for name, count in tactic_counter.most_common(12) if name],
        "below_vwap_reclaim_by_subtype": [
            {"name": name, "count": count}
            for name, count in below_vwap_subtype_counter.most_common(12)
            if name
        ],
        "below_vwap_reclaim_by_subtype_v2": [
            {"name": name, "count": count}
            for name, count in below_vwap_subtype_v2_counter.most_common(12)
            if name
        ],
        "below_vwap_reclaim_subtype_forward_day_count": len(vwap_reclaim_subtype_forward_days),
        "below_vwap_reclaim_subtype_forward": subtype_forward_rows,
        "q8_blocker_groups": [
            acc.to_dict(reason)
            for reason, acc in sorted(group_acc.items(), key=lambda item: item[1].candidate_count, reverse=True)
        ],
    }
```

**Thin wrapper / callers / monkeypatch:** Keep original `_aggregate_shadow_summaries` signature in `libs/reporting/q8_historical_review.py`; delegate to `libs/reporting/q8_historical_shadow_aggregate_projection.py::_aggregate_shadow_summaries` at call time, not a copied implementation. Retain existing import and monkeypatch seam, original exceptions/output ordering, and generator laziness. Where module globals are referenced, owner resolves them from passed source `facade` at use time (do not capture values at import time); no reverse import. **Safety:** report-only computation/read-only on fake/temp fixtures; do not touch real state, live network, broker/order/guard/Step5C/UEF, runtime or frozen tests.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_12h_a1_aggregate_shadow_summaries_owner.py`. Explicit input→expected: empty temp report root for one-day interval → no group days; two fake daily summaries → reason/group totals equal baseline. Compare original baseline output/exception with new Owner and SOURCE wrapper, including patched facade global where relevant. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_shadow_aggregate_projection.py` then `python -m unittest tests/test_p15_rf035_12h_a1_aggregate_shadow_summaries_owner.py -v` normal exit0 (or equivalent targeted pytest). Commit only Actor-owned code/test, normal push and re-fetch A remote SOURCE/TARGET/test blob and HEAD. On BLOCKED report exact reason and continue A2; never stop after first PASS or push failure.

## A2 | RF-035 | libs/reporting/q8_historical_review.py::_promotion_recommendations @ L357 | SOURCE_BLOB=14c227068e0facd5be52189b3940521e64fb9710

**TARGET (new exclusive Owner, absent at A remote HEAD):** `libs/reporting/q8_historical_recommendation_projection.py::_promotion_recommendations`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (preserve semantics; only change global lookup plumbing needed for use-time facade):

```python
def _promotion_recommendations(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    groups = {str(row.get("reason")): dict(row) for row in list(payload.get("q8_blocker_groups") or []) if isinstance(row, Mapping)}
    recs: List[Dict[str, Any]] = []
    defensive = next(
        (
            row
            for row in list(payload.get("trade_by_tactic") or [])
            if str(row.get("name") or "") == "defensive_observe"
        ),
        {},
    )
    if defensive and int(defensive.get("count") or 0) >= 5 and float(defensive.get("avg_return_pct") or 0.0) < 0:
        recs.append(
            {
                "candidate": "risk_off_defensive_observe_no_entry_policy",
                "decision": "promoted_keep",
                "reason": "defensive_observe live trades are negative and 2026-06-08 showed severe risk-off misuse.",
            }
        )
    for reason, label in (
        ("below_vwap_reclaim_not_ready", "subtype_adjust_review"),
        ("breakout_not_ready", "adjust_and_retest"),
        ("pullback_not_mature", "adjust_and_retest"),
        ("volume_confirmation_missing", "retain_strict_or_observe"),
        ("human_chart_sanity_guard_blocked", "retain_veto_review_missed"),
    ):
        row = groups.get(reason) or {}
        if not row:
            continue
        recs.append(
            {
                "candidate": reason,
                "decision": label,
                "candidate_count": row.get("candidate_count"),
                "observed_count": row.get("observed_count"),
                "avg_latest_return_pct": row.get("avg_latest_return_pct"),
                "missed_opportunity_rate": row.get("missed_opportunity_rate"),
                "adverse_rate": row.get("adverse_rate"),
            }
        )
    subtype_rows = list(payload.get("below_vwap_reclaim_subtype_forward") or [])
    if subtype_rows:
        strongest = max(
            subtype_rows,
            key=lambda row: (
                float(row.get("avg_return_15m_pct") or 0.0),
                float(row.get("avg_return_5m_pct") or 0.0),
                int(row.get("observed_count") or 0),
            ),
        )
        recs.append(
            {
                "candidate": "below_vwap_reclaim_subtype_policy",
                "decision": "do_not_relax_globally",
                "reason": (
                    f"Subtype forward evidence is mixed; strongest={strongest.get('name')} "
                    f"5m={float(strongest.get('avg_return_5m_pct') or 0.0):.4f}%, "
                    f"15m={float(strongest.get('avg_return_15m_pct') or 0.0):.4f}%. "
                    "Review classifier labels before behavior promotion."
                ),
            }
        )
    return recs
```

**Thin wrapper / callers / monkeypatch:** Keep original `_promotion_recommendations` signature in `libs/reporting/q8_historical_review.py`; delegate to `libs/reporting/q8_historical_recommendation_projection.py::_promotion_recommendations` at call time, not a copied implementation. Retain existing import and monkeypatch seam, original exceptions/output ordering, and generator laziness. Where module globals are referenced, owner resolves them from passed source `facade` at use time (do not capture values at import time); no reverse import. **Safety:** report-only computation/read-only on fake/temp fixtures; do not touch real state, live network, broker/order/guard/Step5C/UEF, runtime or frozen tests.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_12h_a2_promotion_recommendations_owner.py`. Explicit input→expected: {'q8_blocker_groups':[],'trade_by_tactic':[]} → baseline empty recommendation list; fake negative defensive_observe group → identical advisory recommendation. Compare original baseline output/exception with new Owner and SOURCE wrapper, including patched facade global where relevant. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_recommendation_projection.py` then `python -m unittest tests/test_p15_rf035_12h_a2_promotion_recommendations_owner.py -v` normal exit0 (or equivalent targeted pytest). Commit only Actor-owned code/test, normal push and re-fetch A remote SOURCE/TARGET/test blob and HEAD. On BLOCKED report exact reason and continue A3; never stop after first PASS or push failure.

## A3 | RF-035 | libs/reporting/q8_historical_review.py::build_q8_historical_review_payload @ L422 | SOURCE_BLOB=14c227068e0facd5be52189b3940521e64fb9710

**TARGET (new exclusive Owner, absent at A remote HEAD):** `libs/reporting/q8_historical_payload_projection.py::build_q8_historical_review_payload`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (preserve semantics; only change global lookup plumbing needed for use-time facade):

```python
def build_q8_historical_review_payload(
    *,
    reports_root: Path = Path("reports"),
    start: str,
    end: str,
) -> Dict[str, Any]:
    daily_rows = _daily_summary_rows(reports_root, start=start, end=end)
    trade_rows = _extract_trade_rows(reports_root, start=start, end=end)
    return_rows = [row for row in trade_rows if isinstance(row.get("pnl_pct"), (int, float))]
    shadow = _aggregate_shadow_summaries(reports_root, start=start, end=end)
    pattern_by_tactic = _pattern_rows_from_daily_summaries(
        reports_root,
        start=start,
        end=end,
        section="strategist",
        group_key="by_tactical_strategy",
    )
    pattern_by_exit = _pattern_rows_from_daily_summaries(
        reports_root,
        start=start,
        end=end,
        section="monitor_exit",
        group_key="by_exit_reason",
    )
    payload: Dict[str, Any] = {
        "schema_version": "q8_historical_review.v1",
        "behavior_effect": "evaluation_only",
        "start": str(start)[:10],
        "end": str(end)[:10],
        "daily_count": len(daily_rows),
        "daily_rows": daily_rows,
        "q8_promotion_eligibility": {
            "promotion_allowed_day_count": sum(1 for row in daily_rows if bool(row.get("q8_promotion_allowed"))),
            "trusted_gate_day_count": sum(1 for row in daily_rows if _text(row.get("q8_trust_gate_status"))),
            "status": (
                "promotion_review_possible"
                if any(bool(row.get("q8_promotion_allowed")) for row in daily_rows)
                else "promotion_blocked_by_trust_gate_or_legacy_data"
            ),
            "rule": "Historical conclusions require daily evaluation_trust_gate.promotion_allowed=true. Legacy daily summaries without trust gate are observation-only.",
        },
        "trade_summary": {
            "trade_report_count": len(trade_rows),
            "return_sample_count": len(return_rows),
            "avg_return_pct": _avg([float(row["pnl_pct"]) for row in return_rows]),
            "win_rate": round(sum(1 for row in return_rows if float(row["pnl_pct"]) > 0) / len(return_rows), 4)
            if return_rows
            else 0.0,
            "truth_sources": [
                {"name": name, "count": count}
                for name, count in Counter(_text(row.get("truth_source")) or "missing" for row in trade_rows).most_common(12)
            ],
        },
        "trade_by_tactic": pattern_by_tactic or _aggregate_return_rows(return_rows, "tactic"),
        "trade_by_entry_reason": _aggregate_return_rows(return_rows, "entry_reason"),
        "trade_by_exit_reason": pattern_by_exit or _aggregate_return_rows(return_rows, "exit_reason"),
        **shadow,
    }
    eligibility = payload.get("q8_promotion_eligibility") if isinstance(payload.get("q8_promotion_eligibility"), Mapping) else {}
    if int(eligibility.get("promotion_allowed_day_count") or 0) <= 0:
        payload["promotion_recommendations"] = [
            {
                "candidate": "all_q8_candidates",
                "decision": "retain_under_observation",
                "reason": "no historical day passed the Q8 evaluation trust gate",
            }
        ]
    else:
        payload["promotion_recommendations"] = _promotion_recommendations(payload)
    return payload
```

**Thin wrapper / callers / monkeypatch:** Keep original `build_q8_historical_review_payload` signature in `libs/reporting/q8_historical_review.py`; delegate to `libs/reporting/q8_historical_payload_projection.py::build_q8_historical_review_payload` at call time, not a copied implementation. Retain existing import and monkeypatch seam, original exceptions/output ordering, and generator laziness. Where module globals are referenced, owner resolves them from passed source `facade` at use time (do not capture values at import time); no reverse import. **Safety:** report-only computation/read-only on fake/temp fixtures; do not touch real state, live network, broker/order/guard/Step5C/UEF, runtime or frozen tests.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_12h_a3_build_q8_historical_review_payload_owner.py`. Explicit input→expected: empty temp reports root with start=end='2026-10-30' → schema_version='q8_historical_review.v1', daily_count=0, promotion gate remains blocked. Compare original baseline output/exception with new Owner and SOURCE wrapper, including patched facade global where relevant. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_payload_projection.py` then `python -m unittest tests/test_p15_rf035_12h_a3_build_q8_historical_review_payload_owner.py -v` normal exit0 (or equivalent targeted pytest). Commit only Actor-owned code/test, normal push and re-fetch A remote SOURCE/TARGET/test blob and HEAD. On BLOCKED report exact reason and continue A4; never stop after first PASS or push failure.

## A4 | RF-035 | libs/reporting/q8_historical_review.py::render_q8_historical_review_markdown @ L498 | SOURCE_BLOB=14c227068e0facd5be52189b3940521e64fb9710

**TARGET (new exclusive Owner, absent at A remote HEAD):** `libs/reporting/q8_historical_markdown_projection.py::render_q8_historical_review_markdown`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (preserve semantics; only change global lookup plumbing needed for use-time facade):

```python
def render_q8_historical_review_markdown(payload: Mapping[str, Any]) -> str:
    trade = payload.get("trade_summary") if isinstance(payload.get("trade_summary"), Mapping) else {}
    lines: List[str] = [
        f"# Q8 Historical Review: {payload.get('start')} to {payload.get('end')}",
        "",
        "Purpose: reuse prior live and shadow evidence without mixing incompatible artifact eras.",
        "",
        "This review is evaluation-only. It does not change entry, exit, scanner, Strategist, or execution behavior.",
        "",
        "## Data Windows",
        "",
        "- Live trade performance: usable from 2026-05-18 onward when truth-surface PnL exists.",
        "- Q8 shadow evaluation: most useful from 2026-05-26 onward when candidate shadow summaries are populated.",
        "- Market regime rail: most useful from 2026-06-02 onward when rail IDs are attached to daily summaries.",
        "- Broker truth reconciliation: strongest from 2026-06-08 onward after post-close order-pair repair.",
        "",
        "## Live Trade Summary",
        "",
        f"- Trade report files: **{trade.get('trade_report_count', 0)}**",
        f"- Return samples: **{trade.get('return_sample_count', 0)}**",
        f"- Win rate: **{float(trade.get('win_rate') or 0.0) * 100:.2f}%**",
        f"- Average return: **{float(trade.get('avg_return_pct') or 0.0):.4f}%**",
        "",
    ]
    daily_rows = list(payload.get("daily_rows") or [])
    if daily_rows:
        lines.extend(
            _md_table(
                ["Day", "Trades", "Closed", "Returns", "Missing", "Win", "Avg", "Raw", "Deduped", "Trusted", "Gate", "Allowed", "Rail"],
                [
                    [
                        row.get("day"),
                        row.get("trade_count"),
                        row.get("closed_trade_count"),
                        row.get("return_sample_count"),
                        row.get("unavailable_return_count"),
                        f"{float(row.get('win_rate') or 0.0) * 100:.1f}%",
                        f"{float(row.get('avg_return_pct') or 0.0):.2f}%",
                        row.get("shadow_candidate_count") or 0,
                        row.get("shadow_deduped_candidate_count") or 0,
                        row.get("q8_trusted_forward_count") or 0,
                        row.get("q8_trust_gate_status") or "legacy/no_gate",
                        bool(row.get("q8_promotion_allowed")),
                        row.get("market_regime_rail") or "-",
                    ]
                    for row in daily_rows
                ],
            )
        )
        lines.append("")
    eligibility = payload.get("q8_promotion_eligibility") if isinstance(payload.get("q8_promotion_eligibility"), Mapping) else {}
    lines.extend(
        [
            "## Q8 Promotion Eligibility",
            "",
            f"- status: `{eligibility.get('status') or 'unknown'}`",
            f"- trusted gate days: **{eligibility.get('trusted_gate_day_count') or 0}**",
            f"- promotion allowed days: **{eligibility.get('promotion_allowed_day_count') or 0}**",
            f"- rule: {eligibility.get('rule') or '-'}",
            "",
        ]
    )
    lines.extend(["## Trade Pattern Evidence", ""])
    for title, key in (
        ("By Tactic", "trade_by_tactic"),
        ("By Entry Reason", "trade_by_entry_reason"),
        ("By Exit Reason", "trade_by_exit_reason"),
    ):
        rows = list(payload.get(key) or [])
        lines.extend([f"### {title}", ""])
        lines.extend(
            _md_table(
                ["Name", "Count", "Win", "Avg"],
                [
                    [
                        row.get("name"),
                        row.get("count"),
                        f"{float(row.get('win_rate') or 0.0) * 100:.1f}%",
                        f"{float(row.get('avg_return_pct') or 0.0):.3f}%",
                    ]
                    for row in rows[:10]
                ],
            )
        )
        lines.append("")
    lines.extend(
        [
            "## Q8 Shadow Summary",
            "",
            f"- Q8 shadow summary days: **{payload.get('q_shadow_day_count', 0)}**",
            f"- Q8 blocker forward-review days: **{payload.get('q8_group_day_count', 0)}**",
            "",
            "### Top Shadow Reasons",
            "",
        ]
    )
    lines.extend(
        _md_table(
            ["Reason", "Count"],
            [[row.get("name"), row.get("count")] for row in list(payload.get("by_reason") or [])[:15]],
        )
    )
    lines.extend(["", "### Forward Blocker Review", ""])
    lines.extend(
        _md_table(
            ["Reason", "n", "obs", "Latest", "MFE", "MAE", "Missed", "Adverse", "Decision"],
            [
                [
                    row.get("reason"),
                    row.get("candidate_count"),
                    row.get("observed_count"),
                    f"{float(row.get('avg_latest_return_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_max_favorable_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_max_adverse_pct') or 0.0):.4f}%",
                    f"{float(row.get('missed_opportunity_rate') or 0.0) * 100:.1f}%",
                    f"{float(row.get('adverse_rate') or 0.0) * 100:.1f}%",
                    row.get("dominant_decision") or "-",
                ]
                for row in list(payload.get("q8_blocker_groups") or [])[:10]
            ],
        )
    )
    subtype_rows = list(payload.get("below_vwap_reclaim_by_subtype") or [])
    subtype_v2_rows = list(payload.get("below_vwap_reclaim_by_subtype_v2") or [])
    subtype_forward_rows = list(payload.get("below_vwap_reclaim_subtype_forward") or [])
    lines.extend(
        [
            "",
            "## Below-VWAP Reclaim Subtype Review",
            "",
            f"- Subtype count days: **{payload.get('q_shadow_day_count', 0)}**",
            f"- Subtype forward days: **{payload.get('below_vwap_reclaim_subtype_forward_day_count', 0)}**",
            "- Note: subtype forward evidence is available only after the entry-lane observation fields were added.",
            "",
            "### Subtype Counts",
            "",
        ]
    )
    lines.extend(
        _md_table(
            ["Subtype", "Count"],
            [[row.get("name"), row.get("count")] for row in subtype_rows[:10]],
        )
    )
    lines.extend(["", "### Subtype V2 Counts", ""])
    lines.extend(
        _md_table(
            ["Subtype V2", "Count"],
            [[row.get("name"), row.get("count")] for row in subtype_v2_rows[:12]],
        )
    )
    lines.extend(["", "### Subtype Forward Outcomes", ""])
    lines.extend(
        _md_table(
            ["Subtype", "n", "obs", "3m", "5m", "15m", "30m", "60m", "MFE5", "MAE5", "Decision"],
            [
                [
                    row.get("name"),
                    row.get("candidate_count"),
                    row.get("observed_count"),
                    f"{float(row.get('avg_return_3m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_5m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_15m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_30m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_return_60m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_mfe_5m_pct') or 0.0):.4f}%",
                    f"{float(row.get('avg_mae_5m_pct') or 0.0):.4f}%",
                    row.get("decision") or "-",
                ]
                for row in subtype_forward_rows[:10]
            ],
        )
    )
    lines.extend(["", "## Recommendations", ""])
    lines.extend(
        _md_table(
            ["Candidate", "Decision", "Evidence"],
            [
                [
                    row.get("candidate"),
                    row.get("decision"),
                    row.get("reason")
                    or (
                        f"n={row.get('candidate_count')}, obs={row.get('observed_count')}, "
                        f"latest={float(row.get('avg_latest_return_pct') or 0.0):.4f}%, "
                        f"missed={float(row.get('missed_opportunity_rate') or 0.0) * 100:.1f}%, "
                        f"adverse={float(row.get('adverse_rate') or 0.0) * 100:.1f}%"
                    ),
                ]
                for row in list(payload.get("promotion_recommendations") or [])
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Operator Conclusion",
            "",
            "- Prior data is useful, but it must be sliced by artifact era.",
            "- Live trade PnL already shows persistent negative expectancy in stop/trend-break/low-break exits.",
            "- Q8 shadow raw sample size alone is not promotion evidence.",
            "- Promotion review requires trusted same-day forward outcomes, canonical dedupe, and evaluation_trust_gate.promotion_allowed=true.",
            "- Historical reports generated before the trust gate are legacy observation material, not policy-promotion evidence.",
            "",
        ]
    )
    return "\n".join(lines)
```

**Thin wrapper / callers / monkeypatch:** Keep original `render_q8_historical_review_markdown` signature in `libs/reporting/q8_historical_review.py`; delegate to `libs/reporting/q8_historical_markdown_projection.py::render_q8_historical_review_markdown` at call time, not a copied implementation. Retain existing import and monkeypatch seam, original exceptions/output ordering, and generator laziness. Where module globals are referenced, owner resolves them from passed source `facade` at use time (do not capture values at import time); no reverse import. **Safety:** report-only computation/read-only on fake/temp fixtures; do not touch real state, live network, broker/order/guard/Step5C/UEF, runtime or frozen tests.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_12h_a4_render_q8_historical_review_markdown_owner.py`. Explicit input→expected: synthetic empty historical payload → byte-identical Markdown and headings as baseline. Compare original baseline output/exception with new Owner and SOURCE wrapper, including patched facade global where relevant. Run `python -m py_compile libs/reporting/q8_historical_review.py libs/reporting/q8_historical_markdown_projection.py` then `python -m unittest tests/test_p15_rf035_12h_a4_render_q8_historical_review_markdown_owner.py -v` normal exit0 (or equivalent targeted pytest). Commit only Actor-owned code/test, normal push and re-fetch A remote SOURCE/TARGET/test blob and HEAD. On BLOCKED report exact reason and continue A5; never stop after first PASS or push failure.

## A5 | RF-035 | libs/reporting/post_exit_shadow_recap.py::_utc_now_iso @ L53 | SOURCE_BLOB=36c3fdbaf86998c4194f5fe17c0b793f9a8f8207

**TARGET (new exclusive Owner, absent at A remote HEAD):** `libs/reporting/post_exit_shadow_clock_projection.py::_utc_now_iso`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (preserve semantics; only change global lookup plumbing needed for use-time facade):

```python
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
```

**Thin wrapper / callers / monkeypatch:** Keep original `_utc_now_iso` signature in `libs/reporting/post_exit_shadow_recap.py`; delegate to `libs/reporting/post_exit_shadow_clock_projection.py::_utc_now_iso` at call time, not a copied implementation. Retain existing import and monkeypatch seam, original exceptions/output ordering, and generator laziness. Where module globals are referenced, owner resolves them from passed source `facade` at use time (do not capture values at import time); no reverse import. **Safety:** report-only computation/read-only on fake/temp fixtures; do not touch real state, live network, broker/order/guard/Step5C/UEF, runtime or frozen tests.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_12h_a5_utc_now_iso_owner.py`. Explicit input→expected: mock datetime.now(timezone.utc) fixed 2026-10-31T00:00:00+00:00 → exact ISO text. Compare original baseline output/exception with new Owner and SOURCE wrapper, including patched facade global where relevant. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_clock_projection.py` then `python -m unittest tests/test_p15_rf035_12h_a5_utc_now_iso_owner.py -v` normal exit0 (or equivalent targeted pytest). Commit only Actor-owned code/test, normal push and re-fetch A remote SOURCE/TARGET/test blob and HEAD. On BLOCKED report exact reason and continue A6; never stop after first PASS or push failure.

## A6 | RF-035 | libs/reporting/post_exit_shadow_recap.py::_read_json @ L57 | SOURCE_BLOB=36c3fdbaf86998c4194f5fe17c0b793f9a8f8207

**TARGET (new exclusive Owner, absent at A remote HEAD):** `libs/reporting/post_exit_shadow_read_projection.py::_read_json`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (preserve semantics; only change global lookup plumbing needed for use-time facade):

```python
def _read_json(path: Path) -> Dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}
```

**Thin wrapper / callers / monkeypatch:** Keep original `_read_json` signature in `libs/reporting/post_exit_shadow_recap.py`; delegate to `libs/reporting/post_exit_shadow_read_projection.py::_read_json` at call time, not a copied implementation. Retain existing import and monkeypatch seam, original exceptions/output ordering, and generator laziness. Where module globals are referenced, owner resolves them from passed source `facade` at use time (do not capture values at import time); no reverse import. **Safety:** report-only computation/read-only on fake/temp fixtures; do not touch real state, live network, broker/order/guard/Step5C/UEF, runtime or frozen tests.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_12h_a6_read_json_owner.py`. Explicit input→expected: temp {'a':1} JSON → {'a':1}; malformed/non-dict → {}. Compare original baseline output/exception with new Owner and SOURCE wrapper, including patched facade global where relevant. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_read_projection.py` then `python -m unittest tests/test_p15_rf035_12h_a6_read_json_owner.py -v` normal exit0 (or equivalent targeted pytest). Commit only Actor-owned code/test, normal push and re-fetch A remote SOURCE/TARGET/test blob and HEAD. On BLOCKED report exact reason and continue A7; never stop after first PASS or push failure.

## A7 | RF-035 | libs/reporting/post_exit_shadow_recap.py::_post_exit_shadow_needs_fresh_minutes @ L137 | SOURCE_BLOB=36c3fdbaf86998c4194f5fe17c0b793f9a8f8207

**TARGET (new exclusive Owner, absent at A remote HEAD):** `libs/reporting/post_exit_shadow_freshness_decision_projection.py::_post_exit_shadow_needs_fresh_minutes`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (preserve semantics; only change global lookup plumbing needed for use-time facade):

```python
def _post_exit_shadow_needs_fresh_minutes(shadow: Mapping[str, Any], rows: List[Dict[str, Any]]) -> bool:
    target_epoch = _shadow_latest_required_epoch(shadow)
    now_epoch = datetime.now(timezone.utc).timestamp()
    if target_epoch is not None:
        if now_epoch + 30.0 < target_epoch:
            return False
        if not _rows_reach_epoch(rows, target_epoch):
            return True

    now_kst = datetime.now(timezone.utc).astimezone(KST)
    checkpoints = _as_dict(shadow.get("checkpoints"))
    eod = _as_dict(checkpoints.get("EOD"))
    eod_pending = str(eod.get("status") or "").strip().lower() != "observed"
    if eod_pending and now_kst.strftime("%H%M%S") >= "153500":
        return not _rows_reach_regular_close(rows)
    return False
```

**Thin wrapper / callers / monkeypatch:** Keep original `_post_exit_shadow_needs_fresh_minutes` signature in `libs/reporting/post_exit_shadow_recap.py`; delegate to `libs/reporting/post_exit_shadow_freshness_decision_projection.py::_post_exit_shadow_needs_fresh_minutes` at call time, not a copied implementation. Retain existing import and monkeypatch seam, original exceptions/output ordering, and generator laziness. Where module globals are referenced, owner resolves them from passed source `facade` at use time (do not capture values at import time); no reverse import. **Safety:** report-only computation/read-only on fake/temp fixtures; do not touch real state, live network, broker/order/guard/Step5C/UEF, runtime or frozen tests.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_12h_a7_post_exit_shadow_needs_fresh_minutes_owner.py`. Explicit input→expected: Freeze facade.datetime/timezone/KST at 2026-10-31 16:00 KST; facade._shadow_latest_required_epoch returns None; fake shadow checkpoints.EOD.status='observed' with rows=[] -> False; status='pending' with facade._rows_reach_regular_close returning False -> True. Verify call-time monkeypatch and unchanged exception behavior. Compare original baseline output/exception with new Owner and SOURCE wrapper, including patched facade global where relevant. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_freshness_decision_projection.py` then `python -m unittest tests/test_p15_rf035_12h_a7_post_exit_shadow_needs_fresh_minutes_owner.py -v` normal exit0 (or equivalent targeted pytest). Commit only Actor-owned code/test, normal push and re-fetch A remote SOURCE/TARGET/test blob and HEAD. On BLOCKED report exact reason and continue A8; never stop after first PASS or push failure.

## A8 | RF-035 | libs/reporting/post_exit_shadow_recap.py::iter_trade_report_json_paths @ L283 | SOURCE_BLOB=36c3fdbaf86998c4194f5fe17c0b793f9a8f8207

**TARGET (new exclusive Owner, absent at A remote HEAD):** `libs/reporting/post_exit_shadow_path_projection.py::iter_trade_report_json_paths`. **EXACT CURRENT SOURCE COMPUTATION BODY TO MOVE** (preserve semantics; only change global lookup plumbing needed for use-time facade):

```python
def iter_trade_report_json_paths(reports_root: Path, day: str) -> List[Path]:
    trade_root = reports_root / "trades" / day
    if not trade_root.exists():
        return []
    return sorted(trade_root.rglob("reports/ai_trade_report.json"))
```

**Thin wrapper / callers / monkeypatch:** Keep original `iter_trade_report_json_paths` signature in `libs/reporting/post_exit_shadow_recap.py`; delegate to `libs/reporting/post_exit_shadow_path_projection.py::iter_trade_report_json_paths` at call time, not a copied implementation. Retain existing import and monkeypatch seam, original exceptions/output ordering, and generator laziness. Where module globals are referenced, owner resolves them from passed source `facade` at use time (do not capture values at import time); no reverse import. **Safety:** report-only computation/read-only on fake/temp fixtures; do not touch real state, live network, broker/order/guard/Step5C/UEF, runtime or frozen tests.

**Mandatory targeted normal G2:** `tests/test_p15_rf035_12h_a8_iter_trade_report_json_paths_owner.py`. Explicit input→expected: Use tmp_path with trades/2026-10-31/x/reports/ai_trade_report.json and trades/2026-10-31/y/reports/ai_trade_report.json; expect two sorted Path values; missing day -> []; verify baseline/owner/wrapper parity and no writes. Compare original baseline output/exception with new Owner and SOURCE wrapper, including patched facade global where relevant. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_path_projection.py` then `python -m unittest tests/test_p15_rf035_12h_a8_iter_trade_report_json_paths_owner.py -v` normal exit0 (or equivalent targeted pytest). Commit only Actor-owned code/test, normal push and re-fetch A remote SOURCE/TARGET/test blob and HEAD. On BLOCKED report exact reason and continue A1–8 remaining safe items; never stop after first PASS or push failure.

## SIX VERIFIED FUTURE RESERVES — DESIGN ONLY, NOT EXECUTABLE THIS ORDER

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

Report to #11: `ORDER_ID=A-20261031-12 | CANONICAL_HEAD | ORDER_BLOB | A_REMOTE_HEAD_BEFORE/AFTER | A1..A8 IMPLEMENTED/REMOTE_DONE/BLOCKED | SOURCE/TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | NEW_BODY_MOVES | FIRST_BLOCKER | NEXT_SAFE_ITEM | START_KST/END_KST/ELAPSED_MIN`. START/END only measured, no inferred duration. Terminal push failure is PUSH_BLOCKED, not G1; continue safe items and preserve exact-tree evidence. G1 remote code, G2 normal targeted exit0, G3 C04/C05 handoff are separate. No RF/STATUS/queue/doc edits by A.