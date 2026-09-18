#!/usr/bin/env bash
# 카드 1장을 헤드리스 Claude Code로 실행한다.
# 사용: harness/run_card.sh <CARD_ID> [--max-turns N]
# 먼저 `claude --help`로 플래그를 확인하고, 다르면 이 파일을 고친 뒤 README에 버전을 기록한다.
set -euo pipefail
CARD="${1:?card id required}"; shift || true
MAX_TURNS=60
while [ $# -gt 0 ]; do case "$1" in --max-turns) MAX_TURNS="$2"; shift 2;; *) shift;; esac; done

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[ -f "modules/cards/$CARD.md" ] || { echo "no card: $CARD" >&2; exit 1; }
mkdir -p harness/runs
TS=$(date -u +%Y%m%dT%H%M%SZ)
PROMPT=$(sed "s/{{CARD_ID}}/$CARD/g" harness/prompts/build_card.md)

python3 tools/progress.py --set "$CARD" doing >/dev/null

claude -p "$PROMPT" \
  --output-format json \
  --permission-mode acceptEdits \
  --max-turns "$MAX_TURNS" \
  --allowedTools "Read,Write,Edit,MultiEdit,Glob,Grep,Task,Bash(uv run pytest:*),Bash(uv run ruff:*),Bash(uv run lint-imports:*),Bash(uv add:*),Bash(uv sync:*),Bash(python3 tools/progress.py:*),Bash(git diff:*),Bash(git status:*)" \
  > "harness/runs/$CARD-$TS.json" || {
    echo "claude run failed for $CARD (see harness/runs/$CARD-$TS.json)" >&2
    python3 tools/progress.py --set "$CARD" blocked >/dev/null
    exit 1
  }

echo "done: harness/runs/$CARD-$TS.json"
python3 - "$CARD" "harness/runs/$CARD-$TS.json" <<'PY'
import json, sys
card, path = sys.argv[1], sys.argv[2]
try:
    outer = json.load(open(path))
    text = outer.get("result", "") if isinstance(outer, dict) else ""
    start, end = text.find("{"), text.rfind("}")
    inner = json.loads(text[start:end + 1]) if start >= 0 else {}
    print(f"{card}: result={inner.get('result')} tests={inner.get('tests_passed')} blocker={inner.get('blocker')!r}")
    if inner.get("result") != "review":
        import subprocess; subprocess.run(["python3", "tools/progress.py", "--set", card, "blocked"])
except Exception as e:  # noqa: BLE001
    print(f"{card}: could not parse result ({e}); check the run file manually")
PY
