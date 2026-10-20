# LOOM — 개인용 제조 운영 지능 스택 (개발 키트 v0.1)

> 4계층 구조(물리 → 트윈 → 온톨로지 → 운영판단)를 재조립해, **Claude Code(Sonnet)로 긴 기간에 걸쳐 모듈 단위로 만들고 조립하는** 프로젝트.
> 동시에 하네스·서브에이전트·오케스트레이션·LangChain·LangGraph를 **실제 카드 구현으로** 익힌다.

## 이 키트에 들어 있는 것

| 구분 | 파일 | 수 |
|---|---|---|
| 프로젝트 메모리 | `CLAUDE.md` (Claude Code 자동 로드) · `AGENTS.md` (도구 중립 규칙) | 2 |
| 서브에이전트 | `.claude/agents/*.md` — planner · test-writer · module-builder · reviewer · contract-guardian · eval-runner · researcher · doc-keeper | 8 |
| 스킬 | `.claude/skills/*/SKILL.md` — session · module-build · contracts · langchain · langgraph · eval · plant · ontology · physics · harness | 10 |
| 슬래시 커맨드 | `.claude/commands/*.md` — /start · /build · /review · /handoff · /next · /gate · /parallel · /learn | 8 |
| 훅 | `.claude/settings.json` + `tools/hooks/*.sh` — SessionStart · PostToolUse · PreCompact · Stop | 4 |
| 설계 문서 | `docs/00_PRODUCT` · `01_ARCHITECTURE` · **`02_CONTRACTS`** · `03_MILESTONES` · `04_MODULE_INDEX` · `05_CONTEXT_STRATEGY` · `06_LEARNING_TRACK` · `07_EVAL` · `adr/` | 8 + ADR 3 |
| 모듈 카드 | `modules/registry.yaml` (단일 진실 소스) · `modules/cards/*.md` | **107** (P0 80) |
| 진행·인계 | `state/PROGRESS.md` (생성물) · `state/HANDOFF.md` · `state/DECISIONS.md` | 3 |
| 헤드리스 하네스 | `harness/run_card.sh` · `harness/orchestrate.py` · `harness/prompts/` | 3 |
| 도구 | `tools/progress.py` (표준 라이브러리만) | 1 |
| 학습 | `learning/_TEMPLATE.md` | 1 |
| 배경 연구 | `docs/research/` — 01 E8 분석 · 02 LOOM 청사진·로드맵 · 03 키트 안내 | 3 |

## 5분 시작

```bash
cd ~/Desktop/LOOM          # VS Code: 파일 > 폴더 열기 → 터미널
git init && git add -A && git commit -m "chore: LOOM kit v0.1"
python3 tools/progress.py --next          # → H-001
claude                                    # Claude Code 실행 (모델: Sonnet)
```
Claude Code 안에서:
```
/start H-001
/build H-001
/handoff
/clear
/start            ← 다음 카드
```

## 작업이 흐르는 방식

```
registry.yaml ──► /start ──► 카드 1장 ──► /build
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            ▼                            ▼                            ▼
        planner  ──PLAN──►  test-writer ──RED──►  module-builder ──GREEN──►  reviewer
        (계획)              (테스트 먼저)          (최소 구현)               (계약·경계 검사)
                                                                            │
            ┌───────────────────────────────────────────────────────────────┘
            ▼
       /handoff ──► doc-keeper ──► HANDOFF.md · PROGRESS.md · 커밋 ──► /clear
            │
            └── 다음 세션: SessionStart 훅이 HANDOFF를 자동 주입
```

- **한 세션 = 카드 1장**. 기억은 모델이 아니라 파일(HANDOFF·registry·git)에 있다
- 카드끼리는 `docs/02_CONTRACTS.md`와 섹터 `public.py`로만 연결 → 각 카드를 독립 세션에서 만들고 나중에 조립
- 익숙해지면 `harness/orchestrate.py`로 의존성 순서대로 헤드리스·병렬 실행

## 마일스톤 한눈에

| | 결과 | 게이트 |
|---|---|---|
| M0 | 운영 장치가 도는 빈 저장소 | |
| M1 | 계약 코드화 (Entity·포트·Fake LLM) | |
| M2 | 정답지 달린 가상 프레스-용접 라인 20시나리오 | |
| M3 | 적재 + 원천 추적 | |
| M4 | 온톨로지·추출·설비명 매칭 | |
| M5 | **질문 → 근거 경로 답변 + 자동 채점** | **G1** |
| M6 | 알람 → RCA → 승인(interrupt) → 결정 기록 | **G2** |
| M7 | 근거 링크 주간 리포트 | |
| M8 | MCP + 멀티에이전트 폐루프 | **G3** |
| M9~M11 | PRISM 3D 바인딩 · 물리 서로게이트 · 도면 | |
| M12 | 통합 CLI·데모·포트폴리오 | **G4** |

상세: `docs/03_MILESTONES.md`

## 필수 설치
- Python 3.12, [uv](https://docs.astral.sh/uv/), git, Claude Code
- (M1 이후) `ANTHROPIC_API_KEY` — 실 LLM 스위트에서만. 단위 테스트는 키 없이 통과해야 한다
- (선택) Docker — Postgres(C-106)·COLMAP(K-1103)

## 원칙 요약
계약이 먼저 · 섹터 간 `public.py`만 · 모델 ID 하드코딩 금지 · 단위 테스트에 실 LLM 금지 · 모든 값에 provenance · 회사 데이터 반입 금지 · 파일 300줄 · PRISM 규약 우선
