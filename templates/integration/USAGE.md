# 통합 중앙 템플릿 사용법

이 폴더는 복사 후 값과 환경을 검토하는 **채택 예시**입니다. 실제 통합 skeleton이나 바로 배포할 코드가 아닙니다.

1. `.github/workflows`의 main을 실제 기본 브랜치로 바꿉니다.
2. example domain, Python 버전, package 목록, requirements 경로를 실제 환경으로 바꾸고 통합의 필수 테스트는 `test-profile: ha`로 지정합니다. `update_dependencies.yml`의 `validation-command`도 `tests/components/<domain>/`를 실행하도록 바꾸고 `test-profile: ha`를 지정합니다. YAML은 current 최신 테스트 job의 예시이며 지원 최소를 선언하지 않습니다. 실제 선언된 최소가 current보다 낮으면 별도 minimum-ha job과 호환 requirements를 추가·유지해야 채택 기준을 충족합니다.
3. 각 `@main`을 검토한 main의 commit SHA로 바꿉니다.
4. 테스트/린트 requirements와 기존 pyproject.toml을 정리합니다. Ruff 설정은 현재 코드에 맞게 채택합니다.
5. 테스트는 `tests/components/<domain>/`에 배치하고 실제 HA fixture·config entry·플랫폼 로딩으로 검증합니다. 최소 package matrix는 사용하는 package만 넣으며 두 환경 모두 실제 HA 테스트를 실행합니다. 최소 HA가 현재 검증 버전과 다르면 별도 환경에서 검증합니다.
6. 적용 기록용 STANDARDS.md와 ADOPTION_CHECKLIST.md를 복사하고 참조 커밋·적용 상태·해당 시점의 실제 검증 증거·예외를 기록합니다. 중앙 AGENTS.md나 그 내용을 통합의 AGENTS.md로 복사·생성·추가하지 않으며 다른 파일명으로 에이전트 진입 지침을 설치하지도 않습니다. 사용자 별도 요청 없이는 재설치하지 않고 기존 리포 고유 지침은 임의로 수정·삭제하지 않습니다. blesession/proxy 통합은 [Bluetooth 작성 규칙](../../docs/bluetooth-documentation.md)을 읽고 README.md에는 영어 사용자 가이드, README.ko.md에는 한국어 사용자 가이드를 연결하며 기기별 준비 조건을 추가합니다. 개발자 작성·구현 가이드를 사용자 설정 안내로 연결하지 않습니다.
7. 작업 시작·단계 변경·종료 시 [중앙 적용 현황](../../docs/adoption-status.md)의 자기 리포 행을 갱신하고, 구현과 리뷰·검증은 서로 다른 서브 에이전트에게 위임합니다.
8. [HACS 브랜드 검사 안내](../../docs/hacs.md)에 따라 로컬 custom_components/<domain>/brand/icon.png 또는 실제 원격 brands 등록 근거를 준비하고 해당 커밋에서 HACS를 실행합니다. README 배지·HACS Default 여부와 브랜드 검사 통과는 각각 구분합니다.
9. README 공통 영역에 중앙 템플릿을 적용하고 기존 공통 내용을 합칩니다. 양언어 본문은 같은 구조·내용으로 번역하며 기존 본문·이전 안내·저작권 고지를 보존합니다. 세부 구성은 리포에 맡기고 긴 YAML·설정·개발 명령을 공통 적용 때문에 이동하지 않습니다. header/support/related-projects/license 관리 주석을 지정하고 badges 주석은 header 안에 유지합니다. 배지는 flat, Release → HACS → HA minimum → Tests → Validate → License → Usage 순서이며 기존 고유 배지는 뒤에 보존합니다.
10. `tests/`의 세 빈 init와 루트 conftest는 중앙 파일을 그대로 적용하고 domain 디렉터리를 실제 domain으로 바꿉니다. domain conftest의 fixture 이름·역할을 유지하며 config entry가 있으면 실제 entry 데이터의 mock_config_entry를, 외부 클라이언트가 있으면 mock_client를 추가합니다. 실제 HA setup·플랫폼·unload 테스트를 작성하고 기존 회귀 범위는 보존합니다. placeholder를 완료된 테스트로 제출하지 않습니다.
11. `.hass-standards.json`에 실제 메타데이터·양언어 소개·지원 활성 여부·라이선스·기존 고지·관련 프로젝트를 기록한 뒤 `python3 scripts/check_integration.py <대상경로>`를 실행합니다. `--write-readmes`는 기존 관리 영역만 갱신합니다. 최초 갱신 전 기존 공통 내용·고지를 설정으로 옮겨 검토하고, 도구가 미등록 내용을 이유로 중단하면 삭제·우회하지 말고 보존 계획을 확인합니다. Validate caller의 중앙 검사와 별도 독립 리뷰로 번역 의미·본문 보존·실제 HA 동작을 검증합니다.
12. 공용 caller 이름과 파일명은 Validate/validate.yml, Tests/tests.yml, Update dependencies/update_dependencies.yml로 고정하고 기존 실행 조건을 유지합니다. 전용 CI는 소문자·밑줄 `.yml` 및 역할이 명확한 영어 표시 이름을 사용하되 내용·실행 조건은 리포가 정합니다.
13. 차이가 필요하면 이유·영향·대안을 제시해 중앙 템플릿 수정·검증 또는 사용자 명시적 승인 후 적용합니다. 승인 근거·일자·허용 범위·재검토 조건은 STANDARDS.md에 기록하고 검사 예외 설정과 연결합니다. CI는 승인을 요청하지 않습니다. 중앙 변경만으로 다른 리포를 자동 수정하지 않습니다.

