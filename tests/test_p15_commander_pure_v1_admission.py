"""Exact Commander V1 admission; every mutant starts with actual GREEN proofs."""
import ast
import sys
import pytest
from scripts.refactor import shared_strategist_contracts as S

sys.path.insert(0,str(S.ROOT/'scripts/refactor'))
import shared_role_contracts as R

EXPECTED_STAGE_CHECKER_SHA256 = '2763eec7d6ec3a5d508c30e9b19881458d1c15f96517354d9f7933481ea3a7ad'
SOURCE = "e4a597886f21f1655de170f54e863c2e74910d29"


def test_historical_and_commander_stages_are_distinct_and_green():
    assert S.SOURCE=="d269c906ebadad75a0b833778ebc6a632a388e7c"
    assert S.CANDIDATE_CODE==S.ADMITTED_CODE=="c4960c5312945c8dac9b141df222f54ecc28beda"
    assert S.B_PRE_SOURCE=="4b0c3e0b5f8f24fa3c10d9082b85fab63f15c4c3"
    assert S.B_SOURCE=="54bebe5ece0ac34c4f45df55c44889c9ce323e95"
    assert len(S.B_SOURCE_PATHS)==7 and len(S.B_CONTRACT_PATHS)==6
    assert S.verify_historical_b_scope()<=S.B_SOURCE_PATHS|S.B_CONTRACT_PATHS
    assert S.dump(S.restore_candidate(S.candidate_sources()))==S.dump(ast.parse(S.git_source(S.SOURCE,S.NODE)))
    assert S.verify_next_stage()==frozenset(S.NEXT_RUNTIME)
    result=R.verify_runtime()
    assert (result['moves'],result['facades'],result['monitor_modules'],result['monitor_bodies'])==(313,23,14,20)
    assert S.verify_commander_pure_v1()['runtime_paths']==S.COMMANDER_V1_RUNTIME
    # Still authentic old-stage rejection, never rewritten as a green old baseline.
    with pytest.raises(AssertionError,match='B-stage unapproved'):
        S.verify_legacy_b_scope()


@pytest.mark.parametrize('path', sorted(S.B_SOURCE_PATHS))
def test_historical_b_mutations_remain_red(path):
    assert S.verify_historical_b_scope()
    with pytest.raises(AssertionError,match='historical B-stage source differs'):
        S.verify_historical_b_scope({path:S.git_source(S.B_SOURCE,path)+'\n# forbidden old-stage edit\n'})


@pytest.mark.parametrize('path', sorted(S.COMMANDER_V1_PATHS))
def test_every_commander_source_and_test_pin_is_byte_exact(path):
    assert S.verify_commander_pure_v1()['version']==S.COMMANDER_V1
    assert R.verify_runtime()['moves']==313
    text=(S.ROOT/path).read_text(encoding='utf-8')
    for gate in (S.verify_b_scope,R.verify_runtime):
        with pytest.raises(AssertionError) as rejected:
            gate({path:text+'\n# unauthorized byte drift / ABI change\n'})
        assert path in str(rejected.value)


@pytest.mark.parametrize('path', sorted(S.COMMANDER_V1_PATHS))
def test_omitted_approved_path_never_falls_back_to_historical_stage(path):
    expected=S.COMMANDER_V1_PATHS|S.COMMANDER_V1_CONTRACT_DELTA|S.COMMANDER_V1_NOTES
    S.verify_commander_pure_v1()
    with pytest.raises(AssertionError,match='unexpected/missing inventory'):
        S.verify_commander_pure_v1(inventory=expected-{path})
    for gate in (S.verify_b_scope,R.verify_runtime):
        with pytest.raises(AssertionError,match='missing source'):
            gate({path:None})


@pytest.mark.parametrize('path', [
    'libs/agents/commander/projections/extra.py', 'libs/agents/commander/broker.py',
    'libs/execution/rogue.py','libs/approval/rogue.py','libs/broker/rogue.py',
    'graphs/nodes/execute_from_packet.py','libs/reporting/evaluation/uef9_rogue.py',
    'tests/test_unauthorized_stage.py','tests/fixtures/rogue/golden.json'])
def test_unknown_runtime_authority_test_or_fixture_never_acquires_a_prefix_grant(path):
    S.verify_b_scope();assert R.verify_runtime()['monitor_bodies']==20
    for gate in (S.verify_b_scope,R.verify_runtime):
        with pytest.raises(AssertionError) as rejected:
            gate({path:'BROKER_LLM_PRODUCTION_WRITE = True\n'})
        assert path in str(rejected.value)


@pytest.mark.parametrize('path', [S.VALUE,'libs/runtime/monitor/entry_cascade_projection.py',
    'libs/runtime/monitor_exit/reasons.py','libs/reporting/trade_report_ai.py'])
def test_pinned_historical_role_mutations_rejected_by_both_boundaries(path):
    S.verify_b_scope();assert R.verify_runtime()['moves']==313
    text=(S.ROOT/path).read_text(encoding='utf-8')
    for gate in (S.verify_b_scope,R.verify_runtime):
        with pytest.raises(AssertionError) as rejected:
            gate({path:text+'\nBROKER_AUTHORITY=True\n'})
        assert path in str(rejected.value)


@pytest.mark.parametrize('path', sorted(S.COMMANDER_V1_CONTRACT_FILES))
def test_checker_and_proof_mutations_fail_before_admission(path):
    S.verify_b_scope();assert R.verify_runtime()['moves']==313
    message='checker/test drift' if path in S.COMMANDER_V1_CONTRACT_DELTA else 'unexpected/missing inventory'
    for gate in (S.verify_b_scope,R.verify_runtime):
        with pytest.raises(AssertionError,match=message) as rejected:
            gate({path:(S.ROOT/path).read_text(encoding='utf-8')+'\n# changed proof\n'})
        assert path in str(rejected.value)


