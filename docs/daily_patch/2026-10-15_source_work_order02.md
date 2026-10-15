# 2026-10-15 — GPT Source Work Order02

Branch: refactor/agentra-target-tree
Base: 925f624d4fcf476b5eef425a1ab5c07accafdc16
Status: SCRIPTS_CONTINUATION_IN_PROGRESS
T4 observed before commit: ad3659131e804f9fa84b67f3bf6a0a0b2017a064.
Only the specified sources and symbol consumers were inspected; no broad redesign.

## Actual function ownership

| Function / responsibility | Before | After | Compatibility |
| --- | --- | --- | --- |
| _number | baseline_samsung_hynix/data_provider.py | baseline_candle_reader.py | Q10 original name delegates |
| _normalize_rows | baseline_samsung_hynix/data_provider.py | baseline_candle_reader.py | Q10 facade passes its live _number seam |
| load_existing_candles | baseline_samsung_hynix/data_provider.py, imported by Q12 | baseline_candle_reader.py, imported directly by Q12 | Q10 public signature/defaults retained; facade passes its live _normalize_rows seam |
| Q10/Q12 _read | Two independent pipeline.py bodies | baseline_artifact_io.read_json_dict | Both old _read names delegate |
| Q10/Q12 _write | Two independent pipeline.py bodies | baseline_artifact_io.write_json_dict | Both old _write names delegate |

Paths above are under libs/reporting/. Three candle bodies transferred once;
four local JSON I/O bodies replaced by two shared implementations: two redundant
implementation copies removed. No separate caches or reader copies created.

## Consumers and monkeypatch seams

Targeted symbol search found Q10 pipeline, Q12 data_provider,
opening_rank1_shadow/candle_provider.py and q9_forward_candles.py (late import).
These retain the old Q10 import/call contract without editing other consumers.
Existing Q10 provider tests patch post_exit_shadow_recap freshness; its lazy import
and run_id formation remain in the shared body, preserving that seam.
No tracked caller patching the extracted private helpers was found in the bounded
consumer search. Nevertheless Q10 _number and _normalize_rows facades forward
local callbacks so before-call monkeypatches remain effective rather than becoming
dead aliases. Q12 local load_existing_candles binding also remains patchable.
Q10 private helper patches do not leak into independent Q12 calls.

## Preserved behavior

State OHLCV key precedence, Mapping/list acceptance, day fallback/date filtering,
sorted timestamps, price/volume defaults, symbol isolation, newest timestamp and
equal-timestamp row-count comparison, maximum two freshness attempts, exception
handling, missing-state early return and run_id_prefix/default/fallback unchanged.
allow_fresh_fetch=False returns without a freshness call; tests use stubs and
assert no unexpected calls even if an exception would otherwise be swallowed.

JSON read failure/non-dictionary returns {}; writes preserve UTF-8,
ensure_ascii=False, indent2, final newline and parent creation. I/O facades return
exactly prior results. vnext/storage.py atomic/immutable publication untouched.
All strategy/decision epochs/5-minute/returns/cost calculations, artifact paths,
schemas and authority code remain unchanged.

## Verification

- 81 pytest PASS: test_baseline_shared_owners.py (26 new cases), existing Q10/Q12
  baseline suites, opening_rank1_shadow and q12_delivery_alignment.
- Baseline differential harness executed only the four historical source modules
  from the specified SHA in memory; no old checkout or whole-repository copy.
  Five state-priority scenarios and six freshness scenarios (empty, exception,
  older, newer, equal-latest-more-rows, two failures) give identical Q10/shared/Q12
  values and per-symbol fetch/run-ID sequences; original Q10 function signatures
  identical. Full pipeline pair adds two scenarios: 13 total PASS.
- Full pipeline pair uses synthetic state, explicit fake BTC/fear inputs, fake cost,
  and isolated reports/q9/macro paths. All returned paths identical. Q10 six files
  (four JSON), Q12 nine files (six JSON): all15 artifact files /10 JSON byte-identical.
- Initial Q12 byte comparison differed only in existing hypothesis generated_at
  wall clock; the harness then fixed hypothesis_pipeline.datetime identically on
  both runs. No timestamp field was removed or normalized in the artifacts and no
  production clock code changed. Equality is raw-byte equality under this test clock.
- Targeted pytest temp is OS-temp and self-cleans on success. Differential harness
  TemporaryDirectory self-cleans. No actual external acquisition/orders occurred.
- One nonfatal pytest warning: cache_dir with cacheprovider disabled. No broad test
  replay or native Windows byte-parity claim.

## Scope and residual limits

T4 code-path overlap0 against observed latest T4; approved append-only shared UI
notes are the only allowed document overlap. No T4 checkout/merge/cherry-pick.
All141 CLI wrappers untouched. No scheduler/launcher, Config, order/broker runtime,
Supervisor/Executor, UEF authority, Web/API/Operator UI, strategy or vnext publication
changes. UI notes append-only with accurate entry_count; PR #5 stays Draft.

External/manual dynamic consumers beyond the targeted tracked search remain
unknown; no deletion is inferred. Native Windows parity and live provider behavior
were not tested; deterministic fixtures and pre-call patch contracts were tested.
Out-of-scope helper duplication and architecture/retirement gates remain untouched.
Changed-files-only ZIP is generated from the final commit; no further scope expansion.
