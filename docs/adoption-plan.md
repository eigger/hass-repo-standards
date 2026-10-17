# 공통 규칙 적용 권장 순서

**2026-10-17 기준 계획**입니다. [중앙 현황](adoption-status.md)의 활성 HA 통합 **24개**를 아래 순서로 권장합니다. 이번 단계는 목록과 순서를 정하는 작업이며 개별 통합의 적용·테스트를 시작하거나 현황표의 상태를 변경하지 않았습니다.

근거는 [기존 CI 조사](ci-audit.md), [로컬 조사 스냅샷](ci-inventory.json), 그리고 이번에 읽은 로컬 checkout의 `manifest.json`, 테스트 디렉터리·`conftest.py`, `tests.yml`입니다. 로컬 파일은 원격 최신 상태와 다를 수 있으며, 아래 평가는 테스트 실행 결과나 CI 성공 판정이 아닙니다. 착수 시 원격 기본 브랜치·사용자 변경·실제 지원 범위를 다시 확인합니다.

## 선행 작업과 파일럿

현재 공통 CI의 `unit` 기본값과 실행용 템플릿은 [실제 HA 테스트 규칙](testing.md)의 필수 구조·로딩 검증으로 아직 전환되지 않았습니다. **첫 파일럿과 함께 공통 workflow·환경·템플릿을 보완하고 검증한 다음** 나머지에 확산합니다. caller 교체만으로 채택을 완료하지 않습니다.

첫 파일럿은 **hass-kibble**을 권장합니다. manifest의 외부 Python 요구사항과 HA 구성요소 의존성이 없고, BLE·전용 UI 없이 HTTP 조회·coordinator·sensor·button 경로로 기본 패턴을 확인할 수 있습니다. 기존 HA stub 테스트를 실제 fixture·config entry·플랫폼 로딩으로 바꾸는 기준 사례가 됩니다. 이는 코드 전체가 가장 작다는 판정이 아니라, 공유 환경을 처음 검증할 때 특수 의존성이 적다는 판단입니다.

두 번째는 **hass-catprinter**입니다. `imagespec[datamatrix]`와 `blesession`을 모두 선언하고 기존 CI에 current/minimum 의존성 matrix가 있어, 두 라이브러리·extras·업데이트 bot·Bluetooth proxy 안내를 함께 검증할 대표 사례입니다. 기존 프로토콜 테스트를 유지하면서 실제 HA 로딩 테스트를 추가해야 합니다. `hass-marklife`는 현재 manifest가 imagespec만 선언하므로 두 라이브러리의 동시 파일럿은 catprinter를 사용합니다.

## 단계별 대상

같은 단계는 앞 단계에서 공통 변경을 확정한 뒤 병렬 진행할 수 있습니다. 표의 순서는 권장 착수 순서이며, 복잡도나 작업 시간의 확정 추정은 아닙니다.

