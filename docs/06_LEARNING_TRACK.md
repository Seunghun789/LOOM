# 06 · LEARNING TRACK — 만들면서 배우는 27개 패턴

> 목표: 최근 유행하는 **하네스 · 서브에이전트 · 오케스트레이션(개발 쪽)**과 **LangChain · LangGraph(제품 쪽)**를 **LOOM 카드를 구현하는 과정에서 자연스럽게** 한 번씩 써 본다.
> 규칙: 패턴이 붙은 카드를 끝내면 `learning/<패턴ID>.md` 노트(템플릿 `learning/_TEMPLATE.md`)를 쓴다. `/learn <ID>`로 복습 퀴즈.

## §0 용어 정리 — 헷갈리는 다섯 단어

| 용어 | LOOM에서의 뜻 | 예 |
|---|---|---|
| **하네스(harness)** | 모델을 감싸서 **루프·도구·컨텍스트·권한·검증**을 제공하는 실행 틀. "모델 + 하네스 = 에이전트" | Claude Code, `claude -p`, Claude Agent SDK / LangChain `create_agent` / 평가 하네스 `loom eval` |
| **서브에이전트** | 부모 에이전트가 **별도 컨텍스트 창**으로 띄우는 전문 에이전트. 결과 요약만 부모에게 돌아온다 | `.claude/agents/test-writer.md` / LangGraph 역할 에이전트 노드 |
| **오케스트레이션** | 여러 에이전트·단계의 **순서·분기·병렬·재시도·종료**를 정하는 것 | `/build` 파이프라인, `orchestrate.py` 파동 / Supervisor 그래프 |
| **LangChain** | 모델·도구·프롬프트·리트리버·에이전트의 **부품과 표준 인터페이스** | `init_chat_model`, `@tool`, `with_structured_output`, `create_agent` |
| **LangGraph** | 상태 기반 **그래프 실행 엔진** — 분기·병렬·영속·사람 개입 | `StateGraph`, `Send`, `interrupt`, checkpointer, Store |

**핵심 대응 관계** — 같은 원리가 두 층에 있다:

| 원리 | 개발 층 (Claude Code) | 제품 층 (LangGraph) |
|---|---|---|
| 역할 분리 | planner / test-writer / builder / reviewer | diagnose / judge / solve / verify |
| 컨텍스트 격리 | 서브에이전트 별도 창 | 서브그래프·역할 에이전트 별도 메시지 |
| 상태 외부화 | HANDOFF · registry · git | checkpointer · Store · EntityStore |
| 사람 개입 | `/start` 확인 · review→done | `interrupt()` → `Command(resume=)` |
| 점진 공개 | 스킬 description → 본문 | 라우터가 필요한 도구만 호출 |
| 병렬 | worktree 병렬 카드 | `Send` 팬아웃 |
| 측정 | 테스트·lint·reviewer | 평가 하네스 |
| 도구 공유 | MCP 클라이언트 | MCP adapters |

---

## §1 개발 층 — Claude Code 하네스 (H1~H12)

