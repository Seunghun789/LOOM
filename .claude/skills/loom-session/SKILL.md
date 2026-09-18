---
name: loom-session
description: LOOM 개발 세션의 시작·종료·인계(HANDOFF) 프로토콜. 세션을 시작하거나 끝낼 때, 컨텍스트가 60%를 넘었을 때, 컴팩트 직후 이어서 작업할 때 사용.
---

# LOOM 세션 프로토콜

긴 개발을 **짧은 세션의 연속**으로 만든다. 세션 사이의 기억은 모델이 아니라 파일(HANDOFF·registry·카드·git)에 있다.

## §시작
1. SessionStart 훅이 HANDOFF 앞 50줄과 다음 카드 목록을 주입한다. **HANDOFF를 다시 Read하지 않는다**
2. 카드 1장 선택 → `python3 tools/progress.py --set <ID> doing`
3. 카드 §7 "읽을 것"을 확인하고 **그 목록만** 읽을 계획을 선언한다
4. 컨텍스트 여유 확인: `/context` (Claude Code 내장). 이미 30% 이상이면 `/clear` 후 재시작

## §진행 중 규칙
- 메인 세션은 조정만. 조사는 researcher, 테스트는 test-writer, 구현은 module-builder, 검사는 reviewer
- 서브에이전트 결과는 요약만 받는다. 전체 코드를 메인으로 붙여넣지 않는다
- 60% 도달 → 새 작업 시작 금지 → §종료
- 막히면 20분 이상 붙잡지 않는다: status `blocked`, HANDOFF에 막힌 지점·시도·가설 기록

## §종료
1. 검증 3종: `uv run pytest -q` · `uv run ruff check` · `uv run lint-imports`
2. registry status 갱신 (`review` 또는 `done`)
3. doc-keeper → HANDOFF 덮어쓰기 (아래 형식)
4. 커밋: `feat(<sector>): <ID> <요약>`
5. `/clear`

## §HANDOFF 형식 (state/HANDOFF.md, ≤50줄, 매번 덮어씀)
```markdown
# HANDOFF — <YYYY-MM-DD HH:MM> · 세션 #<N>

## 방금 한 것
- <ID> <제목>: <상태> — <핵심 결과 한 줄> (테스트 N개)

## 다음 할 일 (우선순위 순)
1. /start <ID> — <왜 이것>
2. <ID>

## 주의 (다음 세션이 반드시 알아야 할 것)
- <예: E-501 HybridIndex.search의 filters 키는 'etype'으로 확정 (계약 §6 query와 다름 — ADR-004 대기)>

## 열린 질문 (오너 결정 필요)
- <질문> — 선택지 A/B

## 컨텍스트 메모
- 이번 세션에서 새로 추가된 public 이름: <sector>.public: <names>
- 추가 의존성: <pkg>
```

## §컴팩트 후 재개
PreCompact 훅이 `state/.compact_snapshot.md`를 남긴다. 컴팩트 직후에는:
1. 스냅샷의 doing 카드 ID 확인
2. 해당 카드 §6만 다시 읽고 `git diff --stat`으로 진행 위치 파악
3. HANDOFF가 스냅샷보다 오래됐으면 먼저 HANDOFF 초안 갱신
