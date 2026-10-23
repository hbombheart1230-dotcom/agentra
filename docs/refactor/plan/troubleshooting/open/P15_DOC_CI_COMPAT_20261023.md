# P1.5 문서 개편 CI 호환성 및 예약 검증 오류

- **상태:** `OPEN / BLOCKED` · 담당 GPT 지팀장 · 기준 `integration/p1.5@a3705871`
- **범위:** ROOT→LEAF RF-001~093 문서 개편 / D00-D02 / CURRENT / UI patchnotes; 소스 런타임은 이 건의 변경 대상이 아님.

## 원격 증거
- 2026-10-23 SHA `a3705871`: 필수 GitHub Actions **5개 중 success 1개, failure 4개**. `95d04a4`에도 동일한 1/4 실패가 있었으므로 이전 SHA만 보는 예약 보고는 잘못.
- PASS: [Integration Scripts Linux Windows Contract](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39882696557).
- FAIL: [Shared Candidate Required Contracts](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39882696617), [Integration T4 Regression](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39882696531), [Integration Reporting and Web Compatibility](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39882696646), [Reporting Regression + Design Guard](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39882696542).
- T4/Design Guard: 과거 고정 검증이 `Issues #16–#19 are CLOSED`, `DOC_FREEZE`, `P1.5.2 OPEN`/`DOC-A`, Issue #20 등의 현재 운영문서 내 리터럴 표현을 요구함. 새 CURRENT 운영방식과 역사 고정 문자열 계약 충돌. 테스트 우회/더미 PASS 금지.
- Shared candidate: `scripts/refactor/shared_strategist_contracts.py:94`가 오래된 정확한 B-stage composed 파일 목록만 허용하여 RF93 및 새 문서 경로를 unexpected inventory로 차단. 구 역사 SHA 검증과 현재 docs-only 변경 승인 경계를 분리 설계해야 하며 임의 allowlist 확장 금지.
- Reporting compatibility: `tests/test_patch_notes_sync.py:57`에서 신규 JSON 두 항목에 필수 `impact` 누락; 추가로 최근 문서 `sources`에 디렉터리 경로가 있어 file provenance 검증 위험.
- 원격 브랜치 목록은 5개; 옛 `work/p15-b-operator-live-overview-20261020` ref는 404, 보존 태그 `archive/p15-20261022/b-operator-historical`는 `70843da4...` 그대로. 예약 보고의 구 브랜치 미삭제 주장은 사실과 다름.

## 현재 조치 / 다음 게이트
- [x] UI JSON 기존 두 레코드 `impact` 및 최근 source file-path 스키마 정정, Markdown 동기 기록. 이 조치만으로 CI 전체 PASS 선언 불가.
- [ ] 기존 DOC_FREEZE/역사 SHA 가드가 보존되는 신규 CURRENT 유효성 검사를 어떻게 추가할지 기술 검토/독립 리뷰. 기존 CI 오라클 단순 완화·삭제 금지.
- [ ] 과거 S5 B-stage 정확한 파일 인벤토리와 후속 docs-only 변경을 서로 다른 증명 대상으로 나눌 허용된 경로 검토. 무단 임의 allowlist/테스트 우회 금지.
- [ ] 해당 수정 후보를 독립 CLI와 normal/`python -O`로 검토한 후 **수정된 정확한 통합 SHA**의 5개 CI 확인, 그 전까지 RF DONE/통합 PASS 불가.
- [ ] 예약 실행은 항상 원격 `integration/p1.5` HEAD와 최신 CI를 기준으로 하고, 브랜치 삭제/보존 태그는 API로 재확인. 쓰기 실패는 해당 시도만 BLOCKED 보고하며 오래된 SHA로 덮어쓰기 금지.

**제약:** `main`·실거래·안전 권한·CI 검증 오라클을 수정/약화하지 않음. 이미 공개된 RF 계약은 유지하고 정확한 해결에는 별도 검증 필요.

