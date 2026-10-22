"""Exact S5 source admission; combined candidate still needs Claude review.

No runtime imports or source writes. Candidate blobs may be proved in memory;
Source admission follows the exact-SHA independent verdict linked below.
This does not promote the developer branch or waive any integration failure.
"""
import ast
import copy
import hashlib
import json
import re
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
    if path == UI_CORE:
        # B is a separate admission, never a replacement for the five-function
        # historical proof. Validate all actual B blobs before projecting it.
        verify_b_sources()
        current = git_source(UI_PIN, path)
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


def _verify_five_function_stage(overrides=None):
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


# Frozen S5 source admission: only two earlier CI proof files and the three
# independently stage-pinned Scanner *test* files below can differ from a50d6e47.
# Scanner changes are locked to exact Git blob SHA-1, NOT a wildcard test allowlist.
# All runtime sources, other tests, fixtures, broker/approval/UEF remain frozen.
POST_ACCEPTANCE_CODE_ROOTS = ("libs", "graphs", "apps", "scripts", "tests")
POST_ACCEPTANCE_PROOF_PIN = "cfac9b715dcf59aa04df926f5671d36934c1a1b4"
POST_ACCEPTANCE_PROOF_PATHS = frozenset({
    "scripts/refactor/shared_strategist_contracts.py",
    "tests/test_shared_strategist_contracts.py",
})
HISTORICAL_SCANNER_SCOPE_TEST_BLOBS = {
    "tests/test_p167_v2053_scanner_context_migration.py": "4fafef4ae4ec1fcf960244beef12ec66e8e9cbac",
    "tests/test_p171_v3055_scanner_projection_migration.py": "2c948370f2ac792dc93d7d4e96b4444b62e3d5b3",
    "tests/test_p172_v4056_scanner_policy_migration.py": "f436fbcf147fa834ab0adb316ba7b5d0520e160b",
}
POST_ACCEPTANCE_ALLOWED_SOURCE_PATHS = (
    POST_ACCEPTANCE_PROOF_PATHS | frozenset(HISTORICAL_SCANNER_SCOPE_TEST_BLOBS)
)


def verify_post_acceptance_source_scope(changed):
    paths = set(changed)
    require(paths <= POST_ACCEPTANCE_ALLOWED_SOURCE_PATHS,
            "post-accepted source/test drift (requires new independent source audit): " +
            repr(paths - POST_ACCEPTANCE_ALLOWED_SOURCE_PATHS))
    return frozenset(paths)


