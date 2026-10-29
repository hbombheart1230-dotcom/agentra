# RF-036 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@49cd60c4744c23ca556dbb633b197dbce4810d53`, RF 원본 `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-036.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Codex B 구현 / Claude A read-only. 소유 34개 경로.

## 1. 실측 함수 단위 분석 / 배치

실제 `libs/research/rank1_feature_mart/builder.py` blob `cc332d9c5811690d4d5117f52842eeb001fa9d8d` (387 LOC)의 함수 정의 확인. 이 파일의 단일 기능 경계·소비자 조건을 검토한 분리 후보이며, 영향이 있는 IO/State/LLM/브로커 함수는 효과 Owner로 유지한다.

| 원본 def/정확 라인 | 이동/KEEP | 신규/기존 목표 파일::함수 | 본문 행수·주의 |
|---|---|---|---|
| `libs/research/rank1_feature_mart/builder.py::_market_snapshot` L57-93 | MOVE_BODY | `libs/research/rank1_feature_mart/builder_market_snapshot.py::_market_snapshot` | 37행 · 순수 후보 |
| `libs/research/rank1_feature_mart/builder.py::_strategy_snapshot` L208-234 | MOVE_BODY | `libs/research/rank1_feature_mart/builder_strategy_snapshot.py::_strategy_snapshot` | 27행 · 순수 후보 |

### _market_snapshot — 원본 37행
- **확인된 책임:** `libs/research/rank1_feature_mart/builder.py` L57–93; 직접 호출 helper `_number`. 감지된 효과: 없음.
- **목표:** `libs/research/rank1_feature_mart/builder_market_snapshot.py::_market_snapshot` (Owner Codex B, RF-036). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

### _strategy_snapshot — 원본 27행
- **확인된 책임:** `libs/research/rank1_feature_mart/builder.py` L208–234; 직접 호출 helper 없음. 감지된 효과: 없음.
- **목표:** `libs/research/rank1_feature_mart/builder_strategy_snapshot.py::_strategy_snapshot` (Owner Codex B, RF-036). 본문을 이 모듈로 실제 이전, 기존 함수는 동일 서명의 wrapper만 유지. 호출자/patch seam·키 순서·기존 예외 보존, 중복 로직 제거.
- **검증:** exact 고정 SHA before/after fake fixture 정상·경계·예외/monkeypatch 테스트 1회만; 추가 -O/full peer 반복 금지.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/research/opening_rank1_deep_dive/__init__.py` | `libs/research/opening_rank1_deep_dive/__init__.py` | `85851c67e620` / 93B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_deep_dive/analysis.py` | `libs/research/opening_rank1_deep_dive/analysis.py` | `9c10964aee7c` / 15119B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_deep_dive/loaders.py` | `libs/research/opening_rank1_deep_dive/loaders.py` | `04befe9e0c25` / 5982B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_deep_dive/metadata.py` | `libs/research/opening_rank1_deep_dive/metadata.py` | `41d65f0946e6` / 3922B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_deep_dive/microstructure.py` | `libs/research/opening_rank1_deep_dive/microstructure.py` | `3b0fe281813b` / 8800B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_deep_dive/pipeline.py` | `libs/research/opening_rank1_deep_dive/pipeline.py` | `4992a00d0961` / 8760B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_deep_dive/rank_context.py` | `libs/research/opening_rank1_deep_dive/rank_context.py` | `1d612c85c436` / 5449B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_deep_dive/read_model.py` | `libs/research/opening_rank1_deep_dive/read_model.py` | `3924922684a6` / 9767B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_deep_dive/report.py` | `libs/research/opening_rank1_deep_dive/report.py` | `a8eb6b0251f6` / 8788B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_longitudinal/__init__.py` | `libs/research/opening_rank1_longitudinal/__init__.py` | `6ce28faecb4c` / 99B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_longitudinal/analysis.py` | `libs/research/opening_rank1_longitudinal/analysis.py` | `5b817956fbe2` / 8880B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_longitudinal/daily_provider.py` | `libs/research/opening_rank1_longitudinal/daily_provider.py` | `6306574ecccb` / 6422B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_longitudinal/delayed_outcomes.py` | `libs/research/opening_rank1_longitudinal/delayed_outcomes.py` | `6b98058a97a0` / 6485B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_longitudinal/pipeline.py` | `libs/research/opening_rank1_longitudinal/pipeline.py` | `1788336f0dbe` / 8546B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_longitudinal/report.py` | `libs/research/opening_rank1_longitudinal/report.py` | `c5fd957d8b10` / 9966B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_longitudinal/stage_fate.py` | `libs/research/opening_rank1_longitudinal/stage_fate.py` | `b800e0828eae` / 4430B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/opening_rank1_longitudinal/universe_control.py` | `libs/research/opening_rank1_longitudinal/universe_control.py` | `c24eb84d01c9` / 7081B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/__init__.py` | `libs/research/rank1_feature_mart/__init__.py` | `cfe9c18bca63` / 101B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/activation_contract.py` | `libs/research/rank1_feature_mart/activation_contract.py` | `bbf0fb5feee1` / 1709B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/activation_shadow.py` | `libs/research/rank1_feature_mart/activation_shadow.py` | `799dc296d1ce` / 12950B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/builder.py` | `libs/research/rank1_feature_mart/builder.py` | `cc332d9c5811` / 18824B | 위 실측 함수 이동·효과 경계 먼저 |
| `libs/research/rank1_feature_mart/candidates.py` | `libs/research/rank1_feature_mart/candidates.py` | `2042ae42471e` / 5370B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/chart_features.py` | `libs/research/rank1_feature_mart/chart_features.py` | `ca8e355936bd` / 5582B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/contracts.py` | `libs/research/rank1_feature_mart/contracts.py` | `90b8f7ddb0b0` / 811B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/integrity.py` | `libs/research/rank1_feature_mart/integrity.py` | `6b6952a9d1a6` / 4806B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/loaders.py` | `libs/research/rank1_feature_mart/loaders.py` | `9cd0e98b8863` / 10947B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/outcomes.py` | `libs/research/rank1_feature_mart/outcomes.py` | `cc6a77d71b16` / 5963B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/pipeline.py` | `libs/research/rank1_feature_mart/pipeline.py` | `17cc6bef3bb4` / 7441B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/prospective.py` | `libs/research/rank1_feature_mart/prospective.py` | `61894f7646a2` / 12393B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/prospective_contract.py` | `libs/research/rank1_feature_mart/prospective_contract.py` | `10438e66b194` / 1860B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/report.py` | `libs/research/rank1_feature_mart/report.py` | `fa97967675b6` / 4382B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/strategy_alignment_report.py` | `libs/research/rank1_feature_mart/strategy_alignment_report.py` | `868bbb9e370f` / 7965B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/strategy_choice_observation.py` | `libs/research/rank1_feature_mart/strategy_choice_observation.py` | `971c0f86ee41` / 7703B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/rank1_feature_mart/trees.py` | `libs/research/rank1_feature_mart/trees.py` | `6fe790eafc7b` / 7174B | 짧은 단일 책임이면 KEEP_OK |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Codex B 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #12에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-036|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
