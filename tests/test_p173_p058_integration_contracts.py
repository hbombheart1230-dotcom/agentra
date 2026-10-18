"""P15-058 integration contracts: Gate A repeat_guard probe (real history key + nested policy) and the combined agent tree.

The fixture was generated from the pinned V4 BASE tree (0a3a224) BEFORE the move by
scripts/refactor/p173_v4056_repeat_guard_cases.py; the immutable V4 318-case fixture is untouched.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "refactor"))
FIX = ROOT / "tests" / "fixtures" / "p1_5_p058_repeat_guard" / "cases.json"


def _ok(case):
    out = case["result"].get("ok")
    return out if isinstance(out, dict) else {}


def test_fixture_exercises_the_real_history_key_and_nested_policy_with_repeat_hits():
    cases = json.loads(FIX.read_text(encoding="utf-8"))["cases"]
    assert len(cases) == 286
    block = [c for c in cases if c["fn"] == "_repeat_blocker_cooldown_penalty"]
    sel = [c for c in cases if c["fn"] == "_repeat_symbol_penalty"]
    assert any(_ok(c).get("repeat_count", 0) > 0 for c in block)      # recent_monitor_blocks consumed
    assert any(_ok(c).get("repeat_count", 0) > 0 for c in sel)
    assert any(_ok(c).get("penalty", 0) > 0 for c in cases) and any(_ok(c).get("penalty") == 0 for c in cases)
    assert any("exc" in c["result"] for c in cases)                    # policy=None exception type is frozen too
    assert {c["result"]["monitor_eval_calls"] for c in cases if c["fn"] == "_compute_entry_compatibility_signal"} == {0, 1}
    assert not any(c["result"]["mutated_inputs"] for c in cases)
    hist = [c for c in cases if c["fn"] == "_scanner_recent_block_history" and c["args"][0].get("persisted_state", {}).get("recent_monitor_blocks")]
    assert hist and any(len(_ok_list(c)) > 0 for c in hist)


def _ok_list(case):
    out = case["result"].get("ok")
    return out if isinstance(out, list) else []


def test_final_tree_reproduces_every_pinned_base_case_exactly():
    import p173_v4056_repeat_guard_cases as C
    doc = json.loads(FIX.read_text(encoding="utf-8"))
    got = C.compute()
    assert len(got) == len(doc["cases"])
    for a, b in zip(got, doc["cases"]):
        assert a == b, (b["fn"], b["args"], b["kwargs"])
        assert json.dumps(a, ensure_ascii=False) == json.dumps(b, ensure_ascii=False), (b["fn"], "key order")


def test_combined_agent_tree_is_exactly_the_versioned_allowlist():
    import p15_agent_tree_allowlist as AL
    assert AL.actual_dirs(ROOT / "libs/agents") == set(AL.AGENT_PACKAGES)
    assert AL.actual_dirs(ROOT / "libs/agents/scanner") == set(AL.SCANNER_PACKAGES)
    assert AL.actual_dirs(ROOT / "libs/agents/strategist") == set(AL.STRATEGIST_PACKAGES)
    assert AL.actual_dirs(ROOT / "libs/agents/reporter") == set(AL.REPORTER_PACKAGES)
    assert AL.actual_dirs(ROOT / "libs/agents/monitor") == set(AL.MONITOR_PACKAGES)
