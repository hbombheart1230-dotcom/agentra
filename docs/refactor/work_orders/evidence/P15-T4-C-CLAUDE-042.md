# P15 T4-C — Strategist structural decomposition (Claude)

BASE `8acedae23e64c11b958556e7835b4ebf5e404e73` (docs-only commit on the T4-B ACCEPT code `4e242e5`; hosted CI 38667457908 SUCCESS) → FREEZE `52010813fff7e6c38760f3ffeb8eebc62dbc8911` (golden v3; v1 `c61caab`, v2 `7a35ba1`) → CODE `c5be2eae90926c8692e8a9d8a07edb210e0a61ce` (implementation commit; no implementation file changed afterwards). Scope: `graphs/nodes/strategist_node.py::strategist_node`. No change to Broker, Supervisor, Executor, Step5C, `main`, live `C:\Agentra`, any prompt/model/provider/timeout/retry/fallback of the frame LLM, T3.5/T4-A/T4-B golden fixtures. REAL_LLM_PARITY_NOT_RUN. REAL_REPORT_PARITY_BLOCKED stays OPEN.

## 1. Freeze before implementation

The BASE contract was first frozen and pushed (`c61caab`) before any implementation edit; hosted CI then proved the harness host-dependent, so the golden was regenerated twice by executing the UNMODIFIED BASE tree (`git archive` of `8acedae`) — v2 `7a35ba1` (uniform HttpClient guard: the Kiwoom theme-reader failure text depended on whether `requests` is installed; captured absolute pytest tmp paths relocated into the disposable cwd) and v3 `5201081` (outputs whose stable evidence ids hash Windows path separators are platform bound: FEATURE must equal the same-host pinned BASE exactly while effect names/exceptions are still compared against the golden). No implementation file differs between the freezes and the CODE commit. Frozen contract: 50 captured `strategist_node` State inputs (existing offline suite), 1,141 deterministic variants/scenarios, 1,118 ordered effects. Scenarios: mock frame LLM `ok` / `error` / `timeout` / `raises` / `error + strict` (recording fakes, zero external calls; call count and request payload digests are frozen effects), global-sentiment provider and news provider exceptions, empty / duplicate / fallback universe, news analysis on, plus per-key drop/none/empty perturbations. Frozen per record: full final State with key order, ordered effect list with argument digests, exception, returned-object identity. Replay runs under a frozen clock/uuid/random, scrubbed environment, relative `REPORTS_ROOT` in a disposable cwd, `PYTHONHASHSEED=0`, network blocked at socket and curl level; without mock data the market/news providers are replaced by deterministic offline answers (identical in BASE and FEATURE, so no live yfinance/provider call can occur — discovered while freezing: unguarded replay reached the network through curl_cffi). Native Windows exact golden; portable mode compares to the same-host pinned BASE (`git archive`); strict variant conservation and fail-closed oracle validation; all 50 records platform bound (evidence ids hash Windows separators), so cross-host evidence is the same-host pinned BASE; native Windows compares exact golden digests. Deterministic fixture parity only — NOT real Reporter/LLM/production parity.

## 2. LOC

| Item | BASE | CODE |
|---|---:|---:|
| `strategist_node` | 1,216 | 545 |
| `graphs/nodes/strategist_node.py` (file) | 4,676 | 4,053 |

## 3. OWNER_MATRIX (13 new Owners in existing `libs/runtime/strategist/{context,policy,output}`, all ≤ 350 LOC; 22 ledger segments, `docs/refactor/p1_5_third_pass_t4c_moved_segments_ledger.json`)

| Owner | LOC | Responsibility |
|---|---:|---|
| `policy/global_risk_adjustment.py` | 26 | risk-off/on policy adjustment from global sentiment |
| `context/news_signal_fallbacks.py` | 86 | news exception/disabled fallback signals, news context summary |
| `context/candidate_rerank.py` | 45 | deterministic candidate rerank, negative-news filter, risk-off cap |
| `context/theme_candidate_projection.py` | 36 | theme hints, candidate symbols, theme strength ordering |
| `context/regime_scoring.py` | 38 | regime/sentiment scores and labels |
| `context/llm_input_payload.py` | 111 | frame-LLM input payload + input quality, raw-input snapshot |
| `policy/llm_override_application.py` | 73 | AI/manual override application to the deterministic frame |
| `policy/strategy_policy_annotation.py` | 77 | market/scanner/horizon annotations on strategy policy, commander context, plan |
| `output/strategist_output_core_fields.py` | 114 | core `strategist_output` fields |
| `output/strategist_output_stage_reviews.py` | 46 | stage review / decision fields |
| `output/strategist_output_policy_commander_fields.py` | 89 | policy validation, commander reference, LLM frame status |
| `output/strategist_output_explanations.py` | 30 | explanation fields and memory packet visibility |
| `output/node_event_payloads.py` | 190 | market snapshot, ranked news, summary log, strategic-frame trace, decision-bridge payload builders |

