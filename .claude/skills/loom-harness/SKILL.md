---
name: loom-harness
description: LOOM 개발 하네스 운영 — 헤드리스 claude -p 카드 실행, orchestrate.py 의존성 순서 실행, git worktree 병렬, MCP 서버 연결, Claude Agent SDK 변형. 여러 카드를 자동·병렬로 돌리거나 MCP·SDK를 다룰 때 사용.
---

# 개발 하네스

"하네스(harness)" = 모델을 감싸 **루프·도구·컨텍스트·권한·검증**을 제공하는 실행 틀. LOOM에는 두 층이 있다.
| 층 | 무엇 | 어디 |
|---|---|---|
| 개발 하네스 | Claude Code(대화형) → `claude -p`(헤드리스) → Claude Agent SDK(코드) | `.claude/`, `harness/` |
| 제품 하네스 | LangChain 에이전트·LangGraph 그래프가 LOOM 도구를 감싸는 실행 틀 | `src/loom/evidence`, `operate`, `agent` |
| 평가 하네스 | 시나리오 → 실행 → 지표 | `loom eval` |

> CLI 플래그는 버전마다 바뀐다. 먼저 `claude --help`로 확인하고 `harness/README.md`에 확인한 버전을 적는다.

## §headless — 카드 1장 헤드리스 실행
```bash
harness/run_card.sh C-102
```
내부: `claude -p "<harness/prompts/build_card.md + 카드 ID>" --output-format json --permission-mode acceptEdits --max-turns 60 --allowedTools "..."` → `harness/runs/<ID>-<ts>.json`
- 대화형으로 3~5장을 성공시킨 **후에** 헤드리스를 쓴다 (카드 품질 검증이 먼저)
- 헤드리스 결과는 항상 사람이 `git diff`로 확인 후 `done`

## §orchestrate — 마일스톤 단위 순차/병렬
```bash
python3 harness/orchestrate.py --milestone M1 --dry-run         # 실행 계획
python3 harness/orchestrate.py --milestone M1 --parallel 2      # 준비된 카드 2장씩 worktree 병렬
```
- 파동(wave) 단위: 의존성이 모두 done인 카드 묶음 → 실행 → 테스트 → status review → 다음 파동
- 한 파동이 실패하면 멈춘다 (연쇄 실패 방지)

## §worktree — 병렬 개발
```bash
git worktree add ../loom-N-302 -b card/N-302
cd ../loom-N-302 && harness/run_card.sh N-302
# 끝나면 메인에서
git merge --no-ff card/N-302 && git worktree remove ../loom-N-302
```
충돌 단골: `src/loom/<sector>/public.py`, `tests/conftest.py`, `pyproject.toml`/`uv.lock`
→ 병렬 카드는 **public.py 추가만** 하게 하고 머지 시 순서대로 합친다. 의존성 추가 카드는 병렬에서 뺀다.

## §mcp — LOOM 도구를 Claude Code에 연결 (A-801)
`.mcp.json` (프로젝트 스코프):
```json
{ "mcpServers": { "loom": { "command": "uv", "args": ["run", "python", "-m", "loom.agent.mcp_server"] } } }
```
서버:
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("loom")

@mcp.tool()
def ask(question: str) -> dict:
    """LOOM에 근거 기반 질문을 한다."""
    return run_ask(question).model_dump(mode="json")

if __name__ == "__main__":
    mcp.run()          # stdio
```
LangGraph 쪽에서 같은 서버 사용: `langchain-mcp-adapters`의 `MultiServerMCPClient` → `await client.get_tools()`.
→ **같은 도구를 개발 에이전트(Claude Code)와 제품 에이전트(LangGraph)가 공유**하는 것이 학습 포인트(H10·L13).

## §sdk — Claude Agent SDK 변형 (A-808, 선택)
```python
from claude_agent_sdk import query, ClaudeAgentOptions
async for msg in query(prompt=build_prompt(card_id),
                       options=ClaudeAgentOptions(cwd=".", permission_mode="acceptEdits",
                                                  allowed_tools=["Read", "Edit", "Write", "Bash"])):
    log(msg)
```
비교 관찰: 서브에이전트를 파일(.claude/agents)로 정의 vs 코드로 주입 / 훅·권한 설정 위치 / 비용·턴 제어.

## 비용·안전 가드
- `--max-turns`로 루프 상한
- `permission-mode acceptEdits`는 편집만 자동 승인, 셸 명령은 allowedTools로 제한
- `git push`, `rm -rf`는 settings.json deny
