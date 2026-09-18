---
description: 세션 시작 — 인계 확인, 다음 카드 선택, 상태를 doing으로
allowed-tools: Read, Bash(python3 tools/progress.py:*), Bash(uv run python tools/progress.py:*), Bash(git status:*)
---

LOOM 세션을 시작한다. 스킬 `loom-session`의 §시작 절차를 따른다.

1. `state/HANDOFF.md`의 "다음 할 일"과 "주의"를 3줄로 요약해 보여준다 (SessionStart 훅이 이미 주입했으면 다시 읽지 않는다)
2. `python3 tools/progress.py --next --limit 5` 결과를 보여준다
3. 인자가 있으면 그 카드를, 없으면 HANDOFF의 추천 카드를 선택한다: $ARGUMENTS
4. 선택한 카드의 §1 목표·§6 수용 테스트만 보여주고, `python3 tools/progress.py --set <ID> doing`
5. 컨텍스트 계획을 한 줄로: "읽을 파일 N개 · 예상 서브에이전트 호출: planner → test-writer → module-builder → reviewer"
6. 오너의 "진행" 확인을 기다린다
