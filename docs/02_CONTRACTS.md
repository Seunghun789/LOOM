# 02 · CONTRACTS — 모든 모듈이 지키는 계약

> **이 문서가 모듈 조립의 유일한 접점이다.** 모듈은 서로의 내부 코드를 읽지 않는다. 이 문서의 타입·시그니처와 각 섹터의 `public.py`만 본다.
> 계약을 바꾸려면 ADR(`docs/adr/`)을 먼저 쓰고 `contract-guardian` 서브에이전트 리뷰를 받는다.

목차: §1 패키지·경계 · §2 ID · §3 단위·시간 · §4 Provenance · §5 Entity · §6 저장소 포트 · §7 텔레메트리 · §8 이벤트 · §9 LLM·임베딩 포트 · §10 Answer · §11 Decision · §12 Ground Truth · §13 API 규약 · §14 테스트 규약 · §15 컨테이너(조립)

---

## §1 패키지 구조와 경계 규칙

```
src/loom/
  core/       S0  — 계약 타입·포트·설정·컨테이너. 내부 의존 없음
  plant/      P   — 가상 실증공장
  connect/    S2  — 커넥터·매핑·계보
  semantic/   S3  — 온톨로지·그래프·추출·매칭
  evidence/   S6  — 검색·질의 그래프·Answer·평가
  operate/    S7  — 기준·SPC·알람·RCA·승인·결정로그
  studio/     S9  — 리포트·위젯
  agent/      S8  — 역할 에이전트·오케스트레이션·MCP
  twin/       S4  — PRISM 바인딩·상태 스트림
  physics/    S5  — 솔버 래퍼·서로게이트·OOD
  capture/    S1  — 사진측량·도면
  api/        조립 — FastAPI 앱 (모든 public 사용 가능)
  cli/        조립 — typer CLI (모든 public 사용 가능)
apps/
  console/    Streamlit UI (M5~M7)
  web/        React 셸 + PRISM 뷰어 (M9~)
```

**경계 규칙 (import-linter로 강제, `.importlinter`)**

| 규칙 | 내용 |
|---|---|
| B-1 | `loom.core`는 `loom.*` 어떤 것도 import하지 않는다 |
| B-2 | 섹터 패키지는 `loom.core`와 **다른 섹터의 `public` 모듈만** import한다 (`from loom.semantic.public import GraphView`) |
| B-3 | 섹터의 `public.py`는 그 섹터가 외부에 여는 **유일한 표면**이다. 여기에 없는 이름은 내부 구현이다 |
| B-4 | `loom.api`·`loom.cli`·`apps/*`만 여러 섹터를 조립한다 |
| B-5 | 순환 의존 금지. 허용 방향: `plant → (없음)`, `connect → core`, `semantic → connect.public`, `evidence → semantic.public, connect.public`, `operate → evidence.public, semantic.public`, `studio → operate.public, evidence.public`, `agent → operate.public, evidence.public, plant.public`, `twin → semantic.public, operate.public`, `physics → core`, `capture → semantic.public` |

---

## §2 ID — Entity URN (`loom.core.ids`)

```
urn:loom:{site}:{Type}:{local_id}
  site     : [a-z0-9-]+            예) plantA
  Type     : PascalCase 클래스명     예) Equipment  (온톨로지 클래스와 동일)
  local_id : [A-Za-z0-9._-]+       예) WR-03, L20260916-042
```

```python
from typing import NamedTuple

URN_PREFIX = "urn:loom"

class UrnParts(NamedTuple):
    site: str
    etype: str
    local_id: str

def make_urn(site: str, etype: str, local_id: str) -> str: ...
def parse_urn(urn: str) -> UrnParts: ...          # 형식 위반 시 ValueError
def is_urn(s: str) -> bool: ...
```

- 같은 현실 대상은 **하나의 URN**이다. 3D 객체·센서값·시뮬레이션·결정 기록이 모두 이 URN을 가리킨다.
- 비결정적 ID가 필요한 기록(Answer·Decision·Run)은 `local_id`에 ULID를 쓴다: `make_urn("plantA","Decision", new_ulid())`.

---

## §3 단위·시간 (`loom.core.units`, `loom.core.timeutil`)

| 규칙 | 내용 |
|---|---|
| U-1 | 저장은 SI 기준(m, s, kg, K 또는 °C 명시, A, V, W). 표시는 UI에서 변환 |
| U-2 | `unitCode`는 UN/CEFACT Common Code를 쓴다. 사용 코드 목록은 `loom.core.units.UNIT_CODES` 한 곳에만 둔다 |
| U-3 | 좌표·치수 규칙은 PRISM과 동일(Z-up, m 저장, mm 표시). PRISM `units.ts`와 값이 달라지면 PRISM이 옳다 |
| T-1 | 모든 datetime은 **timezone-aware UTC**. naive datetime은 생성 즉시 ValueError |
| T-2 | 직렬화는 ISO 8601 `Z` 접미사 |

