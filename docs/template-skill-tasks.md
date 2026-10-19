# 템플릿·스킬 개편 작업지시서

2026-10-19. [구현 설계](template-skill-plan.md)를 실제 파일·동작·테스트 단위로 나눈 중앙 도구 구현 작업지시서입니다. 개별 컴포넌트를 지금 구현·이관하라는 지시가 아닙니다. 공통 형식을 에이전트가 수동으로 다시 작성하게 하지 않고 중앙 계약 → 렌더링 → 변경 계획 → 적용 → 검사 경로를 구현합니다. 실행 근거와 한계는 [검증 기록](template-skill-validation.md)에 남깁니다.

| 단계 | 현재 상태 |
|---|---|
| T1 | 계약·입력 검증·공통 렌더러 구현·독립 코드/문서 검증 완료; 문서 반영 후 저장소 검사 36개 문서·7개 workflow 성공 |
| T2 | 읽기 전용 inspect/plan CLI 구현·독립 코드/문서 검증 완료; 문서 반영 후 저장소 검사 37개 문서·7개 workflow 성공 |
| T3 | TODO: 신규 작성 기반·apply·복구 |
| T4 | TODO: 전체 계약 검사·CI 연결 |
| T5 | TODO: 신규 생성·기존 적용 스킬과 실행 안내 |
| T6 | TODO: 중앙 생성·갱신 fixture와 별도 범위의 실제 도입; 외부 리포 미적용 |

## 실행 순서와 공통 완료 조건

T1 → T2 → T3 → T4 → T5 → T6 순서로 진행합니다. 각 단계는 아래 파일과 동작을 구현하고 해당 검증을 통과한 뒤 다음 단계로 넘어갑니다. 실패·미작성 작업은 결과에 남기며 기존 검사 우회로 완료하지 않습니다. 구현 PR은 단계별로 나누고 실행 코드·계약·해당 테스트·사용 명령을 함께 제출합니다.

- 실제 기능과 메타데이터는 입력으로 받고 공통 형식은 코드로 재현합니다. 에이전트 판단이 필요한 것은 실제 기능·번역·기기 조건·미확인 입력이며, 공통 파일명·관리 경계·필수 검사·완료 판정을 임의 해석하게 하지 않습니다.
- 기존 경로와 `check_integration.py`·`sync_badges.py` CLI 및 외부에서 사용하는 함수 이름·오류 의미를 유지합니다. 새 공통 모듈로 위임하고 같은 로직의 복사본을 만들지 않습니다.
- 이 작업지시서의 새 파일명·API·CLI는 구현할 계약입니다. 구현 전에는 존재하는 파일이나 실행 결과로 기록하지 않습니다. 새 외부 의존성 없이 Python 표준 라이브러리와 기존 requirements의 도구를 우선 사용합니다.
- 수정한 동작의 테스트, `python3 -m ruff check .`, `python3 -m ruff format --check .`, `python3 -m unittest discover -s tests -v`, `python3 scripts/check_repository.py`를 실행합니다. workflow/action 변경에는 actionlint도 실행합니다. 실제 HA 검증은 호환되는 별도 환경에서 수행합니다.
- 필수 변경과 승인이 필요한 기존 예외는 구분합니다. 새 기능·지원 최소 변경·중앙 지침의 대상 설치·원격 쓰기를 자동으로 수행하지 않습니다. 담당·독립 검증·증거 기록은 기존 GOV-01~GOV-05를 유지합니다.

## T1. 적용 계약과 공통 렌더러 구현

**파일:** `templates/integration/contract.json`, `schemas/integration-input.schema.json`, `schemas/integration-inventory.schema.json`, `schemas/integration-plan.schema.json`, `scripts/standards/__init__.py`, `contract.py`, `readme.py`, `badges.py`, `conditions.py`, `tests/test_standards_contract.py`. 모듈 파일은 `scripts/standards/` 아래에 둡니다.

