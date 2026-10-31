# C02 — Claude A | A-20261031-15 | FAST-3 eight new verified SOURCE BODY MOVEs

**PRE-FLIGHT:** CANONICAL_HEAD_AT_ISSUANCE=`94f46342c92e41d3521d087ee0c23acc25148cb5`; OLD_C02_BLOB=`821e6374678388025d659d711b250e9af688cfce`; A_ACTOR_HEAD_AT_DESIGN=`cffab3934a7973bca82507bc89e622cd93b09405`; RF-035 is CLAUDE_A exclusive `libs/reporting/` reporting Owner (C03 checked physical RF-035 05_DONE). Prior A-20261031-14 eight functions are **REMOTE_DONE** at A `cffab3934a7973bca82507bc89e622cd93b09405`, Issue #11 6539460831 normal 24/24 exit0, C04 exact integration 5ddfe6fa and C05 14:45 acceptance. Do not repeat them, prior PASS or KEEP. This new order has eight different actual SOURCE bodies; each target was checked 404 on actor and integration. New code/test NOT_RUN by C03.

## EXECUTION / SAFETY — C02 IS THE ONLY TASK DOCUMENT

Read this C02 only; do not read D00, RF, queue, C03 or handoffs, do not choose your own work. At start pin CANONICAL_HEAD, C02 blob, actor remote HEAD, each SOURCE blob and ORDER_ID. Do **all eight** A1–A8 independently. If already moved at a fresher actor HEAD mark REMOTE_DONE and skip; if blocked report precise evidence and continue other safe items. Only edit RF-035 source files below, their specified new projection Owner modules and new targeted tests on A branch `work/p15-a-reporter-pure-20261021`. No B code, C/RF/STATUS/queue/policy/CI documents, protected trading, Broker, Guard, Step5C, UEF, RunLab, real orders/accounts, operating State/logs, live network, deploy, frozen oracle or force push.

Move exact original computation BODY below to TARGET (not copy); leave SOURCE same-name/same-signature/defaults/annotations/public API as **thin wrapper**, no duplicate calculation. TARGET never imports SOURCE. For module-global lookup, TARGET accepts keyword-only `facade` and resolves names at invocation; SOURCE passes `sys.modules[__name__]` (post_exit existing `_r3_sys.modules[__name__]`). Preserve caller imports, monkeypatch after import, exceptions, identity, stdout, bytes, and recursion. Lazy-import target in SOURCE if circular import risk. Use fake/in-memory/TemporaryDirectory and compare original golden behavior with wrapper and Owner, including negative/exception and thin AST checks. Normal targeted unittest/pytest exit0 once for changed scope is G2; -O/full peer/whole CI are not blanket gates. Commit/push only actor code/tests with non-force expected-head lease or approved exact-tree fallback; re-fetch remote actor HEAD and SOURCE/TARGET/test blobs. LOCAL_ONLY != G1. Record actual START/END only if measured. C04 integrates; C05 decides G1/G2/G3 and RF/STATUS/DONE.

## A1 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::_text` @ L27 | SOURCE_BLOB=`cfce1a0c5708f27fd369a22eca7a638227d28ed8`

**TARGET:** `libs/reporting/controlled_lane_text_projection.py::_text` — NEW exclusive A Owner; actor/integration path ABSENT 404. **Exact original computation BODY:**

```python
def _text(value: Any) -> str:
    return str(value or "").strip()
```

**Preserve/wrapper/monkeypatch:** pure string normalization; no facade. Keep exact original SOURCE signature with thin delegation; Owner holds actual body and imports only stdlib/other non-SOURCE dependencies. Compare original/wrapper/Owner including patched globals, errors and output. Isolation: fake/temp only, never real state/order/network.

