"""Strategist market key-event extraction (pure).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _key_events_r3_impl(
    *,
    state,
    global_signal,
    news_signal_map,
    market_regime,
    playbook,
    market_context_inputs,
    news_ctx,
    theme_strength,
    facade,
):
    out: List[str] = []

    def add(x: Any) -> None:
        s = str(x or "").strip()
        if s and s not in out:
            out.append(s)

    # highest priority: explicit externally-provided macro/event list
    for key in ("macro_events", "global_events", "major_events"):
        vals = state.get(key)
        if isinstance(vals, list):
            for row in vals:
                add(row)
            break

    add(
        "global_sentiment "
        f"score={facade._signal_score(global_signal):.3f} "
        f"status={str(global_signal.get('status') or '')} "
        f"source={str(global_signal.get('source') or '')}"
    )
    components = global_signal.get("components") if isinstance(global_signal.get("components"), dict) else {}
    if components:
        add(
            "us_indices "
            f"sp500={facade._to_float(components.get('sp500_ret'), 0.0) * 100.0:.2f}% "
            f"nasdaq={facade._to_float(components.get('nasdaq_ret'), 0.0) * 100.0:.2f}% "
            f"dow={facade._to_float(components.get('dow_ret'), 0.0) * 100.0:.2f}%"
        )
    korea_indices = global_signal.get("korea_indices") if isinstance(global_signal.get("korea_indices"), dict) else {}
    korea_rows = korea_indices.get("indices") if isinstance(korea_indices.get("indices"), dict) else {}
    kospi = korea_rows.get("KOSPI") if isinstance(korea_rows.get("KOSPI"), dict) else {}
    kosdaq = korea_rows.get("KOSDAQ") if isinstance(korea_rows.get("KOSDAQ"), dict) else {}
    if kospi or kosdaq:
        bits: List[str] = []
        if kospi:
            bits.append(
                "kospi="
                f"{facade._to_float(kospi.get('current'), 0.0):.2f}"
                f"/prev={facade._to_float(kospi.get('previous_close'), 0.0):.2f}"
                f"/chg={facade._to_float(kospi.get('change_pct'), 0.0):+.2f}%"
            )
        if kosdaq:
            bits.append(
                "kosdaq="
                f"{facade._to_float(kosdaq.get('current'), 0.0):.2f}"
                f"/prev={facade._to_float(kosdaq.get('previous_close'), 0.0):.2f}"
                f"/chg={facade._to_float(kosdaq.get('change_pct'), 0.0):+.2f}%"
            )
        add("korea_indices " + " ".join(bits))
    fear_index = global_signal.get("fear_index") if isinstance(global_signal.get("fear_index"), dict) else {}
    if fear_index:
        add(
            "fear_index "
            f"vix={facade._to_float(fear_index.get('level'), 0.0):.2f} "
            f"change={facade._to_float(fear_index.get('change_pct'), 0.0):.2f}% "
            f"pressure={facade._to_float(fear_index.get('level_pressure'), 0.0):.3f}"
        )
    add(
        "market_context "
        f"index_trend={facade._to_float(market_context_inputs.get('index_trend'), 0.0):.3f} "
        f"breadth={facade._to_float(market_context_inputs.get('market_breadth'), 0.0):.3f} "
        f"realized_vol={facade._to_float(market_context_inputs.get('realized_volatility'), 0.0):.3f} "
        f"macro_risk={facade._to_float(market_context_inputs.get('macro_risk'), 0.0):.3f}"
    )
    add(
        "news_signal_health "
        f"ok={int(news_ctx.get('ok') or 0)} "
        f"unavailable={int(news_ctx.get('unavailable') or 0)} "
        f"fallback={int(news_ctx.get('fallback') or 0)} "
        f"avg_score={facade._to_float(news_ctx.get('avg_score'), 0.0):.3f}"
    )
    if theme_strength:
        top_theme = sorted(theme_strength.items(), key=lambda kv: kv[1], reverse=True)[0]
        add(f"theme_strength top={top_theme[0]} score={float(top_theme[1]):.3f}")
    add(f"market_regime={market_regime}")
    add(f"playbook={playbook}")

    return out[:5]