| ID | 패턴 | 처음 쓰는 카드 | 무엇을 관찰할까 | 실습 과제 | 함정 |
|---|---|---|---|---|---|
| **H1** | CLAUDE.md 메모리 · `@import` | H-001 | 매 세션 무엇이 자동 로드되는지, `@AGENTS.md`가 어떻게 합쳐지는지 | `/memory`로 로드된 메모리 확인. CLAUDE.md를 200줄로 늘렸다 줄여 `/context` 차이 측정 | CLAUDE.md를 백과사전으로 만들기 → 매 세션 토큰 낭비 |
| **H2** | 커스텀 슬래시 커맨드 · `$ARGUMENTS` · `allowed-tools` | H-004 | 커맨드가 프롬프트 템플릿이라는 점 | `/next`를 수정해 병렬 후보를 표시 | 커맨드에 로직을 과하게 넣기 → 스크립트로 빼라 |
| **H3** | 스킬 (progressive disclosure) | P-201 | description만 상시 로드 → 관련 작업에서 본문 로드되는 순간 | loom-plant description을 모호하게 바꿔 로드 안 되는 것 확인 후 복구 | description이 "무엇"만 있고 "언제"가 없음 |
| **H4** | 서브에이전트 분업 (별도 컨텍스트) | C-101 | 메인 컨텍스트가 얼마나 작게 유지되는지 | 같은 카드를 ①메인 단독 ②4-에이전트 분업으로 해 `/context` 비교 | 서브에이전트가 전체 코드를 되돌려 줌 → 출력 형식 강제 |
| **H5** | 훅 (SessionStart · PostToolUse · PreCompact · Stop) | H-002, H-003 | 훅 stdout/exit 2가 모델에게 어떻게 전달되는지 | post_edit에 "300줄 초과" 피드백 발생시켜 보기 | 차단형 훅 남용 → 작업이 멈춤. 피드백형 우선 |
| **H6** | Plan mode + ADR | N-306 | 계획만 하고 편집하지 않는 모드에서 설계 선택지 비교 | 매핑을 YAML vs 코드로 할지 ADR-00x 작성 | 계획 없이 바로 구현 → 섹터 전체 재작업 |
| **H7** | 병렬 서브에이전트 팬아웃 | N-302~N-305 | 서로 의존 없는 작업을 동시에 위임 | 커넥터 4종을 한 메시지에서 4개 서브에이전트로 | 같은 파일(public.py)을 동시에 수정 |
| **H8** | 헤드리스 `claude -p` | H-005 | 대화 없이 카드가 끝까지 도는 조건 | `run_card.sh` S 카드 1장 → runs/ JSON 읽기 | 사람 확인 없이 done 처리 |
| **H9** | Claude Agent SDK | A-808 | CLI 하네스를 **코드로** 조립할 때 무엇이 같고 다른지 | orchestrate를 SDK로 바꾼 변형 | 권한·턴 제한을 코드에서 빼먹음 |
| **H10** | MCP 서버 (도구 표준) | A-801 | 같은 도구를 Claude Code와 LangGraph가 공유 | `.mcp.json` 등록 → Claude Code에서 `loom.ask` 호출 | 쓰기 도구를 dry_run 없이 노출 |
| **H11** | git worktree 병렬 세션 | H-005, M3 | 브랜치별 독립 작업 폴더 + 머지 순서 | N-302·N-303 worktree 병렬 → 순서 머지 | uv.lock 충돌 → 의존성 추가 카드는 병렬 제외 |
| **H12** | 평가 하네스 (eval-driven) | E-508, A-807 | "테스트 통과"와 "맞다"의 차이 | 프롬프트 한 줄 바꾸고 spine20 전후 비교 | fake LLM만으로 품질 판단 |

**참고 문서**: Claude Code Skills <https://code.claude.com/docs/en/skills> · Agent Skills 개요 <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview> · Claude Code 문서의 Subagents / Hooks / Slash commands / Headless mode / MCP 장, Claude Agent SDK 문서 (버전별 플래그는 `claude --help`로 확인)

## §2 제품 층 — LangChain · LangGraph (L1~L15)

