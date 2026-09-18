---
name: loom-module-build
description: 모듈 카드 1장을 계획→테스트→구현→리뷰→인계까지 끝내는 표준 절차(TDD + 서브에이전트 분업). /build 실행 시, 또는 modules/cards/*.md 카드를 구현하라는 요청을 받았을 때 사용.
---

# 모듈 구현 표준 절차

## 0. 전제 확인 (메인 세션, 2분)
- 카드 frontmatter의 `depends`가 모두 done인가? (`python3 tools/progress.py --next`에 카드가 있으면 OK)
- 카드 크기 S → 서브에이전트 생략 가능(메인이 직접 TDD). M → 반드시 분업

## 1. PLAN — planner
```
Task(planner): "modules/cards/<ID>.md 를 PLAN 형식으로. 의존 public 이름 존재 확인 포함"
```
- BLOCKER ≠ 없음 → 오너에게 질문하고 멈춘다
- 생성 파일이 5개 초과이거나 예상 줄 수 합 400 초과 → 카드 분할 제안 (`<ID>a`, `<ID>b`)

## 2. RED — test-writer
```
Task(test-writer): "<PLAN 붙여넣기> 기준으로 tests/<sector>/test_<module>.py 작성, FAIL 확인"
```
- 테스트가 구현 세부(내부 함수명)에 묶이지 않고 **공개 인터페이스**만 검증하는지 메인이 한 번 훑는다

## 3. GREEN — module-builder
```
Task(module-builder): "<ID> 테스트 통과. 카드 §7 밖 파일 열람 금지. BUILD 형식 보고"
```
- CONTRACT CONFLICT → 멈춤 → `docs/adr/ADR-NNN-<slug>.md` 초안(템플릿 `docs/adr/ADR-000-template.md`) → contract-guardian
- TEST ISSUE → test-writer에게 근거와 함께 재위임 (메인이 판정)

## 4. REVIEW — reviewer
```
Task(reviewer): "<ID> git diff 검사"
```
- CHANGES → MUST만 module-builder에 재위임. 최대 2회. 3회째면 blocked + HANDOFF

## 5. INTEGRATE — 메인
- `uv run pytest -q` 전체 · `uv run lint-imports`
- 섹터 `public.py` 새 이름이 다른 섹터 카드의 기대와 맞는지 `docs/04_MODULE_INDEX.md`에서 후속 카드 1~2개 확인
- `python3 tools/progress.py --set <ID> review`

## 6. LEARN — 학습 패턴이 있는 카드만
- `learning/<패턴ID>.md` 5~15줄: "이 카드에서 이 패턴이 한 일 / 코드 위치 / 대안이었다면"

## 크기별 세션 예산 (Sonnet)
| 크기 | 서브에이전트 호출 | 메인 컨텍스트 목표 |
|---|---|---|
| S | 0~2회 (reviewer만 권장) | ≤35% |
| M | 4회 (planner·test-writer·builder·reviewer) | ≤55% |

## 자주 하는 실수
- 메인이 테스트와 구현을 둘 다 쓰고 리뷰까지 스스로 함 → 자기 확증. 분업을 지킨다
- `public.py`를 안 고침 → 다음 섹터 카드가 import 실패
- fake LLM 응답을 구현에 맞춰 억지로 만듦 → 실 LLM 스위트(`-m llm`)에서 무너짐. fake 응답은 **실제 모델이 낼 법한 모양**으로