## 지팀장 CI 호환성 수리 후보 (2026-10-23)
- **확인된 마지막 녹색 기준:** `51bb7130b2ba627be50800fa89c6108dd1a5018c` (필수 CI 6/6 PASS). RF93 문서 스냅샷 `3fb24fe01761bd8f68587ee48fd0014e807d0d8a`와 분리.
- **기존 실패:** `3fb24fe0` 5개 워크플로 최종 1 PASS / 4 FAIL. Shared/Reporting은 과거 B-stage 정확한 29경로 검사가 후속 120건 문서 변경을 source inventory로 오인. T4/Design Guard는 DOC_FREEZE/역사 provenance 표현 삭제로 실패.
- **수리 범위:** B-stage 기존 29경로 인벤토리·실제 Owner 바이트/AST/ABI·부정 mutation 검증 유지. 녹색 고정 SHA의 역사적 인벤토리와 RF93 문서 스냅샷을 분리하여, 스냅샷 이후 정확히 명시한 CI 수리 파일 외 변경을 거부한다. 문서 provenance는 재활성 지시가 아닌 과거 기록으로 복원한다. UI patchnotes JSON/MD 동기화.
- **판정:** 수리 커밋은 hosted exact-SHA normal/optimized CI 및 별도 독립 CLI verdict 이전까지 `VERIFY_PENDING`. CI 실패가 남으면 수정 완료 선언 금지; 기존 오라클/실거래 경계 변경 금지.

- **후속 실패 세부:** 최초 수리 SHA `419128e0`의 T4/Design Guard는 문서 검사 32번째 assertion에서 `docs/refactor/README.md`의 역사적 `DOC_FREEZE` 표식 누락을 발견. 해당 README에 비활성 provenance를 복원했고 CI 수리 경계에 정확한 경로 한 개만 추가. 기존 오라클/워크플로 수정 없음.

## 2026-10-23 09:54 UTC 지팀장 exact-SHA CI 재검증

