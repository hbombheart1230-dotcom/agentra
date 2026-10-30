# Agentra FAST-3 — C02 A-20261031-00 | 8 NEW RF-035 SOURCE BODY MOVEs

**Authority/preflight:** canonical integration at start `be3ca1b6a796120d22472914517dd9b802e333da`; A owner remote `4c0db15690c15f8e3609a3d4befa2ee91af0d5f3`; OLD_C02_BLOB `e26c5c04e3422e3eb2dd987933d6e31a1c55fffc`. Issue #11 6525028712 and C04/C05 #36 6525447463/6525532064 prove previous A1–A8 all REMOTE_DONE (31 scoped normal PASS; integrated `06e39040`). Never reassign or rerun them. Eight below are NEW, six promoted from verified unused reserve and two additional directly inspected safe read-only helpers. RF-035 Owner=Claude A, B read-only. All SOURCE Git blobs match A and integration; eight TARGET paths were verified absent (404) on A and integration before this issuance. This document is a task supply, NOT code G1/G2/G3.

**Single-document execution:** Read ONLY this C02 and actual code/test paths below; do not read D00/RF/queue/C03 or select your own tasks. Pin fresh canonical HEAD, C02 blob, A HEAD and SOURCE blob before touching each item; if changed, reconcile against latest actual remote state and do not overwrite. Work solely on `work/p15-a-reporter-pure-20261021`, only the SOURCE/TARGET and NEW targeted test for each item. Move exact original calculation BODY (not copy) to single new Owner, leave exact original signature and docstring in a thin wrapper delegating to Owner. Where specified use `facade=sys.modules[__name__]` and a keyword-only `facade` in Owner to preserve call-time monkeypatch; no reverse import or duplicate body. Preserve all caller signatures, output bytes/order/exception behavior, imports and state semantics. New Owner needs its own typing/Path imports; no tests may use live paths. Do ALL A1–A8; a blocked item never cancels other independent safe items. Normal targeted pytest or reproducible stdlib smoke exit0 per changed item; -O/full peer/hosted CI not mandatory. `py_compile` alone is not G2. Code/test only commit, normal push to A, then refetch remote A HEAD and exact SOURCE/TARGET/TEST blobs. If HTTPS credentials block push, record LOCAL_ONLY/PUSH_BLOCKED and preserve tree; no force push, no unreviewed tree recreation. No production files, real orders, Broker/Guard/Step5C/UEF, RunLab, operational report/state writes, or A/B cross-owner modifications. C04 integrates; C05 owns G1/G2/G3/DONE.

## A1 — RF-035 | SOURCE `libs/reporting/daily_report_generator.py::_build_trade_report_integrity` blob `eee37fe6d8c97b23cafbff184142bfcbda4a2944` L87 → TARGET `libs/reporting/daily_report_generator_integrity_projection.py::_build_trade_report_integrity` (new, verified 404)

**Exact original SOURCE BODY to MOVE (75 source lines, unique definition):**

```python
def _build_trade_report_integrity(
    reports_root: Path,
    day: str,
    trade_index: List[Dict[str, Any]],
    broker_alignment: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    missing: List[Dict[str, Any]] = []
    broker_closed_symbols = _broker_closed_symbols_from_alignment(broker_alignment)
    broker_closed_report_open: List[Dict[str, Any]] = []
    for item in trade_index:
        if not isinstance(item, dict):
            continue
        trade_id = str(item.get("trade_id") or "").strip()
        if not trade_id:
            continue
        symbol = normalize_symbol(item.get("symbol"), allow_test_symbols=True)
        lifecycle_status = str(
            item.get("status")
            or item.get("trade_lifecycle_status")
            or item.get("lifecycle_status")
            or ""
        ).strip().lower()
        trade_dir = _find_trade_dir(reports_root, day, trade_id)
        reports_dir = trade_dir / "reports" if trade_dir else None
        checks = {
            "ai_trade_summary_input_json": bool(reports_dir and (reports_dir / "ai_trade_summary_input.json").exists()),
            "ai_trade_summary_json": bool(reports_dir and (reports_dir / "ai_trade_summary.json").exists()),
            "ai_trade_summary_md": bool(reports_dir and (reports_dir / "ai_trade_summary.md").exists()),
        }
        row = {
            "trade_id": trade_id,
            "symbol": symbol or str(item.get("symbol") or ""),
            "lifecycle_status": lifecycle_status,
            "trade_dir": str(trade_dir) if trade_dir else "",
            **checks,
        }
        rows.append(row)
        if symbol and symbol in broker_closed_symbols and lifecycle_status not in ("closed", "done", "completed"):
            broker_closed_report_open.append(
                {
                    "trade_id": trade_id,
                    "symbol": symbol,
                    "lifecycle_status": lifecycle_status or "unknown",
                    "issue": "broker_day_trade_closed_but_report_open",
                }
            )
        if not all(checks.values()):
            missing.append(
                {
                    "trade_id": trade_id,
                    "symbol": row["symbol"],
                    "missing": [key for key, value in checks.items() if not value],
                }
            )
    status = "ok"
    if missing:
        status = "missing_reports"
    if broker_closed_report_open:
        status = "broker_lifecycle_mismatch" if not missing else "missing_reports_and_broker_lifecycle_mismatch"
    return {
        "schema_version": "trade_report_integrity.v1",
        "expected_trade_count": len([x for x in trade_index if isinstance(x, dict) and str(x.get("trade_id") or "").strip()]),
        "checked_trade_count": len(rows),
        "summary_md_count": sum(1 for row in rows if row.get("ai_trade_summary_md")),
        "summary_json_count": sum(1 for row in rows if row.get("ai_trade_summary_json")),
        "summary_input_count": sum(1 for row in rows if row.get("ai_trade_summary_input_json")),
        "missing_count": len(missing),
        "broker_closed_report_open_count": len(broker_closed_report_open),
        "status": status,
        "missing": missing,
        "broker_closed_report_open": broker_closed_report_open,
    }
```

