# 문서 구조

이 리포의 상세 규칙은 한국어로 관리합니다. 메인 README는 리포별 동적 상태와 빠른 진입점만 제공하고, 아래 문서에서 필요한 범위를 선택합니다.

## 통합 채택

| 문서 | 용도 |
|---|---|
| [적용과 변경 관리](adoption.md) | 필수/권장 규칙, 예외, 기준 릴리즈와 채택 절차 |
| [중앙 적용 현황](adoption-status.md) | 리포별 진행 상태와 남은 작업 |
| [통합별 적용 체크리스트](checklist.md) | PASS/TODO/예외와 검증 증거 기록 |
| [통합 템플릿 사용 안내](../templates/integration/USAGE.md) | 템플릿·workflow·환경 입력 적용 |

## 구현과 검증 규칙

| 문서 | 용도 |
|---|---|
| [Home Assistant 개발](home-assistant.md) | 구조, config entry, async, 엔티티, 제품 categories |
| [테스트와 호환성](testing.md) | 실제 HA fixture·로딩, current/minimum 검증 |
| [CI 작성 규칙](ci.md) | 공용 workflow, 권한, 이벤트, timeout |
| [의존성 관리](dependencies.md) | manifest, 테스트 환경, updater, 지원 하한 |
| [HACS와 배포](hacs.md) | manifest, hacs.json, ZIP/릴리스 배포 |
| [README와 배지](documentation.md) | 양언어 README, 관리 영역, 설치·배지 |
| [Bluetooth 문서 작성 규칙](bluetooth-documentation.md) | DOC-07과 blesession 사용자 안내 연결 |
| [Payload 문서 작성 규칙](payload-documentation.md) | DOC-08과 imagespec 실행 계약 |
| [릴리스·유지보수](releases.md) | 통합 유지보수와 중앙 immutable release 절차 |

## 도구와 템플릿

| 문서 | 용도 |
|---|---|
| [템플릿·스킬 사용 안내](template-skill-usage.md) | inspect·plan·apply·recover와 스킬 사용 |
| [템플릿·스킬 구조 개편 구현안](template-skill-plan.md) | T1~T6 설계 배경 |
| [템플릿·스킬 구현 검증](template-skill-validation.md) | T1~T6 역사적 검증 근거 |
| [개발·검사 안내](development.ko.md) | 로컬 설정, 테스트, 검사 명령 |

## 현황과 근거

| 문서 | 용도 |
|---|---|
| [리포별 배포·관심 현황](repository-stats.ko.md) | 동적 릴리스·다운로드·스타·포크와 집계 기준 |
| [공식 자료](sources.md) | 공식 요구사항의 원문과 확인일 |

공통 Bluetooth proxy 사용자 안내와 문제 해결은 [blesession](https://github.com/eigger/blesession/tree/main/docs)에서, imagespec의 공통 payload 안내는 [imagespec](https://github.com/eigger/imagespec/tree/main/docs)에서 관리합니다.