템플릿의 `MIT License`는 예시입니다. 실제 LICENSE 내용에서 이름을 확인해 바꾸며 라이선스가 없다고 예시 라이선스를 생성·부여하지 않습니다.

공통 영역의 실제 파일은 [README.md](README.md)·[README.ko.md](README.ko.md)입니다. 이 안내 파일을 통합 README로 복사하지 않습니다. 기존 본문의 섹션 순서·제목·내용은 각 리포에 맡기고 그대로 보존합니다. 중앙 템플릿은 공통 영역의 문구·순서·줄바꿈만 강제하며 본문 전체 틀을 강제하지 않습니다.

requirements_lint.txt는 복사할 수 있는 실제 고정 예시입니다. requirements_test.txt는 PyPI 메타데이터에서 HA 2026.10.2와 pytest-homeassistant-custom-component 0.13.373의 호환 선언을 확인한 예시이며 Python 3.14를 사용합니다. 모든 통합의 지원 최소를 이 버전으로 올리라는 뜻은 아닙니다. 실제 지원 범위를 확인하고 조합을 검증합니다.

**최신 테스트 환경과 지원 최소는 별개입니다.** 최신화 요청으로 hacs.json의 최소 버전을 올리거나 기존 최소 job을 삭제하지 않습니다. 최신 테스트 실패는 호환 문제를 수정하고 재검증합니다. 새 API 등 구버전 비호환 근거와 별도 명시적 사용자 승인이 있는 지원 정책 변경만 최소 상향을 허용합니다.

선언된 최소 지원과 현재 검증 HA가 원래 정확히 같으면 하나의 필수 job으로 검증합니다. 예전 최소 HA를 실제로 지원하는 통합만 requirements_test_min.txt·필요한 constraints와 별도 minimum-ha job을 추가하여 Python·requirements·expected-ha-version을 각각 지정합니다. 명시적 지원 정책 변경으로 옛 최소를 지원하지 않으면 관련 파일과 job을 함께 제거합니다. 라이브러리 하한이 있으면 dependency-modes/current·minimum 및 minimum-packages를 별도로 지정하며, 외부 Python 의존성이 없으면 minimum 라이브러리 job과 updater를 만들지 않습니다.

`.github/dependabot.yml`은 현재 HA·플러그인을 묶고, 과거 최소 환경이 존재할 때만 그 파일을 자동 갱신에서 제외하는 예시입니다. 제외 경로를 실제 구조에 맞춥니다. 묶인 PR도 workflow의 expected-ha-version·Python·관련 constraints를 자동 갱신하지 않으므로 함께 검토하고 동기화합니다. 기본 브랜치보다 낮아진 제안은 거부합니다. 구버전 비호환 근거와 별도 명시적 승인을 받아 최소 상향을 결정한 경우에만 hacs.json과 README·지원 정책 기록도 함께 맞춥니다. 공통 workflow는 과거 caller 호환을 위해 unit 기본값을 유지하므로 통합은 ha를 명시합니다. pytest-args 생략 시 ha는 tests/components/<domain>/ -v를 사용합니다.

