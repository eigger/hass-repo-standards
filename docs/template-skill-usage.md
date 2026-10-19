# 템플릿·스킬 도구 사용 안내

현재 구현은 계약·공통 렌더러와 읽기 전용 `inspect`·`plan`입니다. 계획은 대상 파일을 변경하지 않습니다. `apply`, 신규 컴포넌트·테스트 작성 기반과 두 스킬은 미구현입니다. [단계별 검증](template-skill-validation.md)과 [구현 작업지시서](template-skill-tasks.md)를 함께 확인합니다.

## 실행 준비와 조사

[개발 안내](development.md)의 기존 의존성을 설치하고 대상 문법 이상 Python으로 실행합니다. `plan`은 실행 중인 중앙 checkout의 HEAD와 명시한 full SHA가 같고 `scripts/`, `schemas/`, `templates/`, `docs/`, `AGENTS.md`, 양언어 README가 깨끗해야 합니다. 미커밋 구현 checkout을 임의 SHA로 실행할 수 없습니다.

아래 `<target>`은 실제 조사할 대상 경로, `<work>`는 대상 밖에 미리 만든 작업 디렉터리입니다. 명령의 `<...>`는 실제 확인한 값으로 바꿉니다. 아래 표기는 실행 증거가 아닙니다.

```text
python3 scripts/manage_integration.py inspect <target> --output <work>/inventory.json
python3 scripts/manage_integration.py plan <target> --mode adopt --input <work>/input.json --standards-ref <reviewed-full-sha> --output <work>/plan.json
python3 scripts/manage_integration.py plan <empty-or-absent-target> --mode create --input <work>/input.json --standards-ref <reviewed-full-sha> --output <work>/create-plan.json
```

`inspect`는 Git 원격·기본/현재 브랜치·작업 트리, manifest·hacs·README 지원 선언·requirements·workflow·관리 주석·조건부 기능을 조사합니다. `observations`의 `field/value/source`, `conflicts`, `pending`을 확인합니다. 기본 브랜치를 main/master로 추정하지 않으며 조회 불가 값을 수동 확인할 과제로 남깁니다. 원격 자격 정보를 결과에 그대로 기록하지 않고 Git이 무시하는 환경 디렉터리는 조사에서 제외합니다.

## 입력 작성

입력은 [단일 입력 스키마](../schemas/integration-input.schema.json)를 따릅니다. `schema_version` 외 값은 확인한 `value`와 그 근거 `source`로 묶습니다. inventory는 조사 결과이며 plan 입력과 구조가 다르므로 그대로 `--input`에 전달하지 않습니다. 원격·domain·선언이 충돌하면 실제 자료를 확인해야 하며 높은 버전이나 임의 기본값을 선택하지 않습니다. T1 API에서는 remote가 선택 항목이지만 T2 계획은 출처를 포함한 remote를 요구합니다.

아래는 `tests/test_standards_contract.py`와 `tests/test_integration_planning.py`의 임시 fixture에 맞춘 설명용 입력입니다. `owner/example`, `trunk`, 라이선스, 기능과 환경 버전은 실제 통합의 값이나 검증 근거가 아닙니다. 실제 대상에는 원격·manifest·지원 선언·LICENSE·기능·검증 환경을 읽어 대체하고 모든 `source`에 실제 근거를 기록합니다.

