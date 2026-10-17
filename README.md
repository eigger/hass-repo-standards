# Home Assistant Repository Standards

Home Assistant 커스텀 통합의 공통 개발·문서·HACS·CI·의존성·릴리스 규칙과 재사용 workflow를 관리합니다. 별도 태그나 GitHub Release 없이 **main과 커밋 이력**으로 관리합니다.

규칙은 한국어로 작성하며 코드 식별자, 로그, CI job 이름은 영어를 사용합니다. 공식 규격과 프로젝트 정책을 구분합니다. 기존 리포는 채택 PR에서 참조한 커밋과 예외를 기록하고 점진적으로 이관합니다.

## 규칙

| 문서 | 내용 |
|---|---|
| [적용과 변경 관리](docs/adoption.md) | 필수·권장 구분, 기존 리포 이관, 예외 |
| [통합별 적용 체크리스트](docs/checklist.md) | 적용 상태·검증 증거·호환 환경·예외 기록 |
| [Home Assistant 개발](docs/home-assistant.md) | Core와 대응하는 구조, 설정, async, 엔티티, BLE |
| [HACS와 배포](docs/hacs.md) | manifest, hacs.json, 버전과 배포 구조 |
| [README와 배지](docs/documentation.md) | 문서 순서, 언어, 배지 조건·순서·스타일 |
| [테스트와 호환성](docs/testing.md) | tests/components/domain 구조, 실제 HA fixture·로딩, 최소 버전 |
| [CI 작성 규칙](docs/ci.md) | 공통 workflow, 권한, 이벤트, timeout, 확장 |
| [의존성 관리](docs/dependencies.md) | 선언 위치·추가 절차, HA 테스트 의존성, 업데이트·최소 버전 |
| [Bluetooth 공통 설정](docs/bluetooth.md) | proxy 설정, 추천 기기·리비전, blesession 통합의 README 연결 |
| [릴리스·유지보수](docs/releases.md) | 버전, 변경 기록, 이관, 지원 상태 |
| [전체 리포 CI 조사](docs/ci-audit.md) | 로컬 hass* 전체 workflow 비교와 이관 계획 |
| [초기 구현 검증](docs/validation.md) | 테스트 환경과 확인 범위 |
| [공식 자료](docs/sources.md) | 확인한 공식 문서와 확인일 |

현재 규칙은 HACS 커스텀 통합도 Core와 유사한 구현·테스트 구조를 사용하도록 정의합니다. 기존 통합 리포와 공통 CI 구현·실행용 템플릿의 전환은 별도 작업으로 진행합니다.

## 공통 CI

| 파일 | 용도 |
|---|---|
| [.github/workflows/validate-integration.yml](.github/workflows/validate-integration.yml) | HACS와 Hassfest 병렬 검증 |
| [.github/workflows/python-tests.yml](.github/workflows/python-tests.yml) | Ruff, Python matrix, manifest 설치, HA 구성요소 요구사항, pytest |
| [.github/workflows/dependency-update.yml](.github/workflows/dependency-update.yml) | 선택 패키지의 안정 버전 조회·manifest 수정·단일 업데이트 PR |
| [actions/python-environment](actions/python-environment/action.yml) | 테스트·브라우저 job에서 같은 Python 의존성 설치 |
| [actions/update-manifest](actions/update-manifest/action.yml) | imagespec·blesession 등 업데이트 로직 |

호출 예시는 [templates/integration](templates/integration/README.md)에 있습니다. 중앙 workflow는 호출한 리포의 코드를 checkout합니다. 리포별 경로·Python·의존성·HA 구성요소·제외 검사는 입력으로 받습니다. 브라우저, 카드, Android, 애드온 빌드는 해당 리포에 남깁니다.

**이 리포 생성만으로 기존 리포의 파일이나 CI는 변경되지 않습니다.** 아래 검사는 읽기 전용입니다.

```bash
python3 -m pip install -r requirements_dev.txt
python3 scripts/audit_repositories.py --root .. --output /tmp/hass-ci-audit.json
python3 scripts/audit_repositories.py --github-owner eigger --output /tmp/hass-ci-remote.json
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
```

배지는 관리 구역 안에서만 갱신합니다. [사용법](docs/documentation.md)을 먼저 확인하세요.

```bash
python3 scripts/sync_badges.py ../hass-example --check
```
