# 적용과 변경 관리

## 범위와 우선순위

이 규칙의 주 대상은 `custom_components/<domain>`이 있는 hass 리포입니다. 카드·Android·YAML 설정·애드온에는 문서·CI 보안·버전 관리 원칙만 적용하며 HA 통합 전용 검사를 강제하지 않습니다.

- **공식**: 링크한 HA/HACS/GitHub 규격. 사용 API와 배포 방식에 적용됩니다.
- **필수**: 이 표준을 채택하는 리포의 프로젝트 정책입니다.
- **권장**: 통합 특성에 맞게 채택합니다.
- 충돌 시 사용자의 명시적 지시와 적용 가능한 공식 규격을 우선하고, 로컬 예외를 기록합니다.

## 채택

**GOV-01 필수**: `STANDARDS.md`에 참조한 표준 커밋 SHA, 적용 profile, 예외(ID·이유·담당자·재검토 조건)를 기록합니다. 예시는 templates/integration/STANDARDS.md입니다. 새 통합은 main의 규칙을 검토해 적용하고, 기존 통합은 결함을 숨기지 않은 채 단계적으로 이관합니다.

**GOV-02 필수**: 이 리포는 별도 태그·GitHub Release·SemVer 없이 main과 커밋 이력으로 관리합니다. 문서는 main에서 확인하며, 실제 채택 PR에서는 `git ls-remote https://github.com/eigger/hass-repo-standards.git refs/heads/main`으로 검토한 commit SHA를 확인해 STANDARDS.md에 기록합니다. 공통 workflow/action 호출은 그 SHA로 고정하여 중앙 변경이 모든 리포에 즉시 적용되지 않도록 합니다. 템플릿의 `@main`은 채택 시 SHA로 교체하는 예시입니다.

**GOV-03 필수**: 규칙 변경은 날짜와 변경 내용을 CHANGELOG에 기록합니다. 기존 채택 리포에 영향을 주는 변경은 영향·이관 방법을 설명하고 각 리포의 명시적 채택 PR로 반영합니다. 이 규칙 리포의 관리 방식과 개별 통합의 배포 버전·릴리스 정책은 별개입니다.

## 이관 순서

1. 현재 CI를 읽기 전용으로 조사하고 기본 브랜치·지원 HA·테스트 환경을 확인합니다.
2. 기존 회귀 테스트를 보존하며 Core 대응 구현과 tests/components/<domain>/ 배치, 실제 HA fixture·entry 로딩 검증으로 전환할 계획을 기록합니다.
3. 의존성 선언·HA 테스트 환경을 정리한 뒤 Validate와 실제 HA 기반 Python CI로 전환합니다. 필요한 브라우저·최소 HA job은 유지합니다.
4. 의존성 업데이트 bot은 dry-run으로 기존 변화와 비교하고 전환합니다.
5. README 배지와 AGENTS.md의 표준 참조를 추가하고, 해당하는 BLE 통합은 공통 Bluetooth 설정·추천 기기로 연결합니다.
6. 실제 원격 CI를 통과한 뒤 required checks 이름을 저장소 설정에 반영합니다.

`needs`/job 이름 변경으로 branch protection이 영구 대기하지 않도록 채택 PR에서 확인합니다. 이 표준 자체는 저장소 설정을 자동 변경하지 않습니다.

## 적용 체크리스트

각 통합을 채택·재검토할 때 [체크리스트 사용법](checklist.md)과 [복사용 템플릿](../templates/integration/ADOPTION_CHECKLIST.md)을 사용합니다. 대상 리포에 `ADOPTION_CHECKLIST.md`로 복사하고 `STANDARDS.md`에서 연결합니다. 참조 규칙의 커밋과 점검한 대상 커밋, 실제 파일·CI 결과·버전 조합을 함께 기록합니다.

미확인·미적용 항목을 완료로 표시하지 않습니다. 예외는 GOV-01의 사유·담당자·재검토 조건을 기록하고, 해당 없음은 기능이 존재하지 않는 근거를 적습니다. 부분 이관과 전체 완료를 구분하며 실제 HA 테스트·최소 버전 검증이 남아 있으면 그 상태를 그대로 남깁니다. 체크리스트 작성 자체가 기존 통합이나 CI를 전환하지는 않습니다.
