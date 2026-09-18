# 05 · CONTEXT STRATEGY — Sonnet으로 긴 개발을 끊기지 않게

## §1 문제
- 107개 모듈·132세션짜리 개발은 어떤 모델의 컨텍스트 창에도 한 번에 들어가지 않는다
- 한 대화를 길게 끌면 앞의 결정이 흐려지고(컴팩트 손실), 토큰 비용이 선형 이상으로 늘고, 실수(다른 섹터 내부 수정)가 늘어난다
- 해법은 "더 긴 컨텍스트"가 아니라 **"짧은 세션 + 외부화된 기억 + 좁은 읽기 범위"**다

## §2 다섯 가지 장치

| # | 장치 | 무엇이 기억을 대신하나 | 파일 |
|---|---|---|---|
| 1 | **계약 우선** | 모듈 사이의 약속을 코드가 아니라 문서로 고정 → 다른 모듈을 안 읽어도 됨 | `docs/02_CONTRACTS.md`, `src/loom/*/public.py` |
| 2 | **카드 = 자기완결 지시서** | 목표·인터페이스·테스트·읽을 것·금지를 한 장에 | `modules/cards/*.md` |
| 3 | **상태 외부화** | 진행·인계·결정을 파일로 | `modules/registry.yaml`, `state/HANDOFF.md`, `state/DECISIONS.md`, git |
| 4 | **서브에이전트 격리** | 긴 읽기·구현·리뷰를 별도 컨텍스트에서, 요약만 메인으로 | `.claude/agents/*.md` |
| 5 | **점진 공개(progressive disclosure)** | 스킬은 description만 상시, 본문은 필요할 때 / CLAUDE.md는 짧게, 나머지는 포인터 | `.claude/skills/*/SKILL.md`, `CLAUDE.md` |

## §3 컨텍스트 예산표 (Sonnet, 한 세션)

| 항목 | 목표 토큰 | 메모 |
|---|---|---|
| 시스템 + 도구 정의 | (고정) | Claude Code가 관리 |
| CLAUDE.md + AGENTS.md | ≤ 4K | 150줄 + 130줄 유지. 늘면 포인터로 이동 |
| 스킬 description 전부 | ≤ 1.5K | 10개 × 짧은 한 문단 |
| SessionStart 주입 (HANDOFF 50줄 + next 5줄 + git 15줄) | ≤ 2K | |
| 카드 1장 | ≤ 2K | |
| 계약 문서 해당 절만 | ≤ 3K | 전체(≈10K)를 읽지 않는다 |
| 의존 public.py | ≤ 2K | 섹터당 ≤80줄 유지 |
| 로드된 스킬 본문 1~2개 | ≤ 4K | |
| 서브에이전트 결과 요약 4회 | ≤ 4K | 각 ≤30줄 |
| **작업 여유** | 나머지 | 여기서 테스트 출력·diff·대화 |

**경보선**: `/context`로 확인. 50% → 새 카드 시작 금지. 60% → `/handoff` 후 `/clear`. 컴팩트는 **사고 발생 시 복구 수단**이지 계획된 운영 방식이 아니다.

## §4 읽기 규칙 (위반이 가장 흔한 실수)
1. 카드 §7 목록 밖 파일을 열어야 할 것 같으면 → `researcher`에게 "X가 어떻게 동작하는지 20줄로" 위임
2. 다른 섹터 코드를 이해해야 하면 → 그 섹터 `public.py`와 `README.md`(≤60줄)만. 부족하면 **README를 고치는 카드**를 만든다
3. 데이터 파일은 `head -20`, 로그는 `tail -40`, 테스트는 `-q`
4. 대형 diff는 `git diff --stat` 먼저, 필요한 파일만 `git diff -- <path>`
5. 같은 파일을 한 세션에서 두 번 Read하지 않는다 (Edit 후 재확인 불필요)

## §5 쓰기 규칙
1. 파일 ≤300줄 (훅이 알림), 함수 ≤50줄 → 다음 세션이 부분만 읽을 수 있게
2. 섹터 `README.md` ≤60줄: "이 섹터가 여는 것 / 핵심 흐름 / 알려진 한계"
3. `public.py` 상단 docstring에 공개 이름 목록과 한 줄 설명 → 다른 섹터가 이것만 읽고 쓸 수 있게
4. 결정은 코드 주석이 아니라 `state/DECISIONS.md` 한 줄 + 필요시 ADR

## §6 세션 유형별 운영

| 유형 | 예 | 메인 세션 역할 | 서브에이전트 |
|---|---|---|---|
| **S 카드 묶음** | C-101 + C-102 | 직접 TDD 가능 | reviewer만 |
| **M 카드** | C-104, E-504 | 오케스트레이터 | planner → test-writer → module-builder → reviewer |
| **조사** | LangGraph interrupt 재개 방식 확인 | 질문만 | researcher |
| **계약 변경** | Answer에 필드 추가 | ADR 초안 | contract-guardian |
| **게이트** | G1 | 판정표 | eval-runner |
| **병렬 파동** | N-302~N-305 | 계획만 (`/parallel`) | 각 worktree에서 헤드리스 |
| **학습 복습** | L6 | 퀴즈 | researcher(코드 발췌) |

## §7 세션이 망가졌을 때
| 증상 | 조치 |
|---|---|
| 모델이 계약과 다른 이름을 쓰기 시작 | 멈추고 카드 §4와 계약 절을 다시 보여준 뒤, 안 되면 `/handoff` → `/clear` |
| 테스트를 약화시키려 함 | reviewer 호출, 거부. 테스트가 정말 틀렸으면 test-writer에게 근거와 함께 |
| 같은 오류를 3회 반복 | status `blocked`, HANDOFF에 오류·시도·가설, 새 세션에서 researcher부터 |
| 컴팩트가 일어남 | 스킬 loom-session §컴팩트 후 재개 |
| 다른 섹터 내부를 수정함 | `git checkout -- <path>`, lint-imports 확인 |

## §8 헤드리스·병렬로 넓히는 시점
1. 대화형 M 카드 3장 이상이 **리뷰 1회 이내로** 통과했다 → 카드 품질 검증됨
2. 훅·서브에이전트 설정 수정이 1주일간 없었다 → 운영 장치 안정
3. 그때부터 S 카드는 `harness/run_card.sh`, 의존 없는 카드 묶음은 `orchestrate.py --parallel 2`
4. 헤드리스 결과는 **항상 사람이 diff 확인 후 done**. registry의 `review` 상태가 그 대기열이다
