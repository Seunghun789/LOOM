# 01 · ARCHITECTURE — 계층·조립·스택

## §1 계층과 섹터

```
┌──────────────────────────────────────────────────────────────────────────┐
│ apps/console (Streamlit, M5~M7)        apps/web (React + PRISM, M9~)      │  UI
├──────────────────────────────────────────────────────────────────────────┤
│ loom.api (FastAPI /v0)                 loom.cli (typer `loom`)            │  조립
├──────────────┬───────────────┬───────────────┬───────────────────────────┤
│ agent  (S8)  │ studio (S9)   │ twin (S4)     │ physics (S5)  capture (S1) │  응용
├──────────────┴───────┬───────┴───────────────┴───────────────────────────┤
│ operate (S7)         │ evidence (S6)                                      │  판단
├──────────────────────┴───────────────────────────────────────────────────┤
│ semantic (S3)                                                             │  의미
├───────────────────────────────┬──────────────────────────────────────────┤
│ connect (S2)                  │ plant (P) — 가상 실증공장 (데이터 원천)   │  연결·원천
├───────────────────────────────┴──────────────────────────────────────────┤
│ core (S0) — ids · units · provenance · entity · ports · telemetry ·       │  계약
│             events · llm · embed · settings · trace · container          │
└──────────────────────────────────────────────────────────────────────────┘
```
허용 의존 방향은 `docs/02_CONTRACTS.md` §1 B-5. **위에서 아래로만**, 섹터 간은 `public.py`로만.

## §2 조립 방식 — "카드 → 모듈 → 섹터 public → 조립 지점"

```
modules/cards/C-104.md ──(TDD 세션)──► src/loom/core/entity.py + tests/core/test_entity.py
                                           │
                                           ▼ 공개 이름 등록
                                    src/loom/core/public.py
                                           │ import (다른 섹터는 이것만)
      ┌────────────────────────────────────┼─────────────────────────────────┐
      ▼                                    ▼                                 ▼
 loom.connect.pipeline             loom.semantic.graph               loom.evidence.graph_ask
      │                                    │                                 │
      └──────────────► 조립 지점: loom.core.container.build_container() ◄────┘
                              loom.api.app / loom.cli.main / apps/*
```

- **모듈**: 파일 1~3개 + 테스트. 카드 1장이 만든다
- **섹터 public.py**: 모듈들을 묶어 외부에 여는 파사드. 섹터의 마지막 카드(예: N-309, O-410, E-508, R-610)가 정리한다
- **조립 지점**: Container로 포트 구현체를 고르고 섹터 함수를 엮는다. 비즈니스 로직 없음
- 이 구조 덕분에 **어떤 카드든 계약 문서 + 의존 public.py만 보고 독립 세션에서 만들 수 있다**

## §3 두 종류의 오케스트레이션

| | 개발 오케스트레이션 | 제품 런타임 오케스트레이션 |
|---|---|---|
| 목적 | LOOM **코드를 만든다** | LOOM이 **질문에 답하고 판단한다** |
| 실행 틀(하네스) | Claude Code 대화형 → `claude -p` → Claude Agent SDK | LangChain `create_agent` · LangGraph `StateGraph` |
| 에이전트 | planner · test-writer · module-builder · reviewer · contract-guardian · eval-runner · researcher · doc-keeper | route · resolve · gather · compose 노드 / diagnose · judge · solve · verify 역할 에이전트 |
| 상태·기억 | 파일: HANDOFF · registry · 카드 · git | checkpointer(스레드) · Store(과거 결정) · EntityStore |
| 사람 개입 | `/start` 승인, 리뷰 후 done, ADR 승인 | `interrupt()` 승인, ASSUMED→CONFIRMED 검토 |
| 도구 공유 | MCP `loom` 서버를 Claude Code가 호출 (A-801 이후) | 같은 MCP 서버를 langchain-mcp-adapters로 호출 |
| 평가 | 테스트·린트·경계 + reviewer | 평가 하네스 spine20·ops·arch |

두 층이 **같은 원리**(역할 분리 · 상태 외부화 · 사람 승인 · 측정)로 설계돼 있어, 한쪽에서 배운 것이 다른 쪽에 그대로 옮겨간다. 학습 매핑은 `docs/06_LEARNING_TRACK.md`.

## §4 기술 스택 (단축판 확정)

| 층 | 선택 | 대안 (나중에) | 결정 이유 |
|---|---|---|---|
| 런타임 | Python 3.12 · uv | — | 분석가 경력·AI 코딩 친화 |
| 모델·검증 | pydantic v2 | — | 계약 = 스키마 |
| 저장소 | **Memory 기본** → Postgres 16 + JSONB + pgvector | Neo4j 투영 | 테스트 속도. 운영 컴포넌트 최소화 |
| 그래프 | NetworkX 투영 | Neo4j Community | 입문 난이도·설치 0 |
| LLM | LangChain `init_chat_model` (Anthropic Sonnet 기본, Ollama 선택) | LiteLLM | LangChain 학습과 겸함 |
| 오케스트레이션 | LangGraph (StateGraph·Send·interrupt·checkpointer·Store) | — | 학습 목표 |
| 임베딩 | Hash(테스트) → bge-m3 / KURE-v1 | Qwen3-Embedding | 한국어 설비명 |
| 검색 | rank-bm25 + dense + RRF | 리랭커 bge-reranker-v2-m3 | 설비 코드 정확 일치가 중요 |
| 문서 | pypdf(테스트) · Docling(실사용) | PaddleOCR-VL | |
| 시뮬 | SimPy · numpy | — | 결정성 |
| 이상탐지 | numpy SPC · PyOD | anomalib(비전) | |
| UI | **Streamlit + pyvis** (M5~M7) → React + PRISM (M9~) | — | 단축 |
| API | FastAPI | — | |
| 에이전트 도구 공유 | MCP (python `mcp` FastMCP) · langchain-mcp-adapters | — | 개발·제품 공유 |
| 물리 | numpy D2Q9 → XLB · PyTorch U-Net · 커스텀 컨포멀 | PhysicsNeMo | CPU 우선 |
| 공간 | ezdxf · Open3D · COLMAP(Docker) | OpenDroneMap | |

## §5 디렉터리 (완성 시)
```
loom/
├─ CLAUDE.md  AGENTS.md  README.md  pyproject.toml  uv.lock  .importlinter  .mcp.json  docker-compose.yml
├─ .claude/   settings.json · agents/ · skills/ · commands/
├─ docs/      00~07 · adr/ · demo/ · PORTFOLIO.md · RUNBOOK.md
├─ modules/   registry.yaml · cards/ · CARD_TEMPLATE.md
├─ state/     HANDOFF.md · PROGRESS.md · DECISIONS.md
├─ harness/   run_card.sh · orchestrate.py · prompts/ · runs/
├─ tools/     progress.py · hooks/ · check_boundaries.sh · db_reset.sh
├─ learning/  _TEMPLATE.md · H1.md … L15.md
├─ src/loom/  core · plant · connect · semantic · evidence · operate · studio · agent · twin · physics · capture · api · cli
├─ tests/     conftest.py · <sector>/…
├─ apps/      console/ (Streamlit) · web/ (React)
└─ var/       packs/ · raw/ · lineage/ · traces/ · eval/ · sim/ · events.jsonl  (gitignore, eval 리포트만 커밋)
```
