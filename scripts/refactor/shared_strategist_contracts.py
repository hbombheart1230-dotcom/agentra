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


# The exact historical 1e1e78a9..c5fe8a9a diff includes eleven
# independently parallel Reporter/Monitor and CI/evidence changes. This
# closed inventory is relevant only to that pinned historical Git diff.
# It is NEVER a general S5 path allowlist for caller-supplied changes.
HISTORICAL_PARALLEL_STAGE_PATHS = frozenset({
    ".github/workflows/p15-shared-candidate.yml",
    "docs/daily_patch/2026-10-18_codex_p15_p2_ci_portability.md",
    "docs/dev-team/integration/CODEX_P2_CI_CHECKPOINT_20261018.md",
    "docs/dev-team/integration/CODEX_P2_LOCAL_EXECUTION_20261018.json",
    "scripts/refactor/monitor_evidence_ast.py",
    "scripts/refactor/work_monitor_retained_boundary.py",
    "tests/fixtures/uef9_synthetic/.gitattributes",
    "tests/test_monitor_evidence_ast.py",
    "tests/test_work_monitor_retained_boundary.py",
    "tests/test_work_monitor_scope_accounting.py",
    "tests/test_work_reporter_seed_migration.py",
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
    read = lambda p: overrides[p] if p in overrides else historical_source(p)
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
        verify_next_scope()
        stage_paths = set(subprocess.check_output(
            ["git", "diff", "--name-only", INTEGRATION_BASE, HISTORICAL_STAGE],
            cwd=ROOT, text=True,
        ).splitlines())
        # git diff compares the two exact trees; a GitHub compare view of
        # divergent refs may instead report merge-base..head changes.
        # The frozen parallel inventory is an upper bound, not eleven mandatory
        # entries in the direct two-tree diff.
        historical_extra = stage_paths - (S5_PATHS | SHARED_PATHS | INTEGRATION_DOC_PATHS)
        require(historical_extra <= HISTORICAL_PARALLEL_STAGE_PATHS,
                "unapproved path in pinned historical S5 stage: " +
                repr(historical_extra - HISTORICAL_PARALLEL_STAGE_PATHS))
        # Only partition the immutable *historical* diff; never give caller
        # changes or untracked paths permission to modify these eleven files.
        changed = stage_paths - HISTORICAL_PARALLEL_STAGE_PATHS
    if untracked is None:
        untracked = []  # current untracked paths are checked by verify_next_scope above
    paths = set(changed) | set(untracked)
    require(paths <= S5_PATHS | SHARED_PATHS | INTEGRATION_DOC_PATHS, "out-of-scope S5/shared path: " + repr(paths - S5_PATHS - SHARED_PATHS - INTEGRATION_DOC_PATHS))
    return paths


# Integration completion: historic S5/T3/T4-D shapes remain frozen at the last
# CI-accepted stage; new-stage admission is exact, not a prefix allowlist.
HISTORICAL_STAGE = "c5fe8a9a59788cd7cf1eb1d72f9aa8b22a40f7ca"
NEXT_BASE = "90ec23837c2b42d37e645ea3026e98247695d89f"
# Last independently audited source integration. Later document/CI governance is not an S5 source-scope expansion.
ACCEPTED_SOURCE_INTEGRATION = "a50d6e4780ddccd810fb0708e756e1bf63d8ede0"
PARSING_PIN = "6849bed4af358c214f63011a0d58ef760ca79fa0"
UI_PIN = "613a945d2b27e735d4019cdc85b4660f2c891d8f"
PARSING = "libs/runtime/strategist/llm/response_contract_parsing.py"
UI_CORE = "apps/operator_ui/data_access_core.py"
UI_INPUT = "apps/operator_ui/data_access_brief_input_projection.py"
UI_SECTIONS = "apps/operator_ui/data_access_brief_sections_projection.py"
NEXT_RUNTIME = {NODE: PARSING_PIN, PARSING: PARSING_PIN,
                UI_CORE: UI_PIN, UI_INPUT: UI_PIN, UI_SECTIONS: UI_PIN}
NEXT_MOVED = {
    NODE: {name: (PARSING, name + "_r3_impl", name + "_r3_impl") for name in
           ("_extract_contract_from_prose", "_extract_json_object", "_classify_llm_parse_failure")},
    UI_CORE: {
        "_build_operator_brief_input": (UI_INPUT, "build_operator_brief_input", "_build_operator_brief_input_projection"),
        "_build_operator_brief_sections": (UI_SECTIONS, "build_operator_brief_sections", "_build_operator_brief_sections_projection"),
    },
}
NEXT_PATHS = frozenset(NEXT_RUNTIME) | {
    "tests/test_p15_strategist_contract_parsing_move.py", "tests/test_operator_ui.py",
    "scripts/refactor/shared_strategist_contracts.py", "scripts/refactor/shared_role_contracts.py",
    "scripts/refactor/shared_candidate_tests.py", "tests/test_shared_strategist_contracts.py",
    "tests/test_p15_strategist_s5_helper_moves.py", "tests/test_p159_current_owner_contract_gates.py",
    "tests/test_p165_t4d_extraction_gates.py", "tests/test_p164_t4c_extraction_gates.py",
    "tests/test_p15_integration_completion.py", "docs/refactor/work_orders/CURRENT.md",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.json",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.md",
}


def historical_source(path):
    """Only approved changed blobs project to the CI-accepted historical view.

    All other files remain current. A changed wrapper/import/owner cannot be
    hidden by reading the old stage: its actual blob must match the audited pin.
    """
    current = (ROOT / path).read_text(encoding="utf-8-sig")
    if path in NEXT_RUNTIME:
        require(current.replace("\r\n", "\n") == git_source(NEXT_RUNTIME[path], path),
                "new-stage source differs from audited pin: " + path)
        require(path != PARSING, "new Owner has no historical source")
        return git_source(HISTORICAL_STAGE, path)
    return current


class _RestoreBriefGlobals(Unqualify):
    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == "facade":
            return ast.copy_location(ast.Name(id=node.attr, ctx=node.ctx), node)
        return self.generic_visit(node)

    def visit_Name(self, node):
        if node.id == "facade" and isinstance(node.ctx, ast.Load):
            return ast.copy_location(ast.parse("_r3_sys.modules[__name__]", mode="eval").body, node)
        return node


def verify_next_stage(overrides=None):
    """Exact audited source + five body/ABI/import restoration proofs, -O safe."""
    overrides = overrides or {}
    sources = {p: overrides.get(p, (ROOT / p).read_text(encoding="utf-8-sig")) for p in NEXT_RUNTIME}
    for path, pin in NEXT_RUNTIME.items():
        require(sources[path].replace("\r\n", "\n") == git_source(pin, path),
                "new-stage source differs from audited pin: " + path)
    for path, moved in NEXT_MOVED.items():
        base_tree = ast.parse(git_source(NEXT_BASE, path))
        tree = ast.parse(sources[path])
        base, current = functions(base_tree), functions(tree)
        require(set(base) == set(current), "new-stage definition inventory")
        for name, (owner, impl_name, alias) in moved.items():
            expected = copy.deepcopy(base[name])
            args = [ast.Name(id=a.arg, ctx=ast.Load()) for a in expected.args.posonlyargs + expected.args.args]
            expected.body = [ast.Return(value=ast.Call(func=ast.Name(id=alias, ctx=ast.Load()), args=args,
                keywords=[ast.keyword(arg="facade", value=ast.parse("_r3_sys.modules[__name__]", mode="eval").body)]))]
            require(dump(current[name]) == dump(expected), "new-stage wrapper/ABI: " + name)
            impl = copy.deepcopy(functions(ast.parse(sources[owner]))[impl_name])
            expected_impl = copy.deepcopy(base[name])
            expected_impl.name = impl_name
            expected_impl.args.kwonlyargs.append(ast.arg(arg="facade"))
            expected_impl.args.kw_defaults.append(None)
            restored = (_RestoreBriefGlobals() if path == UI_CORE else Unqualify()).visit(impl)
            require(dump(restored) == dump(expected_impl), "new-stage body/signature: " + name)
        # Permit exactly the reviewed import addition, preserving old import order.
        # The entire audited source pin above also protects owner module statements.
        for n in tree.body:
            if isinstance(n, ast.FunctionDef) and n.name in moved:
                index = tree.body.index(n)
                tree.body[index] = copy.deepcopy(base[n.name])
        tree.body = [n for n in tree.body if not (isinstance(n, ast.ImportFrom) and n.module == PARSING[:-3].replace("/", "."))]
        for n in tree.body:
            if isinstance(n, ast.ImportFrom) and path == UI_CORE:
                n.names = [a for a in n.names if (n.module, a.name, a.asname) not in {
                    (o[:-3].replace("/", "."), impl, alias) for o, impl, alias in moved.values()}]
        require(dump(tree) == dump(base_tree), "new-stage unmoved source/import changed: " + path)
    return frozenset(NEXT_RUNTIME)


# This is the frozen S5/new-stage *source* admission. Only the two
# traceable CI-contract proof files changed after a50d6e47; all other
# runtime, scripts, tests and fixtures must remain untouched. A later
# modification to this guard requires a new independent diff-only review.
POST_ACCEPTANCE_CODE_ROOTS = ("libs", "graphs", "apps", "scripts", "tests")
POST_ACCEPTANCE_PROOF_PIN = "cfac9b715dcf59aa04df926f5671d36934c1a1b4"
POST_ACCEPTANCE_PROOF_PATHS = frozenset({
    "scripts/refactor/shared_strategist_contracts.py",
    "tests/test_shared_strategist_contracts.py",
})


def verify_post_acceptance_source_scope(changed):
    paths = set(changed)
    require(paths <= POST_ACCEPTANCE_PROOF_PATHS,
            "post-accepted source/test drift (requires new independent source audit): " +
            repr(paths - POST_ACCEPTANCE_PROOF_PATHS))
    return frozenset(paths)


def verify_next_scope(changed=None, untracked=None):
    if changed is None:
        # Reject a rewritten/rebased unrelated HEAD rather than silently
        # selecting a different historical baseline or widening the allowlist.
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ACCEPTED_SOURCE_INTEGRATION, "HEAD"],
            cwd=ROOT, capture_output=True, check=False,
        )
        require(ancestor.returncode == 0, "independently audited source integration is not an ancestor")
        # Current committed source and any tracked worktree edits must remain
        # byte-identical to the independently accepted integration for *all*
        # actual runtime, scripts, tests and frozen fixture paths.
        committed = subprocess.check_output(
            ["git", "diff", "--name-only", ACCEPTED_SOURCE_INTEGRATION, "HEAD", "--", *POST_ACCEPTANCE_CODE_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        worktree = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD", "--", *POST_ACCEPTANCE_CODE_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        # Check the exact two proof files at the recorded prior SHA, not an
        # open prefix allowance for additional source or fixture edits.
        proof_ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", POST_ACCEPTANCE_PROOF_PIN, "HEAD"],
            cwd=ROOT, capture_output=True, check=False,
        )
        require(proof_ancestor.returncode == 0, "pinned CI proof repair not in current history")
        verify_post_acceptance_source_scope(committed)
        since_proof = subprocess.check_output(
            ["git", "diff", "--name-only", POST_ACCEPTANCE_PROOF_PIN, "HEAD",
             "--", *POST_ACCEPTANCE_CODE_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        # The cfac proof repair had two reviewed files, including its unit test.
        # Reject every other source or test edit, and pin the unit test to the
        # subsequent exact revision so future test weakening cannot slip through.
        require(set(since_proof) <= POST_ACCEPTANCE_PROOF_PATHS,
                "new post-proof source/test drift: " +
                repr(set(since_proof) - POST_ACCEPTANCE_PROOF_PATHS))
        test_pin = "05e91ea0e53f296f3507445706901f9b389ad9fd"
        require(subprocess.run(
            ["git", "merge-base", "--is-ancestor", test_pin, "HEAD"],
            cwd=ROOT, capture_output=True, check=False,
        ).returncode == 0, "reviewed scope unit test pin not ancestral")
        require(not subprocess.check_output(
            ["git", "diff", "--name-only", test_pin, "HEAD", "--",
             "tests/test_shared_strategist_contracts.py"],
            cwd=ROOT, text=True,
        ).strip(), "post-pin source scope unit test has been modified")
        require(not worktree, "unreviewed tracked worktree source/test drift: " + repr(set(worktree)))
        # Stage scope is measured at the audited a50d6e47 source admission
        # (19 exact paths), not across later D00/docs/workflow-only commits.
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", NEXT_BASE, ACCEPTED_SOURCE_INTEGRATION],
            cwd=ROOT, text=True,
        ).splitlines()
    if untracked is None:
        untracked = subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True,
        ).splitlines()
    paths = set(changed) | set(untracked)
    require(paths <= NEXT_PATHS, "out-of-scope integration completion path: " + repr(paths - NEXT_PATHS))
    return paths