[실제 HA 테스트 구조](../../docs/testing.md), [의존성 선언·추가 규칙](../../docs/dependencies.md), [Bluetooth 문서 작성 규칙](../../docs/bluetooth-documentation.md)을 채택 기준으로 사용합니다.

채택 점검에는 [체크리스트 사용법](../../docs/checklist.md)과 [ADOPTION_CHECKLIST.md](ADOPTION_CHECKLIST.md)를 사용합니다. 모든 항목은 미확인에서 시작하며 실제 적용한 통합의 증거로 채웁니다.

사용자는 해당 리포 세션에서 “hass-repo-standards 공통 규칙 적용해줘”라고 요청하고, 필요하면 중앙 checkout 경로나 리포 URL을 지정합니다. 에이전트는 적용 작업 때 중앙 [AGENTS.md](../../AGENTS.md)를 직접 읽고 위임·검증·중앙 보고 순서를 따릅니다. 중앙 지침을 통합에 설치할 필요가 없으며 과거 체크리스트의 PASS는 이후 변경을 검증한 결과가 아닙니다.

## blesession 기기별 문제 해결

blesession 사용 통합은 [영어 기기별 템플릿](docs/troubleshooting.md)과 [한국어 기기별 템플릿](docs/troubleshooting.ko.md)을 대상의 같은 경로에 적용합니다. `{{...}}`는 실제 기기 정보 또는 근거 있는 N/A로 교체하고 기존 기기별 안내를 보존하세요. 템플릿을 그대로 복사한 상태는 검사에 실패합니다. 고정 H2 순서와 증상/실패 단계/확인 사항/조치 표를 유지하고 실제 진단·로거만 적습니다. 마지막 절은 기존 Issues/이슈 템플릿을 재사용하며 새 양식을 만들지 않습니다.

공통 원본은 blesession의 [영어 프록시 안내](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md)·[한국어 프록시 안내](https://github.com/eigger/blesession/blob/main/docs/bluetooth.ko.md)·[영어 문제 해결](https://github.com/eigger/blesession/blob/main/docs/troubleshooting.md)·[한국어 문제 해결](https://github.com/eigger/blesession/blob/main/docs/troubleshooting.ko.md)입니다. 각 README는 같은 언어의 프록시 안내와 로컬 문제 해결로 연결하고, 로컬 문제 해결은 같은 언어의 README·공통 문제 해결·다른 언어판으로 연결합니다. README 세부 구조와 기존 본문·고지를 재작성하지 마세요.

공용 Validate는 blesession의 실제 requirement 이름(extras·연산자·marker 포함, marker 비활성이라도 대상) 또는 절대 import를 읽어 적용 여부를 판단합니다. 문서 존재·고정 구조·필수 링크·미입력 표시를 검사하며 실제 진단 의미·하드웨어·번역·원격 Issues 상태는 별도 독립 리뷰가 필요합니다. 읽기만을 위해 라이브러리 설치를 요구하지 않으며 blesession 미사용 통합에 고정 템플릿 자동 검사를 강제하지 않습니다.

공통 문서 이관 공개 순서는 blesession의 새 양언어 원본을 먼저 반영·검증한 뒤 중앙 이전 안내와 새 템플릿 규칙을 반영하는 순서입니다. 로컬 문서 작성만으로 원격 원본이 공개되었다고 보고하지 않습니다. 현재 작업은 commit/push 권한을 자동 부여하지 않으며 다른 리포를 자동 수정하지 않습니다.

로컬 중앙 검사기는 대상 통합의 Python 문법과 같거나 더 최신인 Python으로 실행합니다. standalone standards job은 현재 예제 통합의 Python 3.14 문법을 파싱하도록 Python 3.14를 사용합니다. 이 값은 검사 도구 실행 환경이며 통합의 지원 최소 HA/Python이나 최소 검증 환경을 올리지 않습니다. 중앙 도구 자체의 Python 3.9 단위 테스트 호환성과 대상 파일을 파싱할 수 있는 버전은 구분합니다.
