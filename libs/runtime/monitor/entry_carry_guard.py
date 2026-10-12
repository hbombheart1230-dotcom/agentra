"""Monitor open-carry forced entry-block reason and memory-bias observation flag (pure policy helpers; intent-only role unchanged).

Bodies moved from the public facade. Every former facade module global is
qualified at its use site as `facade.NAME` (explicit injected module; use-time lookup, no entry-time
capture, no getattr fallback), so monkeypatching matches the original module-level resolution.
Owner never imports the facade.
"""
from __future__ import annotations


def _entry_forced_block_reason_for_open_carry_r3_impl(state, all_pos_map, *, now_epoch, facade):
    persisted = state.get("persisted_state") if isinstance(state.get("persisted_state"), dict) else {}
    unresolved: set[str] = set()
    for source in (state, persisted):
        if not isinstance(source, dict):
            continue
        marker = source.get("closeout_unresolved_flatten_by_symbol")
        if isinstance(marker, dict):
            unresolved.update(facade._norm_symbol(x) for x in marker.keys() if facade._norm_symbol(x))
        backup = source.get("closeout_backup_liquidation")
        if isinstance(backup, dict):
            for key in ("unresolved_flatten_symbols", "unresolved_flatten_requires_next_open_symbols"):
                unresolved.update(facade._norm_symbol(x) for x in list(backup.get(key) or []) if facade._norm_symbol(x))

    open_rows = [
        (facade._norm_symbol(sym), row if isinstance(row, dict) else {})
        for sym, row in (all_pos_map or {}).items()
        if facade._norm_symbol(sym) and max(0, facade._to_int((row or {}).get("qty"))) > 0
    ]
    if any(sym in unresolved for sym, _row in open_rows):
        return "closeout_unresolved_flatten_required"

    entry_epoch_by_symbol = (
        persisted.get("position_entry_epoch_by_symbol")
        if isinstance(persisted.get("position_entry_epoch_by_symbol"), dict)
        else {}
    )
    for sym, row in open_rows:
        entry_epoch = facade._to_int(
            row.get("position_entry_epoch")
            if row.get("position_entry_epoch") not in (None, "")
            else row.get("entry_epoch")
        )
        if entry_epoch <= 0:
            entry_epoch = facade._to_int(entry_epoch_by_symbol.get(sym))
        if entry_epoch > 0 and now_epoch > entry_epoch and (now_epoch - entry_epoch) >= 12 * 3600:
            return "overnight_carry_recovery_pending"
    return ""


def _memory_bias_observation_only_r3_impl(state, *, facade):
    if isinstance(state, dict):
        for key in ("memory_bias_observation_only", "commander_memory_bias_observation_only"):
            if state.get(key) not in (None, ""):
                return facade._is_trueish(state.get(key))
    for name in ("MEMORY_BIAS_OBSERVATION_ONLY", "COMMANDER_MEMORY_BIAS_OBSERVATION_ONLY"):
        raw = str(facade.os.getenv(name, "") or "").strip()
        if raw:
            return facade._is_trueish(raw)
    return False
