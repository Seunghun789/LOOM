# HANDOFF — 2026-09-17 · 세션 #0 (키트 생성)

## 방금 한 것
- LOOM 개발 키트 생성: CLAUDE.md · AGENTS.md · 서브에이전트 8 · 스킬 10 · 커맨드 8 · 훅 4 · 카드 107 · docs 00~07 · harness

## 다음 할 일 (우선순위 순)
1. 이 폴더에서 `git init && git add -A && git commit -m "chore: LOOM kit v0.1"`
2. Claude Code 실행 → `/start H-001` → `/build H-001`
3. H-002 · H-004 (같은 세션에서 가능, S 크기)
4. H-003 훅 확인 — 새 세션을 열어 이 HANDOFF가 자동 주입되는지 본다

## 주의
- uv가 없으면 먼저 설치: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- 훅은 pyproject.toml이 생기기 전에는 조용히 건너뛴다 (정상)
- `docs/03_MILESTONES.md §1`의 일정 충돌(PRISM 스파이크 vs LOOM 단축)을 오너가 결정해 DECISIONS.md에 기록

## 열린 질문 (오너 결정 필요)
- PRISM 40h 스파이크 위치 — (A) 12월 M7 이후 (B) M2 기간 주 5세션 병행
- ADR-002 에이전트 API — C-108 착수 시 확정

## 컨텍스트 메모
- 아직 코드 없음. public 이름 없음
