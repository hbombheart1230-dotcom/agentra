from __future__ import annotations

from typing import Any, Dict, List



def _market_token_label_impl(value: Any, *, _clip) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "neutral": "중립",
        "bullish": "강세",
        "bearish": "약세",
        "pullback": "눌림목",
        "breakout": "돌파",
        "trend": "추세",
        "defensive": "방어적",
        "risk_off": "위험회피",
        "risk_on": "위험선호",
        "not_captured": "직접 캡처되지 않음",
        "unavailable": "확인 불가",
    }
    return mapping.get(raw, _clip(value, max_len=80))

def _theme_token_label_impl(value: Any, *, _clip) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "broad_market_leaders": "브로드마켓 리더",
        "semiconductor_leaders": "반도체 리더",
        "high_beta_leaders": "고베타 리더",
    }
    return mapping.get(raw, _clip(value, max_len=80))

def _theme_text_impl(values: Any, *, max_items: int = 4, _theme_token_label, _listify) -> str:
    labels = [_theme_token_label(item) for item in _listify(values, max_items=max_items, max_len=80)]
    labels = [item for item in labels if item]
    if len(labels) == 2:
        return f"{labels[0]}와 {labels[1]}"
    if len(labels) >= 3:
        return ", ".join(labels[:-1]) + f", {labels[-1]}"
    return labels[0] if labels else "not_captured"

def _theme_linkage_label_impl(values: Any, *, _listify, _theme_text) -> str:
    theme_values = [str(item or "").strip().lower() for item in _listify(values, max_items=4, max_len=80)]
    if "broad_market_leaders" in theme_values:
        return "시장 주도 대형주 우위"
    if "semiconductor_leaders" in theme_values:
        return "반도체 리더 우위"
    if "high_beta_leaders" in theme_values:
        return "고베타 리더 우위"
    themed = _theme_text(values, max_items=2)
    return f"{themed} 맥락" if themed and themed != "not_captured" else "시장 맥락"

def _risk_mode_label_impl(value: Any, *, _clip) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "balanced": "균형형",
        "conservative": "보수형",
        "aggressive": "공격형",
    }
    return mapping.get(raw, _clip(value, max_len=80))

def _strategy_constraint_label_impl(value: Any, *, _clip) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "defensive_assets": "방어 자산",
        "counter_trend_low_liquidity": "역추세 저유동성",
        "high_beta_leaders": "고베타 리더",
        "semiconductor_leaders": "반도체 리더",
        "broad_market_leaders": "브로드마켓 리더",
        "illiquid_microcap": "저유동성 소형주",
        "headline_only_momentum": "헤드라인 추격 모멘텀",
        "high_gap_speculative": "갭 급등 투기성 종목",
    }
    return mapping.get(raw, _clip(value, max_len=80))

def _strategy_constraint_text_impl(values: Any, *, max_items: int = 4, _strategy_constraint_label, _listify) -> str:
    labels = [_strategy_constraint_label(item) for item in _listify(values, max_items=max_items, max_len=80)]
    labels = [item for item in labels if item]
    if len(labels) >= 3:
        return ", ".join(labels[:-1]) + f", {labels[-1]}"
    if len(labels) == 2:
        return ", ".join(labels)
    return labels[0] if labels else ""

def _scanner_bias_label_impl(value: Any, *, _clip) -> str:
    raw = _clip(value, max_len=80).strip().lower()
    mapping = {
        "prefer_shallow_pullback_candidates": "얕은 눌림목 후보 선호",
        "penalize_overextended": "과확장 후보 패널티",
        "prefer_reclaim_candidates": "재회복 후보 선호",
        "prefer_volume_confirmation": "거래량 확인 후보 선호",
    }
    return mapping.get(raw, _clip(value, max_len=80))

def _scanner_bias_text_impl(summary: Any, *, ast, _scanner_bias_label, _listify, _clip) -> str:
    data = summary if isinstance(summary, dict) else {}
    active_values = data.get("active_biases")
    if isinstance(active_values, str):
        raw = active_values.strip()
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = ast.literal_eval(raw)
                if isinstance(parsed, list):
                    active_values = parsed
            except Exception:
                pass
    active = [_scanner_bias_label(item) for item in _listify(active_values, max_items=6, max_len=80)]
    active = [item for item in active if item]
    strength = _clip(data.get("bias_strength"), max_len=24).strip().lower()
    strength_label = {"low": "낮음", "medium": "중간", "high": "높음"}.get(strength, _clip(strength, max_len=24))
    if active:
        joined = ", ".join(active)
        if strength_label:
            return f"{joined} (강도 {strength_label})"
        return joined
    raw_summary = _clip(data.get("summary"), max_len=220)
    return raw_summary
