# D01 — Codex B 실행 규칙

> [CURRENT](docs/refactor/work_orders/CURRENT.md) 우선 → [D00](docs/ENGINEERING_DELIVERY_POLICY.md) 공통 계약. D00은 변경·충돌·안전 판단 때만 재독.

- **브랜치:** `work/p15-b-operator-structure-20261022`; 로컬 `C:\Users\홍훈\Agentra-P15\dev-b` 또는 클라우드 checkout. ROOT·checkout·origin HEAD 확인. 신규 브랜치/force push 금지.
- **개발:** CURRENT의 **Codex B 개발** RF 전부를 소유권 범위에서 진행. 차단된 RF는 BLOCKED로 인계하고 나머지 계속. normal/-O·위험 표적 회귀·UI patchnotes JSON/MD는 D00 준수.
- **상대 검증:** CURRENT의 **Codex B 독립 검증** 링크(`verification/claude/`, Claude 작성 RF)를 별도 read-only 세션에서 exact SHA 검증. 자기 변경 self PASS 금지, 상대 CLI 직접 호출 금지.
- **인수인계:** 자기 브랜치 `docs/refactor/work_orders/HANDOFF_B.md` **최신 회차 10~20줄만 유지**, 이전 기록은 Git 이력. 코드 후보 SHA·normal/-O·peer verdict·BLOCKED·CI·GPT_ACTION_REQUIRED·push 재조회 결과만 간결히 기재. RF/STATUS 공용 상태는 GPT가 관리. 빈 영수증 커밋 금지.
- **통합:** 독립 PASS한 Claude RF만 별도 승인 경로·writer/CAS·exact integration SHA normal/-O·hosted CI 확인. GPT만 done. Quick Fix는 D00의 사전 명시 승인에 한함.
- **안전:** main/실거래/안전 계약/CI 오라클 무승인 변경 금지. 불가한 일은 NOT_RUN/UNKNOWN/BLOCKED로 보고.