```python
UNIT_CODES: dict[str, str]   # {"MTR": "metre", "MMT": "millimetre", "SEC": "second", "CEL": "degree Celsius",
                             #  "KEL": "kelvin", "AMP": "ampere", "VLT": "volt", "WTT": "watt", "NEW": "newton",
                             #  "P1": "percent", "C62": "one (dimensionless)", "HUR": "hour"}
def utcnow() -> datetime: ...
def ensure_utc(dt: datetime) -> datetime: ...     # naive → ValueError
def to_iso(dt: datetime) -> str: ...
```

---

## §4 Provenance (`loom.core.provenance`)

**모든 값에는 출처와 확신 상태가 붙는다.** PRISM D-10과 같은 3상태를 쓴다.

```python
from enum import StrEnum
from typing import Literal
from pydantic import BaseModel, Field

class ProvStatus(StrEnum):
    CONFIRMED = "confirmed"   # 사람이 확인했거나, 계측·원천 시스템에서 직접 적재
    ASSUMED   = "assumed"     # 모델·추출·매칭·추정으로 생성. 사람 확인 전
    HOLD      = "hold"        # 충돌·의심으로 사용 보류

ProvMethod = Literal["ingest", "extract_llm", "match", "simulate", "derive", "human"]

class Provenance(BaseModel):
    status: ProvStatus
    method: ProvMethod
    source: str                       # 예) "file://packs/S01/equipment.csv#row=12", "llm://extract/<run_id>"
    run_id: str                       # 적재·추출·추론 실행 ID (ULID)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    recorded_at: datetime             # UTC
```

| 규칙 | 내용 |
|---|---|
| P-1 | `method in {"extract_llm","match","simulate","derive"}` → 기본 `ASSUMED` |
| P-2 | `ASSUMED → CONFIRMED` 승격은 `method="human"`인 새 Provenance로만 한다 (이력 보존) |
| P-3 | `HOLD` 값은 Evidence 답변 근거로 쓰지 않는다 (S6 필터) |
| P-4 | 근거 경로의 각 단계는 `source`를 끝까지 따라가면 원천 파일·행 또는 실행 기록에 닿아야 한다 |

---

## §5 Entity — NGSI-LD 모양 (`loom.core.entity`)

```python
from typing import Any, Literal
from pydantic import BaseModel, Field

class Property(BaseModel):
    type: Literal["Property"] = "Property"
    value: Any
    unitCode: str | None = None
    observedAt: datetime | None = None
    provenance: Provenance

class Relationship(BaseModel):
    type: Literal["Relationship"] = "Relationship"
    object: str                         # 대상 URN
    observedAt: datetime | None = None
    provenance: Provenance

class Entity(BaseModel):
    id: str                             # URN (§2)
    type: str                           # 온톨로지 클래스명 == URN의 Type
    title: str | None = None
    properties: dict[str, Property] = Field(default_factory=dict)
    relationships: dict[str, list[Relationship]] = Field(default_factory=dict)
    version: int = 1                    # 저장소가 관리. 호출자는 설정하지 않는다
    updated_at: datetime | None = None  # 저장소가 관리

    def to_ngsi_ld(self) -> dict[str, Any]: ...
    @classmethod
    def from_ngsi_ld(cls, doc: dict[str, Any]) -> "Entity": ...
    def prop(self, name: str) -> Any | None: ...           # value 편의 접근
    def rel_targets(self, name: str) -> list[str]: ...
```

**직렬화 예시 (`to_ngsi_ld`)**

```json
{
  "id": "urn:loom:plantA:Equipment:WR-03",
  "type": "Equipment",
  "title": "용접 로봇 3호기",
  "tipWear": {"type": "Property", "value": 0.82, "unitCode": "P1",
              "observedAt": "2026-09-16T14:05:00Z",
              "provenance": {"status": "confirmed", "method": "ingest",
                             "source": "file://packs/S01/timeseries.csv#row=8812",
                             "run_id": "01J8...", "confidence": null,
                             "recorded_at": "2026-09-17T01:00:00Z"}},
  "locatedIn": [{"type": "Relationship", "object": "urn:loom:plantA:Station:ST-W2",
                 "provenance": {"status": "confirmed", "method": "ingest", "source": "file://packs/S01/equipment.csv#row=3",
                                "run_id": "01J8...", "recorded_at": "2026-09-17T01:00:00Z"}}],
  "@context": "https://loom.local/context/v0.jsonld"
}
```

