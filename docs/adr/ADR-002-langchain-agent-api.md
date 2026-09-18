# ADR-002 · 에이전트 생성 API 고정 (create_agent vs create_react_agent)

- 상태: proposed — **M1 C-108 착수 시 researcher로 설치 버전 확인 후 확정**
- 날짜: 2026-09-17
- 영향 모듈: A-802, A-803, A-807

## 맥락
LangChain·LangGraph v1.0(2025-10)에서 에이전트 생성의 표준이 `langchain.agents.create_agent`(middleware 지원)로 옮겨졌고, `langgraph.prebuilt.create_react_agent`는 이전 방식이다. 문서·예제가 섞여 있어 세션마다 다른 API를 쓸 위험이 있다.

## 선택지
| 안 | 내용 |
|---|---|
| A | `langchain.agents.create_agent` (v1) |
| B | `langgraph.prebuilt.create_react_agent` |

## 결정 (확정 시 기입)
- 설치 버전: langchain==?, langgraph==?
- 선택: 
- `loom-langchain` 스킬 §agents를 선택에 맞게 수정
