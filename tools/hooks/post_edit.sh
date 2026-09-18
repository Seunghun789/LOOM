#!/usr/bin/env bash
# PostToolUse(Edit|MultiEdit|Write): 편집된 .py에 ruff 적용, 남은 문제만 Claude에게 되돌린다.
# 도구 실행은 이미 끝났으므로 exit 2는 "차단"이 아니라 "피드백 전달" 용도다.
cd "${CLAUDE_PROJECT_DIR:-$(pwd)}" || exit 0
[ -f pyproject.toml ] || exit 0
command -v uv >/dev/null 2>&1 || exit 0
FILE=$(python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); ti=d.get("tool_input",{}); print(ti.get("file_path") or ti.get("path") or "")
except Exception: print("")')
case "$FILE" in
  *.py) ;;
  *) exit 0 ;;
esac
[ -f "$FILE" ] || exit 0
uv run --quiet ruff format "$FILE" >/dev/null 2>&1
OUT=$(uv run --quiet ruff check --fix "$FILE" 2>&1)
if [ $? -ne 0 ]; then
  echo "ruff 문제 (자동 수정 불가) — $FILE" >&2
  echo "$OUT" | tail -20 >&2
  exit 2
fi
LINES=$(wc -l < "$FILE")
if [ "$LINES" -gt 300 ]; then
  echo "규칙 R7 위반: $FILE ${LINES}줄 (300줄 초과) — 분할하라" >&2
  exit 2
fi
exit 0
