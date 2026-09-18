# 04 · MODULE INDEX — 전체 모듈 목록

> 자동 생성 문서. 원본은 `modules/registry.yaml`. 상태는 `state/PROGRESS.md`에서 본다.

크기 S ≈ 1세션(Sonnet 1회 대화, 파일 ≤3, 코드 ≤150줄) · M ≈ 1.5세션(파일 ≤5, 코드 ≤350줄)

## 요약

| 마일스톤 | 모듈 수 | P0 | 예상 세션(전체) | 예상 세션(P0) |
|---|---|---|---|---|
| M0 Harness Bootstrap | 6 | 4 | 6.5 | 4 |
| M1 Core Contracts (S0) | 13 | 12 | 15.5 | 14 |
| M2 Proving Plant (P) | 8 | 8 | 10.5 | 10.5 |
| M3 Connect (S2) | 10 | 8 | 12 | 10 |
| M4 Semantic (S3) | 10 | 8 | 12.5 | 10.5 |
| M5 Evidence + Eval (S6) → G1 | 10 | 9 | 12.5 | 11.5 |
| M6 Operate (S7) → G2 | 11 | 10 | 14.5 | 13.5 |
| M7 Studio (S9) | 7 | 2 | 8.5 | 2.5 |
| M8 Agent Loop (S8) → G3 | 8 | 5 | 11 | 7 |
| M9 Twin Bind (S4·PRISM) | 6 | 4 | 7 | 4.5 |
| M10 Physics (S5) | 7 | 6 | 8.5 | 7.5 |
| M11 Capture (S1) | 5 | 1 | 6 | 1 |
| M12 Assembly & Release → G4 | 6 | 3 | 7 | 3.5 |
| **합계** | **107** | **80** | **132** | **100** |

## M0 · Harness Bootstrap

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [H-001](../modules/cards/H-001.md) | 저장소 골격·uv·pytest·ruff | harness | P0 | S | — | module-builder | H1, H2 |
| [H-002](../modules/cards/H-002.md) | import-linter 경계 규칙 | harness | P0 | S | H-001 | contract-guardian | H5 |
| [H-003](../modules/cards/H-003.md) | Claude Code 훅 연결 | harness | P0 | S | H-001, H-002 | module-builder | H5 |
| [H-004](../modules/cards/H-004.md) | 진행 보드 생성기 | harness | P0 | S | H-001 | module-builder | H2 |
| [H-005](../modules/cards/H-005.md) | 헤드리스 하네스 러너 | harness | P1 | M | H-004 | module-builder | H8, H11 |
| [H-006](../modules/cards/H-006.md) | Docker Compose: Postgres+pgvector | harness | P1 | S | H-001 | module-builder | — |

## M1 · Core Contracts (S0)

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [C-101](../modules/cards/C-101.md) | URN ID | core | P0 | S | H-001 | module-builder | H4 |
| [C-102](../modules/cards/C-102.md) | 단위·시간 유틸 | core | P0 | S | H-001 | module-builder | — |
| [C-103](../modules/cards/C-103.md) | Provenance 모델 | core | P0 | S | C-102 | module-builder | — |
| [C-104](../modules/cards/C-104.md) | Entity·Property·Relationship | core | P0 | M | C-101, C-103 | module-builder | — |
| [C-105](../modules/cards/C-105.md) | EntityStore 포트 + 메모리 구현 | core | P0 | M | C-104 | module-builder | — |
| [C-106](../modules/cards/C-106.md) | Postgres Entity·Telemetry 저장소 | core | P1 | M | C-105, C-107a, H-006 | module-builder | — |
| [C-107a](../modules/cards/C-107a.md) | TelemetryStore 포트 + 메모리 구현 | core | P0 | S | C-104 | module-builder | — |
| [C-107](../modules/cards/C-107.md) | 이벤트 모델·버스 | core | P0 | S | C-102 | module-builder | — |
| [C-108](../modules/cards/C-108.md) | LLM 포트·Fake·사용량 계측 | core | P0 | M | C-110 | module-builder | L1 |
| [C-109](../modules/cards/C-109.md) | Embedder 포트·해시·bge-m3 | core | P0 | S | C-110 | module-builder | — |
| [C-110](../modules/cards/C-110.md) | 설정·로깅·트레이스 | core | P0 | S | C-102 | module-builder | — |
| [C-111](../modules/cards/C-111.md) | 컨테이너 조립 | core | P0 | S | C-105, C-107a, C-107, C-108, C-109, C-110 | module-builder | — |
| [C-112](../modules/cards/C-112.md) | FastAPI 앱 팩토리 + /v0/entities | api | P0 | M | C-111 | module-builder | — |

