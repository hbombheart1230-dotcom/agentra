# D00 — Agentra engineering constitution: DELIVERY FIRST / NO RECURSIVE AUDIT

> **읽기 최적화 (2026-10-22):** [한글 CURRENT](refactor/work_orders/CURRENT.md)가 유일한 활성 작업 상황판이고, 실제 작업·검증·완료 체크는 [plan/pending](refactor/plan/pending/) → [plan/verification](refactor/plan/verification/) → [plan/done](refactor/plan/done/)에, 개발자 실행·티키타카 규칙은 [D01 Codex](../AGENTS.md) / [D02 Claude](../CLAUDE.md)에 있다. 본 D00은 **GPT 및 전 팀에 적용하는 안전·공통 개발 원칙**으로 새 세션 또는 개정·충돌·안전 판단 때 확인한다. 같은 세션에서 이미 읽었고 파일 SHA/내용이 그대로면 전문 재독하지 않는다. 아래 오래된 날짜별 BATCH 지시는 새 작업권한이 아니다.


## 2026-10-22 ACTIVE EXECUTION LOCK — READ FIRST (FULL REPOSITORY)

**Single live instruction pointer: [`docs/refactor/work_orders/CURRENT.md`](refactor/work_orders/CURRENT.md).** Product Owner confirms entire Agentra ROOT→LEAF P1.5.0–11 refactor, not only `libs/agents/`: all 26 `libs/` packages plus `.github/`, `apps/`, `graphs/`, `scripts/`, `tests/`, `docs/`, `deploy/`, `config/`, `data/` and root controls. Reuse frozen V3 and the **existing** P1.5 packets, original full-tree path/owner ledgers, and existing branches; DO NOT activate draft PR31 T00–T09 program or superseded BATCH03–05 as new dispatch. Safety/explicit latest user approval always wins.

**Order:** documentation pointer fixed → reviewed A/B/PR31 source admission and safe one-ref B housekeeping (Codex sole CLI owner under latest PO instruction) → exact composed integration-SHA normal/-O/peer/hosted CI → redundant stage retirement → remaining existing P1.5.0–11 work by original packet ID. Main/real trades and Supervisor/Executor/Step5C authority remain separately gated. Do not claim any action automatically started by reading this file.

**Old instructions below are preserved as dated history and are NOT active assignment authority when conflicting with CURRENT.** Use only safety and process invariants that remain compatible.

## 2026-10-23 ACTIVE RF HANDOFF / INDEPENDENT VERIFICATION QUEUE

- **Canonical lifecycle:** `docs/refactor/plan/pending/RF-xxx.md` (구현 대기) → `docs/refactor/plan/verification/claude/RF-xxx.md` 또는 `verification/codex/` (구현자 self 검증 후 상대 독립 검증 대기) → `docs/refactor/plan/done/RF-xxx.md` (독립 검증자의 제한된 통합과 정확한 SHA CI PASS 후 GPT DONE 판정). `verification/claude`는 **Claude가 구현했고 Codex가 검증할 작업**, `verification/codex`는 **Codex가 구현했고 Claude가 검증할 작업**이다. **93개의 고유 RF 파일은 항상 정확히 한 상태 폴더에만 존재**해야 한다. 검증 대기는 DONE이 아니다.
- **RF 파일 단일 원본:** 기존 RF 본문을 그대로 보존하고 같은 파일의 끝에 짧은 `개발 인수인계` 및 `독립 검증` 섹션을 추가한다. 구현자는 `AUTHOR / BASE_SHA / CANDIDATE_SHA / BRANCH/PR / CHANGED_PATHS / MOVE·KEEP_VERIFIED·WRAPPER 근거 / 공개 import·호출·계약·side effect 동등성 또는 HOLD / 실행한 normal·python -O 명령·exit·PASS 수 / patchnotes JSON·MD / 미해결 문제`를 실제 사실만 기록한다. 검증자는 작성자의 PASS를 그대로 승인하지 않고 **정확한 후보 SHA를 독립 checkout/읽기 전용 검사 및 가능한 위험 표적 테스트**한 뒤 `REVIEWER / REVIEWED_SHA / commands·exit / PASS·REWORK·BLOCKED / NOT_RUN / 결함 / 새 SHA 재검증`을 같은 RF에 기록한다. 빈 증거·구두 보고·exit0만으로 PASS 불가.
- **이동 게이트:** 구현 완료가 아닌데 `verification/`으로 옮기지 않는다. 정확한 후보 코드 SHA가 GitHub에 존재하고 self normal/`python -O` 및 필수 증거가 있을 때만 인수인계 이동을 제안한다. 구현자가 자신의 후보 PR에서 동일 RF를 `pending → verification/<author>`으로 **rename**하고 관련 상대 Markdown 링크(깊이 변경)를 보정한다. **공용 `integration/p1.5` 상태판에 반영하는 metadata-only 이동은 GPT 또는 별도 승인된 단일 queue publisher가 수용**한다. 이 상태 이동은 코드 통합·독립 PASS·실거래 승인과 무관하다. 충돌/중복 이동은 중단하고 HEAD 재조회. 다중 RF 간 공유 patchnotes/STATUS 동시 수정은 GPT가 조정한다.
- **REWORK / BLOCKED:** 검증에서 실패하면 검증 이력을 보존한 채 CURRENT가 원 구현자에게 같은 RF를 재배정한다. 구현자는 새 SHA를 제출하고 이전 독립 PASS를 승계하지 않는다. 필요 시 `pending/`으로 되돌리되 새 RF 파일 생성 금지. 리뷰 수행 환경에서 명령이 불가하면 `PEER_DEFERRED` 또는 `BLOCKED`이지 PASS가 아니다.
- **티키타카의 두 실행 운송수단:** 로컬 상대 CLI(`claude -p` / `codex exec`)의 격리·읽기 전용·실제 exit 요구는 유지. 클라우드에서는 **다른 모델/서비스의 독립 세션이 동일 SHA를 검증**하고 명시적 실행 증거를 남긴 경우만 별도 `REMOTE_PEER_PASS` 후보로 표시할 수 있다. 단순 PR 자동 코멘트, self-test, 타 모델 미실행, 테스트 불가 사실을 CLI PASS로 가장하지 말 것. 최종 독립 게이트 수용은 GPT가 증거로 판정하고, 이후 통합 SHA hosted CI가 필수다.
- **예약·이벤트 중립 규칙:** 트리거는 작업 배정권이 아니다. 매 실행마다 `origin/integration/p1.5`의 CURRENT와 구현/검증 큐를 확인하고 **CURRENT에 명시된 할 일만** 수행한다. 중복 (RF, 역할, 후보 SHA) 실행은 차단하고, 중간에 발생한 새 배정은 유실 없이 다음 실행에서 조회한다. 실행 중 상태는 실제 외부 run 상태와 교차 확인; GitHub Actions 잡 종료만으로 외부 Claude 세션 종료를 추정하지 않는다. 자동 트리거·API 비밀값·`main` 워크플로 추가는 별도 승인 전까지 **NOT_ENABLED**다.

