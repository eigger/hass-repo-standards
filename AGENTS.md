# Repository instructions

이 리포는 Home Assistant 커스텀 통합의 공통 규칙과 CI를 제공합니다.

- 변경 전에 README와 해당 docs 문서를 읽습니다. 규칙의 ID와 필수·권장 수준을 유지합니다.
- 공식 요구사항을 설명할 때 docs/sources.md의 공식 출처를 확인합니다. 프로젝트 정책을 공식 요구사항으로 표현하지 않습니다.
- 다른 통합 리포를 수정하거나 workflow를 실행하는 것은 해당 작업 범위에 포함될 때만 합니다.
- 버전·domain·기본 브랜치·의존성은 기존 메타데이터에서 읽습니다. main/master나 패키지 이름을 추정하지 않습니다.
- 배지는 관리 주석 사이만 변경합니다. 이전 안내와 번역 문서를 보존합니다.
- reusable workflow는 caller checkout을 유지합니다. scripts 접근은 composite action의 github.action_path를 사용합니다.
- 의존성 bot은 extras·연산자·marker를 보존하고 실패를 성공으로 바꾸지 않습니다.
- 수정한 동작에 해당하는 단위 테스트를 실행하고 python3 scripts/check_repository.py를 실행합니다.
- SHA와 PyPI 버전은 실재하는 값만 사용합니다. 이 규칙 리포에는 태그나 GitHub Release를 만들지 않고 main과 커밋으로 관리합니다.