## M2 · Proving Plant (P)

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [P-201](../modules/cards/P-201.md) | 라인 토폴로지 스펙 | plant | P0 | S | C-111 | module-builder | H3 |
| [P-202](../modules/cards/P-202.md) | SimPy 라인 시뮬레이터 | plant | P0 | M | P-201 | module-builder | — |
| [P-203](../modules/cards/P-203.md) | 공정·품질 모델 | plant | P0 | M | P-202 | module-builder | — |
| [P-204](../modules/cards/P-204.md) | 결함 주입 카탈로그 | plant | P0 | M | P-203 | module-builder | — |
| [P-205](../modules/cards/P-205.md) | 산출물 작성기 | plant | P0 | M | P-204 | module-builder | — |
| [P-206](../modules/cards/P-206.md) | 작업표준서 PDF 생성 | plant | P0 | S | P-201 | module-builder | — |
| [P-207](../modules/cards/P-207.md) | 시나리오 팩 빌더 CLI | plant | P0 | M | P-205, P-206 | module-builder | H3 |
| [P-208](../modules/cards/P-208.md) | what-if 러너 | plant | P0 | S | P-207 | module-builder | — |

## M3 · Connect (S2)

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [N-301](../modules/cards/N-301.md) | 커넥터 포트·레지스트리 | connect | P0 | S | C-111 | module-builder | — |
| [N-302](../modules/cards/N-302.md) | CSV·Excel 커넥터 | connect | P0 | S | N-301 | module-builder | H7 |
| [N-303](../modules/cards/N-303.md) | 시계열 커넥터 → TelemetryStore | connect | P0 | S | N-301, C-107a | module-builder | H7 |
| [N-304](../modules/cards/N-304.md) | 텍스트 로그 커넥터 | connect | P0 | S | N-301 | module-builder | H7 |
| [N-305](../modules/cards/N-305.md) | PDF 커넥터 (Docling) | connect | P0 | M | N-301 | module-builder | H7 |
| [N-306](../modules/cards/N-306.md) | 매핑 DSL·매퍼 | connect | P0 | M | N-302, N-303, N-304, N-305 | module-builder | H6 |
| [N-307](../modules/cards/N-307.md) | 매핑 검증 픽스처 | connect | P1 | S | N-306 | module-builder | — |
| [N-308](../modules/cards/N-308.md) | 적재 계보(lineage) | connect | P0 | M | N-306 | module-builder | — |
| [N-309](../modules/cards/N-309.md) | 팩 적재 파이프라인 CLI | connect | P0 | M | N-308, P-207 | module-builder | H4 |
| [N-310](../modules/cards/N-310.md) | MQTT 스트림 커넥터 | connect | P2 | S | N-309 | module-builder | — |

## M4 · Semantic (S3)

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [O-401](../modules/cards/O-401.md) | 코어 온톨로지 v0 | semantic | P0 | M | C-111 | module-builder | — |
| [O-402](../modules/cards/O-402.md) | 온톨로지 검증기 | semantic | P0 | S | O-401 | module-builder | — |
| [O-403](../modules/cards/O-403.md) | 그래프 뷰 (NetworkX 투영) | semantic | P0 | M | O-401 | module-builder | — |
| [O-404](../modules/cards/O-404.md) | 문서 → 운영기준 구조화 추출 | semantic | P0 | M | O-402, C-108, N-309 | module-builder | L1 |
| [O-405](../modules/cards/O-405.md) | 정비일지 추출 (map-reduce) | semantic | P0 | M | O-404, O-406 | module-builder | L1, L7 |
| [O-406](../modules/cards/O-406.md) | 설비명·동의어 매칭 | semantic | P0 | M | C-109, O-401 | module-builder | — |
| [O-407](../modules/cards/O-407.md) | 문서 버전·유효기간 | semantic | P0 | S | O-404 | module-builder | — |
| [O-408](../modules/cards/O-408.md) | 변경 영향 전파 | semantic | P1 | S | O-403 | module-builder | — |
| [O-409](../modules/cards/O-409.md) | SSoT 충돌 탐지 | semantic | P2 | S | O-403 | module-builder | — |
| [O-410](../modules/cards/O-410.md) | 추출 검토 큐 (ASSUMED→CONFIRMED) | semantic | P0 | S | O-404, O-405 | module-builder | — |

