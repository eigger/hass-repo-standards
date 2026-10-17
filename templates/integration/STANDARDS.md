# 적용한 공통 규칙

- 표준: https://github.com/eigger/hass-repo-standards/tree/main
- 참조 커밋 SHA: 채택 시 검토한 main의 전체 SHA 입력
- 채택일: 실제 채택 PR 날짜 입력
- profile: integration / ha (실제 HA fixture·통합 로딩 필수)
- 적용 점검표: [ADOPTION_CHECKLIST.md](ADOPTION_CHECKLIST.md)
- 중앙 현황표: https://github.com/eigger/hass-repo-standards/blob/main/docs/adoption-status.md
- 조율 / 구현 / 독립 리뷰·검증 담당: 작업 시작 시 배정
- 중앙 현황 갱신일: 미등록
- 실제 기본 브랜치: 채택 시 입력
- 테스트 경로: tests/components/<domain>/
- 변경 전 지원 최소 HA / 선언 근거: hacs.json·manifest·README 실제 값과 불일치 기록
- 적용 후 지원 최소 HA: 기본은 기존 값 보존; 상향 시 비호환 근거·별도 명시적 사용자 승인 기록
- current HA 테스트 환경: 실제 HA/Python/pytest-homeassistant-custom-component 조합 입력
- 최소 HA 검증 환경: HA/Python/플러그인 버전 또는 미검증 사유
- 최소 package 검증: 해당 package와 버전

## 예외

| 규칙 ID | 이유 | 담당자 | 재검토 조건 |
|---|---|---|---|

예외가 없으면 '없음'으로 명시합니다. 이 템플릿의 미입력 항목을 완료로 표시하지 않습니다.
