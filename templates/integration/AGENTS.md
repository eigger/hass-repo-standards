# 공통 규칙 참조

이 리포의 STANDARDS.md에 지정한 hass-repo-standards 버전과 예외를 먼저 읽습니다.
원문: https://github.com/eigger/hass-repo-standards/tree/v0.1.0
로컬에 중앙 리포가 없으면 해당 버전의 docs를 읽고 작업합니다. URL을 적는 것만으로 자동 상속되지 않습니다.

- domain, 기본 브랜치, 지원 HA와 dependency 버전은 실제 메타데이터를 확인합니다.
- 배지 관리 주석 밖의 내용과 기존 언어·이전 안내를 보존합니다.
- 통합 동작 변경에는 해당 회귀 테스트를 실행합니다.
- manifest dependency 변경 시 연산자·extras·marker와 최소 버전 계약을 유지합니다.
