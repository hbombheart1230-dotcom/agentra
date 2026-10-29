# RF-036 — 코드 구조/함수 재배치 설계 (T00/V3)

**원본:** `integration/p1.5@ea97703a071238802c25cad92b2c3e55ad9e3062`, FILE_COVERAGE `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. 원 RF: `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-036.md` blob `0566e2116e623664332f8b944de72272bb09fef2`.
**구현 담당:** **Codex B**, 상대 **Claude A**는 해당 원본과 목표 코드 읽기 전용 검증. 소유 34개 파일; 다른 RF 경로 쓰기 금지.

> 설계와 구현은 다르다. 기존 DONE·KEEP·PASS 이력은 그대로 둔다. 이 문서의 `KEEP_IF`는 코드 실사 전 확정 PASS가 아니며, 정당한 KEEP이면 1줄 사유/블롭으로 즉시 통과한다. 반대로 큰 소스의 미완료 함수 이동은 기존 DONE과 별도로 TARGET_GAP으로 추적한다.

## 1. 소스 함수 → 목표 모듈/함수

**원본별 실측 함수 매핑 상태: 미확정.** 아래 전체 Git blob/크기 목록과 고정 목표 폴더 기준으로 분리 대상 원본을 지목한다. 코드 본문을 직접 읽지 않은 함수명·신규 함수를 추측해 확정 명령으로 발행하지 않는다. 해당 Actor가 구현 전 *아래 큰 파일*의 실제 `def/class`를 확인해 함수명을 이 문서에 보강하고, 단일 책임이면 KEEP 사유 한 줄로 즉시 통과한다.

## 2. 우선 구조 분석할 대형 Python 파일

**20KB 초과 원본 Python 없음.** 파일이 작아 책임·위치가 맞는 경우 KEEP_OK. 단순 폴더 꾸미기를 위해 추가 파일 만들지 않는다.


## 3. 소유 전체 파일 / 기본 목표 경로 / 정당한 KEEP 근거

`SOURCE_PATH = 기본 TARGET_PATH`는 T00~T09의 기존 경로 유지 후보이며 새 코어 함수는 위 1·2항으로 분리한다. 경로가 맞고 단일 책임·적정 길이이면 **KEEP_OK**. 근거는 한 줄, 동일 Git blob 재검증 0.

| SOURCE_PATH → 기본 TARGET_PATH | bytes | Git blob | 처리/사유 |
|---|---:|---|---|
| `libs/research/opening_rank1_deep_dive/__init__.py` → `libs/research/opening_rank1_deep_dive/__init__.py` | 93 | `85851c67e620` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_deep_dive/analysis.py` → `libs/research/opening_rank1_deep_dive/analysis.py` | 15119 | `9c10964aee7c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_deep_dive/loaders.py` → `libs/research/opening_rank1_deep_dive/loaders.py` | 5982 | `04befe9e0c25` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_deep_dive/metadata.py` → `libs/research/opening_rank1_deep_dive/metadata.py` | 3922 | `41d65f0946e6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_deep_dive/microstructure.py` → `libs/research/opening_rank1_deep_dive/microstructure.py` | 8800 | `3b0fe281813b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_deep_dive/pipeline.py` → `libs/research/opening_rank1_deep_dive/pipeline.py` | 8760 | `4992a00d0961` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_deep_dive/rank_context.py` → `libs/research/opening_rank1_deep_dive/rank_context.py` | 5449 | `1d612c85c436` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_deep_dive/read_model.py` → `libs/research/opening_rank1_deep_dive/read_model.py` | 9767 | `3924922684a6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_deep_dive/report.py` → `libs/research/opening_rank1_deep_dive/report.py` | 8788 | `a8eb6b0251f6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_longitudinal/__init__.py` → `libs/research/opening_rank1_longitudinal/__init__.py` | 99 | `6ce28faecb4c` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_longitudinal/analysis.py` → `libs/research/opening_rank1_longitudinal/analysis.py` | 8880 | `5b817956fbe2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_longitudinal/daily_provider.py` → `libs/research/opening_rank1_longitudinal/daily_provider.py` | 6422 | `6306574ecccb` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_longitudinal/delayed_outcomes.py` → `libs/research/opening_rank1_longitudinal/delayed_outcomes.py` | 6485 | `6b98058a97a0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_longitudinal/pipeline.py` → `libs/research/opening_rank1_longitudinal/pipeline.py` | 8546 | `1788336f0dbe` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_longitudinal/report.py` → `libs/research/opening_rank1_longitudinal/report.py` | 9966 | `c5fd957d8b10` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_longitudinal/stage_fate.py` → `libs/research/opening_rank1_longitudinal/stage_fate.py` | 4430 | `b800e0828eae` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/opening_rank1_longitudinal/universe_control.py` → `libs/research/opening_rank1_longitudinal/universe_control.py` | 7081 | `c24eb84d01c9` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/__init__.py` → `libs/research/rank1_feature_mart/__init__.py` | 101 | `cfe9c18bca63` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/activation_contract.py` → `libs/research/rank1_feature_mart/activation_contract.py` | 1709 | `bbf0fb5feee1` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/activation_shadow.py` → `libs/research/rank1_feature_mart/activation_shadow.py` | 12950 | `799dc296d1ce` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/builder.py` → `libs/research/rank1_feature_mart/builder.py` | 18824 | `cc332d9c5811` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/candidates.py` → `libs/research/rank1_feature_mart/candidates.py` | 5370 | `2042ae42471e` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/chart_features.py` → `libs/research/rank1_feature_mart/chart_features.py` | 5582 | `ca8e355936bd` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/contracts.py` → `libs/research/rank1_feature_mart/contracts.py` | 811 | `90b8f7ddb0b0` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/integrity.py` → `libs/research/rank1_feature_mart/integrity.py` | 4806 | `6b6952a9d1a6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/loaders.py` → `libs/research/rank1_feature_mart/loaders.py` | 10947 | `9cd0e98b8863` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/outcomes.py` → `libs/research/rank1_feature_mart/outcomes.py` | 5963 | `cc6a77d71b16` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/pipeline.py` → `libs/research/rank1_feature_mart/pipeline.py` | 7441 | `17cc6bef3bb4` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/prospective.py` → `libs/research/rank1_feature_mart/prospective.py` | 12393 | `61894f7646a2` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/prospective_contract.py` → `libs/research/rank1_feature_mart/prospective_contract.py` | 1860 | `10438e66b194` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/report.py` → `libs/research/rank1_feature_mart/report.py` | 4382 | `fa97967675b6` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/strategy_alignment_report.py` → `libs/research/rank1_feature_mart/strategy_alignment_report.py` | 7965 | `868bbb9e370f` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/strategy_choice_observation.py` → `libs/research/rank1_feature_mart/strategy_choice_observation.py` | 7703 | `971c0f86ee41` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |
| `libs/research/rank1_feature_mart/trees.py` → `libs/research/rank1_feature_mart/trees.py` | 7174 | `6fe790eafc7b` | KEEP_IF: 목표 디렉터리·단일책임·적정길이인지 본문 1회 확인; 아니면 큰 함수 추출 |

## 4. 구현 · 검증 · 인수 체크

1. 소유 개발자가 원본 함수와 소비자·효과를 **딱 한 번** 확인. 역할/위치 적합하면 `KEEP_OK | path | 한 줄 사유 | blob` 즉시 통과, 반복 테스트·반대 전수 peer/추가 문서 요구하지 않는다.
2. 실제 MOVE는 SOURCE의 계산 몸체를 TARGET Owner에 **이전**하고 원본에 같은 이름·인자의 얇은 wrapper만 남긴다. SOURCE LOC 감소·TARGET 새 blob·호출자 연결을 증거로 남긴다.
3. 변경 함수에 한하여 before/after fixture 2~4개를 대상으로 **normal targeted pytest 또는 unittest 1회**. 변화 없는 KEEP에는 테스트 0. `-O`/전체 CI/전체 frozen 매 RF 의무 없음.
4. A/B가 각각 자기 브랜치 code/test만 변경·정상 push. 서로 다른 RF가 같은 target 경로를 소유하면 구현 전에 C03이 단독 Owner를 지정. 이 문서의 새로운 타깃은 목표 **제안**이지 기존 FILE_COVERAGE를 자동 변경한 기록이 아니다.
5. C04가 원격 소스 SHA 기준 선별 통합, C05가 기존 RF 이력을 보존하며 `TARGET_STRUCTURE=PASS/PARTIAL/BLOCKED` 판단. 기존 DONE은 자동 취소하지 않되 TARGET_GAP을 완성으로 포장하지 않는다.

**보고:** `RF | ORIGINAL_SOURCE_BLOB | MOVED_FUNCTIONS | NEW_TARGETS | KEEP_OK(paths+reason) | BEFORE/AFTER_LOC | TEST_EXIT | PUSH_SHA | INTEGRATION_SHA | TARGET_STRUCTURE`. 보호된 주문/Broker/Guard/Step5C/UEF/운영 파일·DB 실효과는 무승인 변경하지 않는다.