**Wrapper/callers/monkeypatch:** facade._broker_closed_symbols_from_alignment, facade._find_trade_dir, facade.normalize_symbol must be resolved at call time; preserve report key/count/status ordering and missing reports; do not query broker. Preserve original public/source signature and any existing imports; SOURCE wrapper only delegates to new Owner. Do not execute a live report, LLM, trading or operational command.

**New normal targeted test:** `tests/test_p15_rf035_00h_a1__build_trade_report_integrity_owner.py`. Fake/tmp fixture and expected output: empty trade_index, None broker_alignment -> expected_trade_count=0, checked_trade_count=0, status='ok'; one fake tmp trade with no report files -> missing_count=1, status='missing_reports'; fake broker closed symbol with open lifecycle -> broker_closed_report_open_count=1 and combined mismatch status; monkeypatch helper sentinel. Record before-original vs Owner vs wrapper exact return/exception and patch-seam parity. Run `python -m py_compile libs/reporting/daily_report_generator.py libs/reporting/daily_report_generator_integrity_projection.py`, then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_00h_a1__build_trade_report_integrity_owner.py` (or equivalent .venv python; if pytest unavailable, stdlib normal smoke with exact command/exit). On success commit only scoped SOURCE/TARGET/test, normal push A, refetch remote HEAD and three blobs; on conflict or safety blocker record exact first blocker and **continue A2**. No old same-SHA PASS reruns.

## A2 — RF-035 | SOURCE `libs/reporting/metrics_report_generator.py::_iter_events` blob `1f0fa8dd454ce0d32645bbe6de7a6e1f3c587954` L40 → TARGET `libs/reporting/metrics_report_generator_read_projection.py::_iter_events` (new, verified 404)

**Exact original SOURCE BODY to MOVE (20 source lines, unique definition):**

```python
def _iter_events(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []

    def gen() -> Iterable[Dict[str, Any]]:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if isinstance(obj, dict):
                    yield obj

    return gen()
```

**Wrapper/callers/monkeypatch:** facade.json.loads resolved during iteration, not generator construction; preserve missing-path [] vs generator, skip non-dict JSON, malformed lines and exception behavior. Preserve original public/source signature and any existing imports; SOURCE wrapper only delegates to new Owner. Do not execute a live report, LLM, trading or operational command.

**New normal targeted test:** `tests/test_p15_rf035_00h_a2__iter_events_owner.py`. Fake/tmp fixture and expected output: missing tmp path -> []; JSONL valid dict, array, invalid line, dict -> exactly two dicts in order; patch facade.json.loads to count lazy calls; assert no open before iteration. Record before-original vs Owner vs wrapper exact return/exception and patch-seam parity. Run `python -m py_compile libs/reporting/metrics_report_generator.py libs/reporting/metrics_report_generator_read_projection.py`, then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_00h_a2__iter_events_owner.py` (or equivalent .venv python; if pytest unavailable, stdlib normal smoke with exact command/exit). On success commit only scoped SOURCE/TARGET/test, normal push A, refetch remote HEAD and three blobs; on conflict or safety blocker record exact first blocker and **continue A3**. No old same-SHA PASS reruns.

## A3 — RF-035 | SOURCE `libs/reporting/llm_daily_summary.py::_build_messages` blob `e847ee3941da571732364e3f2d0d5741f93ce363` L29 → TARGET `libs/reporting/llm_daily_summary_message_projection.py::_build_messages` (new, verified 404)

**Exact original SOURCE BODY to MOVE (29 source lines, unique definition):**

```python
def _build_messages(state: Dict[str, Any], policy: Dict[str, Any]) -> List[Dict[str, Any]]:
    day = str(state.get("eod_day") or policy.get("day") or "")
    report = dict(state.get("daily_report") or {})
    approvals = report.get("approvals")
    denials = report.get("denials")
    runs = report.get("runs")

    # Keep prompt compact; we only need a short manager-friendly summary.
    sys = {
        "role": "system",
        "content": (
            "You are a trading system reporter. "
            "Summarize the day's automated decisions succinctly in Korean. "
            "No financial advice. Use bullet points." 
        ),
    }
    user = {
        "role": "user",
        "content": (
            f"Day: {day}\n"
            f"approvals: {approvals}\n"
            f"denials: {denials}\n"
            f"runs: {runs}\n\n"
            "Write a short summary (max 6 bullets) and a one-line takeaway."
        ),
    }
    return [sys, user]
```

**Wrapper/callers/monkeypatch:** Pure message construction; preserve exact original prompt text/whitespace and message ordering, no LLM call; source wrapper delegates directly. Preserve original public/source signature and any existing imports; SOURCE wrapper only delegates to new Owner. Do not execute a live report, LLM, trading or operational command.

**New normal targeted test:** `tests/test_p15_rf035_00h_a3__build_messages_owner.py`. Fake/tmp fixture and expected output: state={'eod_day':'2026-10-30','daily_report':{'approvals':2,'denials':1,'runs':3}}, policy={'day':'wrong'} -> two messages, first role system, second role user containing Day: 2026-10-30 and approvals: 2; missing state -> same original two messages; compare exact strings. Record before-original vs Owner vs wrapper exact return/exception and patch-seam parity. Run `python -m py_compile libs/reporting/llm_daily_summary.py libs/reporting/llm_daily_summary_message_projection.py`, then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_00h_a3__build_messages_owner.py` (or equivalent .venv python; if pytest unavailable, stdlib normal smoke with exact command/exit). On success commit only scoped SOURCE/TARGET/test, normal push A, refetch remote HEAD and three blobs; on conflict or safety blocker record exact first blocker and **continue A4**. No old same-SHA PASS reruns.

## A4 — RF-035 | SOURCE `libs/reporting/strategist_llm_summary.py::_utc_now_iso` blob `b75edd9c2823f525556a15a6dc79b49d562b2f20` L38 → TARGET `libs/reporting/strategist_llm_summary_clock_projection.py::_utc_now_iso` (new, verified 404)

**Exact original SOURCE BODY to MOVE (4 source lines, unique definition):**

```python
def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
```

**Wrapper/callers/monkeypatch:** facade.datetime and facade.timezone at call time, preserve UTC timezone and .isoformat() exactly; no real clock use in fixture. Preserve original public/source signature and any existing imports; SOURCE wrapper only delegates to new Owner. Do not execute a live report, LLM, trading or operational command.

**New normal targeted test:** `tests/test_p15_rf035_00h_a4__utc_now_iso_owner.py`. Fake/tmp fixture and expected output: patch source.datetime.now(timezone.utc) to fixed 2026-10-30T00:00:00+00:00 -> exact '2026-10-30T00:00:00+00:00'; compare wrapper and Owner. Record before-original vs Owner vs wrapper exact return/exception and patch-seam parity. Run `python -m py_compile libs/reporting/strategist_llm_summary.py libs/reporting/strategist_llm_summary_clock_projection.py`, then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_00h_a4__utc_now_iso_owner.py` (or equivalent .venv python; if pytest unavailable, stdlib normal smoke with exact command/exit). On success commit only scoped SOURCE/TARGET/test, normal push A, refetch remote HEAD and three blobs; on conflict or safety blocker record exact first blocker and **continue A5**. No old same-SHA PASS reruns.

## A5 — RF-035 | SOURCE `libs/reporting/market_regime_rail_review.py::load_latest_macro_snapshot` blob `778c8f2dfc4657a2a5f12e89adca0f55c9a01b23` L25 → TARGET `libs/reporting/market_regime_rail_review_read_projection.py::load_latest_macro_snapshot` (new, verified 404)

**Exact original SOURCE BODY to MOVE (9 source lines, unique definition):**

```python
def load_latest_macro_snapshot(day: str, *, root: Path = Path("data/logs/macro_indicators")) -> Dict[str, Any]:
    path = root / str(day)[:10] / "latest.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"available": False, "path": str(path), "error": "macro_snapshot_unavailable"}
    return {**dict(payload), "available": True, "path": str(path)}
```

**Wrapper/callers/monkeypatch:** Preserve exact signature/default root=Path('data/logs/macro_indicators'), read-only path, facade.json.loads at call time and broad exception; no Guard or market feed. Preserve original public/source signature and any existing imports; SOURCE wrapper only delegates to new Owner. Do not execute a live report, LLM, trading or operational command.

**New normal targeted test:** `tests/test_p15_rf035_00h_a5_load_latest_macro_snapshot_owner.py`. Fake/tmp fixture and expected output: tmp root/day/latest.json missing -> {'available':False,'path':exact_tmp_path,'error':'macro_snapshot_unavailable'}; valid {'x':1} -> x=1,available=True,path=tmp; invalid JSON -> same unavailable shape; monkeypatch facade.json.loads. Record before-original vs Owner vs wrapper exact return/exception and patch-seam parity. Run `python -m py_compile libs/reporting/market_regime_rail_review.py libs/reporting/market_regime_rail_review_read_projection.py`, then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_00h_a5_load_latest_macro_snapshot_owner.py` (or equivalent .venv python; if pytest unavailable, stdlib normal smoke with exact command/exit). On success commit only scoped SOURCE/TARGET/test, normal push A, refetch remote HEAD and three blobs; on conflict or safety blocker record exact first blocker and **continue A6**. No old same-SHA PASS reruns.

## A6 — RF-035 | SOURCE `libs/reporting/strategist_llm_summary.py::render_strategist_llm_summary_markdown` blob `b75edd9c2823f525556a15a6dc79b49d562b2f20` L583 → TARGET `libs/reporting/strategist_llm_summary_render_projection.py::render_strategist_llm_summary_markdown` (new, verified 404)

**Exact original SOURCE BODY to MOVE (167 source lines, ACTIVE LAST definition; earlier shadowed definition KEEP):**

```python
def render_strategist_llm_summary_markdown(payload: Dict[str, Any]) -> str:
    meta = _as_dict(payload.get("llm_meta"))
    readout = _as_dict(payload.get("operator_readout"))
    stage_decision = _as_dict(payload.get("stage_decision"))
    if bool(stage_decision.get("is_stage_specific")):
        return _render_stage_specific_summary_markdown_clean(payload)

    frame = _as_dict(payload.get("strategy_frame"))
    detail = _as_dict(payload.get("strategy_detail"))
    changes = _as_dict(payload.get("policy_changes"))
    entry = _as_dict(payload.get("monitor_entry_policy"))
    memory = _as_dict(payload.get("memory_usage"))
    news = _as_dict(payload.get("news_usage"))
    refresh = _as_dict(payload.get("strategy_refresh_trace"))
    horizon = _as_dict(payload.get("strategy_horizon_feedback"))
    hold = _as_dict(horizon.get("expected_hold_window"))
    exit_guidance = _as_dict(horizon.get("exit_guidance"))
    handoff = _as_dict(horizon.get("monitor_handoff"))
    selected_themes = _as_list(frame.get("selected_themes"))
    theme_text = ", ".join(str(x) for x in selected_themes) if selected_themes else "-"
    watch = _as_dict(detail.get("candidate_watch_policy"))
    tactical_strategy = _text(detail.get("tactical_strategy"), "")
    strategy_scores = _as_dict(detail.get("strategy_scores"))
    rejected_reasons = _as_dict(detail.get("rejected_strategy_reasons"))

    lines: List[str] = [
        f"# Strategist LLM Summary ({_text(meta.get('day'), '-')})",
        "",
        "---",
        "",
        "## 전략가 원문 해석 출력",
        "",
        "> 아래 내용은 전략가 LLM 응답과 canonical 전략가 산출물을 사람이 읽기 좋게 재배열한 것입니다.",
        "",
        f"- 상태: {_text(meta.get('status'))} / model={_text(meta.get('model'))}",
        "",
        "### 전략 프레임",
        "",
        f"- 플레이북: **{_text(frame.get('playbook'))}**",
        f"- 선택 테마: {theme_text}",
        f"- 테마 선택 모드: {_text(frame.get('theme_selection_mode'))}",
        f"- fallback 사유: {_text(frame.get('fallback_reason'))}",
        "",
        "**전략가 rationale**",
        "",
        _text(frame.get("rationale")),
        "",
        "### 전략 디테일",
        "",
        f"- 전략 강화 필드: {_strategy_patch_status_clean(detail)}",
        f"- 플레이북 흐름: {_playbook_flow_label(detail)}",
        f"- LLM 요청 플레이북: {_text(detail.get('llm_requested_playbook'))}",
        f"- 최종 플레이북: {_text(detail.get('final_playbook'))}",
        f"- 선택 전술: {_text(detail.get('tactical_strategy'))}",
        f"- 후보 감시 제안: {_watch_scope_label_clean(watch) or '-'}",
        "",
        "#### 전략 점수",
        "",
        *_strategy_score_lines_clean(strategy_scores, selected=tactical_strategy),
        "",
        "#### 제외 전략 이유",
        "",
        *_rejected_strategy_lines(rejected_reasons, selected=tactical_strategy),
        "",
        "### 메모리 사용",
        "",
        *_memory_usage_lines_clean(memory),
        "",
        "### 뉴스 사용",
        "",
        *_news_usage_lines_clean(news),
        "",
        *_quality_audit_lines(payload),
        "### 정책 조정",
        "",
        _directive_line("플레이북", _as_dict(changes.get("playbook_action"))),
        _directive_line("진입 정책", _as_dict(changes.get("entry_policy_action"))),
        _directive_line("모니터 초점", _as_dict(changes.get("monitor_focus_action"))),
        _directive_line("성과 bias", _as_dict(changes.get("selected_symbol_bias_action"))),
        _directive_line("refresh", _as_dict(changes.get("refresh_action"))),
        "",
        "### 전략 Refresh 흐름",
        "",
        f"- 요약: {_text(refresh.get('summary'))}",
        "",
    ]
    lines.extend(_bullet_lines(_as_list(refresh.get("bullets"))))
    lines += ["", "#### 단계", ""]
    stages = _as_list(refresh.get("stages"))
    stage_line_count = 0
    for stage in stages:
        row = _as_dict(stage)
        if not row:
            continue
        stage_line_count += 1
        lines.append(
            f"- {_text(row.get('stage'))}: {_text(row.get('label'))}; "
            f"effective={row.get('effective')}; {_text(row.get('summary'))}"
        )
    if stage_line_count == 0:
        lines.append("- -")

    lines += [
        "",
        "### 모니터 진입 정책",
        "",
        f"- enabled: {entry.get('enabled')}",
        f"- timeframe_minutes: {entry.get('timeframe_minutes')}",
        f"- volume_ratio_min: {entry.get('volume_ratio_min')}",
        f"- vwap 확장 허용: min={entry.get('min_extended_from_vwap_pct')}, max={entry.get('max_extended_from_vwap_pct')}",
        f"- pullback 범위: min={entry.get('pullback_min_pct')}, max={entry.get('pullback_max_pct')}",
        f"- reclaim_tolerance_pct: {entry.get('reclaim_tolerance_pct')}",
        f"- intent_cooldown_sec: {entry.get('intent_cooldown_sec')}",
        f"- require_vwap_reclaim / require_rebound: {entry.get('require_vwap_reclaim')} / {entry.get('require_rebound')}",
        "",
        "### 보유 Horizon",
        "",
        f"- strategy_horizon: {_text(horizon.get('strategy_horizon'))}",
        f"- hold_window_sec: min={hold.get('min_sec')}, target={hold.get('target_sec')}, max={hold.get('max_sec')}",
        f"- preferred_exit: {_text(handoff.get('preferred_exit') or exit_guidance.get('profit_take_style'))}",
        f"- hold_bias: {_text(handoff.get('hold_bias'))}",
        f"- do_not_force_hold: {handoff.get('do_not_force_hold')}",
        f"- allow_early_exit: {exit_guidance.get('allow_early_exit')}",
        "",
        "#### 무효화 조건",
        "",
        *_bullet_lines(_as_list(horizon.get("invalidation_conditions"))),
        "",
        "---",
        "",
        "## 운영자 검토 요약",
        "",
        "> 아래 내용은 전략가 원문을 기준으로 한 deterministic 검토입니다. 추가 LLM 호출은 포함하지 않습니다.",
        "",
        f"- 검토 결론: **{_text(readout.get('headline'))}**",
        f"- 주요 원인: {_text(readout.get('root_cause'))}",
        "",
        "### 잘 된 점",
        "",
        *_bullet_lines(_as_list(readout.get("good_points"))),
        "",
        "### 문제점",
        "",
        *_bullet_lines(_as_list(readout.get("issues"))),
        "",
        "### 권고 액션",
        "",
        *_bullet_lines(_as_list(readout.get("recommended_actions"))),
        "",
        "### 검증 포인트",
        "",
        *_bullet_lines(_as_list(readout.get("validation_questions"))),
        "",
        "---",
        "",
        "## 근거",
        "",
        f"- source_response_json: `{payload.get('source_response_json')}`",
        f"- source_canonical_strategist_json: `{payload.get('source_canonical_strategist_json')}`",
        f"- run_id: `{_text(meta.get('run_id'), '')}`",
        f"- saved_at: `{_text(meta.get('saved_at'), '')}`",
        f"- generated_at: `{_text(payload.get('generated_at'), '')}`",
        "",
    ]
    return "\n".join(lines)
```

**Wrapper/callers/monkeypatch:** ONLY the active SECOND top-level definition (~L583) is moved; earlier shadowed definition (~L318) stays untouched and counts as zero. Every source helper (_as_dict,_as_list,_text,_strategy_patch_status_clean,_playbook_flow_label,_watch_scope_label_clean,_strategy_score_lines_clean,_rejected_strategy_lines,_memory_usage_lines_clean,_news_usage_lines_clean,_quality_audit_lines,_directive_line,_bullet_lines,_render_stage_specific_summary_markdown_clean and all other module helpers) must resolve through facade at invocation; no Owner->SOURCE import. Exact Korean markdown bytes/newline/section order. Preserve original public/source signature and any existing imports; SOURCE wrapper only delegates to new Owner. Do not execute a live report, LLM, trading or operational command.

**New normal targeted test:** `tests/test_p15_rf035_00h_a6_render_strategist_llm_summary_markdown_owner.py`. Fake/tmp fixture and expected output: empty fake payload -> compare complete exact markdown string before/after/Owner; fake llm_meta.day, strategy_frame.playbook, operator_readout -> exact text; stage_decision.is_stage_specific=True with patched facade._render_stage_specific_summary_markdown_clean returning 'STAGE_SENTINEL' -> exact sentinel; no files/network. Record before-original vs Owner vs wrapper exact return/exception and patch-seam parity. Run `python -m py_compile libs/reporting/strategist_llm_summary.py libs/reporting/strategist_llm_summary_render_projection.py`, then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_00h_a6_render_strategist_llm_summary_markdown_owner.py` (or equivalent .venv python; if pytest unavailable, stdlib normal smoke with exact command/exit). On success commit only scoped SOURCE/TARGET/test, normal push A, refetch remote HEAD and three blobs; on conflict or safety blocker record exact first blocker and **continue A7**. No old same-SHA PASS reruns.

## A7 — RF-035 | SOURCE `libs/reporting/daily_report_generator.py::_load_operator_summary_snapshot` blob `eee37fe6d8c97b23cafbff184142bfcbda4a2944` L58 → TARGET `libs/reporting/daily_report_generator_operator_projection.py::_load_operator_summary_snapshot` (new, verified 404)

**Exact original SOURCE BODY to MOVE (17 source lines, unique definition):**

```python
def _load_operator_summary_snapshot(events_path: Path, out_dir: Path, day: str) -> Dict[str, Any]:
    paths = daily_artifact_paths(out_dir, day)
    payload = build_operator_daily_summary_payload(
        events_path,
        out_dir,
        day=day,
        metrics_report_dir=out_dir / "metrics",
        m30_post_golive_dir=out_dir / "milestones" / "m30_post_golive",
        m30_golive_dir=out_dir / "milestones" / "m30_golive",
        m31_slo_incident_dir=out_dir / "m31_slo_incident",
    )
    snapshot = build_operator_summary_snapshot_from_payload(payload)
    snapshot["report_json_path"] = str(paths["operator_summary_json"])
    snapshot["report_md_path"] = str(paths["operator_summary_md"])
    return snapshot
```

**Wrapper/callers/monkeypatch:** facade.daily_artifact_paths, facade.build_operator_daily_summary_payload, facade.build_operator_summary_snapshot_from_payload resolved at call time; no actual report writes, mocked builders only; preserve metrics/milestones path arguments and output keys. Preserve original public/source signature and any existing imports; SOURCE wrapper only delegates to new Owner. Do not execute a live report, LLM, trading or operational command.

**New normal targeted test:** `tests/test_p15_rf035_00h_a7__load_operator_summary_snapshot_owner.py`. Fake/tmp fixture and expected output: patch facade.daily_artifact_paths to return fake tmp operator_summary_json/md, payload builder to record events_path/out_dir/day and return {'ok':1}, snapshot builder to return {'status':'ok'}; expect report_json_path/report_md_path exact tmp strings and status ok; fake builder exception must propagate identically. Record before-original vs Owner vs wrapper exact return/exception and patch-seam parity. Run `python -m py_compile libs/reporting/daily_report_generator.py libs/reporting/daily_report_generator_operator_projection.py`, then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_00h_a7__load_operator_summary_snapshot_owner.py` (or equivalent .venv python; if pytest unavailable, stdlib normal smoke with exact command/exit). On success commit only scoped SOURCE/TARGET/test, normal push A, refetch remote HEAD and three blobs; on conflict or safety blocker record exact first blocker and **continue A8**. No old same-SHA PASS reruns.

## A8 — RF-035 | SOURCE `libs/reporting/llm_daily_summary.py::_is_dry_run` blob `e847ee3941da571732364e3f2d0d5741f93ce363` L25 → TARGET `libs/reporting/llm_daily_summary_env_projection.py::_is_dry_run` (new, verified 404)

**Exact original SOURCE BODY to MOVE (4 source lines, unique definition):**

```python
def _is_dry_run() -> bool:
    return str(os.getenv("DRY_RUN", "0")).strip() in ("1", "true", "True")
```

**Wrapper/callers/monkeypatch:** facade.os.getenv at invocation time; read only DRY_RUN, do not change enable/disable policy, no LLM invocation; source exact-signature wrapper. Preserve original public/source signature and any existing imports; SOURCE wrapper only delegates to new Owner. Do not execute a live report, LLM, trading or operational command.

**New normal targeted test:** `tests/test_p15_rf035_00h_a8__is_dry_run_owner.py`. Fake/tmp fixture and expected output: patch source.os.getenv('DRY_RUN','0') -> '1','true','True' => True; 'TRUE','0','',None => False per original string conversion; spy that getter called at use time; compare Owner and wrapper. Record before-original vs Owner vs wrapper exact return/exception and patch-seam parity. Run `python -m py_compile libs/reporting/llm_daily_summary.py libs/reporting/llm_daily_summary_env_projection.py`, then `python -m pytest -q -p no:cacheprovider tests/test_p15_rf035_00h_a8__is_dry_run_owner.py` (or equivalent .venv python; if pytest unavailable, stdlib normal smoke with exact command/exit). On success commit only scoped SOURCE/TARGET/test, normal push A, refetch remote HEAD and three blobs; on conflict or safety blocker record exact first blocker and **continue Aend/report**. No old same-SHA PASS reruns.

## Future reserve — 6/6 VERIFIED design (NOT executable in current A order)

**Source/ownership proof:** RF-035 implementation coverage explicitly lists `libs/reporting/daily_report_runtime/markdown.py` as Claude-A-owned; SOURCE current A/integration blob `8755975bc5d78e26b48c36179556011498a476d9` identical, 6 distinct non-wrapper top-level function BODIES directly inspected. Five unique TARGET module paths were checked 404 on A and integration. All are deterministic dict→Markdown lines; no file reads/writes, real account/order, network, Guard, Step5C, UEF or RunLab effects. These are **future** items only, not A1–A8, not tested, not code/G1/G2/G3, and not self-selectable by A. Revalidate blobs/target absence before promotion.

### R1 RF-035 | `libs/reporting/daily_report_runtime/markdown.py::render_operator_summary_snapshot` blob `8755975bc5d78e26b48c36179556011498a476d9` L14 → `libs/reporting/daily_report_runtime/markdown_snapshot_projection.py::render_operator_summary_snapshot` (new 404)

Original SOURCE BODY (21 lines) to move only in a **future** C03-issued order:
```python
def render_operator_summary_snapshot(
    operator_summary_snapshot: Dict[str, Any],
    *,
    include_system_status: bool,
) -> List[str]:
    executive = (
        operator_summary_snapshot.get("executive_summary")
        if isinstance(operator_summary_snapshot.get("executive_summary"), dict)
        else {}
    )
    if not executive.get("summary_lines"):
        return []

    lines = ["", "## Operator Summary Snapshot", ""]
    if include_system_status and executive.get("system_status"):
        lines.append(f"- system_status: **{executive['system_status']}**")
    for line in executive.get("summary_lines") or []:
        lines.append(f"- {line}")
    return lines
```
Wrapper: exact original signature delegates to Owner, none; no reverse import or duplicate calculation. Targeted fake normal test design: pure fake {'executive_summary':{'summary_lines':['ok'],'system_status':'healthy'}} + include_system_status True -> header and system_status and '- ok'; False omits status; empty -> []. `tests/test_p15_rf035_reserve_r1_render_operator_summary_snapshot_owner.py` (future only). Preserve original output/exception/monkeypatch parity; py_compile + normal scoped pytest/stdlib smoke exit0 and A push/refetch required **after** future issuance. On conflict skip to next safe reserve item, report BLOCKED.

### R2 RF-035 | `libs/reporting/daily_report_runtime/markdown.py::render_route_and_narrative_sections` blob `8755975bc5d78e26b48c36179556011498a476d9` L35 → `libs/reporting/daily_report_runtime/markdown_route_projection.py::render_route_and_narrative_sections` (new 404)

Original SOURCE BODY (26 lines) to move only in a **future** C03-issued order:
```python
def render_route_and_narrative_sections(payload: Dict[str, Any]) -> List[str]:
    route_summary = payload.get("route_summary") if isinstance(payload.get("route_summary"), dict) else {}
    narrative_policy = (
        payload.get("narrative_axis_policy")
        if isinstance(payload.get("narrative_axis_policy"), dict)
        else narrative_axis_policy()
    )
    return [
        "",
        "## Route Provenance",
        "",
        f"- route_source: `{route_summary.get('route_source') or '-'}`",
        f"- route_source_run_count: **{int(route_summary.get('route_source_run_count') or 0)}**",
        f"- route_source_missing_count: **{int(route_summary.get('route_source_missing_count') or 0)}**",
        f"- route_source_breakdown: `{json.dumps(route_summary.get('route_source_breakdown') or {}, ensure_ascii=False)}`",
        f"- route_selected_total: `{json.dumps(route_summary.get('route_selected_total') or {}, ensure_ascii=False)}`",
        "",
        "## Narrative Axis Policy",
        "",
        f"- entry_primary_for: `{narrative_policy.get('entry_primary_for') or []}`",
        f"- exit_primary_for: `{narrative_policy.get('exit_primary_for') or []}`",
        f"- mixed_only_for_ambiguous_cases: **{bool(narrative_policy.get('mixed_only_for_ambiguous_cases'))}**",
        f"- runtime_semantics_unchanged: **{bool(narrative_policy.get('runtime_semantics_unchanged'))}**",
    ]
```
Wrapper: exact original signature delegates to Owner, facade.json.dumps and facade.narrative_axis_policy at call time; no reverse import or duplicate calculation. Targeted fake normal test design: fake route_source='sim', counts 1/0 and narrative_axis_policy dict -> deterministic route/narrative lines; missing policy -> patched facade.narrative_axis_policy. `tests/test_p15_rf035_reserve_r2_render_route_and_narrative_sections_owner.py` (future only). Preserve original output/exception/monkeypatch parity; py_compile + normal scoped pytest/stdlib smoke exit0 and A push/refetch required **after** future issuance. On conflict skip to next safe reserve item, report BLOCKED.

### R3 RF-035 | `libs/reporting/daily_report_runtime/markdown.py::render_trade_report_integrity` blob `8755975bc5d78e26b48c36179556011498a476d9` L61 → `libs/reporting/daily_report_runtime/markdown_integrity_projection.py::render_trade_report_integrity` (new 404)

Original SOURCE BODY (39 lines) to move only in a **future** C03-issued order:
```python
def render_trade_report_integrity(payload: Dict[str, Any]) -> List[str]:
    integrity = payload.get("trade_report_integrity") if isinstance(payload.get("trade_report_integrity"), dict) else {}
    if not integrity:
        return []
    missing = integrity.get("missing") if isinstance(integrity.get("missing"), list) else []
    broker_closed_report_open = (
        integrity.get("broker_closed_report_open")
        if isinstance(integrity.get("broker_closed_report_open"), list)
        else []
    )
    lines = [
        "",
        "## Trade Report Integrity",
        "",
        f"- status: **{str(integrity.get('status') or 'unknown').upper()}**",
        f"- expected_trade_count: **{int(integrity.get('expected_trade_count') or 0)}**",
        f"- summary_md_count: **{int(integrity.get('summary_md_count') or 0)}**",
        f"- summary_json_count: **{int(integrity.get('summary_json_count') or 0)}**",
        f"- summary_input_count: **{int(integrity.get('summary_input_count') or 0)}**",
        f"- missing_count: **{int(integrity.get('missing_count') or 0)}**",
        f"- broker_closed_report_open_count: **{int(integrity.get('broker_closed_report_open_count') or 0)}**",
    ]
    for row in broker_closed_report_open[:10]:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"- broker closed but report open `{row.get('trade_id') or '-'}` {row.get('symbol') or ''}: "
            f"status=`{row.get('lifecycle_status') or 'unknown'}`"
        )
    for row in missing[:10]:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"- missing `{row.get('trade_id') or '-'}` {row.get('symbol') or ''}: "
            f"`{json.dumps(row.get('missing') or [], ensure_ascii=False)}`"
        )
    return lines
