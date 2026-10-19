# HACS와 배포 규칙

[HACS 공식 요구사항](https://www.hacs.xyz/docs/publish/start/)과 [통합 배포 안내](https://www.hacs.xyz/docs/publish/integration/)를 기준으로 하며, 아래 필수 표기는 프로젝트 정책입니다.

**HACS-01 필수**: 루트에 `hacs.json`, README, LICENSE를 둡니다. `name`은 UI 표시 이름이고 `homeassistant`는 검증한 최소 HA 요구사항으로 관리합니다. 공식적으로 선택인 최소 버전을 이 표준에서는 명시하는 정책을 채택합니다. 확인 전 임의 버전을 넣지 말고 예외를 기록합니다.

**HACS-02 필수**: 기본 배포 구조는 `custom_components/<domain>`입니다. `content_in_root`, `zip_release`, `filename`, `persistent_directory` 등은 실제 구조에 필요할 때만 사용합니다. 기존에 사용한 필드를 일괄 삭제하지 않습니다.

**HACS-03 필수**: 기본 목록 등재와 custom repository 설치를 구분합니다. HACS 검증 성공, hacs.json 존재, brands 등록만으로 Default 배지를 표시하지 않습니다. Default 표기는 실제 목록 등재 확인 링크와 날짜를 기록합니다.

신규 생성과 기존 리포 채택·재검토 모두에서 같은 확인된 등록 상태로 양언어 README의 HACS 설치 안내를 작성합니다. [공식 기본 목록](https://github.com/hacs/default/blob/master/integration)에 등재된 리포는 [My Home Assistant HACS 바로가기](https://www.hacs.xyz/docs/use/my/)로 실제 `owner`·`repository`의 저장소를 열어 다운로드하도록 안내합니다. 이 링크는 자동 설치 완료를 의미하지 않으며 HACS 사전 설치·다운로드 후 HA 재시작을 설명합니다. 미등록 리포는 기존 방식인 실제 GitHub URL의 커스텀 저장소 등록(종류 `Integration`) → 다운로드 → 재시작을 안내합니다. 확인 불가를 등재 근거로 사용하지 않습니다. 기기 설정·수동 설치·이전 안내 등 기존 고유 본문은 보존하며, 임의 본문을 자동으로 덮어쓰지 않습니다.

**HACS-04 필수**: 정식 배포는 GitHub Release로 만들고 tag의 `v` 접두사를 제외한 버전과 해당 commit manifest.version을 일치시킵니다. 통합 버전과 최소 HA/HACS 버전은 별개입니다. prerelease는 GitHub에서도 prerelease로 표시합니다.

**HACS-05 필수**: HACS와 Hassfest 검증을 실행합니다. 공통 Validate workflow는 둘을 별도 job으로 실행합니다. 검사 제외는 입력에 명시하고 STANDARDS.md에 이유·해제 조건을 기록합니다. 오류를 피하기 위한 무기한 ignore는 금지합니다.

HACS-05의 brands 검사는 실제 사용하는 HACS action에서 확인합니다. 현재 [공식 검사 설명](https://hacs.xyz/docs/publish/include/#check-brands)과 [검증 구현](https://github.com/hacs/integration/blob/adc26ec798021d2c2db1e6aa90eabe2e208b8c04/custom_components/hacs/validate/brands.py)은 로컬 `brand/icon.png`를 먼저 확인하고, 없으면 Home Assistant brands의 custom domain 등록 여부를 확인합니다. 기본 구조에서는 `custom_components/<domain>/brand/icon.png`, `content_in_root: true`이면 루트 `brand/icon.png`입니다. 로컬 경로 또는 원격 등록 근거와 해당 커밋의 실제 HACS 실행 결과를 체크리스트에 기록합니다. 공개 메타데이터 관리의 권장 여부와 별개로, 활성화된 필수 검사의 실패는 보완해야 합니다.

[HA 이미지 지침](https://contributors.home-assistant.io/core/integrations/brands/)에 따라 실제 PNG 아이콘은 256×256, 선택 `icon@2x.png`는 512×512로 준비하고 사용 권한·출처를 남깁니다. HACS의 경로 존재 검사가 이미지 내용·권리·렌더링까지 보장하지 않으므로 실제 파일 형식과 표시를 별도로 확인합니다. 로컬 brand의 HA UI 사용은 HA 2026.3부터 지원되므로 이전 HA를 지원할 때 로컬 아이콘 제공만으로 그 버전의 UI 표시까지 검증했다고 기록하지 않습니다. [HACS action 선언](https://github.com/hacs/action/blob/1ebf01c408f29afcb6406bd431bc98fd8cbb15aa/action.yml)은 가변 Docker 이미지를 사용하므로 검사 동작이 바뀌면 공식 설명과 실제 CI 로그를 다시 확인합니다.

**HACS-06 권장**: 공개 리포 description·topics·issue 경로·brands 상태를 관리합니다. `render_readme` 같은 과거 필드의 현재 지원 여부는 사용하는 HACS 버전에서 확인하고, 오래된 예제를 그대로 복사하지 않습니다.
