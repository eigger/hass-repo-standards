# 공통 규칙 적용 지침

사용자가 이 리포에 “공통 규칙 적용해줘”라고 요청하면 세부 지시를 다시 요구하지 않고 아래 진입 절차와 중앙 실행 지침에 따라 점검·구현·리뷰·검증·진행 기록을 수행합니다. 사용자의 명시적 범위·권한과 이 리포의 예외를 우선하며 기존 사용자 변경을 보존합니다.

1. `STANDARDS.md`의 전체 표준 SHA·예외·체크리스트를 확인합니다. 첫 채택이면 실제 중앙 `main` SHA를 조회해 검토하고 기록합니다. 기존 기준 변경은 영향과 이관 내용을 기록합니다.
2. [공통 AGENTS.md](https://github.com/eigger/hass-repo-standards/blob/main/AGENTS.md)와 [README](https://github.com/eigger/hass-repo-standards/blob/main/README.md)를 **실제로 읽고**, 공통 AGENTS의 “통합 리포에서 공통 규칙을 적용할 때” 절차를 실행합니다. 표준 구현 기준은 `STANDARDS.md`의 SHA에서 관련 `docs`를 읽습니다. 로컬 중앙 checkout이 없으면 해당 GitHub 파일을 읽습니다. **URL을 적는 것만으로 지침이 자동 상속되지 않습니다.**
3. [중앙 적용 현황](https://github.com/eigger/hass-repo-standards/blob/main/docs/adoption-status.md)은 고정된 기준 SHA와 별개로 최신 `main`을 읽습니다. 작업 시작·단계 변경·종료 때 본인 리포 행만 갱신하고 다른 세션 변경을 보존합니다. 중앙 미반영 시 이유와 반영할 내용을 로컬 체크리스트·최종 보고에 남깁니다. 강제 push하지 않습니다.
4. **구현은 서브 에이전트에, 리뷰·검증은 구현 담당과 별도의 독립 서브 에이전트에 반드시 위임합니다.** 주 에이전트는 조율·통합·최종 확인을 맡습니다. 담당별 리포·파일 범위를 나누고 같은 파일의 동시 수정을 피하며 검증 환경을 분리합니다. 필수 지적·실패는 수정 후 독립 재검증하고, 미해결이면 완료 처리하지 않습니다. 현재 작업의 collaboration 기능을 사용하며 새 사이드바 세션 생성·다른 채팅 메시지 전송을 뜻하지 않습니다.

실제 domain·브랜치·지원 HA·의존성은 메타데이터에서 확인합니다. Core에 대응하는 구조와 `tests/components/<domain>/`, 실제 HA fixture·config entry·플랫폼 로딩, 의존성 설치·최소 버전, 공통 CI와 기존 회귀 범위를 점검합니다. HA 코어 stub을 쓰지 않고 외부 통신만 mock합니다. README·배지는 관리 범위를 지키고 기존 언어·이전 안내를 보존하며, blesession/proxy 통합은 공통 Bluetooth 안내와 기기 고유 조건을 연결합니다. 의존성 연산자·extras·marker를 보존합니다.

실제 명령·환경·설치 버전·커밋·CI 결과를 `ADOPTION_CHECKLIST.md`에 기록하고 미검증을 통과로 표시하지 않습니다. 원격 push·PR은 사용자 지시와 리포 정책을 따르며 적용만을 이유로 태그·릴리스를 만들지 않습니다. 완료 여부와 예외는 중앙 표·체크리스트 기준을 따르고 마지막에 변경·검증·중앙 반영·남은 일을 보고합니다.
