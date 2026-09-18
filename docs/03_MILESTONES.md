# 03 · MILESTONES — 단축 경로 M0~M12 · 게이트 G1~G4

> 카드 상세는 `modules/cards/`, 전체 표는 `docs/04_MODULE_INDEX.md`, 상태는 `state/PROGRESS.md`.
> **단축 규칙: 각 마일스톤은 P0 카드만으로 닫는다. P1·P2는 게이트 통과 후 빈 슬롯에 넣는다.**

## §0 전체 그림

| 마일스톤 | 섹터 | P0 카드 | P0 세션 | 누적 | 게이트 | 한 줄 결과 |
|---|---|---|---|---|---|---|
| M0 Harness Bootstrap | 개발 하네스 | 4 | 4 | 4 | — | 훅·서브에이전트·진행보드가 도는 빈 저장소 |
| M1 Core Contracts | S0 | 12 | 14 | 18 | — | 계약 타입·포트·Fake LLM·컨테이너·/v0/entities |
| M2 Proving Plant | P | 8 | 10.5 | 28.5 | — | `loom plant build` → 정답지 달린 20시나리오 |
| M3 Connect | S2 | 8 | 10 | 38.5 | — | `loom ingest pack` 멱등 적재 + 계보 |
| M4 Semantic | S3 | 8 | 10.5 | 49 | — | 온톨로지·그래프·문서/정비일지 추출·설비명 매칭 |
| M5 Evidence + Eval | S6 | 9 | 11.5 | 60.5 | **G1** | 질문 → 근거 경로 답변, spine20 채점 |
| M6 Operate | S7 | 10 | 13.5 | 74 | **G2** | 알람 → RCA → 권고 → 승인(interrupt) → 결정 기록 |
| M7 Studio | S9 | 2 | 2.5 | 76.5 | — | 근거 링크 달린 주간 품질 리포트 |
| M8 Agent Loop | S8 | 5 | 7 | 83.5 | **G3** | MCP 도구 + Supervisor 팀 + 폐루프 |
| M9 Twin Bind | S4 | 4 | 4.5 | 88 | — | PRISM 3D에서 클릭 → 질문 |
| M10 Physics | S5 | 6 | 7.5 | 95.5 | — | 2D 냉각 서로게이트 + OOD → L1 권고 |
| M11 Capture | S1 | 1 | 1 | 96.5 | — | DXF → SVG + 설비 후보 |
| M12 Assembly | 조립 | 3 | 3.5 | **100** | **G4** | `loom demo tour` · 포트폴리오 |

세션 = Sonnet 대화 1회(계획·테스트·구현·리뷰·인계 포함, 60~90분). S=1, M=1.5.
전체(P1·P2 포함) 107카드 · 132세션.

## §1 캘린더 (주 15시간 ≈ 주 10세션 가정)

| 기간 | 마일스톤 | 누적 세션 | 비고 |
|---|---|---|---|
| 9/18~9/30 | M0 · M1 | 18 | M0는 대화형으로만 (하네스 러너 금지) |
| 10/1~10/13 | M2 | 28.5 | M1 후반부터 `harness/run_card.sh`로 S 카드 헤드리스 시험 |
| 10/14~10/30 | — | — | 피지컬AI 전문교육 (개발 정지). 과정 5(에이전트·RAG) 노트를 learning/L2·L3·L9에 |
| 11/2~11/15 | M3 · M4 | 49 | 커넥터 4종은 worktree 병렬 (H7·H11) |
| 11/16~11/27 | M5 | 60.5 | **G1 — 11월 포트폴리오 창 안** |
| 11/30~12/11 | M6 | 74 | **G2** |
| 12/14~12/24 | M7 · M8 | 83.5 | **G3** |
| 2027/1/4~1/15 | M9 · M10 | 95.5 | M9는 PRISM 스파이크 산출물 필요 |
| 1/18~1/22 | M11 · M12 | 100 | **G4** |

> **일정 충돌 (오너 결정)**: 이 캘린더는 LOOM 단축을 우선한다. PRISM 40시간 스파이크(원래 9/22~10/13)와 Isaac 실증(11/3~11/16)을 같은 주 15시간 안에 넣으면 LOOM이 약 5주 밀린다. 선택지: (A) PRISM 스파이크를 12월 M7 이후로 이동 (B) M2 기간에 주 5세션만 LOOM, 나머지 PRISM → G1이 12월 중순. 결정은 `state/DECISIONS.md`에 기록.

