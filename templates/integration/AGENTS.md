# 공통 규칙 참조

이 리포의 STANDARDS.md에 지정한 hass-repo-standards 참조 커밋과 예외를 먼저 읽습니다.
원문: https://github.com/eigger/hass-repo-standards/tree/main
로컬에 중앙 리포가 없으면 해당 커밋의 docs를 읽고 작업합니다. URL을 적는 것만으로 자동 상속되지 않습니다.

- domain, 기본 브랜치, 지원 HA와 dependency 버전은 실제 메타데이터를 확인합니다.
- 배지 관리 주석 밖의 내용과 기존 언어·이전 안내를 보존합니다.
- 통합 테스트는 tests/components/<domain>/ 구조와 실제 HA fixture·config entry·플랫폼 로딩을 사용합니다. 가짜 HA 모듈로 대체하지 않으며 외부 통신 경계만 mock합니다.
- 의존성은 manifest의 requirements/dependencies/after_dependencies와 테스트 requirements를 구분하고 실제 HA 환경에서 설치·동작을 검증합니다.
- 통합 동작 변경에는 해당 회귀 테스트를 실행합니다.
- blesession/proxy 통합의 README는 공통 Bluetooth 설정·추천 기기로 연결하고 기기 고유 조건을 적습니다.
- manifest dependency 변경 시 연산자·extras·marker와 최소 버전 계약을 유지합니다.
