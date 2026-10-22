# 공통 규칙 적용 권장 순서

**2026-10-17 기준 계획**입니다. [중앙 현황](adoption-status.md)의 적용 대상 HA 통합 **22개**를 아래 순서로 권장합니다. hass-kibble 첫 파일럿은 PR #8을 squash merge한 뒤, 사용자 재확인에 따라 최신 테스트와 기존 최소 지원을 분리해 f1a7039 커밋에 복원했습니다. 마감 문서 d9f649c에서 최소·최신 환경 각각 31개 테스트와 pip check·HACS·Hassfest의 원격 성공을 독립 확인하고 적용을 완료했습니다. hass-catprinter 두 번째 파일럿도 지원 최소 HA2025.2.0을 유지하며 최소·현재 HA와 imagespec/blesession 네 조합의 실제 HA 테스트 각84passed6skipped, pipcheck·HACS/Hassfest 및 최종 문서 커밋 CI를 독립 확인해 완료했습니다. 나머지 통합의 진행·검증 결과도 중앙 현황표에서 관리합니다.

근거는 [기존 CI 조사](ci-audit.md), [로컬 조사 스냅샷](ci-inventory.json), 그리고 이번에 읽은 로컬 checkout의 `manifest.json`, 테스트 디렉터리·`conftest.py`, `tests.yml`입니다. 로컬 파일은 원격 최신 상태와 다를 수 있으며, 아래 평가는 테스트 실행 결과나 CI 성공 판정이 아닙니다. 착수 시 원격 기본 브랜치·사용자 변경·실제 지원 범위를 다시 확인합니다.

## 선행 작업과 파일럿

공통 CI는 기존 caller 호환을 위해 `unit` 기본값을 유지하고, 실행용 템플릿은 `ha` 단일 최신 기준 job을 예시로 제공합니다. 예전 최소 지원을 실제로 약속하는 통합은 최소/현재가 다를 때 별도 job으로 검증합니다. [실제 HA 테스트 규칙](testing.md)에 따라 파일럿에서 실제 로딩 검증을 확인합니다. **첫 파일럿과 함께 공통 workflow·환경·템플릿을 보완하고 검증한 다음** 나머지에 확산합니다. caller 교체만으로 채택을 완료하지 않습니다.

