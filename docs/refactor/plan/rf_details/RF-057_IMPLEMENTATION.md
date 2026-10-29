# RF-057 — 코드 구조/함수 재배치 설계 (T00/V3)

## SOURCE 본문 검토 확정 — RF-057

`libs/skills/runner.py::SkillRunner.run(self,*,run_id,skill,args)` **L97~373, 약277줄**, `SkillRunner._to_dto` **L380~398, 약19줄**. 담당 **Codex B 단독**. 이 함수는 단순 큰 pure 함수가 아니라 **Step5C/5B mutation ownership·UNKNOWN quarantine·중복 주문 방지의 실제 효과 경계**다.

- **KEEP 효과 몸체:** `SkillRunner.run`의 `is_mutation_api_id` 판정, invalid symbol fail-close, `evaluate_unknown_quarantine_guard`, canonical intent_id 필수 검사, `execute_owned_order`의 CAS/단일 claim, `_capture_dispatch`, `quarantine_symbol_for_unknown_outcome`, 실제 `self.executor.execute`와 events 발생 순서는 **원본 위치에 그대로 둔다**. 새 실행 주체를 만들지 않는다.
- **추출 후보 S1 (순수):** `run`의 L109~136 `step.defaults/map` + 원본 raw args 우선순위·주문 시장가 `ord_uv` 정규화 부분. TARGET `libs/skills/runner_request_projection.py::build_step_context(step,args,api_id,*,render_template,rules)`. 다만 `rules.apply`의 효과 여부/패치 가능한 callable을 먼저 확인; 효과가 있으면 wrapper가 해당 부분까지 직접 수행하고 pure dict projection만 이동한다. 원본 `run`은 안전 게이트 전에 동일 순서로 helper를 호출한다.
- **추출 후보 S2 (읽기 전용):** L341 이후 DTO 선택 후 `SkillRunResult(action="ready",...)` 결과 조립. TARGET `libs/skills/runner_result_projection.py::build_ready_result(skill,spec,args,payloads,step_meta,dto)`; **기존 `_to_dto` 실행과 event log 호출은 원본에 남긴다**, dict/result 필드만 이동한다.
- **검증:** side=buy/sell·`trde_tp=3`·mapped/default/raw 우선순위 fake fixture, malformed symbol broker_call=0, duplicate claim broker<=1, quarantine UNKNOWN, 결과 dto 동등. 실제 Broker/운영 ledger 사용 금지. 각 변경 범위 정상 targeted offline pytest/unittest 1회, 원본 효과 순서·예외 유지.


**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-057.md` blob `dbc91718d013fcc7d225a53b818364805ed5fdb7`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 6개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/skills/__init__.py` → `libs/skills/__init__.py` | 198 | `446a0668e94d` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/skills/dto.py` → `libs/skills/dto.py` | 1070 | `2cee472d2052` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/skills/dto_extractors.py` → `libs/skills/dto_extractors.py` | 7429 | `1a4f10c71481` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/skills/registry.py` → `libs/skills/registry.py` | 2542 | `ea86588ef10f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/skills/rules.py` → `libs/skills/rules.py` | 2328 | `21f702b0a7e8` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/skills/runner.py` → `libs/skills/runner.py` | 19658 | `6544c3205d45` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
