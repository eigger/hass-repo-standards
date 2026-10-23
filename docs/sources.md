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

## HACS 배지·설치 링크 재확인

다음 범위는 **2026-10-20** 확인했습니다. 배지 선택·배치 의무는 이 프로젝트 정책이며 HACS의 공식 배지 의무를 뜻하지 않습니다.

| 공식 자료 | 확인한 범위 |
|---|---|
| [HACS 데이터 원본](https://www.hacs.xyz/docs/faq/data_sources/) | Default integration 데이터는 data-v2.hacs.xyz/integration/data.json, Custom은 GitHub API 사용 |
| [HACS 데이터 생성 구현](https://github.com/hacs/integration/blob/a15e87ec0d1c82e58f1ddbaf17669d3eaa261eb8/scripts/data/generate_category_data.py) | 저장소 ID별 객체와 full_name 선택 |
| [HACS downloads 구현](https://github.com/hacs/integration/blob/a15e87ec0d1c82e58f1ddbaf17669d3eaa261eb8/custom_components/hacs/repositories/base.py) | exports의 downloads와 선택한 ref의 대상 asset download_count, 모든 릴리스·asset 합계나 활성 설치 수 아님 |
| [HACS My 링크 안내](https://www.hacs.xyz/docs/use/my/) | Default·Custom 모두 지원, owner·저장소 이름·Custom category=integration |
| [My 링크 공식 선언](https://github.com/home-assistant/my.home-assistant.io/blob/60656776768e236d79fc427de79b8bdf6b8771f3/redirect.json) | hacs_repository의 owner/repository/category 매개변수와 공식 SVG 배지 |

2026-10-20에는 이 환경의 data-v2 직접 조회가 HTTP 403으로 실시간 다운로드 수·렌더링을 검증하지 못했습니다. 아래 2026-10-23 재검증이 현재 배지 정책의 근거이며, 과거 확인을 실시간 성공으로 소급하지 않습니다.

### 2026-10-23 다운로드 배지 수정 근거

- [Shields JSONPath 구현](https://github.com/badges/shields/blob/8a54092113d396f6e42740d3677f3db948941f8a/services/dynamic/json-path.js)은 `eval: false`를 사용합니다. 기존 `full_name` 필터는 실제 배지에서 `query not supported`를 반환했습니다. 저장소 ID 직접 조회는 동작하지만 HACS 원본에 asset 다운로드 필드가 없는 통합의 설치 수를 제공하지는 않습니다.
- [Shields 전체 릴리스 다운로드](https://shields.io/badges/git-hub-downloads-all-assets-all-releases)는 모든 릴리스 asset의 합계입니다. [GitHub release asset API](https://docs.github.com/en/rest/releases/assets#get-a-release-asset)의 `download_count`가 집계 근거이며, 소스 코드 아카이브나 활성 설치 수와 구분합니다. DOC-03·DOC-05는 Default 배지를 이 방식의 `Downloads`로 수정합니다.
- [Wiser README](https://github.com/asantaga/wiserHomeAssistantPlatform#readme)는 최신 릴리스 다운로드와 Analytics를 별도로 표시하고, [Places README](https://github.com/custom-components/places#readme)는 누적·최신 다운로드·Analytics를 나란히 표시합니다. 실제 배지 응답은 각각 Wiser 2.7K/1,489 installs, Places 66K/5.3K/1,683 installs였습니다. 이는 확인 시점의 응답이며 고정 기대값으로 사용하지 않습니다.
- 두 리포는 `zip_release: true`와 `filename`을 선언합니다. [Places 배포 workflow](https://github.com/custom-components/places/blob/main/.github/workflows/release-please.yml)는 통합 디렉터리를 ZIP으로 만들어 릴리스 asset으로 업로드합니다. 중앙 배지 수정만으로 다른 리포의 배포 방식이나 과거 다운로드 이력을 변경하지 않습니다.
- 자체 리뷰 범위는 기준 중앙 `90a849209e23cc8e61369e2af44b06df6ab81d1e`의 배지 생성·이전 배지 이관·DOC-03/05 문서입니다. 초기 자체 리뷰 후 사용자 요청으로 [PR #14](https://github.com/eigger/hass-repo-standards/pull/14)에서 서브 에이전트 독립 리뷰를 진행합니다. HA 동작·지원 최소·공용 CI 실행 로직은 변경하지 않습니다. 대상 리포 적용·실제 사용자 설치는 이번 검증 범위에 포함하지 않습니다. 최종 대상 SHA·독립 리뷰·원격 CI 결과는 PR 본문에서 연결합니다.
- 검증: Windows Python 3.14.6/PyYAML 6.0.3/packaging 26.2에서 `python -X utf8 -m unittest discover -s tests -p test_tools.py` 24개 PASS. `python -m ruff check .`와 `python -m ruff format --check .`는 설치된 ruff 0.16.4로 PASS(선언 0.17.1과 구분).
- Windows 전체 검사는 POSIX 실행·symlink 권한 오류가 발생해 중단했으며 PASS가 아닙니다. Windows의 `python -X utf8 scripts/check_repository.py`도 기존 CRLF header 판정으로 실패했습니다. 수정 작업 파일을 LF로 복사한 WSL Ubuntu 임시 snapshot에서 Python 3.14.4/PyYAML 6.0.3/packaging 26.0으로 `python3 -m unittest discover -s tests -v` 219개와 `python3 scripts/check_repository.py`(37문서·7workflow) PASS. 표시 이름을 Downloads로 줄인 최종 변경 후 같은 환경에서 영향 있는 24개와 저장소 검사를 다시 통과했습니다.
- 수정한 렌더러가 생성한 배지 URL을 실제 GET하여 Places 66k·Saver 28k 및 HTTP 200을 확인했습니다. 최초 User-Agent 없는 요청의 HTTP 403은 실패로 남기고 명시한 User-Agent로 재검증했습니다. 외부 응답 수치는 캐시에 따라 달라지며 오프라인 단위 테스트 성공으로 원격 동작을 대신 판정하지 않습니다.
- PR 독립 리뷰 1차(`e5dd492afd7d0605245d110f80c5b34092a60efd`): P2 고유 Downloads/GitHub Downloads 배지의 이름 충돌 삭제를 재현했습니다. 새 Downloads 배지는 중앙 생성 URL·스타일·색상·label과 releases 클릭 대상이 모두 일치할 때만 교체하고, 같은 이름의 최신 다운로드·다른 스타일·다른 클릭 대상 배지는 보존하도록 수정했습니다. 회귀 추가 후 Windows `python -X utf8 -m unittest discover -s tests -p test_tools.py` 25개 PASS. 초기 회귀 작성 시 wrapper에 없는 helper를 호출해 실패한 테스트는 고정 입력으로 정정했습니다.

## 통합 제품 카테고리 재확인

다음 범위는 **2026-10-20** 확인했습니다. 적용 가능한 통합의 분류/근거 기록 필수는 중앙 HA-02 정책이며 upstream의 선택 항목·HACS 경고와 구분합니다.

| 공식 자료 | 확인 범위 |
|---|---|
| [HA manifest categories](https://contributors.home-assistant.io/core/integrations/manifest/#categories) | 현재 선택 필드, 1–3개·중복 금지·알려진 분류·부모/자기 하위 분류 금지, entity/system/virtual 키 생략 |
| [HA 제품 분류 안내](https://contributors.home-assistant.io/core/integrations/categories/) | 실제 지원 제품·서비스 용도로 주 분류 먼저 선택하며 entity 플랫폼이나 iot_class와 구분 |
| [Core taxonomy 원본](https://github.com/home-assistant/core/blob/ec18d8b25d1ee39aa8b85a72a170e42bee33228c/homeassistant/generated/integration_categories.json) | 오프라인 snapshot의 category·category.subcategory slug 추출 원본·full SHA |
| [HACS integration_categories 검사](https://github.com/hacs/integration/blob/a15e87ec0d1c82e58f1ddbaf17669d3eaa261eb8/custom_components/hacs/validate/integration_categories.py) | 누락은 경고 후 반환, 존재하는 값은 schema 검증 |
| [HACS categories schema](https://github.com/hacs/integration/blob/a15e87ec0d1c82e58f1ddbaf17669d3eaa261eb8/custom_components/hacs/utils/validate.py) | 문자열 목록·1–3개·기지 분류·중복 검사 |

중앙 snapshot은 검토 당시 원본이며 실시간 upstream 전체를 대신하지 않습니다. 새 분류는 실제 Core/HACS 원본·SHA·확인일과 테스트를 함께 재검토합니다. 실제 지원 최소 HA 로딩·원격 HACS action·제품 분류 의미는 별도 검증이며 이 변경으로 수행했다고 주장하지 않습니다.