**New normal targeted test:** `tests/test_p15_rf035_15h_a1__text_owner.py`. Input → expected: `None`→`''`, `'  A  '`→`'A'`, `0`→`''`; verify pure return parity. Also compare original pre-move golden output and wrapper/Owner; verify no original BODY remains in SOURCE. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_text_projection.py` and `python -m unittest tests.test_p15_rf035_15h_a1__text_owner -v` (or equivalent exact-scope pytest); report actual exit0 and PASS count, never fabricate. Commit/push A-only code+test, refetch actor HEAD and exact blobs. On block report reason and continue A2.

## A2 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::_fixed_lane_strategy` @ L43 | SOURCE_BLOB=`cfce1a0c5708f27fd369a22eca7a638227d28ed8`

**TARGET:** `libs/reporting/controlled_lane_strategy_projection.py::_fixed_lane_strategy` — NEW exclusive A Owner; actor/integration path ABSENT 404. **Exact original computation BODY:**

```python
def _fixed_lane_strategy() -> dict[str, Any]:
    return {
        "controlled_mock_lane": True,
        "strategy_horizon": "intraday",
        "expected_hold_window": {"min_sec": 300, "target_sec": 1800, "max_sec": 14400},
        "llm_used": False,
        "horizon_revision_allowed": False,
    }
```

**Preserve/wrapper/monkeypatch:** constant mock report metadata only; never change Guard or real policy. Keep exact original SOURCE signature with thin delegation; Owner holds actual body and imports only stdlib/other non-SOURCE dependencies. Compare original/wrapper/Owner including patched globals, errors and output. Isolation: fake/temp only, never real state/order/network.

**New normal targeted test:** `tests/test_p15_rf035_15h_a2__fixed_lane_strategy_owner.py`. Input → expected: `()`→`controlled_mock_lane=True`, `expected_hold_window.min_sec=300,target_sec=1800,max_sec=14400`, `llm_used=False`, `horizon_revision_allowed=False`; distinct dict on repeated calls. Also compare original pre-move golden output and wrapper/Owner; verify no original BODY remains in SOURCE. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_strategy_projection.py` and `python -m unittest tests.test_p15_rf035_15h_a2__fixed_lane_strategy_owner -v` (or equivalent exact-scope pytest); report actual exit0 and PASS count, never fabricate. Commit/push A-only code+test, refetch actor HEAD and exact blobs. On block report reason and continue A3.

## A3 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::attach_controlled_lane_report_surface` @ L71 | SOURCE_BLOB=`cfce1a0c5708f27fd369a22eca7a638227d28ed8`

**TARGET:** `libs/reporting/controlled_lane_attach_projection.py::attach_controlled_lane_report_surface` — NEW exclusive A Owner; actor/integration path ABSENT 404. **Exact original computation BODY:**

```python
def attach_controlled_lane_report_surface(report: dict[str, Any], story_input: Mapping[str, Any]) -> dict[str, Any]:
    surface = _first_mapping(
        story_input.get("controlled_mock_lane"),
        _mapping(story_input.get("trade_lifecycle")).get("controlled_mock_lane"),
        _mapping(_mapping(story_input.get("trade_lifecycle")).get("entry")).get("controlled_mock_lane"),
        _mapping(story_input.get("lifecycle_bundle")).get("controlled_mock_lane"),
    )
    if surface:
        report["controlled_mock_lane"] = surface
        fact_payload = _mapping(report.get("fact_payload"))
        trade = _mapping(fact_payload.get("trade"))
        if trade:
            trade.setdefault("controlled_mock_lane", surface)
            fact_payload["trade"] = trade
            report["fact_payload"] = fact_payload
    return report
```

**Preserve/wrapper/monkeypatch:** in-memory report mutation; facade `_first_mapping,_mapping`; preserve identity and setdefault. Keep exact original SOURCE signature with thin delegation; Owner holds actual body and imports only stdlib/other non-SOURCE dependencies. Compare original/wrapper/Owner including patched globals, errors and output. Isolation: fake/temp only, never real state/order/network.

