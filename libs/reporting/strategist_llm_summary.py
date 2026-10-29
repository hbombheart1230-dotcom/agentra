from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from libs.runtime.quant.market_regime_observation import classify_market_regime_rail
from libs.runtime.strategist_input_quality import build_risk_off_exception_policy
from libs.reporting import strategist_llm_summary_stage as _stage_owner
from libs.reporting import strategist_llm_summary_usage as _usage_owner
from libs.reporting import strategist_llm_summary_decision as _decision_owner
from libs.reporting import strategist_llm_summary_readout as _readout_owner
from libs.reporting import strategist_llm_summary_strategy as _strategy_owner
from libs.reporting import strategist_llm_summary_quality_lines as _quality_lines_owner


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
    return _stage_owner.infer_call_kind(payload, raw, meta, facade=sys.modules[__name__])


def _stage_meta(payload: Dict[str, Any], raw: Dict[str, Any], meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return _stage_owner.stage_meta(payload, raw, meta, facade=sys.modules[__name__])


def _parse_response_body(raw: Dict[str, Any]) -> Dict[str, Any]:
    return _stage_owner.parse_response_body(raw)


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
    total = 0
    if not isinstance(value, dict):
        return total
    for row in value.values():
        if not isinstance(row, dict):
            continue
        try:
            total += int(row.get("count") or 0)
        except Exception:
            pass
    return total


def _directive(payload: Dict[str, Any], key: str) -> Dict[str, Any]:
    directives = _as_dict(payload.get("strategy_adjustment_directives"))
    return _as_dict(directives.get(key))


def _compact_operator_summary(value: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "available": bool(value.get("available")),
        "status": _text(value.get("status"), ""),
        "artifact_path": _text(value.get("artifact_path"), ""),
        "trade_count": value.get("trade_count"),
        "closed_trade_count": value.get("closed_trade_count"),
        "win_rate": value.get("win_rate"),
        "avg_return_pct": value.get("avg_return_pct"),
    }


def _memory_usage_from_canonical(canonical: Dict[str, Any]) -> Dict[str, Any]:
    return _usage_owner.memory_usage_from_canonical(canonical, facade=sys.modules[__name__])


def _news_usage_from_canonical(canonical: Dict[str, Any]) -> Dict[str, Any]:
    return _usage_owner.news_usage_from_canonical(canonical, facade=sys.modules[__name__])


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
    return _usage_owner.news_quality_audit(canonical, news_usage, facade=sys.modules[__name__])


def _strategist_output_quality_audit(
    *,
    payload: Dict[str, Any],
    canonical: Dict[str, Any],
    stage_decision: Dict[str, Any],
    strategy_detail: Dict[str, Any],
    market_rail: Dict[str, Any],
    news_quality: Dict[str, Any],
) -> Dict[str, Any]:
    return _decision_owner.strategist_output_quality_audit(payload=payload, canonical=canonical, stage_decision=stage_decision, strategy_detail=strategy_detail, market_rail=market_rail, news_quality=news_quality, facade=sys.modules[__name__])


def _stage_decision_from_payload(
    payload: Dict[str, Any],
    raw: Dict[str, Any],
    meta: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return _decision_owner.stage_decision_from_payload(payload, raw, meta, facade=sys.modules[__name__])


def _operator_readout(payload: Dict[str, Any], stage_decision: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return _readout_owner.operator_readout(payload, stage_decision, facade=sys.modules[__name__])


def _first_text(default: str, *values: Any) -> str:
    for value in values:
        text = _text(value, "")
        if text:
            return text
    return default


def _operator_readout_clean(payload: Dict[str, Any], stage_decision: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return _readout_owner.operator_readout_clean(payload, stage_decision, facade=sys.modules[__name__])


def _first_dict(*values: Any) -> Dict[str, Any]:
    for value in values:
        row = _as_dict(value)
        if row:
            return row
    return {}


def _strategy_detail_from_sources(payload: Dict[str, Any], canonical: Dict[str, Any]) -> Dict[str, Any]:
    return _strategy_owner.strategy_detail_from_sources(payload, canonical, facade=sys.modules[__name__])


def _json_inline(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


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
    pre = _text(detail.get("pre_llm_playbook"), "")
    requested = _text(detail.get("requested_playbook"), "")
    final = _text(detail.get("final_playbook"), "")
    parts = [part for part in (pre, requested, final) if part]
    if not parts:
        return "-"
    flow = " -> ".join(parts)
    source = _text(detail.get("requested_playbook_source"), "")
    return f"{flow} (source={source})" if source else flow


def _score_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("-inf")


def _score_label(value: Any) -> str:
    numeric = _score_value(value)
    if numeric != float("-inf"):
        return f"{numeric:.2f}".rstrip("0").rstrip(".")
    return _text(value)


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


def _strategy_patch_status_clean(detail: Dict[str, Any]) -> str:
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


def _strategy_score_lines_clean(scores: Dict[str, Any], *, selected: str) -> List[str]:
    if not scores:
        return ["- -"]
    rows = sorted(scores.items(), key=lambda row: (_score_value(row[1]), str(row[0])), reverse=True)
    lines: List[str] = []
    for name, score in rows:
        marker = " (선택)" if str(name) == selected else ""
        lines.append(f"- {name}: {_score_label(score)}{marker}")
    return lines


def _rejected_strategy_lines(reasons: Dict[str, Any], *, selected: str) -> List[str]:
    if not reasons:
        return ["- -"]
    lines: List[str] = []
    for name in sorted(reasons):
        if str(name) == selected:
            continue
        reason = reasons.get(name)
        if isinstance(reason, (dict, list)):
            reason_text = _json_inline(reason)
        else:
            reason_text = _text(reason)
        lines.append(f"- {name}: {reason_text}")
    return lines if lines else ["- -"]


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

    return {
        "schema_version": "strategist_llm_summary.v1",
        "artifact_type": "strategist_llm_summary",
        "source_response_json": str(source_path),
        "source_canonical_strategist_json": str(canonical_path) if canonical_path else "",
        "generated_at": _utc_now_iso(),
        "llm_meta": {
            "stage": _first_text("", raw.get("stage"), sidecar_meta.get("stage")),
            "stage_index": stage_meta.get("stage_index"),
            "stage_name": _text(stage_meta.get("stage_name"), ""),
            "call_kind": _text(stage_meta.get("call_kind"), ""),
            "stage_component": _text(stage_meta.get("stage_component"), ""),
            "provider": _first_text("", raw.get("provider"), sidecar_meta.get("provider")),
            "model": _first_text("", raw.get("model"), sidecar_meta.get("model")),
            "status": _first_text("", raw.get("status"), raw.get("llm_status"), sidecar_meta.get("status"), sidecar_meta.get("llm_status")),
            "reason": _first_text("", raw.get("reason"), sidecar_meta.get("reason")),
            "run_id": _first_text("", raw.get("run_id"), sidecar_meta.get("run_id")),
            "day": _first_text("", raw.get("day"), sidecar_meta.get("day")),
            "saved_at": _first_text("", raw.get("saved_at"), sidecar_meta.get("saved_at")),
            "repair_used": bool(raw.get("repair_used") or sidecar_meta.get("repair_used")),
            "profile_name": _first_text("", raw.get("llm_execution_profile_name"), sidecar_meta.get("llm_execution_profile_name")),
            "profile_source": _first_text("", raw.get("llm_execution_profile_source"), sidecar_meta.get("llm_execution_profile_source")),
        },
        "operator_readout": _operator_readout_clean(payload, stage_decision),
        "stage_decision": stage_decision,
        "strategy_frame": {
            "playbook": _text(payload.get("playbook")),
            "selected_themes": _as_list(payload.get("selected_themes")),
            "theme_selection_mode": _text(theme_strategy.get("selection_mode")),
            "fallback_reason": _text(theme_strategy.get("fallback_reason"), ""),
            "rationale": _text(payload.get("rationale"), ""),
        },
        "strategy_detail": strategy_detail,
        "policy_changes": {
            "playbook_action": _directive(payload, "playbook_action"),
            "entry_policy_action": _directive(payload, "entry_policy_action"),
            "monitor_focus_action": _directive(payload, "monitor_focus_action"),
            "selected_symbol_bias_action": _directive(payload, "selected_symbol_bias_action"),
            "refresh_action": _directive(payload, "refresh_action"),
        },
        "monitor_entry_policy": _as_dict(payload.get("monitor_entry_policy")),
        "memory_usage": _memory_usage_from_canonical(canonical),
        "news_usage": news_usage,
        "news_event_intelligence": _as_dict(
            payload.get("news_event_intelligence") or canonical.get("news_event_intelligence")
        ),
        "news_event_intelligence_usage": _as_dict(payload.get("news_event_intelligence_usage")),
        "market_regime_rail": market_regime_rail,
        "news_quality_audit": news_quality,
        "risk_off_exception_policy": risk_off_exception_policy,
        "risk_off_exception_conditions": _as_list(payload.get("risk_off_exception_conditions")),
        "strategist_output_quality_audit": output_quality,
        "strategy_refresh_trace": {
            "summary": _text(refresh_trace.get("summary"), ""),
            "bullets": _as_list(refresh_trace.get("bullets")),
            "stages": _as_list(refresh_trace.get("stages")),
        },
        "strategy_horizon_feedback": horizon,
    }


def _bullet_lines(items: List[Any], *, empty: str = "-") -> List[str]:
    rows = [f"- {item}" for item in items if str(item or "").strip()]
    return rows if rows else [f"- {empty}"]


def _directive_line(label: str, value: Dict[str, Any]) -> str:
    if not value:
        return f"- {label}: -"
    action = _text(value.get("action"))
    target = value.get("target")
    if target is None:
        target = value.get("target_fields") or value.get("target_axes")
    reason = _text(value.get("reason"), "")
    target_text = ", ".join(str(x) for x in target) if isinstance(target, list) else _text(target, "")
    if target_text and reason:
        return f"- {label}: **{action}** -> {target_text}; {reason}"
    if target_text:
        return f"- {label}: **{action}** -> {target_text}"
    if reason:
        return f"- {label}: **{action}**; {reason}"
    return f"- {label}: **{action}**"


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


def _news_usage_lines_clean(news: Dict[str, Any]) -> List[str]:
    if not bool(news.get("available")):
        return ["- 뉴스 사용 trace: -"]
    query_targets = ", ".join(str(x) for x in _as_list(news.get("query_targets"))[:10]) or "-"
    return [
        f"- 검색/수집 대상: {query_targets}",
        f"- 사용 요약: {_text(news.get('human_summary'))}",
        f"- 시장 효과: {_text(news.get('market_effect'))}",
        f"- 플레이북 효과: {_text(news.get('playbook_effect'))}",
        f"- 스캐너 반영: {_text(news.get('scanner_guidance_effect'))}",
        f"- 모니터 반영: {_text(news.get('monitor_policy_effect'))}",
        f"- 근거 헤드라인 수: market={news.get('market_headline_count')}, candidate={news.get('candidate_headline_count')}",
        f"- query reasoning: {_text(news.get('news_query_reasoning'))}",
    ]


def _quality_audit_lines(payload: Dict[str, Any]) -> List[str]:
    return _quality_lines_owner.quality_audit_lines(payload, facade=sys.modules[__name__])


def _render_stage_specific_summary_markdown_clean(payload: Dict[str, Any]) -> str:
    meta = _as_dict(payload.get("llm_meta"))
    readout = _as_dict(payload.get("operator_readout"))
    stage_decision = _as_dict(payload.get("stage_decision"))
    detail = _as_dict(payload.get("strategy_detail"))
    watch = _as_dict(detail.get("candidate_watch_policy"))
    monitor_instruction = _as_dict(stage_decision.get("monitor_instruction"))
    entry_policy_delta = _as_dict(stage_decision.get("entry_policy_delta"))
    commander_actionability = _as_dict(stage_decision.get("commander_actionability"))
    runners = ", ".join(str(x) for x in _as_list(stage_decision.get("runner_up_order"))) or "-"
    triggers = ", ".join(str(x) for x in _as_list(stage_decision.get("priority_exit_triggers"))) or "-"

    lines: List[str] = [
        f"# Strategist LLM Summary ({_text(meta.get('day'), '-')})",
        "",
        "---",
        "",
        "## 단계별 전략가 LLM 출력",
        "",
        f"- 상태: {_text(meta.get('status'))} / model={_text(meta.get('model'))}",
        f"- 단계: {stage_decision.get('stage_index')} / {_text(stage_decision.get('stage_name'))}",
        f"- 호출 종류: {_text(stage_decision.get('call_kind'))}",
        f"- stage component: {_text(stage_decision.get('stage_component') or meta.get('stage_component'))}",
        "",
        "### 결정",
        "",
        f"- decision: **{_text(stage_decision.get('decision'))}**",
        f"- target_symbol: {_text(stage_decision.get('target_symbol'))}",
        f"- target_rank: {stage_decision.get('target_rank')}",
        f"- runner_up_order: {runners}",
        f"- confidence: {stage_decision.get('confidence')}",
        f"- exit_pressure: {_text(stage_decision.get('exit_pressure'), '')}",
        f"- thesis_status: {_text(stage_decision.get('thesis_status'), '')}",
        f"- next_check_minutes: {stage_decision.get('next_check_minutes')}",
        f"- priority_exit_triggers: {triggers}",
        "",
        "### 모니터 지시",
        "",
    ]
    if monitor_instruction:
        for key in sorted(monitor_instruction):
            lines.append(f"- {key}: {_json_inline(monitor_instruction.get(key))}")
    else:
        lines.append("- -")
    lines += ["", "### 진입 정책 delta", ""]
    if entry_policy_delta:
        for key in sorted(entry_policy_delta):
            lines.append(f"- {key}: {_json_inline(entry_policy_delta.get(key))}")
    else:
        lines.append("- -")
    lines += ["", "### 지휘관 적용 가능성", ""]
    if commander_actionability:
        for key in sorted(commander_actionability):
            lines.append(f"- {key}: {_json_inline(commander_actionability.get(key))}")
    else:
        lines.append("- -")
    lines += [
        "",
        "### 사유",
        "",
        _text(stage_decision.get("reason")),
        "",
        "## Canonical 전략 컨텍스트",
        "",
        f"- final_playbook: {_text(detail.get('final_playbook'))}",
        f"- tactical_strategy: {_text(detail.get('tactical_strategy'))}",
        f"- playbook_flow: {_playbook_flow_label(detail)}",
        f"- candidate_watch: {_watch_scope_label_clean(watch) or '-'}",
        "",
        *_quality_audit_lines(payload),
        "## 운영 점검",
        "",
        f"- 요약: **{_text(readout.get('headline'))}**",
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


def generate_strategist_llm_summary(response_json_path: Path) -> Tuple[Path, Path, Dict[str, Any]]:
    source_path = Path(response_json_path)
    payload = build_strategist_llm_summary_payload(source_path)
    md_path = source_path.with_name("strategist_summary.md")
    json_path = source_path.with_name("strategist_summary.json")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_strategist_llm_summary_markdown(payload), encoding="utf-8-sig", newline="\n")
    return md_path, json_path, payload
