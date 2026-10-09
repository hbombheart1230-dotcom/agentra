from __future__ import annotations

import json
from typing import Any, Dict, Mapping

def build_market_scanner_linkage_bullet(section: Any, scanner_reason: Dict[str, Any] | None = None, *, deps: Mapping[str, Any]) -> str:
    _clip = deps["clip"]
    _listify = deps["listify"]
    _num_opt = deps["num_opt"]
    market = section if isinstance(section, dict) else {}
    scanner = scanner_reason if isinstance(scanner_reason, dict) else {}
    symbol = _clip(scanner.get("selected_symbol"), max_len=24)
    if not symbol:
        return ""
    playbook = _clip(market.get("playbook"), max_len=40) or "not_captured"
    source_text = ", ".join(_listify(scanner.get("selected_sources"), max_items=4, max_len=80))
    contribution = scanner.get("news_scanner_contribution") if isinstance(scanner.get("news_scanner_contribution"), dict) else {}
    core = contribution.get("core_score_contributions") if isinstance(contribution.get("core_score_contributions"), dict) else {}
    sentiment_inputs = contribution.get("sentiment_inputs") if isinstance(contribution.get("sentiment_inputs"), dict) else {}

    def _core_value_opt(key: str) -> Optional[float]:
        row = core.get(key)
        if isinstance(row, dict):
            return _num_opt(row.get("value"))
        return _num_opt(row)

    score_value = _num_opt(scanner.get("selected_score"))
    sentiment_contrib = _core_value_opt("sentiment")
    if sentiment_contrib is None:
        sentiment_contrib = _num_opt(sentiment_inputs.get("weighted_sentiment_score_contribution"))
    theme_boost = _core_value_opt("theme_boost")
    global_sentiment_value = _num_opt(sentiment_inputs.get("global_sentiment_score"))
    if global_sentiment_value is None:
        global_sentiment_value = _num_opt(market.get("global_sentiment_score"))
    vix_value = _num_opt(market.get("vix_level"))

    metric_bits: List[str] = []
    if score_value is not None:
        metric_bits.append(f"종합 점수 {score_value:.3f}")
    if sentiment_contrib is not None:
        metric_bits.append(f"감성 기여 {sentiment_contrib:+.3f}")
    if theme_boost is not None:
        metric_bits.append(f"테마 가점 {theme_boost:+.3f}")
    if global_sentiment_value is not None:
        metric_bits.append(f"글로벌 감성 {global_sentiment_value:.3f}")
    if vix_value is not None:
        metric_bits.append(f"VIX {vix_value:.2f}")

    parts: List[str] = [f"종목 {symbol}을 {playbook} 플레이북 기준으로 선정했고"]
    if metric_bits:
        parts.append(", ".join(metric_bits))
    if source_text:
        parts.append(f"선정 소스 {source_text}")
    return "Scanner linkage: " + ", ".join(parts)



