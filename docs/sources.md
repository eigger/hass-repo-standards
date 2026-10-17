# 공식 자료

확인일: **2026-10-17**. 외부 문서는 변할 수 있으므로 API·규격 변경 시 해당 원문을 다시 확인합니다. 이 리포의 필수 정책을 모두 공식 요구사항으로 해석하지 않습니다.

| 자료 | 확인 용도 |
|---|---|
| [HA manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/) | 필드, domain, requirements, custom version |
| [Config entries](https://developers.home-assistant.io/docs/config_entries_index/) | setup/unload 생명주기 |
| [Fetching data](https://developers.home-assistant.io/docs/integration_fetching_data/) | polling/push/coordinator |
| [Blocking operations](https://developers.home-assistant.io/docs/asyncio_blocking_operations/) | event loop와 executor |
| [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) | 품질 개선 참고; 자가 인증 금지 |
| [Core 구현 예시](https://github.com/home-assistant/core/tree/63e9f9bf2eb899e8313257b2b22e63140f17c76f/homeassistant/components/airgradient) | 모듈 역할과 구조 참고 |
| [Core 테스트 예시](https://github.com/home-assistant/core/tree/63e9f9bf2eb899e8313257b2b22e63140f17c76f/tests/components/airgradient) | tests/components/domain, fixture·플랫폼·snapshot 배치 |
| [HA testing](https://developers.home-assistant.io/docs/development_testing/) | 테스트 실행 개념 |
| [플러그인 최소 예시 PyPI 메타데이터](https://pypi.org/pypi/pytest-homeassistant-custom-component/0.13.221/json) | HA 2025.3.0 · Python >=3.13 호환 선언 |
| [플러그인 현재 예시 PyPI 메타데이터](https://pypi.org/pypi/pytest-homeassistant-custom-component/0.13.373/json) | HA 2026.10.2 · Python >=3.14 호환 선언 |
| [Custom component pytest](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component) | 커스텀 통합 fixture와 버전 호환 |
| [HACS general](https://www.hacs.xyz/docs/publish/start/) | hacs.json, 최소 HA, 리포 메타데이터 |
| [HACS integration](https://www.hacs.xyz/docs/publish/integration/) | 통합 배포 구조 |
| [HACS action](https://www.hacs.xyz/docs/publish/action/) | validator와 입력·검사 제외 |
| [HACS 브랜드 검사 구현](https://github.com/hacs/integration/blob/adc26ec798021d2c2db1e6aa90eabe2e208b8c04/custom_components/hacs/validate/brands.py) | 로컬 brand/icon.png 우선·원격 custom domain fallback |
| [HA 브랜드 이미지](https://contributors.home-assistant.io/core/integrations/brands/) | 로컬 brand 지원 버전·PNG 규격 |
| [HACS default inclusion](https://www.hacs.xyz/docs/publish/include/) | Default 목록 등재 |
| [GitHub reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) | workflow_call, 입력, 권한 |
| [GitHub secure use](https://docs.github.com/en/actions/reference/security/secure-use) | 최소 권한·SHA·외부 입력 |
| [Dependabot 설정](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference) | 과거 최소 환경 exclude-paths·HA/플러그인 groups의 범위 |
| [GitHub event triggers](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow) | GITHUB_TOKEN 후속 workflow 제한 |
| [Python dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/) | 연산자, extras, marker |
| [PyPI JSON API](https://docs.pypi.org/api/json/) | 릴리스 파일, yanked, Requires-Python |
| [HA Analytics](https://www.home-assistant.io/integrations/analytics) | opt-in 통계 의미 |
| [Shields Release](https://shields.io/badges/git-hub-release) | release 배지 옵션 |
| [Shields Workflow](https://shields.io/badges/git-hub-actions-workflow-status) | branch와 상태 배지 |
| [Shields Downloads](https://shields.io/badges/git-hub-downloads-all-assets-all-releases) | release asset 집계 의미 |

## Bluetooth 설정 자료

- [HA Bluetooth](https://www.home-assistant.io/integrations/bluetooth/): 로컬·원격 어댑터와 연결/스캔.
- [ESPHome Bluetooth proxy](https://esphome.io/components/bluetooth_proxy/): active 연결, 수신 성능, 연결 용량.
- [ESP32 BLE tracker](https://esphome.io/components/esp32_ble_tracker/): active scan의 의미.
- [ESPHome 공식 프로젝트](https://esphome.io/projects/?type=bluetooth): 기기·리비전 지원과 설치 경로.
- [Seeed XIAO W5500](https://wiki.seeedstudio.com/esphome_xiao_w5500_ethernet_adapter/): V1.2 보드와 proxy 구성.
- [M5Stack AtomS3U](https://docs.m5stack.com/en/core/AtomS3U): USB-A 형태·ESP32-S3 사양. ESPHome 공식 Bluetooth proxy 설치 목록의 별도 대상이 아님. 확인일 2026-10-18.
- [M5Stack AtomS3U ESPHome 예제](https://github.com/m5stack/esphome-yaml/blob/main/examples/kit/atoms3u.yaml): esp32s3·8 MB·ESP-IDF, Wi-Fi 연결 시 ble.disable 동작 확인. 그대로 proxy 펌웨어로 사용하지 않음.
- [M5Stack AtomS3U 다운로드 모드](https://docs.m5stack.com/en/arduino/m5atoms3u/program): USB 최초 설치 준비.
- [ESPHome 시작 안내](https://esphome.io/install/getting-started/): Device Builder·검증·첫 USB 설치.
- [HA ESPHome](https://www.home-assistant.io/integrations/esphome/): 발견/수동 등록·API 포트·암호화 키.
- [ESPHome BLE](https://esphome.io/components/esp32_ble/): ble.disable. [BLE provisioning](https://esphome.io/components/esp32_improv/): 별도 Wi-Fi 설정 도우미와 proxy 동작 구분. Bluetooth 자료 재확인일 2026-10-18.
- [BLE ESL 한국어 README](https://github.com/eigger/hass-ble-esl/blob/main/README.ko.md#설치): 기존 설치 안내의 출발점.
- [blesession 계약](https://github.com/eigger/blesession/blob/main/docs/contract.md): 라이브러리와 통합 책임, 진단 정보.
