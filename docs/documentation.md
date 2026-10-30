# README와 배지 규칙

**DOC-01 필수**: README 공통 영역은 [중앙 영어 템플릿](../templates/integration/README.md)·[한국어 템플릿](../templates/integration/README.ko.md)의 문구·순서·줄바꿈·관리 주석을 의무 적용합니다. 상단은 왼쪽 정렬 프로젝트명 → 한 줄 소개 → 언어 링크 → 배지, 하단은 지원 → 관련 프로젝트(대상이 있을 때) → 라이선스입니다. 공통 영역 밖의 섹션 순서·제목·본문·예제·세부 구성은 각 리포에 맡기며 그대로 보존합니다. 간결화·문체 통일·공통 적용을 이유로 전면 재작성하거나 긴 YAML·참조·개발 명령을 다른 문서로 이동하지 않습니다. 번역 누락·깨진 링크·실제 동작과 다른 설명은 근거를 확인해 수정하되, 본문 재구성은 이유와 변경안을 제시하고 사용자 승인 후 적용합니다.

기존 공통 영역의 내용은 보존해 합치고 중복 영역을 만들지 않습니다. 지원은 제목 다음 빈 줄과 항목별 한 줄의 Markdown 목록을 사용합니다. Issues는 버그 신고·기능 요청, Discussions는 질문·사용 경험 공유로 연결합니다. 원격 설정·주소를 확인하고 비활성 Discussions 항목은 생략하며 임의 활성화하지 않습니다. Issues도 비활성인 경우 실제 대체 지원 경로를 확인하고 중앙 템플릿 개선 또는 승인 예외로 처리합니다. 관련 프로젝트는 기존에 명시했거나 실제 참고·사용한 대상만 링크와 짧은 관계 설명으로 적고, 없으면 제목과 목록을 생략합니다. 라이선스는 마지막에 실제 이름과 LICENSE 파일 링크를 한 문장으로 표시하고 기존 저작권·출처·추가 고지를 보존합니다. 강제 줄바꿈용 `<br>`·줄 끝 공백을 추가하지 않습니다.

