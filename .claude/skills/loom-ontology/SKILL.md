---
name: loom-ontology
description: LOOM 코어 온톨로지 확장·검증 규칙 — 클래스/속성/관계 추가 방법, ISA-95·SOSA·PROV-O 정렬, 도메인·레인지, 추출 결과 연결. semantic 섹터 카드(O-4xx)나 새 엔티티 타입·관계가 필요할 때 사용.
---

# 온톨로지 규칙

파일: `src/loom/semantic/ontology/core_v0.yaml` · 클래스 목록 원문: `docs/00_PRODUCT.md` §4

## YAML 형식
```yaml
classes:
  Equipment:
    parent: Asset
    doc: "생산 설비 (ISA-95 Equipment)"
    props:
      vendor:      {type: string}
      installDate: {type: date}
      tipWear:     {type: number, unit: P1, telemetry: true}
relations:
  locatedIn: {domain: [Equipment, Sensor], range: [Station, Area, Line], inverse: hosts, doc: "물리적 위치"}
  suspectedCause: {domain: [Defect, Alarm], range: [Equipment, Parameter, Lot, Document, Event], inverse: suspectedEffect,
                   doc: "원인 가설 — 항상 ASSUMED, confidence 필수"}
```

## 추가 절차
1. 기존 클래스로 표현 가능한지 먼저 본다 (속성 추가 < 하위 클래스 추가 < 새 클래스)
2. 표준 정렬 확인: 설비 계층=ISA-95, 센서·관측=SOSA/SSN, 출처·파생=PROV-O, 제품·BOM=ISA-95 Material
3. `props`의 `telemetry: true`는 이력을 TelemetryStore에 둔다는 뜻
4. 관계에는 **domain·range·inverse·doc** 4개 필수
5. 핵심 클래스(Entity 계약에 영향: Answer·Decision·Criterion·Document) 변경은 ADR
6. `test_loads_*_classes_*_relations` 기대 개수 갱신

## 원인 가설은 관계가 아니라 판단이다
- `suspectedCause`는 S6·S8이 만든다. **적재(S2)·추출(S3)에서 만들지 않는다**
- 항상 `assumed` + confidence. 사람이 RCA를 승인하면(S7) `confirmedCause` 관계를 새로 만든다

## 설비명 매칭과의 관계
- 온톨로지는 `aliases` 속성을 모든 Asset 하위 클래스에 허용한다 → O-406 matcher의 후보 사전
- 매칭 실패 목록(`var/match_misses.csv`)은 주 1회 검토해 aliases로 승격 (사람 확인 = CONFIRMED)