- **2026-10-23 사용자 승인 — RF 검증자가 통합·CI까지 담당:** Claude 작성 RF는 Codex, Codex 작성 RF는 Claude가 독립 검증한다. 동일 작성자가 자기 변경을 검증·통합 승인하지 않는다. 검증 세션/자식 CLI 자체는 끝까지 읽기 전용이며 code edit/commit/push/nested CLI 금지; **실제 독립 PASS가 확정된 후에만 검증 담당자의 분리된 통합 단계**에서 해당 RF의 승인된 변경 경로를 `integration/p1.5`로 제한 통합할 수 있다. GPT의 매건 수동 cherry-pick·CI 실행 요구는 제거하되, GPT만 RF `done/` 최종 판정·이동 및 소유권 재배정·예외 승인한다. 이 최신 승인 규칙이 아래 날짜별 GPT-only integration 서술에 우선하며 안전·실거래·main 승인권까지 위임하지 않는다.
- **통합 순서·잠금:** 다른 RF를 통째로 병합하지 말고 정확한 BASE/CANDIDATE SHA, 파일 독점권, 공개 API/계약, 기존 통합 HEAD 및 오염되지 않은 source 범위를 확인한다. 하나의 RF 통합 writer만 같은 시점에 쓰도록 실제 GitHub 단일 writer 잠금/queue가 있거나, 최신 HEAD 재조회와 non-force fast-forward/CAS 동등의 원자적 ref 갱신을 입증해야 한다. 동시 진척·충돌·잠금 수단 부재·다른 담당 소유 파일 변경 시 자동 병합하지 말고 `INTEGRATION_BLOCKED`로 GPT 보고. 새 SHA의 통합 코드에 정상/`python -O` 대상 회귀와 필수 GitHub Actions를 적용한다. Actions 결과는 **새 통합 SHA와 URL, 성공/실패/NOT_RUN**으로 기록하고 필수 실패·미실행·pending이면 `CI_PENDING/BLOCKED`이지 PASS가 아니다. 다른 변화가 뒤따랐다면 HEAD와 영향 범위를 다시 확인한다.
- **위임 범위:** 신규 RF의 독립 검증 뒤 **통합/CI 실행 주체만** 검증자로 이전한다. 기존 4-HEAD 합성 후보 `d73be191`과 PR31/source admission, CI 오라클 변경, 공개 공유 계약·안전 경계, `main` 승격은 자동 위임 대상이 아니며 CURRENT의 GPT 별도 게이트 유지. 상태표의 검증 성공과 최종 DONE은 별개이다.
- **Safety and completion unchanged:** D00 안전 원칙, D01/D02 소유권, 동결 P1.5.0~11, Python normal/`-O`, UI patchnotes JSON·MD, RF 검증자 제한 통합·정확한 통합 SHA CI와 GPT 단독 DONE 판정, `main`/실거래 승인 게이트 모두 유지한다.


