# 통합 README 템플릿

이 폴더는 복사 후 값과 환경을 검토하는 **채택 예시**입니다. 실제 통합 skeleton이나 바로 배포할 코드가 아닙니다.

1. `.github/workflows`의 main을 실제 기본 브랜치로 바꿉니다.
2. example domain, Python 버전, package 목록, requirements 경로를 실제 환경으로 바꾸고 통합의 필수 테스트는 `test-profile: ha`로 지정합니다. `update_dependencies.yml`의 `validation-command`도 `tests/components/<domain>/`를 실행하도록 바꾸고 `test-profile: ha`를 지정합니다. YAML은 current 최신 테스트 job의 예시이며 지원 최소를 선언하지 않습니다. 실제 선언된 최소가 current보다 낮으면 별도 minimum-ha job과 호환 requirements를 추가·유지해야 채택 기준을 충족합니다.
3. 각 `@main`을 검토한 main의 commit SHA로 바꿉니다.
4. 테스트/린트 requirements와 기존 pyproject.toml을 정리합니다. Ruff 설정은 현재 코드에 맞게 채택합니다.
5. 테스트는 `tests/components/<domain>/`에 배치하고 실제 HA fixture·config entry·플랫폼 로딩으로 검증합니다. 최소 package matrix는 사용하는 package만 넣으며 두 환경 모두 실제 HA 테스트를 실행합니다. 최소 HA가 현재 검증 버전과 다르면 별도 환경에서 검증합니다.
6. STANDARDS.md, ADOPTION_CHECKLIST.md와 AGENTS.md를 복사하고 참조 커밋·적용 상태·검증 증거·예외를 기록합니다. blesession/proxy 통합의 README는 공통 Bluetooth 설정·추천 기기로 연결하고 기기별 준비 조건을 추가합니다.
7. 작업 시작·단계 변경·종료 시 [중앙 적용 현황](../../docs/adoption-status.md)의 자기 리포 행을 갱신하고, 구현과 리뷰·검증은 서로 다른 서브 에이전트에게 위임합니다.
8. [HACS 브랜드 검사 안내](../../docs/hacs.md)에 따라 로컬 custom_components/<domain>/brand/icon.png 또는 실제 원격 brands 등록 근거를 준비하고 해당 커밋에서 HACS를 실행합니다. README 배지·HACS Default 여부와 브랜드 검사 통과는 각각 구분합니다.
9. README는 아래 틀을 사용하되 기존 언어와 이전 안내를 유지합니다.

```markdown
# Integration Name

<!-- hass-standards:badges:start -->
<!-- hass-standards:badges:end -->

어떤 기기를 어떤 방식으로 연결하는지 한 문단으로 설명합니다.

## Supported devices
확인된 모델·기능·펌웨어와 제한사항.

## Requirements
최소 HA, 필요한 하드웨어·계정·proxy, 로컬/클라우드 조건.

## Installation
HACS Custom repository 추가(Integration), 설치, 재시작, 통합 추가.
수동 설치 경로 custom_components/<domain>과 제거 방법.

## Configuration
필수/선택 필드와 인증·재설정 방법.

## Usage
실제로 동작하는 action/YAML 예시.

## Limitations and troubleshooting
미지원 기능, 진단 정보와 민감 값 제거 안내.

## Support and license
Issues, 기존 Discussions 활성 여부, LICENSE 링크.
```

requirements_lint.txt는 복사할 수 있는 실제 고정 예시입니다. requirements_test.txt는 PyPI 메타데이터에서 HA 2026.10.2와 pytest-homeassistant-custom-component 0.13.373의 호환 선언을 확인한 예시이며 Python 3.14를 사용합니다. 모든 통합의 지원 최소를 이 버전으로 올리라는 뜻은 아닙니다. 실제 지원 범위를 확인하고 조합을 검증합니다.

**최신 테스트 환경과 지원 최소는 별개입니다.** 최신화 요청으로 hacs.json의 최소 버전을 올리거나 기존 최소 job을 삭제하지 않습니다. 최신 테스트 실패는 호환 문제를 수정하고 재검증합니다. 새 API 등 구버전 비호환 근거와 별도 명시적 사용자 승인이 있는 지원 정책 변경만 최소 상향을 허용합니다.

선언된 최소 지원과 현재 검증 HA가 원래 정확히 같으면 하나의 필수 job으로 검증합니다. 예전 최소 HA를 실제로 지원하는 통합만 requirements_test_min.txt·필요한 constraints와 별도 minimum-ha job을 추가하여 Python·requirements·expected-ha-version을 각각 지정합니다. 명시적 지원 정책 변경으로 옛 최소를 지원하지 않으면 관련 파일과 job을 함께 제거합니다. 라이브러리 하한이 있으면 dependency-modes/current·minimum 및 minimum-packages를 별도로 지정하며, 외부 Python 의존성이 없으면 minimum 라이브러리 job과 updater를 만들지 않습니다.

`.github/dependabot.yml`은 현재 HA·플러그인을 묶고, 과거 최소 환경이 존재할 때만 그 파일을 자동 갱신에서 제외하는 예시입니다. 제외 경로를 실제 구조에 맞춥니다. 묶인 PR도 workflow의 expected-ha-version·Python·관련 constraints를 자동 갱신하지 않으므로 함께 검토하고 동기화합니다. 기본 브랜치보다 낮아진 제안은 거부합니다. 구버전 비호환 근거와 별도 명시적 승인을 받아 최소 상향을 결정한 경우에만 hacs.json과 README·지원 정책 기록도 함께 맞춥니다. 공통 workflow는 과거 caller 호환을 위해 unit 기본값을 유지하므로 통합은 ha를 명시합니다. pytest-args 생략 시 ha는 tests/components/<domain>/ -v를 사용합니다.

[실제 HA 테스트 구조](../../docs/testing.md), [의존성 선언·추가 규칙](../../docs/dependencies.md), [Bluetooth 공통 설정·추천 기기](../../docs/bluetooth.md)를 채택 기준으로 사용합니다.

채택 점검에는 [체크리스트 사용법](../../docs/checklist.md)과 [ADOPTION_CHECKLIST.md](ADOPTION_CHECKLIST.md)를 사용합니다. 모든 항목은 미확인에서 시작하며 실제 적용한 통합의 증거로 채웁니다.

이 진입 AGENTS.md 설치 후 사용자는 해당 리포 세션에서 “공통 규칙 적용해줘”라고 요청하면 됩니다. 공통 지침의 읽기·위임·검증·중앙 보고 순서를 따르며 리포별 세부 규칙을 다시 나열할 필요가 없습니다.
