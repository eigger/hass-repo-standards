# 의존성 관리와 공통 CI

대상은 `manifest.json.requirements`에 있는 imagespec·blesession을 포함한 Python 패키지입니다. 아래 규칙은 프로젝트 정책이며, [Python requirement 명세](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)와 [HA manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/)를 함께 적용합니다.

**DEP-01 필수**: manifest를 런타임 의존성의 원본으로 사용합니다. 테스트·린트 전용 패키지는 별도 requirements 파일에 둡니다. HA 자체와 HA가 제공하는 모듈을 통합 requirements에 중복 선언하지 않습니다. 로컬 개발 설치·CI 모두 같은 원본을 읽습니다.

**DEP-02 필수**: 기존 연산자를 보존합니다. `==`는 호환되는 특정 버전, `>=`는 하위 버전 호환 계약입니다. bot이 `==`를 `>=`로 일괄 바꾸지 않습니다. 새 외부 의존성은 검증한 `==`를 기본으로 하고, 내부 라이브러리의 `>=`는 최소 버전 CI와 채택 근거가 있을 때 허용합니다. 이 선택은 프로젝트 정책이며 공식 규격이라고 주장하지 않습니다.

**DEP-03 필수**: `imagespec[datamatrix]>=...`의 extras, 환경 marker, 패키지 이름을 보존합니다. 복합 범위·URL·wildcard·`~=`는 공통 자동 updater가 지원하지 않으므로 실패하고 수동 검토합니다. 지원하지 않는 형식을 조용히 건너뛰지 않습니다. 선택하지 않은 패키지는 수정하지 않습니다. 선택한 requirement의 marker가 현재 환경에서 비활성이면 updater를 실패시킵니다. minimum 환경 설치는 marker가 비활성인 선택 패키지를 로그에 알리고, 선택한 패키지가 모두 비활성이면 실패시킵니다. 해당 marker가 활성인 Python/운영체제 환경에서 업데이트와 검증을 실행해야 합니다.

**DEP-04 필수**: 공통 updater는 PyPI의 안정 버전을 PEP 440로 비교합니다. pre/dev/yanked와 현재 Python에 맞지 않는 파일만 있는 버전은 제외합니다. major 변경은 자동 제안하지 않고 실패하여 검토를 요구합니다. `allow-major`는 검토 후 명시할 수 있습니다. 이미 선언한 버전보다 낮추지 않습니다. `>=` 하한을 올리는 것은 최소 지원 변경이므로 PR에 드러나야 합니다.

**DEP-05 필수**: 여러 통합에서 같은 패키지를 쓴다고 같은 버전을 강제하지 않습니다. 통합별 API 사용과 Python/HA 호환성을 확인합니다. library API 변경, 서비스 동작, 렌더링 결과, 연결/재연결 동작을 해당 테스트로 검증합니다.

## 선언 위치와 추가 기준

**DEP-06 필수**: 외부 Python 패키지와 HA 구성요소 의존성을 구분합니다. Core와 같은 의미로 선언하며 테스트를 통과시키기 위해 잘못된 위치에 패키지를 넣지 않습니다.

| 의존성 종류 | 선언·설치 기준 |
|---|---|
| imagespec·blesession 등 통합의 직접 Python 의존성 | `custom_components/<domain>/manifest.json`의 `requirements` |
| 통합 실행에 반드시 먼저 로딩할 HA 구성요소 | 같은 manifest의 `dependencies`에 HA domain 선언 |
| 선택 기능에서 사용하며 로딩 순서만 필요한 HA 구성요소 | 실제 필요에 맞게 `after_dependencies`; 필수 로딩으로 간주하지 않음 |
| HA 런타임·테스트 fixture | `requirements_test.txt` 또는 해당 환경의 lock/constraints에 호환 버전 고정 |
| pytest 플러그인·timeout·snapshot 등 테스트 도구 | 테스트 requirements에 사용한 도구만 선언 |
| Ruff 등 린트 도구 | `requirements_lint.txt`에 선언 |
| HA 구성요소가 요구하는 외부 패키지 | 테스트에 설치한 HA 버전의 해당 component manifest에서 읽어 설치 |