```
Wrapper: exact original signature delegates to Owner, facade.json.dumps at call time; no reverse import or duplicate calculation. Targeted fake normal test design: empty payload -> []; fake status='missing_reports',missing_count=1,missing=[{'trade_id':'T1','missing':['ai_trade_summary_md']}] -> exact status and missing lines; skip non-dict rows. `tests/test_p15_rf035_reserve_r3_render_trade_report_integrity_owner.py` (future only). Preserve original output/exception/monkeypatch parity; py_compile + normal scoped pytest/stdlib smoke exit0 and A push/refetch required **after** future issuance. On conflict skip to next safe reserve item, report BLOCKED.

### R4 RF-035 | `libs/reporting/daily_report_runtime/markdown.py::render_policy_surface_sections` blob `8755975bc5d78e26b48c36179556011498a476d9` L153 → `libs/reporting/daily_report_runtime/markdown_policy_projection.py::render_policy_surface_sections` (new 404)

Original SOURCE BODY (79 lines) to move only in a **future** C03-issued order:
```python
def render_policy_surface_sections(payload: Dict[str, Any]) -> List[str]:
    policy_surface_summary = (
        payload.get("policy_surface_quality_summary")
        if isinstance(payload.get("policy_surface_quality_summary"), dict)
        else {}
    )
    policy_surface_exec = (
        payload.get("policy_surface_quality_executive_summary")
        if isinstance(payload.get("policy_surface_quality_executive_summary"), dict)
        else {}
    )
    chart_structure_summary = (
        payload.get("chart_structure_decision_hint_summary")
        if isinstance(payload.get("chart_structure_decision_hint_summary"), dict)
        else {}
    )
    chart_structure_exec = (
        payload.get("chart_structure_decision_hint_executive_summary")
        if isinstance(payload.get("chart_structure_decision_hint_executive_summary"), dict)
        else {}
    )
    policy_surface_source = (
        payload.get("policy_surface_quality_source")
        if isinstance(payload.get("policy_surface_quality_source"), dict)
        else {}
    )
    chart_structure_source = (
        payload.get("chart_structure_decision_hint_source")
        if isinstance(payload.get("chart_structure_decision_hint_source"), dict)
        else {}
    )
    chart_structure_examples = (
        chart_structure_summary.get("applied_examples")
        if isinstance(chart_structure_summary.get("applied_examples"), list)
        else []
    )

    lines = [
        "",
        "## Policy Surface Executive Summary",
        "",
        f"- status: **{str(policy_surface_exec.get('status') or 'unknown').upper()}**",
        f"- headline: {str(policy_surface_exec.get('headline') or 'Policy surface unknown')}",
        "",
        "## Policy Surface Quality",
        "",
        f"- schema_available_rate: **{float(policy_surface_summary.get('schema_available_rate') or 0.0):.4f}**",
        f"- normalized_policy_rate: **{float(policy_surface_summary.get('normalized_policy_rate') or 0.0):.4f}**",
        f"- invalid_spec_rate: **{float(policy_surface_summary.get('invalid_spec_rate') or 0.0):.4f}**",
        f"- total_invalid_specs: **{int(policy_surface_summary.get('total_invalid_specs') or 0)}**",
        f"- run_count: **{int(policy_surface_source.get('run_count') or 0)}**",
        "",
        "## Chart Structure Decision Hint Executive Summary",
        "",
        f"- status: **{str(chart_structure_exec.get('status') or 'unknown').upper()}**",
        f"- headline: {str(chart_structure_exec.get('headline') or 'Chart structure guard unknown')}",
        "",
        "## Chart Structure Decision Hint",
        "",
        f"- available_run_count: **{int(chart_structure_summary.get('available_run_count') or 0)}**",
        f"- applied_count: **{int(chart_structure_summary.get('applied_count') or 0)}**",
        f"- applied_rate: **{float(chart_structure_summary.get('applied_rate') or 0.0):.4f}**",
        f"- top_blocking_features: `{json.dumps(chart_structure_summary.get('top_blocking_features') or [], ensure_ascii=False)}`",
        f"- run_count: **{int(chart_structure_source.get('run_count') or 0)}**",
    ]
    if chart_structure_examples:
        lines += ["", "## Chart Structure Decision Hint Applied Examples", ""]
        for example in chart_structure_examples[:3]:
            if not isinstance(example, dict):
                continue
            lines.append(
                f"- `{example.get('run_id') or '-'}` "
                f"[{str(example.get('entry_style') or '-').upper()}] "
                f"{example.get('reason_transition') or '-'} "
                f"blockers=`{json.dumps(example.get('blocking_features') or [], ensure_ascii=False)}`"
            )
    return lines
