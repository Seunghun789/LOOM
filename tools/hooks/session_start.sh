#!/usr/bin/env bash
# SessionStart: stdout이 세션 컨텍스트에 주입된다. 짧게 유지(≤80줄).
cd "${CLAUDE_PROJECT_DIR:-$(pwd)}" || exit 0
echo "## LOOM 세션 시작 컨텍스트 (자동 주입)"
if [ -f state/HANDOFF.md ]; then
  echo "### state/HANDOFF.md (앞 50줄)"
  head -50 state/HANDOFF.md
fi
if command -v uv >/dev/null 2>&1 && [ -f pyproject.toml ]; then
  echo "### 다음 가능 카드"
  uv run --quiet python tools/progress.py --next --limit 5 2>/dev/null || true
elif command -v python3 >/dev/null 2>&1; then
  echo "### 다음 가능 카드"
  python3 tools/progress.py --next --limit 5 2>/dev/null || true
fi
echo "### git"
git status --short 2>/dev/null | head -15
exit 0
