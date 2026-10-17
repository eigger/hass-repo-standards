# hass* 전체 CI 조사

확인일: **2026-10-17**. GitHub `eigger`의 hass로 시작하는 저장소 목록과 각 기본 브랜치 workflow를 읽었고, 로컬 checkout도 따로 비교했습니다. 새 standards 리포 자체는 집계에서 제외했습니다. 검사 실행 결과나 각 리포의 green 상태를 조사한 것은 아닙니다.

## 범위와 증거

- GitHub: **29개 리포, 55개 workflow, 97개 job**. 통합 25개 + 카드/Android/YAML/앱 4개입니다.
- 로컬: **31개 checkout**, 커스텀 통합 디렉터리 27개. `hass-coolled`는 `hass-ble-led-sign` 원격의 중복 checkout입니다.
- `hass-timemore`는 로컬에만 있으며 이번 인증 계정의 GitHub 목록에는 없습니다. 원격 존재/접근 여부를 별도로 확인하기 전 이관하지 않습니다.
- `hass-gicisky`는 GitHub에서 **archived**입니다. 신규 CI 이관 대상에서 제외합니다.
- 로컬/원격 workflow 내용 차이는 `hass-kma/tests.yml`의 lint 대상(scripts 포함 여부)에서 확인했습니다. 현황표의 기준은 GitHub 기본 브랜치입니다.
- [원격 원문 기반 구조화 스냅샷](ci-remote-inventory.json): blob SHA, 이벤트, 권한, 모든 job·step.
- [로컬 스냅샷](ci-inventory.json): 원격, HEAD, dirty 상태, 모든 workflow·step. 기본 브랜치는 origin/HEAD 캐시일 수 있습니다.

## 반복되는 역할과 차이

| 역할 | 현재 차이 | 통합 방식 |
|---|---|---|
| HACS/Hassfest | 18개 리포에 같은 구조 복제, checkout v5/v7, icscale만 brands 제외 | validate-integration.yml, ignore는 입력+기록 |
| Ruff | 17개 job이 `pip install ruff`로 버전 미고정. 대상 custom_components/tests/scripts/tools/docs와 format 여부가 다름 | 버전 관리 requirements + ruff check/format, 제외는 pyproject |
| Python 테스트 | 3.12~3.14 matrix, requirements_test/requirements-test/inline 설치가 혼재 | python-tests.yml의 경로·matrix 입력 |
| HA 테스트 환경 | 실제 HA fixture, stub-only, homeassistant>= 설치, 별도 최소 HA 검사가 섞임 | unit/ha profile, exact HA assertion, 별도 최소 HA job |
| manifest 설치 | shell command substitution, 파일 추출, 설치 생략이 섞임 | 공통 환경 action에서 JSON 파싱과 단일 resolver |
| HA component requirements | niimbot/omron/icscale/esphome-ota/ble-esl에 유사 helper | 설치된 HA manifest에서 재귀 수집하는 공통 action |
| 최소 package | catprinter는 current/minimum matrix, marklife/ble-led-sign은 imagespec만 강제 재설치 | minimum-packages와 dependency-modes 입력으로 동일 구현 |
| dependency update | imagespec 전용, blesession 전용, 복수 package inline bot. 브랜치/버전 비교/PR 처리 차이 | updater action + 하나의 PR workflow |
| PR 후속 CI | 직접 dispatch, warning만 출력, 후속 검사 없음 혼재 | 변경 tree 검증 후 PR; required checks 운영은 명시적으로 분리 |
| 전용 검사 | ble-esl editor, imagespec-card JS, Android Gradle, YAML schema, apps pins/linter | 전용 job 유지, 공통 환경만 재사용 |

55개 workflow 중 **26개는 workflow 수준 permissions 미지정**이며 이는 실제 token이 쓰기 권한이라는 뜻은 아닙니다. 실제 권한은 리포 설정에도 좌우됩니다. **97개 job 모두 job 수준 timeout-minutes가 없습니다.** ble-esl에는 step timeout이 있으나 job timeout과 구분됩니다.

### 의존성 bot에서 확인한 구현 차이

- ble-esl/catprinter/marklife/niimbot/icscale 계열은 `==`를 `>=`로 자동 전환하는 경로가 있습니다. 공통 bot에서는 연산자를 보존합니다.
- gicisky는 `==` 패턴만 찾고 단순 문자열 교체를 합니다. archive이므로 신규 bot을 적용하지 않습니다.
- ble-led-sign/gicisky는 버전별 PR branch, 다른 bot은 단일 branch를 사용합니다. 공통 branch는 `bot/manifest-dependencies`입니다.
- 여러 bot에 main/master base가 하드코딩되어 있습니다. 공통 bot은 GitHub default_branch를 읽습니다.
- PEP 440 parser와 숫자 tuple, info.version 단순 비교가 섞입니다. 공통 bot은 stable/non-yanked/Requires-Python 필터와 major 검토를 사용합니다.
- bot의 변경 검증을 릴리스 승인이나 전체 device 검증으로 표현하지 않습니다.

## 리포별 이관 지도

