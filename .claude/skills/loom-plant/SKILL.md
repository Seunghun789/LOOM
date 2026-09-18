---
name: loom-plant
description: 가상 실증공장(Proving Plant) 시나리오·결함 작성 규칙 — 토폴로지 YAML, 결함 주입, 산출물 지저분함, 정답지, 결정성. plant 섹터 카드(P-2xx)를 구현하거나 새 결함·시나리오를 추가할 때 사용.
---

# 가상 실증공장 작성 규칙

## 왜 있는가
E8조차 "제조사는 검증 전에 데이터를 안 주고, 데이터 없이는 검증이 안 된다"는 악순환 때문에 공장을 인수한다. LOOM은 **원인을 알고 심은 데이터**로 이 악순환을 개인 수준에서 끊는다. 그래서 **정답지가 제품의 일부**다.

## 기본 라인 (press_weld_v0)
```
PR-01 ─┐                  ┌─ WR-01 ─┐
       ├─ CV-01 ─ ST-W1 ──┤         ├─ CV-02 ─┐
PR-02 ─┘                  └─ WR-02 ─┘         │
                          ┌─ WR-03 ─┐         ├─ CV-03 ─ IN-01
                ST-W2 ────┤         ├─────────┘
                          └─ WR-04 ─┘
```
PRISM `reference/press-weld-line.html`과 같은 라인이다. 이름·배치가 달라지면 PRISM 쪽이 옳다.

## 결함 추가 체크리스트
1. `FaultKind` Literal에 이름 추가 → **계약 변경이므로 ADR** (docs/02_CONTRACTS.md §12)
2. `faults.py`에 overrides 함수 + `FAULT_EFFECTS` 인과 설명 한 줄
3. 결함이 **어느 산출물에 흔적을 남기는지** 표로 명시 (timeseries / inspections / alarms / maintenance_log / docs)
4. 대조 신호: 같은 증상을 내는 다른 결함과 구별되는 흔적이 최소 1개 있어야 한다 (예: sensor_offset은 검사 결과는 정상)
5. `test_each_fault_changes_target_kpi` 파라미터에 추가

## 지저분함 규칙 (현실감)
| 대상 | 규칙 |
|---|---|
| 설비명 | 한 설비당 표기 변형 3~5개 (`용접로봇3호`, `W/R-03`, `웰딩 로봇 #3`, `WR03`) |
| 정비일지 | 약어(`팁교`, `캘`), 오타 1%, 날짜 형식 혼용(`9/16`, `2026-09-16`) |
| 시계열 | 결측 0.5%, 스파이크 0.1% |
| CSV | 인코딩 cp949 파일 1개 섞기 |
| 문서 | v2 개정 사항은 개정이력 표와 본문 양쪽에 |

## 결정성
- 모든 난수는 시나리오 `seed`에서 파생한 `numpy.random.default_rng(seed + k)`
- LLM으로 텍스트를 생성하지 않는다 (템플릿 조합만)
- `manifest.json`의 sha256이 재빌드 시 동일해야 한다

## 질문 작성 규칙
- 운영자 말투, 원인 설비 ID를 넣지 않는다: ✅ "어제 2라인 용접 불량 왜 늘었어?" ❌ "WR-03 팁 마모 때문에 불량이 늘었나?"
- 시간 표현은 시나리오 window 기준 상대 표현("어제", "오늘 오후") + 평가 시 `now`를 고정

## 근거 부족 시나리오
- 원인 측 산출물을 제거하고 `removed_artifacts`에 기록 (예: weld_tip_wear인데 maintenance_log와 tipWear 시계열 제거)
- 기대 동작: `insufficient_evidence=True`와 `missing`에 무엇이 없는지
