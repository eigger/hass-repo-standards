# 템플릿·스킬 도구 사용 안내

현재 구현은 계약·공통 렌더러, `inspect`·`plan`·`apply`·`recover`, 신규 작성 기반과 정적 검사이며 T1~T5는 main에 반영했습니다. T6 중앙 fixture의 생성·갱신 자동 회귀 구현·독립 검증과 PR CI도 완료했으며 외부 통합 적용은 이번 요청 범위가 아닙니다. 계획은 대상 파일을 변경하지 않으며 apply는 검증한 계획의 관리 범위를 씁니다. 실제 기기 동작은 작성해야 합니다. [단계별 검증](template-skill-validation.md)과 [구현 작업지시서](template-skill-tasks.md)는 중앙 도구 개발이나 과거 구현 근거를 확인할 때만 참고합니다.

## 실행 준비와 조사

[개발 안내](development.md)의 기존 의존성을 설치하고 대상 문법 이상 Python으로 실행합니다. legacy SHA plan은 실행 중인 중앙 checkout의 HEAD와 명시한 full SHA가 같고 `scripts/`, `schemas/`, `templates/`, `docs/`, `skills/`, `AGENTS.md`, 양언어 README, `actions/`, `.github/`가 깨끗해야 합니다. exact release plan도 resolved SHA의 checkout에서 실행하며, 별도 remote attestation 없이는 만들 수 없습니다. 미커밋 구현 checkout을 임의 SHA로 실행할 수 없습니다.

아래 `<target>`은 실제 조사할 대상 경로, `<work>`는 대상 밖에 미리 만든 작업 디렉터리입니다. 명령의 `<...>`는 실제 확인한 값으로 바꿉니다. 아래 표기는 실행 증거가 아닙니다.

