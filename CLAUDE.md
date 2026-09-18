# LOOM — Claude Code 프로젝트 메모리

> 이 파일은 매 세션 자동으로 로드된다. **짧게 유지한다(150줄 이내).** 긴 내용은 포인터로만 둔다.

@AGENTS.md

## 1. 한 줄
LOOM은 E8(이에이트)의 4계층 구조(물리 → 트윈 → 온톨로지 → 운영판단)를 재조립한 **개인용 제조 운영 지능 스택**이다. 질문 하나에 **근거와 함께** 답하고, 사람이 승인한 판단을 기록하고, 그 기록으로 다음 판단이 나아진다.

## 2. 지금 어디인가
- 진행 상태: `state/PROGRESS.md` (생성물 — 직접 편집하지 말 것, `modules/registry.yaml`이 원본)
- 지난 세션 인계: `state/HANDOFF.md` (SessionStart 훅이 자동 주입)
- 다음 카드: `uv run python tools/progress.py --next`

## 3. 세션 프로토콜 (반드시)
1. **시작** `/start` — HANDOFF·PROGRESS 확인 → 카드 1장 선택 → registry status `doing`
2. **구현** `/build <ID>` — 스킬 `loom-module-build` 절차: 테스트 먼저(test-writer) → 구현(module-builder) → 리뷰(reviewer)
3. **종료** `/handoff` — 테스트·린트·경계 통과 확인 → registry status `review`/`done` → HANDOFF 갱신 → 커밋
4. **한 세션 = 카드 1장** (S 크기 카드는 같은 섹터에서 최대 3장까지)
5. 컨텍스트 사용량이 60%를 넘으면 새 기능을 시작하지 말고 `/handoff` 후 `/clear`

## 4. 컨텍스트 예산 규칙 (Sonnet 기준)
- **카드의 §7 "읽을 것" 목록 밖의 파일은 열지 않는다.** 필요하면 `researcher` 서브에이전트에 요약을 맡긴다
- 다른 섹터는 `src/loom/<sector>/public.py`만 본다. 내부 파일 금지
- `var/`, `*.csv`, `*.jsonl`, `*.pdf`는 `head -20` 이상 출력 금지
- 테스트는 `uv run pytest -q <경로>`로 좁혀 돌린다. 실패 로그는 마지막 40줄만
- 긴 탐색·문서 조사·코드베이스 검색은 서브에이전트로 위임해 **메인 컨텍스트를 보호**한다
- 자세한 전략: `docs/05_CONTEXT_STRATEGY.md`

## 5. 명령
```bash
uv sync                                   # 의존성
uv run pytest -q                          # 단위 테스트 (LLM·네트워크·DB 없이 통과해야 함)
uv run pytest -q -m integration           # Postgres 필요
uv run ruff check --fix && uv run ruff format
uv run lint-imports                       # 섹터 경계 검사 (docs/02_CONTRACTS.md §1)
uv run python tools/progress.py [--next | --set ID status | --milestone M3]
uv run loom --help                        # M2 이후
uv run streamlit run apps/console/Home.py # M5 이후
```

## 6. 지도
| 경로 | 무엇 |
|---|---|
| `docs/00_PRODUCT.md` | 제품 정의·원칙·섹터·온톨로지 클래스 |
| `docs/01_ARCHITECTURE.md` | 계층·조립 방식·기술 스택 |
| `docs/02_CONTRACTS.md` | **조립 계약 — 타입·포트·경계 규칙 (가장 중요)** |
| `docs/03_MILESTONES.md` | M0~M12 마일스톤·게이트 G1~G4 |
| `docs/04_MODULE_INDEX.md` | 모듈 107개 목록 (생성물) |
| `docs/05_CONTEXT_STRATEGY.md` | 긴 컨텍스트 개발 운영법 |
| `docs/06_LEARNING_TRACK.md` | 하네스·LangChain·LangGraph·서브에이전트·오케스트레이션 학습 매핑 |
| `docs/07_EVAL.md` | 평가 하네스·게이트 판정 |
| `docs/research/` | 배경 연구: E8 분석 · LOOM 청사진·로드맵 · 키트 안내 (필요할 때만 읽기 — 길다) |
| `modules/cards/<ID>.md` | 모듈 카드 = 작업 지시서 |
| `.claude/agents/` | 서브에이전트 8종 |
| `.claude/skills/` | 스킬 10종 (description만 상시 로드, 본문은 필요할 때) |
| `.claude/commands/` | 슬래시 커맨드 |
| `harness/` | 헤드리스 `claude -p` 러너·오케스트레이터 |
| `learning/` | 패턴별 학습 노트 |

## 7. 절대 규칙
- R1. 계약(`docs/02_CONTRACTS.md`)을 코드에서 먼저 바꾸지 않는다. ADR → contract-guardian 리뷰 → 반영
- R2. 섹터 간 import는 `public.py`만 (import-linter가 막는다)
- R3. 모델 ID 하드코딩 금지. `get_chat_model(role)`만
- R4. 단위 테스트에서 실 LLM·네트워크·DB 금지 (`LOOM_LLM_FAKE=1` 기본)
- R5. 모든 값에 provenance. LLM·매칭·추정 결과는 `assumed`
- R6. 회사·실제 공장 데이터 반입 금지. 가상 실증공장·공개 데이터만
- R7. 파일 300줄 초과 금지 → 분할
- R8. PRISM과 충돌하면 PRISM 문서가 우선 (좌표·단위·씬 스키마)
