# 공통 규칙 적용 체크리스트

이 파일은 통합 리포로 복사해 사용하는 **미확인 템플릿**입니다. 기존 통합·공통 CI가 전환됐다는 의미가 아닙니다. [사용법과 판정 기준](https://github.com/eigger/hass-repo-standards/blob/main/docs/checklist.md)을 읽고, 아래 규칙은 `STANDARDS.md`에 기록한 표준 커밋에서 확인합니다. 태그·릴리스 대신 `main`의 검토 커밋을 기준으로 하며, 위 사용법 링크의 `main`은 채택 시 검토한 커밋 SHA로 바꿉니다.

## 검토 대상

| 항목 | 값 |
|---|---|
| 통합 리포 / 실제 기본 브랜치 | 미확인 |
| domain / 구현 경로 | 미확인 |
| 검토 대상 통합 커밋 / 채택 PR | 미확인 |
| 검토한 표준 전체 커밋 SHA | 미확인 — `STANDARDS.md`와 일치시킬 것 |
| 검토일 / 조율 담당 | 미확인 |
| 구현 담당 / 자체·독립 리뷰 방식·선택 근거 | 미확인 |
| 중앙 현황표 반영일 / 기록 | 미등록 — 공통 리포 docs/adoption-status.md에 갱신 |
| 변경 전 지원 최소 HA / 근거 파일(hacs.json·manifest·README) | 미확인 — current 테스트 버전과 별도 기록 |
| 유지·변경할 지원 최소 / 변경 시 실제 비호환 근거·명시적 승인 | 미확인 — 최신화 요청만으로 상향하지 않음 |
| current 테스트 HA / 호환 Python·플러그인 | 미확인 |
| 최소 테스트 HA / 호환 Python·플러그인 | 미확인 — 선언 최소가 current와 다르면 별도 환경 |
| profile / 테스트 경로 | 미확인 — 통합 기준 `integration / ha`, `tests/components/<domain>/` |
| 이전 검토 기록 | 미확인 — 최초 검토이면 그 사실 기재 |
| 채택 판정 | 이관 진행 중 — 아직 확인하지 않음 |

상태: `TODO` = 미확인·미충족, `PASS` = 근거로 확인, `EXCEPTION` = 적용 대상의 기록된 예외, `N/A` = 적용 조건에 해당 없음. 모든 항목은 미확인으로 시작합니다. `TODO`를 해당 없음으로 처리하지 않습니다. 묶은 규칙의 결과가 다르면 행을 나눕니다. 권장 항목은 별도로 표시했으며 미채택 이유를 기록합니다.

## 채택·구조·사용자 데이터

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| GOV-01, GOV-02 | `STANDARDS.md`에 표준 SHA·profile·실제 기본 브랜치·예외 기록, workflow/action은 검토 SHA로 고정 | TODO | 미확인 |
| GOV-03 | 새 표준 채택 변경의 영향·이관 방법과 명시적 채택 PR 확인. 규칙 자체를 변경하면 공통 CHANGELOG 기록 | TODO | 미확인 |
| GOV-04 | 중앙 표에 작업 시작·종료·의미 있는 상태 변화 상태, 담당·적용 내용·검증/리뷰 근거 링크·남은 작업 갱신, 타 리포 기록 보존 | TODO | 미확인 |
| GOV-05 | 자체/독립 리뷰 방식·선택 근거 기록, 큰 구조·HA 동작·공용 CI 실행 로직 변경의 독립 리뷰, 지적 수정·영향 검사 재실행 | TODO | 미확인 |
| HA-01, HA-13 | `custom_components/<domain>/`와 domain 일치, 필요한 모듈·공개 API·생명주기는 Core 대응 구조 | TODO | 미확인 |
| HA-02 | manifest 필드·정렬·동작 선언, 실제 제품 categories 1–3개·주 분류 순서·공식 slug·선택 근거·categories_review 일치 또는 entity/system/virtual 키 생략 이유, 공식 품질 등급 자가 표기 없음 | TODO | 미확인 |
| HA-03 (권장) | 공통 상수·설정·갱신·플랫폼 역할 및 프로토콜 경계에 맞게 모듈 구성 | TODO | 미확인 |
| HA-04, HA-08 | UI 설정·중복·안정적 식별 및 기능별 options/reauth/reconfigure, entity 의미·registry 영향 확인 | TODO | 미확인 |
| HA-01, HA-04, HA-08, REL-01, REL-03 | domain·unique ID·entry schema·상태/통계 계약 변경 시 migration 테스트와 사용자 조치 안내 | TODO | 미확인 — 변경 유무부터 확인 |
| HA-05, HA-06 | setup 실패 구분, unload/reload·부분 실패의 task/listener/연결 정리, async·timeout·취소 처리 | TODO | 미확인 |
| HA-07 | 중복 polling·property I/O 방지, push 보존, unavailable/unknown·실패 후 복구 | TODO | 미확인 |
| HA-11, HA-12 | 번역·action/schema 일치, 로그/diagnostics/fixture 비식별화와 제공 시 redaction 테스트 | TODO | 미확인 |

## 실제 HA 테스트·호환성·의존성

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| TEST-08 | `tests/components/<domain>/`에 구현과 대응하는 테스트·domain fixture 배치, discovery·CI 경로 일치 | TODO | 미확인 |
| TEST-02, TEST-03, DEP-07 | 실제 HA·호환 플러그인과 `hass`/`enable_custom_integrations` fixture 사용, HA core stub/복사본/`--no-deps`로 대체하지 않음 | TODO | 미확인 |
| TEST-09 | 실제 loader·config entry manager로 setup/플랫폼 로딩, HA 상태·registry·service/action으로 결과 검증 | TODO | 미확인 |
| TEST-01, TEST-06, TEST-07 | 구현 기능별 성공·실패·중복·migration·unload·복구 회귀 검증, 외부 통신 경계만 mock, skip 사유 | TODO | 미확인 |
| TEST-04, HACS-01 | 변경 전 지원 최소·current·각 Python/플러그인 분리, 선언한 정확한 최소 검증, 상향 시 비호환 근거·명시적 승인 확인 | TODO | 미확인 |
| TEST-05, HA-10, DEP-02, DEP-05 | imagespec·blesession 등 최소/현재 라이브러리 별도 환경, 실제 HA 테스트·정확한 설치값·API 경계 검증 | TODO | 미확인 |
| DEP-01, DEP-06 | Python runtime은 manifest requirements, HA domain은 dependencies/after_dependencies, 테스트·린트 requirements는 별도 | TODO | 미확인 |
| DEP-07, CI-06 | 실제 사용하는 HA 구성요소의 requirements·필수 재귀 의존성·선택 로딩 경로 설치, resolver·`pip check` 통과 | TODO | 미확인 |
| DEP-02, DEP-03, DEP-08 | 의존성 추가/변경의 버전·extras·marker·선언 위치·지원 플랫폼·라이선스 검토, 실제 HA 테스트와 문서 갱신 | TODO | 미확인 — 이번 변경의 해당 여부 확인 |

독립 리뷰는 변경 전후 지원 최소와 current를 비교하고, 봇 PR이 과거 최소 requirements·constraints까지 갱신하거나 expected-ha-version·Python을 누락하지 않았는지 확인합니다. 최신 테스트 실패는 호환 수정 대상으로 처리합니다.

환경마다 아래 행을 복사합니다. 최소 HA와 최소 라이브러리 검증을 혼동하지 않고, marker가 활성인 환경에서 대상 패키지 설치값을 확인합니다. 실행하지 않은 조합은 `TODO` 또는 근거가 있는 `EXCEPTION`으로 남깁니다.

| 검증 축 / 상태 | 통합 커밋 | Python / HA / 플러그인 실제 버전 | 대상 패키지 실제 버전·extras·marker | 명령·테스트 결과·pip check / CI run·job | skip·제외·미검증 범위 |
|---|---|---|---|---|---|
| 현재 환경 / TODO | 미확인 | 미확인 | 미확인 | 미실행 | 미확인 |
| 정확한 최소 HA / TODO | 미확인 | 미확인 | 미확인 | 미실행 | 미확인 |
| 정확한 최소 라이브러리 / TODO | 미확인 | 미확인 | 미확인 | 미실행 | 미확인 |

## HACS·CI·의존성 업데이트

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| HACS-01, HACS-02 | 루트 README/LICENSE/hacs.json, 검증한 최소 HA, 실제 배포 구조와 필요한 옵션 일치 | TODO | 미확인 |
| HACS-03, HACS-05 | Default 여부는 목록 근거로 확인, [로컬 brand/icon.png 또는 원격 brands 근거](https://github.com/eigger/hass-repo-standards/blob/main/docs/hacs.md)와 HACS/Hassfest 실제 실행, ignore는 이유·해제 조건 기록 | TODO | 미확인 |
| HACS-06 (권장) | description·topics·issue 경로·brands 및 사용하는 HACS 필드 지원 확인 | TODO | 미확인 |
| CI-01, CI-02 | Validate/Tests 공통화, 확장 job 유지, 공용 파일명·표시 이름·PR 대상 제한 없는 기본 이벤트·실제 기본 브랜치 push·dispatch·기존 schedule, 전용 CI 명명 형식 | TODO | 미확인 |
| CI-03, CI-05, CI-08 | 최소 권한·checkout 자격증명 비보존·timeout·concurrency, full SHA·갱신 관리, 비신뢰 입력·secrets 경계 | TODO | 미확인 |
| CI-04, CI-07, CI-12 | 실패를 숨기지 않는 실제 `ha` 필수 테스트, 버전별 환경·cache·Ruff 설정과 required checks 이름 확인 | TODO | 미확인 |
| DEP-03, DEP-04, CI-09 | updater의 선택 package·연산자/extras/marker 보존, 안정 버전·major 정책, 실제 기본 브랜치·단일 bot branch·PR만 제안 | TODO | 미확인 |
| CI-09, CI-10, DEP-08 | 변경 tree의 새 하한·실제 HA 검증 후 PR 동기화, 실패 시 중단·변경 없음 시 기존 PR 정리, 후속 required checks 충족 방식 확인 | TODO | 미확인 |

## README·Bluetooth·유지보수

| 규칙 ID | 확인 항목 | 상태 | 근거 / 남은 작업 |
|---|---|---|---|
| DOC-01, DOC-02, DOC-06 | 중앙 header/support/related-projects/license 관리 영역의 정확한 형식, 기존 공통 내용·고지 보존, 영역 밖 순서·제목·본문 유지, 양언어 같은 구조·내용·상호 링크, 번역 의미·누락 리뷰(GOV-05), 실제 활성 지원 링크·실제 라이선스 | TODO | 미확인 |
| DOC-03, DOC-04, DOC-05 | 언어 링크 다음 중첩 배지 관리 블록, flat·Release/HACS/HA minimum/Tests/Validate/License/Downloads(Default) 또는 Usage(Custom) 순서·실제 조건·고유 배지 보존, 실제 기본 브랜치·상태별 필수 동적 집계 배지·양언어 설치 절의 실제 저장소 My HACS 배지·미집계와 0 설치 구분 | TODO | 미확인 |
| HA-09, HA-10 | BLE 사용 시 HA Bluetooth API·라이브러리 공개 경계, 지원한 proxy 경로·재연결·취소·서비스 변경 검증 | TODO | 미확인 |
| DOC-07 | blesession 사용 여부(manifest requirement extras·operator·marker/실제 import) 확인. 사용 통합은 중앙 양언어 docs/troubleshooting 템플릿의 고정 제목·순서·증상 표·실제 진단/로그·기존 Issues 연결, README와 로컬 문서의 언어별 상호/공통 blesession 원본 링크·placeholder 제거·공용 Validate 검사. 기존 본문/기기안내 보존, 새 제보 양식 금지. 프록시만 지원하면 기존 기기 조건·사용자 안내를 수동 확인 | TODO | 미확인 |
| DOC-08 | imagespec 사용 여부·양언어 docs/payload 여섯 절·언어별 README/공통 원본/상호 링크·실제 액션/대상/전체 YAML·기기 출력/지원/제한·기존 예제/본문 보존·기존 지원 연결, 모든 로컬 연결 예제의 payload.examples 등록·실제 경로/payload_format(list 또는 yaml)/크기/모델 색상 | TODO | 미확인 |
| DOC-08, TEST-02, TEST-05, TEST-09 | 정확한 중앙 test_payload_examples scaffold·실제 HA entry/등록 action schema·production 준비 context/함수·기기 전송 없는 installed imagespec.validate/render 비교·각 예제 크기/색상, current/정확한 하한 실제 버전·pip check·명령/CI 결과, exact pin 재사용 근거·adapter 리뷰(GOV-05) | TODO | 미확인 |
| DOC-08, CI-05, CI-07, DEP-08 | 공용 Tests/updater의 standards-ref와 reusable full SHA 일치·caller checkout 보존·도구 별도 checkout·resolver 후 패키지 변경 없음·지원 최소 보존·미실행/skip/xfail/deselect를 PASS로 처리하지 않음 | TODO | 미확인 |
| DOC-07, HA-12 | 기기별 깨우기·인증·타 앱 연결·전송 제약, 실제 검증 경로와 미검증 범위, 공개 문제 로그 비식별화 | TODO | 미확인 |
| HACS-04, REL-01, REL-02, REL-03, CI-11 | 통합 릴리스 시 같은 검증 commit/tag·manifest 버전·산출물·권한, 사용자 영향·지원 변경·제한 안내 | TODO | 미확인 — 규칙 리포에는 릴리스하지 않음 |
| REL-04 | 이전/중단 시 README 상단 경로·유지보수 상태·재등록 여부, 자동 이전으로 오인하지 않는 안내 | TODO | 미확인 |
| REL-05 (권장) | 의존성/HA API 변경과 기능 변경 분리, 표준 변경은 명시적 채택 PR로 반영 | TODO | 미확인 |

## 예외와 남은 작업

예외 원본은 `STANDARDS.md`입니다. 아래에 해당 위치를 연결하고, 예외가 실제 없음을 확인한 뒤에만 `없음`으로 바꿉니다.

| 규칙 ID | 예외 위치 / 이유 | 담당자 | 재검토 조건 |
|---|---|---|---|
| 미확인 | 미확인 | 미확인 | 미확인 |

| 규칙 ID / TODO | 남은 작업 / issue·PR | 담당자 | 완료 근거 |
|---|---|---|---|
| 미확인 | 미확인 | 미확인 | 미확인 |

최종 검토 시 적용 대상 필수 `TODO`와 `EXCEPTION`, 이유가 있는 `N/A`, 권장 미채택을 구분해 적습니다. CI 성공만으로 실물 기기 검증을 주장하지 않습니다. 실물 검증을 수행했다면 모델·펌웨어·어댑터/proxy·연결 경로와 결과를 별도로 기록합니다.

중앙 보고는 [적용 현황표](https://github.com/eigger/hass-repo-standards/blob/main/docs/adoption-status.md)의 자기 리포 행에 반영합니다. 리뷰 지적·수정·재검증 결과와 중앙 갱신 실패 사유가 있으면 남은 작업에도 기록합니다.

## 중앙 템플릿 검증

- `scripts/check_integration.py` 명령·결과·대상 커밋: 미확인
- 세 빈 init·정확한 루트 conftest·domain mock_config_entry/필요 시 mock_client·실제 HA 로딩·기존 회귀 범위 보존: 미확인
- 공통 fixture의 오류 무시·네트워크 일괄 허용·로딩 생략 금지, 개별 허용 범위·사유: 미확인
- 양언어 본문 보존·의미 일치·기존 고지·고유 배지 리뷰(자체/독립·GOV-05): 미확인
- 공용 CI 이름·파일명·기존 실행 조건과 전용 CI 명명 형식: 미확인
- 승인 예외 실제 사용자 근거·일자·경로·범위 및 설정과 STANDARDS.md 대조: 미확인

## imagespec payload 예제 검증 환경 — 해당 시

imagespec 미사용이면 실제 requirement/import 확인 근거와 N/A를 기록합니다. 사용 통합은 모든 등록 예제와 각 검증 환경을 기록하고, 이 표의 미확인 값을 PASS로 취급하지 않습니다.

| 환경 / 대상 커밋 | Python / 실제 HA / 플러그인 | 실제 imagespec / current·정확한 하한 근거 | 예제 경로 / 실제 HA schema·준비 경로 | 기대/실제 출력 크기·허용 색상 | pip check·명령·결과·CI 링크 |
|---|---|---|---|---|---|
| 미확인 | 미확인 | 미확인 | 미확인 | 미확인 | 미확인 |

- 중앙 계약 완료·등록 예제 전체 실행·skip/xfail/deselect 없음: 미확인
- adapter가 production 준비 함수를 호출하고 실제 context/정규화 payload를 쓰는 검토(자체/독립·GOV-05): 미확인
- 템플릿·폰트·이미지·history 실제 지원 context와 외부 통신만 mock한 근거: 미확인
- 공통 원본 실제 기본 브랜치 공개 URL 확인 / 중앙 규칙 반영 순서: 미확인

- DOC-08 matrix별 imagespec marker 활성/비활성 근거·비활성 N/A와 버전 coverage 없음·일반 HA 회귀 지속·다른 활성 환경의 current/정확한 하한 결과: 미확인
- YAML 문자열/목록 액션 입력과 실제 HA 스키마 정규화 후 payload_format 일치·기존 API 보존: 미확인

## HA-02 제품 분류 검토 근거

| 항목 | 실제 판단 / 근거 |
|---|---|
| manifest integration_type | TODO — 기존 선언 보존; 미선언이면 그 사실 기록 |
| categories (주 분류 먼저) | TODO — 실제 지원 제품·서비스 용도 근거로 1–3개; 제외 유형은 키 생략 |
| 주/보조 분류 선택 또는 제외 이유·출처 | TODO — 실제 제품·사용자 안내·검토자/일자; 플랫폼 이름에서 추정하지 않음 |
| categories_review와 manifest의 값/순서/유형 일치 | TODO — 과거 검토를 변경 후 결과로 재사용하지 않음 |
| taxonomy snapshot·HACS warning/실패·실제 실행 결과 | TODO — 중앙 오프라인 검사와 원격 HACS/HA 실행·의미 검토를 구분 |
