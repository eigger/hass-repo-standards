# 테스트와 호환성 규칙

커스텀 통합은 **HA Core의 컴포넌트 테스트 구조와 실제 HA 실행 경로**를 기준으로 작성합니다. Core의 테스트 도구를 커스텀 통합에서 사용할 때는 [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)를 사용합니다. 아래 필수 항목은 프로젝트 정책입니다.

## 폴더 구조

**TEST-08 필수**: 통합 테스트는 Core와 동일한 `tests/components/<domain>/`에 둡니다. 단일 통합 리포도 domain 계층을 생략하지 않습니다. 새 통합을 `tests/test_sensor.py` 같은 평면 구조로 만들지 않습니다. 다음은 배치 기준이며, 구현하지 않은 플랫폼의 빈 테스트 파일을 만들 필요는 없습니다.

```text
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
        ├── test_sensor.py
        ├── test_coordinator.py
        ├── test_diagnostics.py
        ├── fixtures/
        │   └── device_response.json
        └── snapshots/
```

| 경로 | 역할 |
|---|---|
| `tests/conftest.py` | 실제 HA 테스트 플러그인과 리포 공통 fixture 설정 |
| `tests/components/<domain>/conftest.py` | 해당 통합의 entry·외부 클라이언트·응답 fixture |
| `test_init.py` | 실제 entry setup, 실패·복구, unload/reload, 정리 |
| `test_config_flow.py` | HA flow manager를 통한 설정·중복·실패·재인증 |
| `test_<platform>.py` | 실제 플랫폼 로딩 후 상태·registry·action 검증 |
| `test_coordinator.py` | 실제 coordinator의 갱신·예외·복구 검증 |
| `test_diagnostics.py` | 진단 결과와 민감 정보 제거 |
| `fixtures/` | 해당 domain의 비식별 응답·패킷 데이터 |
| `snapshots/` | 사용하는 snapshot extension에 맞춘 domain별 snapshot |

공통 helper는 여러 테스트에서 실제 공유할 때만 둡니다. fixture·snapshot 로더의 기준 경로는 사용하는 플러그인에서 확인합니다. snapshot 사용 시 해당 extension과 fixture 설정을 함께 추가합니다. 독립적인 규칙 검사 도구 등 HA 통합이 아닌 코드의 테스트에는 이 domain 구조를 강제하지 않습니다.

## 실제 Home Assistant를 사용하는 기준

**TEST-01 필수**: 버그 수정은 재현되는 회귀 테스트를 추가합니다. 성공뿐 아니라 잘못된 데이터, timeout, disconnect, 중복 설정, unload/cleanup 등 사용자 동작을 검증합니다. 단순 문구 수정에 구현을 복제한 테스트를 만들지 않습니다.

**TEST-02 필수**: 각 통합은 실제 HA 테스트를 필수 검사로 둡니다. `ha` profile에서 실제 `homeassistant`와 HA 테스트 플러그인을 로드합니다. HA 코어 모듈을 `sys.modules`에 가짜로 등록하거나, `HomeAssistant`·entity platform·config entry manager를 자체 stub으로 대체한 테스트는 통합 검증으로 인정하지 않습니다. 순수 parsing·계산 단위 테스트는 같은 domain 아래 보조 검사로 둘 수 있지만 HA 통합 테스트를 대체하지 않습니다.

**TEST-03 필수**: 커스텀 통합에서는 `hass`, `enable_custom_integrations` 등 실제 플러그인 fixture를 사용합니다. HA 버전, 플러그인, Python은 호환되는 검증 조합으로 고정합니다. `pytest-asyncio` 설정도 해당 조합에 맞춥니다. 플러그인 제약을 무시하는 `--no-deps`나 테스트 코어 복사본으로 환경을 억지로 맞추지 않습니다.

Core의 helper 경로 `tests.common`은 커스텀 통합에서 `pytest_homeassistant_custom_component.common`으로 대응합니다. 이 경로의 `MockConfigEntry` 같은 HA 호환 테스트 helper는 사용할 수 있습니다. 이는 실제 HA 테스트 fixture와 함께 사용하는 entry 생성 도구이며, 가짜 HA 런타임을 만드는 방식과 다릅니다.