## HISTORICAL 2026-10-20 — BATCH05 folder-scale return contract (NOT active task scope)

- Product Owner authorizes **BATCH05 four substantial deliverable groups per primary developer**, about 2–3× the BATCH04 *inspected source scope* and organized by related directory, **but bounded by exact approved file allowlists**. Prefer large/easy PURE reporting/read-model boundaries; don't split already pinned historical R3 Owners or grow tiny helper files merely to satisfy LOC. Developer may finish all four groups with one code/review handoff; no arbitrary time minimum or made-up work durations.
- **Same report format for Codex and Claude**, using the **Claude BATCH04-A detailed example**: title+exact BASE/CANDIDATE SHA, branch/worktree/push, changed paths, A1–A4/B1–B4 code results+LOC, byte/effect/parity and normal/-O test counts, nonvacuous mutation outcomes, local CI/reviewer authority blockers, independent vs self tests, precise NOT_RUN. **LAST heading `### 티키타카 실행 리스트`** must be a complete table of all actual direct child CLI calls, including denied and incomplete attempts, exit, verdict, flags/isolation, reviewer tests actually run vs NOT_RUN, real fixes/new SHA.
- Distinguish `SOURCE_STATIC_PASS`, `PEER_PASS`, `REVIEW_COMPLETION_BLOCKED`, `SOURCE_ADMISSION_PENDING_GPT`, `INTEGRATION_BLOCKED_T3`, `INTEGRATED`; a child EXIT0 or author normal/-O is not full independent PASS. Supplementary command denied1 stays visible even if source review PASS. GPT may separately inspect patchnote files to close doc-only coverage, without misattributing review to peer.
- Two separately diagnosed local/CI issues: **CLI reviewer sandbox** can forbid Python/JSON tests even when static PASS; author runs focused normal/-O separately under authorized isolated scratch; reviewer uses exact plain allowlisted commands or declares `REVIEWER_TESTS_NOT_RUN` and `REVIEW_COMPLETION_BLOCKED`, never a permission bypass. **Hosted T3 immutable Git SHA missing in Linux** remains failed; local `git cat-file -t` presence/absence and read-only test can be recorded, not regarded as hosted repair. Previous denied GitHub workflow mutation is not reauthorized by general task expansion. No alternate tool/script/workflow/test route around denial. Source integration still blocked pending separately permitted approval.
- Canonical exact work scope and stop conditions in `docs/refactor/work_orders/P15_BATCH05_FOLDER_SCALE_REPORTING_AND_OPERATOR_BRIEF_20261020.md`, `CURRENT.md`, Issue #20. D00/D01/D02 are HOW, not self-executing CLI authority. Work order does not launch Windows developer processes.


**Stable alias:** D00 = `docs/ENGINEERING_DELIVERY_POLICY.md`; D01 = root `AGENTS.md` (Codex), D02 = root `CLAUDE.md` (Claude). Trading safety source: `docs/ground_rules/AGENT_RULES.md`. No alternate D00/D01/D02 filenames.

**Adopted by operator / GPT Tech Lead: 2026-10-18. Standing policy for all future P1.5–P8 work.**
**Purpose:** finish verified trading-system improvements in a single integrated codebase, rather than endlessly generating tools, inventories, evidence documents, and branch-specific PASS labels.

> **CURRENT SAFETY / BRANCH TRUTH (2026-10-19):** `main` is **policy-protected / user-approval-only**, but GitHub branch-protection enforcement was **reported absent (`protected:false`, no active ruleset) in the 2026-10-19 read**, and has **not been independently reverified** in this docs-only change. References below to "protected main" describe a **must-not-edit policy**, NOT confirmed GitHub enforcement. Do not merge/push to `main`; request explicit operator-admin setup and verified rules before release promotion. 2026-10-20 D7 DOC_FREEZE has been explicitly accepted; the separately operator-authorized CODE BATCH01 developer branches exist. Closed #16–#19 remain historical; code release/main/live trading are NOT approved.

