# CI 작성 규칙

이 문서의 필수 항목은 프로젝트 정책입니다. [GitHub 보안 지침](https://docs.github.com/en/actions/reference/security/secure-use)과 [재사용 workflow](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)를 참고합니다.

## 역할과 분리

**CI-01 필수**: 검증은 읽기 전용, 업데이트 PR과 릴리스는 쓰기 작업으로 분리합니다. 통합은 Validate·Standards·Tests를 사용하고, frontend/browser/Android/add-on 작업은 독립 job으로 유지합니다. 같은 역할의 코드를 다시 복사하지 않고 중앙 reusable workflow 또는 composite action을 사용합니다.

| 역할 | 중앙 구현 | 리포별 입력/확장 |
|---|---|---|
| HACS·Hassfest | validate-integration.yml | HACS ignore와 사유, 필요한 경우 검토한 hassfest-core-ref |
| Ruff·format·pytest | python-tests.yml | Python matrix, requirements, profile, test args |
| manifest·HA 의존성 설치 | actions/python-environment | domain, 최소 패키지, HA 구성요소 |
| imagespec·blesession 업데이트 | dependency-update.yml | 패키지 목록, schedule, 검증 명령 |
| UI/browser | 로컬 job + python-environment | Node/Playwright, demo 서버 |
| 카드·Android·앱 | 로컬 workflow | 빌드 산출물·서명·이미지 검증 |

## 실행과 결과

**CI-02 필수**: 공용 caller의 파일명·표시 이름·실행 조건은 중앙 템플릿을 의무 적용합니다. 기본 브랜치 이름은 실제 원격 메타데이터에서 읽습니다. 아래 조건은 기존 동작을 유지하며 PR 대상 브랜치를 제한하거나 문서 변경을 paths 필터로 제외하지 않습니다. 태그 push를 별도 실행 조건으로 추가하지 않습니다. cron은 UTC이며 중앙 템플릿의 예약식을 유지합니다.

| 파일명 | 표시 이름 | 실행 조건 |
|---|---|---|
| `validate.yml` | `Validate` | 모든 대상 브랜치 PR의 생성·갱신·재오픈, 실제 기본 브랜치 push, 수동, 매주 예약 |
| `standards.yml` | `Standards` | Validate와 같은 조건 |
| `tests.yml` | `Tests` | 모든 대상 브랜치 PR의 생성·갱신·재오픈, 실제 기본 브랜치 push, 수동 |
| `update_dependencies.yml` | `Update dependencies` | 예약·수동, 업데이트할 외부 의존성이 있는 경우만 적용 |

리포 전용 CI의 작업·실행 조건은 리포에 맡깁니다. 파일명은 소문자 단어를 밑줄로 연결한 `.yml`, 표시 이름은 역할이 명확한 영어로 작성합니다(예: `build_frontend.yml` / `Build frontend`). 공용 CI를 같은 이름의 로컬 구현으로 대체하지 않습니다. 기존 required checks·특수 목적 job을 보존하고 이름 변경 영향은 확인합니다. 불가피한 차이는 [중앙 템플릿 수정 또는 사용자 승인](adoption.md#중앙-템플릿과-예외) 후 적용합니다.

**CI-03 필수**: 검증 workflow는 `permissions: contents: read`, checkout은 `persist-credentials: false`, 각 job에 timeout을 둡니다. 취소 가능한 검증에는 workflow+ref concurrency를 둡니다. dependency updater에는 취소하지 않는 별도 그룹을 둡니다. write 권한은 PR 생성/릴리스 job에만 줍니다.

**CI-04 필수**: 정상 lint/test를 `continue-on-error`, `|| true`, 항상 성공하는 wrapper로 숨기지 않습니다. lint와 test는 의존성이 없다면 병렬 실행합니다. optional matrix는 필수 검사를 대체하지 않습니다. required checks 변경은 채택 PR에 기록합니다. paths 필터로 필수 체크가 영구 Pending이 되는 구성을 피합니다.

**CI-05 필수**: 외부 action은 검토한 full SHA로 참조하고 외부 action 버전 또는 검토한 커밋 설명을 주석으로 붙입니다. 중앙 workflow/action은 기존 full SHA 또는 기록된 immutable exact release tag만 사용합니다. release tag caller는 `.hass-standards.json`의 단일 descriptor와 STANDARDS의 release/resolved SHA가 일치해야 하며 `standards-ref`·별도 중앙 도구 checkout은 resolved full SHA를 사용합니다. 매 실행 release/`latest`를 조회하거나 branch·moving major/minor tag로 fallback하지 않습니다. Dependabot으로 갱신합니다. SHA 고정이 action 내부 Docker 이미지까지 고정하는 것은 아닙니다. HACS/Hassfest는 upstream 이미지가 바뀔 수 있는 validator이며 schedule로 변화를 탐지합니다. 완전한 재현 환경은 별도 image digest 정책이 필요합니다.

## 환경과 명령

**CI-06 필수**: lint와 test 의존성은 버전 관리된 requirements/lock 파일에서 설치합니다. 통합 런타임 요구사항은 manifest에서 읽고 한 번의 pip resolver 호출로 테스트 요구사항과 함께 설치합니다. 여러 `pip install`로 충돌을 가리는 것을 피하고 `pip check`를 실행합니다. 생성 파일은 RUNNER_TEMP에 둡니다.

**CI-07 필수**: Python과 HA/pytest 플러그인은 실제 호환 조합을 입력합니다. 통합의 필수 검사는 `ha`로 실행하고 pytest 대상은 `tests/components/<domain>/`로 맞춥니다. 실제 HA fixture·통합 로딩을 사용하며 `unit`은 독립 도구 등의 보조 검사로만 둡니다. 최소/현재 라이브러리와 최소 HA 환경을 구분합니다. cache key에는 requirements와 manifest를 포함합니다. format은 `ruff format --check .`, lint는 `ruff check .`를 기본으로 하되 외부 복사 코드 제외는 pyproject에 명시합니다.

**CI-08 필수**: PR title/body/branch 같은 표현식은 shell에 직접 삽입하지 않고 env로 전달합니다. `pull_request_target`에서 외부 PR 코드를 checkout해 실행하지 않습니다. 일반 테스트에 secrets를 요구하지 않습니다. 재사용 workflow에 `secrets: inherit`를 기본으로 쓰지 않습니다.

## 업데이트·배포

중앙 표준 release 자체의 갱신은 [CI-13·중앙 표준 자동 업데이트](standards-updates.md)를 따릅니다. 명시적으로 채택한 release consumer는 `standards-ref`를 생략하고 descriptor의 검토 full SHA를 사용합니다. 이 opt-in은 같은 PR의 workflow pins·JSON·문서 기록을 함께 검증하며 기존 caller의 명시적 SHA 계약은 유지합니다. 아래 CI-09의 manifest updater와 구분하여 사용자 승인 범위인 patch·minor 표준 PR에만 필수 CI 통과 후 자동 squash를 예약합니다.

**CI-09 필수**: 의존성 변경은 PR로만 제안합니다. branch는 저장소 기본 브랜치를 API로 읽고 하나의 bot branch를 재사용합니다. 연산자/extras/marker를 유지하며 자동 merge·tag·release는 하지 않습니다. 검증 명령 실패 시 PR을 생성/갱신하지 않습니다.

**CI-10 필수**: GITHUB_TOKEN으로 만든 PR의 push/PR 이벤트가 다른 workflow를 자동 실행한다고 가정하지 않습니다. 공통 updater는 변경한 tree에서 선택 package의 정확한 새 하한과 지정한 검증을 먼저 실행하며, 추가 required checks는 수동 dispatch 또는 GitHub App 토큰 등 별도 운영 방식으로 충족합니다. dispatch 실패를 경고만 하고 모든 검증이 끝났다고 표시하지 않습니다. 본 구현은 PAT/App 비밀키를 요구하지 않습니다.

**CI-11 필수**: release는 검증한 같은 commit/tag에서 수행하고 별도 job만 contents:write를 받습니다. 산출물·manifest·tag 일치를 확인합니다. 이 공통 규칙 리포는 통합의 기존 릴리스에 ZIP asset을 첨부하는 중앙 action·caller를 제공합니다. 태그·릴리스 발행과 버전 변경은 자동화하지 않으며 [릴리스 계약](releases.md#zip-릴리스-첨부)을 따릅니다.

**CI-12 필수**: 테스트 의존성 추가·업데이트 PR도 [실제 HA 테스트 기준](testing.md)과 [의존성 추가 절차](dependencies.md)를 따릅니다. HA 패키지 설치·환경 summary·stub 테스트의 성공만으로 통합 검증을 완료하지 않습니다. 필요한 HA 구성요소와 package 요구사항을 설치하고 실제 entry·플랫폼 테스트를 실행합니다.

현재 테스트의 Python·HA·플러그인을 최신화해도 지원 최소 메타데이터와 최소 검증 job은 유지합니다. 최신 환경의 실패는 호환성을 수정하여 재검증하고, 새 API 등 확인한 구버전 비호환 근거와 별도 명시적 사용자 승인 없이 최소 지원 상향으로 우회하지 않습니다.

공통 workflow/action은 과거 caller 호환을 위해 `unit` 기본값을 유지합니다. 실행용 템플릿은 `ha`를 명시하며, HA 최소/현재 버전이 다르면 각기 Python·requirements를 지정한 별도 caller job으로 실행하고, 최소 job에는 정확한 expected-ha-version을 명시합니다. 정확히 같으면 명시적 최소 기대값을 가진 하나의 필수 job을 사용합니다. `pytest-args`를 생략하면 `ha`는 `tests/components/<domain>/ -v`, `unit`은 `tests/ -v`를 실행합니다. 환경 action은 실제 HA와 테스트 플러그인 설치·버전을 확인하지만 실제 통합 로딩 테스트의 성공은 별도로 검증해야 합니다.

`ha` profile에서 `expected-ha-version`을 생략하거나 비우면 설치된 `pytest-homeassistant-custom-component` 배포 메타데이터의 활성 `homeassistant==...` 요구사항을 읽고 실제 HA 버전과 비교합니다. 활성 exact pin이 없거나 여러 개면 실패하며 버전 검사를 생략하지 않습니다. 현재 HA 전용 job과 editor의 환경 action은 이 기본 동작을 사용해 플러그인 업데이트를 함께 따라갈 수 있습니다. 최소 HA job 및 최소/current를 겸하는 단일 job은 기존의 명시적 exact 기대 버전을 유지합니다. `unit` profile의 빈 입력은 기존처럼 HA 버전 검사를 요구하지 않습니다. 이 동작은 새 중앙 구현을 채택해야 적용되며 기존 caller의 명시적 기대 버전을 자동으로 제거하지 않습니다.

## 입력과 경계

공통 workflow는 로컬 trusted requirements와 명령을 실행합니다. 입력은 사용자 리포가 관리하며 임의 외부 값으로 만들지 않습니다. `pytest-args`, `validation-command`는 의도적인 shell 명령 입력이므로 PR 본문이나 네트워크 응답에서 생성하지 않습니다. composite action은 스크립트를 자신의 `github.action_path`에서 읽고 caller의 파일을 검사합니다. 실제 호출 예시는 templates/integration/.github/workflows에 있습니다.

## 형식 검사

Standards caller는 중앙 `actions/check-standards`을 사용해 README 관리 영역·테스트 기본 구조·공용 workflow 형식을 검사합니다. 검사 action과 reusable workflow는 검토한 전체 SHA로 고정합니다. 기존 Validate 안의 standalone job을 별도 `standards.yml`로 옮기고 표시 이름만 `Standards`로 줄입니다. 검사 규칙·기준·job 실행 단계는 변경하지 않으며, 기존 inline 배치도 같은 기준으로 계속 검사합니다. 검사 실패를 성공으로 바꾸지 않습니다. 검사기는 기록된 승인 예외의 형식과 범위만 반영하며 승인 요청·승인 대기 기능을 수행하지 않습니다. 승인 근거의 진위와 리포별 의미 검증은 적용 에이전트와 독립 리뷰의 책임입니다.

별도 Standards workflow의 중앙 템플릿 검사는 DOC-07에 따라 blesession 사용 통합의 양언어 기기별 문제 해결 문서도 검사합니다. manifest requirement의 정규 패키지명(extras·연산자·marker 포함) 또는 실제 코드 import로 대상을 식별하고, 문서 존재·고정 H2 순서·증상 표·필수 언어별 링크·미완료 placeholder를 검사합니다. 실제 기기 조건·진단 정확성·번역·기존 Issues 상태를 자동으로 입증하지 않으며 독립 리뷰가 필요합니다. blesession 미사용 프록시 통합의 기존 문서 의무는 수동 검토합니다.

standalone standards job은 대상 소스·테스트 문법을 읽을 수 있는 Python으로 실행합니다. 중앙 caller 예제는 Python 3.14이며 로컬 검사기도 대상 통합의 문법과 같거나 더 최신인 Python을 사용합니다. 이는 검사 도구 환경이며 지원 최소 HA/Python·최소 테스트 환경의 변경 근거가 아닙니다. 중앙 도구 자체의 단위 테스트 Python 3.9 호환성과 대상 소스 파싱 조건은 별개입니다.

imagespec 사용 통합의 DOC-08 정적 문서 검사는 Validate에서, 실제 예제 실행 계약은 각 필수 `ha` Tests 환경과 의존성 업데이트 검증에서 수행합니다. caller의 `standards-ref`는 reusable workflow의 검토 full SHA와 같아야 합니다. 중앙 도구는 예약된 별도 `.hass-standards-tools` 경로로 같은 SHA를 checkout하며 해당 경로가 이미 있으면 caller 파일을 덮지 않고 실패합니다. 기존 caller checkout·설치 버전을 유지하고 `actions/check-payload`는 `github.action_path`의 중앙 plugin을 실행합니다. 기기 action을 dispatch하지 않으며 skip/xfail/deselect·설치만 성공·caller 자체 PASS 테스트로 계약 실행을 대체하지 않습니다. 자세한 fixture·메타데이터 계약은 [payload 작성 규칙](payload-documentation.md)을 따릅니다.

DOC-08 적용 대상이라도 개별 matrix에서 imagespec requirement marker가 비활성이면 해당 계약은 N/A·버전 검증 없음으로 명시합니다. 그 job은 중앙 도구 checkout/계약만 생략하고 일반 HA 회귀 검사는 정확한 관리 scaffold만 제외하고 계속합니다. 정적 current/정확한 하한 coverage는 선언한 Python matrix에서 marker 활성 근거가 있는 job만 인정하며 patch 조건의 python_full_version은 실제 patch가 명시된 호환 환경으로 입증해야 합니다. 다른 활성 환경의 계약 실행은 여전히 필수입니다. 활성 환경의 패키지 누락·필수 예제 미실행은 실패이며 marker를 바꾸거나 추가 설치해 숨기지 않습니다.

## Published Hassfest 이미지와 새 manifest 스키마

`validate-integration.yml`의 선택 입력 `hassfest-core-ref`는 빈 문자열이 기본이며 기존 공식 `home-assistant/actions/hassfest` 호출을 그대로 유지합니다. upstream 공식 이미지가 아직 지원하지 않는 manifest 스키마가 필요할 때만 실제 검토한 Core full40SHA를 전달합니다. branch/tag·부분 SHA·임의 저장소 URL은 허용하지 않습니다.

2026-10-20 확인한 공식 `ghcr.io/home-assistant/hassfest:latest`는 stable2026.10.2의 manifest schema로 `categories` 키를 거부했습니다. Core는 `c517d079e1cd3831dd8aa547dd953e336830e846`에서 custom manifest의 categories를 허용했지만 공식 builder는 dev 이미지를 게시하지 않습니다. 선택한 제품 분류를 삭제하거나 실패를 무시하는 대신 해당 변경을 포함한 검토 SHA의 **공식 Dockerfile/entrypoint/전체 validator**를 수정 없이 빌드·실행하는 경로를 제공합니다. 초기 검토 후보는 taxonomy snapshot과 같은 `ec18d8b25d1ee39aa8b85a72a170e42bee33228c`입니다. 이 문서의 후보 SHA만으로 실물·원격 검증 성공을 주장하지 않습니다.

입력을 env로 전달해 엄격히 검사하고 고정 `https://github.com/home-assistant/core.git`의 commit을 runner.temp의 비어 있는 예약 경로로 shallow fetch합니다. 실제 HEAD 일치를 확인하고, 그 source의 `script/hassfest/docker/Dockerfile`로 이미지를 빌드한 뒤 기존 caller checkout을 원래 `/github/workspace`에 mount해 전체 Hassfest를 실행합니다. 원본 caller·manifest를 복사·전처리·제거하지 않으며 HACS job도 유지합니다. fetch/build/실행 실패는 모두 필수 job 실패입니다. secrets·추가 쓰기 권한을 요구하지 않습니다.

이 경로는 검증 도구만 선택하며 통합의 HA 지원 최소나 테스트 runtime을 변경하지 않습니다. cold build 비용과 upstream base image·wheel index·dependency 접근이 추가되고 job timeout은30분입니다. Core source는 fullSHA로 고정하지만 upstream Dockerfile의 base tag/일부 resolve까지 완전 재현하는 digest lock은 아닙니다. 설치된 최신 공식 이미지가 필요한 schema를 지원하면 같은 대상 커밋을 빈 입력으로 실제 재검증한 후 선택 입력을 제거할 수 있습니다. 도입한 대상은 SHA·근거·로컬/원격 build 결과·실제 Hassfest 결과를 STANDARDS/체크리스트에 기록합니다.

공식 근거: [custom categories 지원 변경](https://github.com/home-assistant/core/commit/c517d079e1cd3831dd8aa547dd953e336830e846), [검토 Core Dockerfile](https://github.com/home-assistant/core/blob/ec18d8b25d1ee39aa8b85a72a170e42bee33228c/script/hassfest/docker/Dockerfile), [dev image 미게시 조건](https://github.com/home-assistant/core/blob/ec18d8b25d1ee39aa8b85a72a170e42bee33228c/.github/workflows/builder.yml).

### 로컬 호환 경로 초안 검증 (2026-10-20)

중앙 `0490b2ad8378364b487746ea18fca7a0e1d22edc` 기반 격리 worktree의 초안에서 전체216 unit tests를 구현79.194초·독립76.676초에 통과했습니다. 새7개 검사는 외부 git/docker 경계만 대체하여 잘못된 ref·source 경로 충돌/링크·fetch 오류·HEAD 불일치·build/validator 오류의 실패 전파와 원래 caller mount/manifest 보존을 실행합니다. macOS의 기본 `/var` 임시 경로는 기존 CLI의 symlink 보호로 실패하므로 canonical `TMPDIR=/private/tmp`로 재실행했으며 코드 guard를 완화하지 않았습니다. Ruff0.17.1 check/format92files, actionlint1.7.12, 중앙37documents7workflows 및 diff 검사도 구현·독립 통과했습니다.

실제 Core `ec18d8b25d1ee39aa8b85a72a170e42bee33228c`를 fetch하고 HEAD 일치를 확인해 수정하지 않은 공식 Dockerfile로 local ARM64 build를 시도했습니다. source checkout317MB/context259MB, base image·CI 도구 설치 및115개 패키지 resolve까지 진행했지만85초 이후 일부 wheel 준비에서 진행이 없어서 약5분에 로컬 build를 취소했습니다. 해당 ARM64 wheel의 공식 URL은 host GET200·전체 다운로드로 확인했으나 Docker/uv 내부 정체 원인은 확정하지 않았습니다. 취소는 PASS가 아니며 완성 이미지·실제 공식 Hassfest 실행·원격 job 성공은 아직 미검증입니다. CI의 amd64 경로도 실제 build/run 전에 성공으로 보고하지 않습니다. 이 초안은 중앙 원격에 게시하거나 대상 caller에 적용하지 않았으며, 기존 대상의 published-image Hassfest 실패를 해결했다고 주장하지 않습니다.