def verify_historical_next_scope(changed=None, untracked=None):
    """Original post-acceptance proof on the immutable pre-B Git tree.

    Current worktree drift is a separate V2 check; it is never described as
    passing this historical stage. Explicit caller path probes stay legacy-only.
    """
    if changed is None:
        # Reject a rewritten/rebased unrelated HEAD rather than silently
        # selecting a different historical baseline or widening the allowlist.
        ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ACCEPTED_SOURCE_INTEGRATION, B_PRE_SOURCE],
            cwd=ROOT, capture_output=True, check=False,
        )
        require(ancestor.returncode == 0, "independently audited source integration is not an ancestor")
        # Historical committed source/test inventory from accepted integration
        # through the final pre-B tree, including the exact proof/test repairs.
        committed = subprocess.check_output(
            ["git", "diff", "--name-only", ACCEPTED_SOURCE_INTEGRATION, B_PRE_SOURCE, "--", *POST_ACCEPTANCE_CODE_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        # Check the exact two proof files at the recorded prior SHA, not an
        # open prefix allowance for additional source or fixture edits.
        proof_ancestor = subprocess.run(
            ["git", "merge-base", "--is-ancestor", POST_ACCEPTANCE_PROOF_PIN, B_PRE_SOURCE],
            cwd=ROOT, capture_output=True, check=False,
        )
        require(proof_ancestor.returncode == 0, "pinned CI proof repair not in current history")
        verify_post_acceptance_source_scope(committed)
        since_proof = subprocess.check_output(
            ["git", "diff", "--name-only", POST_ACCEPTANCE_PROOF_PIN, B_PRE_SOURCE,
             "--", *POST_ACCEPTANCE_CODE_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        # The cfac proof repair had two reviewed files, including its unit test.
        # Reject every other source or test edit, and pin the unit test to the
        # subsequent exact revision so future test weakening cannot slip through.
        require(set(since_proof) <= POST_ACCEPTANCE_ALLOWED_SOURCE_PATHS,
                "new post-proof source/test drift: " +
                repr(set(since_proof) - POST_ACCEPTANCE_ALLOWED_SOURCE_PATHS))
        # The three Scanner migration *test* repairs are fixed Git objects.
        # A future modification to even one test must fail before S5 admission.
        for test_path, blob_sha in HISTORICAL_SCANNER_SCOPE_TEST_BLOBS.items():
            head_blob = subprocess.check_output(
                ["git", "rev-parse", B_PRE_SOURCE + ":" + test_path],
                cwd=ROOT, text=True,
            ).strip()
            require(head_blob == blob_sha,
                    "unreviewed historical Scanner scope-test bytes: " + test_path)
        test_pin = "05e91ea0e53f296f3507445706901f9b389ad9fd"
        require(subprocess.run(
            ["git", "merge-base", "--is-ancestor", test_pin, B_PRE_SOURCE],
            cwd=ROOT, capture_output=True, check=False,
        ).returncode == 0, "reviewed scope unit test pin not ancestral")
        require(not subprocess.check_output(
            ["git", "diff", "--name-only", test_pin, B_PRE_SOURCE, "--",
             "tests/test_shared_strategist_contracts.py"],
            cwd=ROOT, text=True,
        ).strip(), "post-pin source scope unit test has been modified")
        # Stage scope is measured at the audited a50d6e47 source admission
        # (19 exact paths), not across later D00/docs/workflow-only commits.
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", NEXT_BASE, ACCEPTED_SOURCE_INTEGRATION],
            cwd=ROOT, text=True,
        ).splitlines()
    if untracked is None:
        untracked = []  # Immutable historical tree; current disk checked by V2.
    paths = set(changed) | set(untracked)
    require(paths <= NEXT_PATHS, "out-of-scope integration completion path: " + repr(paths - NEXT_PATHS))
    return paths


# P1.5-B V2 is intentionally separate from NEXT_RUNTIME/NEXT_PATHS. Their
# original shapes, five functions and original forbidden-path tests stay fixed.
B_PRE_SOURCE = "4b0c3e0b5f8f24fa3c10d9082b85fab63f15c4c3"
B_SOURCE = "54bebe5ece0ac34c4f45df55c44889c9ce323e95"
B_OWNERS = frozenset({
    "apps/operator_ui/data_access_overview_projection.py",
    "apps/operator_ui/data_access_trade_index_projection.py",
    "apps/operator_ui/data_access_run_detail_projection.py",
})
B_RUNTIME = B_OWNERS | {UI_CORE}
B_TESTS = frozenset({
    "tests/test_p15_overview_live_projection.py",
    "tests/test_p15_operator_trade_index_projection.py",
    "tests/test_p15_operator_run_detail_projection.py",
})
B_SOURCE_PATHS = B_RUNTIME | B_TESTS
B_CONTRACT_PATHS = frozenset({
    "scripts/refactor/shared_strategist_contracts.py",
    "scripts/refactor/shared_role_contracts.py",
    "tests/test_shared_strategist_contracts.py",
    "tests/test_p15_integration_completion.py",
    "tests/test_shared_role_contracts.py",
    "tests/test_p15_b_versioned_contract.py",
})
B_DEFINITIONS = frozenset({"load_overview", "_trade_report_index", "load_run_detail"})


def verify_b_sources(overrides=None):
    """Exact reviewed B blobs, restored pre-B imports/exports/ABI and AST.

    No source is executed. Existing differential runtime suites prove effect
    order; this admission cannot silently accept any change to those blobs.
    """
    overrides = overrides or {}
    sources = {}
    for path in sorted(B_RUNTIME):
        source = overrides[path] if path in overrides else (ROOT / path).read_text(encoding="utf-8-sig")
        require(source.replace("\r\n", "\n") == git_source(B_SOURCE, path),
                "new-stage source differs from reviewed B pin: " + path)
        sources[path] = source
    base = ast.parse(git_source(B_PRE_SOURCE, UI_CORE))
    tree = ast.parse(sources[UI_CORE])
    base_defs, current_defs = functions(base), functions(tree)
    require(set(base_defs) == set(current_defs), "B-stage definition inventory")
    for name in B_DEFINITIONS:
        before, after = copy.deepcopy(base_defs[name]), copy.deepcopy(current_defs[name])
        before.body, after.body = [], []
        require(dump(before) == dump(after), "B-stage ABI: " + name)
    owner_modules = {p[:-3].replace("/", ".") for p in B_OWNERS}
    imports = [n for n in tree.body if isinstance(n, ast.ImportFrom) and n.module in owner_modules]
    # The source pin above protects exact aliases, order and call arguments.
    require({n.module for n in imports} == owner_modules and len(imports) == 3,
            "B-stage exact Owner imports")
    tree.body = [copy.deepcopy(base_defs[n.name])
                 if isinstance(n, ast.FunctionDef) and n.name in B_DEFINITIONS else n
                 for n in tree.body if n not in imports]
    require(dump(tree) == dump(base), "B-stage unmoved source/import changed")
    require(git_source(B_PRE_SOURCE, UI_CORE) == git_source(UI_PIN, UI_CORE),
            "B pre-source does not match original five-function stage")
    return frozenset(sources)


def verify_next_stage(overrides=None):
    """Current B admission followed by the unchanged five-function proof."""
    verify_b_sources(overrides)
    projected = dict(overrides or {})
    projected[UI_CORE] = git_source(UI_PIN, UI_CORE)
    return _verify_five_function_stage(projected)


def verify_legacy_b_scope(overrides=None):
    """Closed current source/test delta; no wildcard or editable baseline."""
    overrides = overrides or {}
    require(subprocess.run(["git", "merge-base", "--is-ancestor", B_PRE_SOURCE, "HEAD"],
                           cwd=ROOT, capture_output=True).returncode == 0,
            "B-stage baseline not ancestral")
    pinned_delta = set(subprocess.check_output(
        ["git", "diff", "--name-only", B_PRE_SOURCE, B_SOURCE, "--", *POST_ACCEPTANCE_CODE_ROOTS],
        cwd=ROOT, text=True).splitlines())
    require(pinned_delta == B_SOURCE_PATHS, "B-stage pinned seven-path inventory")
    changed = set(subprocess.check_output(
        ["git", "diff", "--name-only", B_PRE_SOURCE, "--", *POST_ACCEPTANCE_CODE_ROOTS],
        cwd=ROOT, text=True).splitlines())
    changed |= set(subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard", "--", *POST_ACCEPTANCE_CODE_ROOTS],
        cwd=ROOT, text=True).splitlines())
    changed |= set(overrides)
    require(changed <= B_SOURCE_PATHS | B_CONTRACT_PATHS,
            "B-stage unapproved source/test/fixture path: " + repr(changed - B_SOURCE_PATHS - B_CONTRACT_PATHS))
    for path in sorted(B_SOURCE_PATHS):
        current = overrides[path] if path in overrides else (ROOT / path).read_text(encoding="utf-8-sig")
        require(current.replace("\r\n", "\n") == git_source(B_SOURCE, path),
                "B-stage source/test differs from reviewed pin: " + path)
    return frozenset(changed)


def verify_next_scope(changed=None, untracked=None):
    """Legacy explicit-scope API plus historical and strict current V2 checks."""
    # An explicit legacy probe must not suppress validation of the actual V2
    # worktree (including untracked capabilities or modified frozen fixtures).
    verify_b_scope()
    return verify_historical_next_scope(changed, untracked)


# Separately authorized Commander V1. No historical S5/B set or pin is extended.
COMMANDER_V1 = "P15_COMMANDER_PURE_V1"
COMMANDER_V1_BASE = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
COMMANDER_V1_SOURCE = "e4a597886f21f1655de170f54e863c2e74910d29"
COMMANDER_V1_PATHS = frozenset({
    "libs/agents/commander/__init__.py",
    "libs/agents/commander/projections/__init__.py",
    "libs/agents/commander/projections/cache_refresh_read_model.py",
    "libs/agents/commander/projections/decision_context_read_model.py",
    "libs/runtime/commander/decision_context_projection.py",
    "libs/runtime/commander/decision_overlay_projection.py",
    "libs/runtime/commander/decision_rules_projection.py",
    "libs/runtime/commander/strategist_fingerprint.py",
    "libs/runtime/commander/strategist_refresh_decision.py",
    "tests/test_p15_b_commander_monitor_boundaries.py",
    "tests/test_p15_b_commander_monitor_pure_parity.py",
})
COMMANDER_V1_RUNTIME = frozenset(p for p in COMMANDER_V1_PATHS if p.startswith("libs/"))
COMMANDER_V1_CONTRACT_FILES = frozenset({
    "scripts/refactor/shared_strategist_contracts.py", "scripts/refactor/shared_role_contracts.py",
    "tests/test_shared_strategist_contracts.py", "tests/test_shared_role_contracts.py",
    "tests/test_p15_b_versioned_contract.py", "tests/test_p15_integration_completion.py",
    "tests/test_p15_commander_pure_v1_admission.py",
})
COMMANDER_V1_CONTRACT_DELTA = frozenset({
    "scripts/refactor/shared_strategist_contracts.py", "scripts/refactor/shared_role_contracts.py",
    "tests/test_shared_strategist_contracts.py", "tests/test_p15_commander_pure_v1_admission.py",
})
COMMANDER_V1_NOTES = frozenset({
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.json",
    "docs/trading_agent_patch_notes_detailed_update/patch_notes.md",
})
# Exact proof bytes, including the unchanged old tests. Only the literal values
# of this data-only manifest are canonicalized for its own non-circular digest.
# This is drift detection, not a claim that executing tampered checkers is safe.
COMMANDER_V1_PROOF_HASHES = {'scripts/refactor/shared_role_contracts.py': 'a163c61f095a50539b13ac6daceba29a24967d678e708c3c591b3600fa4704d5', 'scripts/refactor/shared_strategist_contracts.py': '2763eec7d6ec3a5d508c30e9b19881458d1c15f96517354d9f7933481ea3a7ad', 'tests/test_p15_b_versioned_contract.py': '4869bbec3813ad2250c08c4fe8f2c71ea86416c507817d89c94d27daab507f3a', 'tests/test_p15_commander_pure_v1_admission.py': '1c760435407407cdc76055a06cff710f51b8496d4446bfe1ad5f2013e5cbc288', 'tests/test_p15_integration_completion.py': '2764e489b911f28354527c1ec00bfb867ab6f08d8d948d7531d5de42ea663293', 'tests/test_shared_role_contracts.py': '6a5c3789536f6d9c2d775e68435bc100a3087b9b35330da8dc13f6d697ec805e', 'tests/test_shared_strategist_contracts.py': '9e069059344da7c36d779d2581df17b6d7332fba0997b4467b7866c755c38f90'}


@lru_cache(maxsize=None)
def _commander_pinned_delta(start, end):
    # Cache immutable object pairs only. Current disk/index/inventory is NEVER cached.
    require(all(re.fullmatch(r"[0-9a-f]{40}", value) for value in (start, end)),
            "Commander V1 immutable diff object IDs")
    return frozenset(subprocess.check_output(
        ["git", "diff", "--name-only", start, end], cwd=ROOT, text=True).splitlines())


def _commander_delta(start, end=None):
    if end is not None:
        return set(_commander_pinned_delta(start, end))
    return set(subprocess.check_output(
        ["git", "diff", "--name-only", start], cwd=ROOT, text=True).splitlines())


def _commander_read(path, overrides):
    if path in overrides:
        text = overrides[path]
        require(isinstance(text, str), "B-stage Commander V1 missing source: " + path)
        return text.replace("\r\n", "\n")
    require((ROOT / path).is_file(), "B-stage Commander V1 missing source: " + path)
    return (ROOT / path).read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def commander_v1_selected(overrides=None):
    # A deleted new file must not silently fall back to old-stage admission.
    return ((ROOT / "tests/test_p15_commander_pure_v1_admission.py").exists()
            or (ROOT / "libs/agents/commander").exists()
            or bool(set(overrides or {}) & COMMANDER_V1_PATHS)
            or subprocess.run(["git", "merge-base", "--is-ancestor", COMMANDER_V1_SOURCE, "HEAD"],
                              cwd=ROOT, capture_output=True).returncode == 0)


@lru_cache(maxsize=None)
def _commander_historical_proof(base, pre, source, paths, contracts):
    # Inputs are immutable Git object IDs and frozen inventories. Mutant sources
    # never enter this cache; they take the explicit-overrides branch below.
    require((base, pre, source, paths, contracts) ==
            (COMMANDER_V1_BASE, B_PRE_SOURCE, B_SOURCE, B_SOURCE_PATHS, B_CONTRACT_PATHS),
            "Commander V1 historical proof inputs")
    return verify_historical_b_scope({})


def verify_historical_b_scope(overrides=None):
    """Authentic old B predicate on its immutable integration tree, not V1 disk."""
    if overrides is None:
        return _commander_historical_proof(COMMANDER_V1_BASE, B_PRE_SOURCE, B_SOURCE,
                                           B_SOURCE_PATHS, B_CONTRACT_PATHS)
    overrides = overrides or {}
    pinned = _commander_delta(B_PRE_SOURCE, B_SOURCE)
    pinned = {p for p in pinned if p.startswith(tuple(r + "/" for r in POST_ACCEPTANCE_CODE_ROOTS))}
    require(pinned == B_SOURCE_PATHS, "B-stage pinned seven-path inventory")
    changed = _commander_delta(B_PRE_SOURCE, COMMANDER_V1_BASE)
    changed = {p for p in changed if p.startswith(tuple(r + "/" for r in POST_ACCEPTANCE_CODE_ROOTS))} | set(overrides)
    require(changed <= B_SOURCE_PATHS | B_CONTRACT_PATHS,
            "historical B-stage unapproved path: " + repr(changed - B_SOURCE_PATHS - B_CONTRACT_PATHS))
    for path in sorted(B_SOURCE_PATHS):
        current = overrides.get(path, git_source(COMMANDER_V1_BASE, path))
        require(isinstance(current, str) and current.replace("\r\n", "\n") == git_source(B_SOURCE, path),
                "historical B-stage source differs: " + path)
    verify_b_sources({p: git_source(COMMANDER_V1_BASE, p) for p in B_RUNTIME})
    return frozenset(changed)


def commander_proof_digest(path, text):
    if path == "scripts/refactor/shared_strategist_contracts.py":
        rows = [n for n in ast.parse(text).body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "COMMANDER_V1_PROOF_HASHES" for t in n.targets)]
        require(len(rows) == 1, "Commander V1 proof manifest definition")
        manifest = ast.literal_eval(rows[0].value)
        require(isinstance(manifest, dict), "Commander V1 literal proof manifest")
        require(manifest == COMMANDER_V1_PROOF_HASHES, "B-stage Commander V1 checker/test drift: " + path)
        require(rows[0].lineno == rows[0].end_lineno, "Commander V1 manifest layout")
        lines = text.splitlines(keepends=True)
        # Canonicalize only the literal value, never a same-line statement or
        # comment. AST columns are UTF-8 byte offsets, including Unicode probes.
        value = rows[0].value
        require(value.lineno == value.end_lineno, "Commander V1 manifest value layout")
        line = lines[value.lineno - 1].encode("utf-8")
        lines[value.lineno - 1] = (line[:value.col_offset] + b"<exact proof values>" +
                                   line[value.end_col_offset:]).decode("utf-8")
        text = "".join(lines)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_commander_pure_v1(overrides=None, *, inventory=None):
    """Exact new-stage sources, proof bytes and complete repo delta; no prefix grant."""
    overrides = overrides or {}
    require(COMMANDER_V1 == "P15_COMMANDER_PURE_V1" and
            COMMANDER_V1_BASE == "d7ab82940deaa05810b28ef78fc0be88e201f9b6" and
            COMMANDER_V1_SOURCE == "e4a597886f21f1655de170f54e863c2e74910d29", "Commander V1 immutable pins")
    pinned = _commander_delta(COMMANDER_V1_BASE, COMMANDER_V1_SOURCE)
    require(pinned == COMMANDER_V1_PATHS | COMMANDER_V1_NOTES, "Commander V1 exact eleven-path pin")
    expected = COMMANDER_V1_PATHS | COMMANDER_V1_CONTRACT_DELTA | COMMANDER_V1_NOTES
    changed = _commander_delta(COMMANDER_V1_BASE)
    changed |= set(subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True).splitlines())
    changed |= set(overrides)
    require(changed == expected, "B-stage Commander V1 unexpected/missing inventory: " + repr(changed ^ expected))
    if inventory is not None:
        require(set(inventory) == expected, "B-stage Commander V1 unexpected/missing inventory: " + repr(set(inventory) ^ expected))
    package = ROOT / "libs/agents/commander"
    disk = {p.relative_to(ROOT).as_posix() for p in package.rglob("*.py")}
    allowed = {p for p in COMMANDER_V1_PATHS if p.startswith("libs/agents/commander/")}
    require(disk == allowed, "B-stage Commander V1 unexpected/missing package file: " + repr(disk ^ allowed))
    for path in sorted(COMMANDER_V1_PATHS):
        require(_commander_read(path, overrides) == git_source(COMMANDER_V1_SOURCE, path),
                "B-stage Commander V1 source/ABI/body differs from pin: " + path)
    require(set(COMMANDER_V1_PROOF_HASHES) == COMMANDER_V1_CONTRACT_FILES,
            "Commander V1 exact proof inventory")
    for path in sorted(COMMANDER_V1_CONTRACT_FILES):
        require(commander_proof_digest(path, _commander_read(path, overrides)) == COMMANDER_V1_PROOF_HASHES[path],
                "B-stage Commander V1 checker/test drift: " + path)
    test_text = _commander_read("tests/test_p15_commander_pure_v1_admission.py", overrides)
    anchors = [n for n in ast.parse(test_text).body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "EXPECTED_STAGE_CHECKER_SHA256" for t in n.targets)]
    require(len(anchors) == 1 and ast.literal_eval(anchors[0].value) == COMMANDER_V1_PROOF_HASHES[
        "scripts/refactor/shared_strategist_contracts.py"], "Commander V1 checker anchor")
    note_path = "docs/trading_agent_patch_notes_detailed_update/patch_notes.json"
    old = json.loads(git_source(COMMANDER_V1_SOURCE, note_path))
    current = json.loads(_commander_read(note_path, overrides))
    require(current["entries"][:-1] == old["entries"] and len(current["entries"]) == len(old["entries"]) + 1,
            "Commander V1 historical patch notes changed")
    require(current["entry_count"] == len(current["entries"]) == len({r["version"] for r in current["entries"]}),
            "Commander V1 patchnote count/version")
    require(current["entries"][-1]["version"] == COMMANDER_V1 and
            current["entries"][-1]["title"] not in {r["title"] for r in old["entries"]}, "Commander V1 note version/title")
    md_path = "docs/trading_agent_patch_notes_detailed_update/patch_notes.md"
    md = _commander_read(md_path, overrides)
    require(md.startswith(git_source(COMMANDER_V1_SOURCE, md_path)) and COMMANDER_V1 in md,
            "Commander V1 historical Markdown changed")
    verify_historical_b_scope()
    return {"version": COMMANDER_V1, "runtime_paths": COMMANDER_V1_RUNTIME,
            "changed_paths": frozenset(changed - COMMANDER_V1_NOTES)}