---

## M0 · Harness Bootstrap
| 항목 | 내용 |
|---|---|
| 목표 | Claude Code 운영 장치(CLAUDE.md·AGENTS.md·서브에이전트·스킬·커맨드·훅·진행보드)가 **실제로 도는** 빈 저장소 |
| 진입 조건 | 이 키트 폴더를 git 저장소로 초기화 (`git init && git add -A && git commit -m "chore: kit"`) |
| P0 | H-001 골격 · H-002 경계 규칙 · H-003 훅 · H-004 진행보드 |
| P1·P2 | H-005 헤드리스 러너 · H-006 Postgres Compose |
| 종료 기준 | ① 새 세션에서 HANDOFF가 자동 주입된다 ② `.py` 편집 시 ruff 피드백 ③ `python3 tools/progress.py --next`가 C-101을 제시 ④ `uv run lint-imports` 통과 |
| 학습 | H1 CLAUDE.md 메모리·import · H2 슬래시 커맨드 · H5 훅 |
| 데모 | 세션 시작 화면 캡처 (`docs/demo/m0.png`) |
| 위험 | 훅 스크립트 실행 권한·경로 → `/hooks`로 확인 |

## M1 · Core Contracts (S0)
| 항목 | 내용 |
|---|---|
| 목표 | `docs/02_CONTRACTS.md` §2~§9·§13·§15의 코드화. 이후 모든 섹터가 이 위에서 독립 개발 가능 |
| P0 | C-101 URN · C-102 단위·시간 · C-103 Provenance · C-104 Entity · C-105 EntityStore(메모리) · C-107a Telemetry · C-107 이벤트 · C-108 LLM 포트·Fake · C-109 Embedder · C-110 설정·트레이스 · C-111 컨테이너 · C-112 FastAPI |
| P1 | C-106 Postgres 저장소 |
| 병렬 | C-101 · C-102 동시 / C-103 · C-107 · C-110 동시 (wave 2~3) |
| 종료 기준 | ① `from loom.core.public import *` 로 계약 타입 전부 import ② 메모리 컨테이너로 엔티티 upsert·as_of·triples ③ `LOOM_LLM_FAKE=1`에서 구조화 출력 경로 테스트 통과 ④ `PUT/GET /v0/entities` |
| 학습 | H4 서브에이전트 분업(첫 적용: C-101) · L1 LangChain 모델·구조화 출력 기초(C-108) |
| 위험 | fake 모델의 structured output 미지원 → `structured()` 헬퍼로 우회 (loom-langchain §structured-output) |

## M2 · Proving Plant (P)
| 항목 | 내용 |
|---|---|
| 목표 | **정답을 아는 데이터**. spine20 팩(결함 14 · 대조군 2 · 근거부족 3 · 버전인지 1) |
| P0 | P-201 토폴로지 · P-202 SimPy · P-203 품질모델 · P-204 결함 7종 · P-205 산출물(지저분함) · P-206 표준서 PDF · P-207 팩 빌더 CLI · P-208 what-if |
| 종료 기준 | ① `uv run loom plant build --pack spine20` 2회 → manifest 해시 동일 ② 시나리오별 ground_truth 스키마 유효 ③ what-if로 팁 교체 시 불량률 감소 |
| 학습 | H3 스킬(loom-plant가 언제 로드되는지 관찰) |
| 위험 | 결함끼리 증상이 같아 원인 구별 불가 → loom-plant §결함 추가 체크리스트 4번(대조 신호) |

## M3 · Connect (S2)
| 항목 | 내용 |
|---|---|
| 목표 | 팩 → 엔티티·텔레메트리 적재. 모든 값이 원천 파일·행으로 되짚어진다 |
| P0 | N-301 포트 · N-302 CSV/Excel · N-303 시계열 · N-304 텍스트 로그 · N-305 PDF · N-306 매핑 DSL · N-308 계보 · N-309 파이프라인 CLI |
| P1·P2 | N-307 매핑 스냅샷 · N-310 MQTT |
| 병렬 | **N-302~N-305 4장을 worktree 병렬** (서로 의존 없음) — 첫 병렬 실습 |
| 종료 기준 | ① `loom ingest pack .../S01` 2회 실행 시 두 번째 새 버전 0 ② 임의 속성 `explain` → 파일·행 ③ PDF·정비일지 RawRecord가 `var/raw/<run_id>/`에 |
| 학습 | H6 Plan mode + ADR(N-306 매핑을 YAML로 할지) · H7 병렬 서브에이전트 · H11 worktree |

