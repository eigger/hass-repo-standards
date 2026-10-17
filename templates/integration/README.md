# 통합 README 템플릿

이 폴더는 복사 후 값과 환경을 검토하는 **채택 예시**입니다. 실제 통합 skeleton이나 바로 배포할 코드가 아닙니다.

1. `.github/workflows`의 main을 실제 기본 브랜치로 바꿉니다.
2. example domain, Python 버전, package 목록, requirements 경로, unit/ha profile을 실제 환경으로 바꿉니다.
3. 각 `@v0.1.0`을 확인한 release commit SHA로 바꿉니다.
4. 테스트/린트 requirements와 기존 pyproject.toml을 정리합니다. Ruff 설정은 현재 코드에 맞게 채택합니다.
5. 최소 package matrix는 사용 중인 package만 넣습니다. HA 최소 버전은 별도 job에서 검증합니다.
6. STANDARDS.md와 AGENTS.md 참조를 추가하고 예외를 기록합니다.
7. README는 아래 틀을 사용하되 기존 언어와 이전 안내를 유지합니다.

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

requirements_lint.txt는 복사할 수 있는 실제 고정 예시입니다. 테스트 requirements는 리포의 현재 테스트 환경을 옮겨야 하므로 일반 파일을 제공하지 않습니다. HA fixture/플러그인 버전을 임의로 통일하지 않습니다.
