"""Operator Brief payload normalisation, Korean-language and internal-marker sanitation (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _normalize_operator_brief_payload_r3_impl(brief, detail, *, llm_response_artifact, facade):
    out = dict(brief or {})
    trade_report = detail.get("trade_report") if isinstance(detail.get("trade_report"), dict) else {}
    canonical_trade = facade._build_canonical_trade_brief_input(trade_report)
    canonical_shared_facts = (
        canonical_trade.get("shared_facts")
        if isinstance(canonical_trade.get("shared_facts"), dict)
        else {}
    )
    shared_facts = out.get("shared_facts") if isinstance(out.get("shared_facts"), dict) else {}
    normalized_shared_facts = dict(canonical_shared_facts)
    normalized_shared_facts.update(shared_facts)
    normalized_shared_facts["data_source"] = {
        **(canonical_shared_facts.get("data_source") if isinstance(canonical_shared_facts.get("data_source"), dict) else {}),
        **(shared_facts.get("data_source") if isinstance(shared_facts.get("data_source"), dict) else {}),
    }
    out["shared_facts"] = normalized_shared_facts
    out["schema_version"] = str(out.get("schema_version") or "operator_brief.v1")
    out["trade_id"] = str(
        out.get("trade_id")
        or trade_report.get("trade_id")
        or canonical_trade.get("trade_id")
        or ""
    )
    out["run_id"] = str(out.get("run_id") or detail.get("run_id") or trade_report.get("run_id") or "")

    normalized_artifact = (
        llm_response_artifact if isinstance(llm_response_artifact, dict) else out.get("llm_response_artifact")
    )
    normalized_artifact = dict(normalized_artifact) if isinstance(normalized_artifact, dict) else {}
    model_info = (
        normalized_artifact.get("model_info")
        if isinstance(normalized_artifact.get("model_info"), dict)
        else {}
    )
    raw_llm_status = str(
        out.get("llm_brief_status")
        or normalized_artifact.get("llm_status")
        or normalized_artifact.get("status")
        or out.get("status")
        or ""
    ).strip()
    llm_status_default = "skipped" if raw_llm_status == "skipped" else "fallback"
    llm_brief_status = facade.canonical_llm_status(raw_llm_status or llm_status_default, default=llm_status_default)
    generation = out.get("generation") if isinstance(out.get("generation"), dict) else {}
    generation_status = str(generation.get("status") or "").strip().lower()
    if not generation_status:
        if llm_brief_status in {"ok", "repaired", "salvaged"}:
            generation_status = llm_brief_status
        elif llm_brief_status == "skipped":
            generation_status = "skipped"
        else:
            generation_status = "deterministic"
    generation_mode = str(generation.get("mode") or "").strip()
    if not generation_mode:
        generation_mode = "llm" if generation_status in {"ok", "repaired", "salvaged"} else "deterministic"
    generation_model = str(
        generation.get("model")
        or out.get("model")
        or model_info.get("model")
        or ""
    ).strip()
    generation_reason = str(
        generation.get("reason")
        or out.get("reason")
        or ((out.get("failure") or {}).get("reason") if isinstance(out.get("failure"), dict) else "")
        or ""
    ).strip()
    normalized_generation = dict(generation)
    normalized_generation["status"] = generation_status
    normalized_generation["mode"] = generation_mode
    normalized_generation["model"] = generation_model
    normalized_generation["reason"] = generation_reason
    out["generation"] = normalized_generation
    out["llm_brief_status"] = llm_brief_status
    failure = out.get("failure") if isinstance(out.get("failure"), dict) else {}
    missing_fields = [str(x or "") for x in list(out.get("required_keys_missing") or []) if str(x or "").strip()]
    completeness_score = float(out.get("completeness_score") or 0.0)
    out["reason_code"] = str(
        out.get("reason_code")
        or out.get("reason")
        or failure.get("status")
        or ""
    ).strip()
    out["provenance"] = str(
        out.get("provenance")
        or ("llm" if llm_brief_status in {"ok", "repaired", "salvaged"} else "fallback")
    ).strip()
    out["completeness"] = completeness_score
    out["missing_fields"] = missing_fields
    return out


def _sanitize_operator_brief_result_r3_impl(detail, candidate, fallback, *, facade):
    out = dict(candidate or {})
    for key in (
        "headline",
        "commander_summary",
        "strategist_summary",
        "scanner_summary",
        "monitor_summary",
        "supervisor_summary",
        "executor_summary",
        "reporter_summary",
    ):
        cleaned = facade._prefer_richer_brief_text(out.get(key), fallback.get(key))
        if key == "monitor_summary" and facade._should_replace_brief_monitor_summary(detail, cleaned):
            cleaned = facade._sanitize_operator_brief_text(fallback.get(key))
        out[key] = cleaned

    for key in (
        "executive_summary",
        "scanner_reason",
        "entry_summary",
        "holding_summary",
        "exit_plan_summary",
        "risk_summary",
    ):
        out[key] = facade._sanitize_operator_brief_text(out.get(key))

    next_checkpoints: List[str] = []
    seen_checkpoints: set[str] = set()
    for value in list(out.get("next_checkpoints") or []):
        cleaned = facade._sanitize_operator_brief_text(value)
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered in seen_checkpoints:
            continue
        next_checkpoints.append(cleaned)
        seen_checkpoints.add(lowered)
        if len(next_checkpoints) >= 5:
            break
    if next_checkpoints:
        out["next_checkpoints"] = next_checkpoints

    candidate_takeaways: List[str] = []
    fallback_takeaways: List[str] = []
    seen_takeaways: set[str] = set()

    def _collect_takeaways(values: Any, target: List[str]) -> None:
        for value in list(values or []):
            cleaned = facade._sanitize_operator_brief_text(value)
            if not cleaned:
                continue
            lowered = cleaned.lower()
            if lowered in seen_takeaways:
                continue
            target.append(cleaned)
            seen_takeaways.add(lowered)
            if len(target) >= 5:
                break

    _collect_takeaways(out.get("operator_takeaways"), candidate_takeaways)
    _collect_takeaways(fallback.get("operator_takeaways"), fallback_takeaways)
    candidate_hangul = sum(1 for item in candidate_takeaways if facade._count_hangul_chars(item) > 0)
    fallback_hangul = sum(1 for item in fallback_takeaways if facade._count_hangul_chars(item) > 0)
    if (
        len(candidate_takeaways) < 4
        or (fallback_hangul > candidate_hangul and len(fallback_takeaways) >= len(candidate_takeaways))
        or (sum(len(item) for item in candidate_takeaways) < max(120, sum(len(item) for item in fallback_takeaways) // 2))
    ):
        out["operator_takeaways"] = fallback_takeaways[:5] or candidate_takeaways[:5]
    else:
        out["operator_takeaways"] = candidate_takeaways[:5]
    return out


def _sanitize_operator_brief_text_r3_impl(text, *, facade):
    cleaned = facade._trim_text(text, max_len=1000)
    if not cleaned:
        return ""
    cleaned = facade.unicodedata.normalize("NFKC", cleaned).replace("\ufeff", "").replace("\x00", " ")
    if facade._contains_internal_brief_marker(cleaned):
        return ""
    cleaned = facade.re.sub(r"[\u0000-\u001f\u007f]", " ", cleaned)
    replacements = [
        ("minute-candle", "분봉"),
        ("minute candle", "분봉"),
        ("defensive_exit", "방어적 청산"),
        ("no_position", "포지션 없음"),
        ("No trigger yet", "아직 청산 신호가 확인되지 않았습니다."),
        ("Peak drawdown", "고점 대비 하락"),
        ("Hard stop", "고정 손절 기준"),
        ("Adaptive stop", "상황 대응형 손절 기준"),
        ("Take profit", "목표 수익 실현 기준"),
        ("Regime", "시장 상태"),
        ("Universe scanned", "비교 후보 수"),
        ("Selected rank", "선정 순위"),
        ("Posture", "현재 포지션 판단"),
        ("Trigger", "감시 신호"),
        ("Exit trigger", "청산 신호"),
    ]
    for src, dst in replacements:
        cleaned = facade.re.sub(facade.re.escape(src), dst, cleaned, flags=facade.re.IGNORECASE)
    normalized_replacements = (
        (r"\bnot[_ ]captured\b", "기록되지 않음"),
        (r"\bnot[_ ]available\b", "확인되지 않음"),
        (r"\bunavailable\b", "확인되지 않음"),
        (r"\bunknown\b", "확인되지 않음"),
        (r"\bno position\b", "포지션 없음"),
        (r"\bstill open\b", "아직 보유 중"),
        (r"\bstop[- ]loss trigger\b", "손절 트리거"),
        (r"\btake[- ]profit trigger\b", "목표 수익 실현 트리거"),
        (r"\brisk gate failure\b", "리스크 게이트 실패"),
        (r"\babnormal volatility expansion\b", "변동성 급확대"),
        (r"\bsentiment\b", "시장 심리"),
        (r"\bplaybook\b", "플레이북"),
        (r"\baligned with\b", "정렬 기준"),
        (r"\btop_value\b", "거래대금 상위"),
        (r"\btop_volume\b", "거래량 상위"),
        (r"\bsector_theme\b", "섹터/테마 정렬"),
        (r"\belevated_vix\b", "VIX 경계"),
        (r"\byield_rise\b", "금리 상승"),
        (r"\bpullback\b", "눌림"),
        (r"\bturnover\b", "회전율"),
        (r"\bvolume\b", "거래량"),
        (r"\bdrawdown\b", "하락폭"),
        (r"\btake_profit\b", "목표 수익 실현 기준"),
        (r"\bhard_stop\b", "고정 손절 기준"),
        (r"\bor\b", "또는"),
        (r"\bpullback_structure_above_vwap_with_confirmation\b", "VWAP 상단 눌림 확인"),
        (r"\bpullback_vwap_hold\b", "VWAP 상단 눌림 유지"),
        (r"\bbreakout_vwap_hold\b", "VWAP 상향 돌파 유지"),
        (r"\bintraday_low_break\b", "장중 저점 이탈"),
        (r"\btrailing stop\b", "추적 손절 기준"),
    )
    for regex_pattern, replacement_text in normalized_replacements:
        cleaned = facade.re.sub(regex_pattern, replacement_text, cleaned, flags=facade.re.IGNORECASE)
    cleaned = facade.re.sub(r"\bBUY\b", "매수", cleaned)
    cleaned = facade.re.sub(r"\bSELL\b", "매도", cleaned)
    cleaned = facade.re.sub(r"\bHOLD\b", "보유 유지", cleaned)
    cleaned = facade.re.sub(r"\bWAIT\b", "진입 보류", cleaned)
    if facade._contains_forbidden_brief_script(cleaned):
        return ""
    cleaned = facade.re.sub(r"\s+", " ", cleaned).strip(" -:|")
    return cleaned


def _operator_brief_language_ok_r3_impl(candidate, *, facade):
    text_fields = [
        "headline",
        "commander_summary",
        "strategist_summary",
        "scanner_summary",
        "monitor_summary",
        "supervisor_summary",
        "executor_summary",
        "reporter_summary",
        "executive_summary",
        "scanner_reason",
        "entry_summary",
        "holding_summary",
        "exit_plan_summary",
        "risk_summary",
    ]
    total_hangul = 0
    total_forbidden = 0

    def _forbidden_count(value: str) -> int:
        return len(facade.re.findall(r"[\u3040-\u30ff\u4e00-\u9fff]", value))

    for key in text_fields:
        value = str(candidate.get(key) or "").strip()
        if not value:
            continue
        forbidden_count = _forbidden_count(value)
        total_forbidden += forbidden_count
        if forbidden_count > 0:
            return False
        hangul_count = facade._count_hangul_chars(value)
        total_hangul += hangul_count
        ascii_letters = len(facade.re.findall(r"[A-Za-z]", value))
        if hangul_count == 0 and ascii_letters >= 12:
            return False

    for key in ("operator_takeaways", "next_checkpoints"):
        for item in list(candidate.get(key) or []):
            value = str(item or "").strip()
            if not value:
                continue
            forbidden_count = _forbidden_count(value)
            total_forbidden += forbidden_count
            if forbidden_count > 0:
                return False

    if total_forbidden > 0:
        return False
    return total_hangul > 0


def _operator_brief_label_ko_r3_impl(value, *, facade):
    raw = facade._trim_text(value, max_len=220)
    if not raw:
        return ""
    lowered = raw.strip().lower()
    mapping = {
        "neutral": "중립",
        "bullish": "강세",
        "bearish": "약세",
        "mixed": "혼조",
        "pullback": "눌림",
        "breakout": "돌파",
        "reversion": "되돌림",
        "leader": "주도주 집중",
        "conservative": "보수적",
        "defensive_exit": "방어적 청산 중심",
        "hold_through_noise": "노이즈 허용 보유",
        "kiwoom_market_data": "실시간 시장 데이터",
        "integrated_chain": "통합 체인",
        "session": "장중 세션",
    }
    if lowered in mapping:
        return mapping[lowered]
    return facade._sanitize_operator_brief_text(raw)