def build_scanner_choice_bullets(scanner_reason: Dict[str, Any], market_context: Dict[str, Any], *, deps: Mapping[str, Any]) -> List[str]:
    _build_runner_up_comparison = deps["build_runner_up_comparison"]
    _build_scanner_driver_summary = deps["build_scanner_driver_summary"]
    _clip = deps["clip"]
    _dedupe_list = deps["dedupe_list"]
    _fmt_num = deps["fmt_num"]
    _listify = deps["listify"]
    _market_token_label = deps["market_token_label"]
    _num_opt = deps["num_opt"]
    _scanner_basis_text = deps["scanner_basis_text"]
    _scanner_chart_feature_coverage = deps["scanner_chart_feature_coverage"]
    _scanner_chart_feature_label = deps["scanner_chart_feature_label"]
    _scanner_monitor_fallback_context = deps["scanner_monitor_fallback_context"]
    _scanner_ranked_candidates = deps["scanner_ranked_candidates"]
    _scanner_selected_row = deps["scanner_selected_row"]
    _scanner_source_text = deps["scanner_source_text"]
    symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24) or "선정 종목"
    rank = scanner_reason.get("selected_rank")
    universe = scanner_reason.get("universe_size")
    score_value = _num_opt(scanner_reason.get("selected_score"))
    confidence_value = _num_opt(scanner_reason.get("confidence"))
    ranked_rows = _scanner_ranked_candidates(scanner_reason)
    selected_row = _scanner_selected_row(scanner_reason)
    selected_risk = _num_opt(selected_row.get("risk_score"))
    fallback_ctx = _scanner_monitor_fallback_context(scanner_reason)
    basis = _scanner_basis_text(scanner_reason)
    source_text = _scanner_source_text(scanner_reason.get("selected_sources"))
    playbook = _market_token_label(market_context.get("playbook")) or _clip(market_context.get("playbook"), max_len=32)
    driver_summary = _build_scanner_driver_summary(scanner_reason)
    coverage = _scanner_chart_feature_coverage(scanner_reason)

    bullets: List[str] = []
    if fallback_ctx["used"] and fallback_ctx["scanner_top_pick_symbol"]:
        rank_text = f"{rank}위" if rank not in (None, "") else "후보"
        fallback_line = (
            f"스캐너 상위 후보 {fallback_ctx['scanner_top_pick_symbol']}은 모니터 단계에서 보류됐고 "
            f"{symbol}은 차순위 재평가 {rank_text}로 실제 진입 종목이 됐습니다."
        )
        if fallback_ctx["reason"]:
            fallback_line = (
                f"스캐너 상위 후보 {fallback_ctx['scanner_top_pick_symbol']}은 {fallback_ctx['reason']} 이유로 보류됐고 "
                f"{symbol}은 차순위 재평가 {rank_text}로 실제 진입 종목이 됐습니다."
            )
        bullets.append(fallback_line)
        if fallback_ctx["trigger_reason"]:
            bullets.append(f"실제 진입은 {fallback_ctx['trigger_reason']} 조건에서 확정됐습니다.")
    if universe not in (None, "") and rank not in (None, ""):
        bullets.append(f"총 {int(universe)}개 후보를 비교했고 {symbol}이 {rank}위로 선정됐습니다.")
    elif rank not in (None, ""):
        bullets.append(f"{symbol}의 최종 선정 순위는 {rank}위였습니다.")
    if score_value is not None:
        metric_bits = [f"종합 점수 {score_value:.3f}"]
        if confidence_value is not None:
            metric_bits.append(f"신뢰도 {confidence_value:.2f}")
        if selected_risk is not None:
            metric_bits.append(f"리스크 {selected_risk:.3f}")
        bullets.append(", ".join(metric_bits) + "로 집계됐습니다.")
    if basis:
        bullets.append(f"주요 선정 기준은 {basis} 축이었습니다.")
    if source_text:
        bullets.append(f"선정에는 {source_text}이 반영됐습니다.")
    if driver_summary:
        bullets.append(f"주요 점수 기여는 {driver_summary}였습니다.")
    if playbook:
        bullets.append(f"전략가 플레이북 {playbook}과 정렬된 후보였습니다.")
    if ranked_rows:
        ranked_text = " / ".join(
            f"#{int(float(row.get('rank') or idx + 1))} {_clip(row.get('symbol'), max_len=24)}({_fmt_num(row.get('score_total'))})"
            for idx, row in enumerate(ranked_rows[:3])
            if _clip(row.get("symbol"), max_len=24)
        )
        if ranked_text:
            bullets.append(f"상위 후보는 {ranked_text} 순이었습니다.")
    if coverage:
        present = int(float(coverage.get("present") or 0)) if _num_opt(coverage.get("present")) is not None else 0
        total = int(float(coverage.get("total") or 0)) if _num_opt(coverage.get("total")) is not None else 0
        missing = [
            _scanner_chart_feature_label(item)
            for item in _listify(coverage.get("missing_keys"), max_items=4, max_len=80)
            if _scanner_chart_feature_label(item)
        ]
        coverage_text = f"차트 피처 커버리지는 {present}/{total}였습니다." if present and total else ""
        if coverage_text and missing:
            coverage_text += f" 누락된 항목은 {', '.join(missing)}이었습니다."
        elif missing:
            coverage_text = f"누락된 차트 피처는 {', '.join(missing)}였습니다."
        if coverage_text:
            bullets.append(coverage_text)
    for row in list(scanner_reason.get("runner_ups") or [])[:2]:
        if isinstance(row, dict):
            rendered = _build_runner_up_comparison(
                row,
                selected_symbol=symbol,
                selected_score=score_value,
                selected_risk=selected_risk,
            )
            if rendered:
                bullets.append(rendered)
    return _dedupe_list(bullets, max_items=10, max_len=260)