def verify_b_scope(overrides=None):
    """Version dispatch; the historical predicate and its closed sets stay intact."""
    if commander_v1_selected(overrides):
        return verify_commander_pure_v1(overrides)["changed_paths"]
    return verify_legacy_b_scope(overrides)


# Issue20 6330021757: one B-only composed stage, no historical pin changes.
B_COMPOSED_BASE = "d7ab82940deaa05810b28ef78fc0be88e201f9b6"
B_COMPOSED_COMMANDER = "e328d7801763a65e6c2c50c90edd693ff685ef95"
B_COMPOSED_BRIEF = "fedef7f7b72ac396c60c7a8ac1d9432e1dab782c"
B_COMPOSED_PATHS = frozenset({
    'apps/operator_ui/data_access_brief_evidence_readout_p15.py',
    'apps/operator_ui/data_access_brief_input_projection.py',
    'apps/operator_ui/data_access_brief_sections_projection.py',
    'apps/operator_ui/data_access_brief_source_truth_p15.py',
    'docs/trading_agent_patch_notes_detailed_update/patch_notes.json',
    'docs/trading_agent_patch_notes_detailed_update/patch_notes.md',
    'libs/agents/commander/__init__.py',
    'libs/agents/commander/projections/__init__.py',
    'libs/agents/commander/projections/cache_refresh_read_model.py',
    'libs/agents/commander/projections/decision_context_read_model.py',
    'libs/runtime/commander/decision_context_projection.py',
    'libs/runtime/commander/decision_overlay_projection.py',
    'libs/runtime/commander/decision_rules_projection.py',
    'libs/runtime/commander/strategist_fingerprint.py',
    'libs/runtime/commander/strategist_refresh_decision.py',
    'scripts/refactor/shared_role_contracts.py',
    'scripts/refactor/shared_strategist_contracts.py',
    'tests/test_p15_b_commander_monitor_boundaries.py',
    'tests/test_p15_b_commander_monitor_pure_parity.py',
    'tests/test_p15_b_operator_brief_boundaries.py',
    'tests/test_p15_b_operator_brief_pure_parity.py',
    'tests/test_p15_commander_pure_v1_admission.py',
    'tests/test_shared_strategist_contracts.py',
})
B_COMPOSED_BRIEF_RUNTIME = frozenset({
    UI_INPUT, UI_SECTIONS,
    "apps/operator_ui/data_access_brief_source_truth_p15.py",
    "apps/operator_ui/data_access_brief_evidence_readout_p15.py",
})
B_COMPOSED_CHECKS = frozenset({
    "scripts/refactor/shared_strategist_contracts.py",
    "scripts/refactor/shared_role_contracts.py",
    "tests/test_p15_integration_completion.py",
})


