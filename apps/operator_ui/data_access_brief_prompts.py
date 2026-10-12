"""Operator Brief prompt/repair/line message construction and response line parsing (string building only; no LLM call).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _build_operator_brief_messages_r3_impl(compact_input, *, facade):
    contract = {
        "headline": "string",
        "commander_summary": "string",
        "strategist_summary": "string",
        "scanner_summary": "string",
        "monitor_summary": "string",
        "supervisor_summary": "string",
        "executor_summary": "string",
        "reporter_summary": "string",
        "operator_takeaways": ["string"],
        "executive_summary": "string",
        "scanner_reason": "string",
        "entry_summary": "string",
        "holding_summary": "string",
        "exit_plan_summary": "string",
        "risk_summary": "string",
        "next_checkpoints": ["string"],
    }
    system_prompt = (
        "당신은 한국 주식 운영자를 위한 운영 브리프 작성자입니다. "
        "응답은 반드시 JSON 객체 하나로만 반환하고, 모든 문장은 자연스러운 한국어로 작성하십시오. "
        "영어, 중국어, 일본어 문장을 섞지 마십시오. "
        "단, VWAP·RSI·ADX·종목코드처럼 시장에서 통용되는 표기만 예외로 허용합니다. "
        "설명 문장, 사고 과정, 지시문 반복을 출력하지 마십시오. "
        "출력은 반드시 '{'로 시작하고 '}'로 끝나는 단일 JSON 객체여야 합니다."
    )
    user_prompt = (
        "입력 데이터를 바탕으로 운영자가 10초 안에 상황을 이해할 수 있는 간결한 브리프를 작성하십시오.\n"
        "작성 규칙:\n"
        "- 운영 브리프는 현재 run/cycle의 즉시 상황 파악용 snapshot이어야 합니다.\n"
        "- 현재 상태, 현재 집중 종목, 전략가 근거, 스캐너 선정 이유, 모니터 blocker/이유, active stop 요약, guard/execution 상태, 다음 확인 항목을 우선 정리하십시오.\n"
        "- 긴 lifecycle 회고, execution 품질 회고, 긴 개선 포인트 섹션은 과하게 늘리지 마십시오.\n"
        "- 모든 설명값은 자연스러운 한국어 문장으로 작성하십시오.\n"
        "- entry_summary에는 반드시 분봉 기준 진입 근거 또는 진입 보류 사유를 명시하십시오.\n"
        "- 분봉 데이터가 없거나 진입 조건이 충분하지 않으면, 예시처럼 보수적으로 설명하십시오: "
        "\"이번 거래는 분봉 데이터가 확보되지 않아 진입 근거를 확인할 수 없었습니다. 따라서 신규 진입은 보류 대상으로 해석했습니다.\"\n"
        "- BUY가 이미 체결되고 lifecycle이 열려 있으면 no_position으로 단정하지 말고 현재 보유 상태를 설명하십시오.\n"
        "- SELL이 체결되어 lifecycle이 닫혀 있으면 어떤 청산 신호로 종료됐는지 명확히 설명하십시오.\n"
        "- scanner_reason에는 후보 순위 맥락과 최종 선정 이유를 2~3줄로만 간결하게 작성하십시오.\n"
        "- holding_summary에는 현재 포지션 상태와 지금 운영자가 알아야 할 핵심 감시 포인트만 담으십시오.\n"
        "- exit_plan_summary에는 현재 active stop/exit 축을 짧게 요약하십시오.\n"
        "- risk_summary에는 현재 리스크 요인을 2~3줄로 정리하십시오.\n"
        "- next_checkpoints에는 운영자가 다음에 확인할 핵심 체크포인트를 작성하십시오.\n"
        "- 점수 breakdown은 핵심 driver 1~3개만 언급하고 장황하게 나열하지 마십시오.\n"
        "- canonical_trade.available, reports/trades, source of truth, run-level 같은 내부 용어를 출력하지 마십시오.\n"
        "- If strategist evidence is present, mention candidate hints, market headlines, and selected-symbol headlines explicitly.\n"
        "- Explain the chain as strategist candidate hints -> scanner top ranks -> final symbol -> selection reason.\n"
        "- When stop policy layers are present, distinguish hard fail-safe stop, adaptive stop, effective stop, trailing stop, and take profit.\n"
        "- For no-trade states, use entry blockers and threshold shortfalls to explain what was missing.\n"
        f"계약: {facade.json.dumps(contract, ensure_ascii=False)}\n"
        f"입력: {facade.json.dumps(compact_input, ensure_ascii=False)}"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _build_operator_brief_repair_messages_r3_impl(raw_text, *, facade):
    contract = {
        "headline": "string",
        "commander_summary": "string",
        "strategist_summary": "string",
        "scanner_summary": "string",
        "monitor_summary": "string",
        "supervisor_summary": "string",
        "executor_summary": "string",
        "reporter_summary": "string",
        "operator_takeaways": ["string"],
        "executive_summary": "string",
        "scanner_reason": "string",
        "entry_summary": "string",
        "holding_summary": "string",
        "exit_plan_summary": "string",
        "risk_summary": "string",
        "next_checkpoints": ["string"],
    }
    return [
        {
            "role": "system",
            "content": (
                "운영 브리프를 계약에 맞는 JSON 객체 하나로 복구하십시오. "
                "모든 설명값은 자연스러운 한국어 문장으로 작성하고, 영어·중국어·일본어 문장은 결과에 남기지 마십시오. "
                "설명 문장이나 사고 과정은 출력하지 말고 JSON 객체만 반환하십시오."
            ),
        },
        {
            "role": "user",
            "content": (
                f"계약: {facade.json.dumps(contract, ensure_ascii=False)}\n"
                f"입력: {raw_text}"
            ),
        },
    ]


def _build_operator_brief_line_messages_r3_impl(compact_input, *, facade):
    return [
        {
            "role": "system",
            "content": (
                "JSON 생성이 실패하면 key:value 형식의 줄 단위 응답으로만 작성하십시오. "
                "각 값은 자연스러운 한국어 문장이어야 합니다."
            ),
        },
        {
            "role": "user",
            "content": (
                "아래 형식만 사용하십시오:\n"
                "headline: ...\n"
                "commander_summary: ...\n"
                "strategist_summary: ...\n"
                "scanner_summary: ...\n"
                "monitor_summary: ...\n"
                "supervisor_summary: ...\n"
                "executor_summary: ...\n"
                "reporter_summary: ...\n"
                "executive_summary: ...\n"
                "scanner_reason: ...\n"
                "entry_summary: ...\n"
                "holding_summary: ...\n"
                "exit_plan_summary: ...\n"
                "risk_summary: ...\n"
                "next_checkpoints: 항목1 | 항목2 | 항목3\n"
                "operator_takeaways: 항목1 | 항목2 | 항목3\n"
                f"입력: {facade.json.dumps(compact_input, ensure_ascii=False)}"
            ),
        },
    ]


def _parse_operator_brief_lines_r3_impl(text, *, facade):
    raw = str(text or "").strip()
    if not raw:
        return {}
    keys = [
        "headline",
        "commander_summary",
        "strategist_summary",
        "scanner_summary",
        "monitor_summary",
        "supervisor_summary",
        "executor_summary",
        "reporter_summary",
        "operator_takeaways",
        "executive_summary",
        "scanner_reason",
        "entry_summary",
        "holding_summary",
        "exit_plan_summary",
        "risk_summary",
        "next_checkpoints",
    ]
    out: Dict[str, Any] = {}
    for key in keys:
        pattern = rf"{key}\s*:\s*(.+)"
        matches = facade.re.findall(pattern, raw, flags=facade.re.IGNORECASE)
        if not matches:
            continue
        if key in {"operator_takeaways", "next_checkpoints"}:
            for candidate in reversed(matches):
                items = [item.strip(" -*") for item in str(candidate).split("|") if item.strip(" -*")]
                if not items:
                    continue
                if key == "operator_takeaways" and all(item.lower().startswith("item") for item in items):
                    continue
                out[key] = items[:5]
                break
            continue
        for candidate in reversed(matches):
            cleaned = str(candidate).strip().strip('"')
            if not cleaned:
                continue
            if cleaned in {"...", "?"}:
                continue
            out[key] = cleaned
            break
    return out


def _build_operator_brief_kr_facts_r3_impl(strategist, scanner, monitor, trade_report, *, facade):
    strategist_facts: List[str] = []
    market_regime = facade._operator_brief_label_ko(strategist.get("market_regime"))
    market_sentiment = facade._operator_brief_label_ko(strategist.get("market_sentiment"))
    playbook = facade._operator_brief_label_ko(strategist.get("playbook"))
    if market_regime or market_sentiment or playbook:
        strategist_facts.append(
            " / ".join(
                part
                for part in [
                    f"시장 상태 {market_regime}" if market_regime else "",
                    f"시장 심리 {market_sentiment}" if market_sentiment else "",
                    f"플레이북 {playbook}" if playbook else "",
                ]
                if part
            )
        )
    scanner_facts: List[str] = []
    selected_symbol = facade._trim_text(scanner.get("selected_symbol"), max_len=24)
    candidate_pool = facade._safe_int(scanner.get("candidate_pool_after_filter"), 0)
    score_total = scanner.get("score_total")
    confidence = scanner.get("confidence")
    if selected_symbol:
        parts = [selected_symbol]
        if candidate_pool > 0:
            parts.append(f"{candidate_pool}개 후보 중 선정")
        if isinstance(score_total, (int, float)):
            parts.append(f"총점 {facade._safe_float(score_total, 0.0):.3f}")
        if isinstance(confidence, (int, float)):
            parts.append(f"신뢰도 {facade._safe_float(confidence, 0.0):.2f}")
        scanner_facts.append(", ".join(parts))
    monitor_facts: List[str] = []
    posture = facade._operator_brief_label_ko(monitor.get("entry_pattern") or monitor.get("monitor_reason"))
    if posture:
        monitor_facts.append(f"모니터 관찰 신호 {posture}")
    lifecycle_status = facade._operator_brief_label_ko(trade_report.get("lifecycle_status"))
    trade_facts = [
        item
        for item in [
            f"거래 상태 {lifecycle_status}" if lifecycle_status else "",
            f"손익률 {facade._sanitize_operator_brief_text(trade_report.get('pnl_pct'))}" if str(trade_report.get("pnl_pct") or "").strip() else "",
        ]
        if item
    ]
    return {
        "strategist": strategist_facts[:3],
        "scanner": scanner_facts[:3],
        "monitor": monitor_facts[:3],
        "trade": trade_facts[:3],
    }


def _truncate_json_r3_impl(v, max_len, *, facade):
    try:
        s = facade.json.dumps(v, ensure_ascii=False, indent=2)
    except Exception:
        s = str(v)
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."