| 단계 | 리포 | 우선 적용·확인할 대표 항목 |
|---|---|---|
| 1 · 기본 파일럿 | [hass-kibble](https://github.com/eigger/hass-kibble) | HTTP 외부 경계만 mock, 실제 HA setup/flow/platform/unload, 공통 Validate/Tests·문서·배지 |
| 2 · 복합 의존성 파일럿 | [hass-catprinter](https://github.com/eigger/hass-catprinter) | imagespec+blesession current/minimum, 프로토콜 회귀 유지, 실제 HA 테스트 추가, updater와 proxy 문서 |
| 3 · HA/BLE 환경 확장 | [hass-icscale](https://github.com/eigger/hass-icscale) | 기존 실제 HA fixture·entry setup을 domain 구조로 이관, Bluetooth 구성요소 설치·세션 테스트 |
| 3 | [hass-niimbot](https://github.com/eigger/hass-niimbot) | 기존 실제 HA fixture, imagespec+blesession, recorder 후행 의존성·플랫폼·서비스 회귀 |
| 3 | [hass-omron](https://github.com/eigger/hass-omron) | 기존 실제 HA fixture와 많은 프로토콜 회귀 보존, blesession updater·Bluetooth 환경 공통화 |
| 4 · blesession 확산 | [hass-atflee](https://github.com/eigger/hass-atflee) | blesession updater와 Bluetooth 구성요소, 실제 HA 테스트·proxy 안내 |
| 4 | [hass-minibig](https://github.com/eigger/hass-minibig) | HA stub 교체, blesession·로컬 폴링·연결 정리 |
| 4 | [hass-magic-caster-wand](https://github.com/eigger/hass-magic-caster-wand) | HA stub 교체, numpy+blesession, Bluetooth 의존성·프로토콜/매크로 회귀 |
| 5 · HTTP/서비스 확산 | [hass-kma](https://github.com/eigger/hass-kma) | HA stub 교체, 외부 API 오류·재인증·센서 상태 |
| 5 | [hass-garage](https://github.com/eigger/hass-garage) | HA stub 교체, 양방향 전송·상태 변경 listener·debounce·unload 회귀 |
| 5 | [hass-kocom-smarthome](https://github.com/eigger/hass-kocom-smarthome) | 기존 정확한 최소 HA job의 범위 보존, 실제 fixture·통합 로딩까지 확대, 인증·비식별화 |
| 5 | [hass-opinet](https://github.com/eigger/hass-opinet) | pyproj 설치·하한 검증, fallback HA stub 제거, API·위치·센서 경로 |
| 5 | [hass-ws-bridge](https://github.com/eigger/hass-ws-bridge) | HA/aiohttp stub 교체, websocket_api 의존성과 서비스·camera 회귀 |
| 6 · 기타 BLE 확산 | [hass-marklife](https://github.com/eigger/hass-marklife) | imagespec 하한·recorder 후행 의존성, 독립 프로토콜 테스트와 실제 HA 테스트 병행 |
| 6 | [hass-ble-led-sign](https://github.com/eigger/hass-ble-led-sign) | imagespec·pillow·requests 선언 보존, HA stub 교체, updater·Bluetooth 안내 |
| 6 | [hass-lywsd02](https://github.com/eigger/hass-lywsd02) | HA/BLE stub 교체, Bluetooth 구성요소와 기존 회귀 범위 보존 |
| 6 | [hass-vson](https://github.com/eigger/hass-vson) | HA stub 교체, BLE 수신·플랫폼 상태·연결 정리 |
| 7 · 전용 기능 보존 | [hass-ble-esl](https://github.com/eigger/hass-ble-esl) | 실제 HA fixture와 imagespec+blesession 유지, editor 전용 job·브라우저 환경, frontend/http/panel/websocket 의존성 |
| 7 | [hass-esphome-ota](https://github.com/eigger/hass-esphome-ota) | 이미 있는 tests/components 구조 보존, 실제 로딩 범위 확인, panel·HTTP·WebSocket·빌드/게시·진단 회귀 |
| 7 | [hass-sip](https://github.com/eigger/hass-sip) | HA stub 교체, ffmpeg/llm/logbook/tts 및 assist_pipeline/stt 후행 의존성, 외부 음성·SIP 경계 분리 |
| 8 · 테스트/CI 기반 추가 | [hass-cyx-rgb-led](https://github.com/eigger/hass-cyx-rgb-led) | 로컬에 테스트·CI 없음: 실제 HA fixture·로딩 테스트와 Validate부터 작성 |
| 8 | [hass-divoom](https://github.com/eigger/hass-divoom) | 로컬 CI 없음: 기존 테스트 범위 확인 후 실제 HA 검증·공통 CI 추가 |
| 8 | [hass-jaalee](https://github.com/eigger/hass-jaalee) | Validate는 존재, 테스트 없음: Bluetooth 실제 HA 테스트 기반 추가 |
| 8 | [hass-melk-light](https://github.com/eigger/hass-melk-light) | 로컬에 테스트·CI 없음: Bluetooth 의존성·실제 HA 테스트·검증 workflow 추가 |

## 별도 범위와 제외

| 대상 | 권장 처리 |
|---|---|
| hass-imagespec-card | HA 통합 파일럿 안정화 후 문서·배지·권한·timeout 원칙 적용. JS lint/test/build/release는 유지 |
| hassble-android | 별도 Android 작업으로 문서·CI 원칙 적용. Gradle·서명·APK/AAB 전용 흐름 유지 |
| hassble-config | 별도 YAML/schema 작업으로 문서·CI 원칙 적용 |
| hassio-apps | 별도 앱 작업으로 pins·add-on linter·업데이트 흐름을 검토 |
| hass-gicisky | 보관·hass-ble-esl 이전 리포이므로 신규 이관에서 제외 |
| hass-coolled | hass-ble-led-sign과 같은 원격의 로컬 checkout이므로 중복 배정하지 않음 |
| hass-timemore | GitHub 목록 미확인. 원격 존재·접근 및 실제 유지 대상을 확인한 뒤 추가 여부 결정 |

각 리포 착수 시 [에이전트 지침](../AGENTS.md)에 따라 **구현 서브 에이전트와 독립 리뷰·검증 서브 에이전트**를 따로 배정합니다. 중앙 공통 CI 수정은 담당자 한 명이 통합하고, 각 리포는 검증된 전체 SHA를 기록합니다. 작업 시작·단계 변경·종료에 [중앙 현황](adoption-status.md)과 리포별 체크리스트를 갱신하며, 필요한 검증이 남으면 완료로 표시하지 않습니다. 이 계획 자체는 기존 리포 변경이나 릴리스 실행 기록이 아닙니다.
