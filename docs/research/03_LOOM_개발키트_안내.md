# LOOM 개발 키트 v0.1 안내 (2026-09-17)

- 위치: `~/Desktop/LOOM` (이 폴더가 저장소 루트. VS Code에서 폴더 열기 → 터미널에서 `claude`)
- 목적: `docs/research/02_LOOM_제조AI_재조립_청사진_로드맵.md`를 Claude Code(Sonnet)로 긴 기간에 걸쳐 모듈 단위 구현·조립하기 위한 운영 키트

## 구성
| 구분 | 내용 |
|---|---|
| 메모리 | `CLAUDE.md`(자동 로드) · `AGENTS.md`(도구 중립 역할·코딩 규칙) |
| 서브에이전트 8 | planner · test-writer · module-builder · reviewer · contract-guardian · eval-runner · researcher · doc-keeper |
| 스킬 10 | loom-session · module-build · contracts · langchain · langgraph · eval · plant · ontology · physics · harness |
| 커맨드 8 | /start · /build · /review · /handoff · /next · /gate · /parallel · /learn |
| 훅 4 | SessionStart(HANDOFF 주입) · PostToolUse(ruff·300줄 피드백) · PreCompact(스냅샷) · Stop(리마인더) |
| 문서 | 00 제품 · 01 아키텍처 · **02 계약(조립 접점)** · 03 마일스톤 · 04 모듈 인덱스 · 05 컨텍스트 전략 · 06 학습 트랙 · 07 평가 · ADR 3 · research/ 3 |
| 모듈 카드 | 107장 (P0 80) · `modules/registry.yaml` 단일 진실 소스 · `tools/progress.py` |
| 하네스 | `harness/run_card.sh`(claude -p) · `orchestrate.py`(의존성 파동·worktree 병렬) |

## 단축 경로
M0 하네스 → M1 계약(S0) → M2 가상 실증공장 → M3 연결(S2) → M4 온톨로지(S3) → **M5 근거 질의 G1** → **M6 운영 G2** → M7 리포트(S9) → **M8 에이전트 폐루프 G3** → M9 PRISM 바인딩 → M10 물리 → M11 도면 → **M12 조립 G4**
- P0만: 100세션. G1까지 60.5세션. 주 10세션 가정 시 교육 기간 제외하고 G1 ≈ 11월 말, G4 ≈ 2027년 1월 말
- G1 기준: spine20 원인 1순위 ≥ 11/15 · 근거경로 100% · 버전 테스트 1/1 · 근거부족 3/3

## 학습 매핑
- 개발 층 H1~H12: CLAUDE.md·커맨드·스킬·서브에이전트·훅·Plan mode·병렬·헤드리스·Agent SDK·MCP·worktree·평가 하네스
- 제품 층 L1~L15: 구조화 출력·도구·리트리버·StateGraph·checkpointer·interrupt·Send·서브그래프·Supervisor·Swarm·반성·트레이싱·MCP adapters·Store·스트리밍

## 열린 결정
- PRISM 40h 스파이크·Isaac 실증과 LOOM 단축 일정 충돌 — (A) 스파이크 12월로 이동 (B) M2 기간 병행
- ADR-002 에이전트 API(create_agent vs create_react_agent) — C-108 착수 시 설치 버전 확인 후 확정