## M4 · Semantic (S3)
| 항목 | 내용 |
|---|---|
| 목표 | 데이터에 의미. 정비일지·표준서에서 운영기준·정비기록을 **ASSUMED**로 추출하고 설비명 흔들림을 해석 |
| P0 | O-401 온톨로지 · O-402 검증 · O-403 그래프 · O-404 문서 추출 · O-405 정비일지 map-reduce · O-406 설비명 매칭 · O-407 문서 버전 · O-410 검토 큐 + `run_semantic_stage` |
| P1·P2 | O-408 변경 영향 · O-409 SSoT 충돌 |
| 종료 기준 | ① spine20 표기 변형 전수 top1 매칭 ② 임의 Defect → Equipment → MaintenanceRecord 경로 존재 ③ 표준서 v2 유효일 이후 기준이 v2 |
| 학습 | L1 구조화 출력(O-404) · L7 LangGraph Send map-reduce(O-405) |
| 위험 | 실 LLM 추출 품질 → 표 행은 규칙 파싱 우선, LLM은 모호한 셀만 (비용·재현성) |

## M5 · Evidence + Eval (S6) → **G1**
| 항목 | 내용 |
|---|---|
| 목표 | "어제 2라인 용접 불량 왜 늘었어?" → 원인 순위 + 근거 경로 + 데이터 버전 + 부족하면 부족하다고 |
| P0 | E-501 하이브리드 검색 · E-502 도구 6종 · E-503 라우터 · E-504 질의 그래프 · E-505 Answer 조립 · E-506 근거부족 정책 · E-508 평가 하네스 · E-509 Streamlit 콘솔 · E-510 /v0/ask |
| P1 | E-507 트레이스 뷰어 |
| **G1 기준** | spine20 실 LLM(2회 평균): 원인 1순위 ≥ 11/15 · evidence_completeness ≥ 0.8 · 근거경로 존재 100% · A-3(URN 실존) 100% · version_test_pass 1/1 · insufficient_recall 3/3 · false_insufficient ≤ 2/17 |
| 판정 | `/gate G1` → eval-runner. 리포트 `var/eval/g1-<date>.md` 커밋, 콘솔 스크린샷 `docs/demo/g1.png` |
| 학습 | L2 도구 · L3 검색 · L4 StateGraph 라우팅 · L12 트레이싱 · H12 평가 하네스 |
| G1 실패 시 | eval-runner 원인 층 분류 → 층별 보강 카드 `_proposed/` → 오너 승인 → 재판정 (최대 2회, 이후 기준 재검토 ADR) |

## M6 · Operate (S7) → **G2**
| 항목 | 내용 |
|---|---|
| 목표 | 알람에서 결정 기록까지. 두 번째 같은 이상에서 **첫 결정이 근거로 인용** |
| P0 | R-601 기준 평가 · R-602 SPC · R-604 알람 · R-605 RCA 서브그래프 · R-606 권고+메모리 · R-607 자율 레벨 · R-608 승인 workflow · R-609 결정 로그 · R-610 지표 · R-611 운영 콘솔 |
| P1 | R-603 PyOD 이상탐지 |
| **G2 기준** | ① L2 케이스가 interrupt에서 멈추고, **프로세스 재시작 후** 같은 thread_id로 승인 재개 ② 용접 시나리오 2회차 권고에 1회차 Decision URN 인용 ③ 거부된 결정도 기록 ④ ops 지표 표시 |
| 학습 | L5 checkpointer · L6 interrupt HITL · L8 서브그래프 · L14 Store 메모리 |

## M7 · Studio (S9)
| 항목 | 내용 |
|---|---|
| 목표 | **개인업무 적용 출구** — 근거 링크 달린 주간 품질 리포트 |
| P0 | T-701 데이터 빌더 · T-702 리포트 렌더러 |
| P1·P2 | T-703 8D 초안 · T-704 위젯 스펙 · T-705 자연어→대시보드 · T-706 스케줄 · T-707 방법 패키지 |
| 종료 기준 | `loom report weekly` → 파레토·추이·RCA 요약·결정 요약·근거 링크 |
| 학습 | (P1에서) L1·L15 스트리밍 |

