---
description: 세션 종료 — 검증, 상태 갱신, HANDOFF 작성, 커밋
allowed-tools: Read, Write, Edit, Bash(uv run pytest:*), Bash(uv run ruff:*), Bash(uv run lint-imports:*), Bash(python3 tools/progress.py:*), Bash(git add:*), Bash(git commit:*), Bash(git diff:*), Bash(git status:*)
---

세션을 끝낸다. 스킬 `loom-session`의 §종료 절차.

1. `uv run pytest -q` · `uv run ruff check` · `uv run lint-imports` (pyproject.toml이 없으면 건너뜀). 실패하면 status를 `doing`으로 두고 HANDOFF에 실패 내용 기록
2. 통과한 카드는 오너 확인 후 `done`, 아니면 `review`
3. `doc-keeper` 서브에이전트: HANDOFF·PROGRESS·DECISIONS·learning 갱신
4. `git add -A && git commit -m "<type>(<sector>): <ID> <요약>"`
5. 마지막 출력: "다음 세션: /start <ID>" 한 줄과 `/clear` 권장
