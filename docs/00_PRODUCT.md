# 00 · PRODUCT — LOOM 제품 정의

> 원본 설계: `docs/research/02_LOOM_제조AI_재조립_청사진_로드맵.md` · `docs/research/01_E8_이에이트_피지컬AI_플랫폼_분석.md`
> 이 문서는 개발에 필요한 부분만 압축한다.

## §1 한 줄
**질문 하나에 근거와 함께 답하고, 사람이 승인한 판단을 기록하며, 그 기록으로 다음 판단이 나아지는** 제조 운영 지능 스택.

## §2 원칙 (코드 리뷰 기준으로도 쓴다)
| # | 원칙 | 코드에서의 모습 |
|---|---|---|
| P1 | 자동화가 아니라 지능화 — 감지와 제어 사이의 이해·판단을 채운다 | S3 온톨로지 + S6 근거 질의 + S7 판단 |
| P2 | 자율 수준을 판단 유형마다 명시 | `AutonomyLevel` L0~L3, `autonomy_policy.yaml` |
| P3 | 근거 없는 답은 답이 아니다 | `Answer.evidence`, A-1~A-3, `insufficient_evidence` |
| P4 | 판단은 자산이다 | `Decision`·`Outcome` 엔티티, `DecisionMemory` |
| P5 | 스스로를 채점한다 | 가상 실증공장 정답지 + 평가 하네스 |
| P6 | 스키마를 먼저 고정한다 | 코어 온톨로지 v0, 계약 문서 |
| P7 | 실증공장을 시뮬레이션으로 먼저 만든다 | `loom.plant` |
| P8 | 트윈은 로봇 학습 환경으로 이어진다 | S4 = PRISM, Isaac 익스포트 연계 (M9 이후) |

## §3 섹터 (= src/loom 패키지)
| 섹터 | 패키지 | E8 원천 | 우선 |
|---|---|---|---|
| S0 Core | `core` | 전 제품 공통 | 1 |
| P Proving Plant | `plant` | Proving Plant 전략 | 1 |
| S2 Connect | `connect` | NDX Connector·Core | 1 |
| S3 Semantic | `semantic` | NAXiS 구조화 | 1 |
| S6 Evidence | `evidence` | NAXiS 탐색·온톨로지 RAG | 1 (G1) |
| S7 Operate | `operate` | NAX Ops | 2 (G2) |
| S9 Studio | `studio` | NAXiS 앱·NFLOW 리포트 | 3 |
| S8 Agent | `agent` | E8 산업AI에이전트 R&D | 3 (G3) |
| S4 Twin | `twin` + `apps/web` | NDX Pro / **PRISM** | 4 |
| S5 Physics | `physics` | NFLOW / NFLOW Ai | 5 |
| S1 Capture | `capture` | NDX Cloud | 6 |

**단축 원칙**: G1(근거 질의)까지 P0 카드만. S9는 개인업무 적용 출구라 S8보다 앞. S4·S5·S1은 G3 이후.
원래 로드맵의 "S4 트윈 바인딩을 물리보다 먼저"는 유지하되, S8 폐루프의 '예측' 단계는 **S5 대신 P의 what-if 시뮬(P-208)**로 먼저 닫는다.

## §4 코어 온톨로지 v0 — 구체 클래스 37 + 추상 1

추상: `Asset` (Site·Area·Line·Station·Equipment·Component·Sensor의 부모. `aliases` 속성 제공. 개수에서 제외)

| 그룹 | 클래스 | 정렬 표준 |
|---|---|---|
| 공간·설비 (7) | Site · Area · Line · Station · Equipment · Component · Sensor | ISA-95, SOSA/SSN |
| 제품·공정 (5) | Product · Part · BOMItem · ProcessSpec · Parameter | ISA-95 |
| 생산 실적 (5) | WorkOrder · Lot · Measurement · Inspection · Defect | ISA-95 |
| 이벤트 (4) | Alarm · Event · MaintenanceRecord · ChangeRequest | — |
| 지식 (3) | Document · Criterion · Hypothesis | PROV-O |
| 판단 (6) | Question · Answer · EvidencePath · Decision · Approval · Outcome | PROV-O |
| 예측 (4) | Scenario · SimulationRun · SurrogateModel · Prediction | — |
| 사람 (3) | Person · Role · Responsibility | — |

관계 13: `partOf` · `locatedIn` · `feeds` · `measures` · `produces` · `hasDefect` · `suspectedCause` · `governedBy` · `documentedIn` · `derivedFrom` · `supersedes` · `approvedBy` · `simulates`

## §5 기본 데모 시나리오
가상 **차체 프레스-용접 라인**(프레스 2 · 용접로봇 4 · 컨베이어 3 · 검사 1). 결함 7종을 원인을 알고 주입한 **spine20 팩**(20 시나리오).
대표 질문: "어제 2라인 용접 불량이 늘어난 원인은?" → 기대 답: WR-03 팁 마모, 근거 경로 Defect → Lot → Station → Equipment → (tipWear 추이 · 정비일지 누락) · 작업표준서 버전.

## §6 범위 밖 (개념 학습만)
Overset 격자 · Multi-GPU 대규모 · 1억 입자 SPH · 공력음향 · LB/오토스케일 · 사용량 과금 · 실제 PLC 제어 · 회사 데이터

## §7 게이트
| 게이트 | 한 줄 | 수치 기준 요약 (상세 docs/07_EVAL.md) |
|---|---|---|
| **G1 Spine** | 질문 하나에 근거와 함께 답한다 | spine20 원인 1순위 ≥ 11/15 · 근거경로 100% · 버전 테스트 통과 · 근거부족 3/3 |
| **G2 Operate** | 알람에서 결정 기록까지 돈다 | 용접 시나리오 2회차 권고가 1회차 결정 인용 · 재시작 후 승인 재개 |
| **G3 Loop** | 에이전트 팀이 폐루프를 돈다 | 폐루프 후 KPI 회복 · 단일/Supervisor/Swarm 비교 리포트 |
| **G4 Release** | 하나의 제품으로 조립된다 | `loom demo tour` 완주 · 포트폴리오 1쪽 |
