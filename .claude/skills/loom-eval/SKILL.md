---
name: loom-eval
description: LOOM 평가 하네스 사용법 — 스위트 실행, 지표 정의, 시나리오 추가, 실패 원인 층 분류, 게이트 판정. 평가를 돌리거나 정답률이 떨어졌을 때, 프롬프트·검색·그래프를 바꾼 뒤 사용.
---

# 평가 하네스

상세 기준: `docs/07_EVAL.md`.

## 스위트
| 스위트 | 명령 | LLM | 용도 |
|---|---|---|---|
| tiny | `uv run loom eval spine --pack var/packs/tiny --llm fake` | fake | 매 커밋, 1분 이내 |
| spine20 | `uv run loom eval spine --pack var/packs/spine20 --llm real` | 실제 | G1 판정, 프롬프트 변경 후 |
| ops | `uv run loom eval ops --pack var/packs/spine20` | 실제 | G2 |
| arch | `uv run loom eval arch --pack var/packs/spine20` | 실제 | G3 (단일/Supervisor/Swarm 비교) |

## 지표
- `top1_acc` · `top3_acc` : 기대 원인 URN이 1순위/3순위 안
- `evidence_completeness` : 기대 근거 타입 집합 ⊆ 답변 근거 경로 타입 집합의 비율 평균
- `version_test_pass` : `expected_doc_version`이 있는 시나리오에서 `data_version`에 해당 버전 포함
- `insufficient_recall` : `expect_insufficient` 시나리오 중 `insufficient_evidence=True` 비율
- `false_insufficient` : 근거가 있는데 부족하다고 한 비율 (낮을수록 좋음)
- `tokens`, `avg_latency_ms`

## 실패 원인 층 분류 (eval-runner가 수행)
| 층 | 증상 | 확인 | 대응 카드 방향 |
|---|---|---|---|
| 온톨로지 | 필요한 관계가 그래프에 없음 | `GraphView.paths(defect, expected)` 빈 결과 | O-401/O-405 규칙 보강 |
| 적재·매칭 | 설비명 해석 실패, HOLD 과다 | `var/match_misses.csv` | O-406 동의어 |
| 검색 | 근거가 있는데 gather가 못 가져옴 | trace의 tool 호출 결과 | E-501/E-502 |
| 추론 | 근거는 다 있는데 순위 틀림 | hypothesize 점수표 | E-504 점수 규칙/프롬프트 |
| 계약 | Answer 형식 위반 | A-1~A-3 검사 실패 | E-505 |

## 규칙
- 실 LLM 스위트는 **비용이 든다** → 오너 승인 후 실행, 결과 파일 커밋
- 프롬프트 변경 PR은 변경 전·후 spine20 리포트 2개가 있어야 merge
- 정답을 프롬프트에 새지 않게: 시나리오 question에 원인 설비 ID를 넣지 않는다 (P-207 규칙)
