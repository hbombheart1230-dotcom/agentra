# RF-037 — SOURCE 실제 함수·TARGET 상세설계

**입력 고정:** `integration/p1.5@49cd60c4744c23ca556dbb633b197dbce4810d53`, RF 원본 `docs/refactor/plan/queue/01_PENDING/UNASSIGNED/RF-037.md`, FILE_COVERAGE CSV blob `b46bcb1f29ed3c0a133b059d690173c195c81bf9`. **독점:** Claude A 구현 / Codex B read-only. 소유 21개 경로.

## 1. 실측 함수 단위 분석 / 배치

이 RF의 Python 함수 본문 실측 없음(원본 Python 부재 또는 읽을 large 함수 없음). 유효한 target 위치의 문서/스크립트/설정/작은 단일 책임 코드는 정당한 KEEP. 새 함수명을 추측하여 개발자가 구현하도록 만들지 않는다.

## 2. 전체 파일별 SOURCE / 기본 목표 TARGET / KEEP·MOVE

기존의 목표 폴더/공개 경로가 맞으면 KEEP_OK 즉시 승인. 함수 이동 목적지는 위 표의 실제 목표를 사용하며 원본 경로는 호환 wrapper 유지.

| SOURCE_PATH | 기본 TARGET_PATH | Git SHA/bytes | 처리조건 |
|---|---|---|---|
| `libs/research/alpha_competition/__init__.py` | `libs/research/alpha_competition/__init__.py` | `abc9272ffd15` / 103B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/alpha_competition/candidates.py` | `libs/research/alpha_competition/candidates.py` | `69276cf5f6e8` / 5487B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/alpha_competition/contracts.py` | `libs/research/alpha_competition/contracts.py` | `922d3a007a61` / 1753B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/alpha_competition/evaluator.py` | `libs/research/alpha_competition/evaluator.py` | `ef3ec090df5f` / 6366B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/alpha_competition/hypotheses.py` | `libs/research/alpha_competition/hypotheses.py` | `b808e49d5e6c` / 2798B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/alpha_competition/pipeline.py` | `libs/research/alpha_competition/pipeline.py` | `18a6bba85ead` / 3966B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/alpha_competition/report.py` | `libs/research/alpha_competition/report.py` | `fec74bdb417e` / 4608B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha/__init__.py` | `libs/research/structural_alpha/__init__.py` | `5413090c0529` / 93B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha/contracts.py` | `libs/research/structural_alpha/contracts.py` | `39263c05e3f9` / 1160B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha/evaluator.py` | `libs/research/structural_alpha/evaluator.py` | `288d0891516f` / 6980B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha/features.py` | `libs/research/structural_alpha/features.py` | `6baf71aaf455` / 5879B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha/pipeline.py` | `libs/research/structural_alpha/pipeline.py` | `3ec2f93b0944` / 4616B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha/report.py` | `libs/research/structural_alpha/report.py` | `8236ef38a0ef` / 3906B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha/strategies.py` | `libs/research/structural_alpha/strategies.py` | `7be2a46adbae` / 5970B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha/windows.py` | `libs/research/structural_alpha/windows.py` | `56918e4d0ec5` / 3231B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha_batch2/__init__.py` | `libs/research/structural_alpha_batch2/__init__.py` | `a75241914235` / 93B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha_batch2/contracts.py` | `libs/research/structural_alpha_batch2/contracts.py` | `cbe8993aa011` / 656B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha_batch2/features.py` | `libs/research/structural_alpha_batch2/features.py` | `a048e82717e9` / 4443B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha_batch2/pipeline.py` | `libs/research/structural_alpha_batch2/pipeline.py` | `04b98f920dcc` / 5015B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha_batch2/report.py` | `libs/research/structural_alpha_batch2/report.py` | `9c90d3cb6005` / 3314B | 짧은 단일 책임이면 KEEP_OK |
| `libs/research/structural_alpha_batch2/strategies.py` | `libs/research/structural_alpha_batch2/strategies.py` | `9da94362b140` / 7098B | 위 실측 함수 이동·효과 경계 먼저 |

## 3. 개발 실행·리뷰·DONE

1. 위치 정확·단일 역할·짧거나 합당한 effect/CLI 경계는 `KEEP_OK|PATH|한 줄 이유|BLOB`으로 종결. 같은 blob 신규 테스트/peer 금지.
2. 실제 `MOVE_BODY`만 SOURCE에서 계산 구현을 삭제하고 TARGET Owner에 실제 함수를 추가. 원명 thin wrapper와 use-time monkeypatch·호출 순서를 유지. 기존 같은 Owner 존재하면 재사용, 이중 구현 금지.
3. 바뀐 경계의 old/new fake/tmp fixture 기반 **정상 targeted unittest/pytest 1회 exit0**. live LLM·Broker·주문/Guard/UEF·운영 State/DB/파일 쓰기 금지. 한 항목 차단은 다른 과제 중지 사유 아님.
4. Claude A 소유 branch code/test만 commit/push; source와 target blob, 원본 LOC 감소, 이동 함수, 정당 KEEP 사유, TEST_EXIT를 #11에 기록. C04 최소 묶음 통합, C05 기존 DONE 이력 보존 + 미완료 TARGET_GAP만 다음 구현 배정.

`RF=RF-037|SOURCE_BLOB|FUNCTION_MOVES|TARGET_BLOBS|KEEP_REASON|BEFORE_AFTER_LOC|NORMAL_EXIT|PUSH_SHA|INTEGRATION_SHA|TARGET_VERDICT`
