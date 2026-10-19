# 템플릿·스킬 도구 사용 안내

현재 구현은 계약·공통 렌더러, 읽기 전용 `inspect`·`plan`, T3의 `apply`·`recover`와 신규 작성 기반입니다. T3 독립 코드/문서 검증은 완료했고 커밋/CI 확인은 남아 있습니다. 계획은 대상 파일을 변경하지 않으며 apply는 검증한 계획의 관리 범위를 씁니다. 실제 기기 동작은 작성해야 하고 두 스킬은 미구현입니다. [단계별 검증](template-skill-validation.md)과 [구현 작업지시서](template-skill-tasks.md)를 함께 확인합니다.

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

`plan`은 `standards_ref`, `target_identity`, `validated_input`, `input_digest`, `guards`, `operations`, `unchanged`, `pending`, `conflicts`를 기록합니다. T3는 원래 대상 루트 존재 여부인 `target_identity.root_exists`를 필수로 기록합니다. 검증한 입력의 독립 복사본과 canonical JSON SHA-256을 포함하므로 입력 파일의 이후 변경과 구분할 수 있습니다. 스키마의 로컬 `$ref`는 input/inventory/plan 세 파일만 허용하고 외부 URI나 다른 경로를 읽지 않습니다. 이전 T2 계획은 새 필수 필드와 SHA가 맞지 않으므로 T3의 깨끗한 검토 checkout에서 다시 생성해야 합니다.

각 operation의 경로·소유 방식·원본·규칙·전후 해시·content·unified diff를 확인합니다. 기존 README는 관리 영역만 계획하고 본문을 보존하며, 기존 테스트·고유 CI·최소 환경과 충돌하는 내용은 자동 교체하지 않습니다. 원본이 없는 계약 자산과 실제 구현·테스트가 필요한 부분은 `pending`으로 남깁니다. 대상 상태가 조사·렌더링 중 바뀌면 계획을 차단합니다. 실행 시각은 계획에 넣지 않습니다.

`inspect`/`plan`은 충돌이 없으면 종료 코드 0, 충돌·입력 오류·I/O 오류면 2를 반환합니다. 가능한 경우 충돌을 포함한 JSON을 출력하므로 코드와 결과를 함께 확인합니다. `pending`이 있는 코드 0은 조사나 초안 계획 작성 성공만 의미하며 통합 완성·실제 HA 검증 성공이 아닙니다. 출력 파일은 대상 밖에 두며 입력 파일을 덮어쓸 수 없고 출력 부모는 미리 존재해야 합니다. symlink/junction 출력 경로도 거부합니다.

## 적용과 복구

검토한 계획에 미해결 충돌이 없을 때 요청 범위에서 실행합니다. `<work>`는 대상 밖에 존재하는 디렉터리이며 기존 journal을 덮어쓰지 않는 새 경로를 사용합니다. `--journal`은 선택 인자이지만 복구 근거를 쉽게 찾도록 아래처럼 명시할 수 있습니다. 실제 기기 명령은 실행하지 않습니다.

```text
python3 scripts/manage_integration.py apply <target> --plan <work>/plan.json --journal <work>/journal.json
python3 scripts/manage_integration.py recover <target> --journal <work>/journal.json
```

apply는 내장 입력 스키마·digest, 동일 full SHA의 깨끗한 실행 자산, 대상 identity·원래 루트 존재 여부·guards를 확인합니다. 같은 입력으로 재계획하여 operation 경로·소유 방식·content·after hash까지 대조합니다. 계획의 JSON content만 임의 편집해 적용하는 경로는 지원하지 않습니다. 잠금과 쓰기 직전 확인으로 동시 편집을 검출하며 대상 밖 journal에 기존 바이트를 base64와 해시로 보관합니다. 기본 journal은 plan 파일 stem에 `.apply.json`을 붙인 경로이며, 지정한 journal의 고정 형제 경로 `<journal>.plan.json`에 검토 계획 anchor를 보존합니다. 예를 들어 `journal.json`의 anchor는 `journal.json.plan.json`입니다. 두 파일은 대상 쓰기 전에 기존 파일을 덮어쓰지 않고 게시하며 기존/orphan anchor가 있으면 자동 교체하지 않습니다. `create_only`의 기존 통합 구현·회귀 테스트는 교체하지 않고 관리 영역 밖 본문·fixture·고유 CI·지원 최소를 보존합니다.

최초의 빈/없는 대상은 create 계획으로 생성합니다. 생성 후에는 같은 입력의 **adopt** 계획에서 추가 `operations`가 0인지 확인해 멱등성을 판정합니다. 비어 있지 않은 결과에 create를 반복하면 신규 생성 조건 때문에 차단됩니다. 실제 동작·검증 pending은 추가 diff가 없어도 남습니다.

파일별 교체가 끝나기 전 실패할 수 있어 다중 파일 전체의 원자성을 보장하지 않습니다. 결과 JSON의 status·적용 경로·journal·복구 안내를 확인하고 부분 실패 후 해당 journal로 recover합니다. recover는 고정 anchor와 journal의 내장 계획·digest를 대조하고 guard와 base64 backup으로 외부 임시 preimage를 복원해 같은 SHA로 전체 재계획합니다. anchor 부재·변조 또는 보존 guard 파일의 후속 수정으로 원래 상태를 재현할 수 없으면 쓰기 전에 거부합니다. 현재 파일이 기록한 출력 해시와 같은지 확인한 뒤 원본을 복원하거나 이번에 만든 파일·디렉터리를 정리하며 후속 사용자 수정은 덮어쓰지 않습니다. 대상 루트가 원래 있었는지도 구분합니다. 원본 plan 파일이 없어도 journal과 anchor를 보존하면 복구할 수 있으므로 두 파일을 함께 보존합니다. 이 무결성 확인은 같은 사용자가 모든 산출물을 함께 바꿀 때 신원을 인증하는 보장이 아닙니다. 실패 상태·입력 오류는 종료 코드 2이며 정상 적용·복구의 0은 실제 HA나 기기 검증 성공을 의미하지 않습니다.

중앙 자산은 45개 중 available 40개·pending 5개입니다. 빈 `custom_components/__init__.py`도 create_only로 생성하고 기존 파일은 보존합니다. 개별 HA 테스트는 수집 단계에서 실제 `custom_components.<domain>.const`의 DOMAIN을 import해 플러그인의 regular package 선점을 방지합니다. available은 원본 존재를 뜻하며 새 코드·UI flow·플랫폼·coordinator·진단·대응 테스트는 TODO·`NotImplementedError`와 실제 작성 pending을 포함합니다. strings/en은 같은 영어 소스에서 생성하고 ko 키·구조·placeholder·미해결 Core 참조를 검증합니다. 실제 UI 문구·기능·entry/client fixture·액션 스키마를 채우기 전에는 완성되지 않습니다. Python 3.9 문법 검사는 정확한 최소/current HA API 호환성 검증을 대신하지 않으며 두 환경의 실제 실행이 필요합니다.

전체 계약 기반 검사는 T4, 스킬 설치·실행은 T5 후속 단계입니다. 생성·복구 성공이나 중앙 fixture 결과를 실제 채택 완료로 보고하지 않습니다.