| 규칙 | 내용 |
|---|---|
| E-1 | `Entity.type`은 `parse_urn(id).etype`과 같아야 한다 (검증기에서 강제) |
| E-2 | 속성·관계 이름은 camelCase. 온톨로지 v0(`semantic/ontology/core_v0.yaml`)에 정의된 이름만 **CONFIRMED**로 저장 가능, 미정의 이름은 `ASSUMED`로만 |
| E-3 | 관계는 항상 리스트 (다중값 허용) |
| E-4 | 시계열 값은 Entity 속성에 **최신값만** 둔다. 이력은 §7 TelemetryStore |

---

## §6 저장소 포트 (`loom.core.ports`)

```python
from typing import Protocol, Iterable

Triple = tuple[str, str, str]           # (src_urn, rel_name, dst_urn)

class EntityStore(Protocol):
    def upsert(self, entity: Entity) -> Entity: ...
        # 같은 id가 있으면 version+1, 이전 버전은 history에 보존. updated_at 설정
    def upsert_many(self, entities: Iterable[Entity]) -> int: ...
    def get(self, urn: str, as_of: datetime | None = None) -> Entity | None: ...
        # as_of: 그 시각 기준 최신 버전 (문서 버전 인지 질의의 기반)
    def query(self, etype: str | None = None, where: dict[str, Any] | None = None,
              limit: int = 100) -> list[Entity]: ...
        # where: {"propName": value} 동등 비교만. 복잡한 질의는 섹터가 자체 인덱스로
    def triples(self, urn: str | None = None, rel: str | None = None,
                direction: Literal["out", "in", "both"] = "both") -> list[Triple]: ...
    def history(self, urn: str) -> list[Entity]: ...
    def delete(self, urn: str) -> bool: ...
```

- 구현체: `MemoryEntityStore`(C-105, 테스트 기본값) · `PostgresEntityStore`(C-106).
- **모든 섹터 테스트는 MemoryEntityStore로 돈다.** Postgres는 통합 테스트(`-m integration`)에서만.

---

## §7 텔레메트리 (`loom.core.telemetry`)

```python
class TelemetryPoint(BaseModel):
    entity: str          # URN
    prop: str            # 속성명 (camelCase)
    ts: datetime         # UTC
    value: float
    unitCode: str | None = None
    source: str          # provenance.source와 같은 형식

class TelemetryStore(Protocol):
    def write(self, points: Iterable[TelemetryPoint]) -> int: ...
    def window(self, entity: str, prop: str, start: datetime, end: datetime) -> list[TelemetryPoint]: ...
    def props_of(self, entity: str) -> list[str]: ...
    def latest(self, entity: str, prop: str) -> TelemetryPoint | None: ...
```

구현체: `MemoryTelemetryStore` · `PostgresTelemetryStore`(C-106과 같은 모듈).

---

## §8 이벤트 (`loom.core.events`)

```python
EventKind = Literal[
    "entity.upserted", "ingest.started", "ingest.completed",
    "extract.completed", "alarm.raised", "alarm.cleared",
    "rca.drafted", "decision.requested", "decision.approved", "decision.rejected",
    "outcome.recorded", "sim.completed",
]

class Event(BaseModel):
    id: str                      # ULID
    kind: EventKind
    subject: str | None = None   # 관련 URN
    payload: dict[str, Any] = {}
    ts: datetime
    run_id: str | None = None

class EventBus(Protocol):
    def publish(self, event: Event) -> None: ...
    def subscribe(self, kind: EventKind, handler: Callable[[Event], None]) -> None: ...
```

- 구현체: `InProcEventBus` + 모든 이벤트를 `var/events.jsonl`에 추가 기록.
- 새 이벤트 종류가 필요하면 **이 Literal에 추가하는 ADR**을 쓴다.

---

## §9 LLM·임베딩 포트 (`loom.core.llm`)

```python
from langchain_core.language_models import BaseChatModel

LLMRole = Literal["route", "extract", "reason", "judge", "write"]

def get_chat_model(role: LLMRole) -> BaseChatModel: ...
    # 설정: LOOM_LLM_<ROLE>="anthropic:<sonnet-model-id>" | "ollama:qwen3:8b" | ...
    # LOOM_LLM_FAKE=1 이면 FakeListChatModel/GenericFakeChatModel 반환 (테스트 기본)
    # 내부에서 langchain.chat_models.init_chat_model 사용

class UsageMeter(Protocol):
    def record(self, role: LLMRole, input_tokens: int, output_tokens: int, model: str) -> None: ...
    def summary(self) -> dict[str, Any]: ...

class Embedder(Protocol):
    dim: int
    def embed(self, texts: list[str]) -> list[list[float]]: ...

def get_embedder() -> Embedder: ...
    # LOOM_EMBEDDER="hash" (테스트 기본, 결정적) | "bge-m3" | "kure-v1"
```