## M5 · Evidence + Eval (S6) → G1

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [E-501](../modules/cards/E-501.md) | 하이브리드 검색 인덱스 | evidence | P0 | M | O-410 | module-builder | L3 |
| [E-502](../modules/cards/E-502.md) | 질의 도구 세트 (@tool) | evidence | P0 | M | E-501, O-407 | module-builder | L2 |
| [E-503](../modules/cards/E-503.md) | 의도 라우터 노드 | evidence | P0 | S | E-502 | module-builder | L4 |
| [E-504](../modules/cards/E-504.md) | 온톨로지 RAG 질의 그래프 | evidence | P0 | M | E-503, E-505, E-506 | module-builder | L4, L12 |
| [E-505](../modules/cards/E-505.md) | Answer 조립기 | evidence | P0 | S | C-111 | module-builder | — |
| [E-506](../modules/cards/E-506.md) | 근거 부족 정책 | evidence | P0 | S | E-505 | module-builder | — |
| [E-507](../modules/cards/E-507.md) | 트레이스 뷰어 | evidence | P1 | S | E-504 | module-builder | L12 |
| [E-508](../modules/cards/E-508.md) | 평가 하네스 | evidence | P0 | M | E-504, P-207 | eval-runner | H12 |
| [E-509](../modules/cards/E-509.md) | 콘솔: 엔티티 탐색기 + 질의 | apps | P0 | M | E-508 | module-builder | — |
| [E-510](../modules/cards/E-510.md) | API: /v0/ask · /v0/entities/{urn}/graph | api | P0 | S | E-508, C-112 | module-builder | — |

## M6 · Operate (S7) → G2

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [R-601](../modules/cards/R-601.md) | 운영기준 평가기 | operate | P0 | M | E-508 | module-builder | — |
| [R-602](../modules/cards/R-602.md) | SPC·공정능력 | operate | P0 | M | C-111 | module-builder | — |
| [R-603](../modules/cards/R-603.md) | 이상 탐지기 | operate | P1 | S | R-602 | module-builder | — |
| [R-604](../modules/cards/R-604.md) | 알람 관리자 | operate | P0 | M | R-601, R-602 | module-builder | — |
| [R-605](../modules/cards/R-605.md) | RCA 초안 그래프 (서브그래프) | operate | P0 | M | R-604 | module-builder | L8 |
| [R-606](../modules/cards/R-606.md) | 대응 권고 + 과거 판단 메모리 | operate | P0 | M | R-605, R-609 | module-builder | L14 |
| [R-607](../modules/cards/R-607.md) | 자율 레벨 정책 | operate | P0 | S | C-111 | module-builder | — |
| [R-608](../modules/cards/R-608.md) | 승인 워크플로 (interrupt + checkpointer) | operate | P0 | M | R-606, R-607 | module-builder | L5, L6 |
| [R-609](../modules/cards/R-609.md) | 결정 로그·결과 회수 | operate | P0 | S | C-111 | module-builder | — |
| [R-610](../modules/cards/R-610.md) | 운영 지표 | operate | P0 | S | R-609 | module-builder | — |
| [R-611](../modules/cards/R-611.md) | 콘솔: 운영 화면 | apps | P0 | M | R-610, E-509 | module-builder | — |

## M7 · Studio (S9)

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [T-701](../modules/cards/T-701.md) | 리포트 데이터 빌더 | studio | P0 | S | R-610, E-508 | module-builder | — |
| [T-702](../modules/cards/T-702.md) | 리포트 렌더러 | studio | P0 | M | T-701 | module-builder | — |
| [T-703](../modules/cards/T-703.md) | 8D·5Why 초안 생성 | studio | P1 | S | T-702 | module-builder | L1 |
| [T-704](../modules/cards/T-704.md) | 위젯 스펙·렌더러 | studio | P1 | M | T-701 | module-builder | — |
| [T-705](../modules/cards/T-705.md) | 자연어 → 대시보드 생성 | studio | P1 | M | T-704 | module-builder | L1, L15 |
| [T-706](../modules/cards/T-706.md) | 주간 리포트 스케줄 CLI | studio | P2 | S | T-702 | module-builder | — |
| [T-707](../modules/cards/T-707.md) | 방법 패키지 내보내기 | studio | P1 | S | E-508, T-702 | module-builder | — |

## M8 · Agent Loop (S8) → G3

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [A-801](../modules/cards/A-801.md) | LOOM MCP 서버 | agent | P0 | M | R-608, E-508, P-208 | module-builder | H10, L13 |
| [A-802](../modules/cards/A-802.md) | 역할 에이전트 4종 | agent | P0 | M | A-801 | module-builder | L2, L9 |
| [A-803](../modules/cards/A-803.md) | Supervisor 오케스트레이션 | agent | P0 | M | A-802 | module-builder | L9 |
| [A-804](../modules/cards/A-804.md) | 스테이션 전담 에이전트 + 가설 보드 | agent | P1 | M | A-803 | module-builder | L7 |
| [A-805](../modules/cards/A-805.md) | 검증·반성 루프 + 예산 가드 | agent | P0 | S | A-803 | module-builder | L11 |
| [A-806](../modules/cards/A-806.md) | 폐루프 데모: 감지→이해→판단→예측→실행→학습 | agent | P0 | M | A-805, R-608, P-208 | module-builder | — |
| [A-807](../modules/cards/A-807.md) | Swarm(handoff) 변형과 비교 평가 | agent | P1 | M | A-806 | eval-runner | L10, H12 |
| [A-808](../modules/cards/A-808.md) | Claude Agent SDK 개발 오케스트레이터 (학습) | harness | P2 | S | H-005 | module-builder | H9 |