def build_scanner_choice_summary(scanner_reason: Dict[str, Any], market_context: Dict[str, Any], *, deps: Mapping[str, Any]) -> str:
    _build_runner_up_comparison = deps["build_runner_up_comparison"]
    _build_scanner_driver_summary = deps["build_scanner_driver_summary"]
    _clip = deps["clip"]
    _market_token_label = deps["market_token_label"]
    _num_opt = deps["num_opt"]
    _scanner_basis_text = deps["scanner_basis_text"]
    _scanner_monitor_fallback_context = deps["scanner_monitor_fallback_context"]
    _scanner_ranked_candidates = deps["scanner_ranked_candidates"]
    _scanner_selected_row = deps["scanner_selected_row"]
    _scanner_source_text = deps["scanner_source_text"]
    symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24) or "선정 종목"
    rank = scanner_reason.get("selected_rank")
    universe = scanner_reason.get("universe_size")
    score_value = _num_opt(scanner_reason.get("selected_score"))
    basis = _scanner_basis_text(scanner_reason)
    sources = _scanner_source_text(scanner_reason.get("selected_sources"))
    playbook = _market_token_label(market_context.get("playbook")) or _clip(market_context.get("playbook"), max_len=32)
    confidence_value = _num_opt(scanner_reason.get("confidence"))
    ranked_rows = _scanner_ranked_candidates(scanner_reason)
    selected_row = _scanner_selected_row(scanner_reason)
    selected_risk = _num_opt(selected_row.get("risk_score"))
    fallback_ctx = _scanner_monitor_fallback_context(scanner_reason)
    driver_summary = _build_scanner_driver_summary(scanner_reason)
    comparison_bits: List[str] = []
    for row in list(scanner_reason.get("runner_ups") or [])[:2]:
        if not isinstance(row, dict):
            continue
        rendered = _build_runner_up_comparison(
            row,
            selected_symbol=symbol,
            selected_score=score_value,
            selected_risk=selected_risk,
        )
        if rendered:
            comparison_bits.append(rendered.rstrip("."))

    if fallback_ctx["used"] and fallback_ctx["scanner_top_pick_symbol"]:
        rank_text = f"{rank}위" if rank not in (None, "") else "후보"
        summary = (
            f"스캐너 상위 후보 {fallback_ctx['scanner_top_pick_symbol']}이 모니터 단계에서 보류된 뒤 "
            f"{symbol}이 차순위 재평가 {rank_text}로 실제 진입 종목에 선택됐습니다"
        )
        if fallback_ctx["reason"]:
            summary = (
                f"스캐너 상위 후보 {fallback_ctx['scanner_top_pick_symbol']}이 {fallback_ctx['reason']} 이유로 보류된 뒤 "
                f"{symbol}이 차순위 재평가 {rank_text}로 실제 진입 종목에 선택됐습니다"
            )
    elif universe not in (None, "") and rank == 1:
        summary = f"{symbol}은 총 {int(universe)}개 후보 중 1위로 선정됐습니다"
    elif rank == 1:
        summary = f"{symbol}은 스캐너 후보 중 최종 1순위였습니다"
    else:
        summary = f"{symbol}이 스캐너 후보로 선정됐습니다"
    if universe not in (None, "") and rank not in (None, ""):
        if not (rank == 1 and summary.endswith("선정됐습니다")):
            summary += f". 총 {int(universe)}개 후보 중 {rank}위였습니다"
    elif rank not in (None, ""):
        summary += f". 선정 순위는 {rank}위였습니다"
    elif universe not in (None, ""):
        summary += f". 비교한 후보는 총 {int(universe)}개였습니다"
    if score_value is not None:
        if fallback_ctx["used"]:
            summary += f". 실제 진입 후보의 종합 점수는 {score_value:.3f}였습니다"
        elif rank == 1:
            summary += f". 종합 점수는 {score_value:.3f}로 가장 높았습니다"
        else:
            summary += f". 종합 점수는 {score_value:.3f}였습니다"
    if basis:
        summary += f". 강했던 축은 {basis} 축이었습니다"
    details: List[str] = []
    if sources:
        details.append(f"선정에는 {sources}이 반영됐습니다")
    if driver_summary:
        details.append(f"핵심 점수 기여는 {driver_summary}였습니다")
    if confidence_value is not None:
        details.append(f"신뢰도는 {confidence_value:.2f} 수준이었습니다")
    if selected_risk is not None:
        details.append(f"리스크는 {selected_risk:.3f} 수준이었습니다")
    if playbook:
        details.append(f"전략가 플레이북 {playbook}과도 정렬됐습니다")
    if details:
        summary += ". " + ". ".join(details) + "."
    if comparison_bits:
        summary += " " + ". ".join(comparison_bits) + "."
    return summary



