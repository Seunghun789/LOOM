#!/usr/bin/env python3
"""마일스톤 단위 카드 오케스트레이터 (파동 실행).

  python3 harness/orchestrate.py --milestone M1 --dry-run
  python3 harness/orchestrate.py --milestone M1 --parallel 2 --priority P0

파동(wave) = 의존성이 모두 done/review인 todo 카드 묶음. 한 파동이 끝나면 테스트를 돌리고,
실패 카드가 있으면 멈춘다. 병렬(>1)은 카드마다 git worktree를 만든다.
주의: 헤드리스 결과는 status=review 로 남는다. 다음 파동은 review도 '충족'으로 간주하지만
      사람이 확인 후 done으로 바꾸기 전에는 머지하지 않는 것을 권장한다.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import progress  # noqa: E402


def waves(modules: list[dict], milestone: str | None, priority: str | None) -> list[list[dict]]:
    status = {m["id"]: m["status"] for m in modules}
    todo = [
        m
        for m in modules
        if m["status"] == "todo"
        and (not milestone or m["milestone"] == milestone)
        and (not priority or m["priority"] <= priority)
    ]
    plan: list[list[dict]] = []
    satisfied = {i for i, s in status.items() if s in ("done", "review")}
    remaining = list(todo)
    while remaining:
        wave = [m for m in remaining if all(d in satisfied for d in m.get("depends", []))]
        if not wave:
            blocked = ", ".join(m["id"] for m in remaining)
            print(f"[plan] 의존성 미충족으로 계획 불가: {blocked}")
            break
        plan.append(wave)
        satisfied |= {m["id"] for m in wave}
        remaining = [m for m in remaining if m not in wave]
    return plan


def run_card(card: str, parallel: bool) -> int:
    if not parallel:
        return subprocess.call([str(ROOT / "harness" / "run_card.sh"), card], cwd=ROOT)
    wt = ROOT.parent / f"loom-{card}"
    if not wt.exists():
        subprocess.check_call(["git", "worktree", "add", str(wt), "-b", f"card/{card}"], cwd=ROOT)
    return subprocess.call([str(wt / "harness" / "run_card.sh"), card], cwd=wt)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--milestone")
    ap.add_argument("--priority", default="P0", help="P0 | P1 | P2 (이 값 이하만)")
    ap.add_argument("--parallel", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-waves", type=int, default=3)
    a = ap.parse_args()

    _, modules = progress.load()
    errs = progress.check(modules)
    if errs:
        sys.exit("registry 오류:\n" + "\n".join(errs))
    plan = waves(modules, a.milestone, a.priority)
    for i, wave in enumerate(plan, 1):
        print(f"wave {i}: " + ", ".join(f"{m['id']}({m['size']})" for m in wave))
    if a.dry_run or not plan:
        return

    for i, wave in enumerate(plan[: a.max_waves], 1):
        ids = [m["id"] for m in wave]
        print(f"\n=== wave {i} 실행: {ids}")
        if a.parallel > 1:
            with ThreadPoolExecutor(max_workers=a.parallel) as ex:
                codes = list(ex.map(lambda c: run_card(c, True), ids))
        else:
            codes = [run_card(c, False) for c in ids]
        failed = [c for c, code in zip(ids, codes, strict=True) if code != 0]
        if a.parallel == 1:
            test = subprocess.call(["uv", "run", "pytest", "-q"], cwd=ROOT)
            if test != 0:
                failed.append("pytest")
        if failed:
            print(f"wave {i} 실패: {failed} — 중단. HANDOFF와 harness/runs/ 확인")
            sys.exit(1)
        if a.parallel > 1:
            print("병렬 파동 완료. 각 worktree에서 diff 확인 후 순서대로 머지하고 다시 실행하라.")
            return
    print(
        "\n계획한 파동 완료. `python3 tools/progress.py`로 보드 갱신,"
        " review 카드를 확인해 done 처리."
    )


if __name__ == "__main__":
    main()