def b_composed_selected():
    # Deletion must not fall back to an earlier stage after this source commit.
    return ((ROOT / "apps/operator_ui/data_access_brief_source_truth_p15.py").exists()
            or subprocess.run(["git", "merge-base", "--is-ancestor", B_COMPOSED_BRIEF, "HEAD"],
                              cwd=ROOT, capture_output=True).returncode == 0)


def verify_b_composed(overrides=None, *, inventory=None):
    """Exact reviewed 23-file B input plus one integration test; no prefix grant.

    Current checker bytes are tied to the tested/reviewed HEAD, not to another
    self-referential hash manifest. Original standalone predicates below remain
    unchanged and are exercised on their pinned historical filesystem trees.
    """
    overrides = overrides or {}
    require((B_COMPOSED_BASE, B_COMPOSED_COMMANDER, B_COMPOSED_BRIEF) ==
            ("d7ab82940deaa05810b28ef78fc0be88e201f9b6",
             "e328d7801763a65e6c2c50c90edd693ff685ef95",
             "fedef7f7b72ac396c60c7a8ac1d9432e1dab782c"), "B composed immutable pins")
    require(_commander_delta(B_COMPOSED_BASE, B_COMPOSED_BRIEF) == set(B_COMPOSED_PATHS),
            "B composed exact 23-file input")
    commander_paths = {p for p in B_COMPOSED_PATHS if p.startswith(
        ("libs/agents/commander/", "libs/runtime/commander/")) or p in {
        "tests/test_p15_b_commander_monitor_boundaries.py",
        "tests/test_p15_b_commander_monitor_pure_parity.py"}}
    require(COMMANDER_V1_PATHS == commander_paths, "Commander V1 exact eleven-path pin")
    old_tree = ast.parse(git_source(B_COMPOSED_COMMANDER, "scripts/refactor/shared_strategist_contracts.py"))
    old_manifest = next(n.value for n in old_tree.body if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == "COMMANDER_V1_PROOF_HASHES" for t in n.targets))
    require(set(COMMANDER_V1_PROOF_HASHES) == COMMANDER_V1_CONTRACT_FILES,
            "Commander V1 exact proof inventory")
    require(COMMANDER_V1_PROOF_HASHES == ast.literal_eval(old_manifest),
            "Commander V1 historical proof manifest changed")
    expected = B_COMPOSED_PATHS | B_COMPOSED_CHECKS
    changed = _commander_delta(B_COMPOSED_BASE)
    changed |= set(subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"],
                                          cwd=ROOT, text=True).splitlines())
    changed |= set(overrides)
    require(changed == expected, "B-stage composed unexpected/missing inventory: " + repr(changed ^ expected))
    if inventory is not None:
        require(set(inventory) == expected,
                "B-stage composed unexpected/missing inventory: " + repr(set(inventory) ^ expected))
    for prefix in ("libs/agents/commander", "apps/operator_ui"):
        pinned = set(subprocess.check_output(["git", "ls-tree", "-r", "--name-only", B_COMPOSED_BRIEF,
                                             "--", prefix], cwd=ROOT, text=True).splitlines())
        pinned = {p for p in pinned if p.endswith(".py")}
        disk = {p.relative_to(ROOT).as_posix() for p in (ROOT / prefix).rglob("*.py")}
        require(disk == pinned, "B-stage composed unexpected/missing package file: " + repr(disk ^ pinned))
    for path in sorted(B_COMPOSED_PATHS - B_COMPOSED_CHECKS - COMMANDER_V1_NOTES):
        require(_commander_read(path, overrides) == git_source(B_COMPOSED_BRIEF, path),
                "new-stage source/ABI/body differs from B pin: " + path)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    for path in sorted(B_COMPOSED_CHECKS):
        require(_commander_read(path, overrides) == git_source(head, path),
                "B-stage checker/test drift from reviewed HEAD: " + path)
    note = "docs/trading_agent_patch_notes_detailed_update/patch_notes.json"
    old = json.loads(git_source(B_COMPOSED_BRIEF, note))
    current = json.loads(_commander_read(note, overrides))
    require(current["entries"][:-1] == old["entries"] and len(current["entries"]) == len(old["entries"]) + 1,
            "B composed historical patchnotes changed")
    require(current["entry_count"] == len(current["entries"]) == len({r["version"] for r in current["entries"]}) == 342,
            "B composed patchnotes count/version")
    require(current["entries"][-1]["version"] == "P15_B_COMPOSED_INTEGRATION_20261022",
            "B composed integration note")
    md = "docs/trading_agent_patch_notes_detailed_update/patch_notes.md"
    require(_commander_read(md, overrides).startswith(git_source(B_COMPOSED_BRIEF, md)),
            "B composed historical Markdown changed")
    verify_historical_b_scope()
    return frozenset(changed)


