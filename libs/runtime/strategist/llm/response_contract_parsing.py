"""Strategist LLM response-contract parsing moved from the facade (graphs/nodes/strategist_node.py).

Bodies moved verbatim; every former facade module global (`re`, `json`, `_strip_fenced_block`,
`_parse_text_list_fragment`, `_extract_contract_from_prose`) is qualified at its use site as `facade.NAME`
(explicit injected module, use-time lookup, no entry-time capture), so facade monkeypatching keeps working.
Owner never imports the facade."""
from __future__ import annotations

from typing import Any, Dict


def _extract_contract_from_prose_r3_impl(text: str, *, facade) -> Dict[str, Any]:
    s = facade._strip_fenced_block(text)
    if not s:
        return {}

    out: Dict[str, Any] = {}
    lines = [str(row or "").strip() for row in s.splitlines() if str(row or "").strip()]
    if not lines:
        return {}

    enum_specs: Dict[str, List[str]] = {
        "market_regime": ["risk_on", "neutral", "risk_off"],
        "market_sentiment": ["bullish", "neutral", "bearish"],
        "playbook": ["breakout", "pullback", "reversal", "defensive"],
        "scanner_bias": ["large_cap", "leader", "momentum", "value"],
        "trade_aggressiveness": ["low", "medium", "high"],
        "risk_tone": ["conservative", "normal", "aggressive"],
        "monitor_guidance": ["hold_through_noise", "defensive_exit", "quick_take_profit"],
    }
    list_keys = ("key_events", "themes", "avoid_themes", "scanner_priority", "report_focus")
    alias_map = {
        "market_regime_hint": "market_regime",
        "market_sentiment_hint": "market_sentiment",
        "playbook_hint": "playbook",
        "themes_hint": "themes",
        "key_events_hint": "key_events",
    }

    def normalized_line(raw_line: str) -> str:
        line = str(raw_line or "").strip()
        line = facade.re.sub(r"^\d+\.\s*", "", line)
        line = facade.re.sub(r"^[-*]\s*", "", line)
        line = line.replace("**", "")
        return line.strip()

    for raw_line in lines:
        line = normalized_line(raw_line)
        if not line or ":" not in line:
            continue
        for raw_key in list(enum_specs.keys()) + list(list_keys) + list(alias_map.keys()):
            match = facade.re.search(rf"\b{facade.re.escape(raw_key)}\b\s*:\s*(.+)$", line, flags=facade.re.IGNORECASE)
            if not match:
                continue
            key = alias_map.get(raw_key, raw_key)
            value = str(match.group(1) or "").strip()
            if key in enum_specs:
                matches = facade.re.findall(r"(risk_on|risk_off|neutral|bullish|bearish|breakout|pullback|reversal|defensive|large_cap|leader|momentum|value|low|medium|high|conservative|normal|aggressive|hold_through_noise|defensive_exit|quick_take_profit)", value, flags=facade.re.IGNORECASE)
                if matches:
                    allowed = {item.lower() for item in enum_specs[key]}
                    for candidate in reversed(matches):
                        normalized = str(candidate or "").strip().lower()
                        if normalized in allowed:
                            out[key] = normalized
                            break
            else:
                bracket_match = facade.re.search(r"(\[[^\]]*\])", value)
                parsed = facade._parse_text_list_fragment(bracket_match.group(1) if bracket_match else value)
                if (not parsed) or (parsed and len(parsed) == 1 and parsed[0] == value):
                    quoted = [str(x or "").strip() for x in facade.re.findall(r'"([^"\n]{1,120})"', value) if str(x or "").strip()]
                    if quoted:
                        parsed = quoted
                if key == "scanner_priority" and parsed:
                    allowed_priority = {"trading_value", "trend_strength", "volume_surge", "leader_quality", "pullback_quality", "relative_strength", "risk_penalty", "low_volatility", "drawdown_control", "momentum"}
                    parsed = [x for x in parsed if str(x or "").strip().lower() in allowed_priority]
                if parsed:
                    out[key] = parsed
            break

    # Fall back to broader regex if line-oriented parsing missed obvious fields.
    for key, allowed in enum_specs.items():
        if key in out:
            continue
        raw_keys = [key] + [alias for alias, target in alias_map.items() if target == key]
        match = None
        for raw_key in raw_keys:
            pattern = rf"{facade.re.escape(raw_key)}\s*:\s*([^\n]+)"
            match = facade.re.search(pattern, s, flags=facade.re.IGNORECASE)
            if match:
                break
        if not match:
            continue
        tail = str(match.group(1) or "")
        candidates = facade.re.findall(
            r"(risk_on|risk_off|neutral|bullish|bearish|breakout|pullback|reversal|defensive|large_cap|leader|momentum|value|low|medium|high|conservative|normal|aggressive|hold_through_noise|defensive_exit|quick_take_profit)",
            tail,
            flags=facade.re.IGNORECASE,
        )
        allowed_set = {item.lower() for item in allowed}
        for candidate in reversed(candidates):
            normalized = str(candidate or "").strip().lower()
            if normalized in allowed_set:
                out[key] = normalized
                break

    for key in list_keys:
        if key in out:
            continue
        raw_keys = [key] + [alias for alias, target in alias_map.items() if target == key]
        match = None
        for raw_key in raw_keys:
            match = facade.re.search(rf"{facade.re.escape(raw_key)}\s*:\s*(\[[^\]]*\])", s, flags=facade.re.IGNORECASE | facade.re.DOTALL)
            if match:
                break
        if not match:
            continue
        parsed = facade._parse_text_list_fragment(match.group(1))
        if parsed:
            out[key] = parsed

    has_contract_signal = bool(
        out.get("market_regime")
        or out.get("playbook")
        or out.get("themes")
        or out.get("monitor_guidance")
    )
    return out if has_contract_signal else {}


