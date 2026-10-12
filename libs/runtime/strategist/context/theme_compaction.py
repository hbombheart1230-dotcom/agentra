"""Strategist theme strength/summary compaction and theme-to-news query helpers (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _compact_theme_strength_for_llm_r3_impl(raw, *, limit, facade):
    src = raw if isinstance(raw, dict) else {}
    rows: list[tuple[str, float]] = []
    for key, value in src.items():
        score = facade._stage_float(value, None)
        if score is None:
            continue
        rows.append((str(key), float(score)))
    rows.sort(key=lambda item: item[1], reverse=True)
    return {key: facade._round_optional(value, 4) for key, value in rows[: max(0, int(limit))]}


def _theme_packet_summary_for_llm_r3_impl(packet, *, facade):
    src = packet if isinstance(packet, dict) else {}
    groups = src.get("groups") if isinstance(src.get("groups"), list) else []
    components = src.get("components_by_theme") if isinstance(src.get("components_by_theme"), dict) else {}
    return {
        "status": str(src.get("status") or ""),
        "source": str(src.get("source") or ""),
        "group_count": int(len(groups)),
        "component_theme_count": int(len(components)),
        "fallback_used": bool(src.get("fallback_used")),
        "fallback_reason": str(src.get("fallback_reason") or src.get("reason") or "")[:160],
    }


def _extract_themes_r3_impl(state, policy, *, facade):
    out: List[str] = []
    seen = set()

    def add_many(items: Any) -> None:
        if not isinstance(items, list):
            return
        for x in items:
            t = str(x or "").strip()
            if not t or t in seen:
                continue
            seen.add(t)
            out.append(t)

    add_many(state.get("themes"))
    add_many(state.get("top_themes"))
    add_many(state.get("sector_filter"))
    add_many(state.get("theme_filter"))
    add_many(policy.get("themes"))
    add_many(policy.get("top_themes"))
    add_many(policy.get("sector_filter"))
    add_many(policy.get("theme_filter"))

    theme_scores = state.get("theme_scores") if isinstance(state.get("theme_scores"), dict) else {}
    if theme_scores:
        ranked = sorted(
            ((str(k or "").strip(), float(v or 0.0)) for k, v in theme_scores.items()),
            key=lambda kv: kv[1],
            reverse=True,
        )
        for name, _score in ranked:
            if name and name not in seen:
                seen.add(name)
                out.append(name)

    theme_map = policy.get("theme_map") if isinstance(policy.get("theme_map"), dict) else {}
    for k in theme_map.keys():
        name = str(k or "").strip()
        if name and name not in seen:
            seen.add(name)
            out.append(name)

    return out[:5]


def _theme_to_news_queries_r3_impl(theme, *, facade):
    raw = str(theme or "").strip()
    if not raw:
        return []
    key = raw.lower().replace("-", "_").replace(" ", "_")
    direct_map: Dict[str, List[str]] = {
        "semiconductor": ["반도체", "HBM", "메모리"],
        "semiconductors_hbm": ["반도체", "HBM", "메모리"],
        "ai": ["AI", "인공지능"],
        "battery": ["2차전지", "배터리"],
        "secondary_battery": ["2차전지", "배터리"],
        "defense": ["방산"],
        "energy_security": ["에너지", "국제유가", "천연가스"],
        "renewable_energy": ["재생에너지", "태양광"],
        "bio": ["바이오", "제약"],
        "healthcare": ["헬스케어", "바이오"],
        "finance": ["금융", "은행"],
        "banks": ["금융", "은행"],
        "internet": ["인터넷", "플랫폼"],
        "platform": ["플랫폼", "인터넷"],
        "shipbuilding": ["조선"],
        "autos": ["자동차"],
        "robotics": ["로봇"],
        "broad_market_leaders": ["시가총액 상위", "주도주"],
        "quality_factor": ["실적주", "대형주"],
        "low_volatility": ["방어주", "저변동성"],
    }
    if key in direct_map:
        return list(direct_map[key])
    terms: List[str] = []
    if "semiconductor" in key or "memory" in key:
        terms.extend(["반도체", "HBM"])
    if key == "ai" or "artificial_intelligence" in key:
        terms.extend(["AI", "인공지능"])
    if "energy" in key:
        terms.extend(["에너지", "국제유가"])
    if "defense" in key:
        terms.append("방산")
    if "battery" in key:
        terms.extend(["2차전지", "배터리"])
    if "bank" in key or "finance" in key:
        terms.extend(["금융", "은행"])
    if not terms:
        terms.append(raw)
    return terms


def _theme_news_query_terms_r3_impl(theme_hints, *, limit, facade):
    out: List[str] = []
    seen: set[str] = set()
    for raw in list(theme_hints or [])[:5]:
        text = str(raw or "").strip()
        if not text:
            continue
        facade._append_unique_text(out, seen, text)
        for q in facade._theme_to_news_queries(text)[:2]:
            facade._append_unique_text(out, seen, q)
        if len(out) >= max(1, int(limit)):
            break
    return out[: max(1, int(limit))]


def _theme_component_symbols_for_news_r3_impl(*, state, available_themes, theme_hints, limit, facade):
    max_symbols = max(0, int(limit))
    if max_symbols <= 0:
        return []
    selected_keys = {str(x or "").strip().lower() for x in list(theme_hints or []) if str(x or "").strip()}
    out: List[str] = []
    seen: set[str] = set()

    def add_symbol(raw: Any) -> None:
        symbol = str(raw or "").strip().upper()
        if not symbol or symbol in seen or len(out) >= max_symbols:
            return
        seen.add(symbol)
        out.append(symbol)

    for row in list(available_themes or [])[:5]:
        if not isinstance(row, dict):
            continue
        theme_name = str(row.get("theme") or row.get("theme_name") or "").strip().lower()
        if selected_keys and theme_name and theme_name not in selected_keys:
            continue
        for sym in list(row.get("component_symbols") or [])[:4]:
            add_symbol(sym)
        if len(out) >= max_symbols:
            return out

    for raw_map in (state.get("theme_map"), state.get("sector_map")):
        if not isinstance(raw_map, dict):
            continue
        for theme_name, symbols in raw_map.items():
            key = str(theme_name or "").strip().lower()
            if selected_keys and key and key not in selected_keys:
                continue
            if not isinstance(symbols, list):
                continue
            for sym in symbols[:4]:
                add_symbol(sym)
            if len(out) >= max_symbols:
                return out
    return out


def _extract_theme_symbol_index_r3_impl(state, policy, *, facade):
    out: Dict[str, set[str]] = {}

    def add_map(raw: Any) -> None:
        if not isinstance(raw, dict):
            return
        for k, symbols in raw.items():
            name = str(k or "").strip().lower()
            if not name:
                continue
            bucket = out.setdefault(name, set())
            if isinstance(symbols, list):
                for sym in symbols:
                    s = str(sym or "").strip().upper()
                    if s:
                        bucket.add(s)

    add_map(state.get("theme_map"))
    add_map(state.get("sector_map"))
    add_map(policy.get("theme_map"))
    add_map(policy.get("sector_map"))
    return out


def _merge_theme_symbol_map_r3_impl(existing, *, themes, candidate_symbols, protect_existing_themes, facade):
    out: Dict[str, List[str]] = {}

    if isinstance(existing, dict):
        for key, symbols in existing.items():
            name = str(key or "").strip().lower()
            if not name:
                continue
            merged: List[str] = []
            seen: set[str] = set()
            if isinstance(symbols, list):
                for sym in symbols:
                    s = str(sym or "").strip().upper()
                    if not s or s in seen:
                        continue
                    seen.add(s)
                    merged.append(s)
            out[name] = merged

    if not candidate_symbols:
        return out

    for theme in themes:
        name = str(theme or "").strip().lower()
        if not name:
            continue
        bucket = list(out.get(name) or [])
        if protect_existing_themes:
            out[name] = bucket
            continue
        seen = set(bucket)
        for sym in candidate_symbols:
            s = str(sym or "").strip().upper()
            if not s or s in seen:
                continue
            seen.add(s)
            bucket.append(s)
        out[name] = bucket
    return out
