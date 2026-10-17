# 초기 구현 검증

확인일: 2026-10-17.

- 표준 도구의 offline unittest 15개 통과: 버전 비교, major 제한, downgrade 방지, extras/marker/연산자 보존, 최소 package 제약, HA component dependency cycle, 배지 관리 구역과 다국어 사전 검증.
- Ruff check/format, 문서 상대 링크·JSON·caller 입력 계약 검사 통과.
- actionlint 1.7.12로 중앙 workflow와 caller 템플릿 문법 검사 통과. 로컬 실행에서는 shellcheck/pyflakes 확장 검사를 끄고 actionlint 자체 검사를 사용.
- 실제 hass-catprinter manifest를 사용한 updater dry-run: 변경 없음.
- macOS arm64, Python 3.13.14 격리 환경에서 실제 hass-catprinter의 imagespec[datamatrix]==1.1.0, blesession==0.9.0 하한 설치 및 pip check 성공. pytest 8.4.2, pytest-asyncio 1.2.0, bleak 1.1.1을 테스트 환경으로 사용.
- 위 환경으로 기존 catprinter 테스트 실행: **64 passed, 6 skipped**. cache/bytecode 생성을 끄고 실행했으며 기존 리포 파일을 수정하지 않음.
- GitHub의 이 리포 CI는 Linux에서 offline 검사와 공통 Python 환경 action의 current/minimum fixture를 검사.

이 결과는 모든 통합의 HA/장치 호환성, HACS/Hassfest 실행 성공, 원격 bot PR 생성·권한 설정까지 검증했다는 뜻은 아닙니다. 해당 검사는 각 리포의 채택 PR에서 확인합니다. 중앙 updater의 PR 생성은 현재 리포에서 실제로 실행하지 않았습니다.

중앙 workflow 내부 action 참조는 구현 commit e7b02dabb8a3d7b477237a2e904b34c3eeab0839에 고정합니다. 이렇게 하여 같은 릴리스 안에서 자기 commit SHA를 순환 참조하지 않고 검증한 action을 사용합니다.
