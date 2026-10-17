# README와 배지 규칙

**DOC-01 필수**: 메인 README는 제목 → 배지 → 한 문단 소개 → 지원 기기/기능 → 요구사항 → 설치 → 설정 → 사용 예시 → 제한/문제 해결 → 지원/라이선스 순서를 기본으로 합니다. 짧은 통합은 절을 합쳐도 되지만 설치·요구사항·제한사항은 찾을 수 있어야 합니다.

**DOC-02 필수**: 메인 언어는 기존 리포의 한국어/영어를 유지합니다. 번역 README가 있으면 언어 전환 링크와 같은 배지 정책을 적용합니다. 검증되지 않은 지원 모델·테스트 개수·호환성을 주장하지 않습니다. YAML 예시는 실제 action/schema와 맞추고 secrets는 예시 값으로 씁니다.

**DOC-03 필수**: 배지는 제목 아래, 왼쪽 정렬, `style=flat-square`로 둡니다. 순서는 HACS → Release → HA minimum → Tests → Validate → License → Usage입니다. 없는 항목만 생략하며 관리 주석 밖의 소개·이전 안내는 보존합니다.

| 배지 | 데이터와 표시 조건 | 클릭 대상 |
|---|---|---|
| HACS | Custom 기본. Default는 확인 근거가 있어야 함 | 설치 절 |
| Release | 실제 정식 Release 확인 후 `github/v/release`, prerelease 제외 | releases |
| HA minimum | hacs.json.homeassistant, `HA ≥ 버전` 표기 | hacs.json |
| Tests / Validate | 해당 caller workflow 파일이 존재할 때 | 해당 workflow |
| License | 실제 LICENSE가 있을 때 | 상대 경로 LICENSE |
| Usage | analytics에 manifest domain이 존재함을 확인한 뒤 선택 | HA Analytics |

**DOC-04 필수**: Tests는 CI 상태를 사용합니다. 수동 `124 Passed` 같은 상수 배지는 금지합니다. CI branch는 실제 기본 브랜치를 지정하며 폴더명을 원격 리포 이름으로 가정하지 않습니다. Release 없는 리포는 배포 버전을 추측하지 않습니다.

**DOC-05 필수**: Usage는 opt-in Analytics 집계입니다. 전체 설치 수·사람 수로 표현하지 않습니다. GitHub downloads는 release asset 집계이므로 공통 배지에서 제외합니다. Analytics는 누락/저빈도 데이터 정책 때문에 처음부터 전 리포에 강제하지 않습니다. 이전된 리포는 이전 안내와 상태를 우선합니다.

## 개발·Bluetooth 공통 문서

**DOC-06 필수**: README에는 HACS 커스텀 통합임을 명확히 쓰고 Core와 유사한 구조라는 이유로 공식 Core 포함·품질 등급을 주장하지 않습니다. 개발 안내에는 [Core 대응 구조](home-assistant.md), [실제 HA 테스트 구조](testing.md), [의존성 추가 절차](dependencies.md)를 반영합니다. 긴 개발 환경·테스트 명령은 CONTRIBUTING 또는 docs/development.md에 두고 README에서 연결할 수 있습니다. 검증한 HA/Python/pytest 플러그인 조합과 미검증 범위를 기록합니다.

**DOC-07 필수**: blesession을 사용하거나 Bluetooth proxy 경로를 지원하는 통합은 README의 요구사항·설치·Bluetooth 설정 절에서 [공통 Bluetooth 문서](bluetooth.md)로 연결하거나 같은 설정 내용을 직접 제공합니다. proxy 설정, 추천 기기와 보드 리비전, active 연결/스캔의 차이, 공통 문제 해결 경로를 찾을 수 있어야 합니다. 직접 적는 경우 공통 원본 링크와 확인일을 함께 관리합니다. 구매 관련 안내는 공식 지원 자료로 확인하고 다른 통합에서 검증한 모델이라는 이유로 자기 통합의 실물 검증을 주장하지 않습니다.

공통 안내와 별도로 기기별 깨우기·페어링·본딩·인증·타 앱 연결 해제·전송 제약을 적습니다. BLE ESL의 재시도·Debounce 같은 기기별 옵션을 모든 blesession 통합에 강제하지 않습니다. 공통 문서에는 특정 통합의 옵션과 프록시 펌웨어 설정을 구분해 작성합니다.

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

`--check`는 불일치 시 exit 1, `--write`는 관리 영역만 갱신합니다. `release: true`, `hacs: default`, `analytics: true`는 운영자가 원격 근거를 확인한 뒤 명시합니다. 스크립트는 원격 Release·목록·Analytics 존재 여부를 검증하지 않습니다. 예시 설정은 templates/integration/.hass-standards.json에 있습니다.

[Analytics 근거](https://www.home-assistant.io/integrations/analytics), [Release 배지 옵션](https://shields.io/badges/git-hub-release).