1. 계약 레코드에 `id`, `source`, `destination`, `ownership`, `condition`, `required_inputs`, `markers`, `extension`, `rules`, `status`를 정의합니다. `ownership`은 `exact_file`, `managed_blocks`, `create_only`, `merge`로 제한합니다. 실제 대상은 설계 3절의 파일별 표·3.1절 생성 트리와 일대일로 등록합니다. 표에 없는 대상 경로는 자동 쓰기 목록에 넣지 않습니다. 경로 토큰은 검증한 `{domain}`과 실제 선택 플랫폼의 `{platform}`만 허용하고 플랫폼 반복은 `platforms` 조건으로 제한합니다. 기존 원본의 `available`과 후속 T3에서 작성할 자산의 `pending`을 구분하며, 원본이 없는 레코드를 렌더링 가능한 것으로 보고하지 않습니다.
2. 입력 스키마에 원격·기본 브랜치·domain·manifest 값·양언어 소개·라이선스·설정 방식·플랫폼·선택 기능·HA 환경·payload 메타데이터를 정의합니다. 각 값의 `value`와 `source`를 기록합니다. 환경은 최소 HA/current HA와 라이브러리 current/minimum을 별도 축으로 저장합니다. 기존 검사 설정은 변경하지 않고 새 입력에서 필요한 `.hass-standards.json` 값을 렌더링합니다.
3. `check_integration.py`의 README 렌더링·관리 경계·본문 보호와 `sync_badges.py`의 렌더링을 공통 모듈로 추출합니다. 기존 파일에서는 같은 공개 함수로 위임합니다. `bluetooth_documents.py`의 `uses_package` 등 조건 판별도 공통으로 사용하며 실제 배포 이름·extras·marker·절대 import 판별을 유지합니다.
4. contract loader는 스키마 버전·소유 방식·조건·규칙 ID·대상 중복·경로 이탈을 검증합니다. 알 수 없는 계약 버전과 필수 입력 누락은 오류로 반환합니다. 스키마와 실제 Python 입력 검증의 허용/거부 사례를 일치시킵니다.

**검증:** 기존 README·배지 렌더링 결과와 예외·본문 보호 테스트를 그대로 통과시킵니다. `test_standards_contract.py`에 잘못된 버전·중복 대상·필수 입력 누락·지원하지 않는 condition·경로 이탈 실패 사례와 네 라이브러리 조합을 추가합니다. 검사기와 생성 렌더러가 같은 입력에 같은 관리 영역 바이트를 내는지 확인합니다.

## T2. inspect와 plan 구현

**파일:** `scripts/manage_integration.py`, `scripts/standards/inventory.py`, `planning.py`, `tests/test_integration_planning.py`. 모듈 파일은 `scripts/standards/` 아래에 둡니다. T1의 inventory·plan 스키마를 채웁니다.

1. `inspect <target> --output <inventory.json>`을 구현합니다. 원격·기본/현재 브랜치·작업 트리 상태·실제 manifest·hacs·README 지원 선언·requirements·workflow·관리 주석·선택 기능을 읽고 출처·충돌·미확인 값을 반환합니다. 기본 브랜치를 main/master로 추정하지 않고 조회 불가 시 확인이 필요한 값으로 남깁니다.
2. `plan <target> --mode create|adopt --input <input.json> --standards-ref <full-sha> --output <plan.json>`을 구현합니다. create는 명시한 비어 있는 대상 경로와 신규 입력을 사용하고 기존 manifest 부재를 오류로 처리하지 않습니다. adopt는 실제 단일 domain을 읽으며 입력과 다르면 차단합니다. 수정된 사용자 파일은 보호하되 깨끗하지 않은 리포 전체를 무조건 거부하지 않습니다.
3. CLI 실행 checkout의 HEAD와 `--standards-ref`가 일치하고 계약·템플릿·실행 코드가 수정되지 않았는지 확인합니다. 원격 최신 SHA 조회 결과만으로 다른 커밋의 도구를 실행했다고 주장하지 않습니다.
4. 계획에 `schema_version`, `standards_ref`, `target_identity`, `validated_input`, `input_digest`, `guards`, `operations`, `pending`, `conflicts`를 기록합니다. `validated_input`은 스키마 검증한 sourced 입력의 독립 복사본이며 canonical JSON SHA-256으로 `input_digest`를 재계산할 수 있어야 합니다. 원본 입력 파일 재읽기로 스냅샷을 대신하지 않습니다. 계획 스키마는 중앙 입력 스키마를 로컬 `$ref`로 참조하고 resolver는 정확한 input/inventory/plan 스키마 세 파일 외 URI·경로를 거부합니다. 각 operation은 경로·소유 방식·원본·규칙·전후 SHA-256·후속 내용·unified diff를 포함합니다. 새 파일은 기존 해시 대신 부재 조건을 기록합니다. guards에는 읽고 보존할 관련 파일의 상태도 포함하며 조사·렌더링 도중 변경도 검출합니다.
5. 생성·관리 영역 갱신·변경 없음·충돌·수동 작성 필요를 구분합니다. 공통 형식은 렌더러가 생성하고 기기 코드·본문·실제 테스트가 미작성인 경우 pending으로 남깁니다. 충돌·필수 입력 누락은 종료 코드 2, 생성 가능한 초안 계획은 0과 pending 목록을 반환합니다. 결과에 실행 시각 같은 비결정적 값을 넣지 않습니다.

**검증:** 임시 Git 리포에서 기존/신규·기본 브랜치 차이·선언 불일치·잘못된 SHA·수정된 실행 자산·조건부 기능을 테스트합니다. 동일한 SHA·입력·대상 상태에서 계획 JSON과 diff가 같아야 합니다. 계획 파일은 target 밖에 쓰고 target의 추적·미추적 파일은 바뀌지 않아야 합니다.

