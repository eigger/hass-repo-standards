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
9. 아래 영어 틀은 대상 `README.md`로, 한국어 틀은 `README.ko.md`로 작성하고 상호 연결합니다. 기존 한국어 내용·이전 안내는 한국어판에 보존하고 영어판에 같은 정보를 제공합니다. 두 언어의 관리 블록에 manifest domain의 동적 Usage 배지를 사전 조회 없이 생성합니다. 이 템플릿 폴더 자체는 배포할 통합이 아닙니다.

```markdown
# Integration Name

<!-- hass-standards:badges:start -->
<!-- hass-standards:badges:end -->

**English** | [한국어](README.ko.md)

Describe the supported device and connection method in one paragraph.

## Supported devices
Verified models, features, firmware, and limitations.

## Requirements
Minimum supported HA, hardware, accounts, proxies, and local/cloud requirements.

## Installation
Add a HACS custom repository (Integration), install, restart, and add the integration.
Document manual installation in custom_components/<domain> and removal.

## Configuration
Required/optional fields, authentication, and reconfiguration.

## Usage
Working action/YAML examples.

## Limitations and troubleshooting
Unsupported features, diagnostics, and removal of sensitive information.

## Development and contributing
Link to CONTRIBUTING or the actual development/testing instructions.

## Support
Report bugs via the enabled repository Issues page.
Use the enabled Discussions page for questions and feature requests.
Check the actual repository settings and replace these instructions with verified links.
If either feature is disabled, document the available support route without enabling it automatically.

## License
Link to the repository LICENSE file.
```

한국어판 `README.ko.md`의 대응 틀입니다. 실제 내용은 영어판과 함께 갱신합니다.

```markdown
# Integration Name

<!-- hass-standards:badges:start -->
<!-- hass-standards:badges:end -->

[English](README.md) | **한국어**

어떤 기기를 어떤 방식으로 연결하는지 한 문단으로 설명합니다.

## 지원 기기
검증한 모델·기능·펌웨어·제한사항.

## 요구사항
지원 최소 HA, 필요한 하드웨어·계정·proxy와 로컬/클라우드 조건.

## 설치
HACS 커스텀 리포(Integration) 추가, 설치, 재시작, 통합 추가.
수동 custom_components/<domain> 설치 경로와 제거 방법.

## 설정
필수·선택 필드와 인증·재설정 방법.

## 사용 예시
실제로 동작하는 action/YAML 예시.

## 제한사항과 문제 해결
미지원 기능, 진단 정보와 민감 값 제거 안내.

## 개발과 참여
CONTRIBUTING 또는 실제 개발·테스트 안내로 연결합니다.

## 지원
활성 Issues의 실제 링크를 버그 보고 경로로 제공합니다.
활성 Discussions의 실제 링크를 질문·기능 제안 경로로 제공합니다.
원격 설정을 확인하고 비활성 기능은 임의로 켜지 않으며 실제 사용 가능한 대체 지원 경로를 명시합니다.

## 라이선스
실제 LICENSE 파일로 연결합니다.
```

requirements_lint.txt는 복사할 수 있는 실제 고정 예시입니다. requirements_test.txt는 PyPI 메타데이터에서 HA 2026.10.2와 pytest-homeassistant-custom-component 0.13.373의 호환 선언을 확인한 예시이며 Python 3.14를 사용합니다. 모든 통합의 지원 최소를 이 버전으로 올리라는 뜻은 아닙니다. 실제 지원 범위를 확인하고 조합을 검증합니다.

**최신 테스트 환경과 지원 최소는 별개입니다.** 최신화 요청으로 hacs.json의 최소 버전을 올리거나 기존 최소 job을 삭제하지 않습니다. 최신 테스트 실패는 호환 문제를 수정하고 재검증합니다. 새 API 등 구버전 비호환 근거와 별도 명시적 사용자 승인이 있는 지원 정책 변경만 최소 상향을 허용합니다.

선언된 최소 지원과 현재 검증 HA가 원래 정확히 같으면 하나의 필수 job으로 검증합니다. 예전 최소 HA를 실제로 지원하는 통합만 requirements_test_min.txt·필요한 constraints와 별도 minimum-ha job을 추가하여 Python·requirements·expected-ha-version을 각각 지정합니다. 명시적 지원 정책 변경으로 옛 최소를 지원하지 않으면 관련 파일과 job을 함께 제거합니다. 라이브러리 하한이 있으면 dependency-modes/current·minimum 및 minimum-packages를 별도로 지정하며, 외부 Python 의존성이 없으면 minimum 라이브러리 job과 updater를 만들지 않습니다.

`.github/dependabot.yml`은 현재 HA·플러그인을 묶고, 과거 최소 환경이 존재할 때만 그 파일을 자동 갱신에서 제외하는 예시입니다. 제외 경로를 실제 구조에 맞춥니다. 묶인 PR도 workflow의 expected-ha-version·Python·관련 constraints를 자동 갱신하지 않으므로 함께 검토하고 동기화합니다. 기본 브랜치보다 낮아진 제안은 거부합니다. 구버전 비호환 근거와 별도 명시적 승인을 받아 최소 상향을 결정한 경우에만 hacs.json과 README·지원 정책 기록도 함께 맞춥니다. 공통 workflow는 과거 caller 호환을 위해 unit 기본값을 유지하므로 통합은 ha를 명시합니다. pytest-args 생략 시 ha는 tests/components/<domain>/ -v를 사용합니다.

[실제 HA 테스트 구조](../../docs/testing.md), [의존성 선언·추가 규칙](../../docs/dependencies.md), [Bluetooth 공통 설정·추천 기기](../../docs/bluetooth.md)를 채택 기준으로 사용합니다.

채택 점검에는 [체크리스트 사용법](../../docs/checklist.md)과 [ADOPTION_CHECKLIST.md](ADOPTION_CHECKLIST.md)를 사용합니다. 모든 항목은 미확인에서 시작하며 실제 적용한 통합의 증거로 채웁니다.

이 진입 AGENTS.md 설치 후 사용자는 해당 리포 세션에서 “공통 규칙 적용해줘”라고 요청하면 됩니다. 공통 지침의 읽기·위임·검증·중앙 보고 순서를 따르며 리포별 세부 규칙을 다시 나열할 필요가 없습니다.
