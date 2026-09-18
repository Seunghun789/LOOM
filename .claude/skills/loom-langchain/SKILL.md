---
name: loom-langchain
description: LOOM에서 LangChain을 쓰는 방식 — 모델 초기화, 구조화 출력, 도구(@tool), 리트리버, 에이전트(create_agent), fake 모델 테스트. LLM 호출·도구·검색·에이전트 코드를 쓰거나 테스트할 때 사용.
---

# LangChain in LOOM

> **버전 주의**: LangChain·LangGraph는 2025년 10월 v1.0에서 에이전트 API가 바뀌었다(`langchain.agents.create_agent`, middleware). 코드를 쓰기 전에 `uv pip show langchain langgraph`로 설치 버전을 확인하고, 아래 예시와 다르면 `researcher`로 공식 문서를 확인한다. 확인 결과는 `state/DECISIONS.md`에 기록.

## §model — 모델은 역할로만 얻는다
```python
from loom.core.public import get_chat_model
model = get_chat_model("reason")      # 내부: langchain.chat_models.init_chat_model("anthropic:<id>")
```
환경변수: `LOOM_LLM_REASON="anthropic:<sonnet-model-id>"`, `LOOM_LLM_ROUTE="ollama:qwen3:4b"`.

## §structured-output — 구조화 출력
```python
from pydantic import BaseModel
class CriterionCandidate(BaseModel):
    item: str; prop: str; op: str; value: float; unit: str

chain = model.with_structured_output(CriterionCandidate)
cand = chain.invoke([("system", PROMPT), ("user", section_text)])
```
**테스트(fake)**: fake 모델은 `with_structured_output`을 지원하지 않을 수 있다. 그래서 `loom.core.llm.structured(model, Schema)` 헬퍼를 쓴다:
```python
def structured(model, schema):
    if getattr(model, "_loom_fake", False):
        from langchain_core.output_parsers import PydanticOutputParser
        return model | PydanticOutputParser(pydantic_object=schema)
    return model.with_structured_output(schema)
```
fake 응답에는 **실제 모델이 낼 법한 JSON 문자열**을 넣는다.

## §tools — 도구
```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class WindowArgs(BaseModel):
    urn: str = Field(description="엔티티 URN")
    prop: str
    start: str = Field(description="ISO8601 UTC")
    end: str

def make_tools(ctx):
    @tool(args_schema=WindowArgs)
    def telemetry_window(urn: str, prop: str, start: str, end: str) -> dict:
        """설비 속성의 시간창 요약과 근거 단계를 반환한다."""
        ...
        return {"summary": {...}, "steps": [step.model_dump(mode="json")]}
    return [telemetry_window]
```
- 도구는 **클로저로 ctx를 캡처**한다 (전역 금지)
- 반환에 `steps` 필수 (근거 추적) · docstring이 LLM에게 보이는 설명이다

## §retriever — 검색
`HybridIndex.as_retriever()`는 `langchain_core.retrievers.BaseRetriever`를 상속한 어댑터를 반환한다:
```python
class LoomRetriever(BaseRetriever):
    index: Any; k: int = 8
    def _get_relevant_documents(self, query, *, run_manager):
        return [Document(page_content=d.text, metadata={"urn": d.urn, **d.meta}) for d, _ in self.index.search(query, self.k)]
```

## §agents — 역할 에이전트
```python
from langchain.agents import create_agent          # LangChain v1
agent = create_agent(model, tools=tools, system_prompt=open(prompt_path).read())
result = agent.invoke({"messages": [("user", task)]})
```
v1 이전 버전이면 `from langgraph.prebuilt import create_react_agent`(`prompt=` 인자). **어느 쪽을 쓰는지 ADR로 고정**.

## §fake-tool-calling — 도구 호출 fake 테스트
```python
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

class FakeToolModel(GenericFakeChatModel):
    def bind_tools(self, tools, **kw):   # 에이전트가 bind_tools를 호출하므로 no-op
        return self

model = FakeToolModel(messages=iter([
    AIMessage(content="", tool_calls=[{"name": "telemetry_window", "args": {...}, "id": "c1"}]),
    AIMessage(content="WR-03 팁 마모가 원인입니다."),
]))
```
`tests/conftest.py`의 `fake_tool_model(responses)` 픽스처로 제공한다.

## §callbacks — 사용량 계측
`UsageMeter(BaseCallbackHandler).on_llm_end`에서 `response.generations[0][0].message.usage_metadata`를 합산. 모든 invoke에 `config={"callbacks": [meter]}`.

## §tracing
기본은 `loom.core.trace.Tracer`(로컬 JSONL). LangSmith를 쓰려면 `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY` — **실데이터 없는 가상 팩에서만**.
