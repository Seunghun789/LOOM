---
name: loom-contracts
description: LOOM 계약(URN·Entity NGSI-LD 모양·Provenance·저장소 포트·Answer·Decision) 사용 예시와 흔한 실수. 엔티티를 만들거나 저장·조회하는 코드, Answer/Decision을 만드는 코드를 쓸 때 사용.
---

# 계약 사용 치트시트

원문: `docs/02_CONTRACTS.md`. 이 스킬은 **올바른 사용 예시**만 담는다.

## 엔티티 만들기
```python
from loom.core.public import make_urn, new_ulid, Entity, Property, Relationship, prov, utcnow

run_id = new_ulid()
src = "file://var/packs/spine20/S01/equipment.csv#row=3"
p = prov("ingest", src, run_id)                      # method=ingest → CONFIRMED

wr03 = Entity(
    id=make_urn("plantA", "Equipment", "WR-03"),
    type="Equipment",
    title="용접 로봇 3호기",
    properties={"vendor": Property(value="ACME", provenance=p)},
    relationships={"locatedIn": [Relationship(object=make_urn("plantA", "Station", "ST-W2"), provenance=p)]},
)
store.upsert(wr03)
```

## LLM이 추출한 값 (항상 ASSUMED)
```python
p = prov("extract_llm", f"llm://extract_criteria/{run_id}", run_id, confidence=0.72)   # → ASSUMED
crit = Entity(id=make_urn(site, "Criterion", "WS-WELD-v2-01"), type="Criterion",
              properties={"minValue": Property(value=5000.0, unitCode="NEW", provenance=p)})   # 5 kN → SI 저장 5000 N
```
> ⚠ unitCode는 `loom.core.units.UNIT_CODES`에 있는 코드만 쓴다. 없는 단위가 필요하면 추측하지 말고 C-102에 코드를 추가하는 작은 카드를 먼저 만든다.

## 사람 확인으로 승격
```python
from loom.core.public import promote
new_p = promote(old_property.provenance, by_person=make_urn(site, "Person", "owner"))
```

## 버전 인지 조회
```python
e_then = store.get(urn, as_of=scenario.window_end)   # 그 시점 최신 버전
history = store.history(urn)
```

## 관계 탐색 (저장소 수준 — 복잡하면 semantic.public.GraphView)
```python
store.triples(urn, rel="locatedIn", direction="out")  # [(src, rel, dst)]
```

## Answer 만들기 (S6만)
```python
from loom.core.answer import Answer, EvidencePath, EvidenceStep, RankedCause
# 규칙: insufficient_evidence=False 이면 evidence ≥ 1 (A-1), causes 내림차순 (A-2), 모든 URN 실존 (A-3)
```
직접 생성하지 말고 `loom.evidence.assemble.assemble_answer(...)`를 쓴다 (규칙 강제).

## 흔한 실수
| 실수 | 올바른 방법 |
|---|---|
| `datetime.now()` | `utcnow()` |
| `relationships={"locatedIn": Relationship(...)}` | 리스트로 감싼다 |
| 타입과 URN Type 불일치 (`type="Robot"`, URN은 `Equipment`) | 온톨로지 클래스명 하나로 통일 |
| 시계열 전체를 Entity 속성에 | 최신값만 속성에, 이력은 TelemetryStore |
| 섹터 코드에서 `build_container()` 호출 | 포트를 인자로 받는다 (§15) |
| 새 이벤트 kind를 문자열로 즉석 사용 | Literal에 없으면 ADR |
