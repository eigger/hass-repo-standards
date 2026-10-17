# 통합 README 템플릿

이 폴더는 복사 후 값과 환경을 검토하는 **채택 예시**입니다. 실제 통합 skeleton이나 바로 배포할 코드가 아닙니다.

1. `.github/workflows`의 main을 실제 기본 브랜치로 바꿉니다.
2. example domain, Python 버전, package 목록, requirements 경로를 실제 환경으로 바꾸고 통합의 필수 테스트는 `test-profile: ha`로 지정합니다. 현재 YAML의 unit 예시는 이전 환경 검사 예시이므로 그대로 채택하지 않습니다.
3. 각 `@main`을 검토한 main의 commit SHA로 바꿉니다.
4. 테스트/린트 requirements와 기존 pyproject.toml을 정리합니다. Ruff 설정은 현재 코드에 맞게 채택합니다.
5. 테스트는 `tests/components/<domain>/`에 배치하고 실제 HA fixture·config entry·플랫폼 로딩으로 검증합니다. 최소 package matrix는 사용하는 package만 넣으며 두 환경 모두 실제 HA 테스트를 실행합니다. 최소 HA는 별도 환경에서 검증합니다.
6. STANDARDS.md, ADOPTION_CHECKLIST.md와 AGENTS.md를 복사하고 참조 커밋·적용 상태·검증 증거·예외를 기록합니다. blesession/proxy 통합의 README는 공통 Bluetooth 설정·추천 기기로 연결하고 기기별 준비 조건을 추가합니다.
7. 작업 시작·단계 변경·종료 시 [중앙 적용 현황](../../docs/adoption-status.md)의 자기 리포 행을 갱신하고, 구현과 리뷰·검증은 서로 다른 서브 에이전트에게 위임합니다.
8. README는 아래 틀을 사용하되 기존 언어와 이전 안내를 유지합니다.

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

requirements_lint.txt는 복사할 수 있는 실제 고정 예시입니다. 테스트 requirements는 실제 HA와 pytest-homeassistant-custom-component의 호환 버전 및 필요한 HA 구성요소 요구사항을 기준으로 작성합니다. 기존 stub 테스트 환경을 그대로 복사하지 않습니다. 이번 변경에서는 실행용 requirements 파일이나 CI YAML을 수정하지 않습니다. HA fixture/플러그인 버전을 임의로 통일하지 않습니다.

[실제 HA 테스트 구조](../../docs/testing.md), [의존성 선언·추가 규칙](../../docs/dependencies.md), [Bluetooth 공통 설정·추천 기기](../../docs/bluetooth.md)를 채택 기준으로 사용합니다.

채택 점검에는 [체크리스트 사용법](../../docs/checklist.md)과 [ADOPTION_CHECKLIST.md](ADOPTION_CHECKLIST.md)를 사용합니다. 모든 항목은 미확인에서 시작하며 실제 적용한 통합의 증거로 채웁니다.

이 진입 AGENTS.md 설치 후 사용자는 해당 리포 세션에서 “공통 규칙 적용해줘”라고 요청하면 됩니다. 공통 지침의 읽기·위임·검증·중앙 보고 순서를 따르며 리포별 세부 규칙을 다시 나열할 필요가 없습니다.
