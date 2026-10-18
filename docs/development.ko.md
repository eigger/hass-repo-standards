# 개발·검사 안내

[English](development.md) | **한국어**

**이 리포 생성만으로 기존 리포의 파일이나 CI는 변경되지 않습니다.** 아래 검사는 읽기 전용입니다.

```bash
python3 -m pip install -r requirements_dev.txt
python3 scripts/audit_repositories.py --root .. --output /tmp/hass-ci-audit.json
python3 scripts/audit_repositories.py --github-owner eigger --output /tmp/hass-ci-remote.json
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
```

배지는 관리 구역 안에서만 갱신합니다. [사용법](documentation.md)을 먼저 확인하세요.

```bash
python3 scripts/sync_badges.py ../hass-example --check
```

중앙 템플릿 채택·검사 절차는 [사용법](../templates/integration/USAGE.md)을 따릅니다. 관리 영역 밖 README는 자동 수정하지 않습니다.

```bash
python3 scripts/check_integration.py ../hass-example
```

공용 Validate 검사기는 blesession 사용 통합의 DOC-07 양언어 로컬 문제 해결 문서·고정 절/표 구조·언어별 원본/지원 링크도 검사합니다. 오프라인 검사로 실물·번역 의미·진단 의미·원격 이슈 템플릿 존재를 검증하지 않습니다. 공통 사용자 안내는 blesession, 중앙은 작성 규칙·템플릿·이전 URL 안내를 관리합니다.

로컬 통합 검사기는 대상 통합의 문법과 같거나 더 최신인 Python으로 실행하세요. standalone standards caller 예제는 현재 통합·테스트 소스를 파싱하기 위해 Python 3.14를 사용합니다. 이는 도구 실행 환경이며 지원 최소 HA/Python을 올리거나 최소 검증 환경을 제거하지 않습니다. 중앙 도구 자체의 Python 3.9 단위 테스트 호환성과 구분합니다.

DOC-08의 imagespec 사용 통합은 [payload 작성 규칙](payload-documentation.md)의 실제 HA·renderer 계약을 실행합니다. Validate의 정적 검사만으로 예제 실행을 대체하지 않습니다. 각 HA job에서 resolver가 설치한 current/정확한 하한을 그대로 사용하고 `actions/check-payload`는 추가 패키지를 설치하지 않습니다. 로컬 재현도 같은 환경에서 검토한 중앙 scripts를 PYTHONPATH에 연결해 `hass_standards_payload` plugin으로 domain의 중앙 scaffold를 실행합니다. 환경 변수·명령은 작성 규칙을 따르며 일반 pytest만으로 scaffold를 PASS로 고치지 않습니다. 공통 원본은 imagespec의 실제 기본 브랜치에 먼저 공개하고 URL을 확인합니다. 로컬 작성·중앙 도구 테스트·실물 검증은 구분합니다.
