# Repository instructions

Home Assistant 커스텀 통합의 공통 규칙·템플릿·도구·CI를 관리합니다.

## 실행 원칙

- 첫 채택은 README·[채택 절차](docs/adoption.md)·[체크리스트](docs/checklist.md)와 적용 규칙을 확인합니다. 후속 작업은 기준 SHA·예외·변경 영향과 관련 절만 읽고, 같은 세션에서 바뀌지 않은 문서는 다시 읽지 않습니다. 규칙 ID·필수/권장 수준과 [공식 근거](docs/sources.md)를 유지합니다.
- 실제 원격·브랜치·domain·지원 최소·의존성을 확인하고 사용자 변경·기존 구현·본문·회귀 테스트를 보존합니다. 지원 최소 상향은 비호환 근거와 별도 명시적 사용자 승인이 필요합니다.
- 공통 형식은 중앙 계약·템플릿에서 생성하고 같은 렌더러로 검사합니다. 기존 리포는 변경 계획을 먼저 만들고 관리 범위만 적용합니다. 예외는 [GOV-01](docs/adoption.md#중앙-템플릿과-예외)을 따릅니다.
- 주 에이전트가 구현·검증하는 것을 기본으로 하며 독립 리뷰 조건·위임 범위는 [GOV-05](docs/adoption.md#채택)를 따릅니다.
- 다른 리포 수정·workflow 수동 실행·commit/push·PR·스킬 설치는 사용자 요청 범위를 따릅니다. 이 리포에는 태그·GitHub Release를 만들지 않습니다. 중앙 AGENTS나 그 내용을 대상의 에이전트 진입 파일로 설치하지 않고 고유 지침을 보존합니다.
- 미실행·실패·예외를 PASS로 기록하지 않습니다. 대상 커밋·명령·실제 설치 버전·결과·CI·미검증 범위를 한 번 기록해 연결합니다. 현황 갱신은 [GOV-04](docs/adoption.md#채택), 완료 판정은 [체크리스트](docs/checklist.md)를 따릅니다.

## 작업별 원본

해당 작업에 필요한 원문만 확인합니다.

| 작업 | 원본 |
|---|---|
| 통합 생성·채택 | [사용 안내](docs/template-skill-usage.md), [템플릿](templates/integration/USAGE.md) |
| 구현·테스트 | [HA 구조·제품 categories](docs/home-assistant.md), [실제 HA fixture·로딩·최소/current 검증](docs/testing.md) |
| README·배지 | [양언어·관리 영역·본문 보존](docs/documentation.md) |
| CI·의존성 | [공용 CI](docs/ci.md), [선언·지원 환경](docs/dependencies.md) |
| Bluetooth·blesession | [DOC-07](docs/bluetooth-documentation.md) |
| imagespec | [DOC-08](docs/payload-documentation.md) |

T1~T6 [작업지시서](docs/template-skill-tasks.md)와 [설계](docs/template-skill-plan.md)는 중앙 도구 최초 구현의 계약·배경입니다. 일반 통합 적용이나 후속 부분 수정에 전 단계를 재실행하지 않습니다.

## 검증

변경한 동작의 단위 테스트와 `python3 scripts/check_repository.py`를 실행합니다. action/workflow 변경 시 actionlint·해당 fixture 검사도 실행합니다. 통합의 첫 채택·후속 변경별 범위와 증거 공유 조건은 [채택 절차](docs/adoption.md#필요한-문서와-검증-범위), 명령은 [개발 안내](docs/development.md)를 따릅니다.
