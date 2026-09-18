#!/usr/bin/env python3
"""LOOM 진행 보드 — 표준 라이브러리만 사용 (uv 설치 전에도 동작).

사용:
  python3 tools/progress.py                     # state/PROGRESS.md 갱신 + 요약 출력
  python3 tools/progress.py --next [--limit N]  # 의존성 충족된 todo 카드 (P0 → 마일스톤 순)
  python3 tools/progress.py --set C-101 doing   # 상태 변경 후 보드 갱신
  python3 tools/progress.py --milestone M3      # 해당 마일스톤만 표시
  python3 tools/progress.py --check             # 누락 의존성·순환 검사 (exit 1 on error)
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "modules" / "registry.yaml"
BOARD = ROOT / "state" / "PROGRESS.md"
STATUSES = ("todo", "doing", "review", "done", "blocked")
SIZE_SESS = {"S": 1.0, "M": 1.5}
ICON = {"todo": "⬜", "doing": "🟦", "review": "🟨", "done": "✅", "blocked": "⛔"}


def _val(raw: str):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [x.strip() for x in inner.split(",") if x.strip()] if inner else []
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1]
    return raw


def load() -> tuple[OrderedDict, list[dict]]:
    milestones: OrderedDict[str, str] = OrderedDict()
    modules: list[dict] = []
    section, cur = None, None
    for line in REG.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" "):
            section = line.split(":")[0].strip()
            continue
        m = re.match(r"^\s*-\s+id:\s*(\S+)", line)
        if m:
            cur = {"id": m.group(1)}
            if section == "modules":
                modules.append(cur)
            elif section == "milestones":
                milestones[m.group(1)] = ""
            continue
        m = re.match(r"^\s+(\w+):\s*(.*)$", line)
        if m and cur is not None:
            k, v = m.group(1), _val(m.group(2))
            if section == "milestones" and k == "name":
                milestones[cur["id"]] = v
            elif section == "modules":
                cur[k] = v
    return milestones, modules


def set_status(mid: str, status: str) -> None:
    if status not in STATUSES:
        sys.exit(f"status must be one of {STATUSES}")
    lines = REG.read_text(encoding="utf-8").splitlines()
    in_block, done = False, False
    for i, line in enumerate(lines):
        m = re.match(r"^\s*-\s+id:\s*(\S+)", line)
        if m:
            in_block = m.group(1) == mid
        elif in_block and re.match(r"^\s+status:", line):
            lines[i] = re.sub(r"status:.*$", f"status: {status}", line)
            done = True
            break
    if not done:
        sys.exit(f"module {mid} not found")
    REG.write_text("\n".join(lines) + "\n", encoding="utf-8")


def check(modules: list[dict]) -> list[str]:
    ids = {m["id"] for m in modules}
    errs = [f"{m['id']}: missing dep {d}" for m in modules for d in m.get("depends", []) if d not in ids]
    graph = {m["id"]: m.get("depends", []) for m in modules}
    color: dict[str, int] = {}

    def visit(n: str, path: list[str]) -> None:
        if color.get(n) == 1:
            errs.append("cycle: " + " -> ".join(path + [n]))
            return
        if color.get(n) == 2:
            return
        color[n] = 1
        for d in graph.get(n, []):
            visit(d, path + [n])
        color[n] = 2

    for n in graph:
        visit(n, [])
    return errs


def ready(modules: list[dict], ms_order: list[str]) -> list[dict]:
    status = {m["id"]: m["status"] for m in modules}
    out = [m for m in modules if m["status"] == "todo"
           and all(status.get(d) == "done" for d in m.get("depends", []))]
    return sorted(out, key=lambda m: (m["priority"], ms_order.index(m["milestone"]), m["id"]))


def write_board(milestones: OrderedDict, modules: list[dict], only: str | None) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = ["# PROGRESS — 자동 생성 (편집 금지, 원본: modules/registry.yaml)", "", f"갱신: {now}", "",
            "| 마일스톤 | 완료 | 진행 | 리뷰 | 막힘 | 전체 | P0 완료율 | 남은 세션(추정) |",
            "|---|---|---|---|---|---|---|---|"]
    for ms, name in milestones.items():
        mods = [m for m in modules if m["milestone"] == ms]
        if not mods:
            continue
        c = {s: sum(1 for m in mods if m["status"] == s) for s in STATUSES}
        p0 = [m for m in mods if m["priority"] == "P0"]
        p0done = sum(1 for m in p0 if m["status"] == "done")
        left = sum(SIZE_SESS.get(m["size"], 1) for m in mods if m["status"] != "done")
        rows.append(f"| {ms} {name} | {c['done']} | {c['doing']} | {c['review']} | {c['blocked']} | "
                    f"{len(mods)} | {p0done}/{len(p0)} | {left:g} |")
    rows += ["", "## 카드", ""]
    for ms, name in milestones.items():
        if only and ms != only:
            continue
        mods = [m for m in modules if m["milestone"] == ms]
        rows += [f"### {ms} · {name}", ""]
        rows += [f"- {ICON[m['status']]} `{m['id']}` {m['title']} · {m['priority']} · {m['size']}"
                 f"{' · ←' + ','.join(m['depends']) if m.get('depends') else ''}" for m in mods]
        rows.append("")
    text = "\n".join(rows)
    if not only:
        BOARD.parent.mkdir(parents=True, exist_ok=True)
        BOARD.write_text(text, encoding="utf-8")
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", action="store_true")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--set", nargs=2, metavar=("ID", "STATUS"))
    ap.add_argument("--milestone")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.set:
        set_status(*a.set)
    milestones, modules = load()
    errs = check(modules)
    if a.check:
        print("\n".join(errs) or "OK")
        sys.exit(1 if errs else 0)
    if a.next:
        for m in ready(modules, list(milestones))[: a.limit]:
            print(f"{m['id']}  [{m['priority']}/{m['size']}/{m['milestone']}]  {m['title']}  → {m['card']}")
        return
    text = write_board(milestones, modules, a.milestone)
    if a.milestone:
        print(text)
    else:
        done = sum(1 for m in modules if m["status"] == "done")
        print(f"PROGRESS.md 갱신 — {done}/{len(modules)} done" + (f" · 경고 {len(errs)}건" if errs else ""))


if __name__ == "__main__":
    main()