## T3. 생성 자산과 apply 구현

**파일:** `scripts/standards/apply.py`, `scaffold.py`, `templates/integration/`의 신규 코드·테스트 작성 기반, `tests/test_integration_apply.py`, `tests/test_integration_scaffold.py`. 모듈 파일은 `scripts/standards/` 아래에 둡니다. 기존 템플릿 위치는 유지합니다.

1. 설계 3.1절의 init·manifest·const·flow·번역·선택 플랫폼과 대응 테스트를 중앙 자산으로 추가합니다. coordinator·entity·diagnostics·액션은 실제 선택 기능만 생성합니다. root conftest와 세 빈 테스트 init는 기존 원본 그대로 생성합니다.
2. manifest의 domain·디렉터리·DOMAIN, config_flow 선언과 실제 파일을 일치시킵니다. 실제 최소/current 환경에서 호환되는 setup·플랫폼 전달·unload·정리 작성 기반을 제공합니다. 실제 client/entry 데이터가 없으면 미완료가 드러나도록 만들고 성공만 반환하는 가짜 구현을 만들지 않습니다.
3. 영어 소스와 `translations/en.json`의 동기화 경로, `ko.json`의 키·placeholder 검증을 구현합니다. 배포 파일에 미해결 Core 문자열 참조를 남기지 않습니다. 실제 기능·번역이 미작성인 경우 pending으로 반환하고 샘플을 완성품으로 취급하지 않습니다.
4. `apply <target> --plan <plan.json>`을 구현합니다. 내장 `validated_input`의 스키마와 canonical JSON digest를 검증한 뒤 동일 SHA·guards로 재계획하여 operation 경로·소유 방식·content·after hash를 대조합니다. 대상 identity·기준 SHA·guards·모든 operation 경로도 사전 검증합니다. 경로가 사라짐/추가됨/수정됨·symlink/junction 이탈·관리 주석 충돌이면 쓰기 전에 종료 코드 2로 중단합니다.
5. 관리 영역 밖 바이트·고유 배지·라이선스 고지·기기 본문·회귀 테스트·전용 CI·최소 환경을 보존합니다. create_only의 기존 파일은 덮어쓰지 않고 merge의 미해결 차이는 conflicts로 반환합니다. 기존 CI의 schedule·특수 job·required checks가 손실될 변경은 자동 적용하지 않습니다.
6. 잠금·쓰기 직전 상태 확인·파일별 임시 쓰기/교체·복구용 원본과 결과 명세를 구현합니다. 부분 실패 시 적용 경로와 복구 명령을 출력하고 복구도 현재 해시를 확인합니다. 일괄 reset/clean과 사용자 편집 덮어쓰기를 사용하지 않습니다.

**검증:** 신규 생성 후 재계획과 기존 적용 후 재계획에서 추가 operation이 없어야 합니다. 긴 양언어 본문·고유 fixture·CI 확장·기존 최소 환경을 넣은 fixture에서 보존 바이트를 비교합니다. 오래된 계획·동시 편집·읽기/쓰기 오류·부분 실패·복구 충돌을 테스트합니다. 초안 작성 기반은 파일 존재만으로 실제 HA 검증을 통과할 수 없어야 합니다.

## T4. 검사기와 CI 연결

**파일:** `scripts/check_integration.py`, `scripts/check_repository.py`, `scripts/bluetooth_documents.py`, `scripts/payload_documents.py`, `tests/test_integration_contract.py`, `tests/test_scaffold_validation.py`. CI 수정이 필요한 경우에만 관련 action/workflow를 변경합니다.

1. 통합 검사기가 T1 계약과 동일 렌더러를 사용하도록 연결합니다. 파일 소유 방식·관리 경계·조건부 문서·full SHA·선택 기능의 구현/테스트·번역 필수 입력을 검사합니다. 기존 예외 ID·경로·승인 증거 처리를 보존합니다.
2. 미작성 필드·placeholder·없는 대응 테스트는 규칙 ID와 경로를 포함해 실패로 반환합니다. 실제 동작의 증거는 별도 HA 테스트 결과로 확인하며 정적 검사에 PASS 문자열을 넣어 대체하지 않습니다.
3. 중앙 저장소 검사에 contract·스키마·새 템플릿·작업지시서/스킬 참조의 무결성을 포함합니다. 템플릿 placeholder 검사와 실제 채택 결과의 미작성 실패를 구분해, 의도적인 작성 기반 때문에 중앙 검사 전체가 실패하지 않게 합니다.
4. 공용 caller의 reusable workflow·action·standards-ref를 같은 검토 SHA로 렌더링합니다. CI는 caller checkout을 유지하고 composite script 경로는 github.action_path를 사용합니다. 형식 불일치를 자동 수정하거나 검증 실패를 성공으로 바꾸지 않습니다.

