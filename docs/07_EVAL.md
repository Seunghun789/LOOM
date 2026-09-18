# 07 · EVAL — 평가 하네스와 게이트 판정

## §1 원칙
- LOOM은 **정답을 알고 심은 데이터**로 스스로를 채점한다 (P5)
- 코드 테스트(pytest)는 "동작하는가", 평가 하네스는 "**맞는가**"를 본다. 둘 다 필요하다
- 기준을 몰래 낮추지 않는다. 기준 변경은 ADR

## §2 스위트
| 스위트 | 팩 | LLM | 시점 | 명령 | 도입 카드 |
|---|---|---|---|---|---|
| unit | — | 없음 | 매 편집 | `uv run pytest -q` | H-001 |
| tiny | tiny (2 시나리오) | fake | 매 커밋 | `uv run loom eval spine --pack var/packs/tiny --llm fake` | E-508 |
| spine20 | spine20 | real | G1, 프롬프트·검색 변경 | `uv run loom eval spine --pack var/packs/spine20 --llm real` | E-508 |
| ops | spine20 중 결함 14 | real | G2 | `uv run loom eval ops --pack var/packs/spine20` | R-610 |
| loop | spine20 중 용접·프레스 4 | real | G3 | `uv run loom loop run --eval` | A-806 |
| arch | spine20 | real | G3(P1) | `uv run loom eval arch` | A-807 |
| physics | rack2d 검증셋 | 없음 | M10 | `uv run loom sim eval` | F-1005 |

## §3 spine20 구성
| 종류 | 수 | 목적 |
|---|---|---|
| 결함 7종 × 대상 2 | 14 | 원인 순위·근거 경로 |
| 대조군(정상) | 2 | "원인 없음/정상 변동"이라고 답하는가 (false positive) |
| 근거 부족 | 3 | 원인 측 산출물 제거 → `insufficient_evidence=True` |
| 버전 인지 | 1 | 표준서 v2 이후 기준으로 판단하는가 |

## §4 지표 정의
| 지표 | 정의 | 대상 시나리오 |
|---|---|---|
| top1_acc | `root_causes[0].cause_urn == expected_root_cause_urn` 비율 | 결함 14 + 버전 1 |
| top3_acc | 기대 URN이 상위 3개 안 | 동일 |
| evidence_completeness | `|expected_evidence_types ∩ 경로 타입| / |expected_evidence_types|` 평균 | 결함 14 + 버전 1 |
| contract_a1_a3 | A-1·A-3 위반 없는 답 비율 | 전체 20 |
| version_test_pass | `expected_doc_version ∈ data_version` | 버전 1 |
| insufficient_recall | `insufficient_evidence=True` 비율 | 근거부족 3 |
| false_insufficient | 근거가 있는데 부족하다고 한 비율 | 결함 14 + 대조 2 + 버전 1 |
| control_specificity | 대조군에서 특정 설비를 원인으로 지목하지 않은 비율 | 대조 2 |
| tokens / latency | 합계·평균 | 전체 |

## §5 게이트 기준
| 게이트 | 스위트 | 기준 |
|---|---|---|
| **G1** | spine20 | **top1 ≥ 11/15** (결함 14 + 버전 1) · evidence_completeness ≥ 0.8 · contract_a1_a3 = 100% · version_test_pass = 1/1 · insufficient_recall = 3/3 · false_insufficient ≤ 2/17 · control_specificity ≥ 1/2 |
| **G2** | ops + 수동 | 알람→결정 흐름 성공 14/14 · 재시작 재개 테스트 통과 · 2회차 과거결정 인용 · 거부 기록 |
| **G3** | loop | 폐루프 4/4에서 승인 후 KPI(불량률) 결함 전 수준의 ±20% 이내 회복 · 예산 가드 발동 테스트 통과 |
| **G4** | tiny(fake) + 수동 | demo tour 완주 · 전체 unit·경계 통과 · PORTFOLIO.md 완성 |

> **G1 수치 해석**: 로드맵 문서의 "20개 중 14개(70%)"를 시나리오 종류별로 나눠 공정하게 채점한다. 원인 순위는 원인이 존재하는 15개로 보고(≥11, 73%), 대조군·근거부족 5개는 각자의 지표로 본다. 리포트에는 참고용으로 "20개 기준 통과 수"도 함께 쓴다.

## §6 리포트 형식 (`var/eval/<suite>-<YYYYMMDD-HHMM>.md`)
```markdown
# EVAL spine20 · 2026-11-27 14:10 · git <sha> · model <route/reason ids>
| 지표 | 값 | 기준 | 판정 |
...
## 시나리오별
| ID | 종류 | 기대 원인 | 1순위 | 근거완결 | 부족판정 | 토큰 | trace |
## 직전 대비
| 지표 | 이번 | 직전 | Δ |
## 실패 원인 층 (eval-runner)
```

## §7 회귀 방지
- 프롬프트(`prompts/*.md`) · 점수 규칙 · 검색 파라미터 변경 커밋은 spine20 전후 리포트 필수
- tiny 스위트는 CI(또는 pre-push 수동)에서 항상
- 실 LLM 결과는 변동이 있다 → 게이트 판정은 **2회 실행 평균**, 둘 다 리포트 커밋
