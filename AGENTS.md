# Repository instructions

Home Assistant 커스텀 통합의 공통 규칙·템플릿·도구·CI를 관리합니다.

## 공통 실행 원칙

- 변경 전에 README와 해당 규칙 원문을 확인하고 규칙 ID·필수/권장 수준을 유지합니다. 공식 요구사항의 근거는 [sources](docs/sources.md)에서 확인합니다.
- 실제 원격·기본 브랜치·domain·버전·의존성을 읽습니다. 사용자 변경·기존 구현·문서 본문·회귀 테스트·지원 범위를 보존합니다.
- 다른 리포 수정·workflow 수동 실행·commit/push·PR은 사용자 요청 범위와 리포 정책을 따릅니다. 이 리포에는 태그·GitHub Release를 만들지 않습니다.
- 미실행·실패·예외를 PASS로 기록하지 않습니다. 검증 증거는 대상 커밋·명령·실제 설치 버전·결과·CI 링크로 남깁니다.
- manifest categories는 [HA-02](docs/home-assistant.md#통합-제품-카테고리-ha-02)에 따라 실제 제품·용도의 근거로 선택합니다. 엔티티 플랫폼에서 추정하거나 공통 기본값을 넣지 않으며 entity/system/virtual은 키를 생략합니다. HACS 누락 경고와 중앙 필수 정책을 구분합니다.
- 최신 테스트 환경과 지원 최소를 분리합니다. 최소 상향은 실제 비호환 근거와 별도 명시적 사용자 승인 후에만 하며, 기존 최소와 current가 다르면 각각 검증합니다.
- README·테스트·공용 CI는 중앙 원본을 사용합니다. 예외는 [GOV-01과 승인 절차](docs/adoption.md#중앙-템플릿과-예외)를 따르며 CI에 승인 대기를 넣지 않습니다.

## 템플릿·스킬 구조 개편

[구현 작업지시서](docs/template-skill-tasks.md)의 T1 → T6 순서로 파일·동작·테스트를 구현하고 각 완료 조건의 실행 결과를 기록합니다. [설계](docs/template-skill-plan.md)는 계약 배경이며 작업지시서는 실제 구현 단위입니다. 미구현 단계의 도구·스킬이나 예정 CLI를 실행했다고 보고하지 않습니다.

공통 형식을 에이전트가 매번 새로 작성하게 하지 않습니다. 중앙 계약·템플릿에서 생성하고 같은 렌더러로 검사하도록 구현합니다. 기존 리포는 변경 계획을 먼저 만들고 관리 범위만 적용합니다.

## 통합 채택·재검토

1. 중앙 README·[채택 절차](docs/adoption.md)·[체크리스트](docs/checklist.md), 대상 STANDARDS의 기준 SHA·예외를 확인합니다. 첫 채택은 실제 중앙 main full SHA를 검토·기록하고 기준 변경은 영향을 기록합니다.
2. 원격·브랜치·작업 트리, manifest·hacs.json·README의 지원 선언, 최소/current HA와 각 Python·테스트 플러그인 조합을 기록합니다. 같은 작업 범위를 다시 확인받지 않고 실제 메타데이터로 진행합니다.
3. [템플릿 사용법](templates/integration/USAGE.md)에 따라 STANDARDS·ADOPTION_CHECKLIST를 작성하고 필요한 수정·검증·미완료 항목을 기록합니다. 검사에 맞추려고 없는 기능을 만들지 않습니다.
4. 구현과 독립 리뷰·검증은 서로 다른 collaboration 서브 에이전트에게 위임합니다(GOV-05). 주 에이전트는 담당 파일·범위·완료 조건을 정하고 통합합니다. 같은 파일을 동시에 수정하지 않고 검증 환경·임시 경로를 분리합니다. 필수 지적 수정 후 영향 있는 검사를 독립 재실행합니다. 위임 불가·미검증은 그대로 보고합니다. 별도 사이드바 채팅 생성·메시지 전송 권한으로 해석하지 않습니다.
5. 시작·단계 변경·종료에 최신 중앙 main의 [현황표](docs/adoption-status.md#갱신-절차)에서 자기 리포 행만 갱신합니다. 기본 브랜치 반영·해당 커밋 검증 전에는 완료로 표시하지 않습니다. 중앙 갱신 불가 시 로컬 체크리스트와 최종 보고에 미반영 사유·내용을 남깁니다.
6. 변경·기준 SHA·실제 검증·커밋/PR·중앙 반영·남은 일을 보고합니다. 중앙 AGENTS나 그 내용을 대상의 에이전트 진입 파일로 설치하지 않고, 기존 리포 고유 지침은 보존합니다. 사용자 별도 요청 없이는 재설치하지 않습니다.

## 작업별 계약

아래 문서는 해당 작업의 필수 계약입니다. 형식·링크·검증 세부 사항은 원본 한 곳에서 관리합니다.

| 작업 | 적용할 원본·핵심 제약 |
|---|---|
| 구현·테스트 | [HA 구조](docs/home-assistant.md), [테스트](docs/testing.md): tests/components/domain, 실제 HA fixture·로딩, 외부 통신 경계만 mock |
| README·배지 | [문서](docs/documentation.md): 양언어·관리 영역·기존 본문 보존, Default는 HACS Downloads·Custom은 manifest domain의 동적 Usage, 양언어 설치 절의 My HACS 배지 |
| CI·의존성 | [CI](docs/ci.md), [의존성](docs/dependencies.md): caller checkout·github.action_path 유지, 선언 위치 구분, extras·연산자·marker 보존, 실패 은폐 금지 |
| Bluetooth·blesession | [DOC-07 작성 계약](docs/bluetooth-documentation.md): 같은 언어의 blesession 사용자 원본·로컬 문제 해결 연결, 실제 기기 조건 기록 |
| imagespec | [DOC-08 실행 계약](docs/payload-documentation.md): 양언어 문서·전체 액션 YAML·실제 production 경로·설치된 current/정확한 하한 검증, 기기 명령·검증 후 패키지 덮어 설치 금지 |

## 검증

변경한 동작의 단위 테스트와 `python3 scripts/check_repository.py`를 실행합니다. action/workflow 변경 시 actionlint·해당 fixture 검사도 실행합니다. 전체 명령은 [개발 안내](docs/development.md)에 있습니다. 환경 제약과 실패는 성공 결과와 구분해 보고합니다.
