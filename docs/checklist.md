# 통합별 적용 체크리스트

중앙에는 작성 기준과 [템플릿](../templates/integration/ADOPTION_CHECKLIST.md)만 둡니다. 실제 점검 결과는 각 통합의 `ADOPTION_CHECKLIST.md`, 기준·예외는 `STANDARDS.md`, 중앙에는 [적용 현황](adoption-status.md)의 요약과 링크만 관리합니다. 체크리스트는 기존 규칙의 확인 기록이며 새 의무나 공식 HA 품질 등급이 아닙니다.

## 작성 순서

1. 실제 원격·기본 브랜치·domain·대상 커밋과 기존 지원 최소를 확인합니다. 최소 HA와 current HA, 각 Python·테스트 플러그인·라이브러리 조합을 구분합니다.
2. `STANDARDS.md`에 검토한 full SHA를 기록합니다. immutable release를 채택하면 exact `vX.Y.Z`와 원격에서 확인한 resolved full SHA를 `.hass-standards.json`의 descriptor와 일치시킵니다.
3. 첫 채택은 전체 적용 항목을 점검합니다. 후속 변경은 영향 있는 항목만 갱신하고 기존 증거를 연결합니다. 점검표를 채우기 위해 없는 기능을 만들지 않습니다.
4. [GOV-01](adoption.md#중앙-템플릿과-예외)에 따라 예외의 사유·범위·승인 근거·담당자·재검토 조건을 기록합니다. 리뷰 방식은 [GOV-05](adoption.md#채택), 중앙 갱신 시점은 GOV-04를 따릅니다.

## 상태와 판정

| 상태 | 의미와 필요한 근거 |
|---|---|
| `TODO` | 미확인·미구현·검증 실패. 현재 상황과 남은 작업을 구분해 기록 |
| `PASS` | 대상 커밋에 필요한 검증을 수행하고 통과. 파일·명령·결과 또는 CI 링크 연결 |
| `EXCEPTION` | 적용 대상의 미충족을 승인된 범위로 관리. STANDARDS의 해당 예외 연결 |
| `N/A` | 기능·의존성 등 적용 조건에 해당하지 않는 구체적인 이유 기록 |

기본값은 `TODO`입니다. 미실행·실패를 PASS나 N/A로 바꾸지 않습니다. 묶인 규칙의 결과가 다르면 행을 나눕니다. 필수 항목이 모두 PASS 또는 근거 있는 N/A이고 실제 기본 브랜치 반영·해당 커밋 검증이 확인돼야 완료입니다. 필수 EXCEPTION이 남으면 예외 포함, 필수 TODO가 남으면 진행 중입니다. 권장 미채택은 필수 미충족과 구분합니다.

## 검증 근거

- 대상 커밋·명령·실행 환경·실제 설치 버전·결과·CI 링크를 한 번 기록하고 연결합니다. 다른 커밋의 PASS를 재사용하지 않습니다.
- 최소 HA와 최소 라이브러리는 별도 축입니다. 실제 HA fixture·entry·플랫폼·상태·action 테스트와 `pip check`를 확인합니다. 설치 summary나 coverage만으로 동작 검증을 대체하지 않습니다.
- 지원 최소 변경에는 비호환 근거와 별도 명시적 승인이 필요합니다. skip·제외·HACS ignore·기기/UI 미검증도 남깁니다.
- `scripts/check_integration.py`와 중앙 템플릿 diff를 확인합니다. 자동 검사는 번역 의미·기존 본문 보존·실제 제품 용도·승인 근거·HA 동작 검토를 대체하지 않습니다.

분야별 세부 조건은 원문에서 관리합니다: [테스트·호환성](testing.md), [CI](ci.md), [의존성](dependencies.md), [README·배지 DOC-03/05/06](documentation.md), [Bluetooth DOC-07](bluetooth-documentation.md), [payload DOC-08](payload-documentation.md), [제품 categories HA-02](home-assistant.md#통합-제품-카테고리-ha-02). DOC-08의 marker·정확한 하한·production 실행·전체 액션 YAML 검증, HA-02의 제품 근거·제외 유형 키 생략 등 필수 조건은 해당 원문과 템플릿을 따릅니다.