- **실제 조회:** `integration/p1.5@138bdaedc050cc6cdf00983e9f92b9b60ddd5531` (Shared job checkout 로그의 SHA 일치). 5개 워크플로의 최신 시도 job 완료 상태 직접 확인: **1 PASS / 4 FAIL**. `main`/런타임 소스 변경 없음. 이 증거는 CI 재실행이 아니라 기존 hosted run의 job/log 재검증이다.
- **PASS:** [Scripts Contract #39920091454](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39920091454) (Linux/Windows success).
- **FAIL inventory:** [Shared Candidate #39920091422](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39920091422) (4개 contracts job fail): `scripts/refactor/shared_strategist_contracts.py:94`의 historical B-stage inventory에서 `docs/ENGINEERING_DELIVERY_POLICY.md`, `docs/refactor/plan/STATUS.md`, `docs/refactor/plan/verification/{claude,codex}/.gitkeep` 4경로 unexpected. [Reporting/Web #39920091470](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39920091470) (reporting-compat fail, web-build PASS): 같은 inventory mismatch, 592 passed / 2 failed / 1 deselected.
- **FAIL peer gate:** [Design Guard #39920091404](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39920091404), [T4 #39920091423](https://github.com/hbombheart1230-dotcom/agentra/actions/runs/39920091423): CI 단계의 `AssertionError: read-only peer-review gate missing`. 해당 기존 검사에서 D01/D02의 `claude -p`/`codex exec` 직접 상대 CLI 요구를 기대하나, 최신 CURRENT는 별도 read-only 독립 검증 세션으로 변경됨. 기존 안전한 독립 검증 게이트 보존을 전제로 역사 계약과 현재 계약의 범위를 분리해야 한다.
- **수리 후보:** Claude `a0493b60` (handoff `59e34204`)는 Codex B 보고상 pinned historical object `613a945d...`의 `apps/operator_ui/data_access_core.py` 부재로 독립 normal setup ERROR, `python -O NOT_RUN`; **PEER_PENDING / NOT_ADMITTED**. 먼저 정확한 역사 객체 확보·검증 가능성 재확인, 이후 read-only normal/-O 검증. 오라클 삭제/느슨한 allowlist/무단 source admission 금지.
- **A 경계 가드(별개):** Claude A `HANDOFF_A.md` 추가 후 179 passed / 7 failed(normal/-O); 보고된 7건은 historical pinned source 대비 신규 handoff 문서 경로에 따른 scope check. **HANDOFF 기록용 branch HEAD와 코드 후보 SHA를 분리**하여 테스트하고 원본 oracle은 수정하지 않는다. RF-013/018은 그 밖의 2290 passed / 1 failed / 58 errors(normal/-O), 독립 PASS 없음으로 BLOCKED.

**다음 게이트:** 지팀장 별도 승인 없이는 CI/가드 코드를 고치지 않는다. Codex B는 CI_RED 후보의 정확한 history 핀과 독립 검증 실패를 증거로 확정; Claude A는 source-only exact SHA 테스트를 별도로 기록; GPT는 계약 호환성의 최소 수정 경계를 검토하고 독립 PASS 전 integration 통합 금지.

## 2026-10-23 후속 A 소스-only 가드 재확인 (독립 PASS 아님)

- A 예약 `RUN_ID=2026-10-23T-claude-a-sched-3`, 브랜치 `bd11c774`, 코드 후보 `a21401db`: HANDOFF가 없는 detached clean source-only worktree에서 A 경계 가드 + S5 helper test를 normal/`python -O` 각각 **185 passed / 1 failed**로 보고. 이전 HANDOFF 포함 브랜치의 7 실패 중 6건은 handoff 문서 경로의 역사 allowlist 충돌로 분리되었으나, **잔여 1건은** `scripts/refactor/shared_strategist_contracts.py:91`의 pinned B-stage 소유 경로 검사가 A 후보 Reporter/Strategist 변경을 거부. 공유 오라클 변경 승인 아님. A 자체 보고, 지팀장 독립 실행 NOT_RUN.
- **다음:** 소스-only `a21401db`와 별개 B-stage 고정 범위 계약의 적용 대상을 구분하여 소유자/안전 영향부터 판정. 기존 oracle·allowlist를 임의 변경하지 않고 CI_RED 후보 독립 검증 이후 최소 호환성 수리 여부 결정. `8e0a7d3` 이후 exact-SHA hosted CI 상태는 별도 확인 전 UNKNOWN.

## 2026-10-23 11:10 UTC — A 가드 원인 세분화 (미수리)

- 원격 Claude A `375861876fda3c7e27927c0a38ab24de2b0a2d6e`, `HANDOFF_A.md`의 `EVIDENCE_11Z` (RUN `2026-10-23T11:08Z-claude-a-sched-4b`) 수거. A 소스 후보는 기존 `a21401db` 그대로이며 **신규 소스 변경 없음**. A 보고의 detached source-only normal/`python -O` 각각 **185 PASS / 1 FAIL**; 실패 `test_diff_against_pinned_source_touches_only_the_closed_path_set`에서 RF-013 Reporter 관련 변경·테스트를 포함한 **51경로**가 역사적 S5 범위 밖이라고 보고. 51경로 목록/테스트 실행은 A 자체 증거이며 GPT 독립 재현 `NOT_RUN`.
- GitHub 정적 교차확인: `a21401db:tests/test_p15_strategist_s5_helper_moves.py`의 해당 테스트는 `scripts.refactor.shared_strategist_contracts.verify_integration_scope()`를 직접 호출하여 **pinned integrated lane**을 검증한다. Reporter/Strategist A 작업 브랜치 전체 변경을 S5의 닫힌 통합 범위로 오인하지 않도록 적용 대상/기준 SHA를 분리해야 한다. **이 사실은 51경로 자동 승인이나 오라클 allowlist 확장 근거가 아니다.** 기존 pinned gate 보존, A 소유 RF별 테스트와 S5 historical integration gate를 구분하여 별도 독립 검증한다.
- A HANDOFF 상단 RUN_ID `10:58Z-...-4`와 후속 증거 `11:08Z-...-4b`가 혼재하고 TEST_NORMAL에 과거 `NOT_RUN` 설명이 남아 있다. 다음 A 회차는 한 개의 정확한 RUN_ID로 현재 회차 실행과 과거 인용을 분리해 기록해야 한다. B는 이후 11:10Z 회차에 새 원격 `1fbfb78e`로 갱신했다. CI_RED read-only normal/`python -O` 각각 exit 1 (`git show` pinned UI 경로 조회 실패), 독립 PASS 없음. **지팀장 GitHub 직접 조회에서는 `613a945d2b27e735d4019cdc85b4660f2c891d8f:apps/operator_ui/data_access_core.py`가 blob `54f8fc8211ceb5cc559ce9e01e1b73254a24b40c`로 존재함을 확인**했다. 따라서 원격 역사에서 파일이 없다는 가정은 기각하며, B 실행 환경의 commit 객체 접근/clone fetch 범위/명령 stderr를 분리 진단해야 한다. 정확한 객체를 read-only로 확보하고 동일 후보의 normal/-O를 재검증하기 전 CI_RED 수용·통합 금지.

## 2026-10-23 13:13 UTC Codex B 재검증 — 역사 객체 접근 해소, 구조 계약 FAIL

- B 원격 HEAD `c3d410769a27a58dfa53adc46f7a131a13420f9c`, RUN `B-20261023T131355Z`. 허가된 읽기 전용 `git fetch origin 613a945d2b27e735d4019cdc85b4660f2c891d8f` exit 0; B 보고 `git cat-file -t` = commit, pinned `apps/operator_ui/data_access_core.py` `git show` exit 0. 이전 **history object unavailable** 원인은 해당 환경에서 해소.
- CI_RED 기존 후보 `a0493b6035b390a1691371364b1e4ba3ec50aea9` detached read-only normal 및 `python -O` **각 exit 1**. 새 차단은 B-stage UI structure **6경로 unexpected/missing** (HANDOFF_B, commander/monitor 4파일, `tests/test_p156_p157_role_contracts.py`); 정확한 경로 분류와 허용 범위는 아직 GPT 승인 없음. **PEER REWORK_REQUIRED, NOT_ADMITTED**. 오라클/후보 변경 및 integration merge 없음.
- 다음 B: 6경로의 기준 SHA·기존 소유권·역사 B-stage 인벤토리 대비 기대/실제를 구분해 증거 제출. GPT: 역사 오라클 보존을 전제로 소유권 및 후보 admission 최소 경계를 판정; 무단 allowlist 확장 금지. integration `f2bd4beb` exact-SHA hosted CI **UNKNOWN** (PR 필터 조회 결과 없음은 PASS 근거 아님).

## 2026-10-23 14:14 UTC B 최신 exact-candidate 재검증 — 이전 UI 6경로 판정 철회

- B HANDOFF `B-20261023T141441Z`, 원격 HEAD `baf066f100291325a72d50bdee74049adaf71167`: 기존 후보 `a0493b6035b390a1691371364b1e4ba3ec50aea9`의 **실제 detached candidate worktree**에서 `verify_next_stage()` normal/`python -O` 각각 **exit 0**으로 B가 보고. 추가 pinned `6849bed4af358c214f63011a0d58ef760ca79fa0` fetch 후 `cat-file`/`git show` 성공. 지팀장 로컬 재실행 NOT_RUN.
- 직전 UI structure 6경로 exit 1은 **B 작업 트리에서 실행한 결과**로 확인되어 이 후보에 대한 REWORK 근거에서 철회. 다만 **별도 peer-session receipt NOT_RUN, exact-candidate hosted CI UNKNOWN, source admission NOT_ADMITTED, 통합 NOT_RUN**. SELF/단일 read-only 재현을 최종 PEER_PASS로 승격하지 않는다.
- 다음: B는 정확한 후보 SHA·worktree·명령·exit를 유지하고 별도 독립 검증 증거를 확보한다. GPT는 역사 오라클을 수정하지 않고 admission 경계와 exact-SHA CI를 확인한 뒤에만 통합을 판정한다.

## 2026-10-23 15:02 UTC — 지팀장 hosted CI 직접 조회·실패 로그 판독 (신규 증거)

- 정확한 integration `fa23381147f911380060af675d48a8eaef9088dd`의 `GET /actions/runs?head_sha=<SHA>` 결과 5건: Scripts `39974053284` **SUCCESS**; Shared `39974053382` **FAILURE**; Reporting/Web `39974053579` **FAILURE**; Design Guard `39974053569`, T4 `39974053411` **IN_PROGRESS** (Linux regression job 각 FAIL, Windows required job 아직 진행 중). 이 기록 시점의 5개 최종 1/4 등 완료 판정 금지. PR-only 조회가 비어도 GitHub Actions는 실제 존재한다.
- **Shared 실패 로그:** Ubuntu normal job `120483928968` (Windows normal/optimized, Ubuntu optimized도 같은 targeted smoke 실패). `scripts/refactor/shared_strategist_contracts.py:94`의 `verify_b_composed()`가 historical B-stage inventory 대조에서 **문서 6경로**를 unexpected/missing으로 보고: `docs/ENGINEERING_DELIVERY_POLICY.md`, `docs/refactor/plan/STATUS.md`, `docs/refactor/plan/pending/RF-013.md`, `docs/refactor/plan/pending/RF-026.md`, `docs/refactor/plan/verification/claude/.gitkeep`, `docs/refactor/plan/verification/codex/.gitkeep`. 예시 2 FAIL / 2 ERROR / 7 PASS; 현재 문서 정본의 합법 변경과 역사 고정 B-stage 검증 범위가 충돌한다. **역사 allowlist 확장·검증 oracle 수정 승인 없음.**
- **Reporting/Web 실패 로그:** job `120483928955`, `tests/test_p166_v1052_candidate_risk_migration.py`의 `test_pilot_touches_no_forbidden_surface`와 `test_current_stage_still_rejects_true_authority_changes`가 동일 문서 6경로 인벤토리로 **2 FAIL / 592 PASS / 1 deselected**. Web build와 LF/Windows baseline job은 PASS. Shared와 별도 제품 결함 2개로 오인하지 말 것.
- **Design Guard/T4 Linux 실패 로그:** jobs `120483929675`, `120483929824`의 `Validate live D00 DOC-FIRST contract and historical preservation` 단계 `AssertionError: read-only peer-review gate missing`. Inline guard는 D01 `AGENTS.md`에 `REVIEW_ONLY_NO_NESTED_CLI` 리터럴을 요구하고, 그 다음 D00 `DIRECT CROSS-CLI RELAY`, D01 `claude -p`, D02 `codex exec` 등 **현재 폐지된 opposite-CLI 실행 방식의 역사 문자열**도 요구한다. D01/D02는 별도 읽기 전용 peer 검증·상대 CLI 미호출을 명시하므로, 문자열 삽입만으로 테스트를 통과시키면 실제 현행 계약 검증이 되지 않는다. 새 계약을 역사 고정 테스트와 구분하는 **의미 보존된 검증 설계**가 필요하며 기존 oracle 임의 완화 금지.
- **즉시 판정/소유권:** 원인은 런타임 RF-013 코드 결함으로 입증되지 않았으며 **GPT 소유의 historical/current contract admission 충돌**. A/B의 이미 지정된 RF 개발을 중단시켜 동일 CI 로그를 재진단시키지 않는다. GPT는 기존 계약의 역사 pinned SHA·검증 대상·문서 변경 경계별 기대 집합을 분리한 최소 수리 후보를 독립 검증할 것. **수락 조건:** 역사 B-stage 원본에 대한 mutation/rejection 테스트 보존, 현재 문서-only 변경의 정상/optimized 회귀 PASS, 현행 read-only/no nested CLI 규칙에 대한 실질 assertion PASS, integration exact SHA hosted 5개 모두 SUCCESS. 조건 전에는 CI_RED / NOT_ADMITTED, RF DONE 0/93.