첫 파일럿은 **hass-kibble**입니다. 최신 HA 테스트 환경은 HA 2026.10.2·Python 3.14·플러그인 0.13.373을 유지합니다. 테스트 최신화를 지원 최소 상향으로 잘못 해석했던 변경을 바로잡고 기존 최소 HA 2025.3.0 선언과 Python 3.13·플러그인 0.13.221의 별도 검증 환경을 복원했습니다. 현재·최소는 따로 검증하고 과거 최소 requirements·constraints는 Dependabot 자동 갱신에서 제외합니다. manifest의 외부 Python 요구사항과 HA 구성요소 의존성이 없고, BLE·전용 UI 없이 HTTP 조회·coordinator·sensor·button 경로로 기본 패턴을 확인할 수 있습니다. 기존 HA stub 테스트를 실제 fixture·config entry·플랫폼 로딩으로 바꾸는 기준 사례가 됩니다. 이는 코드 전체가 가장 작다는 판정이 아니라, 공유 환경을 처음 검증할 때 특수 의존성이 적다는 판단입니다.

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
| 8 · 테스트/CI 기반 추가 | [hass-jaalee](https://github.com/eigger/hass-jaalee) | Validate는 존재, 테스트 없음: Bluetooth 실제 HA 테스트 기반 추가 |
| 8 | [hass-melk-light](https://github.com/eigger/hass-melk-light) | 로컬에 테스트·CI 없음: Bluetooth 의존성·실제 HA 테스트·검증 workflow 추가 |

## 별도 범위와 제외

| 대상 | 권장 처리 |
|---|---|
| hass-imagespec-card | HA 통합 파일럿 안정화 후 문서·배지·권한·timeout 원칙 적용. JS lint/test/build/release는 유지 |
| hassble-android | 별도 Android 작업으로 문서·CI 원칙 적용. Gradle·서명·APK/AAB 전용 흐름 유지 |
| hassble-config | 별도 YAML/schema 작업으로 문서·CI 원칙 적용 |
| hassio-apps | 별도 앱 작업으로 pins·add-on linter·업데이트 흐름을 검토 |
| hass-cyx-rgb-led, hass-divoom | 사용자 요청으로 공통화 대상에서 제외. 별도 요청 전 수정하지 않음 |
| hass-gicisky | 보관·hass-ble-esl 이전 리포이므로 신규 이관에서 제외 |
| hass-coolled | hass-ble-led-sign과 같은 원격의 로컬 checkout이므로 중복 배정하지 않음 |
| hass-timemore | GitHub 목록 미확인. 원격 존재·접근 및 실제 유지 대상을 확인한 뒤 추가 여부 결정 |

각 리포 착수 시 [GOV-05](adoption.md#채택)에 따라 주 에이전트 직접 구현·검증을 기본으로 하며 변경 범위에 맞는 자체/독립 리뷰 방식과 선택 근거를 기록합니다. 중앙 공통 CI 수정은 담당자 한 명이 통합하고, 각 리포는 검증된 전체 SHA를 기록합니다. [GOV-04](adoption.md#채택)에 따라 작업 시작·종료·의미 있는 상태 변화에 [중앙 현황](adoption-status.md)을 갱신하고 상세 증거는 리포별 체크리스트로 연결하며, 필요한 검증이 남으면 완료로 표시하지 않습니다. 이 계획 자체는 기존 리포 변경이나 릴리스 실행 기록이 아닙니다.

## 향후 계획 · 공통 템플릿 생성·적용 자동화

**2026-10-18 논의에 따른 미착수 계획**입니다. 지침을 매번 해석해 작성하면서 발생하는 공통 포맷 차이와 누락을 줄이기 위해, 중앙 템플릿을 생성·갱신 도구로 적용하고 검사기로 일치 여부를 확인하는 방향으로 발전시킬 예정입니다. 이번에는 계획만 기록하며 도구·스킬을 구현하거나 다른 리포에 적용하지 않습니다. 앞의 통합별 권장 적용 순서도 유지합니다.

신규 HA 커스텀 통합에는 HACS 디렉터리·설정 구조, 양언어 README, `tests/components/<domain>/`의 실제 HA fixture·통합 로딩 테스트 기반, 공통 CI를 한 번에 생성할 예정입니다. 기존 리포에도 같은 중앙 원본을 사용하되, 기존 구현·문서 본문·기기 예제·회귀 테스트·지원 최소·사용자 변경을 보존하며 적용합니다. 공통 관리 영역과 리포별 확장 영역을 구분해, 공통 형식을 다시 작성하지 않고 각 리포가 필요한 고유 내용을 추가하도록 할 계획입니다.

라이브러리 사용 여부에 따라 다음 구성을 추가할 예정입니다. 공통 사용자 문서의 원본은 각 라이브러리에서 계속 유지하며 중앙과 통합 리포에 복제하지 않습니다.

| 조건 | 생성·적용할 구성 | 리포에서 작성·검증할 내용 |
|---|---|---|
| 모든 HA 통합 | HACS 구조, 양언어 README 공통 영역, 실제 HA 테스트 기반, 공통 CI | 실제 메타데이터·지원 범위·기능 설명, 외부 통신 mock과 실제 통합 로딩·회귀 테스트 |
| imagespec 사용 | [DOC-08](payload-documentation.md)의 양언어 payload 문서·실제 액션 예제 구조, imagespec [영어](https://github.com/eigger/imagespec/blob/main/docs/payload.md)·[한국어](https://github.com/eigger/imagespec/blob/main/docs/payload.ko.md) 원본 링크, 예제 검증 연결 | 실제 전체 액션 YAML·대상·출력 설정과 production 준비 경로. 실제 HA 및 설치된 imagespec current/정확한 하한에서 실행 검증하며, 없는 액션·기능은 만들지 않음 |
| blesession 사용 | [DOC-07](bluetooth-documentation.md)의 양언어 기기별 문제 해결 문서, 공통 프록시 설정·추천 기기를 제공하는 blesession [영어](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md)·[한국어](https://github.com/eigger/blesession/blob/main/docs/bluetooth.ko.md) 안내와 공통 문제 해결 원본 링크 | 실제 지원 기기·전원·깨우기·페어링·인증·전송 조건과 진단·로그. 기존 기기 안내를 보존하고 실물 미검증 범위를 명시 |

단계별 작업은 모두 **예정**이며, 생성된 파일이 있다는 이유로 실제 검증을 완료한 것으로 처리하지 않습니다.

| 단계 | 예정 작업 | 완료 조건 |
|---|---|---|
| 1 · 적용 계약 정리 | 기존 규칙·템플릿을 기준으로 중앙 관리 파일·영역, 치환 변수, 리포 확장 위치와 조건부 구성을 명시 | 신규·기존 리포의 적용 범위와 보존 대상, 미작성·예외 판정 기준이 정리됨 |
| 2 · 생성·갱신 도구 | 같은 원본·입력에서 같은 공통 형식을 생성하고, 기존 리포는 변경안을 확인한 뒤 관리 범위만 갱신하도록 구현 | 신규 기본 구조와 라이브러리별 구성이 재현되며, 반복 적용 시 불필요한 차이가 없고 기존 고유 내용이 보존됨 |
| 3 · 검사기·CI 연결 | 필수 파일·영역·링크 누락과 중앙 원본 대비 형식 이탈을 실패로 처리하고 실제 HA·payload 검증을 연결 | 누락·이탈 사례가 실패하며, 미작성·미실행·미검증을 PASS로 처리하지 않고 기존 최소/current 환경을 각각 검증함 |
| 4 · 스킬 진입점 제공 | 신규 생성·기존 적용·조건부 문서 구성·독립 리뷰·검증을 도구로 연결 | 규칙 전문을 스킬에 복제하지 않고 검토한 중앙 full SHA의 규칙·템플릿·도구를 함께 사용하며, reusable workflow와 `standards-ref`도 같은 SHA를 참조함 |
| 5 · 독립 검증 후 도입 | 별도 승인된 신규·기존 리포 범위에서 생성·갱신 결과와 보존 여부를 독립 리뷰 | 양언어 의미·정보 보존, 실제 통합 로딩·회귀 테스트·CI 및 조건부 예제가 검증되고 체크리스트에 실제 근거가 기록됨 |

2026-10-19 후속 [템플릿·스킬 구조 개편 구현안](template-skill-plan.md)에 파일별 관리 범위, 입력·SHA 계약, inspect/plan/apply/check 인터페이스, 단계별 PR과 검증 조건을 구체화했습니다. 도구·스킬 구현과 실제 통합 도입은 아직 미착수입니다. 이 계획은 기존 규칙의 ID·필수/권장 수준을 바꾸거나 다른 리포 수정·workflow 실행·commit/push·릴리스를 승인하는 근거가 아닙니다.
