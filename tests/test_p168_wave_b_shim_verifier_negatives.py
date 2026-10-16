"""Rework 054: fail-closed verifier of the V2-053 identity shims used by the Wave B moved-body gate.

Positive: the five real tracked shims pass. Negative: disposable source strings derived from a real shim (nothing on
disk is modified) must all be rejected, including the three Codex counterexamples (extra `raise`, extra
`import subprocess`, wrong canonical import target). The verifier parses source only; it never imports a shim.
"""
import importlib.util
import sys
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("_wave_b_gate", ROOT / "tests" / "test_p154_wave_b_moved_bodies.py")
WB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(WB)

LEGACY = "libs/runtime/scanner/macro_focus.py"
CANON = WB.SHIM_ALLOWLIST[LEGACY]
GOOD = (ROOT / LEGACY).read_text(encoding="utf-8")
IMP = "import sys as _sys"
FRM = "from libs.agents.scanner.context import macro_focus as _canonical"
ASG = "_sys.modules[__name__] = _canonical"


def test_allowlist_is_exactly_the_five_v2_mappings():
    assert WB.SHIM_ALLOWLIST_VERSION == "V2-053/054"
    assert WB.SHIM_ALLOWLIST == {
        f"libs/runtime/scanner/{m}.py": f"libs/agents/scanner/context/{m}.py"
        for m in ("feature_coverage", "sentiment_inputs", "scoring_inputs", "macro_focus", "macro_chart_fit")
    }


@pytest.mark.parametrize("legacy", sorted(WB.SHIM_ALLOWLIST))
def test_real_shims_verify_and_resolve_to_the_allowlisted_body(legacy):
    assert WB._owner_file(legacy) == WB.SHIM_ALLOWLIST[legacy]
    assert WB._verify_identity_shim_source((ROOT / legacy).read_text(encoding="utf-8"), legacy,
                                           WB.SHIM_ALLOWLIST[legacy]) == WB.SHIM_ALLOWLIST[legacy]


def test_comment_and_docstring_variants_are_accepted():
    assert WB._verify_identity_shim_source(f"# c\n{IMP}\n{FRM}  # c\n{ASG}\n", LEGACY, CANON) == CANON
    assert WB._verify_identity_shim_source(f'"""doc"""\n{IMP}\n{FRM}\n{ASG}\n', LEGACY, CANON) == CANON


MUTATIONS = {
    # the three Codex counterexamples
    "codex_extra_raise": GOOD + "\nraise RuntimeError(123)\n",
    "codex_extra_import_subprocess": GOOD + "\nimport subprocess\n",
    "codex_wrong_canonical_target": GOOD.replace(FRM, "from libs.agents.scanner.context import scoring_inputs as _canonical"),
    # further mutations
    "wrong_canonical_package": GOOD.replace(FRM, "from libs.agents.scanner import macro_focus as _canonical"),
    "wrong_module_name": GOOD.replace(FRM, "from libs.agents.scanner.context import macro_focusx as _canonical"),
    "import_alias_mismatch": GOOD.replace(FRM, "from libs.agents.scanner.context import macro_focus as canonical"),
    "relative_import": GOOD.replace(FRM, "from .context import macro_focus as _canonical"),
    "sys_alias_mismatch": GOOD.replace(IMP, "import sys"),
    "extra_import_in_from": GOOD.replace(FRM, FRM + ", sentiment_inputs"),
    "extra_assignment": GOOD + "\nX = 1\n",
    "extra_call": GOOD + "\nprint('x')\n",
    "call_before": f"__import__('os')\n{IMP}\n{FRM}\n{ASG}\n",
    "nonstandard_target_key": GOOD.replace(ASG, "_sys.modules['x'] = _canonical"),
    "nonstandard_target_attr": GOOD.replace(ASG, "_sys.path[__name__] = _canonical"),
    "wrong_value": GOOD.replace(ASG, "_sys.modules[__name__] = _sys"),
    "augmented_double_target": GOOD.replace(ASG, "a = _sys.modules[__name__] = _canonical"),
    "reordered": f"{IMP}\n{ASG}\n{FRM}\n",
    "missing_assignment": f"{IMP}\n{FRM}\n",
    "function_added": GOOD + "\ndef f():\n    return 1\n",
    "malformed_syntax": GOOD + "\ndef (:\n",
    "empty": "",
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_every_mutation_is_rejected(name):
    with pytest.raises(AssertionError):
        WB._verify_identity_shim_source(MUTATIONS[name], LEGACY, CANON)


def test_mutated_file_is_rejected_through_owner_file(tmp_path, monkeypatch):
    fake_root = tmp_path / "repo"
    target = fake_root / LEGACY
    target.parent.mkdir(parents=True)
    target.write_text(MUTATIONS["codex_extra_raise"], encoding="utf-8")
    (fake_root / CANON).parent.mkdir(parents=True)
    (fake_root / CANON).write_text("", encoding="utf-8")
    monkeypatch.setattr(WB, "ROOT", fake_root)
    with pytest.raises(AssertionError):
        WB._owner_file(LEGACY)


def test_non_allowlisted_owner_is_never_followed():
    assert WB._owner_file("libs/runtime/scanner/candidate_rank.py") == "libs/runtime/scanner/candidate_rank.py"
    assert WB._owner_file("libs/runtime/scanner/candidate_risk.py") == "libs/runtime/scanner/candidate_risk.py"


def test_verifier_does_not_import_the_shim():
    for m in [k for k in sys.modules if k.startswith("libs.runtime.scanner.macro_focus")]:
        sys.modules.pop(m)
    WB._verify_identity_shim_source(GOOD, LEGACY, CANON)
    assert "libs.runtime.scanner.macro_focus" not in sys.modules


def test_optimized_python_rejects_all_mutations_without_assert_statements():
    # Import plain source under -O, outside pytest assertion rewriting. Explicit
    # raises in the child also ensure the test itself cannot pass through -O.
    code = """
import runpy
ns = runpy.run_path('tests/test_p168_wave_b_shim_verifier_negatives.py')
wb = ns['WB']
for legacy, canonical in wb.SHIM_ALLOWLIST.items():
    wb._verify_identity_shim_source((ns['ROOT'] / legacy).read_text(encoding='utf-8'), legacy, canonical)
for name, source in ns['MUTATIONS'].items():
    try:
        wb._verify_identity_shim_source(source, ns['LEGACY'], ns['CANON'])
    except AssertionError:
        continue
    raise RuntimeError('optimized verifier accepted ' + name)
print('OPTIMIZED_REJECTED=' + str(len(ns['MUTATIONS'])))
"""
    result = subprocess.run([sys.executable, "-O", "-c", code], cwd=ROOT,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == f"OPTIMIZED_REJECTED={len(MUTATIONS)}"
