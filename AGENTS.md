# AGENTS.md — LOOM에서 일하는 모든 에이전트의 규칙

> 도구 중립 문서다. Claude Code(CLAUDE.md가 이 파일을 import), Codex, Gemini CLI 등 어떤 코딩 에이전트든 이 파일을 따른다.
> Claude Code 전용 설정(서브에이전트·스킬·훅)은 `.claude/`에 있다.

## 1. 역할 체계

LOOM 개발은 **한 명의 사람(오너)**과 **역할이 나뉜 에이전트들**이 한다. 한 대화(메인 세션)는 오케스트레이터이고, 실제 작업은 서브에이전트에 위임해 메인 컨텍스트를 작게 유지한다.

| 역할 | 파일 | 하는 일 | 하지 않는 일 | 모델 |
|---|---|---|---|---|
| **오너 (사람)** | — | 카드 우선순위 결정, 게이트 판정, ADR 승인, 온톨로지·운영기준 도메인 판단 | — | — |
| **오케스트레이터** (메인 세션) | CLAUDE.md | 카드 선택·서브에이전트 호출 순서·결과 통합·HANDOFF 작성 | 대량 파일 읽기, 긴 구현 | sonnet |
| **planner** | `.claude/agents/planner.md` | 카드를 작업 단계로 쪼개고, 필요한 계약·public 목록을 확정 | 코드 작성 | sonnet |
| **test-writer** | `.claude/agents/test-writer.md` | 카드 §6 수용 테스트를 **먼저** pytest로 작성 (실패 상태로) | 구현 코드 작성 | sonnet |
| **module-builder** | `.claude/agents/module-builder.md` | 테스트를 통과시키는 최소 구현, public.py 반영 | 계약 변경, 다른 섹터 내부 열람 | sonnet |
| **reviewer** | `.claude/agents/reviewer.md` | 계약 준수·경계·테스트 품질·300줄 규칙·provenance 검사, 수정 목록 반환 | 직접 대규모 수정 | sonnet |
| **contract-guardian** | `.claude/agents/contract-guardian.md` | 계약 변경 ADR 검토, import-linter 설정 관리 | 기능 구현 | sonnet |
| **eval-runner** | `.claude/agents/eval-runner.md` | 평가 하네스 실행·지표 비교·회귀 판정 리포트 | 모델·프롬프트 임의 수정 | sonnet |
| **researcher** | `.claude/agents/researcher.md` | 라이브러리 API·버전 확인, 긴 문서 요약 (읽기 전용) | 파일 수정 | sonnet |
| **doc-keeper** | `.claude/agents/doc-keeper.md` | README·HANDOFF·PROGRESS·learning 노트 정리 | 코드 수정 | sonnet (가벼운 작업은 haiku 가능) |

**위임 원칙**
- 파일 5개 이상을 읽어야 하는 조사 → `researcher`
- 테스트 작성과 구현은 **다른 서브에이전트**가 한다 (테스트가 구현에 맞춰 느슨해지는 것을 막는다)
- 리뷰는 구현자가 아닌 `reviewer`가 한다
- 서브에이전트는 결과를 **요약(≤30줄) + 변경 파일 목록**으로만 돌려준다

## 2. 작업 단위 — 모듈 카드

- 모든 작업은 `modules/cards/<ID>.md` 카드 한 장에서 시작한다. 카드 밖 작업은 하지 않는다
- 카드가 모호하면 구현하지 말고 `planner`가 **질문 목록**을 만들어 오너에게 올린다
- 카드 상태 흐름: `todo → doing → review → done` (막히면 `blocked` + HANDOFF에 사유)
- 카드에 없는 개선 아이디어는 `state/DECISIONS.md` 하단 "아이디어" 섹션에 한 줄로만 남긴다

## 3. 코딩 규칙

| 영역 | 규칙 |
|---|---|
| 언어 | Python 3.12, 타입 힌트 필수, `from __future__ import annotations` |
| 모델 | pydantic v2 `BaseModel`. dataclass는 내부 전용 값 객체에만 |
| 포트 | 저장소·LLM·임베더·이벤트는 `typing.Protocol`. 함수는 포트를 **인자로** 받는다 |
| 파일 크기 | 파일 ≤300줄, 함수 ≤50줄. 넘으면 분할 |
| 이름 | 모듈 snake_case, 클래스 PascalCase, 엔티티 속성·관계 camelCase (NGSI-LD) |
| 오류 | 도메인 예외는 섹터별 `errors.py`. 빈 `except:` 금지 |
| 난수 | `numpy.random.default_rng(seed)` / `random.Random(seed)` 인스턴스만 |
| 시간 | UTC aware datetime만. `loom.core.timeutil.utcnow()` |
| 로깅 | `logging.getLogger(__name__)`. print 금지 (CLI 출력은 rich) |
| 프롬프트 | `src/loom/<sector>/prompts/*.md` 파일로 분리, 첫 줄에 `<!-- prompt: name v1 -->` |
| LangGraph | 상태는 `TypedDict`, 리듀서는 `Annotated[..., operator.add]`. 그래프 빌더 함수는 `build_*_graph` 이름. 컴파일된 그래프는 모듈 전역에 두지 않는다 |
| LangChain | 도구는 `@tool` + args_schema. 반환은 JSON 직렬화 가능한 dict. 구조화 출력은 `with_structured_output` |
| 의존성 | `uv add <pkg>`. 무거운 선택 의존성(docling·torch·open3d)은 optional extra로 |
| 커밋 | `feat(<sector>): <ID> <요약>` / `test(...)` / `docs(...)` / `chore(harness)`. 카드 1장 = 커밋 1~3개 |

## 4. 테스트 규칙
- `docs/02_CONTRACTS.md` §14를 따른다
- 카드 §6의 항목 이름이 테스트 함수 이름이 된다
- LangGraph 그래프 테스트: fake 모델 + 작은 픽스처로 **노드 방문 순서와 최종 상태**를 검증한다
- 구조화 출력 테스트: fake 모델이 JSON 문자열을 돌려주게 하고 파싱 결과를 검증한다
- 스냅샷이 필요하면 `tests/<sector>/fixtures/*.expected.json`

## 5. 완료 정의 (모든 카드 공통)
1. 카드 §6 수용 테스트 전부 통과
2. `uv run pytest -q` · `uv run ruff check` · `uv run lint-imports` 통과
3. 섹터 `public.py` 반영, 섹터 `README.md`(≤60줄) 갱신
4. `modules/registry.yaml` status 갱신 → `uv run python tools/progress.py`
5. `state/HANDOFF.md` 갱신 (다음 세션이 이 파일만 읽고 이어갈 수 있게)
6. 카드에 학습 패턴이 있으면 `learning/<패턴ID>.md` 노트 5~15줄

## 6. 금지
- 계약 문서를 코드보다 나중에 고치는 것 (계약이 먼저)
- 다른 섹터 내부 import (`public.py`만)
- 실제 회사·공장 데이터 사용
- 모델 ID 하드코딩, API 키 커밋
- 테스트를 통과시키려고 테스트를 약화시키는 것 (reviewer가 거부)
- 한 세션에서 두 섹터 동시 수정 (조립 카드 M12 제외)