**TEST-09 필수**: 테스트 대상 통합을 HA loader와 config entry 경로로 로딩합니다. entry를 실제 `hass`에 등록하고 `hass.config_entries.async_setup(entry.entry_id)`를 실행한 뒤 HA task 완료를 기다립니다. `hass.states`, entity/device registry, HA service/action 호출로 결과를 검증합니다. entity 객체를 직접 만들고 메서드 반환값만 확인하는 테스트만으로 플랫폼 검증을 끝내지 않습니다.

설정 테스트는 `hass.config_entries.flow`를 통해 시작하고 진행합니다. unload/reload는 config entry manager를 통해 실행하여 task·listener·연결 정리까지 확인합니다. 설정 흐름만 분리하는 개별 테스트에서 setup을 제한적으로 patch할 수 있으나, 실제 setup과 플랫폼 로딩을 실행하는 별도 테스트가 반드시 있어야 합니다.

## mock의 경계

**TEST-06 필수**: 기본 CI는 실물 장치·개인 계정·외부 서비스에 의존하지 않습니다. HTTP/BLE 전송, 소켓, 장치 클라이언트 같은 **외부 통신 경계만** mock/응답 fixture로 대체합니다. 검증할 HA 동작이나 통합 로직 자체를 mock하여 통과시키지 않습니다. 실제 기기 검증은 모델·펌웨어·환경을 적은 별도 절차로 관리합니다.

| 사용 가능 | 통합 검증을 대체할 수 없는 방식 |
|---|---|
| 실제 `hass` + HA 테스트 플러그인 fixture | 자체 `FakeHass`, 가짜 `homeassistant.*` 모듈 |
| 플러그인의 config entry·registry·시간 제어 helper | 자체 registry·event loop 생명주기 구현 |
| 외부 API/장치의 정상·오류 응답 | 상태·action 결과를 미리 mock하고 같은 값 확인 |
| BLE 전송과 연결 실패 제어 | HA Bluetooth 구성요소 전체를 stub으로 교체 |

**TEST-07 필수**: 구현한 기능에 해당하는 config flow 성공·실패·중복·재인증, entry setup/unload·migration, 플랫폼 상태·action, unavailable 복구를 검증합니다. 지원하지 않는 기능은 검사를 억지로 추가하지 않고 해당 없음의 이유를 기록합니다. coverage 숫자만으로 위 경로의 검증을 대신하지 않습니다.

## 호환성과 의존성

**TEST-04 필수**: 최소 HA를 지원한다고 선언하면 별도 환경에서 그 **정확한 버전**을 실제 fixture로 테스트합니다. `homeassistant>=최소버전`과 Python matrix는 최소 HA 검증이 아닙니다. 미검증 기존 리포는 예외와 보완 계획을 기록하고, 테스트 편의를 위해 지원 버전을 임의로 올리지 않습니다.

**TEST-05 필수**: imagespec·blesession 등의 최소 버전과 현재 선택 버전을 별도 환경에서 검증합니다. 두 환경 모두 실제 HA 통합 테스트를 실행합니다. 정확한 하한 버전의 설치값을 확인하고 test requirements 및 HA 요구사항과 함께 resolver·`pip check`를 통과해야 합니다. 상세 선언·추가 절차는 [의존성 규칙](dependencies.md)을 따릅니다.

## 채택 시 실행과 완료 기준

통합의 기본 pytest 대상은 `tests/components/<domain>/`입니다. 예를 들어 `python -m pytest tests/components/example/ -v`로 실행합니다. pytest discovery 설정과 CI의 테스트 경로를 함께 맞추고 기존 회귀 테스트를 빠뜨리지 않습니다.

채택 완료에는 실제 HA로 통합을 로딩한 결과, 검증한 HA/Python/플러그인 버전, 최소 라이브러리 설치값, 제외·skip 사유가 필요합니다. HA 패키지가 설치됐다는 summary나 `test-profile: ha` 설정만으로 완료 처리하지 않습니다.

공통 CI는 기존 caller 호환을 위해 `unit` 기본값을 유지합니다. 실행용 템플릿은 `ha`와 두 HA 환경을 명시하며, 환경 action은 실제 HA·플러그인의 설치를 확인합니다. 채택 시 실제 지원 최소 HA와 현재 HA의 호환 조합으로 입력·requirements를 바꾸고 위 구조·실제 로딩 테스트를 실행해야 합니다. 환경 설치 확인은 통합 로딩 검증을 대신하지 않습니다.