HA domain과 PyPI 배포 이름은 같다고 가정하지 않습니다. HA가 제공하는 모듈을 통합의 직접 의존성처럼 다시 추가하지 않고, 테스트 전용 패키지를 런타임 manifest에 넣지 않습니다. 설치된 HA 패키지를 기본으로 하며 Core 저장소의 최신 requirements 전체를 다른 HA 버전에 섞어 설치하지 않습니다.

**DEP-07 필수**: HA 통합 테스트 환경에는 호환되는 `pytest-homeassistant-custom-component`와 실제 `homeassistant`가 반드시 설치돼야 합니다. 플러그인과 HA의 정확한 호환 버전을 requirements/lock/constraints로 기록합니다. 플러그인이 HA를 고정하면 해당 제약을 따르며 중복 선언을 충돌시키지 않습니다. pytest·asyncio·timeout·snapshot은 선택한 플러그인이 제공하는 요구사항을 우선하고, 직접 사용하는 추가 도구만 호환 버전으로 명시합니다.

사용하는 HA 구성요소의 `requirements`와 필수 `dependencies`를 재귀적으로 설치하고, 선택 경로에서 실제 로딩하는 `after_dependencies`도 테스트 대상에 명시합니다. Bluetooth 등을 가짜 모듈로 바꿔 missing dependency를 숨기거나, 모듈 import만 되는 환경을 HA 실행 검증으로 취급하지 않습니다. 설치 확인 후 [실제 통합 로딩 테스트](testing.md)를 실행합니다.

**DEP-08 필수**: 새 의존성을 추가하거나 버전·extras·marker를 변경할 때 다음을 같은 변경에서 검토합니다.

1. 필요한 API와 직접/선택/테스트 전용 의존성 구분을 확인하고 올바른 선언 위치를 수정합니다.
2. 지원 최소 HA·Python에서 패키지가 실제 설치되는지 확인합니다. extras·marker·라이선스·지원 플랫폼과 배포 가능 여부도 확인합니다.
3. manifest와 테스트 요구사항·constraints를 함께 해결하고 설치 버전을 확인한 뒤 `pip check`를 실행합니다. 새로 고정한 값은 존재하는 릴리스만 사용합니다.
4. 외부 통신만 대체한 실제 HA 테스트로 config entry setup·플랫폼·변경한 기능을 검증합니다. imagespec·blesession 같은 하한 계약은 정확한 최소 버전에서도 검증합니다.
5. HACS/Hassfest, 개발 환경 재현 명령, 문서의 요구사항·업데이트 대상 package 목록을 필요한 범위에서 갱신합니다.

`ModuleNotFoundError`가 나면 선언·설치·플러그인/HA 조합을 수정합니다. `sys.modules` stub, blanket import skip, `--no-deps`로 빠진 패키지를 감추지 않습니다. 독립 프로토콜 라이브러리의 단위 테스트도 보조로 유지할 수 있지만 통합의 실제 HA 검증을 생략하는 근거로 삼지 않습니다.

## 공통 updater

`dependency-update.yml`의 입력은 domain, package 목록(JSON), Python 버전, lint/test requirements, validation-command입니다. 기본 bot branch는 `bot/manifest-dependencies` 하나이며 PR 내용에 실제 diff 요약을 넣습니다. 기본 브랜치를 main/master로 추측하지 않습니다. updater action은 변경하지 않을 때 파일을 다시 쓰지 않습니다. 성공적으로 변경 없음이 확인되면 PR 동기화 액션도 실행하여, 철회된 제안이나 이미 반영된 변경의 기존 PR과 branch를 정리합니다. 업데이트 또는 검증 실패 시에는 PR 동기화를 실행하지 않습니다.