## M8 · Agent Loop (S8) → **G3**
| 항목 | 내용 |
|---|---|
| 목표 | E8 R&D 과제 구조(역할 분담 멀티에이전트)와 CTO 발표의 자율 순환을 P 라인에서 닫는다 |
| P0 | A-801 MCP 서버 · A-802 역할 에이전트 · A-803 Supervisor · A-805 검증 루프 · A-806 폐루프 |
| P1·P2 | A-804 스테이션 전담 + 가설 보드 · A-807 Swarm 비교 · A-808 Agent SDK 변형 |
| **G3 기준** | ① Claude Code에서 MCP `loom.ask` 호출 성공 ② 폐루프 1회: 결함 → 알람 → 팀 RCA → what-if → 승인 → 시뮬 적용 → KPI 회복 → Outcome 저장 ③ 라운드·토큰 예산 가드 동작 ④ (P1 완료 시) 단일/Supervisor/Swarm 비교 리포트 |
| 학습 | H10 MCP · L9 Supervisor · L11 반성 루프 · L13 MCP adapters · (P1) L7 · L10 · H9 |

## M9 · Twin Bind (S4 / PRISM)
| 항목 | 내용 |
|---|---|
| 목표 | PRISM 3D에서 설비 클릭 → 질문 컨텍스트, 알람이 3D에 |
| 전제 | PRISM 스파이크 산출물 (없으면 W-901의 더미 scene 헬퍼) |
| P0 | W-901 바인딩 · W-902 SSE 스트림 · W-903 웹 셸+뷰어 · W-905 사이드 어시스턴트 |
| P1·P2 | W-904 상태 색상·핀 · W-906 타임라인 |
| 종료 기준 | 클릭한 설비가 질문에 들어가고, 답변 근거 URN 클릭 시 3D 포커스 |

## M10 · Physics (S5)
| 항목 | 내용 |
|---|---|
| 목표 | NFLOW Ai 데이터센터 냉각 사례의 2D 학습판 |
| P0 | F-1001 템플릿 · F-1002 솔버 · F-1003 스윕 · F-1004 U-Net · F-1005 OOD·컨포멀 · F-1006 제약 최적화→L1 |
| P1 | F-1007 비교 콘솔 |
| 종료 기준 | 포아죄유 검증 통과 · 서로게이트 1초 내 · 컨포멀 커버리지 ≈90% · 학습 범위 밖 경고 · 권고가 Decision(L1)로 기록 |

## M11 · Capture (S1)
| P0 | K-1101 DXF → SVG + 블록 속성 → ASSUMED 설비 후보 |
|---|---|
| P1·P2 | K-1102 도면 표 OCR · K-1103 COLMAP · K-1104 포인트클라우드 측정 · K-1105 웹 뷰어 |

## M12 · Assembly & Release → **G4**
| 항목 | 내용 |
|---|---|
| P0 | Z-1201 통합 CLI · Z-1202 API 게이트웨이 · Z-1206 데모 투어·포트폴리오 |
| P1 | Z-1203 웹 셸 내비 · Z-1204 Compose 프로파일 · Z-1205 JSON-LD 내보내기 |
| **G4 기준** | ① `loom demo tour --pack tiny --llm fake` 완주 (CI) ② 실 LLM 투어 녹화 ③ PORTFOLIO.md에 G1~G3 수치·스크린샷·아키텍처·실패 분석 ④ 전체 테스트·경계 통과 |

---

## §2 게이트 운영 규칙
1. 게이트 필수 P0 카드가 모두 `done`이어야 판정 시작
2. 판정은 `/gate Gn` → eval-runner. 실 LLM 비용은 판정 전에 오너 승인
3. 통과 기록: `state/DECISIONS.md` + `var/eval/` 리포트 커밋 + `docs/demo/` 스크린샷
4. 실패 2회 → 기준 자체를 재검토하는 ADR (기준을 몰래 낮추지 않는다)
5. 게이트 통과 직후 1세션은 **리팩터·P1 정리·learning 노트 복습** 전용
