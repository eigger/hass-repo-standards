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

## 템플릿 생성 구조 검토

다음 자료는 **2026-10-19 재확인**했습니다. [템플릿·스킬 구현안](template-skill-plan.md)의 생성 구조와 검증 근거이며, 위 표 전체의 재확인일을 갱신한 것은 아닙니다.

| 자료 | 확인한 범위 |
|---|---|
| [HA 파일 구조](https://contributors.home-assistant.io/core/integrations/file-structure/) | domain 디렉터리, 기본 init·manifest, 기능별 flow·플랫폼·coordinator·진단 모듈 역할 |
| [HA 커스텀 통합 번역](https://contributors.home-assistant.io/core/integrations/translations/#custom-integrations) | 완성된 translations/en.json 직접 배포, strings.json 자동 컴파일 없음, Core 문자열 참조 미지원 |
| [HA config entries](https://contributors.home-assistant.io/core/integrations/config-entries/) | 실제 setup·플랫폼 전달·unload·자원 정리·migration, 지원 최소별 API 확인 필요 |
| [HA pytest 실행](https://contributors.home-assistant.io/core/development/testing/) | tests/components/domain 실행, Core 품질 등급별 coverage와 커스텀 통합 프로젝트 정책 구분 |

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

## imagespec payload 참고와 검증 범위

다음은 공식 HA 요구사항이 아닌 라이브러리 소유 자료입니다. 중앙 DOC-08은 프로젝트 정책이며 실제 HA schema·renderer 실행 의무와 통합별 고정 문서 틀을 정합니다.

- [imagespec 공통 영어 안내](https://github.com/eigger/imagespec/blob/main/docs/payload.md) / [한국어 안내](https://github.com/eigger/imagespec/blob/main/docs/payload.ko.md): 공통 문법·값·색상·회전·디더링·최소 렌더링 예제. 신규 문서가 로컬 초안인 동안 원격 존재를 확인했다고 쓰지 않으며 실제 기본 브랜치 반영 후 URL을 확인합니다.
- [imagespec 속성 참조](https://github.com/eigger/imagespec/blob/main/docs/reference.md), [요소 예제](https://github.com/eigger/imagespec/blob/main/docs/elements.md), [디더링](https://github.com/eigger/imagespec/blob/main/docs/dithering.md), [호스트 통합](https://github.com/eigger/imagespec/blob/main/docs/integrating.md): 실제 설치 버전의 키·API·RenderContext·지원 범위와 대조하는 라이브러리 원본. 전체 매뉴얼을 중앙에 복제하지 않습니다.

2026-10-18 로컬 문서 작성은 imagespec checkout의 실제 public validate/render·소스·스키마를 기준으로 검증하며 기존 지원 최소·버전·릴리스 정책은 변경하지 않습니다. HA fixture·서비스 스키마 실행 증거와 이미지 렌더링 증거·기기 전달/실물 검증을 구분합니다.

## 에이전트 스킬 호환성

이 절의 확인일은 **2026-10-19**입니다. 에이전트 클라이언트의 스킬 형식·탐색 경로 자료이며 HA의 공식 요구사항과 관계없습니다. 위 HA 자료 표 전체의 확인일을 갱신한 의미도 아닙니다.

| 공식 자료 | 확인 용도 |
|---|---|
| [OpenAI Build skills](https://learn.chatgpt.com/docs/build-skills) | SKILL.md와 공용 지원 파일, 선택 agents/openai.yaml, Codex의 workspace `.agents/skills`·사용자 `~/.agents/skills` |
| [Claude Code skills](https://code.claude.com/docs/en/skills) | 공용 Agent Skills 지원과 workspace `.claude/skills`·사용자 `~/.claude/skills` |
| [Antigravity skills](https://antigravity.google/docs/skills) | App·CLI·IDE별 workspace `.agents/skills`, App/IDE 사용자 `~/.gemini/config/skills`, CLI 사용자 `~/.gemini/antigravity-cli/skills` |

형식 호환과 이 리포의 실제 행동 검증을 구분합니다. Codex의 격리 실행만 검증했고 다른 클라이언트·일반 웹 채팅·자동 발동은 검증하지 않았습니다. 중앙 collaboration 위임 등 제품 기능에 의존하는 정책의 호환성을 확인하기 전 모든 클라이언트에서 동일 실행을 보장한다고 주장하지 않습니다. 명시적 설치 방법과 현재 범위는 [사용 안내](template-skill-usage.md)를 따릅니다.
