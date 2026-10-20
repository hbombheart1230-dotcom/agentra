from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from libs.runtime.quant.market_regime_observation import classify_market_regime_rail
from libs.runtime.strategist_input_quality import build_risk_off_exception_policy
import sys as _summary_sys

from libs.reporting import strategist_llm_summary_markdown_projection as _summary_markdown  # P1.5 BATCH04-A owner
from libs.reporting import strategist_llm_summary_quality_projection as _summary_quality  # P1.5 BATCH04-A owner


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_dict(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return list(value) if isinstance(value, list) else []


def _text(value: Any, default: str = "-") -> str:
    raw = str(value or "").strip()
    return raw if raw else default


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


_STAGE_META_BY_CALL_KIND: Dict[str, Dict[str, Any]] = {
    "selected_symbol_tactical_refresh": {
        "stage_index": 2,
        "stage_name": "selected_symbol_tactical_refresh",
        "stage_component": "strategist_stage2_selected_symbol",
    },
    "stale_intraday_hold_review": {
        "stage_index": 3,
        "stage_name": "stale_intraday_hold_review",
        "stage_component": "strategist_stage3_hold_review",
    },
    "end_of_day_carry_review": {
        "stage_index": 4,
        "stage_name": "end_of_day_carry_review",
        "stage_component": "strategist_stage4_carry_review",
    },
}


def _infer_call_kind(payload: Dict[str, Any], raw: Dict[str, Any], meta: Dict[str, Any] | None = None) -> str:
    sidecar = _as_dict(meta)
    explicit = _text(
        raw.get("call_kind") or sidecar.get("call_kind") or payload.get("call_kind"),
        "",
    )
    if explicit:
        return explicit
    component = _text(
        raw.get("stage_component") or sidecar.get("stage_component") or raw.get("component") or sidecar.get("component"),
        "",
    )
    if component == "strategist_stage2_selected_symbol":
        return "selected_symbol_tactical_refresh"
    if component == "strategist_stage3_hold_review":
        return "stale_intraday_hold_review"
    if component == "strategist_stage4_carry_review":
        return "end_of_day_carry_review"
    if (
        payload.get("selected_symbol_decision") is not None
        or payload.get("target_symbol") is not None
        or payload.get("runner_up_order") is not None
    ):
        return "selected_symbol_tactical_refresh"
    if payload.get("hold_review_decision") is not None:
        return "stale_intraday_hold_review"
    if payload.get("carry_review_decision") is not None:
        return "end_of_day_carry_review"
    return ""


def _stage_meta(payload: Dict[str, Any], raw: Dict[str, Any], meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    sidecar = _as_dict(meta)
    call_kind = _infer_call_kind(payload, raw, sidecar)
    inferred = dict(_STAGE_META_BY_CALL_KIND.get(call_kind) or {})
    return {
        "call_kind": call_kind,
        "stage_index": raw.get("stage_index") or sidecar.get("stage_index") or inferred.get("stage_index"),
        "stage_name": _first_text(
            "",
            raw.get("stage_name"),
            sidecar.get("stage_name"),
            inferred.get("stage_name"),
            call_kind,
        ),
        "stage_component": _first_text(
            "",
            raw.get("stage_component"),
            sidecar.get("stage_component"),
            inferred.get("stage_component"),
            raw.get("component"),
            sidecar.get("component"),
        ),
    }


def _parse_response_body(raw: Dict[str, Any]) -> Dict[str, Any]:
    parsed = raw.get("parsed_output")
    if isinstance(parsed, dict) and parsed:
        return dict(parsed)

    response_text = raw.get("response_text")
    if isinstance(response_text, str) and response_text.strip():
        try:
            loaded = json.loads(response_text)
        except json.JSONDecodeError:
            return {}
        return dict(loaded) if isinstance(loaded, dict) else {}

    attempts = raw.get("attempts")
    if isinstance(attempts, list):
        for row in reversed(attempts):
            if not isinstance(row, dict):
                continue
            parsed = row.get("parsed_output")
            if isinstance(parsed, dict) and parsed:
                return dict(parsed)
            response_text = row.get("raw_response_text")
            if isinstance(response_text, str) and response_text.strip():
                try:
                    loaded = json.loads(response_text)
                except json.JSONDecodeError:
                    continue
                if isinstance(loaded, dict):
                    return dict(loaded)
    return {}


def _canonical_strategist_path_for_response(source_path: Path) -> Path | None:
    if source_path.name != "response.json":
        return None
    artifact_dir = source_path.parent
    run_dir = artifact_dir.parent
    day_dir = run_dir.parent
    llm_dir = day_dir.parent
    if llm_dir.name != "llm":
        category_dir = run_dir.parent
        day_dir = category_dir.parent
        llm_dir = day_dir.parent
        if llm_dir.name != "llm":
            return None
    reports_root = llm_dir.parent
    return reports_root / "canonical" / day_dir.name / run_dir.name / "strategist.json"


def _trade_strategist_input_path_for_response(source_path: Path) -> Path | None:
    if source_path.parent.name != "reports":
        return None
    candidate = source_path.parent.parent / "strategist_input.json"
    return candidate if candidate.exists() else None


def _load_canonical_strategist(source_path: Path) -> Tuple[Path | None, Dict[str, Any]]:
    canonical_path = _canonical_strategist_path_for_response(source_path)
    if canonical_path is not None and canonical_path.exists():
        try:
            raw = json.loads(canonical_path.read_text(encoding="utf-8"))
        except Exception:
            raw = {}
        if isinstance(raw, dict) and raw:
            return canonical_path, dict(raw)

    input_path = _trade_strategist_input_path_for_response(source_path)
    if input_path is None:
        return canonical_path, {}
    try:
        raw_input = json.loads(input_path.read_text(encoding="utf-8"))
    except Exception:
        return input_path, {}
    if not isinstance(raw_input, dict):
        return input_path, {}
    source_input = _as_dict(raw_input.get("source_input"))
    if not source_input:
        return input_path, {}
    canonical = dict(source_input)
    canonical.setdefault("generated_at", raw_input.get("saved_at"))
    canonical.setdefault("run_id", raw_input.get("run_id"))
    return input_path, canonical


def _headline_count_from_sample_map(value: Any) -> int:
    return _summary_quality._headline_count_from_sample_map(value, facade=_summary_sys.modules[__name__])


def _directive(payload: Dict[str, Any], key: str) -> Dict[str, Any]:
    return _summary_quality._directive(payload, key, facade=_summary_sys.modules[__name__])


def _compact_operator_summary(value: Dict[str, Any]) -> Dict[str, Any]:
    return _summary_quality._compact_operator_summary(value, facade=_summary_sys.modules[__name__])


def _memory_usage_from_canonical(canonical: Dict[str, Any]) -> Dict[str, Any]:
    return _summary_quality._memory_usage_from_canonical(canonical, facade=_summary_sys.modules[__name__])


def _news_usage_from_canonical(canonical: Dict[str, Any]) -> Dict[str, Any]:
    return _summary_quality._news_usage_from_canonical(canonical, facade=_summary_sys.modules[__name__])


def _market_rail_from_canonical(canonical: Dict[str, Any]) -> Dict[str, Any]:
    global_signal = _as_dict(canonical.get("global_sentiment_signal"))
    if not global_signal:
        global_signal = _as_dict(_as_dict(canonical.get("market_context")).get("global_signal"))
    packet = {
        "generated_at": _text(canonical.get("generated_at") or canonical.get("saved_at"), ""),
        "global_sentiment": {
            "score": global_signal.get("score"),
            "status": global_signal.get("status"),
            "source": global_signal.get("source"),
        },
        "index_moves": _as_dict(global_signal.get("index_moves")),
        "korea_indices": _as_dict(global_signal.get("korea_indices")),
        "macro_moves": _as_dict(global_signal.get("macro_moves")),
    }
    return classify_market_regime_rail(packet)


def _news_quality_audit(canonical: Dict[str, Any], news_usage: Dict[str, Any]) -> Dict[str, Any]:
    return _summary_quality._news_quality_audit(canonical, news_usage, facade=_summary_sys.modules[__name__])


def _strategist_output_quality_audit(
    *,
    payload: Dict[str, Any],
    canonical: Dict[str, Any],
    stage_decision: Dict[str, Any],
    strategy_detail: Dict[str, Any],
    market_rail: Dict[str, Any],
    news_quality: Dict[str, Any],
) -> Dict[str, Any]:
    return _summary_quality._strategist_output_quality_audit(payload=payload, canonical=canonical, stage_decision=stage_decision, strategy_detail=strategy_detail, market_rail=market_rail, news_quality=news_quality, facade=_summary_sys.modules[__name__])


def _stage_decision_from_payload(
    payload: Dict[str, Any],
    raw: Dict[str, Any],
    meta: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _summary_quality._stage_decision_from_payload(payload, raw, meta, facade=_summary_sys.modules[__name__])


def _operator_readout(payload: Dict[str, Any], stage_decision: Dict[str, Any] | None = None) -> Dict[str, Any]:
    stage_decision = _as_dict(stage_decision)
    if bool(stage_decision.get("is_stage_specific")):
        stage_name = _text(stage_decision.get("stage_name"), "stage_specific")
        decision = _text(stage_decision.get("decision"), "-")
        reason = _text(stage_decision.get("reason"), "")
        return {
            "headline": f"{stage_name} / decision={decision}",
            "good_points": [
                "Stage-specific strategist response was parsed.",
                "Market-frame fields such as selected_themes are not required for this stage.",
            ],
            "issues": [] if reason else ["stage-specific reason is empty"],
            "root_cause": reason or "stage-specific response did not include a reason",
            "recommended_actions": ["Review the stage decision fields instead of the market-frame section."],
            "validation_questions": ["Confirm monitor/executor behavior followed the stage decision."],
        }

    theme_strategy = _as_dict(payload.get("theme_strategy"))
    rationale = _text(payload.get("rationale"), "")
    selected_themes = _as_list(payload.get("selected_themes"))
    fallback_reason = _text(theme_strategy.get("fallback_reason"), "")
    selected_symbol_bias = _directive(payload, "selected_symbol_bias_action")

    good_points: List[str] = []
    issues: List[str] = []
    actions: List[str] = []
    validation: List[str] = []

    entry_policy = _directive(payload, "entry_policy_action")
    monitor_focus = _directive(payload, "monitor_focus_action")
    refresh_action = _directive(payload, "refresh_action")

    if entry_policy:
        good_points.append("최근 손실/과매매 피드백을 진입 정책 조정 근거로 명시했습니다.")
    if monitor_focus:
        good_points.append("모니터가 집중해야 할 축을 volume/reclaim처럼 실행 가능한 형태로 남겼습니다.")
    if refresh_action:
        good_points.append("전략 refresh가 요청된 이유와 최종 적용 단계를 분리해 남겼습니다.")

    if not selected_themes:
        issues.append("selected_themes가 비어 있어 테마 기반 전략 분기가 실제로 작동하지 않았습니다.")
        actions.append("다음 실행에서 Commander가 available_themes/theme_strength_packet을 전략가 호출 전에 채우는지 확인합니다.")
        validation.append("다음 전략가 요약에서 selected_themes가 실제 테마명으로 채워지는가?")
    if "best 및 worst" in rationale or "best and worst" in rationale.lower():
        issues.append("전략 메모리에서 같은 플레이북이 best/worst에 동시에 잡혀 방향성 신호가 약합니다.")
        actions.append("best/worst 중복 플레이북은 방향성 bias가 아니라 memory_quality_flag로만 표시합니다.")
    if str(selected_symbol_bias.get("action") or "").strip().lower() == "none":
        issues.append("심볼 메모리 근거가 없어 특정 종목 편향 조정은 적용되지 않았습니다.")
        validation.append("심볼 summary/memory가 누적된 뒤 selected_symbol_bias_action이 계속 none인지 확인합니다.")

    if not good_points:
        good_points.append("전략가 출력은 파싱 가능하며 playbook, entry policy, refresh trace를 포함합니다.")
    if not issues:
        issues.append("즉시 확인할 구조적 문제는 요약에서 감지되지 않았습니다.")
    if not actions:
        actions.append("다음 실행 결과와 비교해 같은 playbook 반복 여부를 확인합니다.")
    if not validation:
        validation.append("다음 실행에서 playbook/theme/entry policy가 시장 입력에 따라 달라지는가?")

    headline_parts = [_text(payload.get("playbook"), "unknown")]
    if selected_themes:
        headline_parts.append(f"themes={', '.join(str(x) for x in selected_themes[:3])}")
    else:
        headline_parts.append("theme=none")
    if theme_strategy.get("selection_mode"):
        headline_parts.append(f"mode={theme_strategy.get('selection_mode')}")

    root_cause = fallback_reason or rationale or "전략가 출력의 rationale 확인 필요"
    return {
        "headline": " / ".join(headline_parts),
        "good_points": good_points[:4],
        "issues": issues[:4],
        "root_cause": root_cause,
        "recommended_actions": actions[:4],
        "validation_questions": validation[:4],
    }


def _first_text(default: str, *values: Any) -> str:
    return _summary_quality._first_text(default, *values, facade=_summary_sys.modules[__name__])


def _operator_readout_clean(payload: Dict[str, Any], stage_decision: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return _summary_quality._operator_readout_clean(payload, stage_decision, facade=_summary_sys.modules[__name__])


def _first_dict(*values: Any) -> Dict[str, Any]:
    return _summary_quality._first_dict(*values, facade=_summary_sys.modules[__name__])


def _strategy_detail_from_sources(payload: Dict[str, Any], canonical: Dict[str, Any]) -> Dict[str, Any]:
    return _summary_quality._strategy_detail_from_sources(payload, canonical, facade=_summary_sys.modules[__name__])


def _json_inline(value: Any) -> str:
    return _summary_markdown._json_inline(value, facade=_summary_sys.modules[__name__])


def _watch_scope_label(value: Dict[str, Any]) -> str:
    if not value:
        return ""
    rank = value.get("max_priority_rank")
    runner_ups = value.get("max_runner_ups")
    parts: List[str] = []
    if rank not in (None, ""):
        parts.append(f"{rank}위까지")
    if runner_ups not in (None, ""):
        parts.append(f"차순위 {runner_ups}개")
    if value.get("cascade_enabled") not in (None, ""):
        parts.append(f"cascade {'활성' if bool(value.get('cascade_enabled')) else '비활성'}")
    return " / ".join(parts)


def _strategy_patch_status(detail: Dict[str, Any]) -> str:
    required_keys = (
        "pre_llm_playbook",
        "llm_requested_playbook",
        "requested_playbook",
        "requested_playbook_source",
        "final_playbook",
        "tactical_strategy",
        "strategy_scores",
        "rejected_strategy_reasons",
        "candidate_watch_policy",
    )
    missing = [key for key in required_keys if not detail.get(key)]
    if not missing:
        return "적용됨"
    return f"일부 누락 ({', '.join(missing)})"


def _playbook_flow_label(detail: Dict[str, Any]) -> str:
    return _summary_markdown._playbook_flow_label(detail, facade=_summary_sys.modules[__name__])


def _score_value(value: Any) -> float:
    return _summary_markdown._score_value(value, facade=_summary_sys.modules[__name__])


def _score_label(value: Any) -> str:
    return _summary_markdown._score_label(value, facade=_summary_sys.modules[__name__])


def _strategy_score_lines(scores: Dict[str, Any], *, selected: str) -> List[str]:
    if not scores:
        return ["- -"]
    rows = sorted(scores.items(), key=lambda row: (_score_value(row[1]), str(row[0])), reverse=True)
    lines: List[str] = []
    for name, score in rows:
        marker = " (선택)" if str(name) == selected else ""
        lines.append(f"- {name}: {_score_label(score)}{marker}")
    return lines


def _watch_scope_label_clean(value: Dict[str, Any]) -> str:
    return _summary_markdown._watch_scope_label_clean(value, facade=_summary_sys.modules[__name__])


def _strategy_patch_status_clean(detail: Dict[str, Any]) -> str:
    return _summary_markdown._strategy_patch_status_clean(detail, facade=_summary_sys.modules[__name__])


def _strategy_score_lines_clean(scores: Dict[str, Any], *, selected: str) -> List[str]:
    return _summary_markdown._strategy_score_lines_clean(scores, selected=selected, facade=_summary_sys.modules[__name__])


def _rejected_strategy_lines(reasons: Dict[str, Any], *, selected: str) -> List[str]:
    return _summary_markdown._rejected_strategy_lines(reasons, selected=selected, facade=_summary_sys.modules[__name__])


def build_strategist_llm_summary_payload(response_json_path: Path) -> Dict[str, Any]:
    source_path = Path(response_json_path)
    raw = json.loads(source_path.read_text(encoding="utf-8"))
    sidecar_meta = _read_json(source_path.with_name("meta.json"))
    payload = _parse_response_body(raw)
    canonical_path, canonical = _load_canonical_strategist(source_path)
    theme_strategy = _as_dict(payload.get("theme_strategy"))
    refresh_trace = _as_dict(payload.get("strategy_refresh_trace"))
    horizon = _as_dict(payload.get("strategy_horizon_feedback"))
    strategy_detail = _strategy_detail_from_sources(payload, canonical)
    stage_decision = _stage_decision_from_payload(payload, raw, sidecar_meta)
    stage_meta = _stage_meta(payload, raw, sidecar_meta)
    news_usage = _news_usage_from_canonical(canonical)
    market_regime_rail = _market_rail_from_canonical(canonical)
    news_quality = _news_quality_audit(canonical, news_usage)
    risk_off_exception_policy = _as_dict(canonical.get("risk_off_exception_policy")) or build_risk_off_exception_policy(
        market_regime_rail=market_regime_rail,
        news_quality=news_quality,
    )
    output_quality = _strategist_output_quality_audit(
        payload=payload,
        canonical=canonical,
        stage_decision=stage_decision,
        strategy_detail=strategy_detail,
        market_rail=market_regime_rail,
        news_quality=news_quality,
    )

    generated_at = _utc_now_iso()
    return _summary_quality.assemble_summary_payload(
        source_path=source_path,
        canonical_path=canonical_path,
        raw=raw,
        sidecar_meta=sidecar_meta,
        payload=payload,
        canonical=canonical,
        theme_strategy=theme_strategy,
        refresh_trace=refresh_trace,
        horizon=horizon,
        strategy_detail=strategy_detail,
        stage_decision=stage_decision,
        stage_meta=stage_meta,
        news_usage=news_usage,
        market_regime_rail=market_regime_rail,
        news_quality=news_quality,
        risk_off_exception_policy=risk_off_exception_policy,
        output_quality=output_quality,
        generated_at=generated_at,
        facade=_summary_sys.modules[__name__],
    )


def _bullet_lines(items: List[Any], *, empty: str = "-") -> List[str]:
    return _summary_markdown._bullet_lines(items, empty=empty, facade=_summary_sys.modules[__name__])


def _directive_line(label: str, value: Dict[str, Any]) -> str:
    return _summary_markdown._directive_line(label, value, facade=_summary_sys.modules[__name__])


def _memory_usage_lines(memory: Dict[str, Any]) -> List[str]:
    if not bool(memory.get("available")):
        return ["- 메모리 사용 trace: -"]
    lines = [
        f"- 활성 레이어: {', '.join(str(x) for x in _as_list(memory.get('active_layers'))) or '-'}",
        f"- 우선순위: {' -> '.join(str(x) for x in _as_list(memory.get('priority_order'))) or '-'}",
        f"- 요약: {_text(memory.get('human_summary'))}",
    ]
    applied = _as_dict(memory.get("applied_to_strategy"))
    if applied:
        lines.append(f"- 전략 반영: playbook={_text(applied.get('playbook_effect'))}, risk={_text(applied.get('risk_posture_effect'))}")
        lines.append(
            f"- scanner/monitor 반영: scanner={_text(applied.get('scanner_guidance_effect'))}, "
            f"monitor={_text(applied.get('monitor_policy_effect'))}"
        )
    layer_decisions = _as_dict(memory.get("layer_decisions"))
    for layer in ("daily", "weekly", "monthly", "symbol"):
        row = _as_dict(layer_decisions.get(layer))
        if not row:
            continue
        summary = _as_dict(row.get("operator_summary"))
        metrics = []
        if summary.get("trade_count") is not None:
            metrics.append(f"trades={summary.get('trade_count')}")
        if summary.get("win_rate") is not None:
            metrics.append(f"win_rate={summary.get('win_rate')}")
        if summary.get("avg_return_pct") is not None:
            metrics.append(f"avg_return_pct={summary.get('avg_return_pct')}")
        metric_text = f" ({', '.join(metrics)})" if metrics else ""
        lines.append(
            f"- {layer}: used={row.get('used')} status={_text(row.get('status'), '')} "
            f"effect={_text(row.get('effect'), '')}{metric_text}"
        )
    return lines


def _news_usage_lines(news: Dict[str, Any]) -> List[str]:
    if not bool(news.get("available")):
        return ["- 뉴스 사용 trace: -"]
    query_targets = ", ".join(str(x) for x in _as_list(news.get("query_targets"))[:10]) or "-"
    return [
        f"- 검색/수집 타깃: {query_targets}",
        f"- 사용 요약: {_text(news.get('human_summary'))}",
        f"- 시장 효과: {_text(news.get('market_effect'))}",
        f"- 플레이북 효과: {_text(news.get('playbook_effect'))}",
        f"- 스캐너 반영: {_text(news.get('scanner_guidance_effect'))}",
        f"- 모니터 반영: {_text(news.get('monitor_policy_effect'))}",
        f"- 근거 헤드라인 수: market={news.get('market_headline_count')}, candidate={news.get('candidate_headline_count')}",
        f"- query reasoning: {_text(news.get('news_query_reasoning'))}",
    ]


def render_strategist_llm_summary_markdown(payload: Dict[str, Any]) -> str:
    meta = _as_dict(payload.get("llm_meta"))
    readout = _as_dict(payload.get("operator_readout"))
    stage_decision = _as_dict(payload.get("stage_decision"))
    if bool(stage_decision.get("is_stage_specific")):
        return _render_stage_specific_summary_markdown(payload)

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
    watch_scope = _watch_scope_label(watch)
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
        "> 아래 내용은 전략가 LLM 응답의 구조화 필드를 재배치한 것입니다. 리포터가 새로 해석한 문장이 아니라 `response.json`에 저장된 전략가 출력입니다.",
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
        f"- 전략 강화 필드: {_strategy_patch_status(detail)}",
        f"- 플레이북 흐름: {_playbook_flow_label(detail)}",
        f"- LLM 요청 플레이북: {_text(detail.get('llm_requested_playbook'))}",
        f"- 최종 플레이북: {_text(detail.get('final_playbook'))}",
        f"- 선택 전술: {_text(detail.get('tactical_strategy'))}",
        f"- 후보 감시 제안: {watch_scope or '-'}",
        "",
        "#### 전략 점수",
        "",
        *_strategy_score_lines(strategy_scores, selected=tactical_strategy),
        "",
        "#### 탈락 전략 이유",
        "",
        *_rejected_strategy_lines(rejected_reasons, selected=tactical_strategy),
        "",
        "### 메모리 사용",
        "",
        *_memory_usage_lines(memory),
        "",
        "### 뉴스 사용",
        "",
        *_news_usage_lines(news),
        "",
        *_quality_audit_lines(payload),
        "### 정책 조정",
        "",
        _directive_line("플레이북", _as_dict(changes.get("playbook_action"))),
        _directive_line("진입 정책", _as_dict(changes.get("entry_policy_action"))),
        _directive_line("모니터 초점", _as_dict(changes.get("monitor_focus_action"))),
        _directive_line("심볼 bias", _as_dict(changes.get("selected_symbol_bias_action"))),
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
        "### 운용 Horizon",
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
        "## 운영자 검수 요약",
        "",
        "> 아래 내용은 전략가 원문을 기준으로 한 deterministic 검수입니다. 추가 LLM 호출이나 새 전략 해석은 포함하지 않습니다.",
        "",
        f"- 검수 결론: **{_text(readout.get('headline'))}**",
        f"- 주요 원인: {_text(readout.get('root_cause'))}",
        "",
        "### 잘된 점",
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


def _monitor_adjustment_lines(value: Dict[str, Any]) -> List[str]:
    if not value:
        return ["- -"]
    return [f"- {key}: {value.get(key)}" for key in sorted(value)]


def _render_stage_specific_summary_markdown(payload: Dict[str, Any]) -> str:
    meta = _as_dict(payload.get("llm_meta"))
    readout = _as_dict(payload.get("operator_readout"))
    stage_decision = _as_dict(payload.get("stage_decision"))
    detail = _as_dict(payload.get("strategy_detail"))
    watch = _as_dict(detail.get("candidate_watch_policy"))
    triggers = ", ".join(str(x) for x in _as_list(stage_decision.get("priority_exit_triggers"))) or "-"
    monitor_adjustment = _as_dict(stage_decision.get("monitor_adjustment"))

    lines: List[str] = [
        f"# Strategist LLM Summary ({_text(meta.get('day'), '-')})",
        "",
        "---",
        "",
        "## Stage-Specific LLM Output",
        "",
        f"- status: {_text(meta.get('status'))} / model={_text(meta.get('model'))}",
        f"- stage: {stage_decision.get('stage_index')} / {_text(stage_decision.get('stage_name'))}",
        f"- call_kind: {_text(stage_decision.get('call_kind'))}",
        f"- stage_component: {_text(meta.get('stage_component'))}",
        "",
        "### Decision",
        "",
        f"- decision: **{_text(stage_decision.get('decision'))}**",
        f"- exit_pressure: {_text(stage_decision.get('exit_pressure'))}",
        f"- thesis_status: {_text(stage_decision.get('thesis_status'))}",
        f"- next_check_minutes: {stage_decision.get('next_check_minutes')}",
        f"- priority_exit_triggers: {triggers}",
        "",
        "### Monitor Adjustment",
        "",
        *_monitor_adjustment_lines(monitor_adjustment),
        "",
        "### Reason",
        "",
        _text(stage_decision.get("reason")),
        "",
        "## Strategy Context From Canonical",
        "",
        f"- final_playbook: {_text(detail.get('final_playbook'))}",
        f"- tactical_strategy: {_text(detail.get('tactical_strategy'))}",
        f"- playbook_flow: {_playbook_flow_label(detail)}",
        f"- candidate_watch: {_watch_scope_label_clean(watch) or '-'}",
        "",
        *_quality_audit_lines(payload),
        "## Operator Check",
        "",
        f"- summary: **{_text(readout.get('headline'))}**",
        f"- main_reason: {_text(readout.get('root_cause'))}",
        "",
        "### Good Points",
        "",
        *_bullet_lines(_as_list(readout.get("good_points"))),
        "",
        "### Issues",
        "",
        *_bullet_lines(_as_list(readout.get("issues"))),
        "",
        "### Recommended Actions",
        "",
        *_bullet_lines(_as_list(readout.get("recommended_actions"))),
        "",
        "---",
        "",
        "## Evidence",
        "",
        f"- source_response_json: `{payload.get('source_response_json')}`",
        f"- source_canonical_strategist_json: `{payload.get('source_canonical_strategist_json')}`",
        f"- run_id: `{_text(meta.get('run_id'), '')}`",
        f"- saved_at: `{_text(meta.get('saved_at'), '')}`",
        f"- generated_at: `{_text(payload.get('generated_at'), '')}`",
        "",
    ]
    return "\n".join(lines)


def _memory_usage_lines_clean(memory: Dict[str, Any]) -> List[str]:
    return _summary_markdown._memory_usage_lines_clean(memory, facade=_summary_sys.modules[__name__])


def _news_usage_lines_clean(news: Dict[str, Any]) -> List[str]:
    return _summary_markdown._news_usage_lines_clean(news, facade=_summary_sys.modules[__name__])


def _quality_audit_lines(payload: Dict[str, Any]) -> List[str]:
    return _summary_markdown._quality_audit_lines(payload, facade=_summary_sys.modules[__name__])


def _render_stage_specific_summary_markdown_clean(payload: Dict[str, Any]) -> str:
    return _summary_markdown._render_stage_specific_summary_markdown_clean(payload, facade=_summary_sys.modules[__name__])


def render_strategist_llm_summary_markdown(payload: Dict[str, Any]) -> str:
    return _summary_markdown.render_strategist_llm_summary_markdown(payload, facade=_summary_sys.modules[__name__])


def generate_strategist_llm_summary(response_json_path: Path) -> Tuple[Path, Path, Dict[str, Any]]:
    source_path = Path(response_json_path)
    payload = build_strategist_llm_summary_payload(source_path)
    md_path = source_path.with_name("strategist_summary.md")
    json_path = source_path.with_name("strategist_summary.json")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_strategist_llm_summary_markdown(payload), encoding="utf-8-sig", newline="\n")
    return md_path, json_path, payload
