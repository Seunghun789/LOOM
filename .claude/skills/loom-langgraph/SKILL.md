---
name: loom-langgraph
description: LOOM의 LangGraph 패턴 요리책 — StateGraph·조건 라우팅·map-reduce(Send)·서브그래프·checkpointer·interrupt(HITL)·Store 메모리·Supervisor·Swarm·반성 루프·스트리밍과 각 패턴의 테스트 방법. 그래프·에이전트 오케스트레이션 코드를 쓰거나 테스트할 때 사용.
---

# LangGraph 요리책 (LOOM 기준)

> 설치 버전 확인 후 사용: `uv pip show langgraph`. v1 기준 예시. 다르면 researcher로 확인하고 DECISIONS.md에 기록.
> 공통 규칙: 상태는 `TypedDict`, 누적 필드는 `Annotated[list, operator.add]`, 빌더는 `build_*_graph(...)`, 컴파일 그래프를 모듈 전역에 두지 않는다.

## §stategraph — 기본 + 조건 라우팅 (E-503, E-504)
```python
import operator
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END

class AskState(TypedDict, total=False):
    question: str
    intent: str
    evidence_steps: Annotated[list[dict], operator.add]
    answer: dict

def build_ask_graph(ctx, models):
    def route(state):   return {"intent": classify(state["question"], models["route"])}
    def gather(state):  return {"evidence_steps": collect(ctx, state)}
    def compose(state): return {"answer": write_answer(state, models["reason"])}

    g = StateGraph(AskState)
    g.add_node("route", route); g.add_node("gather", gather); g.add_node("compose", compose)
    g.add_edge(START, "route")
    g.add_conditional_edges("route", lambda s: "out" if s["intent"] == "out_of_scope" else "gather",
                            {"gather": "gather", "out": END})
    g.add_edge("gather", "compose"); g.add_edge("compose", END)
    return g.compile()
```
**테스트**: `list(graph.stream(inp, stream_mode="updates"))` → 노드 이름 순서 단언.

## §map-reduce — Send 병렬 팬아웃 (O-405, A-804)
```python
from langgraph.types import Send

class LogState(TypedDict):
    entries: list[dict]
    results: Annotated[list[dict], operator.add]

def fan_out(state):  # 조건 엣지 함수가 Send 리스트를 반환
    return [Send("extract_one", {"entry": e}) for e in state["entries"]]

g.add_conditional_edges(START, fan_out, ["extract_one"])
g.add_node("extract_one", lambda s: {"results": [extract(s["entry"])]})
g.add_edge("extract_one", "reduce")
```
**테스트**: entries 3개 → results 길이 3. 동시성 제한은 `graph.invoke(inp, config={"max_concurrency": 4})`.

## §subgraph — 서브그래프 (R-605)
상태 스키마가 다르면 **래퍼 노드에서 명시적으로 매핑**한다 (키 공유보다 안전):
```python
ask_graph = build_ask_graph(ctx, models)
def call_ask(state: RcaState):
    out = ask_graph.invoke({"question": state["question"]})
    return {"answer": out["answer"]}
rca.add_node("ask", call_ask)
```
**테스트**: fake ask_graph(모의 객체)로 호출 횟수 1 단언.

## §checkpointer — 영속 실행 (R-608)
```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver   # uv add langgraph-checkpoint-sqlite
saver = SqliteSaver(sqlite3.connect("var/ops.sqlite", check_same_thread=False))
graph = builder.compile(checkpointer=saver)
cfg = {"configurable": {"thread_id": "case-01J8..."}}
graph.invoke(inp, cfg)
graph.get_state(cfg)          # 현재 상태·다음 노드
```
테스트는 `from langgraph.checkpoint.memory import InMemorySaver`.