공통 영역은 `hass-standards:header`, `support`, `related-projects`, `license`의 `start`/`end` 관리 주석으로 감쌉니다. 선택 영역이 비어도 경계 주석은 유지합니다. 기존 `hass-standards:badges` 주석은 header 안에 중첩합니다. 최초 적용은 기존 내용을 보존하며 경계를 지정하고, 이후 도구는 관리 영역 안만 수정합니다. 이전·안전 고지도 보존합니다. 중앙 템플릿을 임의 변형하지 않으며 불가피한 차이는 [승인 절차](adoption.md#중앙-템플릿과-예외)를 먼저 따릅니다.

**DOC-02 필수**: 기본 `README.md`는 영어, `README.ko.md`는 한국어이며 상호 언어 링크를 제공합니다. 두 문서는 같은 구조·내용을 번역으로 유지합니다. 기존 본문·설정·이전 안내를 보존하고 누락된 번역을 보완합니다. 언어 일치를 이유로 본문을 삭제·요약·임의 재구성하지 않습니다. CI는 공통 구조·링크·배지·누락 여부를 검사하며, 담당자는 양언어 전체 내용을 대조해 번역 의미·정보 누락·임의 삭제 여부를 확인합니다. 독립 리뷰 필요 여부는 GOV-05를 따릅니다. 상세 docs는 한국어를 유지할 수 있습니다. 검증되지 않은 지원 모델·테스트 개수·호환성을 주장하지 않습니다. YAML 예시는 실제 action/schema와 맞추고 secrets는 예시 값으로 씁니다.

**DOC-03 필수**: 배지는 header의 언어 링크 다음, 왼쪽 정렬, `style=flat`입니다. 공통 순서는 Release → HACS → HA minimum → Tests → Validate → License → Downloads(Default 또는 ZIP 배포) → Usage(ZIP 미배포 Custom)입니다. Downloads와 Usage 중 조건에 맞는 하나만 마지막 공통 배지로 표시하며, 기존 고유 배지가 있으면 공통 배지 뒤에 보존합니다. 조건이 성립하지 않는 항목만 생략합니다(HA 통합은 HACS 상태에 맞는 집계 배지를 항상 포함).

| 배지 | 데이터와 표시 조건 | 클릭 대상 |
|---|---|---|
| Release | 실제 정식 Release 확인 후 `github/v/release`, prerelease 제외 | releases |
| HACS | Custom 기본. Default는 확인 근거가 있어야 함 | 설치 절 |
| HA minimum | hacs.json.homeassistant, `HA ≥ 버전` 표기 | hacs.json |
| Tests / Validate | 해당 caller workflow 파일이 존재할 때 | 해당 workflow |
| License | 실제 LICENSE가 있을 때 | 상대 경로 LICENSE |
| Downloads | 확인된 Default 통합 또는 zip_release:true인 Custom 통합. 실제 owner/repository의 `github/downloads/owner/repository/latest/total` | releases |
| Usage | ZIP 미배포 Custom 통합에 실제 manifest domain으로 동적 배지를 미리 생성. 사전 조회 불필요 | HA Analytics |

**DOC-04 필수**: Tests는 CI 상태를 사용합니다. 수동 `124 Passed` 같은 상수 배지는 금지합니다. CI branch는 실제 기본 브랜치를 지정하며 폴더명을 원격 리포 이름으로 가정하지 않습니다. Release 없는 리포는 배포 버전을 추측하지 않습니다.

**DOC-05 필수**: Usage는 사용자가 데이터 제공에 동의한 HA Analytics 참여 설치 집계입니다. 데이터 제공의 opt-in과 배지 추가 여부를 혼동하지 않습니다. ZIP 미배포 Custom 통합에는 동적 Usage 배지를 미리 넣어 집계가 제공되면 표시되도록 합니다. HTTP 403·미집계·조회 실패를 이유로 배지를 생략하지 않으며, 이를 설치 수 0으로 표시하거나 해석하지 않습니다. 전체 설치 수·사람 수로 표현하지 않습니다. Default 통합과 ZIP 배포 Custom 통합은 Shields의 `https://img.shields.io/github/downloads/{owner}/{repository}/latest/total`을 **Downloads**로 표시하고 실제 저장소의 releases로 연결합니다. ZIP 배포 Custom의 기존 Analytics Usage는 제거하고 Downloads로 교체합니다. 이 값은 현재 정식 릴리스(prerelease 제외)의 첨부 asset 다운로드 합계로 새 릴리스마다 다시 집계되며 HACS 경유 다운로드만 구분하지 않습니다. 활성 설치 수·고유 사용자 수로 표현하거나 HACS Downloads로 이름 붙이지 않습니다. GitHub가 자동 제공하는 Source code ZIP/tarball·clone·개별 소스 파일 다운로드는 집계 대상이 아닙니다. HACS 설치가 집계되려면 통합 ZIP을 릴리스 asset으로 배포하고 `hacs.json`의 `zip_release: true`와 `filename`으로 HACS가 해당 asset을 사용하도록 구성해야 합니다. 배지 도구는 배포 방식이나 workflow를 자동 변경하지 않습니다. ZIP asset이 없는 기존 통합의 설치 이력은 이 배지로 복원할 수 없으며, asset 다운로드 0이나 조회 실패를 0 설치로 해석하거나 고정값으로 덮어쓰지 않습니다. HA 통합이 아닌 리포는 manifest domain이 없으므로 Usage는 N/A입니다. 이전된 리포는 이전 안내와 상태를 우선합니다.

## HACS 설치 링크

**DOC-06 필수**의 설치 안내로 양언어 README의 기존 설치 절에 공식 [My Home Assistant HACS 저장소 배지](https://my.home-assistant.io/create-link/?redirect=hacs_repository)를 제공합니다. Default·Custom 모두 실제 저장소의 `owner`와 저장소 이름 `repository`를 사용하며 Custom은 `category=integration`을 포함합니다. `repository`에 전체 GitHub URL을 넣지 않습니다. 이 링크는 HACS의 저장소 화면을 열며 HACS 사전 설치와 사용자의 다운로드·재시작 등 기존 설치 절차를 대체하지 않습니다.

배지 이미지는 `https://my.home-assistant.io/badges/hacs_repository.svg`, 링크는 `https://my.home-assistant.io/redirect/hacs_repository/?owner=eigger&repository=hass-example&category=integration` 형태입니다. Markdown을 중앙 형식으로 사용하며 HTML도 수동 문서 예제로는 가능하지만 자동 관리 블록은 중앙 Markdown과 일치해야 합니다. 설치 배지는 상단 통계 배지의 flat 규칙 대상이 아닙니다.

`hass-standards:installation:start`/`end` 블록은 설치 배지만 소유합니다. 기존 설치 제목·본문·예제를 보존하고 배지 블록을 해당 절에 추가합니다. 중앙 README 렌더러는 `installation_links`의 로컬 앵커와 일치하는 기존 제목 바로 아래에 블록을 추가합니다. 설정이 없으면 표준 `## Installation`/`## 설치`를 사용하며 설치 절도 없을 때만 지원 영역 앞에 새 절을 추가합니다. 기존 다른 설치 제목을 쓰는 리포는 제목을 바꾸거나 중복 절을 만들지 말고 실제 앵커를 설정하거나 최초 적용 때 해당 절에 배지 관리 주석을 직접 지정합니다. 설정한 앵커가 없거나 중복·위치가 잘못된 경우 기존 본문을 변경하지 않고 실패합니다. 기존 관리 블록은 내용만 갱신합니다. `sync_badges.py`는 상단 배지만 변경하며 설치 블록은 `check_integration.py --write-readmes` 또는 계획/apply로 갱신합니다.

## 개발·Bluetooth 공통 문서

**DOC-06 필수**: README에는 HACS 커스텀 통합임을 명확히 쓰고 Core와 유사한 구조라는 이유로 공식 Core 포함·품질 등급을 주장하지 않습니다. 개발 안내에는 [Core 대응 구조](home-assistant.md), [실제 HA 테스트 구조](testing.md), [의존성 추가 절차](dependencies.md)를 반영합니다. 개발 환경·실제 테스트 명령과 검증 환경 표를 제공하고 양언어 README에서 찾을 수 있게 연결합니다. 본문·상세 문서 배치는 리포가 결정하며 기존 내용을 공통 적용 때문에 이동하지 않습니다. 양언어 README에서 문서 경로가 유효해야 합니다. 상세 문서 언어가 한국어인 경우 링크에 언어를 표시합니다. 검증한 HA/Python/pytest 플러그인 조합과 미검증 범위를 기록합니다.

**DOC-07 필수**: blesession 사용 통합은 [작성 규칙](bluetooth-documentation.md)과 중앙 [영어](../templates/integration/docs/troubleshooting.md)·[한국어](../templates/integration/docs/troubleshooting.ko.md) 기기별 템플릿을 의무 적용해 `docs/troubleshooting.md`와 `docs/troubleshooting.ko.md`를 제공합니다. 고정 H2 제목·순서, 증상/실패 단계/확인 사항/조치 표, 실제 진단·로그 안내, 기존 Issues/이슈 템플릿 연결을 유지합니다. 전원·깨우기·페어링·인증·타 앱·전송 조건은 실제 기기에 맞게 적고 기능이 없거나 해당 없으면 이유를 밝힙니다. 미검증을 검증 완료로 쓰거나 빈 템플릿·TODO·가짜 기능을 통과시키지 않습니다. 기존 기기 안내와 README 본문·고지는 보존하고 새 제보 양식·이슈 템플릿을 만들지 않습니다.

공통 프록시 추천·설정·HA 등록·일반 문제 해결의 원본은 blesession의 [영어 프록시 안내](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md)·[한국어 프록시 안내](https://github.com/eigger/blesession/blob/main/docs/bluetooth.ko.md), [영어 문제 해결](https://github.com/eigger/blesession/blob/main/docs/troubleshooting.md)·[한국어 문제 해결](https://github.com/eigger/blesession/blob/main/docs/troubleshooting.ko.md)입니다. 중앙은 작성 규칙·기기별 템플릿·검사를 관리하며 공통 사용자 본문을 중복 유지하지 않습니다. blesession 미사용 통합도 일반 프록시 안내를 읽을 수 있으며 문서를 읽기 위해 라이브러리 설치를 요구하지 않습니다. Bluetooth proxy 지원 통합은 같은 원본을 사용자 안내로 연결하고 기기 고유 조건을 보완합니다.

blesession 사용 통합의 양언어 README는 각각 같은 언어의 로컬 문제 해결과 공통 프록시 안내로 연결합니다. 로컬 문서도 같은 언어의 README·다른 언어판·공통 문제 해결로 연결합니다. 작성자 규칙·라이브러리 계약을 사용자 설정 안내로 연결하지 않습니다. 오류 단계, 실제 진단 키와 로거, 광고 수신 경로와 확인된 연결 경로 구분, 복구 순서는 실제 라이브러리와 통합 구현을 확인해 적습니다. BLE ESL 전용 센서·재시도·Debounce·timeout을 모든 통합에 복제하지 않습니다.

공통 원본의 확인일 관리, 공식 구매/지원 근거 확인과 라이브러리 계약 검토는 **작성자의 작업**으로 유지합니다. 사용자 문서 본문에 이런 작성 지시나 채택 절차를 섞지 않습니다. 규칙의 세부 조건은 [작성 규칙](bluetooth-documentation.md)을 따릅니다.

## imagespec payload 사용자 안내

**DOC-08 필수**: imagespec 사용 통합은 [작성 규칙](payload-documentation.md)과 중앙 [영어](../templates/integration/docs/payload.md)·[한국어](../templates/integration/docs/payload.ko.md) 템플릿을 적용해 `docs/payload.md`·`docs/payload.ko.md`를 제공합니다. 고정 여섯 H2는 공통 payload 안내 → 이 통합에서 payload 사용 → 최소 동작 예제 → 기기 출력 설정 → 지원 기능과 제한 → 문제 해결이며 영어 대응 제목·순서도 중앙 템플릿을 따릅니다. 하위 H3로 모델별 설명을 보완할 수 있습니다. 실제 액션·대상·전체 YAML·출력 크기/색상/회전·제약을 쓰고 기존 README 본문·기기 예제는 보존합니다. 공통 문법·요소·속성·색상·회전·디더링 원본은 imagespec의 [영어 안내](https://github.com/eigger/imagespec/blob/main/docs/payload.md)·[한국어 안내](https://github.com/eigger/imagespec/blob/main/docs/payload.ko.md)이며 중앙이나 각 통합에서 전체 공통 매뉴얼을 중복 유지하지 않습니다.

양언어 README는 같은 언어의 로컬 payload 안내로 연결하며 로컬 문서는 같은 언어 README·다른 언어판·공통 원본으로 연결합니다. 예제는 `examples/payload/*.yaml`의 실제 전체 HA 액션 파일이며 라이브러리의 bare 요소 목록을 기기 액션으로 오인하지 않습니다. 문서에서 연결한 모든 로컬 액션 YAML을 `.hass-standards.json`의 `payload.examples`에 실제 payload 위치·기대 출력 크기·모델 색상과 함께 등록합니다. 해당 통합에 없는 템플릿·폰트·history·extras·액션·기능은 만들지 않으며 해당 없음의 이유를 명시합니다. 문제 해결은 기존 안내·Issues·이슈 템플릿으로 연결하고 별도 제보 양식을 만들지 않습니다.

공용 Validate는 대상·문서·고정 구조·링크·메타데이터·중앙 테스트 scaffold를 검사합니다. 공용 HA Tests는 실제 설치된 imagespec의 current 및 선언된 정확한 하한에서, 실제 HA fixture·등록된 액션 스키마·통합의 실제 준비/렌더링 경로와 중앙 pytest 계약으로 모든 예제를 검증합니다. 일반 구조 검사나 caller의 자체 PASS 선언으로 실행을 대체하지 않습니다. 외부 전송 경계만 mock하며 기기 명령을 실행하지 않고, resolver 완료 뒤 검증 편의를 위해 패키지를 덮어 설치하지 않습니다. 정확한 단일 pin은 실제 설치 버전이 같을 때만 current 결과를 재사용할 수 있습니다. 지원 최소 HA·Python·라이브러리는 임의 상향하지 않습니다. 실제 미지원 API·환경 제약은 미검증/실패로 기록하고 중앙 템플릿 수정 또는 명시적 승인 예외 절차를 따릅니다.

원본 공개는 imagespec 문서를 실제 기본 브랜치에 먼저 반영해 URL을 검증한 뒤 중앙 규칙을 공개하는 순서입니다. 로컬 초안은 원격 공개·CI 성공·실물 검증의 근거가 아닙니다.

## 배지 도구

`scripts/sync_badges.py`는 네트워크 없이 manifest/hacs/workflow/origin을 읽습니다. `.hass-standards.json`의 `repository`와 `default_branch`가 없으면 Git origin과 origin/HEAD에서 읽으며 모르면 실패합니다. 다른 언어판은 `readmes` 배열에 명시합니다. 관리 구역이 없으면 내용을 변경하지 않고 실패하므로 채택 PR에서 header 안의 언어 링크 다음에 다음 두 줄을 먼저 추가합니다.

```markdown
<!-- hass-standards:badges:start -->
<!-- hass-standards:badges:end -->
```

```bash
python3 scripts/sync_badges.py ../hass-example --check
python3 scripts/sync_badges.py ../hass-example --write
```

`--check`는 불일치 시 exit 1, `--write`는 관리 영역만 갱신합니다. `release: true`와 `hacs: default`는 운영자가 원격 근거를 확인한 뒤 명시합니다. 스크립트는 원격 Release·목록 존재 여부를 검증하지 않으며 `hacs: default`에는 `hacs_default_evidence`(URL·확인일)가 필요합니다. ZIP 미배포 Custom의 Usage는 실제 manifest domain으로 항상 생성하고 원격 조회나 `analytics_evidence`가 필요하지 않습니다. Default 또는 ZIP 배포 Custom은 Downloads를 생성하고, ZIP 배포 Custom의 기존 Usage는 제거합니다. 이전 HACS Downloads 배지는 `--write` 시 교체하며 고유 배지와 관리 영역 밖 본문은 보존합니다. 오래된 설정의 `analytics: false`도 ZIP 미배포 Custom의 Usage를 생략하지 않으며 두 analytics 설정 키는 제거합니다. 이 도구는 단일 HA manifest가 있는 통합용이며 비통합 리포에는 실행하지 않습니다.

영어·한국어 README를 `readmes`에 함께 나열합니다(`README.md`, `README.ko.md`). 설치 앵커는 `installation_links`에 `{"README.md": "#installation", "README.ko.md": "#설치"}`로 지정합니다. 두 파일은 각각 상대 언어 파일로 연결하고 같은 기능·제한·설치 안내를 유지합니다. 저장소 파일 링크는 각 README 위치 기준으로 계산합니다. 예시 설정은 templates/integration/.hass-standards.json에 있습니다.

[Analytics 근거](https://www.home-assistant.io/integrations/analytics), [Release 배지 옵션](https://shields.io/badges/git-hub-release).

## 중앙 템플릿 검사

`python3 scripts/check_integration.py ../hass-example`은 README 공통 영역·테스트 구조·공용 CI 형식을 검사하며 불일치 시 실패합니다. `--write-readmes`는 이미 지정된 README 관리 영역만 갱신합니다. `.hass-standards.json`의 `readme`에는 실제 프로젝트명·양언어 소개·지원 기능 활성 여부·라이선스·기존 고지·관련 프로젝트를 명시합니다. 최초 쓰기 전 기존 공통 내용·고지를 설정으로 옮겨 검토하고, 미등록 내용으로 도구가 중단하면 삭제·우회하지 말고 보존 방법을 확인합니다. 검토 없이 기본값으로 기존 고지를 덮어쓰지 않습니다. [템플릿 사용법](../templates/integration/USAGE.md)을 따르며, 번역 의미·실제 HA 동작·원격 기능 상태의 사실 확인은 CI만으로 대체하지 않습니다.