```text
python3 scripts/manage_integration.py inspect <target> --output <work>/inventory.json
python3 scripts/manage_integration.py plan <target> --mode adopt --input <work>/input.json --standards-ref <reviewed-full-sha> --output <work>/plan.json
python3 scripts/manage_integration.py plan <empty-or-absent-target> --mode create --input <work>/input.json --standards-ref <reviewed-full-sha> --output <work>/create-plan.json
# Published immutable release only; this is not a bootstrap/candidate command.
python3 scripts/manage_integration.py verify-release --repository eigger/hass-repo-standards --tag vX.Y.Z --resolved-sha <full-sha> --output <work>/release-verification.json
python3 scripts/manage_integration.py plan <target> --mode adopt --input <work>/input.json --standards-ref <full-sha> --release-tag vX.Y.Z --release-verification <work>/release-verification.json --output <work>/release-plan.json
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
  "categories": {"value": ["diy_makers"], "source": "synthetic tool fixture decision only, not a real product classification"},
  "manifest": {
    "value": {
      "domain": "example", "name": "Example", "version": "1.0.0",
      "documentation": "https://github.com/owner/example",
      "issue_tracker": "https://github.com/owner/example/issues",
      "codeowners": ["@owner"], "categories": ["diy_makers"], "requirements": [], "dependencies": [],
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

`plan`은 legacy의 `standards_ref` 또는 release의 단일 `standards_reference`(exact tag/resolved SHA)와 remote attestation digest, `target_identity`, `validated_input`, `input_digest`, `guards`, `operations`, `unchanged`, `pending`, `conflicts`를 기록합니다. T3는 원래 대상 루트 존재 여부인 `target_identity.root_exists`를 필수로 기록합니다. release attestation은 network 확인 성공을 기록할 뿐 apply/recover에서 network를 다시 조회하지 않으며 tag 이동 fallback도 하지 않습니다. 검증한 입력의 독립 복사본과 canonical JSON SHA-256을 포함하므로 입력 파일의 이후 변경과 구분할 수 있습니다. 스키마의 로컬 `$ref`는 input/inventory/plan 세 파일만 허용하고 외부 URI나 다른 경로를 읽지 않습니다. 이전 T2 계획은 새 필수 필드와 SHA가 맞지 않으므로 깨끗한 검토 checkout에서 다시 생성해야 합니다.

각 operation의 경로·소유 방식·원본·규칙·전후 해시·content·unified diff를 확인합니다. 기존 README는 관리 영역만 계획하고 본문을 보존하며, 기존 테스트·고유 CI·최소 환경과 충돌하는 내용은 자동 교체하지 않습니다. 원본이 없는 계약 자산과 실제 구현·테스트가 필요한 부분은 `pending`으로 남깁니다. 대상 상태가 조사·렌더링 중 바뀌면 계획을 차단합니다. 실행 시각은 계획에 넣지 않습니다.

기존 `requirements_test.txt`가 생성안과 유효 requirement 줄을 앞뒤 공백을 제외한 같은 순서·문자열로 유지하고 주석/빈 줄만 다르면 기존 바이트를 unchanged로 보존합니다. 버전·extras·연산자·marker·환경 경로·실제 requirement 줄이 다르면 이 보존 규칙으로 병합하지 않습니다. dirty-user-file guard와 실제 충돌 처리는 유지하므로 임의 수동 편집 후 검사를 우회하는 경로가 아닙니다.

Dependabot 생성안은 실제 입력의 minimum requirements/constraints 경로를 제외하고 current 경로는 제외하지 않습니다. 기존 exclude·주기·groups·다른 ecosystem 항목은 보존합니다. minimum/current가 공유하는 경로의 역할을 확인할 수 없으면 pending으로 남기며 최소 지원을 바꾸거나 실제 bot 실행 성공으로 보고하지 않습니다.

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

## 정적 검사와 실제 실행 구분

T4는 기존 통합 검사 CLI에 공유 계약 검사를 연결했습니다. 독립 코드 검증을 완료했으며 새 명령이나 자동 수정 모드는 추가하지 않습니다.

```text
python3 scripts/check_integration.py <target> --check
python3 scripts/check_repository.py
```

`check_integration.py <target>`도 기본 읽기 전용 검사입니다. 성공은 종료 코드 0, 불일치·미완성·입력 오류는 기존과 같은 1이며 규칙 ID·경로·원인을 출력합니다. `.hass-standards.json`의 기존 승인 예외·근거 처리는 유지합니다. `--write-readmes`는 기존의 명시적 README 관리 영역 갱신 모드로 남으며 새 컴포넌트·테스트·기능을 자동 완성하지 않습니다.

검사는 중앙 파일/관리 경계, 실제 DOMAIN·manifest/config flow 일치, 선택 플랫폼·coordinator·진단의 대응 테스트와 활성 assertion 존재, strings/en 일치·ko 키/구조/placeholder·일부 코드에서 정적으로 확인 가능한 번역 키, 실제 액션 메타데이터, STANDARDS의 full SHA와 공용 workflow/action/standards-ref 일치를 확인합니다. 중앙 작성 기반의 정확한 미완성 표시와 알려진 빈 테스트·전체 skip/xfail을 검출해 실패시킵니다. 동적으로 계산한 플랫폼·번역 키나 임의로 변형한 테스트의 실행 의미를 완전히 증명하는 검사는 아닙니다. 정적 판별이 어려운 기존 구현은 근거와 예외 정책을 따라 검토하며 미확인을 성공으로 처리하지 않습니다.

`check_repository.py`는 중앙 계약·세 스키마 정의·원본과 참조·작성 기반 AST/JSON/YAML·번역 구조를 검사합니다. 중앙 `.tmpl` 안의 의도한 TODO는 자산으로 허용하며 적용된 통합의 TODO를 면제하지 않습니다. 기존 workflow/action 파일은 이번 단계에서 변경하지 않았으며 기존 check 진입과 CI 연결로 같은 검사를 실행합니다. caller checkout·action_path도 유지합니다.

정적 성공은 실제 HA setup·플랫폼·unload·실패 복구·외부 I/O mock 경계나 번역 의미·기기 조건의 검증 결과가 아닙니다. 실제 최소/current HA 환경과 해당 payload current/정확한 하한 실행 및 의미 리뷰의 범위는 [채택 절차](adoption.md#필요한-문서와-검증-범위)와 GOV-05를 따르고 증거를 체크리스트에 기록합니다. 생성·복구 성공이나 중앙 fixture 결과를 실제 채택 완료로 보고하지 않습니다.

## 중앙 시나리오 회귀

[raw fixture 안내](../tests/fixtures/scaffold/README.md)와 [CLI 시나리오 테스트](../tests/test_integration_scenarios.py)는 신규/기존 × 기본/imagespec/blesession/둘 다 조합을 검증합니다. 공통 README·CI·테스트는 현재 중앙 도구에서 생성하고 fixture에는 입력과 고유 보존 자료만 둡니다.

```text
python3 -m unittest discover -s tests -p test_integration_scenarios.py -v
```

이 명령은 중앙 저장소의 개발 환경에서 실행합니다. T6의 실제 독립 192개 실행 결과와 검증 대상 커밋의 PR CI는 [검증 기록](template-skill-validation.md)에 있으며, [PR #7](https://github.com/eigger/hass-repo-standards/pull/7)은 main에 병합되었습니다. 실행 대상은 임시 Git fixture이고 실제 외부 통합·기기·실제 최소/current HA 채택 성공을 검증하는 명령이 아닙니다. 중앙 도구·템플릿·스킬의 구현과 실제 통합 적용·개인 스킬 설치는 별도 범위입니다.

## 두 스킬의 원본·명시적 설치

중앙 원본은 [create-ha-integration](../skills/create-ha-integration/SKILL.md)와 [adopt-ha-standards](../skills/adopt-ha-standards/SKILL.md)입니다. 각 디렉터리는 SKILL.md·references/workflow.md·agents/openai.yaml만 포함하며 중앙 템플릿이나 도구를 복제하지 않습니다. 원본 작성·quick_validate 문법 검사와 격리 요청 분기 실행을 마쳤으며 자세한 관측·한계는 검증 기록에 분리합니다. 이번 작업에서 설치나 다른 통합 수정은 수행하지 않았습니다.

SKILL.md의 name/description·본문과 references는 공용 Agent Skills 형식이며 중앙 Python CLI·템플릿도 모델 API에 의존하지 않습니다. agents/openai.yaml은 OpenAI UI를 위한 선택 metadata이고 공통 실행의 필수 파일이 아닙니다. 호환 대상은 스킬을 읽고 파일/셸을 실행하는 **클라이언트**이며 Claude Code나 Antigravity의 지원을 일반 Claude/Gemini 웹 채팅 지원으로 해석하지 않습니다. [OpenAI 스킬 문서](https://learn.chatgpt.com/docs/build-skills), [Claude Code 스킬 문서](https://code.claude.com/docs/en/skills), [Antigravity 스킬 문서](https://antigravity.google/docs/skills)

2026-10-19 확인한 제품별 명시적 설치 위치는 다음과 같습니다. `<skill>`은 두 공용 원본 디렉터리 중 하나입니다. 설치 위치만 다르며 제품별 규칙·템플릿 사본을 별도로 유지하지 않습니다.

| 클라이언트 | Workspace 위치 | 사용자 전역 위치 |
|---|---|---|
| Codex | `.agents/skills/<skill>/` | `~/.agents/skills/<skill>/` |
| Claude Code | `.claude/skills/<skill>/` | `~/.claude/skills/<skill>/` |
| Antigravity App·IDE | `.agents/skills/<skill>/` | `~/.gemini/config/skills/<skill>/` |
| Antigravity CLI | `.agents/skills/<skill>/` | `~/.gemini/antigravity-cli/skills/<skill>/` |

이 표는 각 [공식 Codex](https://learn.chatgpt.com/docs/build-skills)·[Claude Code](https://code.claude.com/docs/en/skills)·[Antigravity](https://antigravity.google/docs/skills) 문서의 탐색 위치를 요약합니다. 이 환경에서 이미 쓰는 `$CODEX_HOME/skills`·`~/.codex/skills` 기존 경로와 현재 공식 Codex 안내의 `.agents/skills`를 구분합니다. 기존 설치를 자동 이동하거나 해당 기존 경로를 모든 클라이언트의 신규 권장 위치로 제시하지 않습니다.

이 리포의 실제 스킬 행동 평가는 Codex에서 수행했습니다. 다른 클라이언트 실행·자동 발동은 미검증입니다. GOV-05는 주 에이전트 직접 수행을 기본으로 하며 독립 리뷰가 필요한 범위에서 사용 가능한 별도 담당자를 활용합니다. 형식 호환이 제품별 위임·권한·실행 기능까지 같음을 보장하지 않으며 독립 리뷰를 수행하지 못하면 그 제약을 기록합니다.

설치는 별도의 사용자 요청이 있을 때 다음처럼 수행합니다.

1. 사용자가 선택한 중앙 checkout의 검토 full SHA와 원본 파일을 확인합니다. 설치할 스킬의 원본 SHA를 사용자 설치 기록에 남깁니다.
2. 사용자가 지정한 제품·설치 범위·경로를 확인하고 위 표의 해당 위치 아래에 두 공용 스킬 디렉터리를 각각 같은 이름으로 복사합니다. 일반 통합 적용 요청만으로 대상의 `.agents/skills`·`.claude/skills`·AGENTS.md나 다른 진입 파일을 자동 설치하지 않습니다. Workspace 설치 표는 별도 명시적 설치 요청이 있을 때의 위치입니다.
3. 이름이 같은 설치본이 있으면 로컬 변경·기존 원본 SHA를 비교하여 보존한 후 사용자 요청 범위에서 갱신합니다. 전체 skills 디렉터리를 덮어쓰거나 다른 스킬을 삭제하지 않습니다. 설치한 SKILL.md·workflow·metadata가 모두 같은 원본 SHA에서 왔는지 확인합니다.
4. 실제 호출에는 **별도로 확인한 중앙 checkout 경로·검토 full SHA·대상 경로·요청 범위**를 제공합니다. 설치된 스킬의 상대 `../../` 경로가 중앙 저장소라고 가정하지 않습니다. 중앙 HEAD·깨끗한 실행 자산·계약 버전 1이 맞지 않으면 실행을 중단하고 필요한 경로/버전 근거를 확인합니다.

중앙 checkout에 폴더가 있다는 것만으로 외부 리포에서 자동 발견된다고 주장하지 않습니다. 설치본 갱신은 중앙 규칙·도구와의 호환성 확인이 필요하며 검토 SHA가 다른 이전 계획은 그대로 재사용하지 않습니다.

설치 후 아래 호출은 Codex 표기 예시입니다. 다른 클라이언트의 호출 UI는 해당 공식 안내를 따르며 이 리포에서는 실제 호출을 검증하지 않았습니다. `<...>`는 실제 확인한 경로·SHA·입력으로 바꿉니다.

```text
$create-ha-integration: 중앙 <central>의 <full-sha>와 입력 <input.json>으로 <target>에 신규 통합 골격을 생성해줘.
$adopt-ha-standards: 중앙 <central>의 <full-sha> 공통 규칙을 기존 <target>에 적용해줘.
$adopt-ha-standards: 기존 <target>의 적용 차이만 검토하고 계획을 만들어줘. 파일은 적용하지 마.
```

신규는 create, 기존은 adopt로 분기하며 검토/계획만 요청하면 inspect/plan에서 멈춥니다. 이미 생성·적용을 요청했고 필수 근거·입력과 충돌 없는 계획이 있으면 같은 범위를 재승인받지 않고 apply합니다. 필수 입력 부재·실제 새 예외 승인 필요·CLI 실패는 근거를 제시하고 필요한 조치만 확인합니다. 스킬은 commit/push·PR·릴리스·workflow 수동 실행·외부 설치 권한을 추가하지 않습니다.

## categories 입력과 기존 설정 이관

[HA-02](home-assistant.md#통합-제품-카테고리-ha-02)에 따라 신규·채택 입력에는 sourced `categories` 판단이 필요합니다. 예시의 `diy_makers`는 도구 fixture용 명시 값이며 실제 통합의 기본 분류가 아닙니다. 지원 제품·서비스와 사용 목적에 맞는 공식 slug를 사람이 선택해 manifest와 같은 순서로 기록하고 실제 근거를 `source`에 적습니다. entity/system/virtual은 입력 `value: []`, 실제 유형/제외 이유를 source에 기록하며 manifest 키는 생략합니다. 입력 envelope의 `schema_version: 1`은 유지하며 검토 standards SHA가 세부 계약을 고정합니다. 이 SHA부터 필드가 없는 과거 version 1 입력은 `missing required inputs: categories`로 실패합니다. 실제 판단·근거를 추가하고 같은 새 SHA로 계획을 다시 생성하며, 과거 계획/입력을 그대로 재사용하거나 값을 자동 보충하지 않습니다.

`render_settings`는 `.hass-standards.json.categories_review`에 선택 배열·source·그때의 integration_type을 저장합니다. 과거 설정은 실제 재검토 후 보완하며 값/순서/유형이 달라지면 다시 검토합니다. 기록 존재는 실제 제품 의미·원격 검증 성공을 보장하지 않습니다. adoption 계획은 기존 manifest의 categories와 integration_type 차이를 conflict로 보고하며 자동 수정하지 않습니다. 원래 manifest·버전·지원 최소·의존성을 보존해 필요한 메타데이터 보완을 수동 검토하고 재계획합니다.