## §interrupt — 사람 승인 (R-608)
```python
from langgraph.types import interrupt, Command

def approval(state):
    if state["autonomy"] != "L2":
        return {"approved": state["autonomy"] == "L3"}
    reply = interrupt({"decision_id": state["decision_id"], "actions": state["actions"]})  # 여기서 멈춤
    return {"approved": reply["decision"] == "approve", "approver": reply["by"]}

# 재개 (다른 프로세스·재시작 후에도 thread_id만 같으면 됨)
graph.invoke(Command(resume={"decision": "approve", "by": "urn:loom:plantA:Person:owner"}), cfg)
```
주의: interrupt 이전 노드 코드는 재개 시 **다시 실행될 수 있다** → interrupt 앞에 부작용(실행·이벤트 발행)을 두지 않는다.
**테스트**: 1차 invoke 후 `graph.get_state(cfg).next == ("approval",)` → 새 그래프 인스턴스(같은 saver)로 resume → 최종 상태.

## §store — 장기 메모리 (R-606)
```python
from langgraph.store.memory import InMemoryStore
store = InMemoryStore(index={"embed": embed_fn, "dims": 256})   # 의미 검색 사용 시
store.put(("decisions", "plantA"), decision_id, {"summary": s, "success": True})
hits = store.search(("decisions", "plantA"), query="WR-03 팁 마모 강도 저하", limit=3)
```
LOOM은 store를 그래프 주입 대신 **DecisionMemory 클래스로 감싸 인자로 전달**한다 (테스트 단순화).

## §command — 노드에서 라우팅 (A-803, A-805)
```python
from typing import Literal
from langgraph.types import Command

def supervisor(state) -> Command[Literal["diagnose", "judge", "solve", "verify", "finalize"]]:
    nxt = decide_next(state)            # LLM 또는 규칙
    return Command(goto=nxt, update={"round": state["round"] + 1})
```

## §supervisor — 감독자 패턴 (A-803)
- 감독자 노드가 Command로 역할 에이전트 노드를 고른다
- 각 역할 에이전트 노드 = `make_role_agent(...)` 컴파일 그래프를 래퍼로 호출, 결과를 `hypotheses`에 병합
- 종료 조건 3개를 **코드로**: `round >= max_rounds`, `budget_used >= budget`, 감독자가 `finalize` 선택
- 대안: `langgraph-supervisor` 패키지의 `create_supervisor` — 직접 구현을 먼저 하고 비교 노트에 기록 (L9)

## §swarm — 핸드오프 패턴 (A-807)
- 각 에이전트가 `transfer_to_<role>` 도구를 가지고 스스로 다음 에이전트로 넘긴다 (중앙 감독자 없음)
- 대안 패키지 `langgraph-swarm` (`create_swarm`, `create_handoff_tool`)
- Supervisor와의 차이를 **같은 평가 스위트**로 측정 (A-807)

## §reflection — 검증 루프 (A-805)
```python
def verify(state) -> Command[Literal["supervisor", "finalize"]]:
    c = critique(state)                               # 구조화 출력 Critique
    if c.ok or state["verify_count"] >= 2:
        return Command(goto="finalize")
    return Command(goto="supervisor", update={"verify_count": state["verify_count"] + 1, "issues": c.issues})
```

## §streaming — UI 스트리밍 (T-705, E-509)
```python
for mode, chunk in graph.stream(inp, stream_mode=["updates", "messages"]):
    ...   # updates: 노드 완료, messages: LLM 토큰
```

## 패턴 선택 가이드
| 상황 | 패턴 |
|---|---|
| 순서가 정해진 파이프라인 | StateGraph 직선 |
| 입력 종류에 따라 분기 | conditional edges |
| 같은 작업을 N개 항목에 | Send map-reduce |
| 재사용 가능한 큰 흐름 | subgraph (래퍼 노드) |
| 사람 승인·재개 | interrupt + checkpointer |
| 과거 사례 기억 | Store |
| 역할 분업 + 중앙 통제 | supervisor |
| 역할 분업 + 자율 인계 | swarm |
| 품질 보증 | reflection loop (횟수 제한 필수) |