@pytest.mark.parametrize('addition', ['\nimport os\n','\n__import__("socket")\n',
    '\nfacade.LLMRouter.from_env()\n','\nState["approval"]=True\n',
    '\nopen("reports/live.json","w").write("broker")\n'])
def test_new_owner_cannot_add_llm_import_state_or_production_write(addition):
    path='libs/agents/commander/projections/cache_refresh_read_model.py'
    S.verify_b_scope();assert R.verify_runtime()['moves']==313
    for gate in (S.verify_b_scope,R.verify_runtime):
        with pytest.raises(AssertionError,match='source/ABI/body'):
            gate({path:(S.ROOT/path).read_text(encoding='utf-8')+addition})


def test_wrapper_argument_and_owner_abi_changes_are_rejected():
    assert R.verify_runtime()['moves']==313
    path='libs/runtime/commander/strategist_fingerprint.py'
    original=(S.ROOT/path).read_text(encoding='utf-8')
    assert 'max_len=max_len' in original
    for gate in (S.verify_b_scope,R.verify_runtime):
        with pytest.raises(AssertionError,match='source/ABI/body'):
            gate({path:original.replace('max_len=max_len','max_len=0',1)})


def test_source_fixture_and_proof_inventories_cannot_be_shortened(monkeypatch):
    S.verify_b_scope()
    path=next(iter(S.COMMANDER_V1_PATHS))
    with monkeypatch.context() as m:
        m.setattr(S,'COMMANDER_V1_PATHS',S.COMMANDER_V1_PATHS-{path})
        with pytest.raises(AssertionError,match='eleven-path pin'):S.verify_b_scope()
    with monkeypatch.context() as m:
        m.setattr(S,'COMMANDER_V1_PROOF_HASHES',{})
        with pytest.raises(AssertionError,match='exact proof inventory'):S.verify_b_scope()


def test_proof_manifest_does_not_hide_same_line_code_or_comments():
    import re
    S.verify_b_scope();assert R.verify_runtime()['moves']==313
    path='scripts/refactor/shared_strategist_contracts.py'
    text=(S.ROOT/path).read_text(encoding='utf-8')
    for suffix in ('; __import__("socket")', '  # hidden checker drift'):
        changed=re.sub(r'^(COMMANDER_V1_PROOF_HASHES = .*)$',lambda m:m[1]+suffix,text,flags=re.M)
        for gate in (S.verify_b_scope,R.verify_runtime):
            with pytest.raises(AssertionError,match='checker/test drift'):
                gate({path:changed})


def test_proof_value_canonicalization_never_grants_an_editable_manifest():
    import re
    S.verify_b_scope();assert R.verify_runtime()['moves']==313
    path='scripts/refactor/shared_strategist_contracts.py'
    text=(S.ROOT/path).read_text(encoding='utf-8')
    changed=re.sub(r'^COMMANDER_V1_PROOF_HASHES = .*$', 'COMMANDER_V1_PROOF_HASHES = {}',text,flags=re.M)
    for gate in (S.verify_b_scope,R.verify_runtime):
        with pytest.raises(AssertionError,match='checker/test drift'):
            gate({path:changed})


@pytest.mark.parametrize('kind', ['abi','body'])
def test_canonical_owner_abi_and_executable_body_are_not_reinterpreted(kind):
    S.verify_b_scope();assert R.verify_runtime()['moves']==313
    path='libs/agents/commander/projections/cache_refresh_read_model.py'
    source=(S.ROOT/path).read_text(encoding='utf-8')
    if kind=='abi':
        old,new='def shadow_float(value: Any, *, facade)', 'def shadow_float(value: Any, *, facade=None)'
    else:
        old,new='return float(value)', 'return 0.0'
    assert old in source
    for gate in (S.verify_b_scope,R.verify_runtime):
        with pytest.raises(AssertionError,match='source/ABI/body'):
            gate({path:source.replace(old,new,1)})


def test_historical_b_normalized_source_predicate_keeps_crlf_compatibility():
    path=next(iter(S.B_SOURCE_PATHS))
    original=S.git_source(S.B_SOURCE,path)
    assert S.verify_historical_b_scope({path:original.replace('\n','\r\n')})


def test_ignored_commander_module_cannot_hide_from_git_inventory(monkeypatch):
    from pathlib import Path
    S.verify_b_scope();assert R.verify_runtime()['moves']==313
    package=S.ROOT/'libs/agents/commander'
    original=Path.rglob
    extra=package/'ignored_capability.py'
    def changed(root,pattern):
        yield from original(root,pattern)
        if root==package and pattern=='*.py':yield extra
    # Inject only the enumerated input, without writing unauthorized production code.
    with monkeypatch.context() as m:
        m.setattr(Path,'rglob',changed)
        for gate in (S.verify_b_scope,R.verify_runtime):
            with pytest.raises(AssertionError,match='package file') as rejected:gate()
            assert extra.relative_to(S.ROOT).as_posix() in str(rejected.value)


def test_cached_immutable_history_never_accepts_a_later_mutant():
    S.verify_historical_b_scope();S.verify_historical_b_scope()
    for path in S.B_SOURCE_PATHS:
        with pytest.raises(AssertionError,match='historical B-stage source differs'):
            S.verify_historical_b_scope({path:S.git_source(S.B_SOURCE,path)+'\n# late mutant\n'})