**New normal targeted test:** `tests/test_p15_rf035_15h_a3_attach_controlled_lane_repor_owner.py`. Input → expected: `report={'fact_payload':{'trade':{'symbol':'A'}}}`, `story_input={'controlled_mock_lane':{'lane_id':'L'}}`→same report identity and both report/trade controlled lane id `L`; empty lane unchanged. Also compare original pre-move golden output and wrapper/Owner; verify no original BODY remains in SOURCE. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_attach_projection.py` and `python -m unittest tests.test_p15_rf035_15h_a3_attach_controlled_lane_repor_owner -v` (or equivalent exact-scope pytest); report actual exit0 and PASS count, never fabricate. Commit/push A-only code+test, refetch actor HEAD and exact blobs. On block report reason and continue A4.

## A4 | RF-035 | SOURCE `libs/reporting/controlled_mock_lane_report.py::apply_controlled_lane_story_surface` @ L89 | SOURCE_BLOB=`cfce1a0c5708f27fd369a22eca7a638227d28ed8`

**TARGET:** `libs/reporting/controlled_lane_story_projection.py::apply_controlled_lane_story_surface` — NEW exclusive A Owner; actor/integration path ABSENT 404. **Exact original computation BODY:**

```python
def apply_controlled_lane_story_surface(
    story_input: Mapping[str, Any], surface: Mapping[str, Any]
) -> dict[str, Any]:
    out = dict(story_input)
    lane = _mapping(surface)
    if not lane:
        return out
    symbol = _text(lane.get("symbol"))
    reason = (
        f"{lane.get('lane_label') or lane.get('lane_id')} 독립 결정 레인이 {symbol}을 선택했습니다. "
        "메인 Scanner 순위는 이 거래에 적용되지 않습니다."
    )
    scanner_surface = {
        "summary": reason,
        "comparison": "This trade did not use the main Scanner ranking authority.",
        "bullets": [
            f"Independent lane: {lane.get('lane_id')}",
            "Scanner rank: not applicable",
            f"Signal ID: {lane.get('signal_id') or 'not_captured'}",
        ],
        "selected_symbol": symbol,
        "selected_rank": None,
        "universe_size": None,
        "selection_authority": "deterministic_independent_lane",
    }
    out["controlled_mock_lane"] = lane
    out["scanner_reason_human"] = scanner_surface
    out["scanner_selection_trace"] = dict(scanner_surface)
    entry_summary = _mapping(out.get("entry_summary"))
    if entry_summary:
        entry_summary["reason_human"] = reason
        entry_summary["controlled_mock_lane"] = lane
        out["entry_summary"] = entry_summary
    lifecycle_summary = _mapping(out.get("lifecycle_summary"))
    if lifecycle_summary:
        lifecycle_summary["entry_reason_human"] = reason
        out["lifecycle_summary"] = lifecycle_summary
    scanner_evidence = _mapping(out.get("scanner_evidence"))
    if scanner_evidence:
        scanner_evidence["selection_authority"] = "deterministic_independent_lane"
        scanner_evidence["selected_rank"] = None
        scanner_evidence["independent_lane"] = lane
        out["scanner_evidence"] = scanner_evidence
    for lifecycle_key in ("trade_lifecycle", "lifecycle"):
        lifecycle = _mapping(out.get(lifecycle_key))
        if lifecycle:
            lifecycle["controlled_mock_lane"] = lane
            entry = _mapping(lifecycle.get("entry"))
            if entry:
                entry["reason_human"] = reason
                entry["controlled_mock_lane"] = lane
                lifecycle["entry"] = entry
            out[lifecycle_key] = lifecycle
    bundle = _mapping(out.get("lifecycle_bundle"))
    if bundle:
        bundle["controlled_mock_lane"] = lane
        bundle["scanner_reason_human"] = scanner_surface
        bundle["scanner_selection_trace"] = scanner_surface
        lifecycle = _mapping(bundle.get("lifecycle"))
        if lifecycle:
            lifecycle["controlled_mock_lane"] = lane
            entry = _mapping(lifecycle.get("entry"))
            if entry:
                entry["reason_human"] = reason
                entry["controlled_mock_lane"] = lane
                lifecycle["entry"] = entry
            bundle["lifecycle"] = lifecycle
        out["lifecycle_bundle"] = bundle
    return out