| 규칙 | 내용 |
|---|---|
| L-1 | 섹터 코드는 **모델 ID를 하드코딩하지 않는다.** 항상 `get_chat_model(role)` |
| L-2 | 구조화 출력은 `model.with_structured_output(PydanticModel)` |
| L-3 | 모든 LLM 호출은 UsageMeter 콜백을 거친다 (토큰·비용 가드) |
| L-4 | 단위 테스트에서 실제 LLM 호출 금지. `LOOM_LLM_FAKE=1`. 실 LLM 테스트는 `-m llm` 마커 |

---

## §10 Answer — 근거 기반 응답 (`loom.core.answer`)

S6이 만들고 S7·S8·S9·UI가 소비한다.

```python
class EvidenceStep(BaseModel):
    src: str                  # URN
    rel: str                  # 관계명 또는 "telemetry:<prop>" 또는 "doc:<section>"
    dst: str                  # URN
    source_ref: str | None    # provenance.source (원천 추적)
    observed_at: datetime | None = None

class EvidencePath(BaseModel):
    steps: list[EvidenceStep]
    supports: str             # 이 경로가 뒷받침하는 주장 한 줄

class RankedCause(BaseModel):
    cause_urn: str | None     # 원인 엔티티 (없으면 None)
    label: str                # 사람이 읽는 원인 설명
    score: float              # 0..1

class Answer(BaseModel):
    id: str                                   # urn:loom:{site}:Answer:{ulid}
    question: str
    answer: str                               # 자연어 답변
    root_causes: list[RankedCause] = []       # RCA형 질문일 때
    evidence: list[EvidencePath] = []
    data_version: str                         # 사용한 문서/데이터 버전 요약. 예) "WS-WELD@v2; pack=S01@run-01J8"
    observed_window: tuple[datetime, datetime] | None = None
    confidence: float                         # 0..1
    insufficient_evidence: bool = False
    trace_id: str
```

| 규칙 | 내용 |
|---|---|
| A-1 | `insufficient_evidence=False`이면 `len(evidence) >= 1` |
| A-2 | `root_causes`는 score 내림차순 |
| A-3 | `evidence`의 모든 URN은 저장소에 존재해야 한다 (평가 하네스가 검사) |

---

## §11 Decision — 판단 기록 (`loom.core.decision`)

S7이 만들고 S8·S9가 소비한다.

```python
class AutonomyLevel(StrEnum):
    L0_INFORM = "L0"      # 알림만
    L1_RECOMMEND = "L1"   # 권고, 사람이 실행
    L2_APPROVE = "L2"     # 사람 승인 후 시스템 실행
    L3_AUTO = "L3"        # 화이트리스트 반복·저위험만 자동

class ProposedAction(BaseModel):
    kind: Literal["notify", "inspect", "set_parameter", "schedule_maintenance", "hold_lot", "other"]
    target: str | None            # URN
    params: dict[str, Any] = {}
    expected_effect: str
    predicted_by: str | None = None   # SimulationRun/what-if URN

class Decision(BaseModel):
    id: str                               # urn:loom:{site}:Decision:{ulid}
    trigger: str | None                   # Alarm URN
    answer_id: str | None                 # Answer URN
    actions: list[ProposedAction]
    autonomy: AutonomyLevel
    status: Literal["proposed", "approved", "rejected", "executed", "closed"]
    approver: str | None = None           # Person URN
    rationale: str | None = None
    created_at: datetime
    decided_at: datetime | None = None

class Outcome(BaseModel):
    decision_id: str
    observed_at: datetime
    kpi_before: dict[str, float]
    kpi_after: dict[str, float]
    success: bool | None
    note: str | None = None
```

Decision·Outcome은 저장 시 Entity(`type="Decision"`/`"Outcome"`)로도 투영해 그래프에서 과거 판단을 근거로 쓸 수 있게 한다.

---

## §12 Ground Truth — 가상 실증공장 정답지 (`loom.core.groundtruth`)

P가 만들고 S6 평가 하네스·S8 비교 평가가 소비한다.

