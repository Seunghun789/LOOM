---
description: 의존성이 충족된 다음 카드 목록
allowed-tools: Bash(python3 tools/progress.py:*)
---

`python3 tools/progress.py --next --limit 8` 실행 결과를 표로 보여주고,
같은 섹터에서 병렬 가능한 카드 묶음(서로 의존 없음)이 있으면 `/parallel` 후보로 표시한다.
