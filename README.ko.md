# Home Assistant Repository Standards

[English](README.md) | **한국어**

Home Assistant 커스텀 통합의 공통 개발·문서·HACS·CI·의존성·릴리스 규칙과 재사용 workflow를 관리합니다. 별도 태그나 GitHub Release 없이 **main과 커밋 이력**으로 관리합니다.

규칙은 한국어로 작성하며 코드 식별자, 로그, CI job 이름은 영어를 사용합니다. 공식 규격과 프로젝트 정책을 구분합니다. 기존 리포는 채택 PR에서 참조한 커밋과 예외를 기록하고 점진적으로 이관합니다.

## 규칙

| 문서 | 내용 |
|---|---|
| [적용과 변경 관리](docs/adoption.md) | 필수·권장 구분, 기존 리포 이관, 예외 |
| [중앙 적용 현황](docs/adoption-status.md) | 리포별 진행 상태·적용 내용·검증/리뷰 근거·남은 작업 |
| [적용 권장 순서](docs/adoption-plan.md) | 적용 대상 HA 통합 22개 파일럿·단계별 적용 계획 |
| [템플릿·스킬 구조 개편 구현안](docs/template-skill-plan.md) | 계약·템플릿·CLI·스킬; T1~T6 구현·독립 검증 완료, T6 PR CI 통과·병합 상태는 [PR #7](https://github.com/eigger/hass-repo-standards/pull/7) 확인 |
| [템플릿·스킬 사용 안내](docs/template-skill-usage.md) | 조사·계획·적용/복구·정적 검사·명시적 스킬 설치; 기기 동작은 별도 구현 |
| [템플릿·스킬 구현 검증](docs/template-skill-validation.md) | 단계별 상태·명령·환경·근거·남은 작업 |
| [통합별 적용 체크리스트](docs/checklist.md) | 적용 상태·검증 증거·호환 환경·예외 기록 |
| [Home Assistant 개발](docs/home-assistant.md) | Core와 대응하는 구조, 설정, async, 엔티티, BLE |
| [HACS와 배포](docs/hacs.md) | manifest, hacs.json, 버전과 배포 구조 |
| [README와 배지](docs/documentation.md) | 문서 순서, 언어, 배지 조건·순서·스타일 |
| [테스트와 호환성](docs/testing.md) | tests/components/domain 구조, 실제 HA fixture·로딩, 최소 버전 |
| [CI 작성 규칙](docs/ci.md) | 공통 workflow, 권한, 이벤트, timeout, 확장 |
| [의존성 관리](docs/dependencies.md) | 선언 위치·추가 절차, HA 테스트 의존성, 업데이트·최소 버전 |
| [Payload 문서 작성 규칙](docs/payload-documentation.md) | 필수 양언어 기기별 안내·실제 HA/imagespec 예제 검사; imagespec의 공통 [한국어](https://github.com/eigger/imagespec/blob/main/docs/payload.ko.md) / [English](https://github.com/eigger/imagespec/blob/main/docs/payload.md) 안내 |
| [Bluetooth 문서 작성 규칙](docs/bluetooth-documentation.md) | 작성자 요구사항과 사용자 안내 연결 |
| [Bluetooth proxy 사용자 안내](https://github.com/eigger/blesession/blob/main/docs/bluetooth.ko.md) | blesession에서 관리하는 공통 사용자 안내 ([English](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md))·[공통 문제 해결](https://github.com/eigger/blesession/blob/main/docs/troubleshooting.ko.md) |
| [릴리스·유지보수](docs/releases.md) | 버전, 변경 기록, 이관, 지원 상태 |
| [전체 리포 CI 조사](docs/ci-audit.md) | 로컬 hass* 전체 workflow 비교와 이관 계획 |
| [초기 구현 검증](docs/validation.md) | 테스트 환경과 확인 범위 |
| [공식 자료](docs/sources.md) | 확인한 공식 문서와 확인일 |

통합의 기본 README.md는 영어, README.ko.md는 한국어로 제공하며 상호 연결합니다. HA 통합의 Usage 배지는 집계 존재 사전 확인 없이 manifest domain으로 미리 추가합니다.

현재 규칙은 HACS 커스텀 통합도 Core와 유사한 구현·테스트 구조를 사용하도록 정의합니다. hass-kibble 첫 파일럿의 공통 규칙 적용·실제 HA 검증·README 언어·Usage 후속 보완을 완료했습니다. hass-catprinter 두 번째 파일럿도 최소·현재 HA와 최종 CI의 독립 검증을 마쳤습니다. 나머지 통합은 중앙 현황표의 순서와 범위에 따라 이관합니다.

## 리포별 작업 시작

**“hass-repo-standards 공통 규칙 적용해줘”**라고 요청하고, 필요하면 중앙 checkout 경로나 리포 URL을 지정합니다. 에이전트는 적용 작업 때 중앙 [AGENTS.md](AGENTS.md)·관련 규칙·체크리스트를 직접 읽습니다. 구현과 리뷰·검증은 별도의 서브 에이전트가 수행하고, 주 에이전트가 결과를 취합하며 중앙 현황표를 갱신합니다.

중앙 AGENTS.md나 그 내용을 통합의 AGENTS.md로 복사·생성·추가하지 않고, 다른 파일명으로 에이전트 진입 지침을 설치하지도 않습니다. 사용자 별도 요청 없이는 재설치하지 않으며 기존 리포 고유 지침은 보존합니다. 통합에는 STANDARDS.md에 검토한 표준 SHA·예외를, ADOPTION_CHECKLIST.md에 해당 시점의 검증 근거를 기록합니다. 과거 PASS는 이후 변경의 검증 결과가 아닙니다.

README 공통 영역·테스트 기본 구조·공용 CI는 중앙 템플릿을 의무 적용하고 자동 검사합니다. README의 나머지 구성과 기존 본문은 각 리포에 맡겨 보존합니다. 양언어는 같은 구조·내용으로 유지하며 독립 리뷰에서 번역 의미를 확인합니다. 차이는 중앙 템플릿 수정 또는 사용자 명시적 승인 후 적용하고 근거·범위를 기록합니다. 승인 요청은 에이전트가 수행하며 CI가 승인 대기하지 않습니다.

공통 Bluetooth 프록시 추천·설정·문제 해결은 blesession에서 관리합니다. 중앙은 작성 규칙·양언어 기기별 문제 해결 템플릿·공용 Validate 검사를 관리합니다. 일반 프록시 안내를 읽기 위해 blesession을 설치할 필요는 없습니다. 기존 중앙 안내 URL은 이전 안내로 유지합니다.

## 공통 CI

| 파일 | 용도 |
|---|---|
| [.github/workflows/validate-integration.yml](.github/workflows/validate-integration.yml) | HACS와 Hassfest 병렬 검증 |
| [.github/workflows/python-tests.yml](.github/workflows/python-tests.yml) | Ruff, Python matrix, manifest 설치, HA 구성요소 요구사항, pytest |
| [.github/workflows/dependency-update.yml](.github/workflows/dependency-update.yml) | 선택 패키지의 안정 버전 조회·manifest 수정·단일 업데이트 PR |
| [actions/python-environment](actions/python-environment/action.yml) | 테스트·브라우저 job에서 같은 Python 의존성 설치 |
| [actions/update-manifest](actions/update-manifest/action.yml) | imagespec·blesession 등 업데이트 로직 |

호출 예시는 [templates/integration](templates/integration/USAGE.md)에 있습니다. 중앙 workflow는 호출한 리포의 코드를 checkout합니다. 리포별 경로·Python·의존성·HA 구성요소·제외 검사는 입력으로 받습니다. 브라우저, 카드, Android, 애드온 빌드는 해당 리포에 남깁니다.

[개발·검사 안내](docs/development.ko.md)에서 로컬 준비·전체 조사·테스트·배지 검사 명령을 확인합니다.

## 지원

- [Issues](https://github.com/eigger/hass-repo-standards/issues): 버그를 신고하거나 기능을 요청하세요.

질문도 현재 Issues를 이용합니다. Discussions는 비활성 상태입니다.

## 라이선스

[MIT License](LICENSE) 라이선스로 배포됩니다.
