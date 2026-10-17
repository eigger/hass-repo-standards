# HACS와 배포 규칙

[HACS 공식 요구사항](https://www.hacs.xyz/docs/publish/start/)과 [통합 배포 안내](https://www.hacs.xyz/docs/publish/integration/)를 기준으로 하며, 아래 필수 표기는 프로젝트 정책입니다.

**HACS-01 필수**: 루트에 `hacs.json`, README, LICENSE를 둡니다. `name`은 UI 표시 이름이고 `homeassistant`는 검증한 최소 HA 요구사항으로 관리합니다. 공식적으로 선택인 최소 버전을 이 표준에서는 명시하는 정책을 채택합니다. 확인 전 임의 버전을 넣지 말고 예외를 기록합니다.

**HACS-02 필수**: 기본 배포 구조는 `custom_components/<domain>`입니다. `content_in_root`, `zip_release`, `filename`, `persistent_directory` 등은 실제 구조에 필요할 때만 사용합니다. 기존에 사용한 필드를 일괄 삭제하지 않습니다.

**HACS-03 필수**: 기본 목록 등재와 custom repository 설치를 구분합니다. HACS 검증 성공, hacs.json 존재, brands 등록만으로 Default 배지를 표시하지 않습니다. Default 표기는 실제 목록 등재 확인 링크와 날짜를 기록합니다.

**HACS-04 필수**: 정식 배포는 GitHub Release로 만들고 tag의 `v` 접두사를 제외한 버전과 해당 commit manifest.version을 일치시킵니다. 통합 버전과 최소 HA/HACS 버전은 별개입니다. prerelease는 GitHub에서도 prerelease로 표시합니다.

**HACS-05 필수**: HACS와 Hassfest 검증을 실행합니다. 공통 Validate workflow는 둘을 별도 job으로 실행합니다. 검사 제외는 입력에 명시하고 STANDARDS.md에 이유·해제 조건을 기록합니다. 오류를 피하기 위한 무기한 ignore는 금지합니다.

**HACS-06 권장**: 공개 리포 description·topics·issue 경로·brands 상태를 관리합니다. `render_readme` 같은 과거 필드의 현재 지원 여부는 사용하는 HACS 버전에서 확인하고, 오래된 예제를 그대로 복사하지 않습니다.
