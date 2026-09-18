# ADR-001 · 단축 스택: 메모리 저장소·Streamlit·NetworkX로 G1까지

- 상태: accepted
- 날짜: 2026-09-17 · 제안: 키트 설계 · 검토: 오너
- 영향 계약 절: §6 저장소 포트, §15 컨테이너

## 맥락
LOOM을 최대한 단축해 G1(근거 질의)에 도달해야 한다. 원 로드맵은 Postgres+pgvector·Neo4j 투영·React UI를 초기부터 두었다. 1인·입문 코딩·Sonnet 세션 체제에서 운영 컴포넌트가 많을수록 세션당 설정·디버깅 비용이 커진다.

## 선택지
| 안 | 내용 | 장점 | 단점 |
|---|---|---|---|
| A | Postgres·Neo4j·React를 M1부터 | 운영 환경과 동일 | 초기 세션 대부분이 인프라 |
| B | 포트는 계약으로 고정하고 구현은 Memory·NetworkX·Streamlit으로 시작 | 테스트 빠름, 섹터 로직에 집중 | 대용량·동시성 검증은 뒤로 |

## 결정
B. 저장소는 `EntityStore`/`TelemetryStore` Protocol을 계약으로 고정하고 `MemoryEntityStore`로 G1까지 간다. Postgres(C-106)는 P1, 같은 계약 테스트를 파라미터화해 교체 가능성을 보장한다. UI는 G3까지 Streamlit, M9에서 PRISM과 함께 React.

## 결과
- 계약 변경: 없음
- 후속 카드: C-106(P1), W-903(M9)
- 위험: 메모리 저장소 as_of 구현이 Postgres와 달라질 수 있음 → C-106에서 동일 테스트 강제
