#!/usr/bin/env bash
# Stop: 차단하지 않는 리마인더. src 변경이 있는데 HANDOFF가 30분 이상 오래되면 알린다.
cd "${CLAUDE_PROJECT_DIR:-$(pwd)}" || exit 0
CHANGED=$(git status --short src tests 2>/dev/null | wc -l | tr -d ' ')
[ "$CHANGED" = "0" ] && exit 0
if [ -f state/HANDOFF.md ]; then
  AGE=$(( $(date +%s) - $(stat -f %m state/HANDOFF.md 2>/dev/null || stat -c %Y state/HANDOFF.md) ))
  if [ "$AGE" -gt 1800 ]; then
    echo "리마인더: 코드 변경 ${CHANGED}건, HANDOFF.md가 $((AGE/60))분 전 상태. 세션을 끝낼 거면 /handoff" >&2
  fi
fi
exit 0