| ID | 패턴 | 처음 쓰는 카드 | 핵심 API | 실습 과제 | 함정 |
|---|---|---|---|---|---|
| **L1** | 모델 추상화 · 구조화 출력 | C-108, O-404 | `init_chat_model`, `with_structured_output` | 같은 추출을 Sonnet/로컬 Qwen으로 돌려 스키마 실패율 비교 | fake 모델로만 검증 |
| **L2** | 도구 · 도구 호출 | E-502, A-802 | `@tool`, `args_schema`, `bind_tools` | 도구 docstring을 바꿔 호출 정확도 변화 관찰 | 도구가 거대한 원시 데이터 반환 → 요약해서 반환 |
| **L3** | 리트리버 · 하이브리드 검색 | E-501 | `BaseRetriever`, BM25+dense RRF | 'WR-03' 같은 코드 검색에서 BM25만/dense만/혼합 비교 | dense만 쓰면 설비 코드 놓침 |
| **L4** | StateGraph · 조건 라우팅 | E-503, E-504 | `StateGraph`, `add_conditional_edges`, `START/END` | 라우터를 규칙→LLM으로 바꿔 비용·정확도 비교 | 상태에 모든 걸 넣기 → 노드별 필요한 키만 |
| **L5** | Checkpointer · 영속 스레드 | R-608 | `InMemorySaver`, `SqliteSaver`, `thread_id`, `get_state` | 실행 중 프로세스 종료 후 재개 | thread_id 재사용 실수로 상태 오염 |
| **L6** | Human-in-the-loop `interrupt` | R-608 | `interrupt()`, `Command(resume=...)` | 승인/반려/수정 3경로 테스트 | interrupt 앞 부작용 → 재개 시 중복 실행 |
| **L7** | Map-reduce `Send` | O-405, A-804 | `Send`, `Annotated[list, operator.add]` | 정비일지 100건 병렬 추출, max_concurrency 조절 | 리듀서 없이 병렬 쓰기 → 덮어쓰기 |
| **L8** | 서브그래프 | R-605 | 컴파일 그래프를 노드로/래퍼로 | ask 그래프를 RCA 그래프에 재사용 | 상태 키 충돌 → 래퍼 노드에서 매핑 |
| **L9** | Supervisor 멀티에이전트 | A-802, A-803 | `Command(goto=)`, 역할 에이전트 | 라운드 상한·예산 가드 | 감독자가 무한 위임 |
| **L10** | Swarm · Handoff | A-807 | handoff 도구, `langgraph-swarm` | Supervisor와 같은 스위트로 비교 | 비교 없이 "멀티에이전트가 더 좋다" 가정 |
| **L11** | 반성(Reflection) · 검증 루프 | A-805 | 구조화 `Critique` + 조건 복귀 | 근거 없는 주장 탐지율 측정 | 루프 횟수 제한 없음 |
| **L12** | 트레이싱 · 관측 | E-504, E-507 | 콜백, `stream_mode="updates"`, (선택) LangSmith | trace로 틀린 답의 원인 층 찾기 | 실데이터를 외부 트레이싱에 전송 |
| **L13** | MCP adapters | A-801 | `langchain-mcp-adapters` `MultiServerMCPClient` | LOOM MCP 도구로 LangGraph 에이전트 구동 | stdio 서버 수명 관리 |
| **L14** | 장기 메모리 Store | R-606 | `InMemoryStore`/`PostgresStore`, namespace, `search` | 과거 결정 인용 여부로 권고 품질 비교 | 실패 사례를 기억하지 않음 |
| **L15** | 스트리밍 UI | T-705, E-509 | `stream_mode=["updates","messages"]` | Streamlit에서 노드 진행·토큰 표시 | UI가 그래프 내부 상태에 강결합 |

**참고 문서**: LangChain v1 변경점 <https://docs.langchain.com/oss/python/releases/langchain-v1> · v1.0 발표 <https://www.langchain.com/blog/langchain-langgraph-1dot0> · LangGraph 문서의 Graph API / Persistence / Interrupts / Memory / Multi-agent 장. **구현 전 설치 버전 확인 필수** (loom-langchain·loom-langgraph 스킬 첫 줄).

## §3 추천 학습 순서 (카드 순서와 일치)

```
M0  H1 → H2 → H5
M1  H4 → L1
M2  H3
M3  H6 → H7 → H11
M4  L1(심화) → L7
M5  L3 → L2 → L4 → L12 → H12        ← G1: "RAG + 그래프 + 평가"를 한 바퀴
M6  L8 → L14 → L5 → L6              ← G2: "영속 + 사람 개입"
M7  (L15)
M8  H10 → L13 → L9 → L11 → (L7 · L10 · H9)   ← G3: "멀티에이전트 + 도구 표준"
```

## §4 교육 과정과의 연결 (10/14~10/30)
| 교육 과정 | 연결 패턴 | 기록할 것 |
|---|---|---|
| 5. 산업현장 맞춤형 피지컬AI 에이전트 (RAG·Tool Use) | L2 · L3 · L9 | 강의 에이전트 구조 vs LOOM E-504·A-803 구조 차이표 |
| 4. Isaac Sim 강화·모방학습 | (M9 이후) P8 | 도메인 랜덤화 ↔ PRISM `physics.variation_range` |
| 2. PLC 디지털트윈 | N-310 MQTT · W-902 | PLC 태그 → URN 매핑 아이디어 |

## §5 학습 노트 품질 기준 (`learning/<ID>.md`)
- ≤ 60줄. 개념 3줄 · LOOM 코드 위치(파일:함수) · **왜 이 방식인가** · 대안과 비교 1표 · 겪은 함정 · 퀴즈 3문항(답은 접어두기)
- "문서를 요약"하지 말고 **내가 LOOM에서 겪은 것**을 쓴다