## 0. Authority order and handoff
1. Trading safety/fail-closed invariants and explicit latest operator authorization always take precedence. Never weaken broker gates, Step5C CAS/UNKNOWN quarantine, UEF oracle, production-write isolation, credentials, or approval control for speed.
2. This standing delivery policy governs HOW all four workers operate. The CURRENT task issue supplies the *specific exact SHA, paths, scope and reviewer*. Historical work orders, dated overrides, stale branch pointers and old NOT_STARTED checklists are **evidence, not active instructions** when they conflict.
3. One live master issue (#20) and `docs/refactor/work_orders/CURRENT.md` identify the single currently approved integration milestone. A GitHub issue/comment **does not launch a CLI session**. The user/operator launches local sessions.
4. GPT acts as **architect + integrator + finish-owner**, not just prompt writer. GPT must directly inspect actual tree/code/imports when possible, settle one owner per responsibility, decide approval and merge scope, and report what was actually committed vs planned. The user retains control of high-risk/live deployment, destructive removal, and protected-main decisions.

## 1. Define DONE properly
- `IMPLEMENTED`: developer committed/pushed exact source SHA and target test evidence.
- `AUDITED`: independent reviewer checked changed boundary and recorded PASS/REWORK with test/CI facts and NOT_RUN, NOT_VERIFIED clearly labeled.
- `INTEGRATED`: **the approved changed code is on the integration branch**, there is no missing cherry-pick, branch fork contamination, or patchnote chronology conflict, and appropriate checks ran on the **newly composed integration SHA**.
- `RELEASE_ACCEPTED`: whole-repository/safety/UI/real-evidence gates required for the *stage* completed; only then user-authorized protected `main` promotion. Never call developer-branch PASS a completed integration or final release.
- A refactor is progress only when **owner clarity, original-file responsibility/complexity reduction, duplicate/compatibility-debt reduction, reliable imports and accepted integrated code** improve. File count, PR count, documents, inventory lines, test invocations and SAFE-count are not delivery metrics.

## 2. Stop endless loops
1. Do **not** create new analyzer, analyzer-of-analyzer, AST inventory, counterexample factory, scope checker, harness or extra document merely to certify another checker. Reuse existing targeted runtime/contract/differential proof. A previously **REWORK/FROZEN** analyzer stays untrusted and is never a source-migration SAFE certificate.
2. Audit **only exact changed paths/callable contracts** since a pinned, previously accepted base. Reuse prior independent PASS for unchanged code. A new negative result in the changed boundary must be addressed; known unchanged historical debt is documented as HOLD, not silently accepted or recursively reaudited.
3. The reviewer must return a bounded `PASS / PASS_WITH_FINDINGS / REWORK / BLOCKED` decision plus evidence/NOT_RUN and STOP. No autonomous expansion into additional full scans, old worktree surveys, extra test generation or other roles without a real code-change/safety trigger and operator scope approval.
4. If work is blocked, present the **specific blocking evidence and the smallest executable remediation**, rather than producing more analysis artefacts. If work passes, hand it to integration promptly instead of starting a new wave on an old developer base.
5. An engineer proposing new infrastructure must demonstrate direct functional need, expected time/cost, alternatives, and specific owner approval. **No perfect-testing-system project nested inside a source refactor.**

## 3. Test strategy (avoid duplicate 3,000-test loops)
- **Developer:** touched-module regression, positive and negative tests, import/State/IO/monkeypatch/LLM/broker boundary checks as applicable, normal and `-O` for relevant focused suites.
- **Independent reviewer:** static diff plus self-run *risk-targeted* tests, fixture/golden and fail-closed adversarial checks; may rely on real, SHA-matched GitHub CI for existing entire matrix. Do not independently rerun ~3,100 tests in two modes on every developer SHA without a demonstrated uncovered cross-cutting risk.
- **Integrator:** compare selected developer commits, resolve conflicting notes, run required matrix on **new integration SHA** and perform contract/replay/write-safety checks. Full-repository pytest/UI visual/real-data parity belong at the stage/freeze gate (or earlier when a real high-risk change warrants it).
- Maintain distinguishable counts: selected CI collection != whole repository; 24 genuine-real-data SKIPs remain SKIP/NOT_RUN, never hidden as PASS. Never fix a failing test by relaxing oracle, skip/xfail/waiver, invented fixture labels, suppressed error, or shortened safety path.
- Resource contention can cause false failures: report hardware/OS/Python and rerun isolated *failing case* first. Parallel or serial full matrices should be a reasoned exceptional choice, not a default reviewer ritual.
- CI success is **not** independent source review, and independent review is **not** a second copy of the entire CI.

## 3A. Two equal development parts — DIRECT CROSS-CLI RELAY (operator policy, 2026-10-20)

**Standing team structure for all approved Agentra refactor work (P1.5 onward):** On the operator's **one Windows PC**, two long-lived **developer** CLI sessions operate concurrently, with independent writer-owned workspaces and an approved exact-SHA work packet for each. **CLAUDE_DEV_A** owns Reporter / Strategist / Scanner and their proven pure analysis, policy and read-model boundaries; **CODEX_DEV_B** owns Monitor / Commander / Operator UI and pure State/integration projections. These are two substantive implementation teams. Neither CLI is permanently assigned as the other's auditor. Shared contracts and graph/effectful paths remain under GPT integration arbitration and the safety rules below. Roles and per-slice file ownership are restated in the current work order, not inferred as unrestricted path access.

**NON-NEGOTIABLE direct CLI self-dispatch — OPERATOR CORRECTION (2026-10-20):** The **primary developer** that just finished writing code **MUST invoke the opposite CLI command itself on the same Windows PC from its own shell/tool**, with no additional operator copy/paste and no handoff to the opposite primary developer chat. For Codex-authored code, the primary Codex session runs `claude -p "<self-contained REVIEW_ONLY_NO_NESTED_CLI request; exact BASE SHA, candidate SHA, changed paths, relevant failure/negative tests>"`; for Claude-authored code, the primary Claude session runs `codex exec "<same read-only review request>"`. Capture the actual child process stdout/stderr/exit code in the **calling developer's existing interactive CLI chat**, inspect structured `PASS | REWORK | BLOCKED`; exit 0 alone is NOT PASS. On genuine REWORK, the **same primary developer** implements the correction, commits/pushes a NEW SHA and **reruns a NEW opposite CLI subprocess locally**. On a real PASS, stop the review loop and hand SHA/evidence to GPT integration. **No user-pasted reviewer start info; no user manually starting the reviewer; no separate long-running primary Claude/Codex session being used as the reviewer; no nested reviewer calls.** If the local command or sandbox refuses, report BLOCKED, never fake execution or evade approvals.

### 2026-10-20 operator update — approval-free local cross-CLI + mandatory final 티키타카 ledger

**Review subprocess permission:** The operator explicitly requests eliminating permission-prompt stalls when the primary developer self-invokes the *other* CLI. On an **externally isolated reviewer snapshot only**, with OS-enforced **source/working-tree read-only ACL**, separate writable per-session pytest scratch, no production/trading credentials or operational files, no unrestricted network or live broker capability, and exact SHA/source diff pinned, permitted no-prompt examples are:

- **CODEX_DEV_B → fresh Claude reviewer:** `claude -p --dangerously-skip-permissions --tools "Read,Glob,Grep,Bash" "<REVIEW_ONLY_NO_NESTED_CLI exact-SHA prompt>"`
- **CLAUDE_DEV_A → fresh Codex reviewer:** `codex exec --dangerously-bypass-approvals-and-sandbox "<REVIEW_ONLY_NO_NESTED_CLI exact-SHA prompt>"`

**These flags bypass native approval/sandbox safeguards; they are NOT a grant of source write permission.** Do not invoke them in an unisolated Windows working copy, dirty operational workspace, or any process with broker tokens, Git push credentials or writable code/CI/production paths. The isolation must be **enforced outside the CLI**, not assumed from the words "read-only" in a prompt. If it cannot be demonstrated, fall back to native noninteractive no-prompt read-only modes (`claude -p --permission-mode dontAsk` with an explicit exact-command allowlist, or `codex exec --sandbox read-only --ask-for-approval never`), and report the concrete `BLOCKED` if tests/commands remain denied. The caller must preflight command spelling against its installed `--help`, use undecorated allowlisted test invocations, never hide nonzero exits with a pipeline, and never retry a denied call as a workaround. **This new user authorization permits one fresh, independently safe review of the previously blocked CODEX B candidate 8fd49dd, not a silent PASS.**

**Reviewer scope remains immutable:** review only exact BASE/CANDIDATE and approved changed files, risk-targeted normal/`-O` tests; do not modify any source/test/contract/notes, commit, push, invoke another CLI, enable live orders, or touch CI workflows. Only the original author may REWORK, then use a new candidate SHA and new child review. Exit 0 is NOT PASS without the explicit verdict.

**Required LAST SECTION in every primary developer's final response: `티키타카 실행 리스트`.** Show one row for **every actual** author→child-review invocation in this work block: round, author and review CLI, exact BASE→CANDIDATE SHA, effective permission/sandbox flags and isolation, child process exit, explicit PASS/REWORK/BLOCKED, independently run normal/`-O` tests or NOT_RUN, concrete findings/fix and any new SHA. Include denied/retried attempts and distinguish a simulated response, no-review exit, and genuine completed PASS. Then print current implementation, peer, integration/CI statuses and the next authorized action. Keep reports concise; do not manufacture extra rounds to fill a time quota.

**Work sizing:** Next independently authorized batches should contain 2–4 connected material implementation+contract+regression outcomes, not a one-function microtask. Scope sizing is NOT a mandatory duration or license to change other files. Stop at NO_MORE_AUTHORIZED_READY_SCOPE if the connected backlog has no approval. This permission rule does not resolve existing T3 Linux missing-object CI or authorize CI workflow writes, main or trading.

**Peer review is a direct child CLI call, NOT a separate orchestration service:**
1. Each developer initially **develops its own approved batch**. After a coherent batch is implemented, run focused positive/negative tests, record exact `BASE_SHA`, `CANDIDATE_SHA`, changed paths and actual NOT_RUN, and commit the candidate in its own isolated lane.
2. **Codex developer calls Claude CLI:** `claude -p "<self-contained read-only review request>"`. **Claude developer calls Codex CLI:** `codex exec "<self-contained read-only review request>"`. The calling developer invokes the opposite installed CLI **from its own available shell/tool** as a **new, noninteractive reviewer process**. The recipient is NOT the other developer's existing long-running developer session. Confirm the installed command syntax and permissions on the actual PC; NEVER bypass sandbox/approval controls merely to force review.
3. A reviewer starts in `REVIEW_ONLY_NO_NESTED_CLI` mode: inspect only the pinned diff and relevant consumers, safety/state/UEF/Step5C/golden impacts; run narrow, safe, read-only focused checks as permitted. **Never edit source, commit/push, dispatch a third CLI, or recursively invoke a reviewer.** Return a concise `PASS / REWORK / BLOCKED` verdict with exact SHA, findings and genuine test/evidence details through stdout or an explicitly permitted bounded per-session receipt.
4. The **calling developer must consume** the peer CLI exit code **and** the structured verdict (exit zero alone is not PASS). On `REWORK`, fix only its own files, create a **new candidate SHA**, re-invoke a **new opposite-CLI review session** and repeat. On `PASS`, publish the SHA-bound receipt and immediately continue its next independently READY batch, while the other primary developer continues its own area. On `BLOCKED`, preserve state, stop unsafe or overlapping work and escalate the concrete blocker; never fabricate PASS or wait indefinitely.
5. **The GPT Tech Lead owns both durable work orders**, shared owner/consumer contracts, inter-part collision arbitration, bounded retry/cost policy, review receipts and selective integration onto the approved integration branch. Only required hosted CI on the **composed integration SHA** establishes integration regression evidence. The operator supervises interrupted CLI sessions and explicitly authorizes any later re-launch, new workspace/branch, DOC_FREEZE, protected-main promotion or actual broker operation.
6. CLI subprocess invocation is **conditional on actual local capability**, not guaranteed by a prompt. No persistent runner, daemon, scheduler, server, GitHub-comment-triggered invocation, auto-resume claim or cross-review infinite recursion. Reuse ordinary CLI shell capabilities and restrict per-run test scratch/output retention.


## 3B. SUBSTANTIVE DEVELOPMENT BLOCK, not one-function microtask (operator directive, 2026-10-20)

**Human expectation:** Give each primary developer a cohesive **60–120-minute-class amount of real source-engineering work** per approved assignment. This is an expected *scope size*, not a sleep timer, billable-hour minimum, quota of commits, or permission to pad with docs/audits. Pack each owner-specific work order with roughly 2–4 causally linked deliverables: identify the actual boundary and consumers, implement meaningful source responsibility reduction, prove BASE parity/negative cases, obtain concrete opposite-CLI review, respond to REWORK, and close an integration-ready contract. A trivial 40-line extraction plus PASS must not be presented as a satisfactory large development block. If scope unexpectedly finishes early, **report the undersizing to GPT** and use only any next explicitly authorized READY slices already in the packet; otherwise hold, do not invent work.

**Coherent pipeline / reciprocal conversation:** Keep both primary CLI sessions interactive. For meaningful milestones, show `[DEV-A|DEV-B][PLAN|EDIT|TEST|PEER_REQUEST|PEER_RESPONSE|REWORK|HANDOFF]` directly in the **existing visible CLI conversation** (operator views via remote-control app), with honest test counts, exit and exact SHA. Before review, state the specific questions and safety boundary; after, display the findings and developer's reasoned disposition. A true REWORK requires a **new implementation SHA** and another fresh bounded review. If reviewer PASS has no defect, do not manufacture back-and-forth, unnecessary tests or forced delays. No external status observer, local progress watcher, ZIP or new tooling to satisfy visibility.

**Do not conflate verdicts:** `PEER_PASS` means a particular candidate passed its bounded source review. `INTEGRATION_READY` additionally requires all mandatory pre-integration contracts and guards to pass or an explicit, independently verified change of those contracts. `INTEGRATED` additionally requires selected code, dual UI notes, and required checks on the new composed SHA. A candidate with intentionally failing historical guard tests is **PEER_PASS_WITH_INTEGRATION_BLOCKER**, not integration-ready; do not simply relabel/skip/xfail/relax its oracle. Ask GPT for a separate scoped owner approval before editing guard contracts.

**Standing ACTIVE-PARALLEL / MINIMUM-IDLE dispatch rule (operator reaffirmation, 2026-10-20):** GPT Tech Lead is accountable for maximizing **meaningful engineering throughput**, not merely keeping CLI sessions busy. Whenever one primary developer is implementing, testing or self-running the opposite reviewer CLI, GPT should proactively supply the other primary developer a **distinct, already authorized or explicitly newly operator-approved READY source-development slice** in its own ownership area, with exact non-overlapping files and real code/test outcomes. Do not park an available developer as a manual review concierge: the authoring developer itself runs `claude -p` (Codex author) or `codex exec` (Claude author). Keep each lane's original primary conversation visible. After a candidate's real peer PASS, promptly progress acceptance/integration while the other lane develops; avoid wasting throughput in docs-only handoff or repeated microtask re-audits. **Safety and authorization bound concurrency:** no simultaneous writers to a shared file, invented tasks, fictitious time minimums, unauthorized source/approval expansion or bypass of BLOCKED security/CI gates. If no disjoint READY implementation is approved or safe, clearly report `NO_MORE_AUTHORIZED_READY_SCOPE` / `BLOCKED` and the smallest required GPT/operator decision, rather than manufacture work or claim it is running in the background. GPT remains responsible for integration and exact composed-SHA CI.

**Continuity:** Primary sessions continue across a related *preauthorized* multi-step block rather than stopping after the first micro-candidate, but cannot self-authorize another branch, workspace, file, 1–2-hour batch, safety boundary or code mutation. On completed approved scope print what was delivered plus `NO_MORE_AUTHORIZED_READY_SCOPE` and hand off; a process exit is normal after that. GPT is responsible for making adequately sized follow-on work packets READY in advance. Do not say a stopped CLI is still running.

**Live facts at the directive date:** `CODEX_DEV_B@c0c3f808967dc921a956d01a879fe489674cad71` reported peer PASS, 100/98 focused developer tests, no new hosted CI and is integration pending. `CLAUDE_DEV_A@ad4eed21d8303d4d8cb99f4097b4812cf2522f97` reported real Codex review REWORK at `7d647493`, then modified new SHA and second review PASS, 139/25 focused tests, but two frozen Reporter guards fail (plus existing missing historical Git objects locally); it remains `PEER_PASS_WITH_INTEGRATION_BLOCKER`. Neither is approved for source release or main. See [active scope/ledger](refactor/work_orders/P15_SUBSTANTIVE_DEV_LOOP_20261020.md) and GitHub Issue #20.

**Minimal peer review receipt:**
```yaml
protocol: AGENTRA_CROSS_CLI_REVIEW_V1
review_mode: REVIEW_ONLY_NO_NESTED_CLI
origin_developer: CLAUDE_DEV_A | CODEX_DEV_B
peer_reviewer: CODEX_CLI | CLAUDE_CLI
base_sha: EXACT_40_HEX
candidate_sha: EXACT_40_HEX
changed_paths: [EXACT_CHANGED_FILES]
verdict: PASS | REWORK | BLOCKED
findings: [CONCRETE_PATH_AND_LINE_OR_NONE]
tests: [ACTUALLY_RUN_COMMAND_AND_EXIT_OR_NOT_RUN]
return_to: ORIGINAL_DEVELOPER_SESSION
```
**Phase gate:** The 2026-10-19 DOC-FIRST override in §6 remains binding. This establishes HOW the two parts develop **after** operator DOC_FREEZE acceptance, not permission to start refactoring before it. Document convergence may follow this review protocol when both CLI sessions are explicitly started. In every mode preserve Broker, Supervisor, Executor, Step5C CAS/UNKNOWN quarantine, UEF canonical evidence, real market data and production-write SAFETY_LOCKs. The reviewer is read-only; there is no live trading authority transfer.

## 4. Branches, scope, and integration
- Keep only user-approved active branch lanes: protected `main`, **one integration branch**, and the minimum needed developer branches; read-only auditors use isolated detached SHAs. No new branches for incremental tasks/ZIPs/re-audits without authorization.
- **Selective audited change promotion only.** Never merge a whole diverged developer branch just to pick a document or tiny source slice. Check actual integration HEAD and ensure notes/paths stay coherent.
- Historical refs with unique commits, open PRs, unknown local worktrees, dirty state or upstream differences are preserved. Delete only after owner/scheduler/restore/unique-commit review; no force-reset, force-move, prune, worktree delete or production directory clean as a shortcut.
- Close and record each accepted slice on integration as soon as its exact required gates pass; do not accumulate weeks of audited-but-unintegrated code.
- The **entire repository root** is in scope: `.github/apps/config/data/deploy/docs/graphs/libs/scripts/tests` and root config files. Role folders alone are not the P1.5 definition of done.
- HYBRID-7 V3: seven roles are public responsibility boundaries, not permission to copy broker, ranking, approval, or UEF authority. `graphs/trading_graph.py` is a graph-shaped test baseline; real operational order path through Commander and `execute_from_packet.py` is separately SAFETY_LOCK.
- No cosmetic `__init__.py`, facade, service, duplicate owner or package just to look complete. Preserve dynamic consumers and late monkeypatch/cold-import semantics.

## 5. Reporting and artifact discipline
Every task report must fit the following compact record; link detailed evidence once, do not duplicate historical results:
```text
TASK / OWNER / BASE_SHA / NEW_SHA / EXACT_CHANGED_PATHS
FUNCTIONAL_DELTA / TESTS_SELF_RUN / CI_REUSED_WITH_SHA
INDEPENDENT_VERDICT / INTEGRATION_SHA_OR_PENDING
RISK_BLOCKERS / NOT_RUN / NEXT_SINGLE_ACTION
```
- The GPT Tech Lead owns a clear **integrated-code progress board**: DONE on integration, AUDITED waiting for pick, REWORK with blocker, BLOCKED/NOT_RUN. No misleading blanket green board.
- When a meaningful tracked change is authorized, update both UI-linked `docs/trading_agent_patch_notes_detailed_update/patch_notes.json` **and** `patch_notes.md` on the actual integration commit, recording honest scope (including docs-only). Don't overwrite older entries or claim an unperformed run.
- When handing user a file bundle, ZIP **only actually changed files** with their relative repository paths; never include secrets, production data, caches, untracked evidence piles or unchanged files. No ZIP generation in CI.
- Test scratch must be session-isolated; successful scratch auto-cleaned, failed evidence bounded retention. Do not grow files/dirs every full test rerun.

**Required report tail:** Both primary developer end-of-task replies must end with a compact `티키타카 실행 리스트` (including explicit blocked child calls, exact SHA/exit/verdict/NOT_RUN). This is an **actual-invocation ledger**, not a requested count of review rounds; preserve READ_ONLY review scope even where execution prompts are disabled.

## 5A. GPT Tech Lead → operator: SHORT UPDATE + COPY/PASTE TO CODING OWNERS ONLY (standing rule, 2026-10-20)

**Operator preference, mandatory for this project:** User controls the primary Claude/Codex developers from a remote app and must NOT be asked to inspect local PC files to find the job. GPT Tech Lead **writes the detailed technical instructions, exact allowlist, BASE SHA, risks, tests and review criteria into a versioned Git work order and posts the authoritative Issue #20 checkpoint**, then responds **briefly in Korean**. Do not deliver full-size developer prompts, large status tables or verbose explanations to the operator by default. An explicit user request for analysis or a consequential safety blocker merits the necessary extra detail.

**Default operator-facing reply after creating/updating a coding task:**
1. One compact status sentence: `Git 작업지시 반영: <commit/link> · <CI PASS/RUNNING/FAIL accurately if checked>`; note any concrete blocker in one further sentence.
2. **Exactly one ready-to-paste short start-info code block for the currently assigned PRIMARY CODING OWNER**; if and only if both primary developers each have their own independent source-implementation task, provide one block for each real coding lane. **NEVER provide a separate Claude/Codex review-start info merely because the other CLI is the reviewer.** The coding developer directly launches its opposite CLI review subprocess via its own shell/tool (§3A). Each typically 4–6 lines, containing the current batch/lane, `git fetch` instruction, **exact repository-relative work-order path**, `Issue #20`, existing approved branch/workspace retention, in-session progress and opposite-CLI review visibility, and short completion evidence (SHA/tests/review/blockers). No long implementation plan inside these blocks; the linked Git work order is the actual instruction.
3. End. Avoid extra suggested tools, downloadables, multi-page reports or repeated restatement. The operator pastes each block ONLY into its designated active primary **developer** CLI; review invocations happen autonomously inside that same developer session, not via a second manual paste.

**Authoring discipline:** The start info is merely a **pointer**, not a substitute for the committed Git work order or an independent source-write authorization. Check newest exact branch refs and Issue #20 status before preparing each new task. **Do not claim** Git/Issue updates launched, resumed or live-streamed a local CLI, or imply an uncompleted CI/review has PASSed. Keep `main`, production-write and all trading SAFETY_LOCK restrictions in force. Long receipts and integration details stay in Git Issue, not the operator's chat. The primary developer may produce richer *in-session* progress visible through the remote app, as required by §3B.

## 6. Required integration-first sequence
```text
GPT issues TWO concurrent approved developer area work packets
  → Claude DEV-A and Codex DEV-B independently implement own slices
  → Each developer invokes the OTHER CLI as a NEW read-only review session
  → Each developer consumes PASS / REWORK / BLOCKED and fixes or continues
  → GPT resolves shared contracts and selectively integrates peer-PASS slices
  → Integration-SHA required CI and compatibility
  → Mark INTEGRATED; both development parts continue next READY slices
  → Stage/FREEZE whole-repo + real-data + UI checks
  → User approves protected-main promotion
```
**Historical 2026-10-19 user override — DOC FIRST (satisfied at D7 DOC_FREEZE on 2026-10-20):** 339-file `docs/refactor` classification, canonical authority consolidation, historical instruction quarantine, full link/reference verification, independent audit and user DOC_FREEZE acceptance precede **all further P1.5 code tasks and new Codex/Claude development branches**. Prior S5/UEF9/Strategist/Operator UI work at `a50d6e47` is completed scoped evidence, not a new task. GitHub Issue comments do NOT launch terminated CLI sessions. Do not mistake previous SHA CI PASS for full release acceptance.

## 7. Anti-loop exit question
Before asking for another audit, plan, tool, branch, inventory or test run, answer:
> **Will this action eliminate a real remaining delivery blocker on the current integration SHA?**
If NO, **stop**, state the fact and return to actual integration or approved source work. The user can override this rule explicitly; trading safety locks cannot be overridden merely by convenience.
