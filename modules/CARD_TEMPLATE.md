---
id: X-000
title: <제목>
sector: <core|plant|connect|semantic|evidence|operate|studio|agent|twin|physics|capture|api|cli|apps|harness|docs>
milestone: M?
priority: P0|P1|P2
size: S|M          # S: 파일≤3·코드≤150줄 / M: 파일≤5·코드≤350줄. 넘으면 카드 분할
depends: []
agent: module-builder
patterns: []
---

# X-000 · <제목>

## 1. 목표
<한두 문장. "무엇이 가능해지는가">

## 2. 의존
- <ID — 제목>

## 3. 생성·수정 파일
- `src/loom/<sector>/<module>.py`
- `tests/<sector>/test_<module>.py`

## 4. 공개 인터페이스
```python
# 시그니처만. 계약 문서 절 참조
```

## 5. 구현 단계
- 

## 6. 수용 테스트 (Definition of Done)
- [ ] test_...
- [ ] `uv run pytest -q` · `uv run ruff check` · `uv run lint-imports`
- [ ] 섹터 `public.py` 반영
- [ ] registry status → review, HANDOFF 갱신

## 7. 읽을 것 (이 목록 밖은 열지 않는다)
- 이 카드
- `docs/02_CONTRACTS.md §N`
- `src/loom/<dep-sector>/public.py`

## 8. 금지
- 다른 섹터 내부 import · 계약 변경 · 실 LLM 단위 테스트 · 300줄 초과

## 9. 학습 포인트
<패턴 ID>

> 새 카드는 `modules/cards/_proposed/`에 먼저 두고, 오너 승인 후 `modules/registry.yaml`에 블록을 추가한다.