```
Wrapper: exact original signature delegates to Owner, facade.json.dumps at call time; no reverse import or duplicate calculation. Targeted fake normal test design: empty payload -> stable section headings and zero counts; fake applied_examples=[{'run_id':'R1','entry_style':'pullback'}] -> example line; invalid int count -> same ValueError. `tests/test_p15_rf035_reserve_r4_render_policy_surface_sections_owner.py` (future only). Preserve original output/exception/monkeypatch parity; py_compile + normal scoped pytest/stdlib smoke exit0 and A push/refetch required **after** future issuance. On conflict skip to next safe reserve item, report BLOCKED.

### R5 RF-035 | `libs/reporting/daily_report_runtime/markdown.py::render_top_issues` blob `8755975bc5d78e26b48c36179556011498a476d9` L232 → `libs/reporting/daily_report_runtime/markdown_operator_projection.py::render_top_issues` (new 404)

Original SOURCE BODY (16 lines) to move only in a **future** C03-issued order:
```python
def render_top_issues(operator_summary_snapshot: Dict[str, Any]) -> List[str]:
    top_issues = (
        operator_summary_snapshot.get("top_issues")
        if isinstance(operator_summary_snapshot.get("top_issues"), list)
        else []
    )
    if not top_issues:
        return []
    lines = ["", "## Top Issues", ""]
    for issue in top_issues:
        if not isinstance(issue, dict):
            continue
        lines.append(f"- [{issue.get('severity') or '-'}] {issue.get('code') or '-'}: {issue.get('detail') or '-'}")
    return lines
