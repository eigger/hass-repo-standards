# 대시보드 카드 규칙

Lovelace/대시보드 카드처럼 HACS `plugin`(프런트엔드 리소스 번들)으로 배포하는 리포의 규칙입니다. 공식 근거는 [HACS plugin 게시 안내](https://www.hacs.xyz/docs/publish/plugin/)와 [HACS 요구사항](https://www.hacs.xyz/docs/publish/start/)이며([sources](sources.md#대시보드-카드-재확인) 참고), 아래 필수 표기는 프로젝트 정책입니다.

기준 사례는 [hass-compact-cards](https://github.com/eigger/hass-compact-cards)(빌드 없는 단일 JS), [hass-overview-cards](https://github.com/eigger/hass-overview-cards)(동일 구조), [hass-imagespec-card](https://github.com/eigger/hass-imagespec-card)(TypeScript·Lit·Vite 빌드)입니다. 사례와 다른 구조를 가진 카드는 근거를 STANDARDS.md에 기록하고 예외로 관리합니다.

## 적용 범위

**CARD-01 필수**: 이 문서는 `custom_components/<domain>`이 없는 카드 리포에만 적용합니다. 카드 리포에는 manifest, Hassfest, HA pytest fixture, Ruff, 제품 categories, imagespec/blesession 계약, 통합 ZIP 릴리스, `check_integration.py`, 통합 템플릿(`.hass-standards.json`, README 관리 영역)을 강제하거나 인위적인 manifest·domain으로 우회하지 않습니다. [GOV-01](adoption.md#중앙-템플릿과-예외) 예외·[GOV-04](adoption.md#채택) 현황 기록 등 프로필 공통 원칙은 그대로 적용합니다.

중앙 통합 프로필의 workflow 이름·입력·템플릿 경로는 카드 지원 때문에 변경하지 않습니다. 카드 전용 자산은 별도 파일로 추가하고 기존 통합 소비자의 갱신을 요구하지 않습니다.

## 배포

**CARD-02 필수**: 루트에 `hacs.json`, README, LICENSE를 둡니다. `name`은 UI 표시 이름이고 `filename`은 실제 번들 파일과 릴리스 asset 이름에 일치시킵니다. `content_in_root`·`dist` 사용 여부는 실제 구조에 맞추고 기존 설치 경로를 바꾸는 이름 변경은 breaking change로 취급합니다. 지원 최소 HA(`homeassistant`)는 실제 확인 전에는 임의로 넣지 않고 예외로 기록하며, 정한 경우 비호환 근거를 남깁니다. `render_readme` 같은 과거 필드는 사용하는 HACS에서 현재 동작을 확인하기 전에는 새로 추가하지 않고, 기존 필드는 일괄 삭제하지 않습니다([HACS-06](hacs.md)).

**CARD-03 필수**: 릴리스는 SemVer이며 `package.json`의 `version`과 `v` 접두사를 제외한 태그를 일치시킵니다. 안정 태그만 정식 릴리스로 게시하고 prerelease는 GitHub에서도 prerelease로 표시합니다. 번들(`filename`)을 GitHub Release asset으로 첨부하고, 검증(읽기 권한)과 게시(쓰기 권한) job을 분리해 같은 커밋에서 실행합니다. 태그가 가리키는 커밋의 번들과 asset이 같아야 하며 한 번 게시한 태그를 이동·재사용하지 않습니다. 변경 기록(CHANGELOG)을 유지하고 사용자에게 필요한 조치(리소스 URL·카드 type 변경 등)를 적습니다. 실제 HA 화면 검증 없이 호환성을 주장하지 않습니다.

## 빌드와 CI

**CARD-04 필수**: `npm ci`와 커밋된 lockfile로 재현 가능한 설치를 합니다. `engines.node`와 CI의 Node 버전이 일치해야 하고, 최소한 문법 검사(`check` 또는 `lint`)와 `test`를 CI에서 실행합니다. 빌드 단계가 있는 카드는 `build` 후 `filename`에 해당하는 산출물의 존재를 확인합니다. DOM 단위 테스트는 브라우저 레이아웃·실제 HA 호환·기기를 검증하지 않으므로 해당 범위는 미검증으로 기록합니다.

CI는 [CI-01](ci.md)처럼 읽기 전용 권한, 외부 action의 전체 SHA pin과 버전 주석, `persist-credentials: false`, `timeout-minutes`, `concurrency`를 사용하고 셸 입력은 환경 변수로 전달합니다. workflow 파일명과 job 이름은 [CI-02](ci.md) 규칙을 따릅니다. 카드 전용 job은 독립 유지하며 HACS 검증이 필요하면 `category: plugin`으로 실행합니다.

**CARD-05 필수**: 런타임 의존성은 최소화하고 테스트·빌드 도구는 `devDependencies`로 분리합니다. Dependabot은 `npm`과 `github-actions`를 주 1회 검사합니다. patch/minor는 필수 CI 성공 후 자동 머지할 수 있으며 major와 버전 올림은 수동입니다. 중앙의 `dependabot-auto-merge.yml`을 재사용할 때는 exact immutable 릴리스([REL-06](releases.md#중앙-표준-릴리스-rel-06))로만 참조합니다.

## 문서

**CARD-06 필수**: README는 영어(`README.md`)와 한국어(`README.ko.md`)를 상호 링크하고 같은 구조로 유지하며 기존 본문을 보존합니다([DOC-02](documentation.md)). 카드는 통합 README 관리 영역·설치 배지 규칙(DOC-01/03/05)을 요구하지 않습니다. 필수 내용은 HACS 설치 방법, 리소스 등록(URL·type `module`), 지원 카드 type과 YAML 예제, 시각 편집기 지원 여부, 스크린샷, 알려진 제한과 검증 범위입니다. 지원하지 않는 HA 버전·브라우저를 단정하지 않습니다.

## 채택 기록

**CARD-07 필수**: 카드 리포는 `STANDARDS.md`에 검토한 중앙 exact 릴리스 또는 full SHA, 적용·제외 규칙과 사유를 기록하고 `ADOPTION_CHECKLIST.md`에 대상 커밋·명령·실제 Node/npm 버전·결과·CI를 남깁니다. 미실행·원격 CI 미확인·실제 HA 미검증은 TODO로 유지합니다. 중앙 [적용 현황](adoption-status.md)에는 카드 리포의 범위와 상태만 기록하며 통합 적용 실적에 포함하지 않습니다. 중앙 재사용 workflow가 추가되기 전에는 로컬 workflow를 유지하고, 전환은 별도 PR로 수행합니다.

## 후속 범위

중앙 카드 검사기(`check_card.py`), 카드 템플릿, 재사용 Node workflow는 아직 없습니다. 도입 전에 카드 소비자 수·반복 중복·릴리스 갱신 부담을 확인하며, 통합 소비자에게 불필요한 갱신을 만들지 않는 릴리스 방식을 먼저 검증합니다.