Moves are verbatim statement runs / value expressions; locals enter as explicit parameters, outputs return as sorted-field NamedTuples, module globals resolve at use time as `facade.NAME` so existing monkeypatch seams stay valid. Scanner canonical ranking/Rank-1 authority, Commander policy precedence and Monitor handoff code are untouched.

## 4. Parity

* Frozen replay: full corpus (`verify <fixture> 1`, 50 records, all 1,141 variants) **0 mismatches** on the CODE tree; CI test replays the sampled set natively on Windows and against the pinned BASE on Linux.
* AST gate (`tests/test_p164_t4c_extraction_gates.py`, 11 tests): inlining every Owner reproduces the BASE `strategist_node` AST exactly; all other definitions (including `_run_strategist_frame_llm`, prompt builders, news/provider helpers) AST-identical; the single `_run_strategist_frame_llm` call site is byte-identical; remaining State writes keep BASE order; no LLM/provider/effect call inside any Owner.
* LLM call parity: mock LLM call count, request payload digest and fallback result are part of the frozen effects/State for ok/error/timeout/raises/strict scenarios — 0 mismatches. Real provider/prompt parity: `REAL_LLM_PARITY_NOT_RUN`.

## 5. SAFETY_LOCK / deliberately not moved

* Frame LLM entry, prompts, model/provider/timeout/retry/fallback, result insertion order: untouched at the original call boundary.
* The LLM result log payload (reads `STRATEGIST_FRAME_LLM_PROMPT_VERSION` from the environment), `llm_response_saved` payload (reads `EVIDENCE_LEDGER_PATH`), candidate generators, news/global providers, memory/feedback/read-model loaders, `record_raw_input`, `_emit_strategist_event`, `_log_strategist_summary`, `append_decision_trace`, `record_decision_bridge`, artifact writer and every `state[...]` write remain in the node.
* BASE×2/FEATURE×2 independent-session differential NOT RUN (P2 carried from T4-B).

## 6. Verification

| Item | Result |
|---|---|
| T4-C structural gates (11) | passed |
| T4-C frozen contract tests (5) incl. forced portable mode + full-corpus replay | passed / 0 mismatches |
| Strategist-related existing tests (180 files) | 1,973 passed, 24 skipped; 20 failed + 2 errors in `test_uef2a_forward_policy_contract.py` / `test_uef5_2_historical_recompute.py` — identical on the pristine BASE tree (pre-existing, unrelated to the Strategist; not changed here) |
| Historical P1.5 gates (`test_p15*`/`test_p16*`) | 3,108 passed, 1 skipped (Windows-only/conditional); re-run subset after harness fixes passed in CI |
| T4-B scope gate | stage-pinned to `8acedae`; T4-A/T4-B/T3.5 fixtures unchanged |
| Production-write leakage | none (disposable roots; network blocked) |

## 7. Remaining

T4-C IMPLEMENTED / PENDING independent Codex audit. T4-D, T5, P1.5.10 and Wave D NOT STARTED. REAL_REPORT_PARITY_BLOCKED OPEN. NTFS mtime P2 OPEN. Cross-seed telemetry-order P2 OPEN.

## 8. CI

CODE `c5be2ea` first runs failed on host-dependence of the freeze harness (Linux: strategy-memory packet ids hash Windows separators; Windows: Kiwoom-reader failure text depends on the requests package) — no implementation difference was reported. After the harness fixes (v2/v3 re-freeze from the unmodified BASE tree) required CI run 38678362869 on `c7583bf`: **regression SUCCESS, Windows harness isolation smoke SUCCESS** (T4-C Linux gate and Windows native replay accounting included). Final documentation commit CI recorded in the report.