# The original functions/bodies and historical manifest above are retained.
# Their old-stage tests execute them from immutable source archives. Current
# wrappers first prove the actual composed source, then expose the same named
# historical view rather than pretending its old source blob was rewritten.
_standalone_commander_v1 = verify_commander_pure_v1
_standalone_next_stage = verify_next_stage
_standalone_historical_source = historical_source


def verify_commander_pure_v1(overrides=None, *, inventory=None):
    if not b_composed_selected():
        return _standalone_commander_v1(overrides, inventory=inventory)
    verify_b_composed(overrides)
    old_paths = COMMANDER_V1_PATHS | COMMANDER_V1_CONTRACT_DELTA | COMMANDER_V1_NOTES
    if inventory is not None:
        require(set(inventory) == old_paths,
                "B-stage Commander V1 unexpected/missing inventory: " + repr(set(inventory) ^ old_paths))
    return {"version": COMMANDER_V1, "runtime_paths": COMMANDER_V1_RUNTIME,
            "changed_paths": frozenset(old_paths - COMMANDER_V1_NOTES)}


def verify_next_stage(overrides=None):
    if not b_composed_selected():
        return _standalone_next_stage(overrides)
    overrides = overrides or {}
    # Preserve original error/ABI semantics for the original five-function stage.
    verify_b_sources(overrides)
    verify_b_composed({p: value for p, value in overrides.items() if p in B_COMPOSED_PATHS})
    projected = dict(overrides)
    for path in (UI_INPUT, UI_SECTIONS):
        projected[path] = git_source(UI_PIN, path)
    return _standalone_next_stage(projected)


def historical_source(path):
    if b_composed_selected() and path in (UI_INPUT, UI_SECTIONS):
        verify_b_composed()
        return git_source(HISTORICAL_STAGE, path)
    return _standalone_historical_source(path)