**검증:** 같은 입력으로 렌더링한 관리 영역은 검사에서 차이가 없어야 하고, 필수 파일·영역·번역·기능별 테스트·SHA를 하나씩 훼손하면 해당 경로가 실패해야 합니다. 형식 검사 통과와 실제 HA/payload 검증 통과를 별도 결과로 확인합니다. 기존 전체 회귀 및 workflow 변경 시 actionlint를 통과시킵니다.

## T5. 두 스킬과 실행 안내 작성

**파일:** `skills/create-ha-integration/SKILL.md`, `skills/adopt-ha-standards/SKILL.md`, 각 `references/workflow.md`, `docs/template-skill-usage.md`, `tests/test_skill_contract.py`.

1. 신규 스킬은 명시한 신규 기능·메타데이터 입력으로 create 계획을 만들고 기존 적용 스킬은 inspect 결과로 adopt 계획을 만듭니다. 검토 요청은 inspect/plan까지만 수행하도록 분기를 명시합니다.
2. 각 workflow에 사용할 명령·입력 필드·생성 파일·충돌 처리·실제 기능 보완·검증 명령·최종 보고 필드를 적습니다. 공통 README·테스트·CI 형식을 직접 작성하는 단계는 넣지 않고 T1~T4 도구를 호출합니다. 미확인 기기 기능·번역·예외는 pending/conflicts로 반환합니다.
3. 실행 순서를 `검토 SHA의 도구 확인 → inspect/입력 확인 → plan/diff → 요청 범위 apply → 실제 기능·테스트 작성 → check/실제 HA 테스트 → 증거 기록`으로 고정합니다. apply 전에 필요한 근거가 없으면 실패 이유와 필요한 입력을 출력하고 형식을 임의로 만들어 우회하지 않습니다.
4. 스킬은 계약 버전·검토 SHA가 맞는 중앙 checkout으로 연결합니다. 사용 문서에 중앙 원본 위치·명시적 설치 방법·버전 확인·기존 스킬 갱신 방법을 적되 대상 통합에 에이전트 진입 파일을 자동 설치하지 않습니다. 중앙 규칙·템플릿을 스킬에 복제하지 않습니다.

**검증:** 정적 테스트로 두 스킬의 도구·원본 경로·지원 계약 버전과 필수 분기를 검사합니다. 신규 생성/기존 적용/검토만/imagespec·blesession/충돌/CLI 실패 요청으로 실제 스킬 동작을 검증하고 명령·선택 분기·산출물·미검증 범위를 기록합니다. 정적 SKILL.md 검사를 실제 에이전트 동작 검증으로 보고하지 않습니다.

## T6. 실제 생성·갱신 검증과 도입 판정

**파일:** `tests/fixtures/scaffold/`의 신규·기존·네 라이브러리 조합 입력 및 보존 비교 자료, `docs/template-skill-validation.md`, 실제 도입 범위가 승인된 경우에만 대상 STANDARDS·ADOPTION_CHECKLIST·중앙 현황의 자기 리포 행.

1. 중앙 fixture에서 신규 기본형, 기존 본문·회귀·CI·최소 환경이 있는 형, imagespec만/blesession만/둘 다를 생성·적용하고 재적용 무차이·보존·누락 실패를 검증합니다. 조건이 제거된 기존 문서·예제를 삭제하지 않는지도 검사합니다.
2. 별도로 승인된 실제 신규·기존 통합에서 실제 코드·entry·외부 경계 fixture를 완성합니다. 선언된 정확한 최소 HA와 current, 각 Python·플러그인 환경에서 flow·setup·플랫폼 상태/액션·unload/reload·실패 복구·해당 migration/진단 및 기존 회귀를 실행합니다.
3. imagespec은 실제 등록 액션 스키마·production 준비 함수·설치된 current/정확한 하한으로 전체 YAML·출력 크기/색상을 검증합니다. 기기 전송·검증 후 추가 설치를 하지 않습니다. blesession 문서는 실제 기기 조건·진단 의미·양언어 보존을 확인하고 실물 미검증을 따로 남깁니다.
4. 실제 설치 버전·pip check·HACS·Hassfest·CI·대상 커밋과 번역 의미/기존 내용 보존 리뷰 결과를 기록합니다. 중앙 fixture 결과를 실제 통합 성공으로 재사용하지 않습니다. 외부 리포 범위가 없으면 중앙 검증까지만 보고하고 T6 실제 도입은 TODO로 남깁니다.

**완료:** 설계의 검증 표와 체크리스트에 각 결과가 연결되고 미해결 필수 항목이 없어야 합니다. 실제 도입 완료는 기본 브랜치 반영·해당 커밋 검증과 중앙 현황의 완료 조건까지 충족한 경우에만 기록합니다.
