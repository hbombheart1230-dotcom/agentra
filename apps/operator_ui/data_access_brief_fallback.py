"""Operator Brief deterministic fallback, failure brief and field salvage (pure text composition).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _fallback_operator_brief_r3_impl(detail, *, facade):
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    canonical_trade = facade._build_canonical_trade_brief_input(trade_report)
    strategist = detail.get("strategist") if isinstance(detail.get("strategist"), dict) else {}
    strategist_summary = strategist.get("summary") if isinstance(strategist.get("summary"), dict) else {}
    strategist_evidence = strategist.get("evidence") if isinstance(strategist.get("evidence"), dict) else {}
    raw_input = strategist_evidence.get("raw_input") if isinstance(strategist_evidence.get("raw_input"), dict) else {}
    global_inputs = raw_input.get("global_sentiment_inputs") if isinstance(raw_input.get("global_sentiment_inputs"), dict) else {}
    fear_index = global_inputs.get("fear_index") if isinstance(global_inputs.get("fear_index"), dict) else {}
    scanner = detail.get("scanner") if isinstance(detail.get("scanner"), dict) else {}
    scanner_summary = scanner.get("summary") if isinstance(scanner.get("summary"), dict) else {}
    scanner_trace = scanner.get("decision_trace") if isinstance(scanner.get("decision_trace"), dict) else {}
    selected = (scanner_trace.get("selected_candidate") or {}) if isinstance(scanner_trace.get("selected_candidate"), dict) else {}
    monitor = detail.get("monitor") if isinstance(detail.get("monitor"), dict) else {}
    monitor_summary = monitor.get("summary") if isinstance(monitor.get("summary"), dict) else {}
    monitor_trace = monitor.get("decision_trace") if isinstance(monitor.get("decision_trace"), dict) else {}
    supervisor = (detail.get("supervisor") or {}).get("verdict") if isinstance(detail.get("supervisor"), dict) else {}
    executor = (detail.get("executor") or {}).get("execution") if isinstance(detail.get("executor"), dict) else {}
    reporter = detail.get("reporter") if isinstance(detail.get("reporter"), dict) else {}
    prefer_runtime_reporter = facade._prefer_runtime_reporter_state(reporter)

    def _prefer_korean_summary(primary: Any, fallback_text: str) -> str:
        cleaned = facade._sanitize_operator_brief_text(primary)
        mixed_english_tokens = [
            "market ",
            "scanner ",
            "monitor ",
            "supervisor",
            "executor",
            "reporter",
            "playbook",
            "global sentiment",
            "rank #",
            "status=",
            "grade=",
        ]
        lowered = cleaned.lower()
        if facade._count_hangul_chars(cleaned) >= 4 and not any(token in lowered for token in mixed_english_tokens):
            return cleaned
        return fallback_text

    global_bits: List[str] = []
    if global_inputs.get("score") is not None:
        global_bits.append(f"\uae00\ub85c\ubc8c \uac10\uc131 \uc810\uc218 {facade._safe_float(global_inputs.get('score'), 0.0):.2f}")
    if fear_index.get("level") is not None:
        global_bits.append(f"VIX {facade._safe_float(fear_index.get('level'), 0.0):.2f}")
    macro_moves = global_inputs.get("macro_moves") if isinstance(global_inputs.get("macro_moves"), dict) else {}
    if macro_moves.get("dxy_pct") is not None:
        global_bits.append(f"\ub2ec\ub7ec \uc9c0\uc218 \ubcc0\ub3d9 {facade._safe_float(macro_moves.get('dxy_pct'), 0.0):.2f}%")

    selected_feature_snapshot = selected.get("feature_snapshot") if isinstance(selected.get("feature_snapshot"), dict) else {}
    feature_coverage = facade._normalized_feature_coverage(
        scanner.get("feature_coverage") if isinstance(scanner.get("feature_coverage"), dict) else {},
        selected_feature_snapshot,
    )
    _, fallback_chart_note = facade._chart_filter_status_and_note(feature_coverage)
    canonical_market_summary = str(canonical_trade.get("market_context_summary") or "").strip()
    canonical_selection_summary = str(canonical_trade.get("selection_summary") or "").strip()
    canonical_monitor_summary = str(canonical_trade.get("monitor_summary") or "").strip()
    canonical_guard_summary = str(canonical_trade.get("guard_summary") or "").strip()
    canonical_execution_summary = str(canonical_trade.get("execution_summary") or "").strip()
    canonical_reporter_summary = str(canonical_trade.get("reporter_summary") or "").strip()
    canonical_lifecycle_summary = str(canonical_trade.get("lifecycle_summary") or "").strip()
    canonical_report_summary = str(canonical_trade.get("report_summary") or "").strip()
    headline_action = str(canonical_trade.get("action") or trade_report.get("action") or "").strip().upper()
    headline_symbol = facade.normalize_symbol(
        canonical_trade.get("symbol") or trade_report.get("symbol") or selected.get("symbol") or scanner_summary.get("top_stock") or "",
        allow_test_symbols=True,
    )
    headline_fallback = " ".join(part for part in [headline_action, headline_symbol, "Operator Summary"] if str(part or "").strip())
    headline = (
        str(canonical_trade.get("headline") or "").strip()
        or headline_fallback
        or f"{detail.get('run_id') or '-'} Operator Summary"
    )

    phase = str(((detail.get("commander") or {}).get("phase") or "session")).strip() or "session"
    path_label = str(((detail.get("commander") or {}).get("path") or "-")).strip() or "-"
    playbook = facade._clean_brief_text(strategist_summary.get("playbook") or "")
    themes = facade._clean_brief_list(strategist_summary.get("themes"), limit=4)
    news_targets = facade._clean_brief_list(strategist_summary.get("news_query_targets"), limit=6)
    candidate_pool = int(scanner_summary.get("candidate_pool_after_filter") or 0)
    top_stock = facade._clean_brief_text(scanner_summary.get("top_stock") or selected.get("symbol") or headline_symbol or "-")
    selected_reason = facade._clean_brief_text(selected.get("why") or canonical_trade.get("selection_basis") or "")
    monitor_reason = facade._clean_brief_text(monitor_summary.get("monitor_reason") or monitor_trace.get("monitor_reason") or canonical_trade.get("monitor_summary") or "")
    exit_reason = facade._clean_brief_text(monitor_summary.get("exit_reason") or monitor_trace.get("exit_reason") or canonical_trade.get("exit_reason") or "")
    supervisor_allowed = bool(supervisor.get("allowed"))
    supervisor_reason = facade._clean_brief_text(supervisor.get("reason") or "")
    executor_action = facade._clean_brief_text(executor.get("action") or canonical_trade.get("action") or "NOOP")
    executor_symbol = facade._clean_brief_text(executor.get("symbol") or headline_symbol or "")
    executor_status = facade._clean_brief_text(executor.get("fill_status_summary") or executor.get("status") or canonical_trade.get("execution_mode_label") or "\uae30\ub85d \ub300\uae30")
    reporter_grade = facade._clean_brief_text(reporter.get("ai_run_grade") or "")
    reporter_run_summary = facade._clean_brief_text(reporter.get("ai_summary") or "")

    strategist_summary_text = _prefer_korean_summary(
        canonical_market_summary,
        (
            f"\uc804\ub7b5\uac00\ub294 {', '.join(global_bits) if global_bits else '\uc2dc\uc7a5 \uc785\ub825\uac12'}\uc744 \uba3c\uc800 \ud655\uc778\ud588\uace0, "
            f"\ub274\uc2a4 \uc810\uac80 \ubc94\uc704\ub294 {', '.join(news_targets) if news_targets else '\ud575\uc2ec \ud0c0\uae43 \uc911\uc2ec'}\uc774\uc5c8\uc2b5\ub2c8\ub2e4. "
            f"{', '.join(themes) if themes else '\uc8fc\uc694 \ud14c\ub9c8 \uc815\ubcf4'}\ub97c \ucc38\uace0\ud574 {playbook or '\uae30\ubcf8'} \uc804\ub7b5 \uad00\uc810\uc73c\ub85c \uc2dc\uc7a5\uc744 \ud574\uc11d\ud588\uc2b5\ub2c8\ub2e4."
        ),
    )
    scanner_summary_text = _prefer_korean_summary(
        canonical_selection_summary,
        (
            f"\uc2a4\uce90\ub108\ub294 {candidate_pool}\uac1c \ud6c4\ubcf4\ub97c \ube44\uad50\ud55c \ub4a4 {top_stock}\uc744 \uc6b0\uc120 \uac10\uc2dc \ub300\uc0c1\uc73c\ub85c \uc62c\ub838\uc2b5\ub2c8\ub2e4. "
            f"{selected_reason or '\uc800\uc7a5\ub41c \uc120\uc815 \uc0ac\uc720\ub294 \uc81c\ud55c\uc801\uc774\uc9c0\ub9cc \uc774\ud6c4 \uad00\ub9ac \uae30\ub85d\uc740 \ud655\uc778\ub429\ub2c8\ub2e4.'}"
        ),
    )
    monitor_summary_text = _prefer_korean_summary(
        canonical_monitor_summary,
        (
            f"\ubaa8\ub2c8\ud130\ub294 {monitor_reason or '\ubcf4\uc720 \uad00\ub9ac \uc2e0\ud638'}\ub97c \ud655\uc778\ud588\uace0, "
            f"{exit_reason or '\ucd94\uac00 \uccad\uc0b0 \uc0ac\uc720 \ubbf8\uae30\ub85d'} \uae30\uc900\uc744 \uc911\uc2ec\uc73c\ub85c \ud310\ub2e8\ud588\uc2b5\ub2c8\ub2e4."
        ),
    )
    supervisor_summary_text = _prefer_korean_summary(
        canonical_guard_summary,
        (
            f"\uac10\ub3c5 \ub2e8\uacc4\uc5d0\uc11c\ub294 {'\uc8fc\ubb38\uc744 \ud5c8\uc6a9\ud588\uc2b5\ub2c8\ub2e4' if supervisor_allowed else '\uc8fc\ubb38\uc744 \ucc28\ub2e8\ud588\uc2b5\ub2c8\ub2e4'}."
            + (f" \ud310\ub2e8 \uc0ac\uc720\ub294 {supervisor_reason}\uc785\ub2c8\ub2e4." if supervisor_reason else "")
        ),
    )
    executor_summary_text = _prefer_korean_summary(
        canonical_execution_summary,
        (
            f"\uc2e4\ud589 \ub2e8\uacc4\uc5d0\uc11c\ub294 {executor_symbol or '\ud574\ub2f9 \uc885\ubaa9'}\uc5d0 \ub300\ud574 {executor_action} \uc694\uccad\uc774 \uae30\ub85d\ub418\uc5c8\uace0, "
            f"\ud604\uc7ac \uc0c1\ud0dc\ub294 {executor_status}\uc785\ub2c8\ub2e4."
        ),
    )
    reporter_summary_text = _prefer_korean_summary(
        "" if prefer_runtime_reporter else canonical_reporter_summary,
        f"\ub9ac\ud3ec\ud130 \ud3c9\uac00\ub294 \ub4f1\uae09 {reporter_grade or '-'}\uc774\uba70, {reporter_run_summary or '\ub2f9\uc77c \uc885\ud569 \ud3c9\uac00\ub294 \uc544\uc9c1 \uc5f0\uacb0\ub418\uc9c0 \uc54a\uc558\uc2b5\ub2c8\ub2e4.'}",
    )

    takeaways: List[str] = []
    if strategist_summary_text:
        takeaways.append(strategist_summary_text)
    if candidate_pool > 0:
        takeaways.append(
            f"\uc2a4\uce90\ub108\ub294 {candidate_pool}\uac1c \ud6c4\ubcf4 \uc911 {top_stock}\uc744 \uc6b0\uc120 \uac10\uc2dc \ub300\uc0c1\uc73c\ub85c \uc62c\ub838\uace0, \ucc28\ud2b8\u00b7\uc218\uae09 \uadfc\uac70\ub294 {fallback_chart_note} \uc218\uc900\uc73c\ub85c \ub0a8\uc544 \uc788\uc2b5\ub2c8\ub2e4."
        )
    elif canonical_trade.get("filters_summary"):
        takeaways.append(_prefer_korean_summary(canonical_trade.get("filters_summary"), "\uc774\ubc88 \uc2e4\ud589\uc5d0\uc11c\ub294 \ud6c4\ubcf4 \ube44\uad50 \ub370\uc774\ud130\uac00 \ucda9\ubd84\ud788 \ub0a8\uc9c0 \uc54a\uc544 \uc2a4\uce90\ub108 \ube44\uad50 \uadfc\uac70\ub97c \ubcf4\uc218\uc801\uc73c\ub85c \ud574\uc11d\ud588\uc2b5\ub2c8\ub2e4."))
    else:
        takeaways.append("\uc774\ubc88 \uc2e4\ud589\uc5d0\uc11c\ub294 \ud6c4\ubcf4 \ube44\uad50 \ub370\uc774\ud130\uac00 \ucda9\ubd84\ud788 \ub0a8\uc9c0 \uc54a\uc544 \uc2a4\uce90\ub108 \ube44\uad50 \uadfc\uac70\ub97c \ubcf4\uc218\uc801\uc73c\ub85c \ud574\uc11d\ud588\uc2b5\ub2c8\ub2e4.")
    if canonical_lifecycle_summary:
        takeaways.append(_prefer_korean_summary(canonical_lifecycle_summary, "\uac70\ub798 \uacbd\uacfc\ub294 \uc77c\ubd80\ub9cc \ub0a8\uc544 \uc788\uc5b4 \ubcf4\uc720\u00b7\uccad\uc0b0 \uae30\ub85d \uc911\uc2ec\uc73c\ub85c \uc815\ub9ac\ud588\uc2b5\ub2c8\ub2e4."))
    elif canonical_report_summary:
        takeaways.append(_prefer_korean_summary(canonical_report_summary, "\uac70\ub798 \uacbd\uacfc\ub294 \uc77c\ubd80\ub9cc \ub0a8\uc544 \uc788\uc5b4 \ubcf4\uc720\u00b7\uccad\uc0b0 \uae30\ub85d \uc911\uc2ec\uc73c\ub85c \uc815\ub9ac\ud588\uc2b5\ub2c8\ub2e4."))
    else:
        takeaways.append(f"\uc2e4\ud589 \uacb0\uacfc\ub294 {executor_action} \uae30\uc900\uc73c\ub85c \uae30\ub85d\ub418\uc5c8\uace0, \uccb4\uacb0 \uc0c1\ud0dc\ub294 {executor_status}\ub85c \ud655\uc778\ub429\ub2c8\ub2e4.")

    return {
        "status": "fallback",
        "model": "",
        "headline": headline,
        "commander_summary": f"\uc9c0\ud718 \ud750\ub984\uc740 {phase} \ub2e8\uacc4\uc5d0\uc11c {path_label} \uacbd\ub85c\ub85c \uc2e4\ud589\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
        "strategist_summary": strategist_summary_text,
        "scanner_summary": scanner_summary_text,
        "monitor_summary": monitor_summary_text,
        "supervisor_summary": supervisor_summary_text,
        "executor_summary": executor_summary_text,
        "reporter_summary": reporter_summary_text,
        "operator_takeaways": takeaways[:5],
    }


def _failure_operator_brief_r3_impl(detail, *, status, model, reason, failure_status, facade):
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    canonical_trade = facade._build_canonical_trade_brief_input(trade_report)
    shared_facts = canonical_trade.get("shared_facts") if isinstance(canonical_trade.get("shared_facts"), dict) else {}
    symbol = facade.normalize_symbol(
        trade_report.get("symbol")
        or (((detail.get("scanner") or {}).get("summary") or {}).get("top_stock") if isinstance(detail.get("scanner"), dict) else "")
        or "",
        allow_test_symbols=True,
    )
    action = str(shared_facts.get("action") or "unavailable").strip().upper()
    if action not in {"BUY", "SELL", "HOLD", "WAIT"}:
        action = "WAIT"
    return {
        "status": str(status or "fallback"),
        "model": str(model or ""),
        "headline": " ".join(part for part in ["AI Brief Failed", action, symbol] if str(part or "").strip()),
        "commander_summary": "",
        "strategist_summary": "",
        "scanner_summary": "",
        "monitor_summary": "",
        "supervisor_summary": "",
        "executor_summary": "",
        "reporter_summary": "",
        "operator_takeaways": [],
        "reason": str(reason or "brief_generation_failed"),
        "failure": {
            "status": str(failure_status or status or "error"),
            "reason": str(reason or "brief_generation_failed"),
        },
    }


def _salvage_operator_brief_fields_r3_impl(text, *, facade):
    raw = str(text or "")
    if not raw.strip():
        return {}
    fields = [
        "headline",
        "commander_summary",
        "strategist_summary",
        "scanner_summary",
        "monitor_summary",
        "supervisor_summary",
        "executor_summary",
        "reporter_summary",
    ]
    out: Dict[str, Any] = {}
    for key in fields:
        pattern = rf'"{key}"\s*:\s*"((?:[^"\\]|\\.)*)"'
        match = facade.re.search(pattern, raw, flags=facade.re.DOTALL)
        if not match:
            continue
        try:
            out[key] = facade.json.loads('"' + match.group(1) + '"')
        except Exception:
            out[key] = match.group(1).replace('\\"', '"')
    takeaways_match = facade.re.search(r'"operator_takeaways"\s*:\s*\[(.*)', raw, flags=facade.re.DOTALL)
    if takeaways_match:
        items = facade.re.findall(r'"((?:[^"\\]|\\.)*)"', takeaways_match.group(1), flags=facade.re.DOTALL)
        cleaned: List[str] = []
        for item in items[:5]:
            try:
                cleaned.append(facade.json.loads('"' + item + '"'))
            except Exception:
                cleaned.append(item.replace('\\"', '"'))
        if cleaned:
            out["operator_takeaways"] = cleaned
    return out