```python
FaultKind = Literal[
    "weld_tip_wear", "die_temp_drift", "conveyor_speed_drift",
    "sensor_offset", "missed_maintenance", "material_lot_variation", "doc_revision_unapplied",
]

class Scenario(BaseModel):
    scenario_id: str                    # "S01".."S20"
    seed: int
    fault: FaultKind | None             # None = 정상(대조군) 또는 근거 부족 시나리오
    target: str | None                  # 결함 주입 대상 URN
    window_start: datetime
    window_end: datetime
    question: str                       # 평가에 쓰는 자연어 질문
    expected_root_cause_urn: str | None
    expected_evidence_types: list[str]  # 근거 경로에 등장해야 하는 타입 집합
    expected_doc_version: str | None    # 버전 인지 시나리오일 때 "WS-WELD@v2"
    expect_insufficient: bool = False   # 원인 데이터를 일부러 뺀 시나리오
    removed_artifacts: list[str] = []   # expect_insufficient일 때 제거한 산출물 이름

class ScenarioPack(BaseModel):
    pack_id: str
    plant_spec: str                     # 사용한 토폴로지 파일 경로
    scenarios: list[Scenario]
```

**팩 디렉터리 규약** (`var/packs/<pack_id>/<scenario_id>/`)

| 파일 | 내용 | 생성 모듈 |
|---|---|---|
| `equipment.csv` | 설비대장 (id, name_ko, type, station, vendor, install_date) — 이름 표기 흔들림 포함 | P-205 |
| `timeseries.csv` | entity, prop, ts, value, unit | P-205 |
| `lots.csv` | lot_id, product, start, end, station_path | P-205 |
| `inspections.csv` | lot_id, ts, check, value, unit, pass | P-205 |
| `alarms.csv` | ts, equipment, code, severity, message | P-205 |
| `maintenance_log.txt` | 자유 서술 정비일지 (한국어, 약어·오타 포함) | P-205 |
| `docs/WS-WELD_v1.pdf`, `docs/WS-WELD_v2.pdf`, `docs/WS-PRESS_v1.pdf` | 작업표준서 | P-206 |
| `ground_truth.json` | 이 시나리오의 `Scenario` | P-207 |
| `manifest.json` | 파일 목록·sha256·seed·생성 시각 | P-207 |

---

## §13 API 규약 (`loom.api`)

| 규칙 | 내용 |
|---|---|
| R-1 | 경로 접두사 `/v0`. 섹터별 라우터: `/v0/entities`, `/v0/ingest`, `/v0/ask`, `/v0/alarms`, `/v0/decisions`, `/v0/reports`, `/v0/twin`, `/v0/sim` |
| R-2 | 엔티티 응답은 `Entity.to_ngsi_ld()` 모양 |
| R-3 | 오류는 RFC 9457 Problem Details `{type,title,status,detail}` |
| R-4 | 라우터는 비즈니스 로직을 갖지 않는다. 섹터 `public.py` 함수 호출만 |

---

## §14 테스트 규약

| 규칙 | 내용 |
|---|---|
| X-1 | 모든 모듈은 `tests/<sector>/test_<module>.py`를 가진다. 카드의 "수용 테스트"가 테스트 함수 이름이 된다 |
| X-2 | 기본 실행 `uv run pytest -q` 는 **네트워크·LLM·Postgres 없이** 통과해야 한다 |
| X-3 | 마커: `integration`(Postgres·Docker), `llm`(실 LLM), `slow`(>10s), `gpu` |
| X-4 | 공용 픽스처는 `tests/conftest.py`: `mem_store`, `mem_telemetry`, `fake_llm`, `tiny_pack`(시나리오 2개짜리 팩) |
| X-5 | 결정성: 난수는 항상 `seed` 인자로. `random`/`numpy` 전역 상태 사용 금지 |
| X-6 | 테스트 출력은 `-q`. 실패 로그 붙여넣기는 마지막 40줄까지만 (컨텍스트 절약) |

---

## §15 컨테이너 — 조립 지점 (`loom.core.container`)

```python
class Container:
    settings: Settings
    entities: EntityStore
    telemetry: TelemetryStore
    events: EventBus
    embedder: Embedder
    usage: UsageMeter
    def chat(self, role: LLMRole) -> BaseChatModel: ...

def build_container(settings: Settings | None = None) -> Container: ...
    # LOOM_STORE="memory" | "postgres" 에 따라 구현체 선택
```

- 섹터 함수는 필요한 포트를 **인자로** 받는다 (`def ingest_pack(pack_dir: Path, store: EntityStore, ...)`). 전역 컨테이너를 import하지 않는다.
- `Container`를 만드는 곳은 `loom.api.app`, `loom.cli.main`, `apps/*`, `tests/conftest.py` 네 곳뿐이다.
