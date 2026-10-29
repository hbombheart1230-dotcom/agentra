# RF-093 — 코드 구조/함수 재배치 설계 (T00)

## T00 root public entry targets
Root README.md/AGENTS.md/CLAUDE.md/.gitignore/.dockerignore, requirements and conftest.py retain their canonical locations. In particular root conftest.py fixture and import/discovery scope must remain unchanged (KEEP_JUSTIFIED). A misplaced or mixed-function root Python would require its exact SOURCE::function and TARGET::function, not a cosmetic move. Small correct root entry = KEEP_OK.


**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-093.md` blob `d0efca8fa2c9aa0d61c85fcb9dd3bad7fafc7d41`.
**구현 담당:** **Claude A**, 상대 **Codex B**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 11개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

| SOURCE_PATH | bytes | 정확한 Git blob | 다음 코드 설계 절차 |
|---|---:|---|---|
| `conftest.py` | 33526 | `952624df2d3312ad37943ad99f9f46227b5ef3ec` | 실제 함수/메서드 경계 읽기 → 서로 다른 책임만 분리 → `conftest_parts.py` **목표 후보**(동일 역할 기존 모듈 우선) → thin wrapper |

## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `.dockerignore` → `.dockerignore` | 924 | `2036b0fa5943` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `.gitignore` → `.gitignore` | 856 | `0b8b5b2360a0` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `AGENTS.md` → `AGENTS.md` | 832 | `76ea38178774` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `CLAUDE.md` → `CLAUDE.md` | 829 | `8377195f283c` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `README.md` → `README.md` | 29758 | `24c5bad016c0` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `_health.json` → `_health.json` | 167 | `a09b9a90d62e` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `b.jsonl` → `b.jsonl` | 3514424 | `fb5ab12fa0ab` | KEEP_IF: 리소스·데이터 소비자 경로 |
| `conftest.py` → `conftest.py` | 33526 | `952624df2d33` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `pytest.ini` → `pytest.ini` | 347 | `94c96571df18` | KEEP_IF: CI/배포/런처 소비자 경로 계약 |
| `requirements.txt` → `requirements.txt` | 639 | `11c43eb2daa3` | KEEP_IF: 문서 참조·경로·내용 정본 |
| `sitecustomize.py` → `sitecustomize.py` | 437 | `45960c0be929` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