| 리포 | 종류 | 실제 기본 브랜치 | 현재 workflow | 공통화/유지 항목 |
|---|---|---|---|---|
| [hass-atflee](https://github.com/eigger/hass-atflee) | integration | master | tests.yml, update_blesession.yml, validate.yml | 공통 Validate + Python Tests; 공통 updater |
| [hass-ble-esl](https://github.com/eigger/hass-ble-esl) | integration | main | tests.yml, update_dependencies.yml, validate.yml | 공통 Validate + Python Tests; editor job + 공통 환경 action; 공통 updater |
| [hass-ble-led-sign](https://github.com/eigger/hass-ble-led-sign) | integration | master | tests.yml, update_dependencies.yml | 공통 Validate + Python Tests; 공통 updater |
| [hass-catprinter](https://github.com/eigger/hass-catprinter) | integration | main | tests.yml, update_dependencies.yml, validate.yml | 공통 Validate + Python Tests; current/minimum matrix 유지; 공통 updater |
| [hass-cyx-rgb-led](https://github.com/eigger/hass-cyx-rgb-led) | integration | master | 없음 | 현재 CI 없음: 검증부터 단계적 채택 |
| [hass-divoom](https://github.com/eigger/hass-divoom) | integration | master | 없음 | 현재 CI 없음: 검증부터 단계적 채택 |
| [hass-esphome-ota](https://github.com/eigger/hass-esphome-ota) | integration | main | tests.yml, validate.yml | 공통 Validate + Python Tests |
| [hass-garage](https://github.com/eigger/hass-garage) | integration | master | tests.yml | 공통 Validate + Python Tests |
| [hass-gicisky](https://github.com/eigger/hass-gicisky) | integration | master | tests.yml, update_dependencies.yml, validate.yml | archive: 이관 제외, 이전 안내 보존 |
| [hass-icscale](https://github.com/eigger/hass-icscale) | integration | main | tests.yml, update_dependencies.yml, validate.yml | 공통 Validate + Python Tests; 공통 updater |
| [hass-imagespec-card](https://github.com/eigger/hass-imagespec-card) | frontend | main | ci.yml, release.yml | 카드 lint/test/build/release 유지; 공통 CI 원칙 적용 |
| [hass-jaalee](https://github.com/eigger/hass-jaalee) | integration | master | validate.yml | 공통 Validate 먼저; 실제 테스트 추가 후 Tests 채택 |
| [hass-kibble](https://github.com/eigger/hass-kibble) | integration | master | tests.yml | 공통 Validate + Python Tests |
| [hass-kma](https://github.com/eigger/hass-kma) | integration | main | tests.yml, validate.yml | 공통 Validate + Python Tests |
| [hass-kocom-smarthome](https://github.com/eigger/hass-kocom-smarthome) | integration | main | tests.yml | 공통 Validate + Python Tests; test-min-ha 유지 |
| [hass-lywsd02](https://github.com/eigger/hass-lywsd02) | integration | main | tests.yml, validate.yml | 공통 Validate + Python Tests |
| [hass-magic-caster-wand](https://github.com/eigger/hass-magic-caster-wand) | integration | master | tests.yml, validate.yml | 공통 Validate + Python Tests |
| [hass-marklife](https://github.com/eigger/hass-marklife) | integration | main | tests.yml, update_dependencies.yml, validate.yml | 공통 Validate + Python Tests; 공통 updater |
| [hass-melk-light](https://github.com/eigger/hass-melk-light) | integration | master | 없음 | 현재 CI 없음: 검증부터 단계적 채택 |
| [hass-minibig](https://github.com/eigger/hass-minibig) | integration | main | tests.yml, validate.yml | 공통 Validate + Python Tests |
| [hass-niimbot](https://github.com/eigger/hass-niimbot) | integration | master | tests.yml, update_dependencies.yml, validate.yml | 공통 Validate + Python Tests; 공통 updater |
| [hass-omron](https://github.com/eigger/hass-omron) | integration | master | tests.yml, update_blesession.yml, validate.yml | 공통 Validate + Python Tests; 공통 updater |
| [hass-opinet](https://github.com/eigger/hass-opinet) | integration | main | tests.yml, validate.yml | 공통 Validate + Python Tests |
| [hass-sip](https://github.com/eigger/hass-sip) | integration | main | tests.yml, validate.yml | 공통 Validate + Python Tests |
| [hass-vson](https://github.com/eigger/hass-vson) | integration | master | tests.yml, validate.yml | 공통 Validate + Python Tests |
| [hass-ws-bridge](https://github.com/eigger/hass-ws-bridge) | integration | main | tests.yml, validate.yml | 공통 Validate + Python Tests |
| [hassble-android](https://github.com/eigger/hassble-android) | android | main | pr-checks.yml, release.yml | Gradle·서명·APK/AAB 유지; 공통 CI 원칙 적용 |
| [hassble-config](https://github.com/eigger/hassble-config) | yaml-config | main | validate.yml | schema 검사 유지; 런타임/권한/timeout 통일 |
| [hassio-apps](https://github.com/eigger/hassio-apps) | apps | master | upstream-bump.yml, validate.yml | pins/add-on linter 유지; 이미지 updater 분리 |

## 권장 순서

1. 단순한 integration 1개에서 Validate/Tests caller를 검증합니다.
2. catprinter 또는 marklife에서 imagespec+blesession current/minimum과 updater dry-run을 확인합니다.
3. niimbot/icscale/omron의 실제 HA 환경과 component 의존성을 이관합니다.
4. ble-esl의 editor 전용 job을 유지하면서 Python 환경 action을 공유합니다.
5. archived/이전/접근 미확인 리포를 제외하고 나머지를 단계적으로 전환합니다.

이번 작업은 **규칙 리포와 공통 구현을 생성**합니다. 위 기존 리포의 workflow, required checks, 봇 PR, 릴리스는 변경하지 않습니다.

## 재조사

```bash
python3 -m pip install -r requirements_dev.txt
python3 scripts/audit_repositories.py --root .. --output /tmp/hass-local.json
python3 scripts/audit_repositories.py --github-owner eigger --output /tmp/hass-remote.json
```

원격 조사는 읽기 전용 gh 인증을 사용하며 최대 1,000개 저장소 목록에서 hass 접두사를 필터링합니다. 이 계정의 이번 목록은 한도 미만입니다.
