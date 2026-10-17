# Changelog

## 0.1.1 — 2026-10-17

- 현재 환경에서 marker가 비활성인 선택 의존성은 검증 없이 갱신하지 않고 실패하도록 수정.
- 성공적으로 변경 없음이 확인될 때도 기존 dependency PR과 branch를 동기화·정리하도록 수정.
- Python/운영체제 marker 및 yanked 제안의 회귀 테스트 추가.
- 수정된 updater action의 commit SHA로 중앙 workflow 참조 갱신. 기존 v0.1.0 태그는 유지.

## 0.1.0 — 2026-10-17

- HA·HACS·문서·배지·테스트·CI·의존성·릴리스 규칙 초안 확정.
- hass* 전체 로컬 CI 조사와 profile별 이관 계획 작성.
- HACS/Hassfest, Python test matrix, imagespec/blesession 등 manifest updater 재사용 workflow 제공.
- 최소 패키지 검사, 환경 설치 composite action, 배지 도구와 호출 템플릿 제공.
- 기존 통합 리포의 수정·workflow 호출·bot PR 생성은 포함하지 않음.