## M9 · Twin Bind (S4·PRISM)

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [W-901](../modules/cards/W-901.md) | PRISM 씬 ↔ URN 바인딩 | twin | P0 | S | O-410 | module-builder | — |
| [W-902](../modules/cards/W-902.md) | 상태 스트림 API (SSE) | twin | P0 | S | W-901, C-112 | module-builder | — |
| [W-903](../modules/cards/W-903.md) | 웹 셸 + PRISM 뷰어 임베드 | apps | P0 | M | W-902 | module-builder | — |
| [W-904](../modules/cards/W-904.md) | 상태 색상·알람 핀 | apps | P1 | M | W-903 | module-builder | — |
| [W-905](../modules/cards/W-905.md) | 사이드 AI 어시스턴트 | apps | P0 | S | W-903, E-510 | module-builder | — |
| [W-906](../modules/cards/W-906.md) | 시뮬 재생 타임라인 | apps | P2 | S | W-904 | module-builder | — |

## M10 · Physics (S5)

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [F-1001](../modules/cards/F-1001.md) | 시나리오 템플릿: 2D 서버랙 냉각 | physics | P0 | S | C-111 | module-builder | — |
| [F-1002](../modules/cards/F-1002.md) | 솔버 래퍼 (LBM 2D 열유동) | physics | P0 | M | F-1001 | module-builder | — |
| [F-1003](../modules/cards/F-1003.md) | 파라미터 스윕 + SimulationRun 엔티티 | physics | P0 | S | F-1002 | module-builder | — |
| [F-1004](../modules/cards/F-1004.md) | 서로게이트 U-Net 학습·추론 | physics | P0 | M | F-1003 | module-builder | — |
| [F-1005](../modules/cards/F-1005.md) | OOD·컨포멀 신뢰구간 | physics | P0 | M | F-1004 | module-builder | — |
| [F-1006](../modules/cards/F-1006.md) | 제약 설정 탐색 → L1 권고 | physics | P0 | S | F-1005, R-609 | module-builder | — |
| [F-1007](../modules/cards/F-1007.md) | 콘솔: GT vs 서로게이트 비교 | apps | P1 | S | F-1006 | module-builder | — |

## M11 · Capture (S1)

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [K-1101](../modules/cards/K-1101.md) | DXF → SVG + 속성 추출 | capture | P0 | S | O-410 | module-builder | — |
| [K-1102](../modules/cards/K-1102.md) | 도면 표 OCR → 기기목록 | capture | P1 | M | K-1101 | module-builder | — |
| [K-1103](../modules/cards/K-1103.md) | 사진측량 파이프라인 (COLMAP) | capture | P2 | M | C-111 | module-builder | — |
| [K-1104](../modules/cards/K-1104.md) | 포인트클라우드 측정·변화 탐지 | capture | P2 | S | K-1103 | module-builder | — |
| [K-1105](../modules/cards/K-1105.md) | 웹 포인트클라우드 뷰어 | apps | P2 | S | K-1104, W-903 | module-builder | — |

## M12 · Assembly & Release → G4

| ID | 제목 | 섹터 | 우선 | 크기 | 의존 | 담당 | 학습 패턴 |
|---|---|---|---|---|---|---|---|
| [Z-1201](../modules/cards/Z-1201.md) | 통합 CLI `loom` | cli | P0 | M | A-806 | module-builder | — |
| [Z-1202](../modules/cards/Z-1202.md) | 통합 API 게이트웨이 | api | P0 | S | Z-1201, W-902 | module-builder | — |
| [Z-1203](../modules/cards/Z-1203.md) | 웹 셸 통합 내비게이션 | apps | P1 | M | Z-1202, W-905 | module-builder | — |
| [Z-1204](../modules/cards/Z-1204.md) | Compose 전체 스택 프로파일 | harness | P1 | S | Z-1202 | module-builder | — |
| [Z-1205](../modules/cards/Z-1205.md) | JSON-LD 전체 내보내기 | core | P1 | S | Z-1201 | module-builder | — |
| [Z-1206](../modules/cards/Z-1206.md) | E2E 데모 투어·포트폴리오 | docs | P0 | S | Z-1201 | doc-keeper | — |