```

**Preserve/wrapper/monkeypatch:** in-memory projection only, preserve exact Korean narrative, nested copy/alias semantics; facade `_mapping,_text`. Keep exact original SOURCE signature with thin delegation; Owner holds actual body and imports only stdlib/other non-SOURCE dependencies. Compare original/wrapper/Owner including patched globals, errors and output. Isolation: fake/temp only, never real state/order/network.

**New normal targeted test:** `tests/test_p15_rf035_15h_a4_apply_controlled_lane_story__owner.py`. Input → expected: fake `story_input={'entry_summary':{'x':1}}`, `surface={'lane_id':'L','symbol':'A'}`→new dict, `scanner_selection_trace.selection_authority='deterministic_independent_lane'`, `selected_rank=None`, `entry_summary.controlled_mock_lane.lane_id='L'`; input unchanged. Also compare original pre-move golden output and wrapper/Owner; verify no original BODY remains in SOURCE. Run `python -m py_compile libs/reporting/controlled_mock_lane_report.py libs/reporting/controlled_lane_story_projection.py` and `python -m unittest tests.test_p15_rf035_15h_a4_apply_controlled_lane_story__owner -v` (or equivalent exact-scope pytest); report actual exit0 and PASS count, never fabricate. Commit/push A-only code+test, refetch actor HEAD and exact blobs. On block report reason and continue A5.

## A5 | RF-035 | SOURCE `libs/reporting/q8_shadow_blocker_review.py::build_q8_shadow_blocker_review` @ L78 | SOURCE_BLOB=`c28e1738c0c1fa90a98e2798901db114770fe966`

**TARGET:** `libs/reporting/q8_shadow_blocker_review_build_projection.py::build_q8_shadow_blocker_review` — NEW exclusive A Owner; actor/integration path ABSENT 404. **Exact original computation BODY:**

```python
def build_q8_shadow_blocker_review(
    payloads: Iterable[Mapping[str, Any]],
    *,
    minute_rows_by_symbol: Mapping[str, list[Mapping[str, Any]]] | None = None,
    review_reasons: Sequence[str] = DEFAULT_REVIEW_REASONS,
    market_regime_rail: Mapping[str, Any] | None = None,
    quant_shadow_evaluation: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    raw_rows = attach_forward_outcomes(_candidate_rows(payloads), minute_rows_by_symbol=minute_rows_by_symbol)
    rows = _dedupe_rows(raw_rows)
    trusted_forward_count = 0
    for row in rows:
        outcome = row.get("shadow_forward_outcome") if isinstance(row.get("shadow_forward_outcome"), Mapping) else {}
        if _bool(_checkpoint_values(outcome).get("available")):
            trusted_forward_count += 1
    trusted_forward_coverage = round(float(trusted_forward_count) / float(len(rows)), 4) if rows else 0.0
    evaluation_gate = (
        quant_shadow_evaluation.get("evaluation_trust_gate")
        if isinstance(quant_shadow_evaluation, Mapping)
        and isinstance(quant_shadow_evaluation.get("evaluation_trust_gate"), Mapping)
        else {}
    )
    trust_gate = (
        dict(evaluation_gate)
        if evaluation_gate
        else build_q8_trust_gate(
            raw_candidate_count=len(raw_rows),
            deduped_candidate_count=len(rows),
            trusted_forward_count=trusted_forward_count,
            trusted_forward_coverage=trusted_forward_coverage,
            candidate_watchlist=[],
        )
    )
    promotion_allowed = bool(trust_gate.get("promotion_allowed"))
    review_reason_set = {str(reason) for reason in review_reasons}
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        reason = _text(row.get("reason"))
        if reason in review_reason_set:
            grouped[reason].append(row)
    groups = [
        _summarize_group(reason, grouped.get(reason, []), promotion_allowed=promotion_allowed)
        for reason in review_reasons
    ]
    observed_total = sum(int(group.get("observed_count") or 0) for group in groups)
    return {
        "schema_version": "q8_shadow_blocker_review.v1",
        "behavior_effect": "evaluation_only",
        "market_regime_rail": dict(market_regime_rail or {}),
        "raw_candidate_count": len(raw_rows),
        "deduped_candidate_count": len(rows),
        "duplicate_count": max(0, len(raw_rows) - len(rows)),
        "dedupe_key": list(CANONICAL_DEDUPE_KEY_FIELDS),
        "evaluation_trust_gate": trust_gate,
        "promotion_allowed": promotion_allowed,
        "candidate_count": len(rows),
        "review_reason_count": len(groups),
        "observed_review_candidate_count": observed_total,
        "groups": groups,
    }
```

**Preserve/wrapper/monkeypatch:** read-only evaluation; SOURCE keeps DEFAULT_REVIEW_REASONS default; TARGET takes explicit review_reasons, no import SOURCE; facade for `_candidate_rows,attach_forward_outcomes,_dedupe_rows,_bool,_checkpoint_values,build_q8_trust_gate,_text,_summarize_group,Mapping,defaultdict,CANONICAL_DEDUPE_KEY_FIELDS`; no trust policy change. Keep exact original SOURCE signature with thin delegation; Owner holds actual body and imports only stdlib/other non-SOURCE dependencies. Compare original/wrapper/Owner including patched globals, errors and output. Isolation: fake/temp only, never real state/order/network.

**New normal targeted test:** `tests/test_p15_rf035_15h_a5_build_q8_shadow_blocker_revi_owner.py`. Input → expected: `payloads=[]`, `review_reasons=('breakout_not_ready',)`, `quant_shadow_evaluation={'evaluation_trust_gate':{'status':'blocked','promotion_allowed':False}}`→`candidate_count=0`, `review_reason_count=1`, `behavior_effect='evaluation_only'`, `promotion_allowed=False`; fake nonempty patch parity. Also compare original pre-move golden output and wrapper/Owner; verify no original BODY remains in SOURCE. Run `python -m py_compile libs/reporting/q8_shadow_blocker_review.py libs/reporting/q8_shadow_blocker_review_build_projection.py` and `python -m unittest tests.test_p15_rf035_15h_a5_build_q8_shadow_blocker_revi_owner -v` (or equivalent exact-scope pytest); report actual exit0 and PASS count, never fabricate. Commit/push A-only code+test, refetch actor HEAD and exact blobs. On block report reason and continue A6.

## A6 | RF-035 | SOURCE `libs/reporting/q8_shadow_blocker_review.py::render_q8_shadow_blocker_review_markdown` @ L140 | SOURCE_BLOB=`c28e1738c0c1fa90a98e2798901db114770fe966`

**TARGET:** `libs/reporting/q8_shadow_blocker_markdown_projection.py::render_q8_shadow_blocker_review_markdown` — NEW exclusive A Owner; actor/integration path ABSENT 404. **Exact original computation BODY:**

```python
def render_q8_shadow_blocker_review_markdown(review: Mapping[str, Any], *, day: str) -> str:
    lines = [
        f"# Q8 Shadow Blocker Review ({day})",
        "",
        "This report is read-only evaluation output. It does not change trading behavior.",
        "",
        "## Summary",
        "",
        f"- candidate_count: **{int(review.get('candidate_count') or 0)}**",
        f"- raw_candidate_count: **{int(review.get('raw_candidate_count') or review.get('candidate_count') or 0)}**",
        f"- duplicate_count: **{int(review.get('duplicate_count') or 0)}**",
        f"- dedupe_key: `{', '.join(list(review.get('dedupe_key') or []))}`",
        f"- review_reason_count: **{int(review.get('review_reason_count') or 0)}**",
        f"- observed_review_candidate_count: **{int(review.get('observed_review_candidate_count') or 0)}**",
    ]
    gate = review.get("evaluation_trust_gate") if isinstance(review.get("evaluation_trust_gate"), Mapping) else {}
    if gate:
        lines.extend(
            [
                f"- trust_gate: `{gate.get('status') or '-'}`",
                f"- promotion_allowed: `{bool(gate.get('promotion_allowed'))}`",
                f"- trust_block_reasons: `{', '.join(list(gate.get('block_reasons') or gate.get('reasons') or [])) or '-'}`",
            ]
        )
    rail = review.get("market_regime_rail") if isinstance(review.get("market_regime_rail"), Mapping) else {}
    if rail:
        lines.append(
            f"- market_regime_rail: `{rail.get('rail_id') or 'not_available'}` "
            f"({rail.get('rail_confidence') or 'none'})"
        )
        lines.append(f"- market_regime_rationale: {rail.get('rationale') or '-'}")
        focus = [str(x) for x in list(rail.get("q8_review_focus") or []) if str(x or "").strip()]
        if focus:
            lines.append(f"- market_regime_q8_focus: `{', '.join(focus)}`")
    lines += [
        "",
        "## Blocker Outcomes",
        "",
        "| Reason | Candidates | Observed | Avg Latest | Avg MFE | Avg MAE | Missed Opp | Adverse | Decision |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    groups = review.get("groups") if isinstance(review.get("groups"), list) else []
    for group in groups:
        if not isinstance(group, Mapping):
            continue
        lines.append(
            f"| `{group.get('reason') or '-'}` "
            f"| {int(group.get('candidate_count') or 0)} "
            f"| {int(group.get('observed_count') or 0)} "
            f"| {float(group.get('avg_latest_return_pct') or 0.0):.4f}% "
            f"| {float(group.get('avg_max_favorable_pct') or 0.0):.4f}% "
            f"| {float(group.get('avg_max_adverse_pct') or 0.0):.4f}% "
            f"| {int(group.get('missed_opportunity_count') or 0)} "
            f"| {int(group.get('adverse_count') or 0)} "
            f"| `{group.get('decision') or 'retain_under_observation'}` |"
        )
    for group in groups:
        if not isinstance(group, Mapping) or not group.get("examples"):
            continue
        lines += ["", f"## Examples: {group.get('reason')}", ""]
        for example in list(group.get("examples") or [])[:5]:
            if not isinstance(example, Mapping):
                continue
            lines.append(
                f"- `{example.get('symbol') or '-'}` role `{example.get('role') or '-'}` "
                f"rank `{example.get('rank') if example.get('rank') is not None else '-'}` "
                f"latest {float(example.get('latest_return_pct') or 0.0):.4f}% "
                f"MFE {float(example.get('max_favorable_pct') or 0.0):.4f}% "
                f"MAE {float(example.get('max_adverse_pct') or 0.0):.4f}%"
            )
    return "\n".join(lines).rstrip() + "\n"
```

**Preserve/wrapper/monkeypatch:** read-only formatter; facade Mapping; preserve bytes/newlines/order and exception behavior. Keep exact original SOURCE signature with thin delegation; Owner holds actual body and imports only stdlib/other non-SOURCE dependencies. Compare original/wrapper/Owner including patched globals, errors and output. Isolation: fake/temp only, never real state/order/network.

**New normal targeted test:** `tests/test_p15_rf035_15h_a6_render_q8_shadow_blocker_rev_owner.py`. Input → expected: `review={'candidate_count':0,'groups':[],'evaluation_trust_gate':{'status':'blocked','promotion_allowed':False}}`, day `2026-10-31`→starts `# Q8 Shadow Blocker Review (2026-10-31)`, includes `candidate_count: **0**`, ends exactly one newline; nonempty group golden byte parity. Also compare original pre-move golden output and wrapper/Owner; verify no original BODY remains in SOURCE. Run `python -m py_compile libs/reporting/q8_shadow_blocker_review.py libs/reporting/q8_shadow_blocker_markdown_projection.py` and `python -m unittest tests.test_p15_rf035_15h_a6_render_q8_shadow_blocker_rev_owner -v` (or equivalent exact-scope pytest); report actual exit0 and PASS count, never fabricate. Commit/push A-only code+test, refetch actor HEAD and exact blobs. On block report reason and continue A7.

## A7 | RF-035 | SOURCE `libs/reporting/post_exit_shadow_recap.py::resolve_post_exit_state_path` @ L65 | SOURCE_BLOB=`29a7692fd5ea05de245338ab340e069d3149be1d`

**TARGET:** `libs/reporting/post_exit_shadow_state_path_projection.py::resolve_post_exit_state_path` — NEW exclusive A Owner; actor/integration path ABSENT 404. **Exact original computation BODY:**

```python
def resolve_post_exit_state_path(reports_root: Path, state_path: Path | None = None) -> Path | None:
    candidates: List[Path] = []
    if state_path is not None and str(state_path).strip():
        candidates.append(Path(state_path))
    for key in ("STATE_STORE_PATH", "MOCK_EXAM_STATE_PATH"):
        raw = str(os.getenv(key) or "").strip()
        if raw:
            candidates.append(Path(raw))

    reports_root_path = Path(reports_root)
    candidates.append(reports_root_path.parent / "data" / "state.json")
    candidates.append(Path("data/state.json"))

    for candidate in candidates:
        path = candidate
        if not path.is_absolute():
            path = (Path.cwd() / path).resolve()
        if path.exists():
            return path
    return None
```

**Preserve/wrapper/monkeypatch:** read-only path selection/exists; facade Path/os, patched env/cwd; NEVER read/write operating State. Keep exact original SOURCE signature with thin delegation; Owner holds actual body and imports only stdlib/other non-SOURCE dependencies. Compare original/wrapper/Owner including patched globals, errors and output. Isolation: fake/temp only, never real state/order/network.

**New normal targeted test:** `tests/test_p15_rf035_15h_a7_resolve_post_exit_state_path_owner.py`. Input → expected: TemporaryDirectory fake `<tmp>/reports` and `<tmp>/data/state.json`, patched env empty and cwd `<tmp>`→existing fake state path; explicit fake state_path takes priority; no candidates→None; no real State touched. Also compare original pre-move golden output and wrapper/Owner; verify no original BODY remains in SOURCE. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_state_path_projection.py` and `python -m unittest tests.test_p15_rf035_15h_a7_resolve_post_exit_state_path_owner -v` (or equivalent exact-scope pytest); report actual exit0 and PASS count, never fabricate. Commit/push A-only code+test, refetch actor HEAD and exact blobs. On block report reason and continue A8.

## A8 | RF-035 | SOURCE `libs/reporting/post_exit_shadow_recap.py::opening_rank1_eod_fallback_row` @ L149 | SOURCE_BLOB=`29a7692fd5ea05de245338ab340e069d3149be1d`

**TARGET:** `libs/reporting/post_exit_shadow_eod_fallback_projection.py::opening_rank1_eod_fallback_row` — NEW exclusive A Owner; actor/integration path ABSENT 404. **Exact original computation BODY:**

```python
def opening_rank1_eod_fallback_row(
    *, reports_root: Path, day: str, symbol: str
) -> tuple[Dict[str, Any] | None, Dict[str, Any]]:
    path = (
        Path(reports_root)
        / "evaluation"
        / "opening_rank1_shadow"
        / str(day)
        / "opening_rank1_shadow_daily.json"
    )
    payload = _read_json(path)
    normalized = normalize_symbol(symbol or "", allow_test_symbols=True)
    for raw in payload.get("episodes") or []:
        episode = _as_dict(raw)
        if normalize_symbol(episode.get("symbol") or "", allow_test_symbols=True) != normalized:
            continue
        eod = _as_dict(_as_dict(episode.get("checkpoints")).get("EOD"))
        if str(eod.get("status") or "").strip().lower() != "observed":
            continue
        price = eod.get("price") if eod.get("price") not in (None, "") else eod.get("observed_price")
        try:
            close = float(price)
        except Exception:
            continue
        observed_epoch = _epoch_seconds(eod.get("observed_epoch") or eod.get("observed_ts"))
        if observed_epoch is None:
            try:
                observed_epoch = datetime.fromisoformat(str(day)).replace(
                    hour=15, minute=30, tzinfo=KST
                ).timestamp()
            except Exception:
                continue
        observed_kst = datetime.fromtimestamp(observed_epoch, tz=timezone.utc).astimezone(KST)
        row = {
            "ts": int(observed_epoch),
            "raw_ts": observed_kst.strftime("%Y%m%d%H%M%S"),
            "open": close,
            "high": close,
            "low": close,
            "close": close,
            "volume": eod.get("volume"),
            "source": "opening_rank1_shadow.EOD",
            "eod_fallback": True,
        }
        return row, {
            "applied": True,
            "source": "opening_rank1_shadow.EOD",
            "source_path": str(path),
        }
    return None, {
        "applied": False,
        "reason": "matching_observed_opening_rank1_eod_not_found",
        "source_path": str(path),
    }
```

**Preserve/wrapper/monkeypatch:** read-only temp historical JSON; facade `_read_json,normalize_symbol,_as_dict,_epoch_seconds,datetime,timezone,KST,Path`; no market/network. Keep exact original SOURCE signature with thin delegation; Owner holds actual body and imports only stdlib/other non-SOURCE dependencies. Compare original/wrapper/Owner including patched globals, errors and output. Isolation: fake/temp only, never real state/order/network.

**New normal targeted test:** `tests/test_p15_rf035_15h_a8_opening_rank1_eod_fallback_r_owner.py`. Input → expected: temp JSON `evaluation/opening_rank1_shadow/2026-10-31/opening_rank1_shadow_daily.json` with `episodes:[{symbol:'005930',checkpoints:{EOD:{status:'observed',price:100,observed_epoch:1700000000}}}]`→row close=100.0, source `opening_rank1_shadow.EOD`, meta applied=True; missing symbol→applied=False. Also compare original pre-move golden output and wrapper/Owner; verify no original BODY remains in SOURCE. Run `python -m py_compile libs/reporting/post_exit_shadow_recap.py libs/reporting/post_exit_shadow_eod_fallback_projection.py` and `python -m unittest tests.test_p15_rf035_15h_a8_opening_rank1_eod_fallback_r_owner -v` (or equivalent exact-scope pytest); report actual exit0 and PASS count, never fabricate. Commit/push A-only code+test, refetch actor HEAD and exact blobs. On block report reason and continue handoff.

## FUTURE RESERVE — RESERVE_NOT_VERIFIED 0/6

Eight current A15 items are executable **not** reserves. C03 has not verified six additional safe future moves at the current actor SHA. The following are investigation leads **NOT ASSIGNMENTS**, do not execute: `q8_shadow_blocker_review.py::_dedupe_rows` (single-line delegation, likely KEEP), `::generate_q8_shadow_blocker_review` (file writes), `post_exit_shadow_recap.py::render_post_exit_shadow_trade_recap_md` and `::render_post_exit_shadow_daily_recap_md` (duplicate definitions, need conflict review), `::_refresh_trade_summary_from_recap` (in-memory mutation review), `q8_historical_review.py::write_q8_historical_review` (file writes). C03 must separately validate Owner/body/target/callers/effect/tests before any future assignment. VERIFIED reserve = 0, never claim 6.

## REPORT / CONTINUITY

Report #11: `ORDER_ID=A-20261031-15 | CANONICAL_HEAD | C02_BLOB | A_REMOTE_BEFORE→AFTER | A1..A8 STATUS | REAL_BODY_MOVES | SOURCE_BLOBS_BEFORE→AFTER | TARGET/TEST_BLOBS | NORMAL_COMMAND/EXIT/PASS | PUSH_REMOTE_SHA | FIRST_BLOCKER | NEXT`. Complete every safe item, even after first PASS or partial push failure; no time-filling if all completed. C03 document supply is not code G1/G2/G3 or RF DONE. RunLab Exited(255), RUN_SOURCE_SHA UNKNOWN: operational SAFETY_HOLD; no runtime manipulation.
