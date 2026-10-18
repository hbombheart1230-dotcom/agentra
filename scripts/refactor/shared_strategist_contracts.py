"""Exact S5 source admission; combined candidate still needs Claude review.

No runtime imports or source writes. Candidate blobs may be proved in memory;
Source admission follows the exact-SHA independent verdict linked below.
This does not promote the developer branch or waive any integration failure.
"""
import ast
import copy
from functools import lru_cache
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "d269c906ebadad75a0b833778ebc6a632a388e7c"
CANDIDATE_CODE = "c4960c5312945c8dac9b141df222f54ecc28beda"
INTEGRATION_BASE = "1e1e78a9061f9a56c3ce1410202ce5193c6af679"
# S5 implementation PASS only; shared/final integration approval is separate.
# https://github.com/hbombheart1230-dotcom/agentra/issues/14#issuecomment-6245517822
ADMITTED_CODE = "c4960c5312945c8dac9b141df222f54ecc28beda"
NODE = "graphs/nodes/strategist_node.py"
VALUE = "libs/runtime/strategist/context/value_helpers.py"
TEXT = "libs/runtime/strategist/llm/text_fragment_helpers.py"
MOVED = {"_clamp": VALUE, "_to_float": VALUE, "_to_int": VALUE,
         "_round_optional": VALUE, "_unit_score": VALUE, "_is_trueish": VALUE,
         "_strip_fenced_block": TEXT, "_parse_text_list_fragment": TEXT}
OWNERS = frozenset({VALUE, TEXT})
RUNTIME_PATHS = frozenset({NODE, *OWNERS})
S5_PATHS = RUNTIME_PATHS | {
    "scripts/refactor/p15_strategist_s5_runner.py", "tests/p15_strategist_s5_cases.py",
    "tests/test_p15_strategist_s5_helper_moves.py",
}
SHARED_PATHS = frozenset({
    "scripts/refactor/shared_strategist_contracts.py", "scripts/refactor/shared_role_contracts.py",
    "scripts/refactor/shared_candidate_tests.py", "tests/test_shared_strategist_contracts.py",
    "tests/test_p164_t4c_extraction_gates.py", "tests/test_p172_strategist_s1_057_migration.py",
    "tests/test_work_monitor_role_contracts.py",
    "docs/dev-team/integration/CODEX_S5_GATE_PREPARATION_20261018.md",
    "docs/dev-team/integration/S5_SCOPE_POST_AUDIT_20261018.patch",
    "docs/daily_patch/2026-10-18_s5_shared_gate_preparation.md",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.json",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.md",
    # Issue16: explicit test/environment repair; no runtime admission expansion.
    "tests/test_uef9_formal_authority.py", "tests/uef9_synthetic_reports.py",
    "tests/fixtures/uef9_synthetic/reports_inputs.json",
    "tests/fixtures/uef9_synthetic/.gitattributes",
    "docs/dev-team/integration/CODEX_UEF9_FIXTURE_CHECKPOINT_20261018.md",
    "docs/daily_patch/2026-10-18_uef9_synthetic_fixture.md",
})

# Root-wide architecture and standing governance are already present on the
# integrator's documented starting SHA. Exact paths only; no runtime/broker
# or UEF authority is admitted by these documentary paths.
INTEGRATION_DOC_PATHS = frozenset({
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "docs/ENGINEERING_DELIVERY_POLICY.md",
    "docs/refactor/architecture/P15_ALL_FILES_OWNERSHIP_CANDIDATES_20261018.csv",
    "docs/refactor/architecture/P15_ALL_LIBS_OWNERS_20261018.md",
    "docs/refactor/architecture/P15_BRANCH_RETIREMENT_20261018.md",
    "docs/refactor/architecture/P15_IMPORT_SPOTCHECK_20261018.md",
    "docs/refactor/architecture/P15_MIGRATION_LEDGER_20261018.md",
    "docs/refactor/architecture/P15_ROOT_TO_LEAF_REALITY_AND_CLEANUP_20261018.md",
    "docs/refactor/architecture/P15_TECHLEAD_MASTER_20261018.md",
    "docs/refactor/architecture/P15_TREE_ALL_PATHS_PINNED_20261018.txt",
    "docs/refactor/work_orders/CURRENT.md",
})


def require(value, message):
    if not value:
        raise AssertionError(message)


def dump(node):
    return ast.dump(node, include_attributes=False)


@lru_cache(maxsize=None)
def git_source(sha, path):
    return subprocess.check_output(["git", "show", sha + ":" + path], cwd=ROOT).decode("utf-8-sig").replace("\r\n", "\n")


def functions(tree):
    rows = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    require(len(rows) == len({n.name for n in rows}), "duplicate Strategist definition")
    return {n.name: n for n in rows}


