"""Strategist theme-packet merge, available-theme resolution and theme strategy surface (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _merge_theme_packet_into_state_r3_impl(state, packet, *, facade):
    if not isinstance(packet, dict):
        return

    top_theme_names: List[str] = []
    for row in list(packet.get("top_themes") or []):
        if not isinstance(row, dict):
            continue
        name = str(row.get("theme_name") or "").strip()
        if name and name.lower() not in {x.lower() for x in top_theme_names}:
            top_theme_names.append(name)

    if top_theme_names:
        existing_top = list(state.get("top_themes") or []) if isinstance(state.get("top_themes"), list) else []
        merged_top: List[str] = []
        seen_top: set[str] = set()
        for name in [*existing_top, *top_theme_names]:
            text = str(name or "").strip()
            key = text.lower()
            if not text or key in seen_top:
                continue
            seen_top.add(key)
            merged_top.append(text)
        state["top_themes"] = merged_top[:8]

    packet_scores = packet.get("theme_scores") if isinstance(packet.get("theme_scores"), dict) else {}
    if packet_scores:
        scores = dict(state.get("theme_scores") or {}) if isinstance(state.get("theme_scores"), dict) else {}
        lowered = {str(k or "").strip().lower() for k in scores.keys()}
        for name, score in packet_scores.items():
            text = str(name or "").strip()
            if not text or text.lower() in lowered:
                continue
            scores[text] = score
            lowered.add(text.lower())
        state["theme_scores"] = scores

    packet_map = packet.get("theme_map") if isinstance(packet.get("theme_map"), dict) else {}
    packet_map_authoritative = facade._theme_packet_symbol_map_is_authoritative(packet)
    if packet_map or packet_map_authoritative:
        top_theme_keys = {str(name or "").strip().lower() for name in top_theme_names if str(name or "").strip()}

        def packet_symbols_for(theme_key: str) -> List[str]:
            for key, symbols in packet_map.items():
                name = str(key or "").strip().lower()
                if name != theme_key:
                    continue
                out_symbols: List[str] = []
                seen_symbols: set[str] = set()
                if isinstance(symbols, list):
                    for sym in symbols:
                        s = str(sym or "").strip().upper()
                        if not s or s in seen_symbols:
                            continue
                        seen_symbols.add(s)
                        out_symbols.append(s)
                return out_symbols
            return []

        def merge_map(existing: Any) -> Dict[str, List[str]]:
            out: Dict[str, List[str]] = {}
            if isinstance(existing, dict):
                for key, symbols in existing.items():
                    name = str(key or "").strip().lower()
                    if not name:
                        continue
                    bucket: List[str] = []
                    seen: set[str] = set()
                    if isinstance(symbols, list):
                        for sym in symbols:
                            s = str(sym or "").strip().upper()
                            if not s or s in seen:
                                continue
                            seen.add(s)
                            bucket.append(s)
                    out[name] = bucket
            if packet_map_authoritative:
                for name in top_theme_keys:
                    # A Kiwoom theme with no returned component list must stay
                    # empty. Do not backfill it with broad scanner candidates.
                    out[name] = packet_symbols_for(name)
            for key, symbols in packet_map.items():
                name = str(key or "").strip().lower()
                if not name:
                    continue
                bucket = list(out.get(name) or [])
                seen = set(bucket)
                if isinstance(symbols, list):
                    for sym in symbols:
                        s = str(sym or "").strip().upper()
                        if not s or s in seen:
                            continue
                        seen.add(s)
                        bucket.append(s)
                out[name] = bucket
            return out

        state["theme_map"] = merge_map(state.get("theme_map"))
        state["sector_map"] = merge_map(state.get("sector_map"))


def _extract_theme_names_from_any_r3_impl(raw, *, limit, facade):
    out: List[str] = []
    seen: set[str] = set()
    if not isinstance(raw, list):
        return out
    for row in raw:
        if isinstance(row, dict):
            value = row.get("theme") or row.get("theme_name") or row.get("name")
        else:
            value = row
        name = str(value or "").strip()
        key = name.lower()
        if not name or key in seen:
            continue
        seen.add(key)
        out.append(name)
        if len(out) >= max(1, int(limit)):
            break
    return out


def _theme_packet_available_themes_r3_impl(packet, *, limit, facade):
    if not isinstance(packet, dict):
        return []
    component_map = packet.get("component_symbols_by_theme")
    if not isinstance(component_map, dict):
        component_map = packet.get("theme_map") if isinstance(packet.get("theme_map"), dict) else {}

    def component_symbols_for(name: str) -> List[str]:
        for key in (name, name.lower()):
            raw = component_map.get(key) if isinstance(component_map, dict) else None
            if isinstance(raw, list):
                symbols: List[str] = []
                seen_symbols: set[str] = set()
                for item in raw:
                    if isinstance(item, dict):
                        sym = str(item.get("symbol") or item.get("stk_cd") or "").strip().upper()
                    else:
                        sym = str(item or "").strip().upper()
                    if not sym or sym in seen_symbols:
                        continue
                    seen_symbols.add(sym)
                    symbols.append(sym)
                return symbols
        return []

    out: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for row in list(packet.get("top_themes") or []):
        if isinstance(row, dict):
            name = str(row.get("theme_name") or row.get("theme") or "").strip()
            code = str(row.get("theme_code") or row.get("code") or "").strip()
            score = facade._to_float(row.get("score"), 0.0)
            stock_count = facade._to_int(row.get("stock_count"), 0)
            rising_count = facade._to_int(row.get("rising_count"), 0)
            falling_count = facade._to_int(row.get("falling_count"), 0)
        else:
            name = str(row or "").strip()
            code = ""
            score = facade._to_float((packet.get("theme_scores") or {}).get(name) if isinstance(packet.get("theme_scores"), dict) else 0.0, 0.0)
            stock_count = 0
            rising_count = 0
            falling_count = 0
        key = name.lower()
        if not name or key in seen:
            continue
        symbols = component_symbols_for(name)
        out.append(
            {
                "theme": name,
                "theme_code": code,
                "score": float(score),
                "stock_count": int(stock_count),
                "rising_count": int(rising_count),
                "falling_count": int(falling_count),
                "component_count": int(len(symbols)),
                "component_symbols": symbols[:12],
            }
        )
        seen.add(key)
        if len(out) >= max(1, int(limit)):
            break
    return out


def _resolve_selected_themes_from_api_r3_impl(*, available_themes, themes, raw_selected, limit, facade):
    available_names = [str(row.get("theme") or "").strip() for row in available_themes if isinstance(row, dict)]
    canonical_by_key = {name.lower(): name for name in available_names if name}
    requested = facade._extract_theme_names_from_any(raw_selected, limit=limit)
    requested.extend([str(x or "").strip() for x in list(themes or []) if str(x or "").strip()])

    out: List[str] = []
    seen: set[str] = set()
    if canonical_by_key:
        for name in requested:
            canonical = canonical_by_key.get(str(name or "").strip().lower())
            if not canonical:
                continue
            key = canonical.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(canonical)
            if len(out) >= max(1, int(limit)):
                return out
        for row in available_themes:
            canonical = str((row or {}).get("theme") or "").strip()
            key = canonical.lower()
            if not canonical or key in seen:
                continue
            seen.add(key)
            out.append(canonical)
            if len(out) >= max(1, int(limit)):
                break
        return out

    for name in requested:
        text = str(name or "").strip()
        key = text.lower()
        if not text or key in seen:
            continue
        seen.add(key)
        out.append(text)
        if len(out) >= max(1, int(limit)):
            break
    return out


def _build_theme_strategy_surface_r3_impl(
    *,
    available_themes,
    selected_themes,
    playbook,
    theme_strength_packet,
    raw_theme_strategy,
    facade,
):
    raw_strategy = raw_theme_strategy if isinstance(raw_theme_strategy, dict) else {}
    available_by_key = {
        str((row or {}).get("theme") or "").strip().lower(): dict(row)
        for row in available_themes
        if isinstance(row, dict) and str(row.get("theme") or "").strip()
    }
    status = str(theme_strength_packet.get("status") or "").strip().lower()
    source = str(theme_strength_packet.get("source") or "").strip()
    fallback_used = status != "ok" or not available_by_key
    overlay = {
        "breakout": "momentum",
        "pullback": "pullback",
        "reversal": "reversal",
        "defensive": "defensive",
    }.get(str(playbook or "").strip().lower(), "fallback")

    rows: List[Dict[str, Any]] = []
    for name in list(selected_themes or [])[:5]:
        key = str(name or "").strip().lower()
        theme_row = dict(available_by_key.get(key) or {})
        rows.append(
            {
                "theme": str(name or "").strip(),
                "score": float(facade._to_float(theme_row.get("score"), 0.0)),
                "component_count": int(facade._to_int(theme_row.get("component_count"), 0)),
                "playbook_overlay": overlay,
                "scanner_directive": (
                    "키움 테마 구성종목 안에서 거래대금, 거래량, 추세, 모멘텀 우위 후보를 우선 랭킹"
                    if not fallback_used
                    else "키움 테마 미확인 상태이므로 기존 후보 소스와 broad-market fallback 병행"
                ),
                "reason": str(raw_strategy.get("reason") or raw_strategy.get("selection_reason") or "").strip()
                or (
                    "키움 테마 강도 packet에서 선택 가능한 테마로 확인됨"
                    if not fallback_used
                    else str(theme_strength_packet.get("reason") or "kiwoom_theme_unavailable")
                ),
            }
        )

    return {
        "source": source or "kiwoom_theme_strength_packet",
        "status": status or "unavailable",
        "selection_mode": "fallback" if fallback_used else "kiwoom_api_constrained",
        "available_theme_count": int(len(available_themes)),
        "selected_themes": rows,
        "selected_theme_names": [str(x or "") for x in list(selected_themes or [])[:5] if str(x or "").strip()],
        "fallback_used": bool(fallback_used),
        "fallback_reason": "" if not fallback_used else str(theme_strength_packet.get("reason") or "kiwoom_theme_unavailable"),
    }
