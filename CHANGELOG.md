# Changelog

## 2026-10-17 — hass-kibble 파일럿 지원

- hass-kibble 첫 적용을 등록하고 hass-cyx-rgb-led·hass-divoom은 사용자 요청으로 제외합니다. 적용 대상 HA 통합은 22개입니다.
- 공통 HA 환경에서 실제 테스트 플러그인 설치·버전을 확인하고, 생략한 pytest 경로는 domain 구조로 결정합니다. 기존 unit caller는 유지합니다.
- 실행용 템플릿에 정확한 최소/현재 HA별 Python·requirements·버전 검사와 실제 HA 테스트 경로를 반영합니다. 예시 버전은 각 통합의 실제 지원 범위에 맞춰 변경해야 합니다.


## 2026-10-17 — Bluetooth 추천 기기 정리

- Olimex 추천을 제거하고 XIAO W5500 V1.2를 기본 추천으로, USB-A 동글 형태의 M5Stack AtomS3U를 추가하고 구매 링크를 병기.
- AtomS3U는 ESPHome 공식 목록 대상이 아님을 밝히고, 기존 설정의 `ble.disable`·`esp32_improv`를 삭제하고 합치도록 안내.
- M5Stack 제품 문서를 docs/sources.md에 추가.

## 2026-10-17 — 중앙 적용 현황과 에이전트 진입 지침

- GitHub 목록 기준 통합 25개와 다른 유형 4개의 중앙 적용 현황표 추가. 실제 적용 실적은 미착수로 시작하고 archive·중복·원격 확인 대상을 구분.
- 작업 시작·단계 변경·종료 때 중앙 표의 자기 리포 행을 갱신하도록 GOV-04 및 로컬/중앙 AGENTS 지침 정의.
- 공통 지침을 읽고 별도 세부 지시 없이 점검·적용·검증·보고하는 시작 절차 추가.
- 구현과 독립 리뷰·검증을 별도 서브 에이전트에게 위임하도록 GOV-05에 명시.
- 체크리스트·STANDARDS·README를 중앙 현황과 연결. 기존 통합의 코드·CI·AGENTS는 변경하지 않음.

## 2026-10-17 — 통합별 적용 체크리스트

- 기존 공통 규칙 ID에 대응하는 적용 체크리스트 사용법과 복사용 템플릿 추가.
- 미확인·적용·예외·해당 없음의 구분, 파일·CI·버전 조합 증거와 예외 재검토 기준 정의.
- README, 채택 안내, STANDARDS 및 에이전트 안내에서 점검표로 연결.
- 개별 통합의 적용 상태는 자동 판정하거나 완료 처리하지 않음.

## 2026-10-17 — Core 대응 구조와 실제 HA 테스트 규칙

- HACS 배포 차이를 제외하고 Core와 유사한 구현·테스트 구조로 작성하도록 명시.
- tests/components/<domain>/ 배치와 실제 HA fixture·config entry·플랫폼 로딩 검증을 필수로 정의.
- HA 코어 stub 금지, 외부 통신 경계 mock 허용 범위와 최소 버전 검증 기준 구체화.
- 패키지·HA 구성요소·테스트 도구의 의존성 선언 위치와 추가 절차 정의.
- Bluetooth proxy 설정·추천 기기 공통 문서 작성 및 해당 통합 README의 직접 안내/링크 규칙 추가.
- 이번 변경은 공통 규칙 문서에 한정. 실행용 템플릿·CI 구현·개별 통합 전환은 이후 작업.

## 2026-10-17 — 관리 방식 정리

- 규칙 리포는 태그·GitHub Release 없이 main과 커밋 이력으로 관리.
- 문서·템플릿은 main을 참조하고, 실제 채택 시 검토한 커밋 SHA로 고정하도록 정리.
- 기존에 생성한 두 태그 정리. 개별 HA 통합의 릴리스 규칙은 유지.

## 2026-10-17 — 리뷰 수정

- 현재 환경에서 marker가 비활성인 선택 의존성은 검증 없이 갱신하지 않고 실패하도록 수정.
- 성공적으로 변경 없음이 확인될 때도 기존 dependency PR과 branch를 동기화·정리하도록 수정.
- Python/운영체제 marker 및 yanked 제안의 회귀 테스트 추가.
- 수정된 updater action의 commit SHA로 중앙 workflow 참조 갱신.

## 2026-10-17 — 초기 작성

- HA·HACS·문서·배지·테스트·CI·의존성·릴리스 규칙 초안 확정.
- hass* 전체 로컬 CI 조사와 profile별 이관 계획 작성.
- HACS/Hassfest, Python test matrix, imagespec/blesession 등 manifest updater 재사용 workflow 제공.
- 최소 패키지 검사, 환경 설치 composite action, 배지 도구와 호출 템플릿 제공.
- 기존 통합 리포의 수정·workflow 호출·bot PR 생성은 포함하지 않음.