def _extract_json_object_r3_impl(text: str, *, facade) -> Dict[str, Any]:
    s = facade._strip_fenced_block(text)
    if not s:
        return {}
    contract_keys = {
        "market_regime",
        "market_regime_rail",
        "news_quality",
        "news_event_intelligence_usage",
        "risk_off_exception_conditions",
        "market_sentiment",
        "key_events",
        "themes",
        "avoid_themes",
        "playbook",
        "tactical_strategy",
        "tactical_subtype",
        "strategy_scores",
        "rejected_strategy_reasons",
        "candidate_watch_policy",
        "scanner_bias",
        "scanner_priority",
        "trade_aggressiveness",
        "risk_tone",
        "monitor_guidance",
        "market_regime_summary",
        "policy_rationale",
        "confidence",
        "policy_source",
        "monitor_entry_policy",
        "report_focus",
        "scanner_source_policy",
        "selected_symbol_decision",
        "hold_review_decision",
        "carry_review",
        "portfolio_level_decision",
    }

    def unwrap(obj: Any) -> Dict[str, Any]:
        if isinstance(obj, list) and obj and isinstance(obj[0], dict):
            obj = obj[0]
        if not isinstance(obj, dict):
            return {}
        if any(k in obj for k in contract_keys):
            return obj
        for key in ("strategist_output", "output", "result", "data"):
            nested = obj.get(key)
            if isinstance(nested, dict) and any(k in nested for k in contract_keys):
                merged = dict(obj)
                merged.pop(key, None)
                merged.update(nested)
                return merged
        return obj
    try:
        obj = facade.json.loads(s)
        unwrapped = unwrap(obj)
        if unwrapped:
            return unwrapped
    except Exception:
        pass
    dec = facade.json.JSONDecoder()
    for i, ch in enumerate(s):
        if ch != "{":
            continue
        try:
            obj, _end = dec.raw_decode(s[i:])
            unwrapped = unwrap(obj)
            if unwrapped:
                return unwrapped
        except Exception:
            continue
    prose_contract = facade._extract_contract_from_prose(s)
    if prose_contract:
        return prose_contract
    return {}


def _classify_llm_parse_failure_r3_impl(raw: Any, *, facade) -> str:
    s = facade._strip_fenced_block(str(raw or "")).strip()
    if not s:
        return "strategist_llm_response_empty"
    if s.startswith("{") or s.startswith("[") or "market_regime" in s or "themes" in s:
        return "strategist_llm_response_truncated_json"
    return "strategist_llm_response_not_json"
