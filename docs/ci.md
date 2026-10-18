# CI 작성 규칙

이 문서의 필수 항목은 프로젝트 정책입니다. [GitHub 보안 지침](https://docs.github.com/en/actions/reference/security/secure-use)과 [재사용 workflow](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows)를 참고합니다.

## 역할과 분리

**CI-01 필수**: 검증은 읽기 전용, 업데이트 PR과 릴리스는 쓰기 작업으로 분리합니다. 통합은 Validate와 Tests를 사용하고, frontend/browser/Android/add-on 작업은 독립 job으로 유지합니다. 같은 역할의 코드를 다시 복사하지 않고 중앙 reusable workflow 또는 composite action을 사용합니다.

| 역할 | 중앙 구현 | 리포별 입력/확장 |
|---|---|---|
| HACS·Hassfest | validate-integration.yml | HACS ignore와 사유 |
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
| `tests.yml` | `Tests` | 모든 대상 브랜치 PR의 생성·갱신·재오픈, 실제 기본 브랜치 push, 수동 |
| `update_dependencies.yml` | `Update dependencies` | 예약·수동, 업데이트할 외부 의존성이 있는 경우만 적용 |

리포 전용 CI의 작업·실행 조건은 리포에 맡깁니다. 파일명은 소문자 단어를 밑줄로 연결한 `.yml`, 표시 이름은 역할이 명확한 영어로 작성합니다(예: `build_frontend.yml` / `Build frontend`). 공용 CI를 같은 이름의 로컬 구현으로 대체하지 않습니다. 기존 required checks·특수 목적 job을 보존하고 이름 변경 영향은 확인합니다. 불가피한 차이는 [중앙 템플릿 수정 또는 사용자 승인](adoption.md#중앙-템플릿과-예외) 후 적용합니다.

**CI-03 필수**: 검증 workflow는 `permissions: contents: read`, checkout은 `persist-credentials: false`, 각 job에 timeout을 둡니다. 취소 가능한 검증에는 workflow+ref concurrency를 둡니다. dependency updater에는 취소하지 않는 별도 그룹을 둡니다. write 권한은 PR 생성/릴리스 job에만 줍니다.

**CI-04 필수**: 정상 lint/test를 `continue-on-error`, `|| true`, 항상 성공하는 wrapper로 숨기지 않습니다. lint와 test는 의존성이 없다면 병렬 실행합니다. optional matrix는 필수 검사를 대체하지 않습니다. required checks 변경은 채택 PR에 기록합니다. paths 필터로 필수 체크가 영구 Pending이 되는 구성을 피합니다.

**CI-05 필수**: 외부 action·중앙 workflow는 검토한 full SHA로 참조하고 외부 action 버전 또는 검토한 커밋 설명을 주석으로 붙입니다. Dependabot으로 갱신합니다. SHA 고정이 action 내부 Docker 이미지까지 고정하는 것은 아닙니다. HACS/Hassfest는 upstream 이미지가 바뀔 수 있는 validator이며 schedule로 변화를 탐지합니다. 완전한 재현 환경은 별도 image digest 정책이 필요합니다.

## 환경과 명령

**CI-06 필수**: lint와 test 의존성은 버전 관리된 requirements/lock 파일에서 설치합니다. 통합 런타임 요구사항은 manifest에서 읽고 한 번의 pip resolver 호출로 테스트 요구사항과 함께 설치합니다. 여러 `pip install`로 충돌을 가리는 것을 피하고 `pip check`를 실행합니다. 생성 파일은 RUNNER_TEMP에 둡니다.

**CI-07 필수**: Python과 HA/pytest 플러그인은 실제 호환 조합을 입력합니다. 통합의 필수 검사는 `ha`로 실행하고 pytest 대상은 `tests/components/<domain>/`로 맞춥니다. 실제 HA fixture·통합 로딩을 사용하며 `unit`은 독립 도구 등의 보조 검사로만 둡니다. 최소/현재 라이브러리와 최소 HA 환경을 구분합니다. cache key에는 requirements와 manifest를 포함합니다. format은 `ruff format --check .`, lint는 `ruff check .`를 기본으로 하되 외부 복사 코드 제외는 pyproject에 명시합니다.

**CI-08 필수**: PR title/body/branch 같은 표현식은 shell에 직접 삽입하지 않고 env로 전달합니다. `pull_request_target`에서 외부 PR 코드를 checkout해 실행하지 않습니다. 일반 테스트에 secrets를 요구하지 않습니다. 재사용 workflow에 `secrets: inherit`를 기본으로 쓰지 않습니다.

## 업데이트·배포

**CI-09 필수**: 의존성 변경은 PR로만 제안합니다. branch는 저장소 기본 브랜치를 API로 읽고 하나의 bot branch를 재사용합니다. 연산자/extras/marker를 유지하며 자동 merge·tag·release는 하지 않습니다. 검증 명령 실패 시 PR을 생성/갱신하지 않습니다.

**CI-10 필수**: GITHUB_TOKEN으로 만든 PR의 push/PR 이벤트가 다른 workflow를 자동 실행한다고 가정하지 않습니다. 공통 updater는 변경한 tree에서 선택 package의 정확한 새 하한과 지정한 검증을 먼저 실행하며, 추가 required checks는 수동 dispatch 또는 GitHub App 토큰 등 별도 운영 방식으로 충족합니다. dispatch 실패를 경고만 하고 모든 검증이 끝났다고 표시하지 않습니다. 본 구현은 PAT/App 비밀키를 요구하지 않습니다.

**CI-11 필수**: release는 검증한 같은 commit/tag에서 수행하고 별도 job만 contents:write를 받습니다. 산출물·manifest·tag 일치를 확인합니다. 이 공통 규칙 리포는 통합 릴리스 자동 배포를 제공하지 않습니다.

**CI-12 필수**: 테스트 의존성 추가·업데이트 PR도 [실제 HA 테스트 기준](testing.md)과 [의존성 추가 절차](dependencies.md)를 따릅니다. HA 패키지 설치·환경 summary·stub 테스트의 성공만으로 통합 검증을 완료하지 않습니다. 필요한 HA 구성요소와 package 요구사항을 설치하고 실제 entry·플랫폼 테스트를 실행합니다.

현재 테스트의 Python·HA·플러그인을 최신화해도 지원 최소 메타데이터와 최소 검증 job은 유지합니다. 최신 환경의 실패는 호환성을 수정하여 재검증하고, 새 API 등 확인한 구버전 비호환 근거와 별도 명시적 사용자 승인 없이 최소 지원 상향으로 우회하지 않습니다.

공통 workflow/action은 과거 caller 호환을 위해 `unit` 기본값을 유지합니다. 실행용 템플릿은 `ha`를 명시하며, HA 최소/현재 버전이 다르면 각기 Python·requirements·expected-ha-version을 지정한 별도 caller job으로 실행하고, 정확히 같으면 하나의 필수 job을 사용합니다. `pytest-args`를 생략하면 `ha`는 `tests/components/<domain>/ -v`, `unit`은 `tests/ -v`를 실행합니다. 환경 action은 실제 HA와 테스트 플러그인 설치·버전을 확인하지만 실제 통합 로딩 테스트의 성공은 별도로 검증해야 합니다.

## 입력과 경계

공통 workflow는 로컬 trusted requirements와 명령을 실행합니다. 입력은 사용자 리포가 관리하며 임의 외부 값으로 만들지 않습니다. `pytest-args`, `validation-command`는 의도적인 shell 명령 입력이므로 PR 본문이나 네트워크 응답에서 생성하지 않습니다. composite action은 스크립트를 자신의 `github.action_path`에서 읽고 caller의 파일을 검사합니다. 실제 호출 예시는 templates/integration/.github/workflows에 있습니다.

## 형식 검사

Validate caller는 중앙 `actions/check-standards`을 사용해 README 관리 영역·테스트 기본 구조·공용 workflow 형식을 검사합니다. 검사 action과 reusable workflow는 검토한 전체 SHA로 고정합니다. 검사 실패를 성공으로 바꾸지 않습니다. 검사기는 기록된 승인 예외의 형식과 범위만 반영하며 승인 요청·승인 대기 기능을 수행하지 않습니다. 승인 근거의 진위와 리포별 의미 검증은 적용 에이전트와 독립 리뷰의 책임입니다.
