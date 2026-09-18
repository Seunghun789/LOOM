---
description: 의존 없는 카드 여러 장을 git worktree로 병렬 진행하는 계획 수립
argument-hint: <카드 ID 목록, 예: N-302 N-303 N-304>
---

카드 `$ARGUMENTS`를 병렬로 진행하는 계획을 세운다. 스킬 `loom-harness` §worktree.

1. 카드들 사이에 의존·같은 파일 수정이 없는지 확인 (있으면 병렬 불가 사유 보고)
2. 카드마다 명령 생성:
   `git worktree add ../loom-<ID> -b card/<ID>` 후 그 폴더에서 `harness/run_card.sh <ID>`
3. 머지 순서와 충돌 가능 파일(`public.py`, `conftest.py`, `pyproject.toml`) 경고
4. 실행은 하지 않는다. 오너가 터미널에서 실행한다