class Unqualify(ast.NodeTransformer):
    def visit_Attribute(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Name) and node.value.id == "facade":
            return ast.copy_location(ast.Name(id=node.attr, ctx=node.ctx), node)
        return node


def candidate_sources():
    """Read historical blobs as data only; does not install/admit S5."""
    return {p: git_source(CANDIDATE_CODE, p) for p in RUNTIME_PATHS}


def restore_candidate(sources):
    """Validate all eight wrappers/owners, restore only those eight BASE defs."""
    require(set(sources) == RUNTIME_PATHS, "S5 exact three-path source set")
    base_tree = ast.parse(git_source(SOURCE, NODE))
    base = functions(base_tree)
    tree = ast.parse(sources[NODE])
    current = functions(tree)
    require(set(current) == set(base), "Strategist definition inventory changed")
    for owner in OWNERS:
        require(sources[owner].replace("\r\n", "\n") == git_source(CANDIDATE_CODE, owner),
                "S5 Owner differs from candidate pin: " + owner)
        owned = functions(ast.parse(sources[owner]))
        require(set(owned) == {n + "_r3_impl" for n, p in MOVED.items() if p == owner}, "S5 Owner exports")
        for name, path in MOVED.items():
            if path != owner:
                continue
            impl = Unqualify().visit(copy.deepcopy(owned[name + "_r3_impl"]))
            require([dump(n) for n in impl.body] == [dump(n) for n in base[name].body], "S5 original body: " + name)
    for name in MOVED:
        expected = copy.deepcopy(base[name])
        require(not expected.args.vararg and not expected.args.kwarg and not expected.args.kwonlyargs,
                "unexpected S5 signature: " + name)
        args = [ast.Name(id=a.arg, ctx=ast.Load()) for a in expected.args.posonlyargs + expected.args.args]
        expected.body = [ast.Return(value=ast.Call(func=ast.Name(id=name + "_r3_impl", ctx=ast.Load()), args=args,
                           keywords=[ast.keyword(arg="facade", value=ast.parse("_r3_sys.modules[__name__]", mode="eval").body)]))]
        require(dump(current[name]) == dump(expected), "nonexact S5 wrapper/ABI: " + name)
    modules = {p[:-3].replace("/", "."): p for p in OWNERS}
    used = set()
    restored = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module in modules:
            owner = modules[node.module]
            names = [n + "_r3_impl" for n, p in MOVED.items() if p == owner]
            require(node.module not in used and node.level == 0 and
                    [(a.name, a.asname) for a in node.names] == [(n, None) for n in names], "nonexact S5 import")
            used.add(node.module)
            continue
        restored.append(copy.deepcopy(base[node.name]) if isinstance(node, ast.FunctionDef) and node.name in MOVED else node)
    require(used == set(modules), "missing S5 import")
    tree.body = restored
    require(dump(tree) == dump(base_tree), "non-S5 node statement/body/import changed")
    return tree


def current_contract(overrides=None):
    """Existing tree or admitted exact S5 only; partial/unreviewed S5 fails."""
    overrides = overrides or {}
    read = lambda p: overrides[p] if p in overrides else (ROOT / p).read_text(encoding="utf-8-sig")
    present = {p for p in OWNERS if p in overrides or (ROOT / p).exists()}
    source = read(NODE)
    if not present:
        require(source.replace("\r\n", "\n") == git_source(SOURCE, NODE), "pre-S5 node changed")
        tree = ast.parse(source)
        return {"tree": tree, "restored": copy.deepcopy(tree), "runtime_paths": frozenset()}
    require(ADMITTED_CODE == CANDIDATE_CODE, "S5 independent auditor PASS/admission pending")
    require(present == OWNERS, "partial S5 Owner installation")
    sources = {p: read(p) for p in RUNTIME_PATHS}
    restored = restore_candidate(sources)
    require(source.replace("\r\n", "\n") == git_source(CANDIDATE_CODE, NODE), "S5 node differs from exact pin")
    return {"tree": ast.parse(source), "restored": restored, "runtime_paths": RUNTIME_PATHS}


def import_pairs():
    return {(p[:-3].replace("/", "."), n + "_r3_impl") for n, p in MOVED.items()}


def verify_integration_scope(changed=None, untracked=None):
    """Exact integrated-lane scope; no prefix wildcard or caller baseline override."""
    if changed is None:
        changed = subprocess.check_output(["git", "diff", "--name-only", INTEGRATION_BASE], cwd=ROOT, text=True).splitlines()
    if untracked is None:
        untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True).splitlines()
    paths = set(changed) | set(untracked)
    require(paths <= S5_PATHS | SHARED_PATHS | INTEGRATION_DOC_PATHS, "out-of-scope S5/shared path: " + repr(paths - S5_PATHS - SHARED_PATHS - INTEGRATION_DOC_PATHS))
    return paths
