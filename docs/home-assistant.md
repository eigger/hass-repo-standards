# Home Assistant 개발 규칙

공식 API 근거는 [공식 자료](sources.md)를 참고합니다. 아래 필수 항목은 이 프로젝트가 채택한 구현 기준입니다. Core 전용 제출 규칙과 커스텀 통합의 의무를 혼동하지 않습니다.

## Core와 구조를 맞추는 기준

**HA-13 필수**: HACS 배포용 커스텀 통합도 HA Core 편입을 고려한 모듈 구성·공개 API·생명주기·테스트 구조로 작성합니다. Core 코드를 통째로 복사하거나 별도 HA 호환 계층을 만드는 방식으로 구조를 맞추지 않습니다. 배포 경로와 커스텀 메타데이터 차이를 제외한 구현 방식은 Core를 기준으로 합니다.

| 항목 | HA Core | HACS 커스텀 통합의 공통 기준 |
|---|---|---|
| 구현 경로 | `homeassistant/components/<domain>/` | `custom_components/<domain>/` |
| 내부 모듈 | `__init__`, config flow, coordinator, entity, 플랫폼 등 | 필요한 모듈을 같은 역할·이름으로 구성 |
| 테스트 | `tests/components/<domain>/` | 동일한 domain 계층과 파일 배치 |
| 테스트 런타임 | Core 테스트 fixture·helper | 실제 HA + custom component pytest fixture·helper |
| HA API | Core의 공개 API와 config entry 생명주기 | 같은 API·로딩·설정·플랫폼 경로 사용 |
| 의존성 | 통합 manifest의 패키지·HA 구성요소 선언 | 같은 의미로 선언, tests/CI에서 실제 설치·로딩 |
| 배포 메타데이터 | Core 소스·배포 체계 | 커스텀 manifest.version, hacs.json, 설치 문서 유지 |
| 번역·품질 정보 | Core의 번역·품질 관리 체계 | 커스텀에 필요한 번역 유지, 공식 품질 등급 자가 표기 금지 |

필요한 파일만 추가합니다. 공통 entity 동작이 있으면 `entity.py`, API 경계가 필요하면 `api.py`, 진단을 제공하면 `diagnostics.py`를 두며 모든 통합에 빈 파일을 강제하지 않습니다. 엔티티 플랫폼 파일과 테스트 파일은 서로 대응시킵니다. 구체적인 테스트 트리는 [테스트 규칙](testing.md)에 정의합니다.

## 구조와 메타데이터

**HA-01 필수**: 배포 경로는 `custom_components/<domain>/`입니다. domain은 디렉터리·manifest·상수에서 일치해야 합니다. 공개된 domain과 unique ID 형식은 사용자 데이터 계약으로 취급합니다. 변경은 릴리스 문서와 마이그레이션 계획을 동반합니다.

**HA-02 필수**: manifest에는 domain, name, version, documentation, issue_tracker, codeowners를 둡니다. 이 목록은 프로젝트 기준이며 공식 필수 필드의 보편적 목록을 뜻하지 않습니다. iot_class·integration_type·config_flow·discovery·dependencies는 실제 동작에 맞춥니다. keys는 domain, name 이후 알파벳순으로 정리합니다. `quality_scale`에 자가 인증 등급을 넣지 않습니다.

**HA-03 권장**: `const.py`에는 공통 상수, `config_flow.py`에는 설정, `coordinator.py`에는 공동 데이터 갱신, 플랫폼 파일에는 엔티티를 둡니다. 파일 분할만을 위한 추상화는 만들지 않습니다. 프로토콜/라이브러리 코드와 HA 엔티티 연결 코드를 분리합니다.

## 설정과 생명주기

**HA-04 필수**: 새 장치·서비스 통합은 UI config flow를 기본으로 합니다. 연결 확인, 중복 설정 방지, 안정적인 식별, 인증 오류를 다룹니다. options flow·reauth·reconfigure는 실제 필요에 맞게 구현합니다. entry 데이터 변경에는 schema version과 migration 테스트가 필요합니다.

**HA-05 필수**: 사용 중인 HA 버전의 config entry API를 사용합니다. setup 실패 시 일시적 연결 오류와 인증 실패를 구분합니다. unload/reload 시 플랫폼·타이머·listener·task·연결을 정리하고, 부분 setup 실패에서도 정리합니다. typed `ConfigEntry.runtime_data`를 권장하되 지원 최소 HA에서 가능한지 먼저 확인합니다.

## 비동기·데이터·엔티티

**HA-06 필수**: event loop에서 blocking 네트워크·파일·sleep 작업을 하지 않습니다. async 클라이언트 또는 executor를 사용하며 executor 적용 범위 전체의 blocking을 확인합니다. 공유 HTTP 세션과 명시적 timeout을 사용합니다. 취소 예외를 삼키거나 무한 재시도하지 않습니다.

**HA-07 필수**: 같은 API를 여러 엔티티가 중복 polling하지 않도록 합니다. coordinator는 적합할 때 사용하며 push는 push 흐름을 보존합니다. 상태 property에서 I/O를 하지 않습니다. 실패 데이터로 정상값·0을 덮어쓰지 않고 unavailable/unknown을 정확히 사용합니다.

**HA-08 필수**: 엔티티 unique ID는 재시작 후 안정적이어야 합니다. 이름·장치 정보·단위·device_class·state_class는 실제 의미에 맞춥니다. 변경 시 기존 registry와 장기 통계 영향을 검토합니다. 선택 기능은 실제 지원 기기에만 노출합니다.

## BLE와 의존 라이브러리

**HA-09 필수**: Bluetooth 장치는 HA Bluetooth 관리 API를 우선 사용하고, 지원을 선언한 경우 ESPHome proxy 경로도 확인합니다. 무분별한 독립 스캔·연결 중복을 피합니다. disconnect, 재연결, 서비스 변경, 취소 상황을 테스트합니다. MAC/주소만으로 영구 식별을 가정하지 않습니다.

**HA-10 필수**: imagespec은 렌더링/명세 경계, blesession은 BLE 세션 경계 등 각 라이브러리 책임을 유지합니다. 라이브러리 내부 private API를 가져오지 않습니다. upstream 변경 시 manifest 요구사항, 최소 버전 테스트, 문서 예제를 함께 검토합니다.

## 사용자에게 보이는 동작

**HA-11 필수**: `strings.json`과 필요한 `translations/*.json`, `services.yaml`을 실제 action/schema와 맞춥니다. 사용자 문자열은 번역 키를 사용하고 로그와 오류 메시지는 원인·복구 방법이 드러나게 작성합니다.

**HA-12 필수**: 로그·diagnostics·테스트 fixture에서 토큰, 비밀번호, 전화번호, 장치 식별 정보 등 민감 값을 제거합니다. diagnostics는 제공할 때 redaction 테스트를 둡니다. 정상적인 재시도마다 동일 경고를 쌓지 않습니다.
