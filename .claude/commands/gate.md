---
description: 마일스톤 게이트 판정 (G1~G4)
argument-hint: <G1|G2|G3|G4>
---

게이트 `$ARGUMENTS`를 판정한다.

1. `docs/03_MILESTONES.md`에서 `$ARGUMENTS`의 필수 카드 목록과 수치 기준을 읽는다
2. 필수 카드 status가 모두 done인지 `python3 tools/progress.py`로 확인
3. `eval-runner` 서브에이전트로 해당 평가 스위트 실행 (실 LLM 여부는 오너에게 먼저 묻는다)
4. 판정표: 기준 · 결과 · PASS/FAIL
5. PASS면 `state/DECISIONS.md`에 게이트 통과 기록, `docs/demo/`에 스크린샷 체크리스트 안내
6. FAIL이면 eval-runner의 "다음 카드 제안"을 새 카드 초안으로 `modules/cards/_proposed/`에 작성 (registry에는 오너 승인 후 추가)
