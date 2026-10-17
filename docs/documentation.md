# README와 배지 규칙

**DOC-01 필수**: 메인 README는 제목 → 배지 → 한 문단 소개 → 핵심 지원 기기/기능 → 최소 요구사항 → 빠른 설치·필수 설정 → 짧은 대표 예제 → 중요 제한사항 → 문서 목록 → 지원·라이선스 순서의 간결한 시작 페이지로 작성합니다. 짧은 통합은 절을 합쳐도 필요한 정보는 찾을 수 있어야 합니다. 상세 옵션, 긴 YAML, 전체 엔티티 참조, 프로토콜, 오류별 대응, 개발·테스트 명령은 `docs/`·`examples/`·CONTRIBUTING으로 분리하고 메인에서 연결합니다. [BLE ESL README](https://github.com/eigger/hass-ble-esl/blob/main/README.md)의 빠른 시작·세부 문서 연결 방식을 참고하되 그 README의 모든 표·옵션을 복제하지 않습니다. 중요 제한·안전·미검증 고지는 메인에도 짧게 유지하며 기존 내용을 삭제하지 않고 상세 문서로 옮깁니다. 같은 설명을 여러 곳에 반복하기보다 원본으로 연결합니다. 개발·참여 안내는 문서 목록에서 실제 개발/테스트 안내로 연결합니다. 지원에는 버그 보고용 Issues, 질문·기능 제안용 활성 Discussions를 구분하고 라이선스에는 실제 LICENSE 파일 링크를 제공합니다. 원격 설정에서 Issues·Discussions의 활성 여부와 실제 주소를 확인한 뒤 유효한 링크만 넣습니다. 기능이 꺼져 있으면 설정을 임의 활성화하지 않고 실제 사용 가능한 대체 지원 경로를 명시합니다.

**DOC-02 필수**: 기본 `README.md`는 영어로 작성하고 한국어판 `README.ko.md`를 함께 제공합니다. 두 파일에 상호 언어 전환 링크와 같은 배지 정책을 적용합니다. 기존 한국어 본문·설정·이전 안내를 한국어판에 보존하고 영어판에 같은 정보를 제공합니다. 개발 규칙과 상세 docs는 한국어를 유지할 수 있습니다. 검증되지 않은 지원 모델·테스트 개수·호환성을 주장하지 않습니다. YAML 예시는 실제 action/schema와 맞추고 secrets는 예시 값으로 씁니다.

**DOC-03 필수**: 배지는 제목 아래, 왼쪽 정렬, `style=flat-square`로 둡니다. 순서는 HACS → Release → HA minimum → Tests → Validate → License → Usage입니다. 조건이 성립하지 않는 항목만 생략하며(HA 통합의 Usage는 항상 포함), 관리 주석 밖의 소개·이전 안내는 보존합니다.

| 배지 | 데이터와 표시 조건 | 클릭 대상 |
|---|---|---|
| HACS | Custom 기본. Default는 확인 근거가 있어야 함 | 설치 절 |
| Release | 실제 정식 Release 확인 후 `github/v/release`, prerelease 제외 | releases |
| HA minimum | hacs.json.homeassistant, `HA ≥ 버전` 표기 | hacs.json |
| Tests / Validate | 해당 caller workflow 파일이 존재할 때 | 해당 workflow |
| License | 실제 LICENSE가 있을 때 | 상대 경로 LICENSE |
| Usage | 모든 HA 통합에 실제 manifest domain으로 동적 배지를 미리 생성. 집계 존재 사전 확인 불필요 | HA Analytics |

**DOC-04 필수**: Tests는 CI 상태를 사용합니다. 수동 `124 Passed` 같은 상수 배지는 금지합니다. CI branch는 실제 기본 브랜치를 지정하며 폴더명을 원격 리포 이름으로 가정하지 않습니다. Release 없는 리포는 배포 버전을 추측하지 않습니다.

**DOC-05 필수**: Usage는 사용자가 데이터 제공에 동의한 HA Analytics 참여 설치 집계입니다. 데이터 제공의 opt-in과 배지 추가 여부를 혼동하지 않습니다. 모든 HA 통합에 동적 Usage 배지를 미리 넣어 집계가 제공되면 표시되도록 합니다. HTTP 403·미집계·조회 실패를 이유로 배지를 생략하지 않으며, 이를 설치 수 0으로 표시하거나 해석하지 않습니다. 전체 설치 수·사람 수로 표현하지 않습니다. GitHub downloads는 release asset 집계이므로 공통 배지에서 제외합니다. HA 통합이 아닌 리포는 manifest domain이 없으므로 Usage는 N/A입니다. 이전된 리포는 이전 안내와 상태를 우선합니다.

## 개발·Bluetooth 공통 문서

**DOC-06 필수**: README에는 HACS 커스텀 통합임을 명확히 쓰고 Core와 유사한 구조라는 이유로 공식 Core 포함·품질 등급을 주장하지 않습니다. 개발 안내에는 [Core 대응 구조](home-assistant.md), [실제 HA 테스트 구조](testing.md), [의존성 추가 절차](dependencies.md)를 반영합니다. 개발 환경·실제 테스트 명령과 검증 환경 표는 CONTRIBUTING 또는 `docs/development.md`에 두고 README의 짧은 문서 목록에서 연결합니다. 상세 사용·설정·엔티티·문제 해결은 해당 docs로 분리하며 영문·한국어 README 모두에서 문서 경로가 유효해야 합니다. 상세 문서 언어가 한국어인 경우 링크에 언어를 표시합니다. 검증한 HA/Python/pytest 플러그인 조합과 미검증 범위를 기록합니다.

**DOC-07 필수**: blesession을 사용하거나 Bluetooth proxy 경로를 지원하는 통합은 [Bluetooth 문서 작성 규칙](bluetooth-documentation.md)에 따라 사용자 안내와 개발자 지시를 분리합니다. 기본 사용자 안내는 영어 [Bluetooth proxy setup](bluetooth.md), 한국어 대응판은 [Bluetooth proxy 설정](bluetooth.ko.md)이며 상호 언어 링크를 제공합니다. 각 README는 해당 언어의 **사용자용** 기기 선택·펌웨어 설치·HA 등록·연결 확인·문제 해결 문서로 연결합니다. 작성 규칙, blesession 계약·채택/구현 가이드를 일반 사용자의 설정 안내로 연결하지 않습니다. README에는 핵심 준비 조건과 짧은 링크만 두고, 자세한 설명은 추가 문서로 분리합니다.

`docs/troubleshooting.md` 등에 통합별 문제 해결을 작성하거나 [공통 사용자 문제 해결](bluetooth.md#troubleshooting)로 연결하면서 모델 고유 깨우기·전원·페어링·본딩·인증·타 앱 연결·전송 제약과 실제 진단 경로를 함께 제공합니다. 한국어판은 [한국어 문제 해결](bluetooth.ko.md#troubleshooting)로 연결합니다. proxy 설정·추천 기기/리비전·active 스캔과 GATT 연결의 차이·민감 정보 제거 후 제보 절차를 찾을 수 있어야 합니다. 실제 제공하지 않는 옵션·진단 기능을 주장하거나 BLE ESL의 재시도·Debounce 등을 모든 통합의 기능으로 복사하지 않습니다. 실제 검증 경로와 미검증 범위를 구분하고 다른 통합의 실물 검증을 자기 통합의 결과로 주장하지 않습니다.

공통 설정을 직접 적을 때의 원본·확인일 관리, 공식 구매/지원 근거 확인과 라이브러리 계약 검토는 **작성자의 작업**으로 유지합니다. 사용자 문서 본문에 이런 작성 지시나 채택 절차를 섞지 않습니다. 규칙의 세부 조건은 [작성 규칙](bluetooth-documentation.md)을 따릅니다.

## 배지 도구

`scripts/sync_badges.py`는 네트워크 없이 manifest/hacs/workflow/origin을 읽습니다. `.hass-standards.json`의 `repository`와 `default_branch`가 없으면 Git origin과 origin/HEAD에서 읽으며 모르면 실패합니다. 다른 언어판은 `readmes` 배열에 명시합니다. 관리 구역이 없으면 내용을 변경하지 않고 실패하므로 채택 PR에서 제목 아래에 다음 두 줄을 먼저 추가합니다.

```markdown
<!-- hass-standards:badges:start -->
<!-- hass-standards:badges:end -->
```

```bash
python3 scripts/sync_badges.py ../hass-example --check
python3 scripts/sync_badges.py ../hass-example --write
```

`--check`는 불일치 시 exit 1, `--write`는 관리 영역만 갱신합니다. `release: true`와 `hacs: default`는 운영자가 원격 근거를 확인한 뒤 명시합니다. 스크립트는 원격 Release·목록 존재 여부를 검증하지 않으며 `hacs: default`에는 `hacs_default_evidence`(URL·확인일)가 필요합니다. Usage는 실제 manifest domain으로 항상 생성하고 원격 조회나 `analytics_evidence`가 필요하지 않습니다. 오래된 설정의 `analytics: false`도 Usage를 생략하지 않으며 두 analytics 설정 키는 제거합니다. 이 도구는 단일 HA manifest가 있는 통합용이며 비통합 리포에는 실행하지 않습니다.

영어·한국어 README를 `readmes`에 함께 나열합니다(`README.md`, `README.ko.md`). 설치 앵커는 `installation_links`에 `{"README.md": "#installation", "README.ko.md": "#설치"}`로 지정합니다. 두 파일은 각각 상대 언어 파일로 연결하고 같은 기능·제한·설치 안내를 유지합니다. 저장소 파일 링크는 각 README 위치 기준으로 계산합니다. 예시 설정은 templates/integration/.hass-standards.json에 있습니다.

[Analytics 근거](https://www.home-assistant.io/integrations/analytics), [Release 배지 옵션](https://shields.io/badges/git-hub-release).
