# 적용과 버전 관리

## 범위와 우선순위

이 규칙의 주 대상은 `custom_components/<domain>`이 있는 hass 리포입니다. 카드·Android·YAML 설정·애드온에는 문서·CI 보안·버전 관리 원칙만 적용하며 HA 통합 전용 검사를 강제하지 않습니다.

- **공식**: 링크한 HA/HACS/GitHub 규격. 사용 API와 배포 방식에 적용됩니다.
- **필수**: 이 표준을 채택하는 리포의 프로젝트 정책입니다.
- **권장**: 통합 특성에 맞게 채택합니다.
- 충돌 시 사용자의 명시적 지시와 적용 가능한 공식 규격을 우선하고, 로컬 예외를 기록합니다.

## 채택

**GOV-01 필수**: `STANDARDS.md`에 표준 버전, 적용 profile, 예외(ID·이유·담당자·재검토 조건)를 기록합니다. 예시는 templates/integration/STANDARDS.md입니다. 새 통합은 v0.1.0 기준을 적용하고, 기존 통합은 결함을 숨기지 않은 채 단계적으로 이관합니다.

**GOV-02 필수**: 공통 workflow/action은 검토한 commit SHA로 고정합니다. 예시의 `v0.1.0`은 읽기 쉬운 배포 참조입니다. 실제 채택 PR에서는 `git ls-remote https://github.com/eigger/hass-repo-standards.git refs/tags/v0.1.0`으로 SHA를 확인해 교체합니다. 중앙 변경이 모든 리포에 즉시 적용되지 않도록 합니다.

**GOV-03 필수**: 규칙 변경은 CHANGELOG에 기록합니다. 표준의 SemVer: major는 기존 채택 리포에 변경을 요구하는 정책, minor는 선택 기능과 호환 입력, patch는 오류·설명 수정입니다. 릴리스 태그는 이동하지 않습니다. 필수 규칙 전환은 차기 major 또는 명시적 채택 PR로 합니다.

## 이관 순서

1. 현재 CI를 읽기 전용으로 조사하고 기본 브랜치·지원 HA·테스트 환경을 확인합니다.
2. 기존 검사가 통과하는 상태를 보존한 채 requirements 파일과 Ruff 설정을 정리합니다.
3. Validate와 Python CI를 공통 workflow로 전환합니다. 필요한 브라우저·최소 HA job은 유지합니다.
4. 의존성 업데이트 bot은 dry-run으로 기존 변화와 비교하고 전환합니다.
5. README 배지와 AGENTS.md의 표준 참조를 추가합니다.
6. 실제 원격 CI를 통과한 뒤 required checks 이름을 저장소 설정에 반영합니다.

`needs`/job 이름 변경으로 branch protection이 영구 대기하지 않도록 채택 PR에서 확인합니다. 이 표준 자체는 저장소 설정을 자동 변경하지 않습니다.
