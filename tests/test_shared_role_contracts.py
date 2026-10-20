"""Mutations target real sources without writing or executing production code."""
import ast
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/refactor"))
import shared_role_contracts as S


def test_exact_combined_runtime_inputs_and_restoration():
    result = S.verify_runtime()
    assert result["moves"] == 313 and result["facades"] == 23
    assert result["monitor_modules"] == 14 and result["monitor_bodies"] == 20


@pytest.mark.parametrize("kind", ["shim_import", "shim_duplicate", "shim_redirect", "owner_body",
                                  "unmoved", "wrapper", "broker", "numbered_owner"])
def test_real_source_mutations_fail_closed(kind):
    # A rejected mutant is evidence only when the exact unmodified input passes.
    assert S.verify_runtime()["moves"] == 313
    path = next(iter(S.whole_moves()))
    source = (ROOT / path).read_text(encoding="utf-8-sig")
    if kind == "shim_import":
        changes = {path: source + "\nimport os\n"}
    elif kind == "shim_duplicate":
        changes = {path: source + source}
    elif kind == "shim_redirect":
        changes = {path: source.replace("from libs.agents.monitor.", "from libs.agents.rogue.")}
    elif kind == "owner_body":
        owner = S.whole_moves()[path]
        changes = {owner: (ROOT / owner).read_text(encoding="utf-8-sig") + "\nBROKER = True\n"}
    elif kind in {"unmoved", "wrapper"}:
        path = "libs/runtime/monitor_exit/reasons.py"
        tree = ast.parse((ROOT / path).read_text(encoding="utf-8-sig"))
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                  and (n.name in S.M.BODY_MOVES[path]["functions"]) == (kind == "wrapper"))
        fn.body = ast.parse("return None").body
        changes = {path: ast.unparse(tree)}
    else:
        path = "libs/broker/shared_candidate_rogue.py" if kind == "broker" else "libs/agents/reporter/narrative/rogue_bodies_09.py"
        changes = {path: "BROKER_CAPABILITY = True\n"}
    message = "unexpected/missing runtime path" if kind in {"broker", "numbered_owner"} else "unapproved runtime body/import/authority"
    with pytest.raises(AssertionError, match=message) as rejected:
        S.verify_runtime(changes)
    assert next(iter(changes)) in str(rejected.value)


def test_shared_checker_rejects_mutation_under_optimized_python():
    code = '''import sys
sys.path.insert(0, 'scripts/refactor')
import shared_role_contracts as S
if S.verify_runtime()['moves'] != 313:
    raise SystemExit('unmutated runtime did not pass')
try:
    S.verify_runtime({'libs/broker/rogue.py': 'pass'})
except AssertionError:
    pass
else:
    raise SystemExit('optimized guard accepted Broker mutation')
'''
    subprocess.run([sys.executable, "-O", "-c", code], cwd=ROOT, check=True)


@pytest.mark.parametrize("path", sorted(S.whole_moves()))
def test_each_identity_shim_rejects_executable_statement_before_resolution(path):
    original = (ROOT / path).read_text(encoding="utf-8-sig")
    with pytest.raises(AssertionError, match="nonexact identity shim"):
        S.source(path, {path: original + "\nraise RuntimeError('rogue')\n"})


@pytest.mark.parametrize("path", sorted(S.M.BODY_MOVES))
@pytest.mark.parametrize("selected", [False, True])
def test_each_mixed_facade_rejects_changed_selected_or_unselected_ast(path, selected):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8-sig"))
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and (n.name in S.M.BODY_MOVES[path]["functions"]) == selected]
    if functions:
        functions[0].body = ast.parse("raise RuntimeError('rogue')").body
    else:
        # Annotation facade has only moved functions; its unmoved module
        # statements still form part of the complete reconstruction contract.
        tree.body.append(ast.parse("BROKER_CAPABILITY = True").body[0])
    with pytest.raises(AssertionError, match="facade/unmoved AST"):
        S.source(path, {path: ast.unparse(tree)})
