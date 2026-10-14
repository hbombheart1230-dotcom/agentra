"""T3.5 deterministic variant corpus for the agent output builders (offline, pure).

`variants(builder, args, kwargs)` yields `(variant_id, args, kwargs)`: single-key perturbations of the *state* (first
positional argument) that drive the builders through their fallback / default / blocked branches, plus a route-grid for
the commander builder. The generator is deterministic and identical on BASE and FEATURE; golden digests are frozen on BASE.
"""
from __future__ import annotations

import copy

COMMANDER_PATHS = ("full_cycle", "monitor_only", "cached_strategist", "blocked", "preopen", "closeout",
                   "strategist_blocked_path", "")
COMMANDER_STATUSES = ("ok", "blocked", "preflight_blocked", "degraded", "")
COMMANDER_PHASES = ("session", "preopen", "closeout", "")
RUNTIME_STATUSES = ("error", "cooldown_wait", "degraded", "ok")
MAX_NESTED = 40


def _empty_like(value):
    if isinstance(value, dict):
        return {}
    if isinstance(value, list):
        return []
    if isinstance(value, str):
        return ""
    if isinstance(value, bool):
        return not value
    if isinstance(value, (int, float)):
        return 0
    return None


def _state_variants(state):
    if not isinstance(state, dict):
        return
    for key in list(state):
        s = copy.deepcopy(state)
        del s[key]
        yield f"drop:{key}", s
        s = copy.deepcopy(state)
        s[key] = None
        yield f"none:{key}", s
        empty = _empty_like(state[key])
        if empty is not None and empty != state[key]:
            s = copy.deepcopy(state)
            s[key] = empty
            yield f"empty:{key}", s
    n = 0
    for key in list(state):
        value = state[key]
        if isinstance(value, dict):
            for sub in list(value):
                if n >= MAX_NESTED:
                    return
                s = copy.deepcopy(state)
                del s[key][sub]
                yield f"drop:{key}.{sub}", s
                n += 1


def variants(builder, args, kwargs):
    args = list(args)
    if args:
        for vid, s in _state_variants(args[0]):
            yield vid, [s] + copy.deepcopy(args[1:]), copy.deepcopy(kwargs)
    if builder in ("build_commander_output_artifact", "build_commander_shadow_artifact") and args:
        base = args[0]
        for path in COMMANDER_PATHS:
            for status in COMMANDER_STATUSES:
                k = copy.deepcopy(kwargs)
                k.update({"path": path, "status": status})
                yield f"route:{path}|{status}", [copy.deepcopy(base)], k
        for phase in COMMANDER_PHASES:
            k = copy.deepcopy(kwargs)
            k["phase"] = phase
            yield f"phase:{phase}", [copy.deepcopy(base)], k
        for rs in RUNTIME_STATUSES:
            s = copy.deepcopy(base)
            s["runtime_status"] = rs
            yield f"runtime_status:{rs}", [s], copy.deepcopy(kwargs)
        for reason in ("", "post_scanner_selected_symbol_refresh", "x" * 300):
            k = copy.deepcopy(kwargs)
            k["reason"] = reason
            yield f"reason:{len(reason)}:{reason[:12]}", [copy.deepcopy(base)], k
