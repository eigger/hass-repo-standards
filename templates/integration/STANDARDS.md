# 적용한 공통 규칙

- 표준: https://github.com/eigger/hass-repo-standards/tree/main
- 참조 커밋 SHA: 채택 시 검토한 main의 전체 SHA 입력
- Standards release: 채택 시 검토한 exact release 입력
- Resolved standards SHA: 채택 시 검토한 main의 전체 SHA 입력
- 채택일: 실제 채택 PR 날짜 입력
- profile: integration / ha (실제 HA fixture·통합 로딩 필수)
- 적용 점검표: [ADOPTION_CHECKLIST.md](ADOPTION_CHECKLIST.md)
- 중앙 현황표: https://github.com/eigger/hass-repo-standards/blob/main/docs/adoption-status.md
- 구현·검증 담당 / 자체·독립 리뷰 방식·선택 근거: GOV-05에 따라 기록
- 중앙 현황 갱신일: 미등록
- 실제 기본 브랜치: 채택 시 입력
- 테스트 경로: tests/components/<domain>/
- 변경 전 지원 최소 HA / 선언 근거: hacs.json·manifest·README 실제 값과 불일치 기록
- 적용 후 지원 최소 HA: 기본은 기존 값 보존; 상향 시 비호환 근거·별도 명시적 사용자 승인 기록
- current HA 테스트 환경: 실제 HA/Python/pytest-homeassistant-custom-component 조합 입력
- 최소 HA 검증 환경: HA/Python/플러그인 버전 또는 미검증 사유
- 최소 package 검증: 해당 package와 버전
- imagespec DOC-08 해당 여부 / 예제 계약 검증: 실제 requirement/import·payload.examples·환경별 검증 근거 또는 N/A
- imagespec 공용 Tests/updater standards-ref: release의 resolved SHA (구형 SHA 채택은 reusable workflow SHA)

## 예외

| 규칙 ID / 검사 예외 ID | 대상 경로·허용 범위 | 이유·영향·대안 | 승인자·일자·실제 승인 근거 | 담당자 | 재검토 조건 |
|---|---|---|---|---|---|

예외가 없으면 '없음'으로 명시합니다. 이 템플릿의 미입력 항목을 완료로 표시하지 않습니다.

중앙 README 공통 영역·테스트 기본 파일·공용 CI는 의무 템플릿입니다. 임의 차이는 먼저 중앙 템플릿 수정·검증 또는 사용자 명시적 승인을 거친 뒤 적용합니다. 승인 요청은 에이전트가 수행하며 CI는 기록을 검사할 뿐 승인 대기 절차를 갖지 않습니다. 자동 검사 예외는 `.hass-standards.json`의 `exceptions`에 위 승인 근거·허용 범위를 연결합니다. 기존 승인 범위 내라면 재승인하지 않으며 새 기준과 충돌해 기존 승인으로 판단할 수 없는 경우만 확인합니다.