```json
{
  "schema_version": 1,
  "repository": {"value": "owner/example", "source": "explicit unit-test input (not device evidence)"},
  "remote": {"value": "https://github.com/owner/example.git", "source": "explicit fixture origin"},
  "default_branch": {"value": "trunk", "source": "explicit unit-test input (not device evidence)"},
  "domain": {"value": "example", "source": "explicit unit-test input (not device evidence)"},
  "manifest": {
    "value": {
      "domain": "example", "name": "Example", "version": "1.0.0",
      "documentation": "https://github.com/owner/example",
      "issue_tracker": "https://github.com/owner/example/issues",
      "codeowners": ["@owner"], "requirements": [], "dependencies": [],
      "after_dependencies": [], "config_flow": true
    },
    "source": "explicit unit-test input (not device evidence)"
  },
  "readme": {
    "value": {
      "title": "Example", "descriptions": {"en": "An integration.", "ko": "통합입니다."},
      "issues": true, "discussions": false, "related_projects": []
    },
    "source": "explicit unit-test input (not device evidence)"
  },
  "license": {
    "value": {"name": "MIT License", "path": "LICENSE", "notices": {"en": [], "ko": []}},
    "source": "explicit unit-test input (not device evidence)"
  },
  "configuration": {"value": "ui", "source": "explicit unit-test input (not device evidence)"},
  "platforms": {"value": ["sensor"], "source": "explicit unit-test input (not device evidence)"},
  "features": {
    "value": {
      "coordinator": false, "shared_entity": false, "diagnostics": false,
      "actions": false, "fixtures": false, "snapshots": false, "dependency_updates": false
    },
    "source": "explicit unit-test input (not device evidence)"
  },
  "environments": {
    "value": {
      "minimum": {"ha": "2026.10.2", "python": "3.14", "pytest_homeassistant_custom_component": "0.13.373", "requirements": ["requirements_test.txt"], "constraints": []},
      "current": {"ha": "2026.10.2", "python": "3.14", "pytest_homeassistant_custom_component": "0.13.373", "requirements": ["requirements_test.txt"], "constraints": []},
      "libraries": {}
    },
    "source": "explicit unit-test input (not device evidence)"
  }
}
```

fixture의 최소/current가 같은 것은 실제 대상의 최소를 올릴 근거가 아닙니다. 서로 다르면 각 환경을 따로 기록합니다. imagespec·blesession 사용은 실제 requirements·절대 import로 판단하며 라이브러리 버전·payload 필드는 스키마와 해당 규칙에 따라 추가합니다.

## 계획 검토와 제한

`plan`은 `standards_ref`, `target_identity`, `validated_input`, `input_digest`, `guards`, `operations`, `unchanged`, `pending`, `conflicts`를 기록합니다. 검증한 입력의 독립 복사본과 canonical JSON SHA-256을 포함하므로 입력 파일의 이후 변경과 구분할 수 있습니다. 스키마의 로컬 `$ref`는 input/inventory/plan 세 파일만 허용하고 외부 URI나 다른 경로를 읽지 않습니다.

각 operation의 경로·소유 방식·원본·규칙·전후 해시·content·unified diff를 확인합니다. 기존 README는 관리 영역만 계획하고 본문을 보존하며, 기존 테스트·고유 CI·최소 환경과 충돌하는 내용은 자동 교체하지 않습니다. 원본이 없는 계약 자산과 실제 구현·테스트가 필요한 부분은 `pending`으로 남깁니다. 대상 상태가 조사·렌더링 중 바뀌면 계획을 차단합니다. 실행 시각은 계획에 넣지 않습니다.

`inspect`/`plan`은 충돌이 없으면 종료 코드 0, 충돌·입력 오류·I/O 오류면 2를 반환합니다. 가능한 경우 충돌을 포함한 JSON을 출력하므로 코드와 결과를 함께 확인합니다. `pending`이 있는 코드 0은 조사나 초안 계획 작성 성공만 의미하며 통합 완성·실제 HA 검증 성공이 아닙니다. 출력 파일은 대상 밖에 두며 입력 파일을 덮어쓸 수 없고 출력 부모는 미리 존재해야 합니다. symlink/junction 출력 경로도 거부합니다.

실제 적용·복구는 T3, 전체 계약 기반 검사는 T4, 스킬 설치·실행은 T5 구현 후 안내합니다. 현재 계획의 content를 임의로 복사해 공식 apply나 실제 채택 완료로 보고하지 않습니다.
