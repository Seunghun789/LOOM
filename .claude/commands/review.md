---
description: 현재 변경분을 reviewer 서브에이전트로 검사
argument-hint: [카드 ID]
---

`reviewer` 서브에이전트에게 `git diff` 기준으로 카드 `$ARGUMENTS`의 체크리스트 검사를 맡긴다.
결과의 MUST 항목만 보여주고, 고칠지 오너에게 묻는다.
