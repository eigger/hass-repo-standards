# 템플릿·스킬 구조 개편 구현안

2026-10-19 작성. [로드맵](adoption-plan.md#향후-계획--공통-템플릿-생성적용-자동화)의 후속 설계입니다. **T1 계약·공통 렌더러부터 T5 신규 생성·기존 채택 스킬까지 독립 검증과 PR CI 후 main에 반영했습니다.** T6 중앙 생성·갱신 시나리오 자동 회귀의 구현·독립 검증을 완료했고 최종 PR CI/병합을 기다립니다. 이번 중앙 도구·템플릿·스킬 작업은 T6 중앙 검증으로 마무리하며 외부 통합 실제 도입은 요청 범위 밖입니다. 설계 당시 중앙 기준은 `0a0b6271562232db131b3d5a836415878e9ceab8`이며 단계별 실제 커밋은 [검증 기록](template-skill-validation.md)에 구분합니다. 실제 사용 범위는 [사용 안내](template-skill-usage.md)를 따릅니다.

이 문서는 구현한 중앙 인터페이스·파일 범위·계약 배경과 검증 조건을 설명합니다. T1~T6의 현재 결과는 단계별 상태표와 검증 기록을 따릅니다. 실제 기기 코드·입력·환경은 적용 대상마다 완성하고 검증해야 합니다. 기존 규칙 ID·필수/권장 수준, 예외 승인, 통합별 적용 순서와 서브 에이전트 운영 지침은 변경하지 않습니다. 중앙 작업 완료가 다른 통합 수정·workflow 수동 실행·지원 최소 상향·스킬 설치·릴리스를 승인하지 않습니다.

## 1. 현재 구현과 적용 범위

| 현재 자산 | 재사용하는 내용 | 중앙 구현 연결 |
|---|---|---|
| [채택 예시](../templates/integration/USAGE.md) | 양언어 README·CI·테스트 기반·조건부 문서 | 신규 생성과 기존 갱신이 공유하는 적용 계약 |
| [통합 검사기](../scripts/check_integration.py) | README 렌더링·관리 영역 보호, 테스트·workflow·문서 검사, 예외 처리 | 렌더링과 읽기 전용 검사의 분리, 공통 렌더러 재사용 |
| [배지 도구](../scripts/sync_badges.py) | 실제 메타데이터 기반 배지·고유 배지 보존 | 새 생성·갱신 경로에서도 같은 구현 사용 |
| [Bluetooth 검사](../scripts/bluetooth_documents.py)·[payload 검사](../scripts/payload_documents.py) | 실제 requirement/import 조건 판별·문서 계약 | 조건부 생성 목록과 검사 대상의 일치 |
| [공용 CI](ci.md)·[payload 실행 계약](payload-documentation.md) | caller checkout·실제 HA·설치된 라이브러리 검증 | 같은 중앙 full SHA에서 생성·검사·실행 연결 |

T3 템플릿은 실제 메타데이터와 domain별 `test_init.py` 등 명시적인 작성 기반을 제공합니다. 실제 entry·client·flow 입력·플랫폼 동작은 미완성이며 TODO·`NotImplementedError`·pending으로 드러냅니다. 파일 생성만으로 동작하는 통합이나 실제 HA 검증 완료를 주장하지 않습니다.

## 2. 원본과 실행 책임

| 위치 | 책임 | 중복 방지 원칙 |
|---|---|---|
| `docs/` | 규칙·배경·예외·검증 기준의 원본 | 스킬·코드에 규칙 전문을 복제하지 않음 |
| `templates/integration/` | 공통 산출물과 적용 계약 | 같은 형식의 템플릿을 스킬 assets에 다시 두지 않음 |
| `scripts/standards/` | 조사·입력 검증·렌더링·변경 계획·쓰기의 공통 모듈 | 생성기와 검사기가 같은 렌더러·조건 판별 사용 |
| `scripts/manage_integration.py` | 생성·갱신 CLI | 기존 검사·배지 CLI와 호환되는 진입점 추가 |
| `skills/create-ha-integration/` | 신규 통합 생성 절차 연결 | 실제 메타데이터와 미작성 작업 확인 |
| `skills/adopt-ha-standards/` | 기존 통합 채택·재검토 절차 연결 | 기존 본문·테스트·지원 범위·사용자 변경 보존 |
| `actions/`·`.github/workflows/` | CI의 읽기 전용 검사·실행 검증 | 생성·쓰기·승인 대기 없이 실패를 그대로 보고 |

스킬은 필요한 규칙 문서를 읽고 CLI를 호출하는 얇은 진입점으로 만듭니다. imagespec·blesession은 각 스킬의 조건부 절차로 연결하며 전체 스킬을 라이브러리별로 복제하지 않습니다. 스킬 없이도 CLI와 CI 검사가 독립적으로 동작해야 합니다.

## 3. 파일별 적용 계약

`templates/integration/contract.json`에 계약 스키마 버전, 원본·대상 경로, 적용 조건, 소유 방식, 관리 주석, 필수 입력, 확장 위치, 관련 규칙 ID를 기록합니다. 경로 토큰은 검증한 `{domain}`과 실제 선택한 플랫폼의 `{platform}`만 허용하며, 플랫폼 반복은 `platforms` 조건에서만 사용합니다. 일반 문자열 전체 치환이나 템플릿 내 코드 실행은 허용하지 않습니다. T3의 45개 레코드는 원본이 있는 `available` 40개와 없는 `pending` 5개를 구분합니다. 원본이 있는 작성 기반도 실제 동작은 미완성일 수 있으므로 renderer가 반환하는 실제 작성·검증 pending을 별도로 유지합니다. `available`은 실제 통합 완성을 뜻하지 않습니다.

| 대상 | 소유 방식 | 신규 생성 | 기존 갱신 |
|---|---|---|---|
| 세 빈 `__init__.py`, `tests/conftest.py` | 중앙 파일 전체 고정 | 중앙 바이트 그대로 생성 | 차이를 표시하고 고유 fixture 이관이 필요한 경우 자동 덮어쓰기 차단 |
| README header/support/related-projects/license와 내부 badges | 중앙 관리 영역 | 양언어 원본으로 생성 | 기존 관리 영역만 갱신, 나머지 바이트·고유 배지·고지 보존 |
| domain `conftest.py` | 중앙 관리 영역 + 통합 확장 | 고정 영역과 미작성 fixture 안내 | 고정 영역 외 실제 entry·외부 통신 fixture 보존 |
| `test_init.py`, 통합 구현, 기존 회귀 테스트 | 최초 생성 후 통합 소유 | 실제 로딩 테스트 작성 기반 제공 | 자동 교체·삭제하지 않음 |
| 공용 caller workflow | 중앙 구조 + 허용된 입력·확장 | 실제 기본 브랜치·검토 SHA·환경으로 생성 | 기존 schedule·특수 job·required checks 영향을 비교해 병합안 작성 |
| 양언어 troubleshooting/payload 문서 | 고정 구조 + 통합 본문 | 조건에 맞는 구조·링크·미작성 표시 | 기존 본문·기기 예제를 보존하며 구조 차이는 수동 이관 과제로 표시 |
| `examples/payload/`·payload adapter | 통합 소유 | 필요한 경로와 작성 과제만 제시 | 실제 액션·production 경로·예제를 교체하지 않음 |
| manifest·hacs.json | 실제 메타데이터 | 명시 입력으로 기본 구조 생성 | 지원 최소·버전·의존성을 자동 변경하지 않음 |
| requirements·constraints·pyproject·Dependabot | 환경별 입력·통합 확장 | 검토한 환경 조합으로 작성 | 현재·최소 파일과 기존 설정을 보존하고 충돌은 차단 |
| `.hass-standards.json` | 적용 설정·기존 예외 | 확인한 값만 기록 | 기존 payload·예외·추가 설정을 보존하고 필요한 값만 병합 |
| `STANDARDS.md`·`ADOPTION_CHECKLIST.md` | 검토·실행 증거 | TODO 상태의 기록 기반 | 과거 증거를 보존하고 이번 검토 구간을 추가, PASS 재사용 금지 |
| `LICENSE`·리포 고유 AGENTS·전용 CI·README 본문 | 통합 소유 | 라이선스 등 필요한 결정이 없으면 미완료 | 자동 생성·교체·삭제하지 않음 |

공용 CI는 문서 전체를 자유롭게 병합하지 않고 [CI-01~CI-07](ci.md)의 고정 조건과 허용 입력을 계약으로 표현합니다. 기존 실행 조건이 중앙 계약과 충돌하면 중앙 템플릿 개선 또는 기존 승인 절차로 해결하며, job이나 schedule을 조용히 삭제하지 않습니다. 조건부 라이브러리 사용이 사라져도 기존 문서·예제는 자동 삭제하지 않고 재검토 대상으로 남깁니다.

Dependabot은 실제 minimum requirements/constraints 입력으로 제외 경로를 구성하고 current 경로와의 충돌을 검사하며 기존 주기·groups·ecosystem·고유 exclude를 보존합니다. 공유 경로의 역할이 미확인이면 pending으로 남깁니다. requirements의 유효 줄이 같고 주석/빈 줄만 다를 때는 기존 바이트를 보존하며 실제 의존성 차이를 조용히 병합하지 않습니다.

관리 주석이 없거나 중복·역전되어 있으면 기존 문서에서 경계를 추측하지 않습니다. 최초 이관안에서 기존 내용의 보존 위치와 설정 반영을 검토한 후 경계를 지정합니다. domain 변경이나 다중 통합 manifest 발견은 초기 버전의 자동 처리 범위 밖이며 명시적 오류로 반환합니다.

### 3.1. 컴포넌트와 테스트 생성 구조

신규 UI 설정 기반 장치·서비스 통합은 아래 구조를 생성 계약의 기준으로 사용합니다. T3는 선택 기능에 필요한 코드·번역·테스트 작성 기반을 제공하고 실제 응답 fixture·snapshot·payload 액션 등 미확인 산출물은 pending으로 남깁니다. 기존 통합에는 같은 역할·경로를 적용하되 동작과 지원 범위·고유 구현을 보존하고, 기존 YAML 설정이나 없는 기능을 공통 형식 때문에 새로 만들거나 제거하지 않습니다.

```text
custom_components/
├── __init__.py                  # 빈 패키지 marker; 기존 파일은 create_only로 보존
└── <domain>/
```

`custom_components/<domain>/` 내부:

```text
├── __init__.py
├── manifest.json
├── const.py
├── config_flow.py
├── strings.json                 # HA-11의 소스 관리 기준; 런타임 번역 아님
├── translations/
│   ├── en.json
│   └── ko.json
├── <platform>.py                # 실제 제공하는 플랫폼별 생성
├── coordinator.py               # 데이터 갱신 coordinator가 필요한 경우
├── entity.py                    # 플랫폼 간 공유 entity 동작이 있는 경우
├── diagnostics.py               # 진단 기능을 제공하는 경우
└── services.yaml                # 통합이 설명할 액션을 제공하는 경우

tests/
├── __init__.py
├── conftest.py
└── components/
    ├── __init__.py
    └── <domain>/
        ├── __init__.py
        ├── conftest.py
        ├── test_init.py
        ├── test_config_flow.py
        ├── test_<platform>.py
        ├── test_coordinator.py  # 해당 구현이 있는 경우
        ├── test_diagnostics.py  # 해당 구현이 있는 경우
        ├── test_payload_examples.py  # imagespec 적용 조건 충족 시
        ├── fixtures/           # 비식별 응답·패킷 데이터가 필요한 경우
        └── snapshots/          # snapshot 검증을 사용하는 경우
```

HA 공식 [파일 구조](https://contributors.home-assistant.io/core/integrations/file-structure/)는 `__init__.py`·`manifest.json`과 기능별 모듈 역할을 정의합니다. UI config flow 기본 적용, 양언어 구성, 세 빈 테스트 init·정확한 중앙 conftest·커스텀 테스트 플러그인 고정은 [HA-04·HA-11·HA-13](home-assistant.md)과 [TEST-02·TEST-03·TEST-08](testing.md)의 프로젝트 정책입니다. 모든 커스텀 통합의 설치 조건이나 Core 품질 등급 인증으로 표현하지 않습니다. 공식 근거와 재확인일은 [출처 목록](sources.md)에 연결합니다.

| 생성 조건 | 구현 파일·계약 | 대응 테스트·완료 기준 |
|---|---|---|
| 모든 통합의 기본 구조 | `__init__.py`, 실제 domain·이름·custom version 등의 manifest, 공통 상수를 위한 `const.py` | `test_init.py`에서 실제 HA 로딩 검증. manifest·디렉터리·DOMAIN 일치와 HACS/Hassfest 확인 |
| UI 설정을 제공함 | `config_flow.py`, manifest의 `config_flow: true`, 실제 설정·오류 번역 키 | `test_config_flow.py`에서 실제 HA flow manager로 성공·실패 후 복구·중복·안정적 unique ID 확인. options/reauth/reconfigure/discovery는 실제 제공 경로만 검증 |
| 엔티티 플랫폼을 제공함 | 선택한 `sensor.py`, `button.py` 등 실제 플랫폼과 setup 연결 | 각 `test_<platform>.py`에서 실제 entry·플랫폼 로딩 후 상태·registry·지원 액션 검증. 사용하지 않는 플랫폼 파일 생성 금지 |
| coordinator가 적합함 | `coordinator.py`와 필요한 첫 갱신·오류 처리 | `test_coordinator.py`에서 정상·갱신 실패·unavailable·복구 검증. push 구조를 polling으로 바꾸지 않음 |
| 공유 entity 동작이 있음 | `entity.py` | 플랫폼 테스트로 공통 동작 검증, 별도 helper 테스트는 실제 공유 로직이 있을 때만 추가 |
| 진단을 제공함 | `diagnostics.py` | `test_diagnostics.py`에서 실제 진단 결과와 민감 정보 제거 검증 |
| 액션을 제공함 | 실제 등록 코드·스키마·`services.yaml`·번역 키 | 플랫폼 또는 기능별 테스트에서 실제 등록·입력 오류·출력 검증. 기기 I/O만 mock하고 가짜 액션을 생성하지 않음 |
| imagespec을 사용함 | 기존 DOC-08 문서·실제 YAML·production adapter | 정확한 중앙 `test_payload_examples.py` scaffold와 실제 HA/설치된 renderer 계약. 기존 payload 조건·marker 정책 유지 |

기능별 테스트 파일은 작성 기반으로 생성할 수 있지만, TODO·빈 테스트·일괄 skip을 완료된 테스트로 만들지 않습니다. 계약에는 선택 기능별 생성 목록과 미작성 작업을 함께 남기고, 실제 기능·입력 없이 coordinator·플랫폼·액션·fixture를 발명하지 않습니다. 기존 테스트는 내용·수집 범위를 보존하며 domain 경로로 이관한 뒤 다시 실행합니다.

### 3.2. 커스텀 통합의 UI 번역

README 번역과 HA UI 번역은 별도 산출물입니다. 공식 [커스텀 통합 번역 안내](https://contributors.home-assistant.io/core/integrations/translations/#custom-integrations)에 따라 커스텀 통합은 완성된 `translations/en.json`을 직접 배포하고, 이 프로젝트의 양언어 생성 구성에는 `translations/ko.json`을 포함합니다. HA는 커스텀 통합의 `strings.json`을 자동 컴파일하거나 UI 번역으로 직접 읽지 않으므로, 해당 파일만 생성한 상태를 완료로 처리하지 않습니다.

기존 HA-11의 `strings.json` 소스 관리 기준은 유지하며, 새 생성 도구는 영어 원본과 배포용 `en.json`을 동기화하는 명시적 경로를 제공합니다. 커스텀 배포 파일에는 Core의 `[%key:...%]` 참조를 그대로 두지 않고 실제 문구를 기록합니다. 영어·한국어 번역 키와 placeholder, config flow·entity·action·오류 코드의 실제 사용 키를 대조하고, 해당 HA 버전에서 번역이 로딩되는지 검증합니다. 기존 번역·고유 문구는 보존하고 새로운 기능이나 미번역 문구를 임의 생성해 누락을 감추지 않습니다.

### 3.3. 실제 HA 생명주기와 완료 판정

생성되는 config entry 기반 구현은 실제 `async_setup_entry`와 플랫폼 전달, `async_unload_entry`와 플랫폼 해제·연결·listener·task 정리 경로를 연결합니다. `async_setup`은 통합 전역 설정·액션 등록 등 필요한 역할이 있을 때 구현합니다. 플랫폼 없는 통합에 가짜 플랫폼을 추가하지 않습니다. config entry 데이터 변경 시 실제 migration 경로와 테스트를 함께 작성합니다.

공식 [config entry 생명주기](https://contributors.home-assistant.io/core/integrations/config-entries/)를 따르되 예제의 최신 Python 문법·HA API를 무조건 복사하지 않습니다. `runtime_data` 등 API와 타입 문법은 선언한 최소 HA·Python의 지원 여부를 확인하고 기존 최소·current 환경에서 각각 검증합니다. 호환되지 않으면 기존 정책에 따른 구현·지원 판단을 남기며 최소 지원을 자동으로 올리지 않습니다.

`test_init.py`는 실제 `hass`·플러그인과 `MockConfigEntry`로 entry setup·로딩 상태·unload/reload·해당 실패와 복구·정리를 검증합니다. domain conftest에는 실제 entry 데이터의 `mock_config_entry`와 필요한 외부 경계의 `mock_client`를 제공하고, 실제 HA 로더·config entry manager·플랫폼을 stub이나 성공 반환값으로 대체하지 않습니다. config flow만 고립해서 검사한 결과를 통합 전체 로딩 결과로 재사용하지 않습니다.

완료 판단에는 구조 검사와 실제 동작 검증을 모두 사용합니다. config flow가 있는데 대응 테스트가 없거나 선택한 플랫폼의 실제 로딩 테스트가 미작성인 경우 미완료로 보고합니다. 파일 존재·AST 파싱·테스트 개수만으로 완료 처리하지 않으며, 실제 수집·실행 결과와 기능별 assertion·mock 경계 리뷰를 연결합니다. Core의 [domain별 pytest 실행 방식](https://contributors.home-assistant.io/core/development/testing/)을 사용하되 Core의 품질 등급별 coverage 수치를 모든 커스텀 통합의 보편적 HA 요구사항으로 강제하지 않습니다.

## 4. 입력과 기준 SHA

적용용 입력은 별도 `--input` JSON으로 받고, 스키마와 예시는 중앙에 둡니다. 일회성 조사 결과·변경 계획은 대상 리포 밖의 작업 디렉터리에 저장합니다. `.hass-standards.json`은 기존 검사 설정 역할을 유지하며 일회성 조사 상태를 넣지 않습니다.

| 입력 | 기존 리포의 출처 | 신규 리포에서 필요한 값 |
|---|---|---|
| 원격·실제 기본 브랜치·작업 트리 | Git·GitHub 메타데이터, 조회 실패 시 확인된 명시 입력 | 확인한 원격 메타데이터 또는 사용자의 명시 입력 |
| domain·버전·runtime/HA 의존성 | 실제 manifest, 절대 import는 조건 판별 보조 | 명시한 실제 설계 값, 미결정 버전·의존성은 차단 |
| 설정 방식·플랫폼·선택 기능 | 실제 flow·플랫폼·등록 액션·coordinator·진단 코드 | 실제 제공할 기능과 플랫폼 목록, 해당 entry 데이터·외부 클라이언트 경계·UI 번역 |
| 지원 최소 HA | hacs.json·manifest·README 비교 | 명시한 지원 정책 |
| current 및 minimum HA 환경 | 실제 requirements·constraints·workflow | 검토한 HA·Python·플러그인 조합과 파일 경로 |
| 양언어 설명·지원 경로·라이선스 고지 | 기존 본문·LICENSE·확인한 원격 기능 | 양언어 입력·실제 LICENSE 확인 |
| payload 경로·크기·팔레트·adapter | 실제 액션·기기·production 코드 | 실제 기능이 정해진 뒤 입력, 가짜 기본값 금지 |

출처가 다른 선언은 조사 결과에 함께 남기고 높은 버전이나 편리한 값을 임의 선택하지 않습니다. requirements의 배포 이름·extras·연산자·marker를 보존하고, 라이브러리 사용 조건은 기존 검사기와 공유합니다. marker 비활성과 라이브러리 미사용은 구분합니다. 미지원 requirement 형식을 임의 단순화하지 않습니다.

`--standards-ref`는 존재하는 검토 full SHA여야 합니다. 그 커밋의 규칙·계약·템플릿·도구를 별도 checkout에서 함께 사용하며 caller 작업 트리를 대체하지 않습니다. 초기 버전은 현재 CLI checkout의 HEAD가 지정 SHA와 일치하고 실행 자산이 수정되지 않았는지 확인하며, 다른 SHA를 인자로만 받아 현재 도구로 실행하지 않습니다. 잘못된 SHA·수정된 실행 자산·지원하지 않는 계약 버전은 차단합니다. 생성한 reusable workflow·action 참조와 해당 `standards-ref`를 같은 SHA로 맞춥니다.

최신 중앙 현황 조회와 검토 SHA 고정은 별개입니다. 중앙 현황 갱신은 기존 [절차](adoption-status.md#갱신-절차)를 따르며 CLI의 로컬 파일 적용이 원격 현황 갱신을 대신하지 않습니다.

## 5. CLI와 변경 계획

`inspect`·`plan`과 T3의 `apply`·`recover`를 구현하고 독립 코드 검증을 완료했습니다. T4는 기존 `check_integration.py`의 읽기 전용 검사에 생성물 계약 검사를 연결하고 main에 반영했습니다. `<...>`는 실제 확인한 값으로 교체하는 설명용 표기이며, 실행 조건과 현재 제한은 [사용 안내](template-skill-usage.md)를 따릅니다.

```text
python3 scripts/manage_integration.py inspect <target> --output <work>/inventory.json
python3 scripts/manage_integration.py plan <target> --mode create|adopt --input <input.json> --standards-ref <full-sha> --output <work>/plan.json
python3 scripts/manage_integration.py apply <target> --plan <work>/plan.json --journal <work>/journal.json
python3 scripts/manage_integration.py recover <target> --journal <work>/journal.json
python3 scripts/check_integration.py <target> --check
```

1. **inspect:** 읽기 전용으로 메타데이터·버전 선언·조건부 기능·관리 경계·사용자 변경을 수집합니다. 불명확한 값에는 원인과 필요한 확인을 표시하고 패키지 설치·workflow 실행·원격 쓰기는 하지 않습니다.
2. **plan:** 같은 원본·입력·대상에서 같은 변경 계획과 unified diff를 만듭니다. 각 경로에 생성/관리 영역 갱신/변경 없음/충돌/수동 작성 필요, 관련 규칙·원본·입력 출처·전후 해시를 기록합니다. 검증한 sourced 입력의 독립 복사본을 `validated_input`으로 포함하고 canonical JSON의 SHA-256을 `input_digest`에 기록하므로 원본 입력 파일을 다시 읽지 않고 입력 스냅샷을 검증할 수 있습니다. 계획 스키마는 중앙 입력 스키마를 로컬 `$ref`로 연결하며 resolver는 정확한 세 스키마 파일 외 URI·경로를 거부합니다. 내용과 diff는 계획에 담고 경로·SHA·해시를 검증해 읽습니다. 조사·렌더링 도중 대상 상태가 변하면 충돌로 차단합니다.
3. **apply:** 계획의 내장 입력을 스키마로 검증하고 digest를 확인한 뒤, 동일 SHA와 guards에 대해 재계획하여 operation 경로·소유 방식·content·after hash를 대조합니다. target identity의 `root_exists`를 포함한 원래 대상 루트 존재 상태·대상 전후 상태·계약 버전도 확인한 뒤 관리 범위만 적용합니다. 계획 이후 파일 변경, 새 파일 경로 충돌, 경로 이탈·symlink/junction 이탈, 지원 최소 변경, 읽지 못한 기존 파일은 쓰기 전에 차단합니다. 관련 입력·보존 대상의 해시도 확인하고 작업 도중 잠금·쓰기 직전 재확인으로 동시 편집을 보호합니다. 이전 T2 계획에는 새 필수 필드가 없고 기준 SHA도 다르므로 T3 SHA에서 재생성합니다.
4. **check:** 기존 CLI와 예외 경로를 유지한 채 같은 계약·렌더러로 형식·선택 기능/대응 테스트·번역 구조/확인 가능한 사용 키·SHA·정확한 작성 기반 미완성 표시를 검사합니다. 기본/`--check` 중에는 파일을 쓰거나 자동 적용·의존성 설치를 하지 않습니다. 기존 `--write-readmes`는 명시적 관리 영역 갱신 모드로 유지하고 사전 검사·본문 보호를 유지합니다. 이 정적 검사는 실제 HA 동작·임의 테스트 실행 의미·번역 의미를 증명하지 않으며 별도 실행과 리뷰를 요구합니다. 중앙 검사기는 같은 계약과 schema/scaffold 무결성을 검사하되 의도적인 중앙 작성 기반 TODO와 실제 생성물의 미완성을 구분합니다.

계획에 미해결 충돌이나 필수 입력 누락이 있으면 apply를 차단합니다. 실제 테스트·기기 설명 등 수동 작성이 필요한 기반 파일은 초안으로 생성할 수 있지만 검사와 체크리스트는 미완료로 남깁니다. 생성 직후 무조건 PASS가 되도록 비어 있는 테스트·가짜 액션·일괄 skip을 만들지 않습니다.

종료 코드는 새 CLI에서 `0`=해당 명령 성공, `1`=형식 불일치·미완료·계약 위반, `2`=입력 오류·충돌·오래된 계획·I/O 오류로 구분합니다. plan의 `0`은 적용 가능한 변경안 작성 성공만 뜻하며 HA 검증 성공이 아닙니다. 초안을 포함한 계획은 `pending` 목록을 출력하고 check는 미완료를 보고합니다. 기존 CLI 종료 코드·오류 의미는 호환을 유지합니다.

apply는 파일별 임시 쓰기·교체와 대상 밖 journal의 base64 원본·전후 해시를 사용합니다. 대상 쓰기 전에 journal과 고정 형제 `<journal>.plan.json`의 검토 계획 anchor를 기존 파일을 덮어쓰지 않고 게시합니다. 다중 파일 전체가 원자적이라고 주장하지 않습니다. 중간 실패 시 변경한 경로·복구 방법을 반환하며 `recover`는 anchor와 내장 계획·digest를 대조한 뒤 guard·backup으로 원래 상태를 외부 임시 경로에 재현하고 같은 SHA로 재계획합니다. anchor 부재·변조·재현 불가나 현재 파일 해시 불일치는 거부하여 후속 사용자 편집을 덮어쓰지 않습니다. 원래 루트 존재 여부와 생성 경로를 구분하여 복구합니다. journal과 anchor를 함께 보존하며 모든 산출물을 함께 수정하는 동일 사용자에 대한 신원 인증을 보장한다고 주장하지 않습니다. `git reset`·`git clean`으로 복구하지 않습니다. 생성물의 인코딩·개행 정책을 계약에 정하고, 관리 영역 밖의 기존 바이트는 유지합니다.

## 6. 스킬 실행 계약과 배포

두 스킬의 `SKILL.md`에는 발동 범위, 필수 입력, 읽을 규칙, 사용할 CLI, 중단 조건, 최종 증거 위치를 적습니다. 신규 생성과 기존 채택을 혼동하지 않고 단순 검토 요청은 읽기 전용으로 처리합니다. 라이브러리별 참고 문서는 같은 SHA의 중앙 원본을 연결합니다.

스킬은 inspect → 관련 규칙 확인 → plan/diff 검토 → 요청 범위의 apply → 실제 구현 보완 → 검사·실행 검증 → 기록 순서를 안내합니다. 기존 AGENTS·본문 보존·예외·위임 정책을 참조하며 자체 정책으로 재정의하지 않습니다. 스킬 실행만으로 commit/push·PR·릴리스·다른 리포 작업 권한을 얻지 않습니다.

중앙 `skills/`를 배포 원본으로 두며 명시적 설치·갱신·실행 방법은 [사용 안내](template-skill-usage.md)에 기록합니다. 각 스킬의 SKILL.md·references/workflow.md·agents/openai.yaml은 같은 원본 SHA에서 유지합니다. 중앙 규칙·템플릿은 스킬에 복사하지 않으며, 설치된 스킬은 검토 SHA의 중앙 checkout으로 인계합니다. 이전 스킬과 새 도구 조합은 계약 버전 검사로 호환 여부를 확인합니다. 대상 통합에 `.agents/skills`나 다른 에이전트 진입 파일을 자동 설치하지 않습니다. 중앙 checkout만으로 다른 리포에서 스킬이 자동 발견된다고 가정하지 않습니다.

## 7. 단계별 PR과 완료 조건

실제 구현은 [작업지시서 T1~T6](template-skill-tasks.md)의 파일·동작·검증 순서로 진행합니다. 현재 상태와 실행 근거는 [검증 기록](template-skill-validation.md)에 남깁니다. 각 구현 PR은 해당 범위의 테스트·문서·호환성 근거를 함께 제공하며, 이 설계 PR의 검사 결과를 구현 검증으로 재사용하지 않습니다.

| 단계 | 현재 상태 |
|---|---|
| T1 | 계약·스키마 검증·공통 렌더러 구현·독립 코드 검증 완료 |
| T2 | 읽기 전용 inspect/plan 구현·독립 코드 검증 완료 |
| T3 | apply·recover·새 작성 기반 구현·독립 검증·PR CI 성공·main 병합 |
| T4 | 생성물 검사·중앙 계약 연결 구현·독립 검증·PR CI 성공·main 병합 |
| T5 | 두 스킬·실행 안내·정적/격리 행동 검증·PR CI 성공·main 병합 |
| T6 | 중앙 자동 회귀 구현·독립 검증 완료; 최종 PR CI/병합 대기, 외부 실제 도입은 범위 밖 |

| 순서 | 구현 범위·주요 경로 | 완료 조건 |
|---|---|---|
| 1. 적용 계약·렌더러 | `templates/integration/contract.json`, 입력 스키마·예시, `scripts/standards/`, 기존 검사·배지 wrapper | 파일 소유 방식·조건·입력 출처가 명시되고 기존 출력·오류·보호 동작 회귀 유지 |
| 2. 조사·계획 | `scripts/manage_integration.py`의 inspect/plan, 조사·계획 스키마 | 기본 브랜치·버전 불일치·조건부 기능·관리 경계 조사, 재현 가능한 diff, target 밖 변경 없음 |
| 3. 신규·기존 적용 | apply·복구, 3.1~3.3의 컴포넌트·UI 번역·실제 HA 테스트 작성 기반 | 기능별 생성 목록·대응 테스트·번역·생명주기 연결, 반복 적용 무차이, 오래된 계획·경로 충돌 차단, 기존 본문·fixture·CI·지원 범위 보존 |
| 4. 검사·CI 연결 | `check_integration.py`, 문서 검사, `check_repository.py`, 필요 action/workflow | 생성과 검사 같은 계약 사용, 누락·미작성·SHA 불일치 실패, caller checkout 및 action_path 유지 |
| 5. 두 스킬 | `skills/create-ha-integration/`, `skills/adopt-ha-standards/`, 설치·사용 문서 | 신규/기존/단순 검토/조건부 문서 요청 구분, 같은 SHA 도구 연결, 무단 설치·적용 없음 |
| 6. 중앙 검증 | 중앙 fixture의 신규/기존·네 조건 자동 회귀 | 중앙 범위 검증·독립 리뷰·PR CI·main 반영으로 이번 요청 완료; 실제 외부 통합 도입은 별도 범위 |

계약 단계가 정해지기 전 템플릿을 대규모 이동하지 않습니다. 기존 경로·수동 채택 안내·CLI를 유지하고 새 방식이 검증된 뒤 안내를 전환합니다. 기존 채택 리포는 고정 SHA로 계속 동작하며, 새 기준 채택 요청에서 차이·예외·새 SHA를 기록합니다. 전환 실패 시 기존 SHA·수동 경로를 유지하고 대상 변경은 검토한 복구 절차로만 되돌립니다.

## 8. 검증 계획

| 검증 축 | 필수 사례와 판정 |
|---|---|
| 재현성 | 동일 입력·SHA·대상에서 동일 계획, apply 후 재계획의 변경 없음 |
| 보존 | 양언어 긴 본문·이전 안내·고유 배지·고지·기기 예제·회귀 테스트·fixture 확장·전용 CI·최소 환경이 유지됨 |
| 경계·실패 | 없는/중복/역전 주석, 비어 있지 않은 고정 파일, domain 불일치·다중 manifest, 오래된 계획·동시 편집·쓰기 실패·경로 이탈·부분 적용 복구 |
| 조건부 구성 | 기본만/imagespec만/blesession만/둘 다, extras·배포 이름 정규화·절대 import·비활성 marker, 조건 제거 시 기존 문서 유지 |
| 컴포넌트·테스트 대응 | UI flow·실제 플랫폼·coordinator·진단·액션의 선택별 생성 파일과 대응 테스트 확인, 없는 기능의 빈 파일 생성 금지, 기존 YAML 설정·회귀 수집 범위 보존 |
| UI 번역 | 영어 소스와 배포용 en.json 동기화, ko.json의 키·placeholder·실제 사용 키 일치, 미해결 Core 참조 탐지, 실제 HA 번역 로딩. strings.json만 존재하면 완료 불가 |
| 미완성 탐지 | 미작성 설명·가짜 액션·빈/skip lifecycle 테스트가 완료로 분류되지 않음. 정적 탐지의 한계는 실제 실행·독립 리뷰로 확인 |
| CI 호환 | 실제 기본 브랜치와 공용 이벤트·예약식·특수 job·권한·timeout·required checks 영향, workflow/action/standards-ref SHA 일치 |
| 기존 도구 | 기존 unittest·배지/README 렌더링·문서/실행 계약·CLI 오류 코드 회귀 유지 |
| 실제 통합 | 정확한 지원 최소 HA와 current의 별도 호환 Python·플러그인, 실제 entry/platform/setup/unload 및 기존 회귀, pip check·HACS·Hassfest |
| payload | 실제 HA 스키마·통합 production 준비 함수·설치된 imagespec current/정확한 하한의 출력·크기·팔레트, 기기 명령 없이 검증 |
| 스킬 | 요청별 발동·분기·중단·도구 선택을 검증하고 CLI 실패·미검증을 성공으로 서술하지 않는지 확인 |

중앙 도구 테스트는 네트워크와 GitHub 쓰기 없이 임시 리포에서 실행합니다. 스키마 fixture와 테스트용 통합은 중앙 생성기 검증 근거이며 실제 채택·실물 기기 확인의 근거가 아닙니다. 정적 성공·실제 HA 성공·원격 CI·번역 의미·기기 확인을 각각 구분합니다.

이번 중앙 작업은 T6 자동 fixture 검증까지이며 외부 통합·하드웨어·실제 최소/current HA 도입 검증은 요청 범위 밖·미실행입니다. 중앙 도구와 두 스킬이 존재하고 검사됐다는 것과 개별 통합의 실제 완성·채택을 구분합니다. 중앙 리포는 채택 현황표 대상 통합이 아니므로 해당 표를 변경하지 않습니다.

구현 검증은 변경에 맞는 단위 테스트와 `python3 scripts/check_repository.py`를 실행하고, action/workflow 변경에는 actionlint와 해당 fixture 검사를 추가합니다. 실제 채택은 [체크리스트](checklist.md)에 명령·대상 커밋·실제 설치 버전·CI 링크·미검증 범위를 기록하고 [완료 기준](adoption-status.md)을 따릅니다. 외부 리포 검증 범위가 없으면 중앙 fixture까지만 보고하고 도입 완료로 기록하지 않습니다.
