# harness/ — 헤드리스 개발 러너

| 파일 | 역할 |
|---|---|
| `run_card.sh <ID>` | 카드 1장을 `claude -p`로 실행, 결과 JSON을 `runs/`에 저장, status를 review/blocked로 |
| `orchestrate.py` | registry 의존성으로 파동을 계산해 순차·병렬(worktree) 실행 |
| `prompts/build_card.md` | 헤드리스 오케스트레이터 프롬프트 |
| `runs/` | 실행 기록 (커밋 권장 — 학습 자료) |
| `sdk_orchestrate.py` | (A-808에서 작성) Claude Agent SDK 변형 |

## 사용 순서
1. **대화형으로 3~5장** (`/start` → `/build` → `/handoff`) — 카드 품질·훅·서브에이전트가 도는지 확인
2. `claude --help`로 플래그 확인 → 아래 "확인 기록" 작성
3. `python3 harness/orchestrate.py --milestone M1 --dry-run`
4. S 크기 카드 1장 헤드리스: `harness/run_card.sh C-102`
5. `git diff` 확인 → `python3 tools/progress.py --set C-102 done` → 커밋
6. 익숙해지면 `--parallel 2` (의존성 추가 없는 카드끼리만)

## 확인 기록 (직접 채울 것)
- Claude Code 버전:
- `claude -p` 플래그 확인일:
- 달라진 점:

## 머지 절차 (병렬 후)
```bash
git -C ../loom-<ID> diff main --stat
git merge --no-ff card/<ID>
git worktree remove ../loom-<ID> && git branch -d card/<ID>
uv run pytest -q && uv run lint-imports
```
