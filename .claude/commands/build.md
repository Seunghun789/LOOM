---
description: 카드 1장을 TDD 서브에이전트 파이프라인으로 구현 (planner → test-writer → module-builder → reviewer)
argument-hint: <카드 ID, 예: C-104>
---

카드 `$ARGUMENTS`를 구현한다. 스킬 `loom-module-build`를 따른다.

**메인 세션은 오케스트레이터다. 직접 구현하지 말고 서브에이전트에 위임하고, 각 결과는 요약만 받는다.**

1. `planner` 서브에이전트: `modules/cards/$ARGUMENTS.md` → PLAN. BLOCKER가 있으면 멈추고 오너에게 질문
2. `test-writer` 서브에이전트: PLAN과 카드로 테스트 작성 → FAIL 확인
3. `module-builder` 서브에이전트: 테스트 통과 구현. CONTRACT CONFLICT/TEST ISSUE면 멈추고 보고
4. `reviewer` 서브에이전트: CHANGES면 MUST 항목만 module-builder에 재위임 (최대 2회)
5. APPROVE 후 `python3 tools/progress.py --set $ARGUMENTS review`
6. 결과 요약 표: 파일 · 테스트 수 · 추가 의존성 · 학습 패턴
7. 카드 크기가 S이고 컨텍스트 여유(50% 미만)가 있으면 같은 섹터의 다음 S 카드를 제안, 아니면 `/handoff` 제안