def build_scanner_candidate_comparison_section(scanner_reason: Dict[str, Any], market_context: Dict[str, Any], *, deps: Mapping[str, Any]) -> Dict[str, Any]:
    _build_scanner_choice_bullets = deps["build_scanner_choice_bullets"]
    _build_scanner_choice_summary = deps["build_scanner_choice_summary"]
    _clip = deps["clip"]
    _dedupe_list = deps["dedupe_list"]
    _num_opt = deps["num_opt"]
    _scanner_ranked_candidates = deps["scanner_ranked_candidates"]
    ranked_rows = _scanner_ranked_candidates(scanner_reason)
    runner_ups = [row for row in list(scanner_reason.get("runner_ups") or []) if isinstance(row, dict)]
    runner_ups_lost = [row for row in list(scanner_reason.get("runner_ups_lost") or []) if isinstance(row, dict)]
    symbol = _clip(scanner_reason.get("selected_symbol"), max_len=24) or "?? ?? ???"
    universe = scanner_reason.get("universe_size")
    if not ranked_rows and universe in (None, "", 0):
        if runner_ups or runner_ups_lost:
            bullets: List[str] = []
            for row in runner_ups[:2]:
                comp_symbol = _clip(row.get("symbol"), max_len=24)
                comp_rank = _clip(row.get("rank"), max_len=8) or "?"
                comp_score = _num_opt(row.get("score_total"))
                comp_why = _clip(row.get("why"), max_len=160)
                if not comp_symbol:
                    continue
                detail = f"{comp_symbol}? rank {comp_rank}"
                if comp_score is not None:
                    detail += f", score {comp_score:.3f}"
                if comp_why:
                    detail += f", ?? ??? {comp_why}"
                bullets.append(detail + "???.")
            for row in runner_ups_lost[:2]:
                lost_symbol = _clip(row.get("symbol"), max_len=24)
                lost_reason = _clip(row.get("summary") or row.get("reason"), max_len=160)
                if lost_symbol and lost_reason:
                    bullets.append(f"{lost_symbol} ?? ??? {lost_reason}???.")
                elif lost_symbol:
                    bullets.append(f"{lost_symbol}? runner-up ????? ?? ????? ?????.")
            return {
                "summary": f"{symbol} ???? runner-up ?? ??? ??? ????.",
                "bullets": _dedupe_list(bullets, max_items=12, max_len=260),
            }
        return {
            "summary": "??? ?? ??? ?? ?? ?? ?? ??? ??????.",
            "bullets": [
                f"?? ??? {symbol}?? ????? ranked candidate / runner-up trace? ?? ?? ??? ??????.",
            ],
        }

    summary = _build_scanner_choice_summary(scanner_reason, market_context)
    bullets = _build_scanner_choice_bullets(scanner_reason, market_context)
    if universe not in (None, "") and ranked_rows:
        try:
            universe_count = int(float(universe))
        except Exception:
            universe_count = 0
        bullets = [f"??? ???? ?? ?? {universe_count}?????."] + list(bullets)
    return {
        "summary": summary,
        "bullets": _dedupe_list(bullets, max_items=12, max_len=260),
    }

# Entry / holding / reporter / execution / exit section builders.


