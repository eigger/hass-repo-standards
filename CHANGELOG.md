# Changelog

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