```
Wrapper: exact original signature delegates to Owner, pure, no facade; no reverse import or duplicate calculation. Targeted fake normal test design: empty snapshot -> []; fake top_issues=[{'severity':'warn','code':'X','detail':'demo'}] -> ['','## Top Issues','','- [warn] X: demo']; invalid rows skipped. `tests/test_p15_rf035_reserve_r5_render_top_issues_owner.py` (future only). Preserve original output/exception/monkeypatch parity; py_compile + normal scoped pytest/stdlib smoke exit0 and A push/refetch required **after** future issuance. On conflict skip to next safe reserve item, report BLOCKED.

### R6 RF-035 | `libs/reporting/daily_report_runtime/markdown.py::render_recommended_operator_actions` blob `8755975bc5d78e26b48c36179556011498a476d9` L248 → `libs/reporting/daily_report_runtime/markdown_operator_projection.py::render_recommended_operator_actions` (new 404)

Original SOURCE BODY (14 lines) to move only in a **future** C03-issued order:
```python
def render_recommended_operator_actions(operator_summary_snapshot: Dict[str, Any]) -> List[str]:
    recommended_actions = (
        operator_summary_snapshot.get("recommended_operator_actions")
        if isinstance(operator_summary_snapshot.get("recommended_operator_actions"), list)
        else []
    )
    if not recommended_actions:
        return []
    lines = ["", "## Recommended Operator Actions", ""]
    for action in recommended_actions:
        lines.append(f"- {action}")
    return lines
```
Wrapper: exact original signature delegates to Owner, pure, no facade; no reverse import or duplicate calculation. Targeted fake normal test design: empty snapshot -> []; fake recommended_operator_actions=['A','B'] -> ['','## Recommended Operator Actions','','- A','- B']. `tests/test_p15_rf035_reserve_r6_render_recommended_operator_actions_owner.py` (future only). Preserve original output/exception/monkeypatch parity; py_compile + normal scoped pytest/stdlib smoke exit0 and A push/refetch required **after** future issuance. On conflict skip to next safe reserve item, report BLOCKED.

## Required A report

Issue #11: `ORDER_ID=A-20261031-00 | CANONICAL_HEAD | C02_BLOB | A_REMOTE_BEFORE/AFTER | A1..A8 IMPLEMENTED/BLOCKED | SOURCE_BLOBS_BEFORE/AFTER | TARGET_BLOBS | TARGETED_NORMAL_COMMAND/EXIT | PUSH_VERIFIED/LOCAL_ONLY | FIRST_BLOCKER | NEXT | START_KST/END_KST` (measured only). Do not claim RF DONE, code G3, or runtime validation.
