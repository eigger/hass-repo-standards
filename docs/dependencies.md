# 의존성 관리와 공통 CI

대상은 `manifest.json.requirements`에 있는 imagespec·blesession을 포함한 Python 패키지입니다. 아래 규칙은 프로젝트 정책이며, [Python requirement 명세](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)와 [HA manifest](https://developers.home-assistant.io/docs/creating_integration_manifest/)를 함께 적용합니다.

**DEP-01 필수**: manifest를 런타임 의존성의 원본으로 사용합니다. 테스트·린트 전용 패키지는 별도 requirements 파일에 둡니다. HA 자체와 HA가 제공하는 모듈을 통합 requirements에 중복 선언하지 않습니다. 로컬 개발 설치·CI 모두 같은 원본을 읽습니다.

**DEP-02 필수**: 기존 연산자를 보존합니다. `==`는 호환되는 특정 버전, `>=`는 하위 버전 호환 계약입니다. bot이 `==`를 `>=`로 일괄 바꾸지 않습니다. 새 외부 의존성은 검증한 `==`를 기본으로 하고, 내부 라이브러리의 `>=`는 최소 버전 CI와 채택 근거가 있을 때 허용합니다. 이 선택은 프로젝트 정책이며 공식 규격이라고 주장하지 않습니다.

**DEP-03 필수**: `imagespec[datamatrix]>=...`의 extras, 환경 marker, 패키지 이름을 보존합니다. 복합 범위·URL·wildcard·`~=`는 공통 자동 updater가 지원하지 않으므로 실패하고 수동 검토합니다. 지원하지 않는 형식을 조용히 건너뛰지 않습니다. 선택하지 않은 패키지는 수정하지 않습니다. 선택한 requirement의 marker가 현재 환경에서 비활성이면 updater를 실패시킵니다. 해당 marker가 활성인 Python/운영체제 환경에서 업데이트와 검증을 실행해야 합니다.

**DEP-04 필수**: 공통 updater는 PyPI의 안정 버전을 PEP 440로 비교합니다. pre/dev/yanked와 현재 Python에 맞지 않는 파일만 있는 버전은 제외합니다. major 변경은 자동 제안하지 않고 실패하여 검토를 요구합니다. `allow-major`는 검토 후 명시할 수 있습니다. 이미 선언한 버전보다 낮추지 않습니다. `>=` 하한을 올리는 것은 최소 지원 변경이므로 PR에 드러나야 합니다.

**DEP-05 필수**: 여러 통합에서 같은 패키지를 쓴다고 같은 버전을 강제하지 않습니다. 통합별 API 사용과 Python/HA 호환성을 확인합니다. library API 변경, 서비스 동작, 렌더링 결과, 연결/재연결 동작을 해당 테스트로 검증합니다.

## 공통 updater

`dependency-update.yml`의 입력은 domain, package 목록(JSON), Python 버전, lint/test requirements, validation-command입니다. 기본 bot branch는 `bot/manifest-dependencies` 하나이며 PR 내용에 실제 diff 요약을 넣습니다. 기본 브랜치를 main/master로 추측하지 않습니다. updater action은 변경하지 않을 때 파일을 다시 쓰지 않습니다. 성공적으로 변경 없음이 확인되면 PR 동기화 액션도 실행하여, 철회된 제안이나 이미 반영된 변경의 기존 PR과 branch를 정리합니다. 업데이트 또는 검증 실패 시에는 PR 동기화를 실행하지 않습니다.

- 예: `packages: '["imagespec", "blesession"]'` 또는 `'["blesession"]'`.
- `validation-command`는 **필수**입니다. 예: `python -m ruff check . && python -m pytest tests/ -q`. 선택 package를 테스트하지 않는 명령으로 통과시키지 않습니다.
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

Dependabot은 GitHub Actions와 일반 requirements 갱신을 맡습니다. manifest updater와 같은 파일을 동시에 수정하는 bot은 두지 않습니다.