- 예: `packages: '["imagespec", "blesession"]'` 또는 `'["blesession"]'`.
- `validation-command`는 **필수**이며 통합 리포에서는 실제 HA 테스트 경로 `tests/components/<domain>/`를 실행해야 합니다. 예: `python -m ruff check . && python -m pytest tests/components/example/ -q`. 선택 package를 테스트하지 않는 명령으로 통과시키지 않습니다.
- bot은 변경 manifest에서 선택한 패키지를 정확한 새 하한 버전으로 설치·확인하고 테스트 요구사항을 함께 설치합니다. 이어서 필요하면 HA component 요구사항을 추가하고, `pip check` 후 검증합니다.
- GITHUB_TOKEN PR의 후속 CI 제한은 [CI-10](ci.md)을 따릅니다. updater에서 수행한 검증과 PR required checks를 구별합니다.
- GitHub의 Actions PR 생성 허용 설정이 필요합니다. 설정을 자동 변경하지 않습니다.

## 최소 버전 검증

`python-tests.yml`의 `dependency-modes: '["current", "minimum"]'`와 `minimum-packages`를 지정하면 두 환경을 별도 job으로 실행합니다. current는 선택한 test requirements/constraint와 manifest 범위 안에서 resolver가 선택한 버전이며, 반드시 PyPI 절대 최신이라는 뜻은 아닙니다. minimum은 지정 패키지의 `>=x`를 `==x` 추가 제약으로 설치하고 설치값까지 확인합니다. 두 환경 모두 extras와 marker를 유지합니다.

`ha-components`는 실제 설치한 HA 패키지의 구성요소 manifest에서 requirements와 명시적 dependencies를 읽습니다. 설치만으로 HA 생명주기 검증이 되는 것은 아닙니다. 네트워크 discovery나 선택 after_dependencies가 필요하면 component 이름을 추가 입력합니다.

## 공통 도구의 로컬 사용

```bash
python3 -m pip install -r requirements_tools.txt
python3 actions/update-manifest/update.py --manifest ../hass-example/custom_components/example/manifest.json --packages '["imagespec", "blesession"]'
# 위 명령은 기본 dry-run. 적용하려면 --write를 명시합니다.
```

Dependabot은 GitHub Actions와 일반 requirements 갱신을 맡습니다. manifest updater와 같은 파일을 동시에 수정하는 bot은 두지 않습니다. [공식 설정 설명](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference#exclude-paths)에 따라 과거 최소 지원용 requirements·constraints는 `exclude-paths`로 일반 업데이트에서 제외하여 현재 환경 갱신과 섞이지 않게 합니다. 실제 사용하는 경로를 지정하며 지원 정책 변경 시 검토한 변경으로만 갱신합니다.

DEP-07·DEP-08 적용 시 현재 HA와 테스트 플러그인은 같은 PR에서 호환 조합으로 갱신합니다. Dependabot의 `groups`는 PR 묶음이며 Python·HA 제약·workflow의 `expected-ha-version`·지원 최소 메타데이터를 자동 동기화하지 않습니다. 변경 전 실제 기본 브랜치를 다시 읽고 기존보다 낮아진 제안은 거부합니다. 공식 안정 릴리스·플러그인 메타데이터를 확인하고 Python·requirements·constraints·정확한 HA 검사값을 함께 맞춘 뒤 resolver·`pip check`·실제 HA 테스트를 실행합니다. 기존 최소를 유지하면 최소 메타데이터는 유지하고, 최소를 올리기로 명시적으로 결정한 경우에는 hacs.json·문서·지원 정책 기록도 같은 변경에서 갱신합니다. 예전 커밋 기준으로 생성된 PR의 제목만 보고 합치지 않습니다.

설치 action은 `ha`에서 실제 HA와 `pytest-homeassistant-custom-component`의 설치를 확인하고 버전을 보고합니다. 실행용 requirements 예시는 채택할 통합의 실제 지원 범위에 맞춰 검토합니다. 각 통합 manifest는 해당 통합의 채택 범위에서만 변경합니다.
