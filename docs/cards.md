# 대시보드 카드 규칙

Lovelace/대시보드 카드처럼 HACS `plugin`(프런트엔드 리소스 번들)으로 배포하는 리포의 규칙입니다. 공식 근거는 [HACS plugin 게시 안내](https://www.hacs.xyz/docs/publish/plugin/)와 [HACS 요구사항](https://www.hacs.xyz/docs/publish/start/)이며([sources](sources.md#대시보드-카드-재확인) 참고), 아래 필수 표기는 프로젝트 정책입니다.

참조 구조는 [hass-compact-cards](https://github.com/eigger/hass-compact-cards)(빌드 없는 단일 JS), [hass-overview-cards](https://github.com/eigger/hass-overview-cards)(동일 구조), [hass-imagespec-card](https://github.com/eigger/hass-imagespec-card)(TypeScript·Lit·Vite 빌드)입니다. 이는 번들 배치·빌드 방식의 참조일 뿐 CARD 규칙을 모두 충족한 준수 사례가 아닙니다. compact·overview는 2026-11-08 소유자 결정에 따라 MIT LICENSE를 추가했습니다. 기준 조사 당시 imagespec-card는 루트 LICENSE·README.ko.md·CHANGELOG·STANDARDS.md·`engines.node`가 없었으며 CI가 tag pin·단일 release job을 사용했습니다. compact·overview의 번들 이름은 저장소 이름과 달라 `hacs.json`의 `filename`에 의존합니다(HACS 문서가 plugin의 `filename`을 지원). 규칙과 다른 구조는 근거를 STANDARDS.md에 기록하고 예외로 관리합니다.

## 적용 범위

**CARD-01 필수**: 이 문서는 `custom_components/<domain>`이 없는 카드 리포에만 적용합니다. 카드 리포에는 manifest, Hassfest, HA pytest fixture, Ruff, 제품 categories, imagespec/blesession 계약, 통합 ZIP 릴리스, `check_integration.py`, 통합 템플릿(`.hass-standards.json`, README 관리 영역)을 강제하거나 인위적인 manifest·domain으로 우회하지 않습니다. 통합 프로필과 공통인 [GOV-01](adoption.md#중앙-템플릿과-예외) 예외 기록·[GOV-04](adoption.md#채택) 현황 갱신 원칙은 그대로 적용합니다.

중앙 통합 프로필의 workflow 이름·입력·템플릿 경로는 카드 지원 때문에 변경하지 않습니다. 카드 전용 자산은 별도 파일로 추가하며 통합 소비자의 규칙·workflow 내용 변경을 요구하지 않습니다. 중앙 릴리스에 따른 중앙 참조 갱신 PR은 일반 [REL-06](releases.md#중앙-표준-릴리스-rel-06) 절차이며 아래 CARD-08에서 영향을 다룹니다.

## 배포

**CARD-02 필수**: 루트에 `hacs.json`, README, LICENSE를 둡니다. `name`은 UI 표시 이름이고, 번들 이름이 저장소 이름(`lovelace-` 접두사 예외)과 다르면 `filename`을 명시해 실제 번들 파일과 릴리스 asset 이름에 일치시킵니다. HACS는 `dist/` → 최신 릴리스 → 루트 순으로 번들을 찾고 릴리스 asset이 필수가 아니므로, 아래 릴리스 asset 첨부는 HACS 필수 조건이 아니라 재현성을 위한 프로젝트 정책입니다. `content_in_root`·`dist` 사용 여부는 실제 구조에 맞추고 기존 설치 경로를 바꾸는 이름 변경은 breaking change로 취급합니다. 지원 최소 HA(`homeassistant`)는 실제 확인 전에는 임의로 넣지 않고 예외로 기록하며, 정한 경우 비호환 근거를 남깁니다. `render_readme` 같은 과거 필드는 사용하는 HACS에서 현재 동작을 확인하기 전에는 새로 추가하지 않고, 기존 필드는 일괄 삭제하지 않습니다([HACS-06](hacs.md)).

**CARD-03 필수**: 릴리스는 SemVer이며 `package.json`의 `version`과 `v` 접두사를 제외한 태그를 일치시킵니다. 안정 태그만 정식 릴리스로 게시하고 prerelease는 GitHub에서도 prerelease로 표시합니다. 번들(`filename`)을 GitHub Release asset으로 첨부하고, 검증(읽기 권한)과 게시(쓰기 권한) job을 분리해 같은 커밋에서 실행합니다. 태그가 가리키는 커밋의 번들과 asset이 같아야 하며 한 번 게시한 태그를 이동·재사용하지 않습니다. 변경 기록(CHANGELOG)을 유지하고 사용자에게 필요한 조치(리소스 URL·카드 type 변경 등)를 적습니다. 실제 HA 화면 검증 없이 호환성을 주장하지 않습니다.

## 빌드와 CI

**CARD-04 필수**: `npm ci`와 커밋된 lockfile로 재현 가능한 설치를 합니다. CI는 `engines.node` 범위의 최소 major 버전으로 실행하고, 최소한 문법 검사(`check` 또는 `lint`)와 `test`를 CI에서 실행합니다. 빌드 단계가 있는 카드는 `build` 후 `filename`에 해당하는 산출물의 존재를 확인합니다. DOM 단위 테스트는 브라우저 레이아웃·실제 HA 호환·기기를 검증하지 않으므로 해당 범위는 미검증으로 기록합니다.

CI는 [CI-01](ci.md)처럼 읽기 전용 권한, 외부 action의 전체 SHA pin과 버전 주석, `persist-credentials: false`, `timeout-minutes`, `concurrency`를 사용하고 셸 입력은 환경 변수로 전달합니다. 리포 전용 workflow 이름은 [CI-02](ci.md)의 리포 전용 CI 문단(소문자·밑줄 파일명, 명확한 영어 표시 이름)만 따르며 통합 공용 caller 파일명(Validate·Standards·Tests)은 요구하지 않습니다. 기존 required check 이름은 보존합니다. 카드 전용 job은 독립 유지하며 HACS 검증이 필요하면 `category: plugin`으로 실행합니다.

**CARD-05 필수**: 런타임 의존성은 최소화하고 테스트·빌드 도구는 `devDependencies`로 분리합니다. Dependabot은 `npm`과 `github-actions`를 주 1회 검사합니다. patch/minor는 필수 CI 성공 후 자동 머지할 수 있으며 major와 버전 올림은 수동입니다. 중앙의 `dependabot-auto-merge.yml`을 재사용할 때는 exact 릴리스 tag 또는 그 릴리스의 full SHA(버전 주석 포함)로만 참조하고 branch·moving tag는 금지합니다([REL-06](releases.md#중앙-표준-릴리스-rel-06)). Dependabot이 SHA를 올리면 버전 주석과 STANDARDS.md 기록도 함께 갱신합니다.

## 문서

**CARD-06 필수**: README는 영어(`README.md`)와 한국어(`README.ko.md`)를 상호 링크하고 같은 구조로 유지하며 기존 본문을 보존합니다([DOC-02](documentation.md)). 카드는 통합 README 관리 영역·설치 배지 규칙(DOC-01/03/05)을 요구하지 않습니다. 필수 내용은 HACS 설치 방법, 리소스 등록(URL·type `module`), 지원 카드 type과 YAML 예제, 시각 편집기 지원 여부, 스크린샷, 알려진 제한과 검증 범위입니다. 지원하지 않는 HA 버전·브라우저를 단정하지 않습니다.

## 채택 기록

**CARD-07 필수**: 카드 리포는 `STANDARDS.md`에 새 채택은 검토한 중앙 exact 릴리스(및 resolved full SHA)를, 비릴리스 full SHA는 기존 참조 호환으로만 유지하며 적용·제외 규칙과 사유를 기록하고 `ADOPTION_CHECKLIST.md`에 대상 커밋·명령·실제 Node/npm 버전·결과·CI를 남깁니다. 미실행·원격 CI 미확인·실제 HA 미검증은 TODO로 유지합니다. 중앙 [적용 현황](adoption-status.md)은 GOV-04 항목 전체(담당자/세션, 적용 내용, 기준 SHA·대상 커밋·체크리스트·CI·리뷰 근거, 남은 작업, 갱신일)를 카드 리포에도 동일하게 기록하되 통합 적용 실적에는 포함하지 않으며, 상태는 현황표에 정의된 값만 씁니다. 중앙 재사용 workflow가 추가되기 전에는 로컬 workflow를 유지하고, 전환은 별도 PR로 수행합니다.

## 중앙 재사용 workflow

**CARD-08 권장**: 카드 리포는 로컬 복사본 대신 중앙 [card-check.yml](../.github/workflows/card-check.yml)과 [card-release.yml](../.github/workflows/card-release.yml)을 호출할 수 있습니다. caller 예시는 [templates/card](../templates/card/.github/workflows)이며 새 카드 caller의 `uses`에는 REL-06의 검증된 immutable 릴리스 exact 태그(예를 들어 `@v1.2.0`)를 쓰고, `STANDARDS.md`에 해당 태그와 resolved full SHA를 함께 기록합니다. 이전에 검증한 full SHA와 버전 주석을 함께 쓰는 기존 caller는 호환됩니다. 브랜치·moving tag는 사용하지 않습니다.

- 입력: `bundle-path`(필수), `node-version`(기본 22), `check-script`·`test-script`(기본 `check`·`test`), `lint-script`·`build-script`(선택, 기본 빈 값은 생략). 셸 단계에는 입력이 환경 변수로만 전달되고, npm script 이름·번들 경로(숨김 경로·`..`·디렉터리 제외)·Node major는 사용 전에 형식 검사를 통과해야 합니다. CARD-04에 따라 `check-script` 또는 `lint-script` 중 하나와 `test-script`는 비울 수 없고 `build-script`만 선택입니다.
- card-release는 안정 SemVer 태그 push에서만 동작하며, CARD-03의 prerelease 게시는 이 workflow의 범위 밖이라 수동 절차로 처리합니다. `validate`(읽기)가 `package.json` 버전과 태그를 대조하고 번들을 artifact로 넘기면 `release`(쓰기)가 같은 파일을 asset으로 첨부합니다. 기존 릴리스를 덮어쓰거나 `--clobber`를 쓰지 않습니다.
- 호출하는 caller의 job에 `contents: write`를 줘야 release가 동작합니다. 재사용 workflow로 전환하면 required status check 이름이 `<caller job> / <called job>` 형태로 바뀌므로 branch protection의 필수 check를 같은 PR에서 함께 갱신합니다.
- 전환은 카드 리포별 별도 PR로 수행하며 기존 `check.yml`·`release.yml`의 동작(필수 check, 태그 트리거)을 보존합니다. 중앙 릴리스가 발행되기 전에는 전환하지 않습니다.

중앙에 workflow를 추가·변경하면 배포 단위가 바뀌므로 [REL-06](releases.md#중앙-표준-릴리스-rel-06) 릴리스가 필요하고, 통합 소비자의 Dependabot이 중앙 참조 갱신 PR을 만듭니다. 문서·현황 변경은 릴리스를 강제하지 않으므로 카드 workflow 변경은 다른 중앙 변경과 묶어 릴리스합니다.

## 후속 범위

중앙 카드 검사기(`check_card.py`)와 카드 scaffold는 아직 없습니다. 도입 전에 카드 소비자 수와 반복 중복을 확인합니다.

### v1.2.0 발행 직후 관측

[immutable v1.2.0](https://github.com/eigger/hass-repo-standards/releases/tag/v1.2.0) 발행(2026-11-07 23:10:25 KST)부터 2026-11-07 23:22:47 KST까지 [등록된 통합 23개](../standards-consumers.json)의 GitHub Pulls API에서 모든 상태의 PR을 조회했습니다. 발행 후 새로 생성된 Dependabot PR과 기존 `central-standards` Dependabot PR의 발행 후 메타데이터 갱신이 각각 **0건**이었습니다. CI 실행 표본은 **0건**으로 소요 시간은 산출할 수 없었습니다. 23개 모두 GitHub Actions 업데이트를 `daily`로 설정했습니다. 이 설정의 [정기 검사일은 월요일부터 금요일까지](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#interval)이며, 이번 관측은 토요일 발행 직후에 끝났습니다. 발행 후 첫 갱신 주기의 PR 수와 해당 PR의 CI 소요는 후속 관측에 남겨 둡니다.
