#!/usr/bin/env bash
# PreCompact: 컴팩트 직전 상태 스냅샷을 남긴다. 컴팩트 후 SessionStart(compact)가 HANDOFF를 다시 주입한다.
cd "${CLAUDE_PROJECT_DIR:-$(pwd)}" || exit 0
mkdir -p state
{
  echo "# 컴팩트 스냅샷 $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "## git status"; git status --short 2>/dev/null | head -30
  echo "## doing 카드"; grep -B9 "status: doing" modules/registry.yaml 2>/dev/null | grep "id:" || true
} > state/.compact_snapshot.md
echo "컴팩트 전: state/HANDOFF.md가 최신이 아니면 컴팩트 후 첫 작업으로 /handoff 초안을 갱신할 것."
exit 0
